"""
委托支付载荷定义
定义 PSD-PAY-DEL 协议的数据结构
"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone


@dataclass
class PaymentTokenInfo:
    """
    支付标记信息
    用于传统 token 化支付场景
    """
    token: str
    token_type: str = "CARD_TOKEN"
    token_scheme: str = "EMV_PAIT"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "token_type": self.token_type,
            "token_scheme": self.token_scheme
        }


@dataclass
class SubAccountInfo:
    """
    专属子账户信息
    用于资金隔离的支付场景
    """
    subaccount_id: str
    signature: str
    signature_algorithm: str = "ES256"
    key_reference: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "subaccount_id": self.subaccount_id,
            "signature": self.signature,
            "signature_algorithm": self.signature_algorithm
        }
        if self.key_reference:
            result["key_reference"] = self.key_reference
        return result


@dataclass
class IACDelegationInfo:
    """
    IAC 委托信息
    从 IAC 中提取的委托相关内容
    """
    delegation_id: str
    delegation_mode: str = "SPECIFIED"
    validity_context: Optional[Dict[str, str]] = None
    signer_identity: Optional[str] = None
    allowed_amounts: Optional[Dict[str, float]] = None
    allowed_payment_methods: Optional[List[str]] = None
    allowed_merchants: Optional[List[str]] = None

    @classmethod
    def from_iac_payload(cls, iac_payload: Dict[str, Any]) -> "IACDelegationInfo":
        """
        从 IAC 载荷中提取委托信息

        Args:
            iac_payload: 解码后的 IAC JWT 载荷

        Returns:
            IACDelegationInfo 实例
        """
        # 从 vc.credential_subject 中提取
        cred_subject = iac_payload.get("vc", {}).get("credential_subject", {})

        return cls(
            delegation_id=cred_subject.get("delegation_id", iac_payload.get("jti", "")),
            delegation_mode=cred_subject.get("delegation_mode", "SPECIFIED"),
            validity_context={
                "validity_start_time": cred_subject.get("validity_start_time"),
                "validity_end_time": cred_subject.get("validity_end_time")
            },
            signer_identity=cred_subject.get("signer_identity"),
            allowed_amounts={
                "max_total_amount": cred_subject.get("max_total_amount"),
                "max_single_amount": cred_subject.get("max_single_amount")
            },
            allowed_payment_methods=cred_subject.get("allowed_payment_methods"),
            allowed_merchants=cred_subject.get("allowed_merchants")
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "delegation_id": self.delegation_id,
            "delegation_mode": self.delegation_mode
        }
        if self.validity_context:
            result["validity_context"] = self.validity_context
        if self.signer_identity:
            result["signer_identity"] = self.signer_identity
        if self.allowed_amounts:
            result["allowed_amounts"] = self.allowed_amounts
        if self.allowed_payment_methods:
            result["allowed_payment_methods"] = self.allowed_payment_methods
        if self.allowed_merchants:
            result["allowed_merchants"] = self.allowed_merchants
        return result


@dataclass
class DelegatedPaymentPayload:
    """
    委托支付载荷
    符合 ACT 协议 PSD-PAY-DEL 规范的完整请求结构
    """
    request_id: str
    buyer_agent_id: str
    delegation_id: str
    iac: str  # 完整的 JWT 格式 IAC
    merchant_id: str
    merchant_order_id: str
    cart_snapshot_hash: str
    amount: str
    currency: str
    timestamp: str

    # 可选字段
    payment_method: Optional[str] = None
    payment_token: Optional[PaymentTokenInfo] = None
    subaccount_info: Optional[SubAccountInfo] = None
    iac_delegation_info: Optional[IACDelegationInfo] = None
    description: Optional[str] = None
    signature: Optional[str] = None
    signature_covered_fields: Optional[List[str]] = None

    # 内部字段（不应序列化）
    _created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def create(
        cls,
        buyer_agent_id: str,
        delegation_id: str,
        iac: str,
        merchant_id: str,
        merchant_order_id: str,
        cart_snapshot_hash: str,
        amount: float,
        currency: str = "CNY",
        payment_method: Optional[str] = None,
        payment_token: Optional[Dict[str, str]] = None,
        subaccount_info: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        signature: Optional[str] = None,
        signature_covered_fields: Optional[List[str]] = None
    ) -> "DelegatedPaymentPayload":
        """
        创建委托支付载荷

        Args:
            buyer_agent_id: 买方智能体 DID
            delegation_id: 委托标识
            iac: 意图授权凭证 JWT
            merchant_id: 商户 DID
            merchant_order_id: 商户订单号
            cart_snapshot_hash: 购物车快照哈希
            amount: 支付金额
            currency: 币种
            payment_method: 支付方式（可选）
            payment_token: 支付标记信息（可选）
            subaccount_info: 子账户信息（可选）
            description: 描述（可选）
            signature: 智能体签名（可选）
            signature_covered_fields: 签名覆盖字段（可选）

        Returns:
            DelegatedPaymentPayload 实例
        """
        import uuid
        from datetime import timezone

        return cls(
            request_id=f"req-deleg-{uuid.uuid4().hex[:12]}",
            buyer_agent_id=buyer_agent_id,
            delegation_id=delegation_id,
            iac=iac,
            merchant_id=merchant_id,
            merchant_order_id=merchant_order_id,
            cart_snapshot_hash=cart_snapshot_hash,
            amount=f"{amount:.2f}",
            currency=currency,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payment_method=payment_method,
            payment_token=PaymentTokenInfo(**payment_token) if payment_token else None,
            subaccount_info=SubAccountInfo(**subaccount_info) if subaccount_info else None,
            description=description,
            signature=signature,
            signature_covered_fields=signature_covered_fields
        )

    def sign(self, agent_private_key: str) -> str:
        """
        对关键字段进行签名

        Args:
            agent_private_key: 智能体私钥

        Returns:
            签名后的十六进制字符串
        """
        # 构造待签名字段
        fields_to_sign = self.signature_covered_fields or [
            "request_id",
            "delegation_id",
            "merchant_order_id",
            "amount",
            "currency",
            "timestamp"
        ]

        # 拼接字段值
        data_to_sign = ""
        for field in fields_to_sign:
            value = getattr(self, field, "")
            if value:
                if isinstance(value, dict):
                    value = json.dumps(value, sort_keys=True)
                data_to_sign += f"{field}={value};"

        # 简单签名（真实场景应使用数字签名算法如 ES256）
        import hmac
        import hashlib

        signature = hmac.new(
            agent_private_key.encode(),
            data_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()

        self.signature = signature
        self.signature_covered_fields = fields_to_sign

        return signature

    def to_dict(self, include_signature: bool = True) -> Dict[str, Any]:
        """
        转换为字典

        Args:
            include_signature: 是否包含签名

        Returns:
            字典表示
        """
        result = {
            "request_id": self.request_id,
            "buyer_agent_id": self.buyer_agent_id,
            "delegation_id": self.delegation_id,
            "iac": self.iac,
            "merchant_id": self.merchant_id,
            "merchant_order_id": self.merchant_order_id,
            "cart_snapshot_hash": self.cart_snapshot_hash,
            "amount": self.amount,
            "currency": self.currency,
            "timestamp": self.timestamp
        }

        # 添加可选字段
        if self.payment_method:
            result["payment_method"] = self.payment_method

        if self.payment_token:
            result["payment_token"] = self.payment_token.to_dict()

        if self.subaccount_info:
            result["subaccount_info"] = self.subaccount_info.to_dict()

        if self.description:
            result["description"] = self.description

        if include_signature and self.signature:
            result["signature"] = self.signature
            result["signature_covered_fields"] = self.signature_covered_fields

        return result

    def to_json(self, include_signature: bool = True) -> str:
        """
        转换为 JSON 字符串

        Args:
            include_signature: 是否包含签名

        Returns:
            JSON 字符串
        """
        return json.dumps(self.to_dict(include_signature), ensure_ascii=False, indent=2)

    @staticmethod
    def calculate_cart_snapshot_hash(cart_items: List[Dict[str, Any]]) -> str:
        """
        计算购物车快照的 SHA-256 哈希

        Args:
            cart_items: 商品列表

        Returns:
            SHA-256 哈希前缀
        """
        cart_str = json.dumps(cart_items, sort_keys=True)
        hash_obj = hashlib.sha256(cart_str.encode())

        return f"sha256:{hash_obj.hexdigest()}"