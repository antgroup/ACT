"""
委托支付服务 (PSD-PAY-DEL Service)
实现 ACT 协议用户委托支付的完整业务流程
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import uuid
import random
import string

from .payload import (
    DelegatedPaymentPayload,
    IACDelegationInfo,
    SubAccountInfo,
    PaymentTokenInfo
)
from .validator import (
    DelegatedPaymentValidator,
    IACValidator,
    PaymentError,
    PaymentErrorCode
)


class PaymentStatus(Enum):
    """
    交易状态
    参考 ACT 协议定义的状态机
    """
    CREATE = "CREATE"  # 创建
    WAIT_BUYER_PAY = "WAIT_BUYER_PAY"  # 等待买家支付
    WAIT_SELLER_FULFILLMENT = "WAIT_SELLER_FULFILLMENT"  # 等待卖家履约
    WAIT_BUYER_RECEIPT = "WAIT_BUYER_RECEIPT"  # 等待买家回执
    TRADE_FINISHED = "TRADE_FINISHED"  # 交易完成
    TRADE_CLOSED = "TRADE_CLOSED"  # 交易关闭（退款或取消）


@dataclass
class PaymentResult:
    """
    支付结果
    """
    success: bool
    payment_id: Optional[str]
    transaction_id: Optional[str]
    status: Optional[PaymentStatus]
    amount: Optional[float]
    currency: Optional[str]
    message: Optional[str]
    error: Optional[PaymentError] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "success": self.success,
            "payment_id": self.payment_id,
            "transaction_id": self.transaction_id,
            "status": self.status.value if self.status else None,
            "amount": self.amount,
            "currency": self.currency,
            "message": self.message
        }
        if self.error:
            result["error"] = self.error.to_dict()
        if self.details:
            result["details"] = self.details
        return result


class DelegatedPaymentService:
    """
    委托支付服务
    实现 PSD-PAY-DEL 的完整支付流程
    """

    def __init__(
        self,
        iac_validator: Optional[IACValidator] = None,
        cumulative_amount_store: Optional[Dict[str, float]] = None
    ):
        """
        初始化委托支付服务

        Args:
            iac_validator: IAC 验证器
            cumulative_amount_store: 累计金额存储
        """
        self.iac_validator = iac_validator or IACValidator()
        self.validator = DelegatedPaymentValidator(iac_validator)
        self.cumulative_amount_store = cumulative_amount_store or {}

        # 支付记录存储
        self.payments: Dict[str, Dict[str, Any]] = {}

        # 已处理请求 ID（用于防重放）
        self.processed_requests: set = set()

        print("[委托支付服务] 初始化完成")

    def process_delegated_payment(
        self,
        request_payload: Dict[str, Any]
    ) -> PaymentResult:
        """
        处理委托支付请求

        完整流程：
        1. 请求验证（防重放、签名、IAC、约束）
        2. 执行扣款
        3. 生成支付凭证
        4. 返回结果并更新状态

        Args:
            request_payload: 委托支付请求载荷

        Returns:
            支付结果
        """
        # ===== 步骤 1：请求验证 =====
        is_valid, error = self.validator.validate_request(request_payload)

        if not is_valid:
            return PaymentResult(
                success=False,
                payment_id=None,
                transaction_id=None,
                status=None,
                amount=None,
                currency=None,
                message=error.message,
                error=error
            )

        # ===== 步骤 2：防重放检查 =====
        request_id = request_payload.get("request_id")
        if request_id in self.processed_requests:
            return PaymentResult(
                success=False,
                payment_id=None,
                transaction_id=None,
                status=None,
                amount=None,
                currency=None,
                message="请求已处理，疑似重放攻击",
                error=PaymentError(
                    code=PaymentErrorCode.REQUEST_DUPLICATE,
                    message="请求重复"
                )
            )

        # ===== 步骤 3：执行扣款 =====
        try:
            amount = float(request_payload.get("amount", "0"))
            currency = request_payload.get("currency", "CNY")
            merchant_id = request_payload.get("merchant_id", "")
            merchant_order_id = request_payload.get("merchant_order_id", "")

            # 模拟扣款操作
            payment_id = self._execute_payment(
                request_id=request_id,
                amount=amount,
                currency=currency,
                merchant_id=merchant_id,
                merchant_order_id=merchant_order_id,
                request_payload=request_payload
            )

            if not payment_id:
                return PaymentResult(
                    success=False,
                    payment_id=None,
                    transaction_id=None,
                    status=None,
                    amount=None,
                    currency=None,
                    message="扣款操作失败"
                )

            # ===== 步骤 4：更新累计金额 =====
            delegation_id = request_payload.get("delegation_id")
            if delegation_id:
                self.validator.update_cumulative_amount(delegation_id, amount)

            # ===== 步骤 5：标记请求已处理 =====
            self.processed_requests.add(request_id)

            # 获取支付记录
            payment = self.payments.get(payment_id, {})

            return PaymentResult(
                success=True,
                payment_id=payment.get("payment_id"),
                transaction_id=payment.get("transaction_id"),
                status=PaymentStatus.TRADE_FINISHED,
                amount=payment.get("amount"),
                currency=payment.get("currency"),
                message="支付成功",
                details={
                    "payment_id": payment.get("payment_id"),
                    "transaction_id": payment.get("transaction_id"),
                    "merchant_order_id": merchant_order_id,
                    "delegation_id": delegation_id
                }
            )

        except Exception as e:
            return PaymentResult(
                success=False,
                payment_id=None,
                transaction_id=None,
                status=None,
                amount=None,
                currency=None,
                message=f"支付处理异常：{str(e)}",
                error=PaymentError(
                    code=PaymentErrorCode.SYSTEM_ERROR,
                    message=str(e)
                )
            )

    def _execute_payment(
        self,
        request_id: str,
        amount: float,
        currency: str,
        merchant_id: str,
        merchant_order_id: str,
        request_payload: Dict[str, Any]
    ) -> Optional[str]:
        """
        执行实际扣款操作

        Args:
            request_id: 请求 ID
            amount: 金额
            currency: 币种
            merchant_id: 商户 ID
            merchant_order_id: 商户订单 ID
            request_payload: 完整请求载荷

        Returns:
            支付 ID
        """
        # 生成支付流水号
        payment_id = f"PAYDEL{uuid.uuid4().hex[:16].upper()}"

        # 生成交易流水号
        transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"

        # Check if using subaccount or payment token
        subaccount_info = request_payload.get("subaccount_info")
        payment_token = request_payload.get("payment_token")

        if subaccount_info:
            # Use subaccount payment
            if isinstance(subaccount_info, dict):
                subaccount_id = subaccount_info.get("subaccount_id")
            else:
                subaccount_id = getattr(subaccount_info, "subaccount_id", None)

            if not subaccount_id:
                return None

            # Check subaccount status (mock)
            subaccount_status = self._check_subaccount_status(subaccount_id)
            if not subaccount_status["valid"]:
                return None

            # Deduct from subaccount
            self._deduct_from_subaccount(subaccount_id, amount)
        elif payment_token:
            # Use payment token
            if isinstance(payment_token, dict):
                token = payment_token.get("token")
            else:
                token = getattr(payment_token, "token", None)

            if not token:
                return None

            # Mock payment token processing
            self._process_with_payment_token({"token": token})

        # 创建支付记录
        payment_record = {
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "request_id": request_id,
            "merchant_order_id": merchant_order_id,
            "amount": amount,
            "currency": currency,
            "status": PaymentStatus.TRADE_FINISHED.value,
            "created_at": datetime.now().isoformat(),
            "payment_method": "delegated_payment",
            "verification_result": {
                "iac_valid": True,
                "agent_signature_valid": True,
                "amount_verified": True
            }
        }

        self.payments[payment_id] = payment_record

        return payment_id

    def _check_subaccount_status(
        self,
        subaccount_id: str
    ) -> Dict[str, Any]:
        """
        检查子账户状态（mock）

        Args:
            subaccount_id: 子账户 ID

        Returns:
            账户状态信息
        """
        # 模拟账户状态
        return {
            "valid": True,
            "status": "ACTIVE",
            "balance": 10000.0,
            "frozen_amount": 0.0
        }

    def _deduct_from_subaccount(
        self,
        subaccount_id: str,
        amount: float
    ):
        """
        从子账户扣款（mock）

        Args:
            subaccount_id: 子账户 ID
            amount: 扣款金额
        """
        print(f"[子账户] 扣款：{subaccount_id} ¥{amount:.2f}")

    def _validate_payment_token(
        self,
        payment_token: Dict[str, Any]
    ) -> bool:
        """
        验证支付标记（mock）

        Args:
            payment_token: 支付标记信息

        Returns:
            是否有效
        """
        token = payment_token.get("token", "")
        # 模拟验证（真实场景需查询 PSP）
        return len(token) > 0

    def _process_with_payment_token(
        self,
        payment_token: Dict[str, Any]
    ):
        """
        使用支付标记处理支付（mock）

        Args:
            payment_token: 支付标记信息
        """
        token = payment_token.get("token", "")
        print(f"[支付标记] 处理支付：token={token[:10]}...")

    def get_payment_info(
        self,
        payment_id: str
    ) -> PaymentResult:
        """
        查询支付信息

        Args:
            payment_id: 支付流水号

        Returns:
            支付信息
        """
        payment = self.payments.get(payment_id)

        if not payment:
            return PaymentResult(
                success=False,
                payment_id=None,
                transaction_id=None,
                status=None,
                amount=None,
                currency=None,
                message=f"支付记录 {payment_id} 不存在"
            )

        return PaymentResult(
            success=True,
            payment_id=payment.get("payment_id"),
            transaction_id=payment.get("transaction_id"),
            status=PaymentStatus(payment.get("status", "CREATE")),
            amount=payment.get("amount"),
            currency=payment.get("currency"),
            message="获取支付信息成功",
            details=payment
        )

    def get_payment_by_order(
        self,
        merchant_order_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        根据商户订单号查询支付信息

        Args:
            merchant_order_id: 商户订单号

        Returns:
            支付记录或 None
        """
        for payment in self.payments.values():
            if payment.get("merchant_order_id") == merchant_order_id:
                return payment
        return None

    def get_cumulative_amount(
        self,
        delegation_id: str
    ) -> float:
        """
        获取授权累计扣款确认额

        Args:
            delegation_id: 委托标识

        Returns:
            累计金额
        """
        return self.validator.get_cumulative_amount(delegation_id)

    def revoke_delegation(
        self,
        delegation_id: str
    ) -> bool:
        """
        吊销委托授权

        Args:
            delegation_id: 委托标识

        Returns:
            是否成功
        """
        # 添加吊销状态（实际应存入持久化存储）
        print(f"[委托] 吊销授权：{delegation_id}")
        return True

    def cancel_pending_payment(
        self,
        payment_id: str
    ) -> PaymentResult:
        """
        取消待处理支付

        Args:
            payment_id: 支付流水号

        Returns:
            取消结果
        """
        payment = self.payments.get(payment_id)

        if not payment:
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                transaction_id=None,
                status=None,
                amount=None,
                currency=None,
                message=f"支付 {payment_id} 不存在"
            )

        if payment.get("status") != PaymentStatus.CREATE.value:
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                transaction_id=None,
                status=None,
                amount=None,
                currency=None,
                message="只能取消 CREATE 状态的支付"
            )

        # 更新状态
        payment["status"] = PaymentStatus.TRADE_CLOSED.value
        payment["closed_at"] = datetime.now().isoformat()
        payment["close_reason"] = "cancel_request"

        return PaymentResult(
            success=True,
            payment_id=payment_id,
            transaction_id=payment.get("transaction_id"),
            status=PaymentStatus.TRADE_CLOSED,
            amount=payment.get("amount"),
            currency=payment.get("currency"),
            message="支付已取消"
        )