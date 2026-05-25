#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版测试应用
"""
import streamlit as st
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

# 初始化 Session State
if "agent" not in st.session_state:
    st.session_state.agent = None
if "messages" not in st.session_state:
    st.session_state.messages = []

def main():
    st.title("🛒 电商购物助手测试")
    
    # 初始化Agent
    if st.button("初始化助理 Agent"):
        with st.spinner("正在初始化..."):
            try:
                agent = create_assistant_agent()
                st.session_state.agent = agent
                st.success("✅ 助理 Agent 初始化成功（规则模式）")
            except Exception as e:
                st.error(f"❌ 初始化失败: {str(e)}")
    
    # 显示Agent状态
    if st.session_state.agent:
        st.info("✅ 助理 Agent 已就绪")
        
        # 测试功能
        if st.button("测试欢迎消息"):
            welcome_msg = st.session_state.agent._get_welcome_message()
            st.write(welcome_msg)
        
        if st.button("测试商品查询"):
            response = st.session_state.agent._handle_product_query()
            st.write(response)
        
        # 聊天输入
        user_input = st.text_input("输入测试消息（如：看看商品）")
        if st.button("发送") and user_input:
            response = st.session_state.agent.chat(user_input)
            st.write(f"Agent回复: {response}")
    else:
        st.warning("⚠️ 请先初始化助理 Agent")

if __name__ == "__main__":
    main()
