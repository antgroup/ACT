"""
即时支付模块 (Instant Payment)
实现 ACT 协议的即时支付流程
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from datetime import datetime
import uuid
import random
import string


@dataclass
class InstantPayRequest:
    """
    即时支付请求
    用户直接支付订单
    """
    order_id: str  # 订单 ID
    amount: float  # 支付金额
    payment_method: Optional[str] = "mock_payment"  # 支付方式
    user_id: Optional[str] = None  # 用户 ID
    currency: str = "CNY"  # 币种
    description: Optional[str] = None  # 支付描述
    callback_url: Optional[str] = None  # 回调 URL（用于异步通知）


@dataclass
class InstantPayResponse:
    """
    即时支付响应
    """
    success: bool
    payment_id: Optional[str] = None
    transaction_id: Optional[str] = None
    status: Optional[str] = None  # success/failed/pending
    amount: Optional[float] = None
    currency: Optional[str] = None
    message: str = ""
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


class InstantPaymentService:
    """
    即时支付服务
    处理用户直接支付的完整流程
    """

    def __init__(self, merchant_service=None):
        """
        初始化即时支付服务

        Args:
            merchant_service: 商户服务实例（可选，用于验证订单）
        """
        self.merchant_service = merchant_service
        self.payments: Dict[str, Dict[str, Any]] = {}
        print("[即时支付服务] 初始化完成")

    def pay(self, request: InstantPayRequest) -> InstantPayResponse:
        """
        处理即时支付

        流程：
        1. 验证订单
        2. 验证金额
        3. 执行支付
        4. 生成支付记录
        5. 返回结果

        Args:
            request: 即时支付请求

        Returns:
            即时支付响应
        """
        # 1. 验证订单
        if self.merchant_service:
            order_result = self.merchant_service.get_order(request.order_id)
            if not order_result.get("success"):
                return InstantPayResponse(
                    success=False,
                    message=f"订单不存在：{request.order_id}",
                    error_code="ORDER_NOT_FOUND"
                )

            order = order_result["data"]

            # 检查订单状态
            if order.get("status") == "paid":
                return InstantPayResponse(
                    success=False,
                    message="订单已支付，请勿重复支付",
                    error_code="ORDER_ALREADY_PAID"
                )

            # 验证金额
            expected_amount = order.get("total_amount", 0)
            if abs(request.amount - expected_amount) > 0.01:
                return InstantPayResponse(
                    success=False,
                    message=f"支付金额不正确，应付：¥{expected_amount:.2f}, 实付：¥{request.amount:.2f}",
                    error_code="AMOUNT_MISMATCH"
                )

        # 2. 生成支付 ID
        payment_id = f"INST{uuid.uuid4().hex[:16].upper()}"

        # 3. 生成交易 ID
        transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"

        # 4. 创建支付记录
        payment_record = {
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "order_id": request.order_id,
            "user_id": request.user_id,
            "amount": request.amount,
            "currency": request.currency,
            "payment_method": request.payment_method,
            "status": "success",
            "type": "INSTANT",
            "created_at": datetime.now().isoformat(),
            "description": request.description
        }

        # 5. 保存支付记录
        self.payments[payment_id] = payment_record

        # 6. 更新订单状态（如果提供了商户服务）
        if self.merchant_service and hasattr(self.merchant_service, 'update_order_status'):
            self.merchant_service.update_order_status(
                order_id=request.order_id,
                status="paid",
                payment_id=payment_id
            )

        print(f"[即时支付] 支付成功：{payment_id}, 订单：{request.order_id}, 金额：¥{request.amount:.2f}")

        return InstantPayResponse(
            success=True,
            payment_id=payment_id,
            transaction_id=transaction_id,
            status="success",
            amount=request.amount,
            currency=request.currency,
            message=f"支付成功，支付流水号：{payment_id}"
        )

    def get_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        查询支付记录

        Args:
            payment_id: 支付流水号

        Returns:
            支付记录或 None
        """
        return self.payments.get(payment_id)

    def get_payment_by_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        根据订单 ID 查询支付记录

        Args:
            order_id: 订单 ID

        Returns:
            支付记录或 None
        """
        for payment in self.payments.values():
            if payment.get("order_id") == order_id:
                return payment
        return None

    def refund(self, payment_id: str, amount: Optional[float] = None,
               reason: str = "用户申请退款") -> InstantPayResponse:
        """
        处理退款

        Args:
            payment_id: 支付流水号
            amount: 退款金额（全额退款为 None）
            reason: 退款原因

        Returns:
            退款响应
        """
        payment = self.payments.get(payment_id)
        if not payment:
            return InstantPayResponse(
                success=False,
                message="支付记录不存在",
                error_code="PAYMENT_NOT_FOUND"
            )

        if payment.get("status") == "refunded":
            return InstantPayResponse(
                success=False,
                message="该支付已退款",
                error_code="ALREADY_REFUNDED"
            )

        # 生成退款 ID
        refund_id = f"REF{uuid.uuid4().hex[:12].upper()}"

        # 计算退款金额
        refund_amount = amount if amount else payment.get("amount")

        # 更新支付状态
        payment["status"] = "refunded"
        payment["refund_id"] = refund_id
        payment["refund_amount"] = refund_amount
        payment["refund_reason"] = reason
        payment["refunded_at"] = datetime.now().isoformat()

        # 更新订单状态
        if self.merchant_service:
            self.merchant_service.update_order_status(
                order_id=payment["order_id"],
                status="refunded"
            )

        print(f"[即时支付] 退款成功：{refund_id}, 支付：{payment_id}, 金额：¥{refund_amount:.2f}")

        return InstantPayResponse(
            success=True,
            payment_id=payment_id,
            message=f"退款成功，退款流水号：{refund_id}",
            details={
                "refund_id": refund_id,
                "refund_amount": refund_amount
            }
        )