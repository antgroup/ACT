"""
市场服务模块
为代理提供商品动态发现、搜索和推荐能力
"""
import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class MarketService:
    """
    市场服务类
    职责：商品注册、商品搜索、智能推荐
    """

    def __init__(self):
        """初始化市场服务"""
        # 商品数据库 - 代理可以动态添加商品
        self.products: List[Dict[str, Any]] = []

        # 供应商数据库
        self.suppliers: Dict[str, Dict[str, Any]] = {}

        # 商品 ID 生成器
        self._next_item_id = 1000

        # 自动触发器 - 当库存低于阈值时自动触发购买
        self.stock_alert_rules: List[Dict[str, Any]] = []

        # 定时触发器 - 按指定时间触发购买
        self.scheduled_purchase_rules: List[Dict[str, Any]] = []

        print("[市场服务] 初始化完成")

    def register_product(
        self,
        name: str,
        price: float,
        category: str,
        description: str = "",
        stock: int = 100,
        tags: Optional[List[str]] = None,
        supplier_id: Optional[str] = None,
        low_stock_threshold: Optional[int] = None
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
            low_stock_threshold: 低库存预警阈值（可选）

        Returns:
            Dict: 注册结果
        """
        try:
            # 生成商品 ID
            item_id = f"MCH-{self._next_item_id:04d}"
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
                "low_stock_threshold": low_stock_threshold,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # 添加到商品库
            self.products.append(product)

            # 如果有供应商 ID，注册供应商
            if supplier_id:
                if supplier_id not in self.suppliers:
                    self.suppliers[supplier_id] = {
                        "supplier_id": supplier_id,
                        "products": [],
                        "registered_at": datetime.now().isoformat()
                    }
                self.suppliers[supplier_id]["products"].append(item_id)

            # 如果设置了低库存阈值，添加预警规则
            if low_stock_threshold is not None:
                self.stock_alert_rules.append({
                    "item_id": item_id,
                    "threshold": low_stock_threshold,
                    "action": "notify",
                    "created_at": datetime.now().isoformat()
                })

            print(f"[市场服务] 商品注册成功：{item_id} - {name}")

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

    def search_products(
        self,
        keywords: Optional[str] = None,
        categories: Optional[List[str]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """
        搜索商品

        Args:
            keywords: 关键词搜索
            categories: 类别过滤
            min_price: 最低价格
            max_price: 最高价格
            tags: 标签过滤

        Returns:
            Dict: 搜索结果
        """
        try:
            results = self.products.copy()

            # 关键词搜索
            if keywords:
                keywords_lower = keywords.lower()
                results = [
                    p for p in results
                    if keywords_lower in p["name"].lower()
                    or keywords_lower in p.get("description", "").lower()
                    or keywords_lower in p["category"].lower()
                ]

            # 类别过滤
            if categories:
                results = [p for p in results if p["category"] in categories]

            # 价格范围过滤
            if min_price is not None:
                results = [p for p in results if p["price"] >= min_price]
            if max_price is not None:
                results = [p for p in results if p["price"] <= max_price]

            # 标签过滤
            if tags:
                results = [
                    p for p in results
                    if any(tag in p.get("tags", []) for tag in tags)
                ]

            return {
                "success": True,
                "data": results,
                "total_count": len(results),
                "message": f"找到 {len(results)} 个商品"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"搜索失败：{str(e)}"
            }

    def get_low_stock_products(self) -> Dict:
        """
        获取库存低于阈值的商品

        Returns:
            Dict: 低库存商品列表
        """
        try:
            low_stock = [
                p for p in self.products
                if p.get("low_stock_threshold") is not None
                and p["stock"] <= p["low_stock_threshold"]
            ]

            print(f"[市场服务] 低库存商品数量：{len(low_stock)}")

            return {
                "success": True,
                "data": low_stock,
                "total_count": len(low_stock),
                "message": f"发现 {len(low_stock)} 个低库存商品"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"查询低库存失败：{str(e)}"
            }

    def add_scheduled_purchase(
        self,
        item_id: str,
        scheduled_time: str,
        quantity: int = 1,
        max_price: Optional[float] = None,
        description: str = ""
    ) -> Dict:
        """
        添加定时购买任务

        Args:
            item_id: 商品 ID
            scheduled_time: 计划执行时间 (ISO 格式)
            quantity: 购买数量
            max_price: 最高允许价格
            description: 任务描述

        Returns:
            Dict: 任务创建结果
        """
        try:
            # 验证商品存在
            product = self.get_product_by_id(item_id)
            if not product["success"]:
                return product

            # 创建定时任务
            task_id = f"SCH-{self._next_item_id:04d}"
            self._next_item_id += 1

            scheduled_task = {
                "task_id": task_id,
                "item_id": item_id,
                "product_name": product["data"]["name"],
                "scheduled_time": scheduled_time,
                "quantity": quantity,
                "max_price": max_price,
                "description": description,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }

            self.scheduled_purchase_rules.append(scheduled_task)

            print(f"[市场服务] 定时购买任务创建：{task_id} - {scheduled_time}")

            return {
                "success": True,
                "data": scheduled_task.copy(),
                "message": f"定时购买任务创建成功，任务 ID: {task_id}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"创建定时任务失败：{str(e)}"
            }

    def get_pending_scheduled_tasks(self) -> Dict:
        """
        获取待执行的定时任务

        Returns:
            Dict: 待执行任务列表
        """
        try:
            # 检查是否有任务需要执行（这里简化处理）
            pending_tasks = [
                t for t in self.scheduled_purchase_rules
                if t["status"] == "pending"
            ]

            return {
                "success": True,
                "data": pending_tasks,
                "total_count": len(pending_tasks),
                "message": f"发现 {len(pending_tasks)} 个待执行任务"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"查询定时任务失败：{str(e)}"
            }

    def recommend_products(
        self,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        根据用户偏好推荐商品

        Args:
            user_preferences: 用户偏好 {categories, tags, max_price}

        Returns:
            Dict: 推荐结果
        """
        try:
            recommendations = self.products.copy()

            # 过滤类别偏好
            if user_preferences:
                if "categories" in user_preferences:
                    recommendations = [
                        p for p in recommendations
                        if p["category"] in user_preferences["categories"]
                    ]
                if "max_price" in user_preferences:
                    recommendations = [
                        p for p in recommendations
                        if p["price"] <= user_preferences["max_price"]
                    ]
                if "tags" in user_preferences:
                    recommendations = [
                        p for p in recommendations
                        if any(tag in p.get("tags", []) for tag in user_preferences["tags"])
                    ]

            # 简单排序：按价格从低到高
            recommendations.sort(key=lambda x: x["price"])

            return {
                "success": True,
                "data": recommendations[:10],  # 返回前 10 个推荐
                "total_count": len(recommendations),
                "message": f"推荐了 {len(recommendations)} 个商品"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"推荐失败：{str(e)}"
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

    def get_all_products(self) -> Dict:
        """获取所有商品"""
        return {
            "success": True,
            "data": self.products.copy(),
            "total_count": len(self.products),
            "message": "获取商品列表成功"
        }


# 创建全局市场服务实例
market_service = MarketService()