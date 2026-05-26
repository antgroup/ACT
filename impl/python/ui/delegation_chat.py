"""
委托支付对话界面
提供完整的 AI 对话交互体验
"""
import streamlit as st
from typing import Dict, Any
from datetime import datetime

from assistant_agent.delegated_payment_agent import DelegatedPaymentAgent


def render_delegation_chat_tab():
    """渲染委托支付对话标签页"""

    st.markdown('<div class="main-header">💼 委托支付智能助理</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">自然语言交互式委托支付体验</div>', unsafe_allow_html=True)

    # 初始化
    if "delegation_agent" not in st.session_state:
        st.session_state.delegation_agent = DelegatedPaymentAgent()
        st.session_state.messages = []
        st.session_state.delegation_status = None

    # 记录内容显示区域
    left_col, right_col = st.columns([2, 1])

    with left_col:
        # 对话历史记录显示 - 使用滚动容器
        st.markdown("### 💬 对话记录")

        # 创建一个可滚动的消息容器
        with st.container():
            if st.session_state.messages:
                for message in st.session_state.messages:
                    role = message["role"]
                    content = message["content"]

                    if role == "user":
                        with st.chat_message("user"):
                            st.markdown(content)
                    else:
                        with st.chat_message("assistant"):
                            st.markdown(content)
            else:
                # 初始欢迎消息
                welcome = st.session_state.delegation_agent._get_welcome_message()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": welcome
                })

                with st.chat_message("assistant"):
                    st.markdown(welcome)

            # 始终自动滚动到底部 - 在消息列表末尾添加占位符
            st.markdown("<div id='chat-bottom' style='margin-top: -50px;'></div>", unsafe_allow_html=True)

            # 用户输入框
            if prompt := st.chat_input("请输入您的需求，例如：帮我买《人工智能》这本书..."):
                # 处理用户消息
                with st.chat_message("user"):
                    st.markdown(prompt)

                # 添加用户消息到历史
                st.session_state.messages.append({
                    "role": "user",
                    "content": prompt
                })

                # 获取智能体回复
                with st.chat_message("assistant"):
                    with st.spinner("智能助理正在思考..."):
                        try:
                            response = st.session_state.delegation_agent.process_user_message(prompt)

                            # 解析响应中的关键信息
                            if "**委托支付参数**" in response:
                                st.session_state.delegation_status = "negotiating"
                            elif "**委托协议签发成功**" in response:
                                st.session_state.delegation_status = "iaissued"
                            elif "**支付成功**" in response:
                                st.session_state.delegation_status = "paid"

                            formatted_response = format_response(response)
                            st.markdown(formatted_response)

                            # 添加助手回复到历史
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response
                            })
                        except Exception as e:
                            error_msg = f"❌ 处理消息时出错：{str(e)}"
                            st.error(error_msg)

                # 再次添加底部占位符以触发滚动
                st.markdown("<div id='chat-bottom' style='margin-top: -50px; margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    with right_col:
        # 委托状态面板
        render_delegation_status_panel()

        # 快捷指令面板
        render_quick_actions()


def format_response(response: str) -> str:
    """格式化智能体响应"""

    # 基本的 Markdown 格式化
    formatted = response

    # 添加代码块样式处理
    lines = formatted.split('\n')
    formatted_lines = []

    in_code_block = False
    code_buffer = []

    for line in lines:
        # 检测代码行
        if line.startswith('- ') or line.startswith('   -') or line.startswith('   '):
            formatted_lines.append(line)
        else:
            formatted_lines.append(line)

    return '\n'.join(formatted_lines)


def render_delegation_status_panel():
    """渲染委托状态面板（右侧）"""

    agent = st.session_state.delegation_agent
    context = agent.delegation_context

    st.markdown("### 📊 委托状态")

    if not context.get("iac"):
        st.info("💡 暂无活动委托，请开始您的咨询")
        return

    # 委托基本状态
    st.markdown("""
    **委托协议已生效**
    """)
    st.markdown("---")

    # 基本信息
    st.markdown("**基本信息**")
    st.markdown(f"""
    - **委托 ID**: `{context.get('delegation_id', '')[:30]}...`
    - **委托人**: {agent.user_profile['principal_id']}
    - **智能体**: {agent.user_profile['agent_id']}
    - **模式**: {context.get('scenario', '专属型')}
    """)

    st.markdown("---")

    # 额度信息
    st.markdown("**额度信息**")

    # 获取累计支付金额
    cumulative = 0.0
    if context.get("active_delegation_id"):
        try:
            cumulative = agent.delegation_handler.payment_service.get_cumulative_amount(
                context["active_delegation_id"]
            )
        except:
            pass

    total = context.get("max_total_amount", 0)
    remaining = total - cumulative

    # 进度条
    progress = cumulative / total if total > 0 else 0
    st.progress(min(progress, 1.0))

    st.metric(
        label="已用额度",
        value=f"¥{cumulative:.2f}",
        help="已在该委托下支付的金额"
    )

    st.metric(
        label="剩余额度",
        value=f"¥{remaining:.2f}",
        help="还可支付的金额"
    )

    st.markdown("---")

    # 授权约束
    st.markdown("**授权约束**")
    st.markdown(f"""
    - **总金额上限**: ¥{total:.2f}
    - **单笔上限**: ¥{context.get('max_single_amount', 0):.2f}
    - **委托目的**: {context.get('delegation_purpose', '未指定')[:50]}...
    """)

    st.markdown("---")

    # IAC 展示（折叠）
    with st.expander("📜 查看完整 IAC 凭证"):
        st.success(f"有效期：至 {(datetime.fromisoformat(context.get('validity_end', datetime.now().isoformat())))}")
        st.json({
            "type": "vc+jwt",
            "jti": context.get("delegation_id"),
            "iss": agent.user_profile["principal_id"],
            "sub": agent.user_profile["agent_id"]
        })


def render_quick_actions():
    """渲染快捷操作按钮"""

    st.markdown("---")
    st.markdown("**快捷操作**")

    agent = st.session_state.delegation_agent

    # 开始新征程 - 重置会话
    if st.button("🆕 开始新征程", key="quick_new_start", use_container_width=True):
        # 重置会话状态
        st.session_state.delegation_agent = DelegatedPaymentAgent()
        st.session_state.messages = []
        st.session_state.delegation_status = None
        st.success("已重置会话！")
        st.rerun()

    st.markdown("---")
    st.markdown("### 🎯 快速指令")

    # 默认商品列表
    default_products = [
        ("🎧 无线耳机", "帮我买商品 1（无线耳机）"),
        ("⌨️ 机械键盘", "帮我买商品 2（机械键盘）"),
    ]

    for btn_text, cmd in default_products:
        if st.button(btn_text, key=btn_text.replace(" ", "_").lower(), use_container_width=True):
            response = agent.process_user_message(cmd)
            # 添加用户消息到历史
            st.session_state.messages.append({"role": "user", "content": cmd})
            # 添加助手回复到历史
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.success("指令已发送！")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🔍 市场功能")

    market_commands = [
        ("📦 查看商品列表", "查看商品列表"),
        ("🎯 推荐商品", "推荐商品"),
        ("⚠️ 检查低库存", "检查低库存"),
    ]

    for btn_text, cmd in market_commands:
        if st.button(btn_text, key=btn_text.replace(" ", "_").lower(), use_container_width=True):
            response = agent.process_user_message(cmd)
            st.session_state.messages.append({"role": "user", "content": cmd})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.success("指令已发送！")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📦 商品列表")

    # 商品列表按钮
    if st.button("📦 查看商品列表", key="quick_list", use_container_width=True):
        response = agent.process_user_message("商品列表")
        st.session_state.messages.append({"role": "user", "content": "商品列表"})
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.success("指令已发送！")
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ 委托管理")

    # 重置会话（取消委托）
    if st.button("🚫 取消委托", key="quick_cancel", use_container_width=True):
        st.session_state.delegation_agent = DelegatedPaymentAgent()
        st.session_state.messages = []
        st.session_state.delegation_status = None
        st.warning("会话已重置！")
        st.rerun()
