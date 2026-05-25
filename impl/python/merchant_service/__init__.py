"""
商户服务模块
提供商品管理和订单管理能力
这是一个独立的服务模块，不是 Agent
"""
from .service import MerchantService, merchant_service

__all__ = ['MerchantService', 'merchant_service']