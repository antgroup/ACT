"""
Streamlit Web UI
电商助手的聊天界面
"""
import streamlit as st
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from assistant_agent.agent import create_assistant_agent

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="电商购物助手",
    page_icon="🛒",
    layout="centered",
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
    .sidebar-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化 Session State"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        st.session_state.agent = None
        st.session_state.agent_mode = "rule"
    
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False


def initialize_agent(mode: str, api_key: str = None, model: str = "gpt-3.5-turbo"):
    """
    初始化助理 Agent
    
    Args:
        mode: Agent 模式 ("rule" 或 "llm")
        api_key: OpenAI API Key（LLM 模式需要）
        model: 模型名称
    """
    try:
        if mode == "rule":
            # 规则模式（不需要 API Key）
            st.session_state.agent = create_assistant_agent()
            st.session_state.agent_mode = "rule"
            st.session_state.agent_initialized = True
            return True, "助理 Agent 初始化成功（规则模式）"
        
        elif mode == "llm":
            if not api_key:
                return False, "请提供 OpenAI API Key"
            
            # LLM 模式
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
        return False, f"初始化失败: {str(e)}"


def main():
    """主函数"""
    # 初始化 Session State
    init_session_state()
    
    # 页面标题
    st.markdown('<div class="main-header">🛒 电商购物助手</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">基于 Agentscope 的 Multi-Agent 系统</div>', unsafe_allow_html=True)
    
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
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # Agent 模式选择
        agent_mode = st.radio(
            "选择 Agent 模式",
            options=["rule", "llm"],
            format_func=lambda x: "规则模式（推荐）" if x == "rule" else "LLM 模式（需要 API Key）",
            help="规则模式使用预定义规则，LLM 模式使用大语言模型"
        )
        
        # LLM 配置（仅在 LLM 模式下显示）
        api_key = None
        model = "gpt-3.5-turbo"
        
        if agent_mode == "llm":
            st.markdown("---")
            st.subheader("🔑 LLM 配置")
            
            # API Key 输入
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=os.getenv("OPENAI_API_KEY", ""),
                help="输入您的 OpenAI API Key"
            )
            
            # 模型选择
            model = st.selectbox(
                "选择模型",
                options=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                help="选择要使用的 OpenAI 模型"
            )
        
        # 初始化按钮
        st.markdown("---")
        if st.button("🚀 初始化助理 Agent", type="primary", use_container_width=True):
            with st.spinner("正在初始化..."):
                success, message = initialize_agent(agent_mode, api_key, model)
                if success:
                    st.success(message)
                    # 清空对话历史
                    st.session_state.messages = []
                    # 添加欢迎消息
                    welcome_msg = st.session_state.agent._get_welcome_message()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": welcome_msg
                    })
                    st.rerun()
                else:
                    st.error(message)
        
        # 重置对话按钮
        if st.button("🔄 重置对话", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.agent:
                st.session_state.agent.reset()
            st.success("对话已重置！")
            st.rerun()
        
        # 显示状态
        st.markdown("---")
        st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
        st.markdown("**📊 系统状态**")
        if st.session_state.agent_initialized:
            st.markdown(f"✅ 助理 Agent 已就绪")
            st.markdown(f"🤖 模式: {st.session_state.agent_mode.upper()}")
            st.markdown(f"💬 消息数: {len(st.session_state.messages)}")
        else:
            st.markdown("⚠️ 助理 Agent 未初始化")
            st.markdown("请点击上方按钮初始化")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 架构说明
        st.markdown("---")
        with st.expander("🏗️ 系统架构"):
            st.markdown("""
            **四个独立模块：**
            
            1. **🖥️ 用户界面 (ui/)**
               - Streamlit Web UI
               - 聊天界面
            
            2. **🤖 助理 Agent (assistant_agent/)**
               - 理解用户意图
               - 协调服务调用
               - 呈现结果
            
            3. **🏪 商户服务 (merchant_service/)**
               - 管理商品库存
               - 处理订单创建
               - 提供订单查询
            
            4. **💳 支付服务 (payment_service/)**
               - 处理支付请求
               - 验证支付金额
               - 更新订单状态
            
            **工作流程：**
            ```
            用户界面 → 助理Agent → 商户服务
                                  ↓
                             支付服务
            ```
            """)
        
        # 使用说明
        st.markdown("---")
        with st.expander("📖 使用说明"):
            st.markdown("""
            **功能介绍：**
            
            1. **查看商品**
               - 说："看看商品" 或 "有什么产品"
               
            2. **购买商品**
               - 说："我要买 P001" 或 "购买 P002 2个"
               
            3. **支付订单**
               - 下单后说："支付" 或 "付款"
               
            4. **查询订单**
               - 说："查询订单 ORD12345678"
            
            **商品列表：**
            - P001: Apple (苹果) - ¥5.99
            - P002: Banana (香蕉) - ¥3.99
            - P003: Orange (橙子) - ¥4.99
            - P004: Grape (葡萄) - ¥8.99
            """)
    
    # 主聊天区域
    st.markdown("---")
    
    # 检查 Agent 是否初始化
    if not st.session_state.agent_initialized:
        st.warning("⚠️ 请先在左侧初始化助理 Agent")
        st.info("💡 提示：选择「规则模式」可以快速开始，无需 API Key")
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
                    
                    # 添加 Agent 响应到历史
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                
                except Exception as e:
                    error_msg = f"❌ 处理消息时出错: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


if __name__ == "__main__":
    main()