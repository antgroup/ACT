"""
委托支付模块 (Delegated Payment - PSD-PAY-DEL)
实现 ACT 协议的委托支付流程
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
import uuid
import random
import string


@dataclass
class DelegationCancelRequest:
    """
    委托取消请求
    """
    delegation_id: str  # 委托 ID
    principal_id: str  # 委托人 ID
    reason: Optional[str] = None  # 取消原因


@dataclass
class DelegationApplyRequest:
    """
    委托协议签约请求
    用于创建委托支付授权
    """
    principal_id: str  # 委托人（用户）
    agent_id: str  # 受托智能体
    delegation_id: str  # 委托标识
    max_total_amount: float = 10000.0  # 总金额上限
    max_single_amount: Optional[float] = None  # 单笔上限
    validity_start: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    validity_end: str = field(default_factory=lambda: (datetime.now(timezone.utc) + __import__('datetime').timedelta(days=30)).isoformat())
    delegation_purpose: Optional[str] = None  # 委托目的
    allowed_merchants: Optional[List[str]] = None  # 允许商户白名单
    allowed_items: Optional[List[str]] = None  # 允许商品白名单
    allowed_payment_methods: Optional[List[str]] = None  # 允许支付方式


@dataclass
class DelegationApplyResponse:
    """
    委托协议签约响应
    包含签发的 IAC（意图授权凭证）
    """
    delegation_id: str
    iac: str  # IAC JWT 凭证
    status: str  # SIGNED/ACTIVE
    issued_at: str
    message: str
    max_total_amount: float = 0.0
    max_single_amount: Optional[float] = None
    agent_type: str = "DEDICATED_AGENT"  # DEDICATED_AGENT/PLATFORM_AGENT
    subaccount_id: Optional[str] = None


@dataclass
class DelegationPayRequest:
    """
    委托支付请求
    智能体使用 IAC 执行支付
    """
    request_id: str
    buyer_agent_id: str
    delegation_id: str
    iac: str  # IAC JWT 凭证
    merchant_id: str
    merchant_order_id: str
    cart_snapshot_hash: str
    amount: float
    currency: str = "CNY"
    payment_method: Optional[str] = None
    subaccount_id: Optional[str] = None
    signature: Optional[str] = None


@dataclass
class DelegationPayResponse:
    """
    委托支付响应
    """
    success: bool
    payment_id: Optional[str] = None
    transaction_id: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    message: str = ""
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "success": self.success,
            "payment_id": self.payment_id,
            "transaction_id": self.transaction_id,
            "status": self.status,
            "amount": self.amount,
            "currency": self.currency,
            "message": self.message
        }
        if self.error_code:
            result["error"] = {
                "code": self.error_code,
                "message": self.error_message
            }
        return result


class DelegatedPaymentService:
    """
    委托支付服务 (PSD-PAY-DEL)
    实现 ACT 协议的用户委托支付流程
    """

    def __init__(self):
        """
        初始化委托支付服务
        """
        self.delegations: Dict[str, Dict[str, Any]] = {}
        self.cumulative_amounts: Dict[str, float] = {}
        self.revoked_delegations: set = set()
        self.payments: Dict[str, Dict[str, Any]] = {}
        print("[委托支付服务] 初始化完成")

    def apply(self, request: DelegationApplyRequest) -> DelegationApplyResponse:
        """
        申请委托协议授权

        流程：
        1. 验证请求参数
        2. 生成委托记录
        3. 签发 IAC（意图授权凭证）
        4. 返回授权结果

        Args:
            request: 委托协议签约请求

        Returns:
            委托协议签约响应
        """
        # 1. 生成 IAC token (模拟 JWT)
        iac = self._create_iac_token(request)

        # 2. 创建委托记录
        delegation = {
            "delegation_id": request.delegation_id,
            "principal_id": request.principal_id,
            "agent_id": request.agent_id,
            "iac": iac,
            "max_total_amount": request.max_total_amount,
            "max_single_amount": request.max_single_amount,
            "status": "ACTIVE",
            "validity_start": request.validity_start,
            "validity_end": request.validity_end,
            "delegation_purpose": request.delegation_purpose,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        self.delegations[request.delegation_id] = delegation
        self.cumulative_amounts[request.delegation_id] = 0.0

        print(f"[委托支付] 委托协议已创建：{request.delegation_id}, 总额度：¥{request.max_total_amount:.2f}")

        return DelegationApplyResponse(
            delegation_id=request.delegation_id,
            iac=iac,
            status="ACTIVE",
            issued_at=datetime.now(timezone.utc).isoformat(),
            message="委托协议签发成功",
            max_total_amount=request.max_total_amount,
            max_single_amount=request.max_single_amount
        )

    def pay(self, request: DelegationPayRequest) -> DelegationPayResponse:
        """
        执行委托支付

        流程：
        1. 验证 IAC 有效性
        2. 验证智能体身份
        3. 验证金额约束
        4. 执行扣款
        5. 更新累计金额
        6. 返回结果

        Args:
            request: 委托支付请求

        Returns:
            委托支付响应
        """
        # 1. 验证委托是否存在
        delegation = self.delegations.get(request.delegation_id)
        if not delegation:
            return DelegationPayResponse(
                success=False,
                message="委托不存在",
                error_code="DELEGATION_NOT_FOUND"
            )

        # 2. 验证委托未吊销
        if request.delegation_id in self.revoked_delegations:
            return DelegationPayResponse(
                success=False,
                message="委托已被吊销",
                error_code="DELEGATION_REVOKED"
            )

        # 3. 验证 IAC 签名（简化：检查是否存在）
        if request.iac != delegation["iac"]:
            return DelegationPayResponse(
                success=False,
                message="IAC 凭证无效",
                error_code="IAC_INVALID"
            )

        # 4. 验证智能体身份
        if request.buyer_agent_id != delegation["agent_id"]:
            return DelegationPayResponse(
                success=False,
                message="智能体身份不匹配",
                error_code="AGENT_MISMATCH"
            )

        # 5. 验证金额约束
        if request.amount > delegation["max_single_amount"]:
            return DelegationPayResponse(
                success=False,
                message=f"单笔金额超出授权上限：¥{request.amount:.2f} > ¥{delegation['max_single_amount']:.2f}",
                error_code="AMOUNT_EXCEEDS_SINGLE_LIMIT"
            )

        # 6. 验证累计额度
        current_total = self.cumulative_amounts.get(request.delegation_id, 0)
        if current_total + request.amount > delegation["max_total_amount"]:
            return DelegationPayResponse(
                success=False,
                message=f"累计金额超出授权上限：¥{current_total + request.amount:.2f} > ¥{delegation['max_total_amount']:.2f}",
                error_code="AMOUNT_EXCEEDS_TOTAL_LIMIT"
            )

        # 7. 执行支付
        payment_id = f"DELEG{uuid.uuid4().hex[:16].upper()}"
        transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"

        payment_record = {
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "delegation_id": request.delegation_id,
            "merchant_id": request.merchant_id,
            "merchant_order_id": request.merchant_order_id,
            "amount": request.amount,
            "currency": request.currency,
            "status": "success",
            "type": "DELEGATED",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        self.payments[payment_id] = payment_record
        self.cumulative_amounts[request.delegation_id] = current_total + request.amount

        print(f"[委托支付] 支付成功：{payment_id}, 委托：{request.delegation_id[:16]}..., 金额：¥{request.amount:.2f}")

        return DelegationPayResponse(
            success=True,
            payment_id=payment_id,
            transaction_id=transaction_id,
            status="success",
            amount=request.amount,
            currency=request.currency,
            message="委托支付成功"
        )

    def cancel(self, request: DelegationCancelRequest) -> DelegationApplyResponse:
        """
        取消委托

        Args:
            request: 取消请求

        Returns:
            取消结果响应
        """
        if request.delegation_id not in self.delegations:
            return DelegationApplyResponse(
                delegation_id=request.delegation_id,
                iac="",
                status="FAILED",
                issued_at=datetime.now(timezone.utc).isoformat(),
                message="委托不存在"
            )

        if request.delegation_id in self.revoked_delegations:
            return DelegationApplyResponse(
                delegation_id=request.delegation_id,
                iac="",
                status="REVOKED",
                issued_at=datetime.now(timezone.utc).isoformat(),
                message="委托已被吊销"
            )

        self.revoked_delegations.add(request.delegation_id)
        print(f"[委托支付] 委托已取消：{request.delegation_id}")

        return DelegationApplyResponse(
            delegation_id=request.delegation_id,
            iac="",
            status="REVOKED",
            issued_at=datetime.now(timezone.utc).isoformat(),
            message="委托协议已取消"
        )

    def get_cumulative_amount(self, delegation_id: str) -> float:
        """
        获取累计扣款金额

        Args:
            delegation_id: 委托 ID

        Returns:
            累计金额
        """
        return self.cumulative_amounts.get(delegation_id, 0.0)

    def get_delegation(self, delegation_id: str) -> Optional[Dict[str, Any]]:
        """
        查询委托信息

        Args:
            delegation_id: 委托 ID

        Returns:
            委托信息或 None
        """
        return self.delegations.get(delegation_id)

    def _create_iac_token(self, request: DelegationApplyRequest) -> str:
        """
        创建 IAC（意图授权凭证）JWT token

        Args:
            request: 委托协议签约请求

        Returns:
            IAC JWT 字符串
        """
        # 简化的 JWT 创建（实际应使用 PyJWT）
        payload = {
            "iss": request.principal_id,
            "sub": request.agent_id,
            "jti": request.delegation_id,
            "type": "vc+jwt",
            "vc": {
                "credential_subject": {
                    "delegation_id": request.delegation_id,
                    "max_total_amount": request.max_total_amount,
                    "max_single_amount": request.max_single_amount,
                    "validity_start": request.validity_start,
                    "validity_end": request.validity_end
                }
            },
            "exp": datetime.now(timezone.utc).timestamp() + 31536000  # 1 年后过期
        }

        # 简化签名（实际应使用密钥）
        import base64
        import json
        import hmac
        import hashlib

        header = {"alg": "HS256", "typ": "JWT"}
        header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()
        payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
        signature = hmac.new(b"mock-secret-key", f"{header_encoded}.{payload_encoded}".encode(), hashlib.sha256).digest()
        signature_encoded = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()

        return f"{header_encoded}.{payload_encoded}.{signature_encoded}"