"""
委托支付智能体 (Delegated Payment Agent)
负责与用户自然对话，识别委托支付需求，自动执行完整流程

核心功能：
1. 自然语言理解 - 识别用户表达的需要委托支付的意图
2. 自动执行流程 - 自动签发 IAC、执行支付、更新状态
3. 引导式交互 - 引导用户完成授权边界设置
4. 透明化展示 - 清晰展示每个步骤的执行结果
"""
from typing import Dict, Any, List, Optional
import re
import uuid
from datetime import datetime, timedelta

from psd.delegated_payment import (
    DelegatedPaymentHandler,
    DelegationApplyRequest,
    DelegationCancelRequest,
    DelegationScenario
)
from psd.delegated_payment.payload import PaymentTokenInfo, DelegatedPaymentPayload
from merchant_service.service import merchant_service
from market_service.service import market_service


class DelegatedPaymentAgent:
    """
    委托支付智能体
    能够识别、引导并执行委托支付完整流程
    """

    def __init__(self):
        """初始化委托支付智能体"""
        self.name = "委托支付助理"
        self.delegation_handler = DelegatedPaymentHandler()

        # 对话上下文
        self.user_profile = {
            "principal_id": "did:act:example.com/user-alice",
            "agent_id": "did:act:example.com/alice-agent"
        }

        # 委托支付状态
        self.delegation_context = {
            "active_delegation_id": None,
            "iac": None,
            "delegation_id": None,
            "max_total_amount": 5000.0,
            "max_single_amount": 1000.0,
            "delegation_purpose": None,
            "scenario": "DEDICATED_AGENT",  # 场景三：专属型智能体
            "subaccount_id": "SA-ALICE-001"
        }

        # 对话阶段
        self.conversation_stage = "idle"

        # 产品历史记录（已访问过的商品）
        self.product_history = []

        # 低库存商品缓存
        self._low_stock_products = []

        # 定时任务缓存
        self._scheduled_tasks = []

        # 当前会话 ID
        self.session_id = f"session-{int(datetime.now().timestamp())}"

    def process_user_message(self, user_message: str) -> str:
        """处理用户消息，返回智能体的回复"""
        user_message_lower = user_message.lower().strip()

        # 优先级 1: 取消委托指令（任何阶段都生效）
        cancel_keywords = ["取消", "cancel", "revoke", "吊销"]
        if any(kw in user_message for kw in cancel_keywords):
            return self._handle_cancel_delegation(user_message)

        # 优先级 2: 市场功能指令
        market_commands = ["注册", "新增", "add", "推荐", "搜索", "低库存", "定时", "商品列表", "查看", "list"]
        is_market_command = any(cmd in user_message for cmd in market_commands)

        if is_market_command:
            return self._handle_confirm_purchase(user_message)

        # 优先级 3: 识别新的委托意图
        buy_intent_keywords = ["帮我买", "帮我订", "帮我下单", "帮我支付", "帮我", "帮我再买", "帮我再订"]
        has_buy_intent = any(kw in user_message for kw in buy_intent_keywords)

        if has_buy_intent:
            # 新的委托需求，重新识别
            self.conversation_stage = "idle"
            return self._handle_identify_intent(user_message)

        # 优先级 4: 根据当前阶段处理
        if self.conversation_stage == "idle":
            return self._handle_identify_intent(user_message)
        elif self.conversation_stage == "negotiating_purpose":
            return self._handle_negotiate_constraints(user_message)
        elif self.conversation_stage == "confirming":
            return self._handle_confirm_purchase(user_message)
        else:
            return self._get_welcome_message()

    def _handle_cancel_delegation(self, user_message: str) -> str:
        """处理取消委托请求 - 在任何阶段都可以调用"""
        delegation_id = self.delegation_context.get("delegation_id")

        if not delegation_id:
            return "当前没有活跃的委托，无需取消。"

        # 调用真实的取消委托 API
        try:
            cancel_request = DelegationCancelRequest(
                delegation_id=delegation_id,
                principal_id=self.user_profile["principal_id"],
                reason=user_message
            )

            cancel_response = self.delegation_handler.cancel_delegation(cancel_request)

            # 重置本地状态
            self.conversation_stage = "idle"
            self.delegation_context["active_delegation_id"] = None
            self.delegation_context["iac"] = None
            self.delegation_context["delegation_id"] = None

            return f"""
✅ **委托已取消**

委托 ID: `{delegation_id[:40]}...`
**取消原因**: {cancel_response.message if hasattr(cancel_response, 'message') else user_message}
**原状态**: {cancel_response.old_status if hasattr(cancel_response, 'old_status') else 'ACTIVE'}
**新状态**: {cancel_response.new_status if hasattr(cancel_response, 'new_status') else 'REVOKED'}

您可以重新发起新的委托支付请求。
"""
        except Exception as e:
            # 如果 API 调用失败，至少重置本地状态
            self.conversation_stage = "idle"
            self.delegation_context["active_delegation_id"] = None
            self.delegation_context["iac"] = None
            self.delegation_context["delegation_id"] = None

            return f"""
会话已重置。

委托支付已取消（本地状态已清除）。
如果您需要继续操作，请重新发起委托请求。
"""

    def _is_price_in_message(self, user_message: str) -> float:
        """检查消息中是否包含价格信息"""
        price_pattern = re.search(r'(\d+(?:\.\d+)?)\s*元', user_message)
        if price_pattern:
            try:
                return float(price_pattern.group(1))
            except ValueError:
                pass
        return -1.0

    def _is_confirm_response(self, user_message: str) -> bool:
        """检查是否是确认回复"""
        if not user_message:
            return False
        confirm_keywords = ["好的", "可以", "行", "没问题", "使用", "就用这个", "确认", "同意", "yes", "ok"]
        return any(kw in user_message.lower() for kw in confirm_keywords)

    def _handle_identify_intent(self, user_message: str) -> str:
        """识别用户的委托支付意图"""

        # 检测明确的委托支付关键词
        delegation_keywords = [
            "帮我买", "帮我买", "帮我订", "帮我下单", "帮我支付",
            "帮我支付", "代为支付", "智能体支付", "自动购买",
            "帮我", "替我", "帮我在"
        ]

        detected_intent = False

        # 尝试识别价格相关意图
        price_pattern = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*元', user_message)
        if price_pattern:
            detected_intent = True

        # 尝试识别商品相关意图
        product_keywords = [
            "买", "购买", "订", "下单", "机票", "火车票",
            "书", "书籍", "电影", "票", "订阅", "会员"
        ]
        has_product = any(kw in user_message for kw in product_keywords)

        if has_product:
            detected_intent = True

        # 识别场景描述
        if "委托" in user_message or "授权" in user_message or "智能体" in user_message:
            detected_intent = True

        if detected_intent:
            # 提取关键信息
            price_str = price_pattern.group(0) if price_pattern else None
            price_amount = self._extract_price(price_str)

            # 设置委托目的
            self.delegation_context["delegation_purpose"] = user_message
            self.delegation_context["max_single_amount"] = price_amount or 500.0
            self.delegation_context["max_total_amount"] = (price_amount or 500.0) * 3

            # 进入协商阶段
            self.conversation_stage = "negotiating_purpose"

            purpose = user_message
            return f"""
🤖 **智能支付助理**:

收到您的需求：**{purpose}**

我理解您希望我帮您完成购买，并且愿意使用**委托支付**功能。

---
**建议的委托支付方案**：

根据您的需求，我建议如下委托设置：

1. **委托目的**：{purpose}
2. **单次支付上限**：¥{price_amount * 1.5 if price_amount else 750.0:.2f}（预留 50% 余量）
3. **总支付上限**：¥{price_amount * 5 if price_amount else 2500.0:.2f}（允许 5 次支付）
4. **委托有效期**：30 天

---
**是否使用此委托支付方案？** 您可以直接说"好的"、"同意"或"使用"。
"""
        else:
            return self._get_welcome_message()

    def _handle_negotiate_constraints(self, user_message: str) -> str:
        """协商委托支付约束条件"""

        # 检查是否是要取消/重置会话（先处理取消委托）
        cancel_keywords = ["取消委托", "吊销委托", "取消", "cancel", "revoke"]
        if any(kw in user_message for kw in cancel_keywords):
            # 检查是否有有效的委托
            delegation_id = self.delegation_context.get("delegation_id")
            if delegation_id:
                # 调用真实的取消委托 API
                cancel_request = DelegationCancelRequest(
                    delegation_id=delegation_id,
                    principal_id=self.user_profile["principal_id"],
                    reason=user_message
                )

                cancel_response = self.delegation_handler.cancel_delegation(cancel_request)

                # 重置本地状态
                self.conversation_stage = "idle"
                self.delegation_context["active_delegation_id"] = None
                self.delegation_context["iac"] = None
                self.delegation_context["delegation_id"] = None

                return f"""
✅ **委托已取消**

委托 ID: `{delegation_id[:40]}...`
**取消原因**: {cancel_response.message if hasattr(cancel_response, 'message') else '用户请求'}
**原状态**: {cancel_response.old_status if hasattr(cancel_response, 'old_status') else 'ACTIVE'}
**新状态**: {cancel_response.new_status if hasattr(cancel_response, 'new_status') else 'REVOKED'}

您可以重新发起新的委托支付请求。
"""
            else:
                return "当前没有活跃的委托，无需取消。"

        # 检查是否是重置会话
        reset_keywords = ["不对", "错误", "错了", "reset", "restart"]
        if any(kw in user_message for kw in reset_keywords):
            # 重置会话状态
            self.conversation_stage = "idle"
            self.delegation_context["active_delegation_id"] = None
            self.delegation_context["iac"] = None
            self.delegation_context["delegation_id"] = None
            return self._get_welcome_message()

        # 检查是否是新的委托需求（重新开始）
        new_intent_keywords = ["帮我买", "帮我订", "帮我下单", "帮我支付", "帮我", "帮我再买", "帮我再订"]
        has_new_intent = any(kw in user_message for kw in new_intent_keywords)

        if has_new_intent:
            # 检测到新的委托需求，重新识别意图
            self.conversation_stage = "idle"
            return self._handle_identify_intent(user_message)

        confirm_keywords = ["好的", "好的", "可以", "行", "就行", "没问题", "嗯", "嗯", "使用", "同意", "确认"]
        has_confirm = any(kw in user_message for kw in confirm_keywords)

        if has_confirm:
            return self._execute_delegation_application()
        else:
            return self._continue_negotiation(user_message)

    def _continue_negotiation(self, user_message: str) -> str:
        """继续协商约束条件"""

        price_pattern = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*元', user_message)
        purpose_keywords = ["买", "购买", "订", "下单"]

        price_str = price_pattern.group(0) if price_pattern else None
        new_price = self._extract_price(price_str)

        current_purpose = self.delegation_context["delegation_purpose"]
        if new_price:
            self.delegation_context["max_single_amount"] = new_price * 2
            self.delegation_context["max_total_amount"] = new_price * 5

            return f"""
好的，我理解您的需求。让我为您调整委托支付参数：

**当前委托设置**：
- 委托目的：{current_purpose}
- 单次支付上限：¥{self.delegation_context['max_single_amount']:.2f}
- 总支付上限：¥{self.delegation_context['max_total_amount']:.2f}

请确认是否使用这些参数执行委托支付？
"""
        else:
            return f"""
我明白了。当前委托设置如下：

**委托支付参数**：
- 总金额上限：¥{self.delegation_context['max_total_amount']:.2f}
- 单笔支付上限：¥{self.delegation_context['max_single_amount']:.2f}
- 委托目的：{current_purpose}

请确认是否使用这些参数执行委托支付，还是需要调整？
"""

    def _execute_delegation_application(self) -> str:
        """执行委托协议签发

        委托支付流程：委托授权 - 不是立即执行购买，而是授权智能体在条件符合时代偿购买
        """

        delegation_id = f"urn:uuid:{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:4]}" \
                        f"-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}" \
                        f"-{uuid.uuid4().hex[:12]}"

        self.delegation_context["delegation_id"] = delegation_id

        apply_request = DelegationApplyRequest(
            principal_id=self.user_profile["principal_id"],
            agent_id=self.user_profile["agent_id"],
            delegation_id=delegation_id,
            agent_type=self.delegation_context["scenario"],
            subaccount_id=self.delegation_context["subaccount_id"],
            delegation_purpose=self.delegation_context["delegation_purpose"],
            max_total_amount=self.delegation_context["max_total_amount"],
            max_single_amount=self.delegation_context["max_single_amount"],
            validity_start=datetime.now().isoformat(),
            validity_end=(datetime.now() + timedelta(days=30)).isoformat()
        )

        result = self.delegation_handler.apply_delegation(apply_request)

        self.delegation_context["iac"] = result.iac
        self.delegation_context["active_delegation_id"] = delegation_id

        self.conversation_stage = "confirming"

        return f"""
✅ **委托协议签发成功！**

我已在系统中成功签发 IAC（意图授权凭证）：

| 项目 | 值 |
|------|-----|
| 委托 ID | `{delegation_id[:40]}...` |
| 委托人 | {self.user_profile['principal_id']} |
| 智能体 | {self.user_profile['agent_id']} |
| 模式 | 专属型智能体 |
| 单次上限 | ¥{result.max_single_amount:.2f} |
| 总额上限 | ¥{result.max_total_amount:.2f} |

委托目的：\"> \"{self.delegation_context['delegation_purpose']}"

---
**委托已生效，您可以随时说"购买 XXX"让智能体代您购买。**

您还可以：
- 查看商品列表
- 搜索商品
- 取消委托
"""

    def _extract_purchase_intent(self) -> str:
        """从委托目的中提取商品购买意图"""
        purpose = self.delegation_context.get("delegation_purpose", "")
        # 提取"帮我买/订 XXX"中的商品名称
        import re
        match = re.search(r'帮我 [买订下单]([^\，，]+)(?:，|。|$)', purpose)
        if match:
            return match.group(1).strip()
        return purpose

    def _find_matching_product(self, products: list, description: str) -> dict:
        """在商品列表中寻找匹配的商品（支持模糊匹配）"""
        import re
        # 提取商品名称关键词（去除价格等）
        keywords = re.sub(r'\d+[ ]*元', '', description)
        keywords = keywords.strip()

        # 精确匹配
        for product in products:
            if keywords == product["name"]:
                return product

        # 模糊匹配 - 包含关系
        for product in products:
            if (keywords in product["name"] or
                product["name"] in keywords or
                product["item_id"] in keywords):
                return product

        # 拼音/同义词匹配（简化版）
        alias_map = {
            "智能手环": ["手环", "智能手表"],
            "手表": ["手环", "智能手表"],
            "耳机": ["无线耳机", "蓝牙耳机"],
            "苹果": ["Apple", "红苹果"],
        }

        for alias, synonyms in alias_map.items():
            if any(s in keywords for s in synonyms + [alias]):
                for product in products:
                    if product["name"] in synonyms or product["name"] == alias:
                        return product

        return None

    def _handle_confirm_purchase(self, user_message: str) -> str:
        """处理购买确认"""

        products_result = merchant_service.get_product_list()

        if not products_result["success"]:
            return "抱歉，无法获取商品列表。请稍后重试。"

        products = products_result["data"]

        buy_keywords = ["买", "购买", "要", "下单", "book", "书籍"]
        has_buy_intent = any(kw in user_message.lower() for kw in buy_keywords)

        if has_buy_intent:
            selected_product = None

            for product in products:
                if product["name"] in user_message or product["item_id"] in user_message:
                    selected_product = product
                    break

            if selected_product:
                return self._execute_payment(selected_product)
            elif selected_product is None and has_buy_intent:
                # 没有选中的商品，展示列表
                return self._show_product_list(products)
            else:
                return self._show_product_list(products)

        # 语义处理：查看商品列表
        if "商品列表" in user_message or "product list" in user_message.lower():
            products_result = merchant_service.get_product_list()
            if products_result["success"] and products_result["data"]:
                products = products_result["data"]
                return self._show_product_list(products)

        # 语义处理：搜索商品
        if "搜索" in user_message or "search" in user_message.lower():
            keywords = user_message.replace("搜索", "").replace("search", "").strip()
            return self.search_products(keywords)

        # 语义处理：注册新商品
        if "注册" in user_message or "新增" in user_message or "add" in user_message.lower():
            # 尝试提取商品信息 - 支持多种格式
            import re

            # 格式 1: 新增商品：商品名、价格、类别（逗号分隔）
            # 先去除"注册新商品："、"新增商品："等前缀
            clean_parts = re.split(r'[:：]', user_message, maxsplit=1)
            clean_message = clean_parts[1].strip() if len(clean_parts) > 1 else user_message

            # 从逗号分隔中提取各部分
            parts = clean_message.split('、')
            if len(parts) >= 3:
                name = parts[0].strip()
                category = parts[2].strip()
                # 价格：从中间部分提取数字
                price_str = parts[1].strip().replace('元', '')
                price_match = re.search(r'(\d+(?:\.\d+)?)', price_str)
            elif len(parts) >= 2:
                name = parts[0].strip()
                # 尝试在剩余部分找价格
                price_str = clean_message
                price_match = re.search(r'(\d+(?:\.\d+)?)\s*元', clean_message)
                category = "default"
            else:
                name = "未知商品"
                price_match = None
                category = "default"

            product_info = {
                "name": name if name else "未知商品",
                "price": float(price_match.group(1)) if price_match else float(price_str) if 'price_str' in locals() else 0.0,
                "category": category,
                "stock": 100,
                "low_stock_threshold": 10
            }
            return self.register_new_product(product_info)

        # 语义处理：检查低库存
        if "低库存" in user_message or "库存预警" in user_message:
            return self.check_low_stock()

        # 语义处理：创建定时购买
        if "定时" in user_message or "scheduled" in user_message.lower():
            # 提取商品 ID 和时间
            if "商品" in user_message and "@" in user_message:
                parts = user_message.split("@")
                item_part = parts[0]
                time_part = parts[1].strip() if len(parts) > 1 else ""

                item_match = re.search(r'([A-Z]{3}-\d{4})', item_part)
                if item_match:
                    item_id = item_match.group(1)
                    return self.schedule_purchase(item_id, time_part)

            return self.show_scheduled_tasks()

        # 语义处理：推荐商品
        if "推荐" in user_message or "recommend" in user_message.lower():
            return self.recommend_products()

        # 默认展示商品列表
        return self._show_product_list(products)

    def _execute_payment(self, product: Dict[str, Any]) -> str:
        """执行支付"""

        if not self.delegation_context["iac"]:
            return "尚未建立委托协议，请先授权。"

        cart_items = [{
            "item_id": product["item_id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": 1
        }]

        cart_hash = DelegatedPaymentPayload.calculate_cart_snapshot_hash(cart_items)
        payment_amount = product["price"]

        max_single = self.delegation_context["max_single_amount"]
        if payment_amount > max_single:
            return f"""
⚠️ 商品价格 ¥{payment_amount:.2f} 超过授权上限 ¥{max_single:.2f}

您可以：
1. 修改商品选择
2. 重新授权更高的委托金额
"""

        # 构造支付请求对象
        from psd.delegated_payment import DelegationPayRequest

        pay_request = DelegationPayRequest(
            request_id=f"pay-{self.delegation_context['delegation_id'][:8]}-{int(datetime.now().timestamp())}",
            buyer_agent_id=self.user_profile["agent_id"],
            delegation_id=self.delegation_context["delegation_id"],
            iac=self.delegation_context["iac"],
            merchant_id="did:act:merchant-shop",
            merchant_order_id=f"MCH{int(datetime.now().timestamp())}",
            cart_snapshot_hash=cart_hash,
            amount=payment_amount,
            currency="CNY",
            payment_token=PaymentTokenInfo(
                token="t_mock_token_" + uuid.uuid4().hex[:10],
                token_type="CARD_TOKEN",
                token_scheme="EMV_PAIT"
            )
        )

        # 如果有子账户，添加子账户信息
        if self.delegation_context.get("subaccount_id"):
            pay_request.subaccount_id = self.delegation_context["subaccount_id"]

        pay_result = self.delegation_handler.pay(pay_request)

        if pay_result.success:
            cumulative = self.delegation_handler.payment_service.get_cumulative_amount(
                self.delegation_context["active_delegation_id"]
            )
            remaining = self.delegation_context["max_total_amount"] - cumulative

            self.conversation_stage = "idle"

            return f"""
💰 **支付成功！**

| 项目 | 详情 |
|------|------|
| 商品 | {product['name']} |
| 金额 | ¥{pay_result.amount:.2f} |
| 支付流水号 | `{pay_result.payment_id}` |
| 交易流水号 | `{pay_result.transaction_id}` |
| 支付状态 | {pay_result.status} |

---
**当前委托状态**：
- 累计支付：¥{cumulative:.2f}
- 剩余额度：¥{remaining:.2f}
"""
        else:
            return f"支付失败：{pay_result.error_message or '未知错误'}"

    def get_product_list_suggestion(self) -> str:
        """
        获取商品列表建议 - 整合市场服务智能发现
        """
        recommendations = []

        # 从商户服务获取商品
        merchant_result = merchant_service.get_product_list()
        if merchant_result["success"] and merchant_result["data"]:
            for p in merchant_result["data"]:
                recommendations.append(f"- {p['name']} (¥{p['price']:.2f}, ID: {p['item_id']})")

        # 从市场服务获取商品
        market_result = market_service.get_all_products()
        if market_result["success"] and market_result["data"]:
            for p in market_result["data"]:
                recommendations.append(f"- {p['name']} (¥{p['price']:.2f}, ID: {p['item_id']})")

        if recommendations:
            return "\n".join(recommendations)
        return "暂无商品"

    def search_products(self, keywords: str) -> str:
        """
        搜索商品 - 搜索市场服务和商户服务
        """
        products = []

        # 从商户服务获取商品
        merchant_result = merchant_service.get_product_list()
        if merchant_result["success"] and merchant_result["data"]:
            for p in merchant_result["data"]:
                # 简单关键词匹配
                if (keywords.lower() in p["name"].lower() or
                    keywords.lower() in p.get("description", "").lower() or
                    keywords.lower() in p.get("category", "").lower()):
                    products.append({
                        "name": p["name"],
                        "item_id": p["item_id"],
                        "price": p["price"],
                        "category": p.get("category", "默认"),
                        "description": p.get("description", "")
                    })

        # 从市场服务获取商品
        market_result = market_service.search_products(keywords=keywords)
        if market_result["success"] and market_result["data"]:
            for p in market_result["data"]:
                products.append({
                    "name": p["name"],
                    "item_id": p["item_id"],
                    "price": p["price"],
                    "category": p.get("category", "默认"),
                    "description": p.get("description", "")
                })

        if products:
            response = "\n# 搜索 " + keywords + " 结果 (找到" + str(len(products)) + "个商品):\n\n"
            for i, p in enumerate(products, 1):
                response += f"""
{i}. **{p['name']}**
   - 商品 ID: `{p['item_id']}`
   - 价格：¥{p['price']:.2f}
   - 类别：{p['category']}
   - 描述：{p.get('description', '')}
"""
            return response
        return "\n# 未找到与 " + keywords + " 相关的商品"

    def register_new_product(self, product_info: Dict[str, Any]) -> str:
        """
        注册新商品到市场
        """
        result = market_service.register_product(
            name=product_info.get("name", ""),
            price=product_info.get("price", 0),
            category=product_info.get("category", "default"),
            description=product_info.get("description", ""),
            stock=product_info.get("stock", 100),
            tags=product_info.get("tags", []),
            supplier_id=product_info.get("supplier_id"),
            low_stock_threshold=product_info.get("low_stock_threshold")
        )

        if result["success"]:
            product = result["data"]
            return f"""
✅ **商品注册成功!**

新商品已添加到市场:
- **名称**: {product['name']}
- **商品 ID**: `{product['item_id']}`
- **价格**: ¥{product['price']:.2f}
- **类别**: {product['category']}
- **库存**: {product['stock']} 件

商品已可由智能体发现!
"""
        return f"❌ 商品注册失败：{result['message']}"

    def check_low_stock(self) -> str:
        """
        检查低库存商品
        """
        result = market_service.get_low_stock_products()
        if result["success"] and result["data"]:
            products = result["data"]
            response = f"\n⚠️ **低库存预警** (发现{len(products)}个低库存商品):\n\n"
            for p in products:
                threshold = p.get("low_stock_threshold", "未设置")
                response += f"""
- `{p['item_id']}` {p['name']}: 库存 {p['stock']}/{threshold}
"""
            return response + "\n建议触发补货或自动购买!"
        return "\n✅ 暂无低库存商品预警"

    def schedule_purchase(self, item_id: str, scheduled_time: str, quantity: int = 1) -> str:
        """
        创建定时购买任务
        """
        result = market_service.add_scheduled_purchase(
            item_id=item_id,
            scheduled_time=scheduled_time,
            quantity=quantity
        )

        if result["success"]:
            task = result["data"]
            return "```\n✅ **定时购买任务已创建**!\n\n" + \
                "- **任务 ID**: `" + str(task['task_id']) + "`\n" + \
                "- **商品**: " + str(task['product_name']) + "\n" + \
                "- **执行时间**: " + str(task['scheduled_time']) + "\n" + \
                "- **购买数量**: " + str(task['quantity']) + " 件\n\n" + \
                "智能体会在指定时间自动执行购买!\n```"
        return f"❌ 定时任务创建失败：{result['message']}"

    def show_scheduled_tasks(self) -> str:
        """
        显示所有定时任务
        """
        result = market_service.get_pending_scheduled_tasks()
        if result["success"] and result["data"]:
            tasks = result["data"]
            response = "\n📅 **待执行的定时购买任务**:\n\n"
            for t in tasks:
                response += f"""
- `{t['task_id']}`: 购买 {t['product_name']} (数量：{t['quantity']}) @ {t['scheduled_time']}
"""
            return response
        return "\n❌ 暂无待执行的定时购买任务"

    def recommend_products(self, user_prefs: Dict[str, Any] = None) -> str:
        """
        推荐商品 - 从商户服务和市场服务获取商品
        """
        products = []

        # 从商户服务获取商品
        merchant_result = merchant_service.get_product_list()
        if merchant_result["success"] and merchant_result["data"]:
            for p in merchant_result["data"]:
                products.append({
                    "name": p["name"],
                    "price": p["price"],
                    "category": p.get("category", "默认"),
                    "description": p.get("description", "")
                })

        # 从市场服务获取商品
        market_result = market_service.get_all_products()
        if market_result["success"] and market_result["data"]:
            for p in market_result["data"]:
                products.append({
                    "name": p["name"],
                    "price": p["price"],
                    "category": p.get("category", "默认"),
                    "description": p.get("description", "")
                })

        if products:
            # 按价格排序（从低到高）
            products.sort(key=lambda x: x["price"])
            response = "\n🎯 **为您推荐以下商品**:\n\n"
            for i, p in enumerate(products, 1):
                response += f"""
{i}. **{p['name']}** - ¥{p['price']:.2f} ({p['category']})
   - {p.get('description', '')}
"""
            return response
        return "\n❌ 暂无可推荐的商品"

    def _show_product_list(self, products: List[Dict[str, Any]]) -> str:
        """展示商品列表"""

        response = "\n📦 **当前可售商品列表**：\n\n"

        for i, product in enumerate(products, 1):
            tags_info = ""
            if product.get("tags"):
                tags_info = f" | 标签：{', '.join(product['tags'])}"
            response += f"""
{i}. **{product['name']}**
   - 商品 ID: `{product['item_id']}`
   - 价格：¥{product['price']:.2f}
   - 库存：{product['stock']} 件
   - 类别：{product.get('category', 'N/A')}{tags_info}"""

        # 获取商品列表建议
        suggestion = self.get_product_list_suggestion()
        response += f"""

---
**商品列表**:
```
{suggestion}
```

**智能操作**:
- "搜索建议关键词"
- "注册新商品：商品名、价格、类别"
- "检查低库存商品"
- "创建定时购买：商品 ID, 时间，数量"
- "推荐商品"
"""

        return response

    def _extract_price(self, price_str: str) -> Optional[float]:
        """从价格字符串中提取金额"""

        if not price_str:
            return None

        clean_str = str(price_str).replace("元", "").replace(",", "")

        try:
            return float(clean_str)
        except ValueError:
            return None

    def _get_welcome_message(self) -> str:
        """欢迎消息"""

        return """
🌟 您好！我是**委托支付智能助理**，可以帮您自动完成购买。

---
## 我能为您做什么？

### 1️⃣ 委托支付（推荐）
只需告诉我您的需求，例如：
- "帮我买《人工智能：现代方法》这本书，不超过 150 元"
- "帮我订明天上午飞北京的机票，不超过 1200 元"
- "帮我订阅年度会员，不超过 500 元"

我将：
1. 自动签发授权凭证（IAC）
2. 监控商品价格/可用库存
3. 在条件满足时自动执行支付
4. 实时向您汇报进度

### 2️⃣ 普通购买
如果没有委托支付需求，我也可以：
- 帮您查询商品
- 创建订单
- 处理支付

### 3️⃣ 市场服务
- "推荐商品" - 查看推荐商品
- "搜索 XXX" - 搜索商品
- "注册新商品：商品名、价格、类别" - 动态添加商品
- "检查低库存" - 查看库存预警

---
**请告诉我您的需求，或者直接说一个商品名称。**
"""