"""
Streamlit Web UI
ACT 协议 - 电商助手与委托支付演示
"""
import streamlit as st
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入核心服务
from merchant_service.service import merchant_service
from payment_service.service import PaymentService
from psd.delegated_payment import (
    DelegatedPaymentHandler,
    DelegationApplyRequest,
    DelegationQueryRequest,
    DelegationCancelRequest,
    DelegationPayRequest
)
from psd.delegated_payment.payload import PaymentTokenInfo, DelegatedPaymentPayload

# 导入支付服务
from payment_service.instant_payment import InstantPaymentService, InstantPayRequest
from payment_service.delegated_payment import DelegatedPaymentService
from payment_service.autonomous_payment import AutonomousPaymentService, PaymentStrategy

# 导入身份选择界面（新功能）
from ui.identity_select import render_identity_select, render_user_interface, render_merchant_interface

# 导入购物助手和商户服务界面
from ui.shopping_assistant import render_shopping_assistant_tab, init_shopping_assistant_state
from ui.merchant_service_ui import render_merchant_service_tab
from ui.payment_demo import render_payment_demo_tab
from assistant_agent.delegation_agent import DelegationAgent

# 页面配置
st.set_page_config(
    page_title="ACT 协议 - 电商助手 & 委托支付",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .role-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .agent-badge {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .merchant-badge {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
    .payment-badge {
        background-color: #e8f5e9;
        color: #388e3c;
    }
    .delegation-badge {
        background-color: #fef3e2;
        color: #f57c00;
    }
    .sidebar-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化 Session State"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 角色相关状态
    if "current_role" not in st.session_state:
        st.session_state.current_role = None  # None, "user", "merchant"

    if "role_history" not in st.session_state:
        st.session_state.role_history = []

    # 智能代理配置（电商购物助手）
    if "smart_agent_config" not in st.session_state:
        st.session_state.smart_agent_config = {
            "enabled": False,
            "price_alerts": [],  # 价格预警：[{"item_id": "...", "target_price": 100}]
            "auto_purchase": False,  # 自动购买开关
            "schedule_purchase": [],  # 定时购买：[{"item_id": "...", "trigger_time": "10:00"}]
        }

    # 监控中的商品
    if "monitored_items" not in st.session_state:
        st.session_state.monitored_items = []

    # 自动执行记录
    if "auto_execution_log" not in st.session_state:
        st.session_state.auto_execution_log = []

    if "agent" not in st.session_state:
        st.session_state.agent = None
        st.session_state.agent_mode = "rule"

    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False

    # 委托支付 Agent
    if "delegation_agent" not in st.session_state:
        st.session_state.delegation_agent = DelegationAgent()
        st.session_state.agent_chat_delegation = st.session_state.delegation_agent.process_delegation_command

    # 核心服务实例（共享）
    if "merchant_service" not in st.session_state:
        st.session_state.merchant_service = merchant_service

    if "payment_service" not in st.session_state:
        st.session_state.payment_service = PaymentService(merchant_service)

    # 委托支付相关状态
    if "delegation_handler" not in st.session_state:
        st.session_state.delegation_handler = DelegatedPaymentHandler()

    if "active_delegation" not in st.session_state:
        st.session_state.active_delegation = None

    if "cart_items" not in st.session_state:
        st.session_state.cart_items = []

    # 支付服务（分离）
    from payment_service.instant_payment import InstantPaymentService
    from payment_service.delegated_payment import DelegatedPaymentService
    if "instant_service" not in st.session_state:
        st.session_state.instant_service = InstantPaymentService(merchant_service)
    if "delegated_service" not in st.session_state:
        st.session_state.delegated_service = DelegatedPaymentService()

    # Agent 配置（购物助手）
    if "agent_config" not in st.session_state:
        st.session_state.agent_config = {
            "user_id": "user-shopping-assistant",
            "auto_purchase_enabled": False,
            "price_alert_enabled": True,
            "max_price_threshold": 100.0
        }

    # 用户角色专用状态
    if "user_wishlist" not in st.session_state:
        st.session_state.user_wishlist = []  # 心愿单

    if "user_orders" not in st.session_state:
        st.session_state.user_orders = []  # 用户订单

    # 商户角色专用状态
    if "merchant_products" not in st.session_state:
        st.session_state.merchant_products = []  # 商户商品

    if "merchant_notifications" not in st.session_state:
        st.session_state.merchant_notifications = []  # 商户通知

    # 商品变更通知（全局共享）
    if "product_notifications" not in st.session_state:
        st.session_state.product_notifications = []  # 商品变更通知


def initialize_agent(mode: str, api_key: str = None, model: str = "gpt-3.5-turbo"):
    """初始化助理 Agent"""
    from assistant_agent.agent import create_assistant_agent

    try:
        if mode == "rule":
            st.session_state.agent = create_assistant_agent()
            st.session_state.agent_mode = "rule"
            st.session_state.agent_initialized = True
            return True, "助理 Agent 初始化成功（规则模式）"

        elif mode == "llm":
            if not api_key:
                return False, "请提供 OpenAI API Key"

            st.session_state.agent = create_assistant_agent(
                api_key=api_key,
                model=model
            )
            st.session_state.agent_mode = "llm"
            st.session_state.agent_initialized = True
            return True, f"助理 Agent 初始化成功（LLM 模式 - {model}）"

        else:
            return False, "未知的 Agent 模式"

    except Exception as e:
        return False, f"初始化失败：{str(e)}"


def render_ecommerce_tab():
    """渲染电商购物标签页"""
    st.markdown('<div class="main-header">🛒 电商购物助手</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">基于 ACT 协议的商业交互演示</div>', unsafe_allow_html=True)

    # 显示角色说明
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span class="role-badge agent-badge">🤖 助理 Agent</span>
        <span style="color: #999;">→</span>
        <span class="role-badge merchant-badge">🏪 商户服务</span>
        <span style="color: #999;">+</span>
        <span class="role-badge payment-badge">💳 支付服务</span>
    </div>
    """, unsafe_allow_html=True)

    # 主聊天区域
    st.markdown("---")

    if not st.session_state.agent_initialized:
        st.warning("⚠️ 请先在左侧初始化助理 Agent")
        return

    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 用户输入
    if prompt := st.chat_input("请输入您的消息..."):
        # 添加用户消息到历史
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 获取 Agent 响应
        with st.chat_message("assistant"):
            with st.spinner("助理 Agent 正在处理..."):
                try:
                    response = st.session_state.agent.chat(prompt)
                    st.markdown(response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    error_msg = f"❌ 处理消息时出错：{str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


def render_delegation_tab():
    """
    渲染委托支付标签页 - 交互式智能体代理界面

    支持两种场景：
    1. 场景二：平台型智能体定向委托
    2. 场景三：专属型智能体定向委托
    """
    st.markdown('<div class="main-header">💼 ACT 协议委托支付 (PSD-PAY-DEL)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">智能体自主支付 - 基于 IAC 的可信授权</div>', unsafe_allow_html=True)

    # 场景选择面板
    st.markdown("### 📋 选择委托支付场景")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🏢 场景二：平台型智能体定向委托

        **适用情形：**
        - 委托人不在场
        - 购买标的已在初始交互中明确
        - 多租户共享平台智能体

        **核心特征：**
        - 双重身份验证（平台 + 委托人）
        - 跨委托人风险隔离
        - 授权边界内程序化支付

        **典型示例：**
        > "帮我订明天上午飞北京的机票，不超过 1200 元"
        """)

    with col2:
        st.markdown("""
        ### 🎯 场景三：专属型智能体定向委托

        **适用情形：**
        - 委托人不在场
        - 购买标的已在初始交互中明确
        - 智能体与委托人设备/账号强绑定

        **核心特征：**
        - 独立唯一智能体身份
        - 支持子账户风险隔离
        - 直接锚定专属智能体验证

        **典型示例：**
        > "帮我买《人工智能：现代方法》这本书，不超过 150 元"
        """)

    # 场景选择
    selected_scenario = st.radio(
        "选择演示场景",
        options=["场景二：平台型智能体", "场景三：专属型智能体"],
        help="选择后将按照所选场景的配置流程进行演示"
    )

    st.markdown("---")

    # 功能说明
    st.info("""
    **委托支付流程：**

    1. **签约** → 签发 IAC 凭证
    2. **查询** → 查询协议状态
    3. **支付** → 智能体自动执行
    4. **监控** → 查看累计额度
    """)

    # 初始化场景参数
    if "delegation_scenario" not in st.session_state:
        st.session_state.delegation_scenario = selected_scenario

    # 创建两个列：左侧操作面板，右侧状态显示
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.header("📋 操作面板")

        # Tab 用于不同操作
        op_tab1, op_tab2, op_tab3, op_tab4 = st.tabs(["1. 签约", "2. 查询", "3. 支付", "4. 吊销"])

        # Tab 1: 签约
        with op_tab1:
            st.subheader("签署委托协议")

            with st.form("apply_form"):
                principal_id = st.text_input(
                    "委托人 ID",
                    value="did:act:example.com/user-alice",
                    help="委托人去中心化身份"
                )

                agent_id = st.text_input(
                    "智能体 ID",
                    value="did:act:example.com/agent-alice-001",
                    help="受托智能体去中心化身份"
                )

                delegation_id = st.text_input(
                    "委托标识",
                    value="urn:uuid:7f3e9a12-b4c8-4d56-a321-8b7c6d5e4f30",
                    help="UUID 格式的委托标识"
                )

                col1, col2 = st.columns(2)
                with col1:
                    max_total = st.number_input(
                        "总金额上限",
                        min_value=0.0,
                        value=5000.0,
                        step=100.0,
                        format="%.2f"
                    )
                with col2:
                    max_single = st.number_input(
                        "单笔金额上限",
                        min_value=0.0,
                        value=1000.0,
                        step=100.0,
                        format="%.2f"
                    )

                submitted = st.form_submit_button("签发 IAC", use_container_width=True, type="primary")

                if submitted:
                    result = st.session_state.delegation_handler.apply_delegation(
                        DelegationApplyRequest(
                            principal_id=principal_id,
                            agent_id=agent_id,
                            delegation_id=delegation_id,
                            max_total_amount=max_total,
                            max_single_amount=max_single
                        )
                    )

                    if result.message:
                        st.success(f"✅ {result.message}")
                        # 保存委托信息
                        st.session_state.active_delegation = {
                            "delegation_id": result.delegation_id,
                            "iac": result.iac,
                            "principal_id": principal_id,
                            "max_total": result.max_total_amount,
                            "max_single": result.max_single_amount or 0
                        }
                        st.session_state.messages.append({
                            "role": "system",
                            "content": f"委托已签发：{result.delegation_id}"
                        })

        # Tab 2: 查询
        with op_tab2:
            st.subheader("查询委托状态")

            if st.session_state.active_delegation:
                if st.button("查询当前委托状态", type="primary"):
                    query_result = st.session_state.delegation_handler.query_delegation(
                        DelegationQueryRequest(
                            delegation_id=st.session_state.active_delegation["delegation_id"],
                            principal_id=st.session_state.active_delegation.get("principal_id", "")
                        )
                    )

                    st.json({
                        "delegation_id": query_result.delegation_id,
                        "status": query_result.status,
                        "cumulative_amount": query_result.cumulative_amount,
                        "message": "查询成功"
                    })
            else:
                st.warning("请先在「1. 签约」中签发委托协议")

        # Tab 3: 支付
        with op_tab3:
            st.subheader("执行委托支付")

            if st.session_state.active_delegation:
                # 先显示购物车
                st.markdown("### 🛒 选择商品")

                # 从商户服务获取商品列表
                products_result = merchant_service.get_product_list()

                if products_result["success"]:
                    cols = st.columns(4)
                    for i, product in enumerate(products_result["data"]):
                        with cols[i % 4]:
                            if st.button(
                                f"{product['name']}\n¥{product['price']:.2f}",
                                key=f"prod_{product['item_id']}",
                                use_container_width=True
                            ):
                                st.session_state.cart_items = [{
                                    "item_id": product["item_id"],
                                    "name": product["name"],
                                    "price": product["price"],
                                    "qty": 1
                                }]
                                st.success(f"已添加 {product['name']} 到购物车")
                                st.rerun()

                # 显示购物车
                if st.session_state.cart_items:
                    st.markdown("### 📝 购物车")
                    total = sum(item["price"] * item["qty"] for item in st.session_state.cart_items)

                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**商品明细**:")
                        for item in st.session_state.cart_items:
                            st.markdown(f"• {item['name']}: ¥{item['price']:.2f} x {item['qty']}")
                    with col2:
                        st.markdown("**订单总额**")
                        st.markdown(f"### ¥{total:.2f}")

                    # 计算购物车快照
                    cart_hash = DelegatedPaymentPayload.calculate_cart_snapshot_hash(
                        [{"item_id": item["item_id"], "name": item["name"], "price": item["price"]}
                         for item in st.session_state.cart_items]
                    )

                    # 支付表单
                    with st.form("pay_form"):
                        pay_amount = st.number_input(
                            "支付金额",
                            min_value=0.0,
                            value=total,
                            step=1.0,
                            format="%.2f",
                            key="pay_amt"
                        )

                        col1, col2 = st.columns(2)
                        with col1:
                            payment_method = st.text_input(
                                "支付方式",
                                value="urn:act:payment:example-wallet"
                            )
                        with col2:
                            payment_token = st.text_input(
                                "支付标记 Token",
                                value="t_mock_token_abc123"
                            )

                        col1, col2 = st.columns(2)
                        with col1:
                            submit_pay = st.form_submit_button(
                                "🚀 提交支付",
                                use_container_width=True,
                                type="primary"
                            )
                        with col2:
                            if st.button(
                                "清空购物车",
                                use_container_width=True
                            ):
                                st.session_state.cart_items = []
                                st.rerun()

                    if submit_pay:
                        # 执行支付
                        pay_req = DelegationPayRequest(
                            request_id=f"pay-{st.session_state.active_delegation['delegation_id'][:8]}",
                            buyer_agent_id=st.session_state.active_delegation.get("agent_id", "did:act:agent"),
                            delegation_id=st.session_state.active_delegation["delegation_id"],
                            iac=st.session_state.active_delegation["iac"],
                            merchant_id="did:act:merchant-shop",
                            merchant_order_id=f"ORD-{st.time.time_ns()}",
                            cart_snapshot_hash=cart_hash,
                            amount=pay_amount,
                            currency="CNY",
                            payment_token=PaymentTokenInfo(token=payment_token)
                        )

                        pay_result = st.session_state.delegation_handler.pay(pay_req)

                        if pay_result.success:
                            st.success("✅ 支付成功！")
                            st.success(f"""
                            **支付详情：**
                            - 支付流水号：{pay_result.payment_id}
                            - 交易流水号：{pay_result.transaction_id}
                            - 订单号：MCH20240514123456789
                            - 支付金额：¥{pay_result.amount:.2f}
                            - 状态：{pay_result.status}
                            """)
                        else:
                            st.error(f"❌ 支付失败：{pay_result.error_message or '未知错误'}")
            else:
                st.warning("请先在「1. 签约」中签发委托协议")

        # Tab 4: 吊销
        with op_tab4:
            st.subheader("吊销委托授权")

            if st.session_state.active_delegation:
                if st.button(
                    "吊销当前委托",
                    type="primary",
                    use_container_width=True
                ):
                    cancel_result = st.session_state.delegation_handler.cancel_delegation(
                        DelegationCancelRequest(
                            delegation_id=st.session_state.active_delegation["delegation_id"],
                            principal_id="did:act:example.com/user-alice",
                            reason="任务完成，取消委托"
                        )
                    )

                    st.success(f"✅ {cancel_result.message}")
                    st.session_state.active_delegation = None
                    st.rerun()
            else:
                st.warning("当前没有活动的委托")

    with right_col:
        st.header("📊 委托状态")

        if st.session_state.active_delegation:
            st.success("✅ 委托已生效")
            st.markdown("---")

            st.metric("委托 ID", st.session_state.active_delegation["delegation_id"][:32] + "...")

            # 获取累计金额
            cumulative = st.session_state.delegation_handler.payment_service.get_cumulative_amount(
                st.session_state.active_delegation["delegation_id"]
            )

            st.metric(
                "累计扣款",
                f"¥{cumulative:.2f}",
                help="已在该委托下支付的总金额"
            )

            max_total = st.session_state.active_delegation["max_total"]
            remaining = max_total - cumulative

            status_color = "🟢" if remaining > 0 else "🔴"
            st.metric(
                "剩余额度",
                f"{status_color} ¥{remaining:.2f}",
                help="还可支付的金额"
            )

            st.markdown("---")
            st.info("""
            **IAC 凭证信息：**

            - **委托人**：`did:act:user-alice`
            - **智能体**：`did:act:agent-alice-001`
            - **委托模式**：SPECIFIED（定向委托）
            - **总金额上限**：¥5,000.00
            - **单笔上限**：¥1,000.00
            """)

            with st.expander("📜 查看 IAC JWT"):
                st.code(
                    st.session_state.active_delegation["iac"],
                    language="json",
                    line_numbers=False
                )

        else:
            st.warning("🚫 暂无活动委托")
            st.markdown("""
            要开始使用委托支付，请：

            1. 在「操作面板」→「1. 签约」中签发 IAC
            2. 然后即可进行查询、支付和吊销操作
            """)

        # 累计记录
        st.markdown("---")
        st.header("📈 累计扣款记录")

        cumulative_records = []
        for payment in st.session_state.delegation_handler.payment_service.payments.values():
            if payment.get("verification_result", {}).get("iac_valid"):
                cumulative_records.append({
                    "payment_id": payment["payment_id"],
                    "amount": payment["amount"],
                    "status": payment["status"],
                    "created_at": payment["created_at"]
                })

        if cumulative_records:
            st.json(cumulative_records)
        else:
            st.info("暂无支付记录")


def main():
    """主函数"""
    # 初始化 Session State
    init_session_state()

    # 检查是否已选择角色
    if st.session_state.current_role is None:
        # 未选择角色，显示身份选择界面
        render_identity_select()
    else:
        # 已选择角色，显示对应角色的界面
        render_role_based_interface()


def render_role_based_interface():
    """根据当前角色渲染对应界面"""
    role = st.session_state.current_role

    # 数据同步提示
    if "sync_message" in st.session_state:
        st.info(st.session_state.sync_message)
        del st.session_state.sync_message

    # 用户视图 - 显示商户服务通知
    if role == "user":
        show_merchant_notification()

    # 显示角色切换按钮（右上角）
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button(
            "⇄ " + ("商户 🏪" if role == "user" else "用户 👤"),
            key="switch_role_btn",
            use_container_width=True
        ):
            new_role = "merchant" if role == "user" else "user"
            st.session_state.current_role = new_role
            st.session_state.role_history.append((new_role, str(st.timestamp() if hasattr(st, 'timestamp') else "now")))
            st.session_state.sync_message = f"⚠️ 切换到{('用户' if new_role == 'user' else '商户')}角色 - 商品和订单数据将实时同步"
            st.rerun()

    if role == "user":
        render_user_view()
    else:
        render_merchant_view()


def show_merchant_notification():
    """显示商户服务通知"""
    notifications = st.session_state.product_notifications
    if notifications:
        st.markdown("---")
        st.markdown("### 📢 商户服务通知")
        for notif in notifications[-3:]:
            time_str = notif.get("timestamp", "")
            action = notif.get("action", "")
            product = notif.get("product", {})
            if action == "created":
                st.success(f"🆕 新商品上架：{product.get('name', '')}")
            elif action == "deleted":
                st.info(f"🗑️ 商品下架：{product.get('name', '')}")


def _render_role_status_badge():
    """渲染角色状态徽章"""
    role = st.session_state.current_role
    role_name = "用户 👤" if role == "user" else "商户 🏪"
    col1, col2 = st.columns([4, 1])
    with col2:
        st.markdown(
            f"""
            <div style="
                background-color: {'#e3f2fd' if role == 'user' else '#f3e5f5'};
                color: {'#1976d2' if role == 'user' else '#7b1fa2'};
                padding: 10px 20px;
                border-radius: 20px;
                font-weight: bold;
                text-align: center;
            ">
                ✅ {role_name}
            </div>
            """,
            unsafe_allow_html=True
        )


def render_user_view():
    """渲染用户视图"""
    st.markdown('<div class="main-header">👤 用户中心 - ACT 协议</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">智能购物 & 委托支付</div>', unsafe_allow_html=True)

    # 用户功能 Tabs - 新增支付模式演示首页
    user_tabs = st.tabs([
        "🎯 支付模式演示",
        "🤖 智能体对话 (智能购物助手)",
        "💳 即时支付",
        "💰 委托支付管理",
        "📦 我的订单",
        "🔔 通知中心"
    ])

    with user_tabs[0]:
        # 支付模式演示首页 - 三种支付方式对比和可视化
        render_payment_demo_tab()

    with user_tabs[1]:
        # 智能体对话 Tab - 使用购物助手界面（左右分栏）
        st.subheader("🤖 AI 智能购物助手")
        st.info("这是一个**AI 智能体助手**，您可以直接与其对话来完成购物任务！")

        # 检查是否已初始化智能体
        if not st.session_state.agent_initialized:
            st.info("💡 请先初始化智能体助手")

            # Agent 模式选择
            agent_mode = st.radio(
                "选择 Agent 模式",
                options=["rule (规则模式)", "llm (LLM 模式)"],
                format_func=lambda x: {
                    "rule (规则模式)": "📋 规则模式 - 使用预定义规则",
                    "llm (LLM 模式)": "🧠 LLM 模式 - 使用大语言模型"
                }.get(x, x)
            )

            api_key = None
            model = "gpt-3.5-turbo"

            if agent_mode == "llm (LLM 模式)":
                api_key = st.text_input(
                    "OpenAI API Key（可选）",
                    type="password",
                    help="输入您的 OpenAI API Key 以使用 LLM 模式，如果不填将使用规则模式",
                    key="user_api_key"
                )

            if st.button("🚀 初始化智能体助手", type="primary", use_container_width=True):
                with st.spinner("正在初始化..."):
                    # 根据选择调用初始化
                    if agent_mode == "llm (LLM 模式)" and api_key:
                        success, message = initialize_agent("llm", api_key, model)
                    else:
                        success, message = initialize_agent("rule", None, None)

                    if success:
                        st.success(message)
                        # 初始化购物助手 state
                        init_shopping_assistant_state()
                        st.session_state.messages = []
                        st.rerun()
                    else:
                        st.error(message)
        else:
            # 显示购物助手界面（左右分栏）
            render_shopping_assistant_tab()

    with user_tabs[1]:
        st.subheader("💳 即时支付")
        st.info("直接选择商品并完成支付")

        if st.session_state.cart_items:
            st.markdown("### 🛒 购物车")
            total = sum(item['price'] for item in st.session_state.cart_items)
            for item in st.session_state.cart_items:
                st.markdown(f"- {item['name']}: ¥{item['price']:.2f}")
            st.metric("订单总额", f"¥{total:.2f}")

            if st.button("💰 立即支付", type="primary"):
                # 这里可以集成即时支付逻辑
                st.success("支付成功！")
                st.session_state.cart_items = []
                st.rerun()
        else:
            st.info("购物车为空，请先添加商品")

    with user_tabs[2]:
        # 委托支付管理 Tab - 智能体对话驱动
        st.subheader("💰 委托支付管理")
        st.markdown("""
        **向智能体下达委托指令**

        您可以直接与智能体对话，下达委托支付任务。智能体将在授权范围内代为支付。

        **可以对我说的委托指令：**
        - "开设委托 5000 元额度"
        - "查询委托状态"
        - "购买 {商品名}"
        - "取消委托"
        """)

        # 显示委托 Agent 聊天界面
        _render_delegation_chat()

    # 在下方显示当前委托状态

    with user_tabs[3]:
        # 智能体对话 Tab
        st.subheader("📦 我的订单")
        st.info("查看您的所有订单记录")

        # 获取所有订单
        orders_result = merchant_service.get_all_orders()
        if orders_result["success"] and orders_result["data"]:
            for order in orders_result["data"]:
                status_colors = {
                    "paid": "🟢",
                    "pending_payment": "🟡",
                    "cancelled": "⚪"
                }
                status = order.get("status", "unknown")
                st.markdown(
                    f"**{order.get('order_id', 'N/A')}** {status_colors.get(status, '⚪')} "
                    f"¥{order.get('total_amount', 0):.2f}"
                )
        else:
            st.info("暂无订单")

    with user_tabs[4]:
        st.subheader("🔔 通知中心")
        st.info("接收商品变更通知")

        # 显示通知
        notifications = st.session_state.product_notifications
        if notifications:
            for notif in notifications:
                st.info(f"{notif.get('timestamp', '')}: {notif.get('message', '')}")
        else:
            st.info("暂无通知")

    # 显示当前委托状态（在所有用户视图的底部）
    _render_delegation_status()


def _render_delegation_status():
    """渲染当前委托状态（在所有用户视图的底部）"""
    if not st.session_state.active_delegation:
        return

    st.markdown("---")
    st.markdown('#### 📊 当前委托状态')
    delegation = st.session_state.active_delegation
    cumulative = st.session_state.delegated_service.get_cumulative_amount(
        delegation["delegation_id"]
    )
    remaining = delegation["max_total"] - cumulative

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("委托 ID", delegation["delegation_id"][:20] + "...")
    with col2:
        st.metric("总额度", f"¥{delegation['max_total']:.2f}")
    with col3:
        st.metric("累计支付", f"¥{cumulative:.2f}")
    with col4:
        st.metric("剩余额度", f"¥{remaining:.2f}")

    st.divider()

    if st.button("🔒 吊销委托", type="primary", key="revoke_delegation_btn"):
        if st.session_state.delegated_service.cancel(
            delegation["delegation_id"],
            "用户请求取消"
        ).get("success"):
            st.session_state.active_delegation = None
            st.success("委托已吊销")
            st.rerun()
        else:
            st.error("吊销失败")


def render_ai_chat_interface():
    """渲染 AI 智能体对话界面"""
    st.markdown("---")

    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 用户输入
    if prompt := st.chat_input("输入指令，例如：'帮我买 iPhone，不超过 10000 元' 或 '下单购物车里的商品'"):
        # 添加用户消息到历史
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 获取智能体响应
        with st.chat_message("assistant"):
            with st.spinner("智能体助手正在处理..."):
                try:
                    response = st.session_state.agent.chat(prompt)
                    st.markdown(response)

                    # 解析响应并执行操作
                    execute_shopping_commands(response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    error_msg = f"❌ 处理消息时出错：{str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


def execute_shopping_commands(response: str):
    """执行购物相关指令"""
    # 简单的命令解析，可以根据需求扩展
    if "添加到购物车" in response or "加入购物车" in response:
        # 自动添加商品到购物车
        pass


def _render_delegation_chat():
    """渲染委托支付 Agent 聊天界面"""
    if not st.session_state.agent_initialized:
        st.info("💡 请先初始化智能体助手")
        return

    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 用户输入
    if prompt := st.chat_input("输入委托指令，例如：'开设委托 5000' 或 '购买 Apple'"):
        # 添加用户消息到历史
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 获取智能体响应
        with st.chat_message("assistant"):
            with st.spinner("智能体正在处理委托指令..."):
                try:
                    response = st.session_state.agent_chat_delegation(prompt)
                    st.markdown(response)

                    # 将响应添加到消息历史
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    error_msg = f"❌ 处理委托指令时出错：{str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


def render_merchant_view():
    """渲染商户视图"""
    st.markdown('<div class="main-header">🏪 商户服务中心 - ACT 协议</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">商品管理 & 订单处理</div>', unsafe_allow_html=True)

    # 商户功能 Tabs
    merchant_tabs = st.tabs([
        "📦 商品管理",
        "📋 订单处理",
        "📈 数据看板",
        "⚙️ 设置"
    ])

    with merchant_tabs[0]:
        render_merchant_product_management()

    with merchant_tabs[1]:
        render_merchant_order_management()

    with merchant_tabs[2]:
        render_merchant_data_dashboard()

    with merchant_tabs[3]:
        st.subheader("⚙️ 商户设置")
        st.info("配置您的商户服务")

        # 商户配置项
        config_col1, config_col2 = st.columns(2)
        with config_col1:
            merchant_name = st.text_input("商户名称", value="ACT Demo Shop")
            commission_rate = st.number_input("服务费率 (%)", min_value=0.0, value=2.5, step=0.1)
        with config_col2:
            auto_approve = st.checkbox("自动审核商品", value=True)
            notify_users = st.checkbox("商品发布时通知用户", value=True)

        if st.button("💾 保存设置"):
            st.success("设置已保存！")


def render_merchant_product_management():
    """商户商品管理"""
    st.markdown("### 📦 商品管理")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ➕ 新增商品")

        with st.form("add_product"):
            name = st.text_input("商品名称 *", placeholder="如：iPhone 15 Pro")
            price = st.number_input("价格 (¥) *", min_value=0.0, step=1.0, format="%.2f")
            stock = st.number_input("库存", min_value=0, value=100)
            category = st.selectbox("类别", ["数码", "服装", "食品", "书籍", "其他"])

            submitted = st.form_submit_button("上架商品", type="primary")

            if submitted:
                result = merchant_service.register_product(
                    name=name,
                    price=price,
                    category=category,
                    stock=stock
                )
                if result["success"]:
                    st.success(f"✅ 商品上架成功！商品 ID: {result['data']['item_id'][:16]}...")
                    st.rerun()
                else:
                    st.error(f"上架失败：{result['message']}")

    with col2:
        st.markdown("### 📋 商品列表")

        products_result = merchant_service.get_product_list()
        if products_result["success"] and products_result["data"]:
            for product in products_result["data"]:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**{product['name']}**")
                        st.caption(f"库存：{product['stock']}")
                    with col2:
                        st.metric("价格", f"¥{product['price']:.2f}")
                    with col3:
                        if st.button("下架", key=f"del_{product['item_id']}"):
                            merchant_service.delete_product(product["item_id"])
                            st.success("已下架")
                            st.rerun()
        else:
            st.info("暂无商品")


def render_merchant_order_management():
    """商户订单管理"""
    st.markdown("### 📋 订单处理")

    orders_result = merchant_service.get_all_orders()
    if orders_result["success"] and orders_result["data"]:
        for order in orders_result["data"]:
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**订单号**: {order.get('order_id', 'N/A')}")
                with col2:
                    status = order.get('status', 'unknown')
                    status_emoji = {"paid": "✅", "pending_payment": "⏳", "cancelled": "❌"}.get(status, "❓")
                    st.markdown(f"**状态**: {status_emoji} {status}")
                with col3:
                    st.metric("金额", f"¥{order.get('total_amount', 0):.2f}")
    else:
        st.info("暂无订单")


def render_merchant_data_dashboard():
    """商户数据看板"""
    st.markdown("### 📊 经营数据看板")

    products_result = merchant_service.get_product_list()
    orders_result = merchant_service.get_all_orders()

    products = products_result.get("data", [])
    orders = orders_result.get("data", [])

    # 核心指标
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("商品总数", f"{len(products)}")
    with col2:
        st.metric("订单总数", f"{len(orders)}")
    with col3:
        paid_orders = [o for o in orders if o.get("status") == "paid"]
        st.metric("已支付", f"{len(paid_orders)}")
    with col4:
        revenue = sum(o.get("total_amount", 0) for o in paid_orders)
        st.metric("总营收", f"¥{revenue:.2f}")

    # 收入趋势
    st.markdown("### 💰 收入趋势")
    if orders:
        paid_amounts = [o.get("total_amount", 0) for o in orders if o.get("status") == "paid"]
        st.bar_chart(paid_amounts)
    else:
        st.info("暂无收入数据")


if __name__ == "__main__":
    main()