"""
委托支付处理器
实现委托支付的四个子流程：签约、查询、解约、支付

支持两种场景：
1. 场景二：平台型智能体定向委托 - 多租户共享，双重身份验证
2. 场景三：专属型智能体定向委托 - 独立身份，子账户隔离

参考 ACT 协议 PSD-PAY-DEL 规范
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from enum import Enum

from .service import DelegatedPaymentService, PaymentResult
from .payload import DelegatedPaymentPayload


class DelegationScenario(Enum):
    """
    委托支付场景类型
    """
    PLATFORM_AGENT = "PLATFORM_AGENT"  # 场景二：平台型智能体（多租户共享）
    DEDICATED_AGENT = "DEDICATED_AGENT"  # 场景三：专属型智能体（独立身份）


@dataclass
class IACDelegationInfo:
    """
    IAC 委托信息
    用于存储完整的委托凭证信息
    """
    # 基础字段
    delegation_id: str  # 委托标识
    delegation_mode: str  # SPECIFIED/UNSPECIFIED

    # 委托人信息
    principal_id: str  # 委托人 DID

    # 智能体信息（根据不同场景验证）
    agent_id: str  # 受托智能体 DID
    agent_type: str  # PLATFORM_AGENT / DEDICATED_AGENT

    # 场景二（平台型）特有的委托人 - 智能体绑定验证
    principal_agent_binding_verified: bool = False

    # 场景三（专属型）特有的子账户
    subaccount_id: Optional[str] = None

    # 金额约束
    max_total_amount: float = 0.0
    max_single_amount: Optional[float] = None
    amount_currency: str = "CNY"

    # 时效约束
    validity_start: Optional[str] = None
    validity_end: Optional[str] = None

    # 约束项
    allowed_payment_methods: Optional[List[str]] = None
    allowed_merchants: Optional[List[str]] = None
    allowed_items: Optional[List[str]] = None  # 允许购买的商品列表

    # 委托目的说明（用于明确交易对象）
    delegation_purpose: Optional[str] = None

    # 额外上下文
    context: Optional[Dict[str, Any]] = None


@dataclass
class DelegationApplyRequest:
    """
    委托协议签约请求
    对应 PSD-PAY-DEL-APPLY

    支持两种场景：
    1. 场景二（平台型智能体）：agent_type=PLATFORM_AGENT，需要平台 + 委托人双重绑定验证
    2. 场景三（专属型智能体）：agent_type=DEDICATED_AGENT，可设置子账户进行风险隔离
    """
    principal_id: str  # 委托人
    agent_id: str  # 受托智能体
    delegation_id: str  # 委托标识
    delegation_mode: str = "SPECIFIED"  # 委托模式
    agent_type: str = "PLATFORM_AGENT"  # 智能体类型（PLATFORM_AGENT/DEDICATED_AGENT）
    subaccount_id: Optional[str] = None  # 场景三：专属子账户（可选）
    delegation_purpose: Optional[str] = None  # 委托目的说明（明确购买标的）
    allowed_items: Optional[List[str]] = None  # 允许购买的商品列表（场景特定约束）

    validity_start: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    validity_end: str = field(default_factory=lambda: datetime(
        year=datetime.now().year + 1,
        month=datetime.now().month,
        day=datetime.now().day,
        tzinfo=timezone.utc
    ).isoformat())
    max_total_amount: float = 10000.0  # 总金额上限
    max_single_amount: Optional[float] = None  # 单笔上限
    allowed_payment_methods: Optional[List[str]] = None  # 允许的支付方式
    allowed_merchants: Optional[List[str]] = None  # 允许的商户列表


@dataclass
class DelegationApplyResponse:
    """
    委托协议签约响应
    """
    delegation_id: str
    iac: str  # 签发的 IAC 凭证
    status: str  # 协议状态：SIGNED/ACTIVE
    issued_at: str
    message: str
    max_total_amount: float = 0.0
    max_single_amount: Optional[float] = None

    # 场景信息（新增，用于 UI 展示）
    agent_type: str = "PLATFORM_AGENT"  # PLATFORM_AGENT / DEDICATED_AGENT
    delegation_purpose: Optional[str] = None  # 委托目的说明
    subaccount_id: Optional[str] = None  # 场景三专属子账户


@dataclass
class DelegationQueryRequest:
    """
    委托协议查询请求
    对应 PSD-PAY-DEL-QUERY
    """
    delegation_id: str
    principal_id: str  # 委托人（用于鉴权）


@dataclass
class DelegationQueryResponse:
    """
    委托协议查询响应
    """
    delegation_id: str
    status: str  # SIGNED/ACTIVE/SUSPENDED/REVOKED/EXPIRED
    principal_id: str
    agent_id: str
    validity_start: str
    validity_end: str
    max_total_amount: float
    cumulative_amount: float  # 累计扣款确认额
    detail: Optional[Dict[str, Any]] = None


@dataclass
class DelegationCancelRequest:
    """
    委托协议取消请求
    对应 PSD-PAY-DEL-CANCEL
    """
    delegation_id: str
    principal_id: str  # 委托人（用于鉴权）
    reason: Optional[str] = None  # 取消原因


@dataclass
class DelegationCancelResponse:
    """
    委托协议取消响应
    """
    delegation_id: str
    old_status: str
    new_status: str
    cancelled_at: str
    message: str


@dataclass
class DelegationPayRequest:
    """
    委托支付请求
    对应 PSD-PAY-DEL-PAY
    """
    request_id: str
    buyer_agent_id: str
    delegation_id: str
    iac: str  # IAC JWT
    merchant_id: str
    merchant_order_id: str
    cart_snapshot_hash: str
    amount: float
    currency: str = "CNY"
    payment_method: Optional[str] = None
    payment_token: Optional[Dict[str, Any]] = None
    subaccount_info: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    signature: Optional[str] = None
    signature_covered_fields: Optional[List[str]] = None


@dataclass
class DelegationPayResponse:
    """
    委托支付响应
    """
    success: bool
    payment_id: Optional[str]
    transaction_id: Optional[str]
    status: Optional[str]
    amount: Optional[float]
    currency: Optional[str]
    message: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

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
        if self.details:
            result["details"] = self.details
        return result


class DelegatedPaymentHandler:
    """
    委托支付处理器
    提供四个子流程的接口：APPLY、QUERY、CANCEL、PAY
    """

    def __init__(
        self,
        payment_service: Optional[DelegatedPaymentService] = None
    ):
        """
        初始化处理器

        Args:
            payment_service: 委托支付服务
        """
        self.payment_service = payment_service or DelegatedPaymentService()

    def apply_delegation(
        self,
        request: DelegationApplyRequest
    ) -> DelegationApplyResponse:
        """
        步骤 1：委托协议签约

        为用户签发 IAC（意图授权凭证）

        支持两种场景：
        1. 场景二（平台型智能体）：agent_type=PLATFORM_AGENT
           - 需验证平台 + 委托人双重绑定
           - 设置 delegation_purpose 明确授权边界
        2. 场景三（专属型智能体）：agent_type=DEDICATED_AGENT
           - 可直接锚定专属智能体身份
           - 可选设置 subaccount_id 进行风险隔离

        Args:
            request: 签约请求

        Returns:
            签约响应
        """
        from .mock_jwt import MockJWT

        # 生成 IAC
        iac = MockJWT.create_iac_token(
            delegation_id=request.delegation_id,
            principal_id=request.principal_id,
            agent_id=request.agent_id,
            validity_start=request.validity_start,
            validity_end=request.validity_end,
            max_total_amount=request.max_total_amount,
            max_single_amount=request.max_single_amount,
            allowed_payment_methods=request.allowed_payment_methods,
            allowed_merchants=request.allowed_merchants,
            allowed_items=request.allowed_items,  # 场景特定商品约束
            delegation_mode=request.delegation_mode,
            agent_type=request.agent_type,  # PLATFORM_AGENT / DEDICATED_AGENT
            subaccount_id=request.subaccount_id,  # 场景三专属子账户
            delegation_purpose=request.delegation_purpose  # 委托目的说明
        )

        return DelegationApplyResponse(
            delegation_id=request.delegation_id,
            iac=iac,
            status="SIGNED",
            issued_at=datetime.now(timezone.utc).isoformat(),
            message="委托协议签发成功",
            max_total_amount=request.max_total_amount,
            max_single_amount=request.max_single_amount,
            agent_type=request.agent_type,
            delegation_purpose=request.delegation_purpose,
            subaccount_id=request.subaccount_id
        )

    def query_delegation(
        self,
        request: DelegationQueryRequest
    ) -> DelegationQueryResponse:
        """
        步骤 2：委托协议查询

        查询委托协议状态和累计扣款金额

        Args:
            request: 查询请求

        Returns:
            查询响应
        """
        cumulative = self.payment_service.get_cumulative_amount(request.delegation_id)

        # 获取 IAC 中的信息（需要解码验证）
        # 这里简化为返回固定格式
        return DelegationQueryResponse(
            delegation_id=request.delegation_id,
            status="ACTIVE",
            principal_id="",  # 实际需要从 IAC 中获取
            agent_id="",
            validity_start="",
            validity_end="",
            max_total_amount=0.0,
            cumulative_amount=cumulative
        )

    def cancel_delegation(
        self,
        request: DelegationCancelRequest
    ) -> DelegationCancelResponse:
        """
        步骤 3：委托协议取消

        吊销委托授权

        Args:
            request: 取消请求

        Returns:
            取消响应
        """
        old_status = "ACTIVE"  # 实际应查询当前状态

        # 执行吊销
        success = self.payment_service.revoke_delegation(request.delegation_id)

        if not success:
            return DelegationCancelResponse(
                delegation_id=request.delegation_id,
                old_status=old_status,
                new_status="FAILED",
                cancelled_at=datetime.now(timezone.utc).isoformat(),
                message="取消委托失败"
            )

        return DelegationCancelResponse(
            delegation_id=request.delegation_id,
            old_status=old_status,
            new_status="REVOKED",
            cancelled_at=datetime.now(timezone.utc).isoformat(),
            message="委托协议已取消"
        )

    def pay(
        self,
        request: DelegationPayRequest
    ) -> DelegationPayResponse:
        """
        步骤 4：委托支付执行

        执行实际的委托支付流程

        Args:
            request: 支付请求

        Returns:
            支付响应
        """
        # 构造支付请求载荷
        payment_request = {
            "request_id": request.request_id,
            "buyer_agent_id": request.buyer_agent_id,
            "delegation_id": request.delegation_id,
            "iac": request.iac,
            "merchant_id": request.merchant_id,
            "merchant_order_id": request.merchant_order_id,
            "cart_snapshot_hash": request.cart_snapshot_hash,
            "amount": f"{request.amount:.2f}",
            "currency": request.currency,
            "payment_method": request.payment_method,
            "payment_token": request.payment_token,
            "subaccount_info": request.subaccount_info,
            "description": request.description,
            "signature": request.signature,
            "signature_covered_fields": request.signature_covered_fields
        }

        # 执行支付
        result = self.payment_service.process_delegated_payment(payment_request)

        return DelegationPayResponse(
            success=result.success,
            payment_id=result.payment_id,
            transaction_id=result.transaction_id,
            status=result.status.value if result.status else None,
            amount=result.amount,
            currency=result.currency,
            message=result.message,
            error_code=result.error.code.value if result.error else None,
            error_message=result.error.message if result.error else None,
            details=result.details
        )

    def pay_from_payload(
        self,
        payload: Dict[str, Any]
    ) -> DelegationPayResponse:
        """
        从原始载荷执行委托支付

        Args:
            payload: 委托支付载荷字典

        Returns:
            支付响应
        """
        # 创建请求对象
        request = DelegationPayRequest(
            request_id=payload.get("request_id", ""),
            buyer_agent_id=payload.get("buyer_agent_id", ""),
            delegation_id=payload.get("delegation_id", ""),
            iac=payload.get("iac", ""),
            merchant_id=payload.get("merchant_id", ""),
            merchant_order_id=payload.get("merchant_order_id", ""),
            cart_snapshot_hash=payload.get("cart_snapshot_hash", ""),
            amount=float(payload.get("amount", "0")),
            currency=payload.get("currency", "CNY"),
            payment_method=payload.get("payment_method"),
            payment_token=payload.get("payment_token"),
            subaccount_info=payload.get("subaccount_info"),
            description=payload.get("description"),
            signature=payload.get("signature"),
            signature_covered_fields=payload.get("signature_covered_fields")
        )

        return self.pay(request)

    def build_payment_payload(
        self,
        buyer_agent_id: str,
        delegation_id: str,
        iac: str,
        merchant_id: str,
        merchant_order_id: str,
        cart_snapshot_hash: str,
        amount: float,
        currency: str = "CNY",
        use_subaccount: bool = False,
        subaccount_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        构建委托支付载荷

        Args:
            buyer_agent_id: 买方智能体 ID
            delegation_id: 委托标识
            iac: IAC 凭证
            merchant_id: 商户 ID
            merchant_order_id: 商户订单号
            cart_snapshot_hash: 购物车快照哈希
            amount: 支付金额
            currency: 币种
            use_subaccount: 是否使用子账户
            subaccount_id: 子账户 ID（如果 use_subaccount=True）

        Returns:
            支付载荷字典
        """
        import uuid
        from datetime import timezone

        # 创建一个临时的 payload 用于计算签名
        payload = DelegatedPaymentPayload.create(
            buyer_agent_id=buyer_agent_id,
            delegation_id=delegation_id,
            iac=iac,
            merchant_id=merchant_id,
            merchant_order_id=merchant_order_id,
            cart_snapshot_hash=cart_snapshot_hash,
            amount=amount,
            currency=currency
        )

        if use_subaccount and subaccount_id:
            payload.subaccount_info = SubAccountInfo(
                subaccount_id=subaccount_id,
                signature=f"mock_signature_{uuid.uuid4().hex[:16]}",
                signature_algorithm="ES256"
            )

        return payload.to_dict()