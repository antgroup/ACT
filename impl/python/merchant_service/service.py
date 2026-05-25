"""
商户服务模块
提供商品管理和订单管理能力
这是一个独立的服务模块，不是 Agent
"""
import random
import string
from typing import Dict, List, Optional
from datetime import datetime


class MerchantService:
    """
    商户服务类
    职责：管理商品库存、处理订单创建和查询
    """
    
    def __init__(self):
        """初始化商户服务"""
        # 商品数据库
        self.products = [
            {
                "item_id": "P001",
                "name": "Apple",
                "price": 5.99,
                "stock": 100,
                "description": "新鲜红苹果，香甜可口",
                "category": "水果"
            },
            {
                "item_id": "P002",
                "name": "Banana",
                "price": 3.99,
                "stock": 150,
                "description": "进口香蕉，营养丰富",
                "category": "水果"
            },
            {
                "item_id": "P003",
                "name": "Orange",
                "price": 4.99,
                "stock": 80,
                "description": "新鲜橙子，维C满满",
                "category": "水果"
            },
            {
                "item_id": "P004",
                "name": "Grape",
                "price": 8.99,
                "stock": 60,
                "description": "无籽葡萄，甜度高",
                "category": "水果"
            }
        ]
        
        # 订单数据库
        self.orders: Dict[str, Dict] = {}
        
        print("[商户服务] 初始化完成，商品数量:", len(self.products))
    
    def get_product_list(self) -> Dict:
        """
        获取所有商品列表
        
        Returns:
            Dict: {
                "success": bool,
                "data": List[Dict] 商品列表,
                "message": str
            }
        """
        try:
            return {
                "success": True,
                "data": self.products.copy(),
                "total_count": len(self.products),
                "message": "获取商品列表成功"
            }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"获取商品列表失败: {str(e)}"
            }
    
    def get_product_by_id(self, item_id: str) -> Dict:
        """
        根据商品ID获取商品详情
        
        Args:
            item_id: 商品ID
            
        Returns:
            Dict: {
                "success": bool,
                "data": Dict 商品信息,
                "message": str
            }
        """
        try:
            for product in self.products:
                if product["item_id"] == item_id:
                    return {
                        "success": True,
                        "data": product.copy(),
                        "message": "获取商品详情成功"
                    }
            
            return {
                "success": False,
                "data": None,
                "message": f"商品 {item_id} 不存在"
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"获取商品详情失败: {str(e)}"
            }
    
    def create_order(self, item_id: str, quantity: int = 1, customer_id: str = "default") -> Dict:
        """
        创建订单
        
        Args:
            item_id: 商品ID
            quantity: 购买数量
            customer_id: 客户ID
            
        Returns:
            Dict: {
                "success": bool,
                "data": Dict 订单信息,
                "message": str
            }
        """
        try:
            # 查找商品
            product = None
            for p in self.products:
                if p["item_id"] == item_id:
                    product = p
                    break
            
            if not product:
                return {
                    "success": False,
                    "data": None,
                    "message": f"商品 {item_id} 不存在"
                }
            
            # 检查库存
            if product["stock"] < quantity:
                return {
                    "success": False,
                    "data": None,
                    "message": f"库存不足，当前库存: {product['stock']} 件"
                }
            
            # 生成订单ID
            order_id = "ORD" + ''.join(random.choices(string.digits, k=8))
            
            # 计算总价
            unit_price = product["price"]
            total_amount = unit_price * quantity
            
            # 创建订单
            order = {
                "order_id": order_id,
                "customer_id": customer_id,
                "item_id": item_id,
                "product_name": product["name"],
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": total_amount,
                "status": "pending_payment",  # 待支付
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # 保存订单
            self.orders[order_id] = order
            
            # 扣减库存
            product["stock"] -= quantity
            
            print(f"[商户服务] 订单创建成功: {order_id}, 商品: {product['name']}, 数量: {quantity}")
            
            return {
                "success": True,
                "data": order.copy(),
                "message": f"订单创建成功，订单号: {order_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"创建订单失败: {str(e)}"
            }
    
    def get_order(self, order_id: str) -> Dict:
        """
        查询订单信息
        
        Args:
            order_id: 订单ID
            
        Returns:
            Dict: {
                "success": bool,
                "data": Dict 订单信息,
                "message": str
            }
        """
        try:
            if order_id not in self.orders:
                return {
                    "success": False,
                    "data": None,
                    "message": f"订单 {order_id} 不存在"
                }
            
            return {
                "success": True,
                "data": self.orders[order_id].copy(),
                "message": "获取订单信息成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"查询订单失败: {str(e)}"
            }
    
    def update_order_status(self, order_id: str, status: str, payment_id: str = None) -> Dict:
        """
        更新订单状态（由支付服务调用）
        
        Args:
            order_id: 订单ID
            status: 新状态
            payment_id: 支付流水号（可选）
            
        Returns:
            Dict: {
                "success": bool,
                "data": Dict 更新后的订单信息,
                "message": str
            }
        """
        try:
            if order_id not in self.orders:
                return {
                    "success": False,
                    "data": None,
                    "message": f"订单 {order_id} 不存在"
                }
            
            order = self.orders[order_id]
            order["status"] = status
            order["updated_at"] = datetime.now().isoformat()
            
            if payment_id:
                order["payment_id"] = payment_id
            
            print(f"[商户服务] 订单状态更新: {order_id} -> {status}")
            
            return {
                "success": True,
                "data": order.copy(),
                "message": f"订单状态更新为: {status}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"更新订单状态失败: {str(e)}"
            }
    
    def get_all_orders(self, customer_id: str = None) -> Dict:
        """
        获取所有订单（可按客户筛选）
        
        Args:
            customer_id: 客户ID（可选）
            
        Returns:
            Dict: {
                "success": bool,
                "data": List[Dict] 订单列表,
                "message": str
            }
        """
        try:
            if customer_id:
                orders = [
                    order for order in self.orders.values()
                    if order["customer_id"] == customer_id
                ]
            else:
                orders = list(self.orders.values())
            
            return {
                "success": True,
                "data": orders,
                "total_count": len(orders),
                "message": "获取订单列表成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"获取订单列表失败: {str(e)}"
            }


# 创建全局商户服务实例
merchant_service = MerchantService()