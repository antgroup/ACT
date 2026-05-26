"""
身份选择界面 (Identity Select UI)
ACT 协议 - 用户/商户身份选择与角色切换
"""
import streamlit as st
from typing import Optional


def render_identity_select():
    """
    渲染身份选择主界面

    界面布局:
    - 欢迎来到 ACT 协议页面
    - 角色选择卡片 (用户/商户)
    - 角色切换功能
    """
    init_identity_state()

    # 页面标题
    st.markdown('<div class="main-header">🎭 ACT 协议 - 身份选择</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">请选择您的角色以进入相应服务</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        render_user_card()

    with col2:
        render_merchant_card()

    # 显示消息历史
    if "identity_messages" not in st.session_state:
        st.session_state.identity_messages = []

    if st.session_state.identity_messages:
        st.markdown("---")
        for msg in st.session_state.identity_messages:
            st.info(msg)


def init_identity_state():
    """初始化身份选择专用 session state"""
    if "current_role" not in st.session_state:
        st.session_state.current_role = None  # None, "user", "merchant"

    if "role_history" not in st.session_state:
        st.session_state.role_history = []  # 记录角色切换历史


def render_user_card():
    """渲染用户角色卡片"""
    is_selected = st.session_state.current_role == "user"

    with st.container(border=True):
        if is_selected:
            st.markdown('### ✅ 已选择：用户', help="您已选择用户角色")
        else:
            st.markdown('### 用户', help="作为用户，您可以：智能购物、委托支付")

        st.markdown("""
        <div style="text-align: center; margin: 1rem 0;">
            <div style="font-size: 4rem;">👤</div>
            <p style="color: #666;">我的智能购物助手</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**可用功能**:")
        st.markdown("""
        - 🛒 查看商品列表
        - 🛍️ 添加到购物车
        - 💳 **即时支付** - 直接购买
        - 💼 **委托支付** - 授权智能体代买
        - 📦 订单查询
        - 🔔 商品变更通知
        """)

        if not is_selected:
            if st.button("选择用户角色", key="select_user", use_container_width=True, type="primary"):
                st.session_state.current_role = "user"
                st.session_state.role_history.append(("user", st.timestamp() if hasattr(st, 'timestamp') else "now"))
                st.success("✅ 已切换至用户角色")
                st.rerun()
        else:
            st.success("✅ 用户角色已激活")
            if st.button("切换到商户", key="switch_to_merchant", use_container_width=True):
                st.session_state.current_role = "merchant"
                st.session_state.role_history.append(("merchant", "now"))
                st.session_state.sync_message = "⚠️ 切换后将同步商品和订单数据"
                st.rerun()


def render_merchant_card():
    """渲染商户角色卡片"""
    is_selected = st.session_state.current_role == "merchant"

    with st.container(border=True):
        if is_selected:
            st.markdown('### ✅ 已选择：商户', help="您已选择商户角色")
        else:
            st.markdown('### 商户', help="作为商户，您可以：管理商品、查看订单")

        st.markdown("""
        <div style="text-align: center; margin: 1rem 0;">
            <div style="font-size: 4rem;">🏪</div>
            <p style="color: #666;">商户服务后台</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**可用功能**:")
        st.markdown("""
        - 📦 商品管理（上架/下架/编辑）
        - 💰 价格调整
        - 📊 订单管理
        - 📈 经营数据看板
        - 🔔 实时通知商品变更
        """)

        if not is_selected:
            if st.button("选择商户角色", key="select_merchant", use_container_width=True, type="primary"):
                st.session_state.current_role = "merchant"
                st.session_state.role_history.append(("merchant", st.timestamp() if hasattr(st, 'timestamp') else "now"))
                st.success("✅ 已切换至商户角色")
                st.rerun()
        else:
            st.success("✅ 商户角色已激活")
            if st.button("切换到用户", key="switch_to_user", use_container_width=True):
                st.session_state.current_role = "user"
                st.session_state.role_history.append(("user", "now"))
                st.session_state.sync_message = "⚠️ 切换后将同步商品和订单数据"
                st.rerun()


def render_role_features():
    """渲染当前所选角色的功能说明"""
    if not st.session_state.current_role:
        st.info("💡 请选择左上角或右上角的角色卡片以开始使用")
        return

    role = st.session_state.current_role
    st.markdown("---")
    st.markdown(f"### 📋 您的角色：**{'用户' if role == 'user' else '商户'}**")

    if role == "user":
        st.markdown("""
        **用户角色功能简介：**

        1. **智能购物助手** - AI 助手帮您完成购物流程
        2. **即时支付** - 直接完成购买
        3. **委托支付** - 授权智能体代为支付

        <div style="margin-top: 1rem;">
            <button onclick="document.querySelector('.user-tab').click()" style="padding: 10px 20px; background-color: #1f77b4; color: white; border: none; border-radius: 5px; cursor: pointer;">进入用户界面</button>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        **商户角色功能简介：**

        1. **商品管理** - 上架、下架、编辑商品
        2. **订单管理** - 查看和管理订单
        3. **数据看板** - 经营数据可视化

        <div style="margin-top: 1rem;">
            <button onclick="document.querySelector('.merchant-tab').click()" style="padding: 10px 20px; background-color: #7b1fa2; color: white; border: none; border-radius: 5px; cursor: pointer;">进入商户界面</button>
        </div>
        """, unsafe_allow_html=True)


def render_current_role_interface():
    """渲染当前所选角色的专属界面"""
    if not st.session_state.current_role:
        return

    role = st.session_state.current_role

    if role == "user":
        render_user_interface()
    else:
        render_merchant_interface()


def render_user_interface():
    """渲染用户专属界面"""
    st.markdown("---")

    # 用户界面选项
    user_tabs = st.tabs(["💼 智能购物助手", "💳 即时支付", "💰 委托支付", "📦 我的订单"])

    with user_tabs[0]:
        st.subheader("智能购物助手")
        st.info("AI 助手将帮您完成商品挑选、添加到购物车、支付等全流程。")
        # TODO: 这里可以嵌入购物助手界面

    with user_tabs[1]:
        st.subheader("即时支付")
        st.info("直接选择商品并完成支付。")
        # TODO: 这里可以嵌入即时支付界面

    with user_tabs[2]:
        st.subheader("委托支付")
        st.info("授权智能体在额度范围内代为支付。")
        # TODO: 这里可以嵌入委托支付界面

    with user_tabs[3]:
        st.subheader("我的订单")
        st.info("查看您的所有订单记录。")
        # TODO: 这里可以嵌入订单查询界面


def render_merchant_interface():
    """渲染商户专属界面"""
    st.markdown("---")

    # 商户界面选项
    merchant_tabs = st.tabs(["📦 商品管理", "📋 订单管理", "📈 数据看板"])

    with merchant_tabs[0]:
        st.subheader("商品管理")
        st.info("管理您的商品库 - 上架、下架、编辑。")
        # TODO: 这里可以嵌入商品管理界面

    with merchant_tabs[1]:
        st.subheader("订单管理")
        st.info("查看所有订单及其状态。")
        # TODO: 这里可以嵌入订单管理界面

    with merchant_tabs[2]:
        st.subheader("数据看板")
        st.info("查看经营数据和销售统计。")
        # TODO: 这里可以嵌入数据看板界面