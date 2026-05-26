"""
支付服务模块 (Payment Service)
实现 ACT 协议的三种支付模式：
1. 即时支付 (Instant Payment) - 用户直接支付
2. 委托支付 (Delegated Payment) - 授权智能体代付 (PSD-PAY-DEL)
3. 自主支付 (Autonomous Payment) - 智能体自主决策支付

架构角色：
- 用户 (User/Principal): 发起支付请求
- 商户服务 (Merchant Service): 商品管理（上架/下架/编辑）
- 支付服务 (Payment Service): 支付处理（三种支付模式）
- 智能体 (Agent): 代表用户执行委托/自主支付
"""

from .service import PaymentService
from .instant_payment import InstantPaymentService, InstantPayRequest, InstantPayResponse
from .delegated_payment import (
    DelegatedPaymentService,
    DelegationApplyRequest,
    DelegationPayRequest,
    DelegationPayResponse,
    DelegationApplyResponse,
    DelegationCancelRequest
)
from .autonomous_payment import AutonomousPaymentService, AutonomousPayRequest, AutonomousPayResponse

__all__ = [
    # Core
    'PaymentService',
    # Instant Payment
    'InstantPaymentService',
    'InstantPayRequest',
    'InstantPayResponse',
    # Delegated Payment (PSD-PAY-DEL)
    'DelegatedPaymentService',
    'DelegationApplyRequest',
    'DelegationPayRequest',
    'DelegationPayResponse',
    'DelegationApplyResponse',
    'DelegationCancelRequest',
    # Autonomous Payment
    'AutonomousPaymentService',
    'AutonomousPayRequest',
    'AutonomousPayResponse'
]