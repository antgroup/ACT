"""
模型配置界面模块
提供 UI 上的模型选择和配置功能
"""
import streamlit as st
import os
from typing import Dict, Any, Optional


def get_dashscope_models() -> list:
    """获取支持的 DashScope 模型列表"""
    return [
        ("qwen-turbo", "通义千问 Turbo - 速度快、成本低（推荐）"),
        ("qwen-plus", "通义千问 Plus - 性能均衡"),
        ("qwen-max", "通义千问 Max - 最强能力"),
        ("qwen-long", "通义千问 Long - 长文本专用"),
        ("qwen-coder-plus", "通义千问 Coder - 代码生成"),
        ("qwen-math-plus", "通义千问 Math - 数学推理"),
        ("deepseek-r1", "DeepSeek R1 - 开源推理模型"),
        ("deepseek-v3", "DeepSeek V3 - 开源通用模型"),
    ]


def get_openai_models() -> list:
    """获取支持的 OpenAI 模型列表"""
    return [
        ("gpt-3.5-turbo", "GPT-3.5 Turbo - 性价比高"),
        ("gpt-4", "GPT-4 - 最强能力"),
        ("gpt-4-turbo", "GPT-4 Turbo - 最新版"),
    ]


def init_model_config_state():
    """初始化模型配置状态"""
    if "model_config" not in st.session_state:
        st.session_state.model_config = {
            "provider": "dashscope",  # 默认使用阿里系
            "dashscope_api_key": "",
            "openai_api_key": "",
            "dashscope_model": "qwen-turbo",
            "openai_model": "gpt-3.5-turbo",
            "configured": False,
            "use_llm": False,
        }

    # 从环境变量加载默认配置
    if not st.session_state.model_config.get("configured"):
        # 尝试从环境变量加载
        dashscope_key = os.getenv("DASHSCOPE_API_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        provider = os.getenv("MODEL_PROVIDER", "dashscope")
        dashscope_model = os.getenv("DASHSCOPE_MODEL", "qwen-turbo")
        openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        if dashscope_key:
            st.session_state.model_config["dashscope_api_key"] = dashscope_key
        if openai_key:
            st.session_state.model_config["openai_api_key"] = openai_key

        st.session_state.model_config["provider"] = provider
        st.session_state.model_config["dashscope_model"] = dashscope_model
        st.session_state.model_config["openai_model"] = openai_model


def render_model_config_sidebar():
    """在侧边栏渲染模型配置界面"""
    init_model_config_state()

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🤖 模型配置")

        config = st.session_state.model_config

        # 模型提供商选择
        provider = st.radio(
            "选择模型提供商",
            options=["dashscope", "openai"],
            format_func=lambda x: {
                "dashscope": "🚀 DashScope (阿里云 - 推荐)",
                "openai": "🌐 OpenAI (GPT 系列)"
            }.get(x, x),
            index=0 if config["provider"] == "dashscope" else 1
        )
        config["provider"] = provider

        st.markdown("---")

        # 根据提供商显示不同配置
        if provider == "dashscope":
            _render_dashscope_config(config)
        else:
            _render_openai_config(config)

        st.markdown("---")

        # 配置状态显示
        if config["configured"]:
            st.success(f"✅ 已配置: {config['provider']} - {config.get(f'{provider}_model', '')}")
        else:
            st.info("💡 请输入 API Key 并保存配置")

        return config


def _render_dashscope_config(config: Dict[str, Any]):
    """渲染 DashScope 配置"""
    st.markdown("#### 🔷 DashScope 配置")
    st.caption("[获取 API Key](https://dashscope.console.aliyun.com/api-key)")

    # API Key 输入
    api_key = st.text_input(
        "DashScope API Key",
        value=config["dashscope_api_key"],
        type="password",
        placeholder="sk-xxxx",
        key="dashscope_key_input"
    )
    config["dashscope_api_key"] = api_key

    # 模型选择
    models = get_dashscope_models()
    model_display_map = {k: v for k, v in models}
    current_model = config["dashscope_model"]

    selected_model = st.selectbox(
        "选择模型",
        options=[m[0] for m in models],
        format_func=lambda x: model_display_map.get(x, x),
        index=[m[0] for m in models].index(current_model) if current_model in [m[0] for m in models] else 0
    )
    config["dashscope_model"] = selected_model

    # 显示选中模型的详细信息
    model_info = {
        "qwen-turbo": {
            "desc": "速度快、成本低，适合大多数日常对话场景",
            "best_for": "日常问答、简单任务",
            "speed": "⚡⚡⚡⚡⚡",
            "cost": "💰"
        },
        "qwen-plus": {
            "desc": "性能均衡，在保持较好速度的同时提供优质回复",
            "best_for": "综合任务",
            "speed": "⚡⚡⚡⚡",
            "cost": "💰💰"
        },
        "qwen-max": {
            "desc": "最强能力版，适合复杂推理和多步骤任务",
            "best_for": "复杂推理、创意任务",
            "speed": "⚡⚡⚡",
            "cost": "💰💰💰"
        },
        "qwen-long": {
            "desc": "支持长文本，可处理百万级 token 的长文档",
            "best_for": "长文档分析",
            "speed": "⚡⚡⚡",
            "cost": "💰💰"
        },
        "qwen-coder-plus": {
            "desc": "专为代码生成和编程任务优化",
            "best_for": "编程、代码解释",
            "speed": "⚡⚡⚡⚡",
            "cost": "💰💰"
        },
        "qwen-math-plus": {
            "desc": "数学和逻辑推理专用，解决复杂数学问题",
            "best_for": "数学计算、逻辑推理",
            "speed": "⚡⚡⚡",
            "cost": "💰💰"
        },
        "deepseek-r1": {
            "desc": "开源推理模型，逻辑能力强，适合复杂分析",
            "best_for": "深度推理、分析任务",
            "speed": "⚡⚡⚡",
            "cost": "💰"
        },
        "deepseek-v3": {
            "desc": "开源通用模型，性价比极高",
            "best_for": "综合任务",
            "speed": "⚡⚡⚡⚡",
            "cost": "💰"
        },
    }

    if selected_model in model_info:
        info = model_info[selected_model]
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 8px; font-size: 0.9em;">
            <strong>💡 特点</strong>：{info['desc']}<br>
            <strong>🎯 适用</strong>：{info['best_for']}<br>
            <strong>⚡ 速度</strong>：{info['speed']} <strong>💰 成本</strong>：{info['cost']}
        </div>
        """, unsafe_allow_html=True)

    # 保存配置按钮
    if st.button("💾 保存 DashScope 配置", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ 请输入 API Key")
        else:
            config["configured"] = True
            config["use_llm"] = True
            st.success("✅ 配置已保存")
            st.rerun()


def _render_openai_config(config: Dict[str, Any]):
    """渲染 OpenAI 配置"""
    st.markdown("#### 🌐 OpenAI 配置")
    st.caption("[获取 API Key](https://platform.openai.com/api-keys)")

    # API Key 输入
    api_key = st.text_input(
        "OpenAI API Key",
        value=config["openai_api_key"],
        type="password",
        placeholder="sk-xxxx",
        key="openai_key_input"
    )
    config["openai_api_key"] = api_key

    # 自定义 Base URL（可选）
    custom_base_url = st.text_input(
        "自定义 API 地址（可选）",
        value=config.get("openai_base_url", ""),
        placeholder="https://api.openai.com/v1（默认）",
        key="openai_base_input"
    )
    config["openai_base_url"] = custom_base_url if custom_base_url else None

    # 模型选择
    models = get_openai_models()
    model_display_map = {k: v for k, v in models}
    current_model = config["openai_model"]

    selected_model = st.selectbox(
        "选择模型",
        options=[m[0] for m in models],
        format_func=lambda x: model_display_map.get(x, x),
        index=[m[0] for m in models].index(current_model) if current_model in [m[0] for m in models] else 0
    )
    config["openai_model"] = selected_model

    # 显示选中模型的详细信息
    model_info = {
        "gpt-3.5-turbo": {
            "desc": "性价比高，响应速度快",
            "best_for": "日常对话、简单任务",
            "speed": "⚡⚡⚡⚡⚡",
            "cost": "💰"
        },
        "gpt-4": {
            "desc": "最强能力，适合复杂任务",
            "best_for": "复杂推理、创作任务",
            "speed": "⚡⚡⚡",
            "cost": "💰💰💰"
        },
        "gpt-4-turbo": {
            "desc": "最新的 GPT-4 版本，能力和速度平衡",
            "best_for": "综合任务",
            "speed": "⚡⚡⚡⚡",
            "cost": "💰💰"
        },
    }

    if selected_model in model_info:
        info = model_info[selected_model]
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 8px; font-size: 0.9em;">
            <strong>💡 特点</strong>：{info['desc']}<br>
            <strong>🎯 适用</strong>：{info['best_for']}<br>
            <strong>⚡ 速度</strong>：{info['speed']} <strong>💰 成本</strong>：{info['cost']}
        </div>
        """, unsafe_allow_html=True)

    # 保存配置按钮
    if st.button("💾 保存 OpenAI 配置", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ 请输入 API Key")
        else:
            config["configured"] = True
            config["use_llm"] = True
            st.success("✅ 配置已保存")
            st.rerun()


def get_current_model_config() -> Optional[Dict[str, Any]]:
    """获取当前模型配置（用于初始化 Agent）"""
    init_model_config_state()
    config = st.session_state.model_config

    if not config.get("configured"):
        return None

    provider = config["provider"]

    if provider == "dashscope":
        return {
            "provider": "dashscope",
            "api_key": config["dashscope_api_key"],
            "model": config["dashscope_model"],
            "base_url": None,  # DashScope 使用默认地址
        }
    else:
        return {
            "provider": "openai",
            "api_key": config["openai_api_key"],
            "model": config["openai_model"],
            "base_url": config.get("openai_base_url"),
        }


def test_model_connection(provider: str, api_key: str, model: str, base_url: str = None) -> tuple:
    """
    测试模型连接是否成功

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if provider == "dashscope":
            import dashscope
            dashscope.api_key = api_key

            # 简单测试调用
            response = dashscope.Generation.call(
                model=model,
                messages=[{"role": "user", "content": "你好"}],
                max_tokens=10
            )

            if response.status_code == 200:
                return True, "连接成功"
            else:
                return False, f"API 错误: {response.message}"

        else:  # openai
            import openai
            client = openai.OpenAI(api_key=api_key, base_url=base_url)

            # 简单测试调用
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "你好"}],
                max_tokens=10
            )

            return True, "连接成功"

    except Exception as e:
        return False, f"连接失败: {str(e)}"


def render_model_test_button():
    """渲染测试连接按钮"""
    config = get_current_model_config()
    if not config:
        return

    if st.sidebar.button("🧪 测试连接", use_container_width=True):
        with st.spinner("正在测试连接..."):
            success, message = test_model_connection(
                config["provider"],
                config["api_key"],
                config["model"],
                config.get("base_url")
            )

            if success:
                st.sidebar.success(f"✅ {message}")
            else:
                st.sidebar.error(f"❌ {message}")
