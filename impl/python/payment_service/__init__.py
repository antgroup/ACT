"""
支付服务模块
提供订单支付处理能力
这是一个独立的服务模块，不是 Agent
"""
from .service import PaymentService

__all__ = ['PaymentService']