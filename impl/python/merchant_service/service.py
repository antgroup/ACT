"""
商户服务模块
提供商品管理和订单管理能力
这是一个独立的服务模块，不是 Agent
"""
import random
import string
from typing import Dict, List, Optional, Callable
from datetime import datetime


class MerchantService:
    """
    商户服务类
    职责：管理商品库存、处理订单创建和查询
    """

    # 商品变更事件钩子 - 使用实例级别存储
    def __init__(self):
        """初始化商户服务"""
        self._on_product_changed: Optional[Callable] = None
        # 商品数据库
        self.products = [
            {
                "item_id": "P001",
                "name": "Apple",
                "price": 5.99,
                "stock": 100,
                "description": "新鲜红苹果，香甜可口",
                "category": "水果",
                "tags": ["healthy", "snack", "fresh"],
                "supplier": "fruit-farm-001"
            },
            {
                "item_id": "P002",
                "name": "Banana",
                "price": 3.99,
                "stock": 150,
                "description": "进口香蕉，营养丰富",
                "category": "水果",
                "tags": ["healthy", "snack", "energy"],
                "supplier": "import-fruits-002"
            },
            {
                "item_id": "P003",
                "name": "Orange",
                "price": 4.99,
                "stock": 80,
                "description": "新鲜橙子，维 C 满满",
                "category": "水果",
                "tags": ["healthy", "vitamin", "fresh"],
                "supplier": "citrus-grove-003"
            },
            {
                "item_id": "P004",
                "name": "Grape",
                "price": 8.99,
                "stock": 60,
                "description": "无籽葡萄，甜度高",
                "category": "水果",
                "tags": ["sweet", "snack", "fresh"],
                "supplier": "vineyard-004"
            }
        ]

        # 订单数据库
        self.orders: Dict[str, Dict] = {}

        # 商品 ID 生成器
        self._next_item_id = 100

        print("[商户服务] 初始化完成，商品数量:", len(self.products))

    @classmethod
    def set_product_changed_callback(self, callback: Callable):
        """设置商品变更事件处理器"""
        self._on_product_changed = callback

    def _notify_product_changed(self, product: Dict):
        """通知商品变更"""
        if self._on_product_changed:
            self._on_product_changed(product)

    def register_product(
        self,
        name: str,
        price: float,
        category: str,
        description: str = "",
        stock: int = 100,
        tags: Optional[List[str]] = None,
        supplier_id: Optional[str] = None
    ) -> Dict:
        """
        注册新商品到市场

        Args:
            name: 商品名称
            price: 商品价格
            category: 商品类别
            description: 商品描述
            stock: 初始库存
            tags: 商品标签列表
            supplier_id: 供应商 ID

        Returns:
            Dict: 注册结果
        """
        try:
            # 生成商品 ID
            item_id = f"P{self._next_item_id:03d}"
            self._next_item_id += 1

            # 创建商品
            product = {
                "item_id": item_id,
                "name": name,
                "price": price,
                "category": category,
                "description": description,
                "stock": stock,
                "tags": tags or [],
                "supplier_id": supplier_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # 添加到商品库
            self.products.append(product)

            print(f"[商户服务] 商品注册成功：{item_id} - {name}")

            # 通知商品变更
            self._notify_product_changed(product)

            return {
                "success": True,
                "data": product.copy(),
                "message": f"商品注册成功，商品 ID: {item_id}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"商品注册失败：{str(e)}"
            }

    def get_product_list(self) -> Dict:
        """获取所有商品列表"""
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
                "message": f"获取商品列表失败：{str(e)}"
            }

    def get_product_by_id(self, item_id: str) -> Dict:
        """根据商品 ID 获取商品详情"""
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
                "message": f"获取商品详情失败：{str(e)}"
            }

    def update_product_stock(self, item_id: str, quantity: int) -> Dict:
        """更新商品库存"""
        try:
            for product in self.products:
                if product["item_id"] == item_id:
                    new_stock = product["stock"] + quantity
                    if new_stock < 0:
                        return {
                            "success": False,
                            "message": f"库存不足，当前库存：{product['stock']} 件"
                        }
                    product["stock"] = new_stock
                    product["updated_at"] = datetime.now().isoformat()
                    return {
                        "success": True,
                        "data": product.copy(),
                        "message": f"库存更新成功，新库存：{new_stock} 件"
                    }

            return {
                "success": False,
                "message": f"商品 {item_id} 不存在"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"更新库存失败：{str(e)}"
            }

    def delete_product(self, item_id: str) -> Dict:
        """删除商品"""
        try:
            for i, product in enumerate(self.products):
                if product["item_id"] == item_id:
                    deleted = self.products.pop(i)
                    print(f"[商户服务] 商品已删除：{item_id} - {deleted['name']}")
                    self._notify_product_changed(deleted)
                    return {
                        "success": True,
                        "data": deleted.copy(),
                        "message": f"商品已删除"
                    }

            return {
                "success": False,
                "message": f"商品 {item_id} 不存在"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"删除商品失败：{str(e)}"
            }

    def create_order(
        self,
        item_id: str,
        quantity: int = 1,
        customer_id: str = "default"
    ) -> Dict:
        """创建订单"""
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
                    "message": f"库存不足，当前库存：{product['stock']} 件"
                }

            # 生成订单 ID
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
                "status": "pending_payment",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # 保存订单
            self.orders[order_id] = order

            # 扣减库存
            product["stock"] -= quantity

            print(f"[商户服务] 订单创建成功：{order_id}, 商品：{product['name']}, 数量：{quantity}")

            return {
                "success": True,
                "data": order.copy(),
                "message": f"订单创建成功，订单号：{order_id}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"创建订单失败：{str(e)}"
            }

    def get_order(self, order_id: str) -> Dict:
        """查询订单信息"""
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
                "message": f"查询订单失败：{str(e)}"
            }

    def update_order_status(self, order_id: str, status: str, payment_id: str = None) -> Dict:
        """更新订单状态"""
        try:
            if order_id not in self.orders:
                return {
                    "success": False,
                    "data": None,
                    "message": f"订单 {order_id} 不存在"
                }

            self.orders[order_id]["status"] = status
            if payment_id:
                self.orders[order_id]["payment_id"] = payment_id
            self.orders[order_id]["updated_at"] = datetime.now().isoformat()

            print(f"[商户服务] 订单状态已更新：{order_id} -> {status}")

            return {
                "success": True,
                "data": self.orders[order_id].copy(),
                "message": f"订单状态已更新为：{status}"
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"更新订单状态失败：{str(e)}"
            }

    def get_all_orders(self, customer_id: str = None) -> Dict:
        """获取所有订单（可按客户筛选）"""
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
                "message": f"获取订单列表失败：{str(e)}"
            }


# 创建全局商户服务实例
merchant_service = MerchantService()