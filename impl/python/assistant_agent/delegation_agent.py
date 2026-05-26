"""
委托支付 Agent 模块
负责处理与委托支付相关的用户指令
"""
from typing import Dict, Any, Optional
import re
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from payment_service.delegated_payment import (
    DelegatedPaymentService,
    DelegationApplyRequest,
    DelegationCancelRequest
)
from merchant_service.service import merchant_service


class DelegationAgent:
    """
    委托支付 Agent
    负责理解用户的委托指令，与用户交互完成委托协议签约和管理
    """

    def __init__(self):
        """初始化委托支付 Agent"""
        self.delegated_service = DelegatedPaymentService()
        self.active_delegation: Optional[Dict[str, Any]] = None
        self.delegation_requests: Dict[str, Dict[str, Any]] = {}

    def process_delegation_command(self, user_input: str) -> str:
        """
        处理委托支付相关的用户指令

        Args:
            user_input: 用户的自然语言指令

        Returns:
            Agent 的响应
        """
        user_input_lower = user_input.lower()

        # 识别指令类型
        if any(cmd in user_input_lower for cmd in ["开设委托", "创建委托", "建立委托", "create delegation", "new delegation"]):
            return self._handle_create_delegation(user_input)

        if any(cmd in user_input_lower for cmd in ["查询委托", "查看委托", "委托状态", "delegation status", "show delegation"]):
            return self._handle_query_delegation()

        if any(cmd in user_input_lower for cmd in ["取消委托", "吊销委托", "结束委托", "cancel delegation", "revoke delegation"]):
            return self._handle_cancel_delegation()

        if any(cmd in user_input_lower for cmd in ["购买", "下单", "买", "buy", "order"]):
            return self._handle_commerce_purchase(user_input)

        if any(cmd in user_input_lower for cmd in ["查看商品", "看看商品", "商品列表", "list product", "show product"]):
            return self._handle_view_products()

        # 默认响应
        return self._get_delegation_welcome(user_input)

    def _handle_create_delegation(self, user_input: str) -> str:
        """
        处理开设委托指令

        解析用户输入的额度限制，创建委托协议
        示例指令：
        - "开设委托 5000 元额度"
        - "授权智能体买东西，每次最多 500 元"
        - "帮我授权智能体，总额 10000 元，单笔 2000 元"
        """
        # 提取金额信息
        max_total = self._extract_amount(user_input)
        max_single = self._extract_single_limit(user_input)

        if not max_total or max_total <= 0:
            max_total = 5000.0  # 默认额度

        if not max_single or max_single <= 0:
            # 默认单笔为总额的 20%，最多不超过总额的一半
            max_single = min(max_total * 0.2, max_total / 2)
            if max_single < 100:
                max_single = 100  # 最低单笔限额

        delegation_id = f"delegation-{int(time.time() * 1000)}"
        principal_id = "did:act:user-shopping-assistant"
        agent_id = "did:act:agent-shopping"

        # 创建委托协议
        request = DelegationApplyRequest(
            principal_id=principal_id,
            agent_id=agent_id,
            delegation_id=delegation_id,
            max_total_amount=max_total,
            max_single_amount=max_single,
            delegation_purpose="智能购物助手自动购买授权"
        )

        result = self.delegated_service.apply(request)

        if result.max_total_amount > 0:
            self.active_delegation = {
                "delegation_id": result.delegation_id,
                "iac": result.iac[:100] + "..." if len(result.iac) > 100 else result.iac,
                "max_total": result.max_total_amount,
                "max_single": result.max_single_amount or 0,
                "principal_id": principal_id,
                "agent_id": agent_id
            }
            self.delegation_requests[delegation_id] = {
                "request": request,
                "response": result,
                "created_at": str(result.issued_at)
            }
            return (
                f"[OK] **委托协议已签发**!\n\n"
                f"**委托协议详细信息**:\n"
                f"   • **委托 ID**: `{result.delegation_id[:30] if len(result.delegation_id) > 30 else result.delegation_id}...`\n"
                f"   • **总额度**: ¥{result.max_total_amount:.2f}\n"
                f"   • **单笔上限**: ¥{result.max_single_amount or 0:.2f}\n\n"
                f"**可以对我说的委托指令**:\n"
                f"• 查询委托状态\n"
                f"• 购买 {self._extract_item_name(user_input) or '商品'}\n"
                f"• 取消委托"
            )
        else:
            return f"[Error] 开设委托失败：{result.message}"

    def _handle_query_delegation(self) -> str:
        """处理查询委托状态的指令"""
        if not self.active_delegation:
            return (
                "**暂无活跃的委托协议**\n\n"
                "**可以对我说：**\n"
                "• 开设委托 5000\n"
                "• 创建委托 10000"
            )

        delegation = self.active_delegation
        cumulative = self.delegated_service.get_cumulative_amount(
            delegation["delegation_id"]
        )
        remaining = delegation["max_total"] - cumulative

        status_indicator = "🟢 启用中" if remaining > 0 else "🔴 已用完"

        return (
            f"**委托协议状态**\n\n"
            f"状态：**{status_indicator}**\n\n"
            f"**委托详细信息**:\n"
            f"   • **委托 ID**: `{delegation['delegation_id'][:30]}...`\n"
            f"   • **总额度**: ¥{delegation['max_total']:.2f}\n"
            f"   • **累计支付**: ¥{cumulative:.2f}\n"
            f"   • **剩余额度**: ¥{remaining:.2f}\n\n"
            f"**可以对我说的委托指令**:\n"
            f"• 查看委托 IAC 凭证\n"
            f"• 购买 {self._extract_item_name('') or '商品'}\n"
            f"• 取消委托"
        )

    def _handle_cancel_delegation(self) -> str:
        """处理取消委托的指令"""
        if not self.active_delegation:
            return "**无活跃委托可取消**"

        delegation_id = self.active_delegation["delegation_id"]

        result = self.delegated_service.cancel(
            delegation_id,
            "User requested cancellation"
        )

        if result.get("success"):
            self.active_delegation = None
            return (
                f"[OK] **委托协议已取消**\n\n"
                f"所有后续委托支付将不再可用。"
            )
        else:
            return f"[Error] 取消失败：{result.get('message', '未知错误')}"

    def _handle_commerce_purchase(self, user_input: str) -> str:
        """
        处理使用委托协议进行购买的指令

        解析用户想购买商品，检查额度，执行支付
        """
        if not self.active_delegation:
            return (
                "**暂无活跃委托协议**\n\n"
                "**可以对我说：**\n"
                "• 开设委托 5000\n"
                "• 创建委托 10000\n"
                "• 授权智能体买东西"
            )

        # 获取商品列表
        products_result = merchant_service.get_product_list()
        products = products_result.get("data", []) if products_result.get("success") else []

        if not products:
            return "**暂无可用商品**\n\n**请先联系商户上架商品**"

        # 提取要购买的商品名称
        target_item = self._extract_item_name(user_input)

        # 查找目标商品
        target_product = None
        for p in products:
            if target_item and target_item.lower() in p["name"].lower():
                target_product = p
                break

        if not target_product:
            # 如果没有指定商品或找不到，显示可用商品列表
            item_list = "\n".join([f"• {p['name']} - ¥{p['price']:.2f}" for p in products[:5]])
            return (
                f"***可用商品列表**:\n\n"
                f"{item_list}\n\n"
                f"**可以对我说**:\n"
                f"• 购买 {products[0]['name'] if products else '某商品'}\n"
                f"• 查看商品"
            )

        # 检查额度是否足够
        cumulative = self.delegated_service.get_cumulative_amount(
            self.active_delegation["delegation_id"]
        )
        remaining = self.active_delegation["max_total"] - cumulative

        if target_product["price"] > remaining:
            return (
                f"**额度不足**\n\n"
                f"**商品价格**: ¥{target_product['price']:.2f}\n"
                f"**委托剩余额度**: ¥{remaining:.2f}\n\n"
                f"**解决方法**: 开设新的委托\n"
                f"• 开设委托 10000"
            )

        # 创建订单并支付
        order_result = merchant_service.create_order(
            item_id=target_product["item_id"],
            quantity=1
        )

        if order_result.get("success"):
            # 使用即时支付服务下单
            instant_service = InstantPaymentService(merchant_service)
            order = order_result["data"]
            pay_request = InstantPayRequest(
                order_id=order["order_id"],
                amount=order["total_amount"],
                payment_method="credit_card"
            )
            pay_result = instant_service.pay(pay_request)

            if pay_result.success:
                return (
                    f"[OK] **下单成功**！\n\n"
                    f"**商品**: {target_product['name']}\n"
                    f"**价格**: ¥{target_product['price']:.2f}\n"
                    f"**订单**: {order['order_id']}\n\n"
                    f"**委托统计**:\n"
                    f"• 累计支付：¥{cumulative + target_product['price']:.2f}\n"
                    f"• 剩余额度：¥{remaining - target_product['price']:.2f}"
                )
            else:
                return f"**支付失败**: {pay_result.message}"
        else:
            return f"**创建订单失败**: {order_result.get('message', '未知错误')}"

    def _handle_view_products(self) -> str:
        """查看商品列表"""
        products_result = merchant_service.get_product_list()
        products = products_result.get("data", []) if products_result.get("success") else []

        if not products:
            return "**暂无可用商品**\n\n**请先联系商户上架商品**"

        response = "**可用商品列表**:\n\n"
        for p in products:
            response += f"• {p['name']} - ¥{p['price']:.2f} (库存:{p['stock']})\n"

        response += "\n**可以对我说**:\n"
        response += "• 购买 Apple\n"
        response += "• 下单购买 {商品名}"
        return response

    def _extract_amount(self, user_input: str) -> Optional[float]:
        """从用户输入中提取金额"""
        # 匹配中文数字或阿拉伯数字 + '元'
        pattern = r'(\d+(?:\.\d+)?)\s*[元 Yuan]+'
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    def _extract_single_limit(self, user_input: str) -> Optional[float]:
        """从用户输入中提取单笔限额"""
        pattern = r'(?:单笔 | 单次 | 每次 | single|max).*?(\d+(?:\.\d+)?)\s*[元 Yuan]+'
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    def _extract_item_name(self, user_input: str) -> Optional[str]:
        """从用户输入中提取商品名称"""
        # 移除"购买"、"下单"、"buy"、"order"等关键词
        cleaned = re.sub(r'购买 | 买 | 下单 | buy|order|for|用于', '', user_input, flags=re.IGNORECASE)
        # 提取剩余的文字作为商品名称
        cleaned = cleaned.strip()
        return cleaned if cleaned else None

    def _get_delegation_welcome(self, user_input: str = "") -> str:
        """获取委托支付欢迎信息"""
        return (
            "**委托支付助手**\n\n"
            "我可以帮助您管理委托支付授权。\n\n"
            "**可以对我说**:\n"
            "• 开设委托 5000 - 创建额度为 5000 元的委托\n"
            "• 查询委托状态 - 查看当前委托的剩余额度\n"
            "• 购买 Apple - 使用委托购买指定商品\n"
            "• 取消委托 - 终止当前委托授权\n\n"
            "也可以直接对话您的需求，例如：\n"
            "• \"帮我买 iPhone，不超过 10000 元\"\n"
            "• \"授权智能体买东西，每次最多 500 元\""
        )

    def get_active_delegation(self) -> Optional[Dict[str, Any]]:
        """获取当前活跃的委托协议"""
        return self.active_delegation

    def set_active_delegation(self, delegation: Dict[str, Any]):
        """设置当前活跃的委托协议"""
        self.active_delegation = delegation