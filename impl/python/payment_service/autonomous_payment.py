"""
自主支付模块 (Autonomous Payment)
实现 ACT 协议的自主支付流程
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
import uuid


@dataclass
class AutonomousPayRequest:
    """
    自主支付请求
    智能体基于预设策略自主决策支付
    """
    request_id: str
    agent_id: str  # 智能体 ID
    principal_id: str  # 委托人 ID
    merchant_id: str
    order_id: str
    amount: float
    strategy_id: str  # 使用的支付策略
    cart_snapshot_hash: str
    currency: str = "CNY"
    context: Optional[Dict[str, Any]] = None  # 支付上下文


@dataclass
class AutonomousPayResponse:
    """
    自主支付响应
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


@dataclass
class PaymentStrategy:
    """
    支付策略
    定义自主支付的规则和约束
    """
    strategy_id: str
    name: str
    description: str
    max_single_amount: float  # 单笔上限
    max_daily_amount: float  # 日累计上限
    allowed_merchants: List[str]  # 允许商户白名单
    allowed_categories: List[str]  # 允许商品类别
    enabled: bool = True


class AutonomousPaymentService:
    """
    自主支付服务
    实现智能体基于策略的自主支付
    """

    def __init__(self):
        """
        初始化自主支付服务
        """
        self.strategies: Dict[str, PaymentStrategy] = {}
        self.payments: Dict[str, Dict[str, Any]] = {}
        self.daily_limits: Dict[str, Dict[str, float]] = {}  # {principal_id: {date: total}}
        print("[自主支付服务] 初始化完成")

    def register_strategy(self, strategy: PaymentStrategy) -> bool:
        """
        注册支付策略

        Args:
            strategy: 支付策略

        Returns:
            是否注册成功
        """
        if strategy.enabled:
            self.strategies[strategy.strategy_id] = strategy
            print(f"[自主支付] 策略已注册：{strategy.strategy_id} - {strategy.name}")
        return True

    def execute(self, request: AutonomousPayRequest) -> AutonomousPayResponse:
        """
        执行自主支付

        流程：
        1. 验证策略存在
        2. 验证策略启用状态
        3. 执行策略约束检查
        4. 检查日累计限额
        5. 执行支付

        Args:
            request: 自主支付请求

        Returns:
            自主支付响应
        """
        # 1. 验证策略是否存在
        strategy = self.strategies.get(request.strategy_id)
        if not strategy:
            return AutonomousPayResponse(
                success=False,
                message=f"策略不存在：{request.strategy_id}",
                error_code="STRATEGY_NOT_FOUND"
            )

        # 2. 验证策略启用状态
        if not strategy.enabled:
            return AutonomousPayResponse(
                success=False,
                message="策略已禁用",
                error_code="STRATEGY_DISABLED"
            )

        # 3. 检查单笔金额限制
        if request.amount > strategy.max_single_amount:
            return AutonomousPayResponse(
                success=False,
                message=f"金额超出策略限制：¥{request.amount:.2f} > ¥{strategy.max_single_amount:.2f}",
                error_code="AMOUNT_EXCEEDS_LIMIT"
            )

        # 4. 检查商户白名单
        if strategy.allowed_merchants and request.merchant_id not in strategy.allowed_merchants:
            return AutonomousPayResponse(
                success=False,
                message=f"商户不在允许列表中",
                error_code="MERCHANT_NOT_ALLOWED"
            )

        # 5. 检查日累计限额
        today = datetime.now(timezone.utc).date().isoformat()
        principal_id = request.principal_id

        if principal_id not in self.daily_limits:
            self.daily_limits[principal_id] = {}

        current_daily = self.daily_limits[principal_id].get(today, 0.0)

        if current_daily + request.amount > strategy.max_daily_amount:
            return AutonomousPayResponse(
                success=False,
                message=f"日累计额度不足：已用¥{current_daily:.2f}, 剩余¥{strategy.max_daily_amount - current_daily:.2f}",
                error_code="DAILY_LIMIT_EXCEEDED"
            )

        # 6. 执行支付
        payment_id = f"AUTO{uuid.uuid4().hex[:16].upper()}"
        transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"

        payment_record = {
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "principal_id": principal_id,
            "agent_id": request.agent_id,
            "merchant_id": request.merchant_id,
            "order_id": request.order_id,
            "amount": request.amount,
            "currency": request.currency,
            "strategy_id": request.strategy_id,
            "status": "success",
            "type": "AUTONOMOUS",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        self.payments[payment_id] = payment_record
        self.daily_limits[principal_id][today] = current_daily + request.amount

        print(f"[自主支付] 支付成功：{payment_id}, 策略：{request.strategy_id}, 金额：¥{request.amount:.2f}")

        return AutonomousPayResponse(
            success=True,
            payment_id=payment_id,
            transaction_id=transaction_id,
            status="success",
            amount=request.amount,
            currency=request.currency,
            message="自主支付成功"
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

    def update_strategy(self, strategy_id: str, enabled: Optional[bool] = None,
                       max_single_amount: Optional[float] = None) -> bool:
        """
        更新支付策略

        Args:
            strategy_id: 策略 ID
            enabled: 是否启用
            max_single_amount: 单笔上限

        Returns:
            是否更新成功
        """
        strategy = self.strategies.get(strategy_id)
        if not strategy:
            return False

        if enabled is not None:
            strategy.enabled = enabled

        if max_single_amount is not None:
            strategy.max_single_amount = max_single_amount

        print(f"[自主支付] 策略已更新：{strategy_id}")
        return True