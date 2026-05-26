"""
购物助手界面 (Shopping Assistant UI)
ACT 协议 - 智能购物助手对话界面
"""
import streamlit as st
import time
import re
from typing import Dict, Optional

from merchant_service.service import merchant_service
from payment_service.instant_payment import InstantPaymentService, InstantPayRequest
from payment_service.delegated_payment import (
    DelegatedPaymentService,
    DelegationApplyRequest,
    DelegationCancelRequest
)


def render_shopping_assistant_tab():
    """
    渲染购物助手对话界面

    界面布局 - 左右分栏：
    - 左侧：聊天对话区域
    - 右侧：快捷操作面板（商品、委托状态、购物车）
    """
    # 初始化购物助手专用 session state
    init_shopping_assistant_state()

    # 页面标题
    st.markdown('<div class="main-header">[Cart] ACT 协议 - 智能购物助手</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">基于委托支付的智能购物体验</div>', unsafe_allow_html=True)

    # 左右分栏
    col1, col2 = st.columns([3, 1])

    with col1:
        render_chat_area()

    with col2:
        render_side_panel()


def init_shopping_assistant_state():
    """初始化购物助手专用 session state"""
    # 委托支付相关
    if "active_delegation" not in st.session_state:
        st.session_state.active_delegation = None

    # 购物车
    if "shopping_cart" not in st.session_state:
        st.session_state.shopping_cart = []

    # 自动购买任务列表
    if "auto_purchase_tasks" not in st.session_state:
        st.session_state.auto_purchase_tasks = []

    # 价格预警列表
    if "price_alerts" not in st.session_state:
        st.session_state.price_alerts = []

    # 智能体配置
    if "agent_config" not in st.session_state:
        st.session_state.agent_config = {
            "auto_purchase_enabled": False,
            "price_alert_enabled": True,
            "max_price_threshold": 100.0
        }

    # 注册商品变更回调（即时商品变化通知）
    merchant_service._on_product_changed = on_product_changed_callback


def on_product_changed_callback(product: Dict):
    """商品变更回调 - 当商户服务修改商品时触发"""
    if "product_notifications" not in st.session_state:
        st.session_state.product_notifications = []

    notification = {
        "action": "deleted",
        "product": product,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.product_notifications.insert(0, notification)
    if len(st.session_state.product_notifications) > 5:
        st.session_state.product_notifications = st.session_state.product_notifications[:5]


def render_chat_area():
    """渲染聊天对话区域"""
    if "assistant_messages" not in st.session_state:
        st.session_state.assistant_messages = []

    # 显示聊天历史
    for message in st.session_state.assistant_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 用户输入
    if prompt := st.chat_input("请输入您的消息..."):
        handle_user_message(prompt)


def handle_user_message(prompt: str):
    """处理用户消息"""
    # 添加用户消息
    st.session_state.assistant_messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # 处理消息
    with st.chat_message("assistant"):
        with st.spinner("助理 Agent 正在处理..."):
            response = process_shopping_command(prompt)
            st.markdown(response)

            st.session_state.assistant_messages.append({
                "role": "assistant",
                "content": response
            })


def process_shopping_command(prompt: str) -> str:
    """
    处理购物相关命令

    支持命令：
    - 查看商品/商品列表
    - 加入购物车 [商品名]
    - 添加到购物车
    - 查看购物车
    - 结算/购买
    - 开设委托 [总额限制]
    - 使用委托购买 [商品名]
    - 查询委托状态
    - 取消委托
    - 添加自动购买任务 [商品名] [价格上限]
    - 执行自动购买
    """
    prompt_lower = prompt.lower()

    # 查看商品列表
    if any(cmd in prompt_lower for cmd in ["查看商品", "看商品", "商品列表", "list product", "show product"]):
        return handle_view_products()

    # 加入购物车
    if any(cmd in prompt_lower for cmd in ["加入购物车", "添加商品", "add to cart", "add product"]):
        return handle_add_to_cart(prompt)

    # 查看购物车
    if any(cmd in prompt_lower for cmd in ["查看购物车", "看购物车", "购物车", "view cart", "show cart"]):
        return handle_view_cart()

    # 结算/购买
    if any(cmd in prompt_lower for cmd in ["结算", "购买", "checkout", "buy", "支付"]):
        return handle_checkout()

    # 开设委托
    if any(cmd in prompt_lower for cmd in ["开设委托", "新的委托", "create delegation", "new delegation"]):
        return handle_create_delegation(prompt)

    # 使用委托购买
    if any(cmd in prompt_lower for cmd in ["使用委托", "委托购买", "delegation buy", "use delegation"]) and any(cmd in prompt_lower for cmd in ["购买", "买"]):
        return handle_delegation_purchase(prompt)

    # 查询委托状态
    if any(cmd in prompt_lower for cmd in ["查询委托", "委托状态", "查看委托", "delegation status", "show delegation"]):
        return handle_query_delegation()

    # 取消委托
    if any(cmd in prompt_lower for cmd in ["取消委托", "吊销委托", "cancel delegation", "revoke"]):
        return handle_cancel_delegation()

    # 添加自动购买任务
    if any(cmd in prompt_lower for cmd in ["添加自动", "自动购买任务", "auto buy task", "set auto"]):
        return handle_add_auto_task(prompt)

    # 执行自动购买
    if any(cmd in prompt_lower for cmd in ["执行自动购买", "运行自动", "run auto"]):
        return handle_run_auto_purchase()

    # 默认回复
    return get_default_response(prompt)


def handle_view_products() -> str:
    """处理查看商品请求"""
    products_result = merchant_service.get_product_list()
    products = products_result.get("data", []) if products_result.get("success") else []

    if not products:
        return "(No products) 暂无可用商品。\n\n请先联系商户上架商品，或去商户服务界面添加商品~"

    response = "(Box) **可用商品列表**:\n\n"
    for p in products:
        response += f"• {p['name']} - ¥{p['price']:.2f} (库存:{p['stock']})\n"

    response += "(Lightbulb) **可以对我说**:\n- \"添加 Apple 到购物车\"\n- \"查看详情\"\n- \"加入购物车中的香蕉\""
    return response


def handle_add_to_cart(prompt: str) -> str:
    """处理添加商品到购物车"""
    products_result = merchant_service.get_product_list()
    products = products_result.get("data", []) if products_result.get("success") else []

    if not products:
        return "[Error] 暂无可用商品，请先上架商品"

    # 提取商品名称
    for p in products:
        # 智能匹配商品名称
        if p['name'] in prompt:
            # 添加到购物车
            st.session_state.shopping_cart.append({
                "item_id": p["item_id"],
                "name": p["name"],
                "price": p["price"],
                "qty": 1
            })
            return f"[Check] 已将 **{p['name']}** 加入购物车!\n\n(Cart) 当前购物车:{len(st.session_state.shopping_cart)} 件商品"

    # 未找到商品
    return f"""
❌ **未找到目标商品**

**可用商品：**
""" + chr(10).join([f"  • {p['name']} - ¥{p['price']:.2f}" for p in products]) + """

💡 **请确保商品名称准确，或尝试说「查看商品」查看更多选项。**
"""


def handle_view_cart() -> str:
    """处理查看购物车请求"""
    cart = st.session_state.shopping_cart

    if not cart:
        return r"""
🛒 **购物车是空的**

💡 可以对我说：
  • 查看商品
  • 添加商品到购物车
  • 购买香蕉
"""

    items_text = []
    total = 0
    for item in cart:
        subtotal = item["price"] * item["qty"]
        items_text.append(f"  • {item['name']} x{item['qty']} = ¥{subtotal:.2f}")
        total += subtotal

    return f"""
🛒 **您的购物车** ({len(cart)} 件商品)

{'\n'.join(items_text)}

**订单总额：¥{round(total, 2)}**

💡 我可以说：
  • 结算
  • 购买
  • 查看商品
"""


def handle_checkout() -> str:
    """处理结算请求"""
    cart = st.session_state.shopping_cart

    if not cart:
        return "(Cart) 购物车是空的。\n\n请先添加商品到购物车哦~"

    # 结算后台逻辑将在这里实现
    total = sum(item["price"] * item["qty"] for item in cart)

    # 检查是否有有效委托
    if st.session_state.active_delegation:
        remaining = st.session_state.active_delegation["max_total"] - \
                    st.session_state.delegated_service.get_cumulative_amount(
                        st.session_state.active_delegation["delegation_id"]
                    )

        if total > remaining:
            return f"""
⚠️ **额度不足**

**订单总额**: ¥{total:.2f}
**委托剩余额度**: ¥{remaining:.2f}

---
💡 可以对我说：
  • 开设委托 500
  • 使用即时支付
"""

    # 执行即时支付
    payment_service = InstantPaymentService(merchant_service)
    results = []

    for item in cart:
        # 创建订单
        order_result = merchant_service.create_order(
            item_id=item["item_id"],
            quantity=item["qty"]
        )
        if order_result["success"]:
            order = order_result["data"]
            pay_request = InstantPayRequest(
                order_id=order["order_id"],
                amount=order["total_amount"],
                payment_method="credit_card"
            )
            pay_result = payment_service.pay(pay_request)
            if pay_result.success:
                results.append(f"  ✅ {item['name']} (订单:{order['order_id'][:8]})")
            else:
                results.append(f"  ❌ {item['name']}: {pay_result.message}")

    # 清空购物车
    st.session_state.shopping_cart = []

    return f"""
✅ **结算成功!**

**支付明细**:
{chr(10).join(results)}

**订单总额**: ¥{total:.2f}
"""


def handle_create_delegation(prompt: str) -> str:
    """处理开设委托请求"""
    # 检查是否有服务
    if "delegated_service" not in st.session_state:
        return r"""
❌ **委托支付服务未就绪**

请联系管理员检查服务状态。
"""

    # 提取金额
    import re
    amount_match = re.search(r'(\d+)￥|(\d+)', prompt)

    if amount_match:
        max_total = float(amount_match.group(1) or amount_match.group(2))
    else:
        max_total = 500.0  # 默认额度

    max_single = max_total / 5  # 单笔上限为总额的一半
    if max_single > 500:
        max_single = 500

    # 生成委托 ID
    delegation_id = f"urn:act:delegation:{int(time.time() * 1000)}"

    result = st.session_state.delegated_service.apply(
        DelegationApplyRequest(
            principal_id="did:act:user-assistant",
            agent_id="did:act:agent-shopping",
            delegation_id=delegation_id,
            max_total_amount=max_total,
            max_single_amount=max_single,
            delegation_purpose="智能购物助手自动购买授权"
        )
    )

    if result.max_total_amount > 0:
        st.session_state.active_delegation = {
            "delegation_id": result.delegation_id,
            "iac": result.iac[:100] + "...",
            "max_total": result.max_total_amount,
            "max_single": result.max_single_amount,
            "agent_id": "did:act:agent-shopping"
        }
        resp = "[OK] **委托协议已签发**！\n\n"
        resp += "**委托 ID**: `" + str(result.delegation_id[:30]) + "...`\n"
        resp += "**总额度**: ¥" + str(round(result.max_total_amount, 2)) + "\n"
        resp += "**单笔上限**: ¥" + str(round(result.max_single_amount, 2)) + "\n\n"
        resp += "---\n**现在可以对购物助手说：**\n"
        resp += "- 使用委托购买 Apple\n"
        resp += "- 查询委托状态\n"
        resp += "- 查看商品"
        return resp
    else:
        return "[Error] 开设委托失败：" + result.message


def handle_query_delegation() -> str:
    """查询委托状态"""
    if not st.session_state.active_delegation:
        return "***暂无活跃的委托协议***\n\n---\n**可以对我说：**\n- 开设委托 500\n- 创建委托 1000"

    delegation = st.session_state.active_delegation
    cumulative = st.session_state.delegated_service.get_cumulative_amount(
        delegation["delegation_id"]
    )
    remaining = delegation["max_total"] - cumulative

    status_emoji = "[ON]" if remaining > 0 else "[OFF]"

    resp = "***委托协议状态***\n\n"
    resp += "状态：**启用中**\n"
    resp += "**委托 ID**: `" + str(delegation["delegation_id"][:30]) + "`...\n"
    resp += "**总额度**: ¥" + str(round(delegation["max_total"], 2)) + "\n"
    resp += "**累计支付**: ¥" + str(round(cumulative, 2)) + "\n"
    resp += "**剩余额度**: ¥" + str(round(remaining, 2)) + "\n\n"
    resp += "---\n**可以对我说：**\n"
    resp += "- 查看委托 IAC 凭证\n"
    resp += "- 使用委托购买\n"
    resp += "- 取消委托"
    return resp


def handle_cancel_delegation() -> str:
    """处理取消委托"""
    if not st.session_state.active_delegation:
        return "***无活跃委托可取消***"

    delegation_id = st.session_state.active_delegation["delegation_id"]

    result = st.session_state.delegated_service.cancel(
        DelegationCancelRequest(
            delegation_id=delegation_id,
            principal_id="did:act:user-assistant",
            reason="用户请求取消"
        )
    )

    if result.status == "REVOKED":
        st.session_state.active_delegation = None
        return "[OK] **委托协议已取消**\n\n所有后续委托支付将不再可用。"
    else:
        return "[Error] 取消失败：" + result.message


def handle_add_auto_task(prompt: str) -> str:
    """添加自动购买任务"""
    # 分析商品名称和价格
    import re

    # 尝试提取价格
    price_match = re.search(r'(?:价格上限|不超过|atmost|max).*?(\d+¥|\d+)￥?|(\d+)￥?|(\d+)', prompt)

    if price_match:
        max_price = float(price_match.group(1) or price_match.group(2) or price_match.group(3))
    else:
        max_price = 100.0  # 默认

    # 提取商品名称（去掉明确的价格相关词）
    clean_prompt = re.sub(r'价格上限|不超过|amount|max|\d+￥|￥\d+', '', prompt)

    # 尝试从中提取商品名称
    response = "[Settings] **添加自动购买任务**\n\n请提供更多信息：\n- 商品名称：{item_name}\n- 价格上限：¥{price:.2f}\n\n[Lightbulb] **完整命令示例**：\n- \"添加自动购买任务 Apple 价格不超过 100\"\n- \"设置自动购买：不超过 200\" "

    return response


def handle_delegation_purchase(prompt: str) -> str:
    """使用委托购买"""
    if not st.session_state.active_delegation:
        return "[No Delegation] 暂无活跃委托\n\n[Lightbulb] **可以对我说：**\n- \"开设委托 500\"\n- \"创建委托 1000\""

    # 获取商品列表
    products_result = merchant_service.get_product_list()
    products = products_result.get("data", []) if products_result.get("success") else []

    if not products:
        return "[Error] 暂无可用商品"

    # 查找目标商品
    for p in products:
        if p["name"] in prompt:
            # 检查额度
            remaining = st.session_state.active_delegation["max_total"] - \
                        st.session_state.delegated_service.get_cumulative_amount(
                            st.session_state.active_delegation["delegation_id"]
                        )

            if p["price"] > remaining:
                return "[Error] 商品 " + p["name"] + " 价格上限不足\n\n" + \
                "***任务价格***: ¥" + str(round(p["price"], 2)) + "\n" + \
                "***委托剩余额度***: ¥" + str(round(remaining, 2)) + "\n\n" + \
                "---\n**可以对我说：**\n- 开设委托 1000"

            # 下单并支付
            order_result = merchant_service.create_order(
                item_id=p["item_id"],
                quantity=1
            )

            if order_result["success"]:
                st.success(f"[OK] 委托购买成功！**{p['name']}** - ¥{p['price']:.2f}")
                resp = "[OK] **委托购买成功**！\n\n"
            resp += "***商品***: " + p["name"] + "\n"
            resp += "***价格***: ¥" + str(round(p["price"], 2)) + "\n"
            resp += "***订单***: " + order_result["data"]["order_id"] + "\n\n"
            resp += "***委托统计***:\n"
            cumulative = st.session_state.delegated_service.get_cumulative_amount(
                st.session_state.active_delegation["delegation_id"]
            )
            resp += "• 累计支付：¥" + str(round(cumulative, 2)) + "\n"
            resp += "• 剩余额度：¥" + str(round(remaining - p["price"], 2)) + "\n\n"
            resp += "---\n**可以对我说：**\n- 查看商品\n- 查询委托状态"
            return resp

    return "[Error] 未找到目标商品\n\n[Lightbulb] **可用商品：**\n{items}\n\n请确保商品名称准确。".format(
        items=chr(10).join([f"• {p['name']}" for p in products])
    )


def handle_run_auto_purchase() -> str:
    """执行自动购买任务"""
    tasks = st.session_state.auto_purchase_tasks

    if not tasks:
        return "(TaskList) **暂无自动购买任务**\n\n[Lightbulb] **可以对我说：**\n- \"添加自动购买任务 Apple 不超过 50\"\n- \"设置自动购买\""

    response = "[Robot] **您的自动购买任务**:\n\n"
    for i, task in enumerate(tasks, 1):
        response += f"{i}. {task.get('name', '未命名')} -¥{task.get('max_price', 100):.2f}\n"

    response += """
[Lightbulb] **可以对我说：**
- "执行自动购买"
- "购买 Apple" """
    return response


def get_default_response(prompt: str) -> str:
    """默认回复"""
    # 尝试获取第一个商品名称用于个性化回复
    products_result = merchant_service.get_product_list()
    products = products_result.get("data", []) if products_result.get("success") else []
    first_product = products[0]['name'] if products else "商品"

    prompt_truncated = prompt[:30] + "..." if len(prompt) > 30 else prompt

    return f"""
我收到您的需求：**{prompt_truncated}**

---

**我可以为您做什么？**

| 👉 我能帮您 | 💬 您可以对我说 |
|------------|----------------|
| 📦 查看商品 | "查看商品" 或 "list product" |
| 🛒 添加到购物车 | "添加 {first_product} 到购物车" |
| 🛍️ 查看购物车 | "查看购物车" 或 "view cart" |
| 💳 结算购买 | "结算" 或"购买" |
| 💰 开设委托 | "开设委托 500" 或 "create delegation" |
| 🤖 委托购买 | "使用委托购买 {first_product}" |
| 📊 委托状态 | "查询委托状态" 或 "delegation status" |
| 🔒 取消委托 | "取消委托" |

---

💡 **提示**：您也可以点击右侧面板快速操作！
"""


def render_side_panel():
    """渲染右侧侧边栏"""
    st.markdown("---")

    # 委托状态
    if st.session_state.active_delegation:
        st.markdown("### [Scroll] 委托状态")
        delegation = st.session_state.active_delegation
        cumulative = st.session_state.delegated_service.get_cumulative_amount(
            delegation["delegation_id"]
        )
        remaining = delegation["max_total"] - cumulative

        st.metric("剩余额度", f"¥{remaining:.2f}")
        st.metric("累计支付", f"¥{cumulative:.2f}")

        with st.expander("[Lock] IAC 凭证"):
            st.code(delegation.get("iac", ""), language="json")

        st.divider()

    # 购物车
    st.markdown("### [Cart] 购物车")

    cart = st.session_state.shopping_cart

    if not cart:
        st.info("购物车为空")
    else:
        for item in cart:
            st.markdown(f"• {item['name']} x{item['qty']} = ¥{item['price']*item['qty']:.2f}")

        total = sum(item["price"] * item["qty"] for item in cart)
        st.markdown(f"---")
        st.metric("订单总额", f"¥{total:.2f}")

        if st.button("[MoneyBag] 结算", use_container_width=True, type="primary"):
            process_checkout_expression()
            st.rerun()

    st.divider()

    # 快捷操作
    st.markdown("### ⚡ 快捷操作")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📦 查看商品", use_container_width=True):
            msg = "查看商品"
            handle_user_message(msg)

    with col2:
        if st.button("💰 开设委托", use_container_width=True):
            msg = "开设委托 500"
            handle_user_message(msg)

    st.divider()

    # 自动购买
    tasks = st.session_state.auto_purchase_tasks

    st.markdown("🤖 自动购买")

    if not tasks:
        st.info("暂无任务")
    else:
        for i in range(len(tasks)):
            st.write(f"{i+1}. {tasks[i].get('name', '任务')}")

        if st.button("▶ 执行", use_container_width=True):
            handle_run_auto_purchase()