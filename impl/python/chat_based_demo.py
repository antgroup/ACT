"""
ACT 协议 - GPT对话式支付演示
Chat-based Demo for ACT Protocol Payment Methods

核心设计理念：
1. 所有交互通过自然语言对话完成
2. 智能体根据用户意图自动判断使用哪种支付模式
3. 三种支付模式的流程和差异通过对话清晰展示
4. 用户和商户角色切换时，商品和订单数据保持同步
5. 支持LLM模型意图识别（可选）和规则基础识别（回退）
"""

import streamlit as st
import json
import os
import time
import uuid
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

# 数据持久化 - 使用JSON文件存储，确保用户和商户数据同步
DATA_FILE = os.path.join(os.path.dirname(__file__), "demo_data.json")


# ==================== LLM 模型接口 ====================

class RealLLMClient:
    """
    真实 LLM 客户端 - 调用实际 API (DashScope/OpenAI)
    支持真实的意图识别和自然语言理解
    """

    SYSTEM_PROMPT = """你是ACT协议智能支付助手，负责理解用户的支付意图。

ACT协议支持三种支付模式：
1. **即时支付 (instant_payment)** - 用户实时在场确认购买，如"买iPhone"
2. **委托支付 (delegated_payment)** - 预先授权智能体代为支付，如"授权每月买咖啡，额度500元"
3. **自主支付/A2A支付 (autonomous_payment)** - 复杂任务让智能体自主决策，如"帮我安排出差，预算5000元"

请分析用户消息，返回JSON格式：
{
  "intent": "意图类型(instant_payment/delegated_payment/autonomous_payment/cancel_delegation/help/view_products/view_orders/view_delegations/default)",
  "confidence": 置信度(0-1),
  "entities": {
    "amount": 提取的金额数字,
    "product_name": "商品名称",
    "time_pattern": "时间模式"
  },
  "response": "对用户的回复建议"
}

只返回JSON，不要其他文字。"""

    # 类属性：标记这是真实LLM客户端
    is_mock = False

    def __init__(self, provider: str, api_key: str, model: str, temperature: float = 0.7, base_url: str = None):
        self.provider = provider  # "dashscope" or "openai"
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.base_url = base_url

    def identify_intent(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """使用真实LLM识别意图"""
        try:
            if self.provider == "dashscope":
                return self._identify_with_dashscope(message)
            elif self.provider == "openai":
                return self._identify_with_openai(message)
            else:
                # 未知provider，回退到mock
                return self._fallback_to_mock(message)
        except Exception as e:
            st.error(f"LLM API调用失败: {str(e)}")
            return self._fallback_to_mock(message)

    def _identify_with_dashscope(self, message: str) -> Dict[str, Any]:
        """使用 DashScope API"""
        import dashscope
        dashscope.api_key = self.api_key

        response = dashscope.Generation.call(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            temperature=self.temperature,
            result_format="message"
        )

        if response.status_code == 200:
            content = response.output.choices[0].message.content
            return self._parse_llm_response(content)
        else:
            raise Exception(f"DashScope error: {response.message}")

    def _identify_with_openai(self, message: str) -> Dict[str, Any]:
        """使用 OpenAI API"""
        import openai
        client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            temperature=self.temperature
        )

        content = response.choices[0].message.content
        return self._parse_llm_response(content)

    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """解析LLM返回的JSON"""
        # 尝试从响应中提取JSON
        import json
        import re

        # 移除markdown代码块标记
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        content = content.strip()

        try:
            result = json.loads(content)
            # 确保返回格式正确
            return {
                "intent": result.get("intent", "default"),
                "confidence": result.get("confidence", 0.5),
                "entities": result.get("entities", {}),
                "response": result.get("response", ""),
            }
        except json.JSONDecodeError:
            # JSON解析失败，回退到mock
            return self._fallback_to_mock(content)

    def _fallback_to_mock(self, message: str) -> Dict[str, Any]:
        """回退到mock识别"""
        mock_client = MockLLMClient()
        return mock_client.identify_intent(message)

    def chat_completion(self, messages: List[Dict], **kwargs) -> str:
        """聊天补全接口"""
        try:
            if self.provider == "dashscope":
                import dashscope
                dashscope.api_key = self.api_key
                response = dashscope.Generation.call(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    result_format="message"
                )
                if response.status_code == 200:
                    return response.output.choices[0].message.content
                else:
                    raise Exception(response.message)
            elif self.provider == "openai":
                import openai
                client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"[LLM错误: {str(e)}]"


class MockLLMClient:
    """
    Mock LLM 客户端 - 模拟LLM响应，无需真实API Key
    用于演示和测试，支持意图识别和智能回复
    """

    is_mock = True  # 标记为 Mock 客户端

    # 意图识别关键词库
    INTENT_PATTERNS = {
        "instant_payment": [
            r"买\s*(.+?)",
            r"购买\s*(.+?)",
            r"现在买\s*(.+?)",
            r"立即[购买]\s*(.+?)",
            r"下单\s*(.+?)",
            r"支付\s*(.+?)",
            r"结算\s*(.+?)",
            r"[我|帮][要|我]?[买|订].*",
        ],
        "delegated_payment": [
            r"授权.*",
            r"委托.*",
            r"自动续费.*",
            r"每月帮[我]?.*",
            r"定期帮[我]?.*",
            r"设置[iac|委托].*",
            r"开通委托.*",
            r"[预]?授权.*",
        ],
        "autonomous_payment": [
            r"帮[我]?安排.*",
            r"帮[我]?规划.*",
            r"帮[我]?预订.*",
            r"出差.*",
            r"旅游.*",
            r"旅行.*",
            r"整体方案.*",
            r"行程.*",
            r"[制定|安排].*计划.*",
        ],
        "help": [
            r"帮助.*",
            r"help.*",
            r"怎么用.*",
            r"说明.*",
            r"[做什么|能干啥].*",
        ],
        "view_products": [
            r"商品.*",
            r"有[什么|啥].*",
            r"[看|瞅].*商品.*",
            r"[有什么|卖什么|有哪些].*",
        ],
        "view_orders": [
            r"订单.*",
            r"[我的]?购买[记录|历史].*",
            r"[看|查].*订单.*",
        ],
        "view_delegations": [
            r"委托[状态|情况]?.*",
            r"iac[状态]?.*",
            r"授权[状态]?.*",
            r"额度.*",
            r"剩余.*",
        ],
    }

    def __init__(self, model_name: str = "mock-qwen-turbo", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.is_mock = True

    def identify_intent(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """
        使用模式匹配识别用户意图
        模拟LLM意图识别 - 无需真实API调用

        Returns: {
            "intent": str,  # 主要意图
            "confidence": float,  # 置信度 0-1
            "entities": Dict,  # 提取的实体
            "response": str,  # 可能的回复建议
        }
        """
        message = message.strip()
        msg_lower = message.lower()

        # 提取实体
        entities = self._extract_entities(message)

        # 计算各意图的匹配分数
        intent_scores = {}

        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, msg_lower, re.IGNORECASE):
                    score += 1.0
                    # 完全匹配更高分
                    if re.match(pattern, msg_lower, re.IGNORECASE):
                        score += 0.5
            intent_scores[intent] = min(score, 2.0)  # 最高2分

        # 选择最高分的意图
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            best_score = intent_scores[best_intent]
        else:
            best_intent = "default"
            best_score = 0.0

        # 转换为置信度 (0-1)
        confidence = min(best_score / 2.0, 1.0)

        # 根据置信度生成回复建议
        response = self._generate_suggested_response(best_intent, entities, confidence)

        return {
            "intent": best_intent,
            "confidence": confidence,
            "entities": entities,
            "response": response,
            "all_scores": intent_scores,
        }

    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """提取实体：金额、商品、额度等"""
        entities = {}

        # 提取金额 ¥xxx 或 xxx元/块
        amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:元|块|¥|￥)', message)
        if amount_match:
            entities['amount'] = float(amount_match.group(1))

        # 提取商品名称
        product_patterns = [
            r'[买购买订].*?([\w\s\-]+?)(?:\s|$|，|。)',
            r'(?:iPhone|MacBook|AirPods|星巴克|奈雪)',
        ]
        for pattern in product_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                entities['product_name'] = match.group(1).strip() if match.groups() else match.group(0)
                break

        # 提取时间相关
        time_patterns = [
            r'(每周|每月|每天|定期)',
            r'(\d+)天',
            r'(\d+)月',
        ]
        for pattern in time_patterns:
            match = re.search(pattern, message)
            if match:
                entities['time_pattern'] = match.group(1) if match.groups() else match.group(0)
                break

        return entities

    def _generate_suggested_response(self, intent: str, entities: Dict, confidence: float) -> str:
        """根据意图生成建议回复"""
        if confidence < 0.3:
            return "抱歉，我不太明白您的意思。请输入「帮助」查看说明。"

        responses = {
            "instant_payment": "我识别到您的即时支付意图，准备为您处理购买。",
            "delegated_payment": "我识别到您的委托授权意图，准备为您设置IAC凭证。",
            "autonomous_payment": "我识别到您的复杂任务委托意图，准备为您创建A2A任务。",
            "help": "让我为您介绍ACT协议的三种支付模式...",
            "view_products": "为您显示当前可购买的商品列表。",
            "view_orders": "为您查询订单记录。",
            "view_delegations": "为您查询委托授权状态。",
            "default": "有什么可以帮您的吗？",
        }
        return responses.get(intent, responses["default"])

    def generate_response(self, message: str, context: Dict = None) -> str:
        """生成智能回复"""
        intent_result = self.identify_intent(message, context)
        return intent_result["response"]

    def chat_completion(self, messages: List[Dict], **kwargs) -> str:
        """模拟聊天补全接口"""
        if messages:
            last_message = messages[-1].get("content", "")
            return self.generate_response(last_message)
        return "您好！有什么可以帮您的？"


# ==================== 模型配置管理 ====================

def init_model_config():
    """初始化模型配置到 session state"""
    if "model_config" not in st.session_state:
        st.session_state.model_config = {
            "use_llm": False,  # 是否启用LLM
            "provider": "mock",  # mock, dashscope, openai
            "model": "mock-qwen-turbo",  # 模型名称
            "api_key": "",  # API Key
            "base_url": "",  # 自定义API地址（仅OpenAI）
            "temperature": 0.7,
            "configured": False,
        }

    # 从环境变量加载配置
    # 注意：只有在当前provider匹配时才加载对应的环境变量
    provider = st.session_state.model_config.get("provider", "mock")
    if provider == "dashscope" and os.getenv("DASHSCOPE_API_KEY"):
        st.session_state.model_config["api_key"] = os.getenv("DASHSCOPE_API_KEY")
    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        st.session_state.model_config["api_key"] = os.getenv("OPENAI_API_KEY")

    if "llm_client" not in st.session_state:
        st.session_state.llm_client = None


def get_llm_client(config: Dict = None):
    """获取LLM客户端实例 - 支持真实API和Mock"""
    if config is None:
        config = st.session_state.get("model_config", {})

    if not config.get("use_llm", False):
        return None

    provider = config.get("provider", "mock")

    # Mock 模式
    if provider == "mock":
        return MockLLMClient(model_name=config.get("model", "mock-qwen-turbo"))

    # 真实 API 模式
    api_key = config.get("api_key", "")
    if not api_key:
        st.warning(f"⚠️ 已选择 {provider} 但未提供 API Key，将回退到 Mock 模式")
        return MockLLMClient(model_name="mock-fallback")

    # 创建真实LLM客户端
    return RealLLMClient(
        provider=provider,
        api_key=api_key,
        model=config.get("model", "qwen-turbo"),
        temperature=config.get("temperature", 0.7),
        base_url=config.get("base_url", None)
    )


def render_llm_config_sidebar():
    """在侧边栏渲染LLM配置 - 支持真实API"""
    init_model_config()
    config = st.session_state.model_config

    st.markdown("---")
    st.markdown("### 🤖 智能模型配置")

    # 模式选择
    use_llm = st.toggle(
        "启用智能模型",
        value=config.get("use_llm", False),
        help="开启后使用AI模型进行意图识别，关闭则使用规则匹配"
    )
    config["use_llm"] = use_llm

    if use_llm:
        st.info("✅ 智能模型已启用")

        # 提供商选择
        provider = st.radio(
            "选择模型提供商",
            options=["mock", "dashscope", "openai"],
            format_func=lambda x: {
                "mock": "🧪 Mock模式 (本地模拟，无需API Key)",
                "dashscope": "🚀 DashScope (阿里云 - 通义千问)",
                "openai": "🌐 OpenAI (GPT系列)"
            }.get(x, x),
            index=["mock", "dashscope", "openai"].index(config.get("provider", "mock"))
        )
        config["provider"] = provider

        # 根据提供商显示不同配置
        if provider == "mock":
            # Mock 模式配置
            model_options = [
                ("mock-qwen-turbo", "Mock通义千问 Turbo"),
                ("mock-gpt-3.5", "Mock GPT-3.5"),
            ]
            selected_model = st.selectbox(
                "选择模型",
                options=[m[0] for m in model_options],
                format_func=lambda x: dict(model_options).get(x, x),
                index=0
            )
            config["model"] = selected_model
            st.caption("💡 Mock模式使用本地规则模拟LLM，无需API Key")

        elif provider == "dashscope":
            # DashScope 配置
            dashscope_models = [
                ("qwen-turbo", "通义千问 Turbo - 速度快、成本低"),
                ("qwen-plus", "通义千问 Plus - 性能均衡"),
                ("qwen-max", "通义千问 Max - 最强能力"),
                ("qwen-long", "通义千问 Long - 长文本"),
                ("deepseek-r1", "DeepSeek R1 - 开源推理模型"),
                ("deepseek-v3", "DeepSeek V3 - 开源通用模型"),
            ]
            selected_model = st.selectbox(
                "选择模型",
                options=[m[0] for m in dashscope_models],
                format_func=lambda x: dict(dashscope_models).get(x, x),
                index=0
            )
            config["model"] = selected_model

            # API Key 输入
            api_key = st.text_input(
                "DashScope API Key",
                value=config.get("api_key", ""),
                type="password",
                placeholder="sk-xxxxxxxx",
                help="从 https://dashscope.console.aliyun.com/api-key 获取"
            )
            config["api_key"] = api_key

            # 从环境变量加载
            env_key = os.getenv("DASHSCOPE_API_KEY", "")
            if env_key and not api_key:
                st.info("✅ 已从环境变量加载 DASHSCOPE_API_KEY")
                config["api_key"] = env_key

        elif provider == "openai":
            # OpenAI 配置
            openai_models = [
                ("gpt-3.5-turbo", "GPT-3.5 Turbo - 性价比高"),
                ("gpt-4", "GPT-4 - 最强能力"),
                ("gpt-4-turbo", "GPT-4 Turbo - 最新版"),
            ]
            selected_model = st.selectbox(
                "选择模型",
                options=[m[0] for m in openai_models],
                format_func=lambda x: dict(openai_models).get(x, x),
                index=0
            )
            config["model"] = selected_model

            # API Key 输入
            api_key = st.text_input(
                "OpenAI API Key",
                value=config.get("api_key", ""),
                type="password",
                placeholder="sk-xxxxxxxx",
                help="从 https://platform.openai.com/api-keys 获取"
            )
            config["api_key"] = api_key

            # 从环境变量加载
            env_key = os.getenv("OPENAI_API_KEY", "")
            if env_key and not api_key:
                st.info("✅ 已从环境变量加载 OPENAI_API_KEY")
                config["api_key"] = env_key

            # 可选的 Base URL
            base_url = st.text_input(
                "自定义 API 地址（可选）",
                value=config.get("base_url", ""),
                placeholder="https://api.openai.com/v1",
                help="使用代理或第三方服务时填写"
            )
            config["base_url"] = base_url if base_url else None

        # 温度设置
        st.markdown("---")
        temperature = st.slider(
            "创造力/随机性 (Temperature)",
            min_value=0.0,
            max_value=1.0,
            value=config.get("temperature", 0.7),
            step=0.1,
            help="值越低回答越确定，越高越有创造性"
        )
        config["temperature"] = temperature

        # 测试连接按钮（仅真实API模式）
        if provider != "mock":
            if st.button("🧪 测试连接", use_container_width=True):
                with st.spinner("正在测试..."):
                    success, msg = test_llm_connection(config)
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

        # 显示模型能力
        st.markdown("**模型能力：**")
        st.markdown("""
        - ✅ 意图识别（即时/委托/A2A支付）
        - ✅ 实体提取（金额、商品、时间）
        - ✅ 智能回复建议
        - ✅ 上下文理解
        """)

        # 调试开关
        st.markdown("---")
        show_debug = st.checkbox(
            "🔍 显示LLM调试信息",
            value=st.session_state.get("show_llm_debug", False),
            help="在侧边栏显示意图识别详情"
        )
        st.session_state.show_llm_debug = show_debug

    else:
        st.warning("⚠️ 使用规则模式：基于关键词匹配意图")

    # 保存配置
    config["configured"] = True

    # 显示当前配置摘要
    st.markdown("---")
    st.markdown("**当前配置：**")
    if use_llm:
        provider_display = "🧪 Mock" if provider == "mock" else ("🚀 DashScope" if provider == "dashscope" else "🌐 OpenAI")
        st.write(f"- 提供商: {provider_display}")
        st.write(f"- 模型: {config.get('model', 'N/A')}")
        if provider != "mock":
            api_key_status = "✅ 已设置" if config.get("api_key") else "❌ 未设置"
            st.write(f"- API Key: {api_key_status}")
    else:
        st.write("- 模式: ⚙️ 规则匹配")

    # 提示需要重新创建Agent
    agent = st.session_state.get("agent")
    if agent and use_llm and provider != "mock":
        client_is_mock = getattr(agent.llm_client, 'is_mock', True) if agent.llm_client else True
        if client_is_mock:
            st.warning("⚠️ 配置已更新但Agent仍使用Mock模式")

    # 应用配置按钮
    if agent and st.button("🔄 应用配置到当前会话", use_container_width=True, type="primary"):
        # 重新创建Agent
        st.session_state.agent = create_agent_with_llm(
            st.session_state.user_id,
            st.session_state.current_role
        )
        st.success("✅ 配置已应用")
        st.rerun()

    return config


def test_llm_connection(config: Dict) -> Tuple[bool, str]:
    """测试LLM连接是否成功"""
    try:
        provider = config.get("provider")
        api_key = config.get("api_key", "")
        model = config.get("model", "")
        base_url = config.get("base_url")

        if not api_key:
            return False, "请先输入 API Key"

        if provider == "dashscope":
            import dashscope
            dashscope.api_key = api_key
            response = dashscope.Generation.call(
                model=model,
                messages=[{"role": "user", "content": "你好"}],
                max_tokens=10,
                result_format="message"
            )
            if response.status_code == 200:
                return True, "连接成功"
            else:
                return False, f"API错误: {response.message}"

        elif provider == "openai":
            import openai
            client = openai.OpenAI(api_key=api_key, base_url=base_url)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "你好"}],
                max_tokens=10
            )
            return True, "连接成功"

        return False, "未知的提供商"

    except Exception as e:
        return False, f"连接失败: {str(e)}"


def load_demo_data() -> Dict[str, Any]:
    """加载演示数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "products": [
            {"id": "p1", "name": "iPhone 15 Pro", "price": 8999.0, "stock": 10, "merchant_id": "m1"},
            {"id": "p2", "name": "MacBook Pro M3", "price": 14999.0, "stock": 5, "merchant_id": "m1"},
            {"id": "p3", "name": "AirPods Pro 2", "price": 1899.0, "stock": 20, "merchant_id": "m1"},
            {"id": "p4", "name": "星巴克大杯拿铁", "price": 38.0, "stock": 100, "merchant_id": "m2"},
            {"id": "p5", "name": "奈雪的茶", "price": 32.0, "stock": 50, "merchant_id": "m2"},
        ],
        "orders": [],
        "delegations": [],
        "sub_accounts": {},
        "notifications": []
    }


def save_demo_data(data: Dict[str, Any]):
    """保存演示数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%H:%M:%S")
        if self.metadata is None:
            self.metadata = {}


class ACTChatAgent:
    """
    ACT协议智能对话Agent
    支持三种支付模式的识别和执行
    支持LLM模型意图识别（可选）和规则基础识别（回退）
    """

    def __init__(self, user_id: str, role: str, llm_client: Optional[MockLLMClient] = None):
        self.user_id = user_id
        self.role = role  # "user" 或 "merchant"
        self.data = load_demo_data()
        self.current_mode = None  # 当前支付模式
        self.pending_action = None  # 待确认的操作
        self.llm_client = llm_client  # LLM客户端（可选）
        self.use_llm = llm_client is not None  # 是否启用LLM

    def _identify_intent_with_llm(self, message: str) -> Tuple[str, float, Dict]:
        """
        使用LLM识别意图
        Returns: (intent, confidence, entities)
        """
        if not self.llm_client:
            return "unknown", 0.0, {}

        result = self.llm_client.identify_intent(message, {
            "user_id": self.user_id,
            "role": self.role,
            "pending_action": self.pending_action,
        })

        return result["intent"], result["confidence"], result.get("entities", {})

    def _identify_intent_rule_based(self, message: str) -> Tuple[str, Dict]:
        """
        基于规则的意图识别
        Returns: (intent, context)
        """
        msg_lower = message.lower().strip()

        # 帮助指令
        if any(kw in msg_lower for kw in ["帮助", "help", "怎么用", "说明"]):
            return "help", {}

        # 商户相关指令
        if self.role == "merchant":
            return "merchant_command", {"message": message}

        # 使用委托购买 - 特殊处理
        if "使用委托" in message or "用委托" in message:
            return "delegated_payment_execute", {"message": message}

        # 取消/吊销委托
        if any(kw in msg_lower for kw in ["取消委托", "吊销委托", "撤销委托", "终止委托", "关闭委托", "停用委托", "删除委托"]):
            return "cancel_delegation", {"message": message}

        # 自主支付 (A2A) - 复杂任务委托
        if any(kw in msg_lower for kw in ["帮我安排", "帮我规划", "帮我预订", "出差", "旅游", "整体方案"]):
            return "autonomous_payment", {"message": message}

        # 委托支付 - 定向授权（预先授权，后续自动执行）
        if any(kw in msg_lower for kw in ["授权", "委托", "自动续费", "每月帮我", "定期帮我", "设置iac", "开通委托"]):
            return "delegated_payment", {"message": message}

        # 即时支付 - 立即购买（用户实时在场）
        if any(kw in msg_lower for kw in ["买", "购买", "现在买", "立即买", "下单", "支付", "结算"]):
            return "instant_payment", {"message": message}

        # 查询类指令
        if any(kw in msg_lower for kw in ["订单", "我的订单", "购买记录"]):
            return "view_orders", {}

        if any(kw in msg_lower for kw in ["商品", "有什么", "列表", "看看商品"]):
            return "view_products", {}

        if any(kw in msg_lower for kw in ["委托状态", "iac状态", "授权状态", "额度"]):
            return "view_delegations", {}

        # 默认对话
        return "default_chat", {"message": message}

    def get_user_name(self) -> str:
        """获取用户显示名称"""
        return "用户" if self.role == "user" else "商户管理员"

    def process_message(self, message: str) -> ChatMessage:
        """
        处理用户消息，根据意图路由到不同的支付模式处理
        支持LLM意图识别 + 规则回退机制
        """
        # 首先尝试使用LLM识别意图（如果启用）
        llm_intent = None
        llm_confidence = 0.0
        llm_entities = {}

        if self.use_llm and self.llm_client:
            llm_intent, llm_confidence, llm_entities = self._identify_intent_with_llm(message)
            # 在侧边栏显示LLM识别结果（调试用）
            if st.session_state.get("show_llm_debug", False):
                with st.sidebar:
                    st.markdown("---")
                    st.markdown("**🔍 LLM意图识别**")
                    st.write(f"意图: `{llm_intent}`")
                    st.write(f"置信度: `{llm_confidence:.2f}`")
                    st.write(f"实体: `{llm_entities}`")

        # 决策：如果LLM置信度足够高，使用LLM意图；否则使用规则匹配
        CONFIDENCE_THRESHOLD = 0.5  # 置信度阈值

        if self.use_llm and llm_confidence >= CONFIDENCE_THRESHOLD:
            # 使用LLM识别的意图
            intent = llm_intent
            context = llm_entities
            use_llm_path = True
        else:
            # 回退到规则匹配
            intent, context = self._identify_intent_rule_based(message)
            use_llm_path = False

        # 根据意图路由到对应的处理器
        handler_map = {
            "help": lambda: self._handle_help(),
            "merchant_command": lambda: self._handle_merchant_commands(context.get("message", message)),
            "autonomous_payment": lambda: self._handle_autonomous_payment_intent(context.get("message", message)),
            "delegated_payment": lambda: self._handle_delegated_payment_intent(context.get("message", message)),
            "delegated_payment_execute": lambda: self._handle_delegated_payment_execute(context.get("message", message)),
            "cancel_delegation": lambda: self._handle_cancel_delegation(context.get("message", message)),
            "instant_payment": lambda: self._handle_instant_payment_intent(context.get("message", message)),
            "view_orders": lambda: self._handle_view_orders(),
            "view_products": lambda: self._handle_view_products(),
            "view_delegations": lambda: self._handle_view_delegations(),
            "default_chat": lambda: self._handle_default_chat(context.get("message", message)),
        }

        # 执行对应的处理器
        handler = handler_map.get(intent, handler_map["default_chat"])
        response = handler()

        # 如果是LLM识别的路径，添加元数据标记
        if use_llm_path and response.metadata is None:
            response.metadata = {}
        if use_llm_path and response.metadata is not None:
            response.metadata["llm_used"] = True
            response.metadata["llm_intent"] = llm_intent
            response.metadata["llm_confidence"] = llm_confidence

        return response

    def _handle_help(self) -> ChatMessage:
        """显示帮助信息 - 支持LLM生成智能回复"""
        # 如果启用了真实LLM，使用LLM生成更自然的帮助回复
        if self.use_llm and self.llm_client and not getattr(self.llm_client, 'is_mock', True):
            try:
                system_prompt = """你是ACT协议智能助手。用户询问帮助，请用友好、自然的中文介绍ACT协议的三种支付模式：

1. 即时支付(Instant Payment) - 用户实时在场确认购买
2. 委托支付(Delegated Payment) - 预先授权，智能体在额度内自动支付
3. 自主支付/A2A支付(Autonomous Payment) - 复杂任务，智能体自主决策和支付

请用简洁易懂的方式介绍，用对话式的语气，适当使用emoji。控制在300字以内。"""

                response_content = self.llm_client.chat_completion([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "请帮我介绍一下ACT协议的支付模式"}
                ])

                return ChatMessage(
                    role="assistant",
                    content=response_content,
                    metadata={"llm_generated": True, "protocol": "HELP"}
                )
            except Exception as e:
                # LLM调用失败，显示错误并回退到默认帮助
                error_msg = f"[LLM调用失败: {str(e)[:100]}]"
                return ChatMessage(
                    role="assistant",
                    content=f"⚠️ {error_msg}\n\n---\n\n**默认帮助信息**：\n\n嗨！我是您的ACT协议智能购物助手 🤖\n\n我可以帮您完成以下三种支付模式：\n\n1. 💸 **即时支付** - 您在线，想立即购买\n2. 💼 **委托支付** - 预先授权，后续自动执行\n3. 🤖 **自主支付/A2A支付** - 复杂任务，智能体自主决策",
                    metadata={"llm_error": str(e), "llm_failed": True, "protocol": "HELP"}
                )

        # 默认帮助内容（Mock模式）
        content = """
嗨！我是您的ACT协议智能购物助手 🤖

我可以帮您完成以下三种支付模式：

---

## 💸 **1. 即时支付 (Instant Payment)**
**适用场景**：您在线，想立即购买
**对话示例**：
- "帮我买一杯星巴克大杯拿铁"
- "现在购买iPhone 15 Pro"
**特点**：
- 您实时确认支付
- 无需预先授权
- 收银台确认即完成授权

---

## 💼 **2. 委托支付 (Delegated Payment)**
**适用场景**：预先授权，后续自动执行
**对话示例**：
- "帮我授权每月自动续费中国移动套餐，不超过100元"
- "设置IAC委托：每天自动购买咖啡，额度200元"
- "开通委托：帮我代购某本书，额度150元"
**特点**：
- 签发IAC授权凭证
- 智能体在额度内代您支付
- 您可以随时查询状态和剩余额度

---

## 🤖 **3. 自主支付 / A2A支付 (Autonomous Payment)**
**适用场景**：复杂任务，需要智能体自主决策
**对话示例**：
- "帮我安排下周出差上海，预算5000元"
- "帮我规划一个3天2晚的杭州旅游，预算3000元"
- "预订明天飞北京的机票和酒店，预算控制在1200元"
**特点**：
- 智能体自动拆解子任务（机票、酒店、用车等）
- A2A（智能体对智能体）直接交易
- 使用专属子账户，资金隔离
- 全程无需您逐笔确认

---

您想体验哪种支付模式呢？可以直接告诉我您的需求！
        """.strip()
        return ChatMessage(role="assistant", content=content)

    def _handle_instant_payment_intent(self, message: str) -> ChatMessage:
        """处理即时支付意图"""
        # 解析商品
        product = self._parse_product_from_message(message)

        if not product:
            products_list = "\n".join([f"- {p['name']}: ¥{p['price']}" for p in self.data["products"]])
            return ChatMessage(
                role="assistant",
                content=f"我没有找到您想要的商品。当前可购买的商品有：\n\n{products_list}\n\n请告诉我具体想买什么？"
            )

        if product["stock"] <= 0:
            return ChatMessage(
                role="assistant",
                content=f"抱歉，**{product['name']}** 暂时缺货。您可以看看其他商品，或者联系商户补货。"
            )

        self.pending_action = {
            "type": "instant_payment",
            "product_id": product["id"],
            "product_name": product["name"],
            "amount": product["price"]
        }

        content = f"""
💸 **即时支付确认**

我理解了您的购买意图：
- 商品：**{product['name']}**
- 价格：¥{product['price']}
- 模式：**即时支付** (PSD-PAY-INS)

**流程说明**：
1. ✅ 解析购买意图 (ADD-INT-EAC)
2. ✅ 获取商品信息 (CID-MER-CAT)
3. ⏳ 等待您确认支付
4. ⏳ 唤起收银台
5. ⏳ 您实时确认完成支付

**关键特征**：
- 您**全程在场**实时确认
- 无需签发IAC
- 使用已绑定的支付标记

请回复"**确认支付**"或"**取消**"：
        """.strip()

        return ChatMessage(role="assistant", content=content, metadata={"protocol": "PSD-PAY-INS"})

    def _handle_delegated_payment_intent(self, message: str) -> ChatMessage:
        """处理委托支付意图 (定向委托)"""
        # 解析额度和商品
        amount = self._parse_amount_from_message(message)

        if not amount or amount <= 0:
            amount = 500.0  # 默认额度

        delegation_id = f"did:act:delegation:{uuid.uuid4().hex[:16]}"

        self.pending_action = {
            "type": "delegated_payment_setup",
            "delegation_id": delegation_id,
            "max_total": amount,
            "max_single": amount / 5  # 单笔为总额的1/5
        }

        content = f"""
💼 **委托支付授权设置**

我理解了您的委托意图，准备为您签发IAC授权凭证。

**拟定的授权参数**：
- 委托ID：`{delegation_id}`
- 总额度上限：**¥{amount:.2f}**
- 单笔上限：**¥{amount/5:.2f}**
- 模式：**定向委托支付** (delegation_mode: SPECIFIED)

**流程说明**：
1. ⏳ 您确认签发IAC
2. ⏳ 生成IAC凭证 (ADD-IAC-ISS)
3. ⏳ 设置额度与限制
4. ✅ 后续智能体在授权内自动执行 (PSD-PAY-DEL)
5. ✅ 无需您实时介入

**关键特征**：
- 您**预先授权**，后续自动执行
- 签发IAC凭证作为授权依据
- 智能体在授权边界内程序化支付
- 支持累计额度管控

**涉及协议组件**：
- `ADD-INT-EAC` - 获取委托意图
- `ADD-IAC-ISS` - 签发IAC
- `PSD-PAY-DEL` - 委托支付流程

请回复"**签发委托**"或"**修改额度 [金额]**"或"**取消**"：
        """.strip()

        return ChatMessage(role="assistant", content=content, metadata={"protocol": "PSD-PAY-DEL"})

    def _handle_autonomous_payment_intent(self, message: str) -> ChatMessage:
        """处理自主支付/A2A支付意图 - 如果没有预算则询问"""
        # 解析预算
        budget = self._parse_amount_from_message(message)

        # 判断任务类型
        task_desc = self._parse_autonomous_task(message)

        # 如果没有指定预算，询问用户
        if not budget or budget <= 0:
            self.pending_action = {
                "type": "autonomous_payment_setup_pending_budget",
                "task_desc": task_desc,
                "message": message
            }
            return ChatMessage(
                role="assistant",
                content=f"""
🤖 **自主支付 / A2A支付任务规划**

我理解了您的任务需求：**{task_desc}**

这是一个适合使用A2A自主支付模式的复杂任务。智能体将自主完成：
- 任务拆解（交通、住宿、门票等）
- A2A服务发现与协商
- 基于HTTP 402的支付流程
- 全程无需您逐笔确认

**⚠️ 请设定预算上限**

为了控制智能体的支出范围，请告诉我您的预算，例如：
- "预算5000元"
- "不超过10000块"
- "控制在3000以内"

输入预算金额后，我将为您创建任务并开立专属子账户。
                """.strip(),
                metadata={"protocol": "PSD-PAY-A2A", "pending_budget": True}
            )

        # 有预算，继续创建任务
        task_id = f"did:act:task:{uuid.uuid4().hex[:16]}"

        self.pending_action = {
            "type": "autonomous_payment_setup",
            "task_id": task_id,
            "budget": budget,
            "description": task_desc
        }

        content = f"""
🤖 **自主支付 / A2A支付任务规划**

我理解了您的复杂任务需求，将为您创建A2A支付任务。

**任务规划**：
- 任务ID：`{task_id}`
- 任务描述：**{task_desc}**
- 总预算：**¥{budget:.2f}**
- 模式：**自主委托** (delegation_mode: BOUNDED + A2A支付)

**执行流程**：
1. ⏳ 您确认任务边界
2. ⏳ 为智能体开立专属子账户 (PSD-AGT-SUB)
3. ⏳ 子账户充值 ¥{budget:.2f}
4. ✅ 智能体自主拆解子任务（机票、酒店、用车等）
5. ✅ 智能体发现卖方智能体 (CID-PCA-NEG)
6. ✅ 卖方返回HTTP 402支付诉求
7. ✅ 买方智能体构造A2A支付载荷 (PSD-PAY-A2A)
8. ✅ PSP核验IAC与子账户密钥签名，完成扣款
9. ✅ 智能体携带支付凭证访问资源

**关键特征**：
- 智能体拥有**高度自主决策权**
- 智能体间**A2A直接交易**
- 使用**专属子账户**，资金隔离
- 基于HTTP 402语义扩展
- 全程**无需您逐笔确认**

**涉及协议组件**：
- `ADD-INT-EAC` - 获取任务边界
- `PSD-AGT-SUB` - 智能体子账户
- `CID-PCA-NEG` - 支付能力协商
- `PSD-PAY-A2A` - A2A支付流程

想开始模拟执行这个过程吗？回复"**确认创建任务**"或"**修改预算 [金额]**"或"**取消**"：
        """.strip()

        return ChatMessage(role="assistant", content=content, metadata={"protocol": "PSD-PAY-A2A"})

    def confirm_pending_action(self) -> ChatMessage:
        """执行待确认的操作"""
        if not self.pending_action:
            return ChatMessage(role="assistant", content="没有待确认的操作。")

        action_type = self.pending_action["type"]

        if action_type == "instant_payment":
            return self._execute_instant_payment()
        elif action_type == "delegated_payment_setup":
            return self._execute_delegated_setup()
        elif action_type == "delegated_payment_execute":
            return self._execute_delegated_payment()
        elif action_type == "autonomous_payment_setup":
            return self._execute_autonomous_setup()
        elif action_type == "autonomous_payment_execute":
            return self._execute_autonomous_payment()
        elif action_type == "cancel_delegation":
            return self._execute_cancel_delegation()

        self.pending_action = None

    def _execute_instant_payment(self) -> ChatMessage:
        """执行即时支付"""
        action = self.pending_action
        self.pending_action = None

        product_id = action["product_id"]

        # 扣减库存
        for p in self.data["products"]:
            if p["id"] == product_id:
                p["stock"] -= 1
                break

        # 创建订单
        order = {
            "id": f"ORD-{uuid.uuid4().hex[:12]}",
            "user_id": self.user_id,
            "product_id": product_id,
            "product_name": action["product_name"],
            "amount": action["amount"],
            "payment_mode": "instant",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        self.data["orders"].append(order)
        save_demo_data(self.data)

        return ChatMessage(
            role="assistant",
            content=f"""
✅ **即时支付成功！**

**支付详情**：
- 订单号：{order['id']}
- 商品：{action['product_name']}
- 金额：¥{action['amount']:.2f}
- 支付模式：**即时支付** (PSD-PAY-INS)
- 状态：已完成

**协议执行回顾**：
1. ✅ 获取并解析购买意图 (ADD-INT-EAC)
2. ✅ 结构化表达意图 (ADD-INT-ISR)
3. ✅ 获取商户商品目录 (CID-MER-CAT)
4. ✅ 购物车确认与规则自检 (CID-CART-CFM)
5. ✅ 使用已绑定的支付标记 (PSD-PMT-BND)
6. ✅ 即时支付流程完成 (PSD-PAY-INS)

**关键特征体现**：
✓ 用户全程在场实时确认
✓ 无需签发IAC，收银台确认即授权
✓ 单次即时交易

---
您还需要购买其他商品吗？或者想体验委托支付/自主支付模式？
            """.strip(),
            metadata={"payment_complete": True, "mode": "instant"}
        )

    def _execute_delegated_setup(self) -> ChatMessage:
        """执行委托支付设置"""
        action = self.pending_action
        self.pending_action = None

        # 保存委托
        delegation = {
            "id": action["delegation_id"],
            "user_id": self.user_id,
            "max_total": action["max_total"],
            "max_single": action["max_single"],
            "used_amount": 0.0,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "iac_jwt": self._generate_mock_iac(action)
        }
        self.data["delegations"].append(delegation)
        save_demo_data(self.data)

        return ChatMessage(
            role="assistant",
            content=f"""
✅ **IAC委托授权已签发！**

**委托凭证详情**：
- 委托ID：`{action['delegation_id']}`
- 总额度：**¥{action['max_total']:.2f}**
- 单笔上限：**¥{action['max_single']:.2f}**
- 当前已用：¥0.00
- 状态：**已激活**

**IAC凭证（模拟JWT）**：
```json
{self._generate_mock_iac(action, pretty=True)}
```

**协议执行回顾**：
1. ✅ 获取用户定向委托意图 (ADD-INT-EAC)
2. ✅ 结构化表达意图 (ADD-INT-ISR: delegation_mode=SPECIFIED)
3. ✅ 委托人核身确认
4. ✅ 签发IAC凭证 (ADD-IAC-ISS)
5. ✅ IAC生命周期管理启动 (ADD-IAC-LCM)

**接下来您可以**：
- 说"**使用委托购买 [商品名]**" - 智能体将基于IAC自动执行支付
- 说"**查询委托状态**" - 查看剩余额度和使用记录
- 说"**吊销委托**" - 取消授权

---
想试试用委托购买商品吗？例如："使用委托购买iPhone 15 Pro"
            """.strip(),
            metadata={"delegation_created": True, "mode": "delegated"}
        )

    def _execute_delegated_payment(self) -> ChatMessage:
        """使用委托执行支付"""
        action = self.pending_action
        self.pending_action = None

        delegation_id = action["delegation_id"]
        delegation = None

        for d in self.data["delegations"]:
            if d["id"] == delegation_id and d["status"] == "active":
                delegation = d
                break

        if not delegation:
            return ChatMessage(role="assistant", content="未找到有效的委托授权，请先创建委托。")

        # 检查额度
        remaining = delegation["max_total"] - delegation["used_amount"]
        if action["amount"] > remaining:
            return ChatMessage(
                role="assistant",
                content=f"❌ 委托额度不足！本次需要 ¥{action['amount']:.2f}，剩余额度 ¥{remaining:.2f}"
            )

        # 执行支付
        delegation["used_amount"] += action["amount"]

        # 创建订单
        order = {
            "id": f"ORD-{uuid.uuid4().hex[:12]}",
            "user_id": self.user_id,
            "product_id": action.get("product_id"),
            "product_name": action.get("product_name", "委托购买"),
            "amount": action["amount"],
            "payment_mode": "delegated",
            "delegation_id": delegation_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        self.data["orders"].append(order)
        save_demo_data(self.data)

        return ChatMessage(
            role="assistant",
            content=f"""
✅ **委托支付成功！** (PSD-PAY-DEL)

**支付详情**：
- 订单号：{order['id']}
- 商品：{action.get('product_name', '委托购买')}
- 金额：¥{action['amount']:.2f}
- 支付方式：**IAC委托支付**
- 委托ID：`{delegation_id[:30]}...`
- 委托剩余额度：**¥{delegation['max_total'] - delegation['used_amount']:.2f}**

**协议执行流程**：
1. ✅ 意图上下文传递 (CID-INT-RUT)
2. ✅ 智能体完成购物车确认 (CID-CART-CFM)
3. ✅ 智能体基于IAC发起委托支付 (PSD-PAY-DEL)
4. ✅ PSP核验IAC有效性
5. ✅ 执行扣款

**关键特征体现**：
✓ 用户**无需实时在场**，智能体自主执行
✓ 基于预签发的IAC凭证授权
✓ 自动额度管控，防止超额
✓ 支持累计额度跟踪

---
委托授权仍有效，您可以说"**再帮我买 [商品]**"继续使用委托支付。
            """.strip(),
            metadata={"payment_complete": True, "mode": "delegated"}
        )

    def _handle_delegated_payment_execute(self, message: str) -> ChatMessage:
        """处理使用委托购买（通过意图识别路由）"""
        # 解析商品
        product = self._parse_product_from_message(message)

        if not product:
            return ChatMessage(
                role="assistant",
                content="请告诉我具体想购买什么商品，例如：\"使用委托购买iPhone\""
            )

        # 查找有效委托
        delegation = None
        for d in self.data["delegations"]:
            if d.get("user_id") == self.user_id and d.get("status") == "active":
                delegation = d
                break

        if not delegation:
            return ChatMessage(
                role="assistant",
                content="您没有有效的委托授权。请先说\"帮我授权...\"创建委托。"
            )

        # 设置待执行操作
        self.pending_action = {
            "type": "delegated_payment_execute",
            "delegation_id": delegation["id"],
            "product_id": product["id"],
            "product_name": product["name"],
            "amount": product["price"]
        }

        return ChatMessage(
            role="assistant",
            content=f"确认使用委托支付购买**{product['name']}**（¥{product['price']:.2f}）吗？请回复\"确认支付\"或\"取消\"",
            metadata={"protocol": "PSD-PAY-DEL"}
        )

    def _handle_cancel_delegation(self, message: str) -> ChatMessage:
        """处理取消/吊销委托"""
        # 查找用户当前有效的委托
        user_delegations = [d for d in self.data["delegations"]
                           if d.get("user_id") == self.user_id and d.get("status") == "active"]

        if not user_delegations:
            return ChatMessage(
                role="assistant",
                content="您当前没有有效的委托授权需要取消。\n\n您可以对我说：\"帮我授权每月买咖啡，额度500元\" 来创建新的委托。"
            )

        # 如果有多个委托，取最新的一个（或者可以让用户选择）
        delegation = user_delegations[-1]

        # 设置待执行操作（需要用户确认）
        self.pending_action = {
            "type": "cancel_delegation",
            "delegation_id": delegation["id"],
            "delegation_info": delegation
        }

        remaining = delegation["max_total"] - delegation["used_amount"]

        return ChatMessage(
            role="assistant",
            content=f"""
**确认取消委托授权？**

委托ID：`{delegation['id'][:25]}...`
- 总额度：¥{delegation['max_total']:.2f}
- 已使用：¥{delegation['used_amount']:.2f}
- 剩余：¥{remaining:.2f}

⚠️ 取消后该委托将立即失效，无法继续使用委托支付。

请回复 **"确认取消"** 或 **"取消"**
            """.strip(),
            metadata={"requires_confirmation": True, "action_type": "cancel_delegation"}
        )

    def _execute_cancel_delegation(self) -> ChatMessage:
        """执行取消委托操作"""
        action = self.pending_action
        self.pending_action = None

        delegation_id = action["delegation_id"]

        # 找到并更新委托状态
        for d in self.data["delegations"]:
            if d["id"] == delegation_id:
                d["status"] = "cancelled"
                d["cancelled_at"] = datetime.now().isoformat()
                break

        save_demo_data(self.data)

        return ChatMessage(
            role="assistant",
            content="""
✅ **委托授权已取消**

- 该委托已立即失效
- 不再允许使用委托支付
- 已产生的订单不受影响

您可以随时创建新的委托授权。
            """.strip()
        )

    def _execute_autonomous_setup(self) -> ChatMessage:
        """执行自主支付/A2A任务设置"""
        action = self.pending_action
        self.pending_action = None

        budget = action["budget"]
        task_id = action["task_id"]

        # 创建子账户
        sub_account_id = f"did:act:sub:{uuid.uuid4().hex[:12]}"

        # 保存任务和子账户
        task = {
            "id": task_id,
            "user_id": self.user_id,
            "description": action["description"],
            "budget": budget,
            "sub_account_id": sub_account_id,
            "sub_account_balance": budget,
            "status": "active",
            "sub_tasks": [],
            "created_at": datetime.now().isoformat()
        }

        self.data["sub_accounts"][sub_account_id] = {
            "balance": budget,
            "initial_budget": budget,
            "transactions": []
        }

        self.data["orders"].append({  # 作为任务记录
            "id": task_id,
            "type": "autonomous_task",
            "user_id": self.user_id,
            **task
        })
        save_demo_data(self.data)

        return ChatMessage(
            role="assistant",
            content=f"""
✅ **自主支付任务已创建！** (PSD-PAY-A2A)

**任务配置**：
- 任务ID：`{task_id}`
- 专属子账户：`{sub_account_id}`
- 子账户初始余额：**¥{budget:.2f}**
- 模式：**自主委托** + A2A支付

**IAC凭证（Bound模式）**：
```json
{{
  "delegation_id": "{task_id}",
  "delegation_mode": "BOUNDED",
  "max_total_amount": {budget},
  "allowed_categories": ["all"],
  "sub_account": "{sub_account_id}"
}}
```

**协议执行回顾**：
1. ✅ 获取复杂任务目标与约束边界 (ADD-INT-EAC)
2. ✅ 结构化表达意图 (ADD-INT-ISR: delegation_mode=BOUNDED)
3. ✅ 签发自主委托类型的IAC (ADD-IAC-ISS)
4. ✅ 为智能体开立专属子账户 (PSD-AGT-SUB)
5. ✅ 子账户充值完成

**接下来将自动执行**：
6. ⏳ 智能体自主拆解子任务
7. ⏳ 服务市场发现卖方智能体
8. ⏳ 与卖方智能体支付能力协商 (CID-PCA-NEG)
9. ⏳ 接收HTTP 402支付诉求
10. ⏳ A2A支付流程 (PSD-PAY-A2A)

想开始模拟执行这个过程吗？回复"**开始执行任务**"：
            """.strip(),
            metadata={"autonomous_task_created": True, "mode": "a2a"}
        )

    def simulate_autonomous_execution(self, task_id: str, step: str = "flight") -> ChatMessage:
        """模拟自主支付任务的A2A执行过程 - 支持多步骤任务"""

        # 获取任务信息（如果存在）
        task = None
        initial_budget = 5000.0
        if task_id:
            for order in self.data.get("orders", []):
                if order.get("id") == task_id and order.get("type") == "autonomous_task":
                    task = order
                    initial_budget = order.get("budget", 5000.0)
                    break

        # 根据当前步骤生成不同的执行记录
        if step == "flight":
            used = 800.0
            step_name = "机票预订"
            next_step_name = "酒店预订"
            steps = [
                ("🤖 买方智能体", "正在拆解任务为子任务：机票、酒店、用车..."),
                ("🔍 服务发现", "在A2A服务市场发现机票服务智能体..."),
                ("💬 CID-PCA-NEG", "与机票服务智能体协商支付能力..."),
                ("📡 HTTP 402", "卖方智能体返回支付诉求：¥800 for 机票"),
                ("💰 A2A支付", "买方智能体提交A2A支付载荷至PSP"),
                ("🔐 PSP核验", "验证IAC有效性和子账户密钥签名..."),
                ("✅ 扣款成功", f"从子账户扣款¥800，余额¥{initial_budget - used:.0f}"),
                ("🎫 资源访问", "买方智能体携带支付凭证获取机票确认..."),
            ]
            status_line = f"- ✅ 子任务1（机票）：完成，支付¥800\n- ⏳ 子任务2（酒店）：等待执行"
            next_prompt = f'想继续执行{next_step_name}吗？回复"**继续执行**"'

        elif step == "hotel":
            used = 2000.0  # 800 + 1200
            step_name = "酒店预订"
            next_step_name = "用车预订"
            steps = [
                ("🤖 买方智能体", "开始执行子任务2：酒店预订..."),
                ("🔍 服务发现", "在A2A服务市场发现酒店预订智能体..."),
                ("💬 CID-PCA-NEG", "与酒店服务智能体协商支付能力..."),
                ("📡 HTTP 402", "卖方智能体返回支付诉求：¥1200 for 两晚酒店"),
                ("💰 A2A支付", "买方智能体提交A2A支付载荷至PSP"),
                ("🔐 PSP核验", "验证IAC有效性和子账户密钥签名..."),
                ("✅ 扣款成功", f"从子账户扣款¥1200，余额¥{initial_budget - used:.0f}"),
                ("🏨 资源访问", "买方智能体携带支付凭证确认酒店预订..."),
            ]
            status_line = f"- ✅ 子任务1（机票）：完成，支付¥800\n- ✅ 子任务2（酒店）：完成，支付¥1200\n- ⏳ 子任务3（用车）：等待执行"
            next_prompt = f'想继续执行{next_step_name}吗？回复"**继续执行**"'

        elif step == "car":
            used = 2300.0  # 800 + 1200 + 300
            step_name = "用车预订"
            steps = [
                ("🤖 买方智能体", "开始执行子任务3：用车预订..."),
                ("🔍 服务发现", "在A2A服务市场发现用车服务智能体..."),
                ("💬 CID-PCA-NEG", "与用车服务智能体协商支付能力..."),
                ("📡 HTTP 402", "卖方智能体返回支付诉求：¥300 for 机场接送"),
                ("💰 A2A支付", "买方智能体提交A2A支付载荷至PSP"),
                ("🔐 PSP核验", "验证IAC有效性和子账户密钥签名..."),
                ("✅ 扣款成功", f"从子账户扣款¥300，余额¥{initial_budget - used:.0f}"),
                ("🚗 资源访问", "买方智能体携带支付凭证确认用车服务..."),
            ]
            status_line = f"- ✅ 子任务1（机票）：完成，支付¥800\n- ✅ 子任务2（酒店）：完成，支付¥1200\n- ✅ 子任务3（用车）：完成，支付¥300"
            next_prompt = "🎉 所有子任务已完成！"

        else:
            return ChatMessage(
                role="assistant",
                content="""
🎉 **A2A自主支付任务全部完成！**

**执行汇总**：
- ✅ 子任务1（机票）：¥800
- ✅ 子任务2（酒店）：¥1200
- ✅ 子任务3（用车）：¥300

**总计支出：¥2300**
**子账户剩余：实际根据初始预算计算

所有支付均通过A2A协议自动完成，无需您逐笔介入。
                """.strip(),
                metadata={"a2a_simulation": True, "step": "complete"}
            )

        progress = "\n".join([f"**{i+1}. {s[0]}**: {s[1]}" for i, s in enumerate(steps)])
        remaining = initial_budget - used

        return ChatMessage(
            role="assistant",
            content=f"""
🤖 **A2A自主支付执行实录 - {step_name}**

{progress}

**当前状态**：
{status_line}

**子账户余额**：
- 初始：¥{initial_budget:.2f}
- 已用：¥{used:.2f}
- 剩余：**¥{remaining:.2f}**

---
**A2A支付特征体现**：
✓ 智能体间直接交易 (Agent-to-Agent)
✓ HTTP 402语义扩展
✓ 专属子账户资金隔离
✓ 全程无用户逐笔介入

{next_prompt}
            """.strip(),
            metadata={"a2a_simulation": True, "step": step}
        )

    def _handle_merchant_commands(self, message: str) -> ChatMessage:
        """处理商户相关指令"""
        msg_lower = message.lower()

        if any(kw in msg_lower for kw in ["上架", "添加商品", "新增商品"]):
            return ChatMessage(role="assistant", content="商户上架商品功能需要通过表单交互。请告诉我商品名称、价格和库存，格式：上架 [商品名] 价格 [金额] 库存 [数量]")

        if any(kw in msg_lower for kw in ["查看订单", "所有订单", "销售情况"]):
            return self._handle_merchant_view_orders()

        if any(kw in msg_lower for kw in ["通知用户", "推送", "公告"]):
            return ChatMessage(role="assistant", content="请输入要通知用户的内容，格式：通知 [内容]")

        return ChatMessage(role="assistant", content="商户管理功能开发中。可用指令：查看订单、上架商品、通知用户")

    def _handle_view_orders(self) -> ChatMessage:
        """查看用户订单 - 显示所有购买记录和A2A任务"""
        # 获取用户的所有订单（不包括A2A任务）
        user_orders = [o for o in self.data["orders"] if o.get("user_id") == self.user_id and o.get("type") != "autonomous_task"]

        # 获取用户的A2A任务
        user_tasks = [o for o in self.data["orders"] if o.get("user_id") == self.user_id and o.get("type") == "autonomous_task"]

        content_lines = []

        # 统计信息
        instant_count = len([o for o in user_orders if o.get("payment_mode") == "instant"])
        delegated_count = len([o for o in user_orders if o.get("payment_mode") == "delegated"])

        content_lines.append(f"📊 **您的交易统计**")
        content_lines.append(f"- 即时支付订单: {instant_count} 笔")
        content_lines.append(f"- 委托支付订单: {delegated_count} 笔")
        content_lines.append(f"- A2A任务: {len(user_tasks)} 个")
        content_lines.append(f"- **总计: {len(user_orders) + len(user_tasks)} 条记录**")
        content_lines.append("")

        # 显示购买订单
        if user_orders:
            content_lines.append(f"**最近购买记录**（共 {len(user_orders)} 条，显示最近10条）：")
            for i, o in enumerate(reversed(user_orders[-10:]), 1):
                mode_icon = {"instant": "💸", "delegated": "💼"}.get(o.get("payment_mode"), "💰")
                content_lines.append(f"{i}. {mode_icon} {o['product_name']} | ¥{o['amount']:.2f} | {o['payment_mode']} | {o['status']}")
            content_lines.append("")
        else:
            content_lines.append("💡 暂无购买订单。输入「买iPhone」体验即时支付！")
            content_lines.append("")

        # 显示A2A任务
        if user_tasks:
            content_lines.append(f"**A2A自主任务**（共 {len(user_tasks)} 个）：")
            for i, t in enumerate(user_tasks, 1):
                sub_balance = t.get("sub_account_balance", 0)
                initial = t.get("budget", 0)
                used = initial - sub_balance
                content_lines.append(f"{i}. 🤖 {t.get('description', '自主任务')} | 预算¥{initial:.2f} | 已用¥{used:.2f} | 状态: {t.get('status', 'active')}")
            content_lines.append("")

        return ChatMessage(role="assistant", content="\n".join(content_lines))

    def _handle_view_products(self) -> ChatMessage:
        """查看商品列表"""
        products = self.data["products"]

        product_list = "\n".join([
            f"- **{p['name']}** | ¥{p['price']:.2f} | 库存: {p['stock']}"
            for p in products
        ])

        return ChatMessage(role="assistant", content=f"**当前可购买的商品**：\n\n{product_list}\n\n想买什么直接告诉我，例如：\"买iPhone 15 Pro\"")

    def _handle_view_delegations(self) -> ChatMessage:
        """查看委托状态"""
        user_delegations = [d for d in self.data["delegations"] if d.get("user_id") == self.user_id and d.get("status") == "active"]

        if not user_delegations:
            return ChatMessage(role="assistant", content="您没有正在生效的委托授权。\n\n可以对我说：\"帮我授权每月买咖啡，额度500元\" 来创建委托。")

        delegation = user_delegations[-1]  # 最新的
        remaining = delegation["max_total"] - delegation["used_amount"]

        return ChatMessage(
            role="assistant",
            content=f"""
**您的IAC委托状态**：

- 委托ID：`{delegation['id'][:40]}...`
- 总额度：¥{delegation['max_total']:.2f}
- 已使用：¥{delegation['used_amount']:.2f}
- **剩余额度：¥{remaining:.2f}**
- 状态：{delegation['status']}

可以使用委托购买商品，智能体将自动在授权额度内完成支付。
            """.strip()
        )

    def _handle_merchant_view_orders(self) -> ChatMessage:
        """商户查看所有订单 - 包含统计分析"""
        all_orders = [o for o in self.data["orders"] if o.get("type") != "autonomous_task"]
        all_tasks = [o for o in self.data["orders"] if o.get("type") == "autonomous_task"]

        if not all_orders and not all_tasks:
            return ChatMessage(role="assistant", content="暂无订单或任务记录。")

        content_lines = []

        # 统计汇总
        instant_total = sum(o['amount'] for o in all_orders if o.get("payment_mode") == "instant")
        delegated_total = sum(o['amount'] for o in all_orders if o.get("payment_mode") == "delegated")
        instant_count = len([o for o in all_orders if o.get("payment_mode") == "instant"])
        delegated_count = len([o for o in all_orders if o.get("payment_mode") == "delegated"])

        content_lines.append("📈 **整体交易统计**")
        content_lines.append(f"- 总订单数: {len(all_orders)} 笔")
        content_lines.append(f"- 即时支付: {instant_count} 笔 (¥{instant_total:.2f})")
        content_lines.append(f"- 委托支付: {delegated_count} 笔 (¥{delegated_total:.2f})")
        content_lines.append(f"- A2A任务: {len(all_tasks)} 个")
        content_lines.append(f"- 总交易额: ¥{instant_total + delegated_total:.2f}")
        content_lines.append("")

        # 显示最近订单
        if all_orders:
            content_lines.append(f"**最近订单**（最近10条）：")
            for i, o in enumerate(reversed(all_orders[-10:]), 1):
                mode_icon = {"instant": "💸", "delegated": "💼"}.get(o.get("payment_mode"), "💰")
                user_short = o.get("user_id", "unknown")[:8]
                content_lines.append(f"{i}. {mode_icon} {o.get('product_name', 'N/A')} | ¥{o['amount']:.2f} | 用户{user_short}... | {o.get('timestamp', 'N/A')[:10]}")
            content_lines.append("")

        # 显示A2A任务汇总
        if all_tasks:
            content_lines.append(f"**活跃的A2A任务**（共{len(all_tasks)}个）：")
            for i, t in enumerate(all_tasks[-5:], 1):
                content_lines.append(f"{i}. 🤖 {t.get('description', '自主任务')} | 预算¥{t.get('budget', 0):.2f}")

        return ChatMessage(role="assistant", content="\n".join(content_lines))

    def _handle_default_chat(self, message: str) -> ChatMessage:
        """默认对话回复 - 支持LLM生成智能回复"""
        # 检查是否可以使用真实LLM生成回复
        can_use_llm = self.use_llm and self.llm_client and not getattr(self.llm_client, 'is_mock', True)

        # 调试信息
        if st.session_state.get("show_llm_debug", False):
            st.markdown(f"<div style='font-size: 0.7rem; color: gray;'>调试: use_llm={self.use_llm}, client={type(self.llm_client).__name__ if self.llm_client else None}, is_mock={getattr(self.llm_client, 'is_mock', 'N/A')}, can_use={can_use_llm}</div>", unsafe_allow_html=True)

        if can_use_llm:
            try:
                system_prompt = """你是ACT协议智能购物助手。用户刚刚说了一句你可能不太理解的话，请用友好、自然的中文回复，询问用户需要什么帮助。

ACT协议支持三种支付模式：
1. 即时支付 - 用户实时购买商品
2. 委托支付 - 预先授权，智能体代为支付
3. 自主支付/A2A支付 - 复杂任务，智能体自主决策

请简洁、友好地回复，引导用户说出他们的需求。"""

                response_content = self.llm_client.chat_completion([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ])

                return ChatMessage(
                    role="assistant",
                    content=response_content,
                    metadata={"llm_generated": True}
                )
            except Exception as e:
                # LLM调用失败，显示错误信息并回退到默认回复
                error_msg = f"[LLM调用失败: {str(e)[:100]}]"
                # 始终显示错误，帮助排查问题
                return ChatMessage(
                    role="assistant",
                    content=f"⚠️ {error_msg}\n\n我已回退到默认回复模式。\n\n嗨！我是您的ACT协议智能助手。\n\n我可以帮您：\n\n**作为用户**：\n- 💸 即时购买商品\n- 💼 设置委托授权\n- 🤖 创建A2A任务\n\n**作为商户**：\n- 📦 管理商品\n- 📋 查看订单\n- 📢 推送通知",
                    metadata={"llm_error": str(e), "llm_failed": True}
                )

        # 默认回复（Mock模式）
        return ChatMessage(
            role="assistant",
            content=f"嗨！我是您的ACT协议智能助手。\n\n我可以帮您：\n\n**作为用户**：\n- 💸 即时购买商品（您在场确认支付）\n- 💼 设置委托授权（预授权后智能体自动执行）\n- 🤖 创建自动化任务（A2A支付，智能体自主决策）\n\n**作为商户**：\n- 📦 管理商品上架\n- 📋 查看订单情况\n- 📢 向用户推送通知\n\n不知道怎么做？输入\"帮助\"查看详细说明！"
        )

    # ----- 工具方法 -----

    def _parse_product_from_message(self, message: str) -> Optional[Dict]:
        """从消息中解析商品 - 支持模糊匹配"""
        message_lower = message.lower()

        # 1. 首先尝试精确匹配（商品名在消息中）
        for p in self.data["products"]:
            if p["name"].lower() in message_lower:
                return p

        # 2. 尝试反向匹配（消息中的词在商品名中）
        # 提取消息中的关键词（过滤常见词汇）
        import re
        keywords = re.findall(r'[a-zA-Z]+|[\u4e00-\u9fff]+', message_lower)
        filtered_keywords = [k for k in keywords if k not in ['买', '购买', '下单', '支付', '我要', '想要', '给我', '来个']]

        # 按关键词匹配数量排序，选择最匹配的商品
        best_match = None
        best_score = 0

        for p in self.data["products"]:
            product_name_lower = p["name"].lower()
            score = 0

            # 检查每个关键词是否在商品名中
            for keyword in filtered_keywords:
                if keyword in product_name_lower:
                    score += 1
                    # 如果关键词长度超过2，给予更高权重
                    if len(keyword) > 2:
                        score += 1

            # 如果有品牌名匹配（如 iPhone, MacBook, 星巴克等），给予额外权重
            brand_keywords = ['iphone', 'macbook', 'airpods', '星巴克', '奈雪']
            for brand in brand_keywords:
                if brand in message_lower and brand in product_name_lower:
                    score += 2

            if score > best_score:
                best_score = score
                best_match = p

        # 如果匹配分数足够高，返回最佳匹配
        if best_score >= 1:
            return best_match

        return None

    def _parse_amount_from_message(self, message: str) -> Optional[float]:
        """从消息中解析金额 - 支持万(w)、千(k)等缩写"""
        import re
        msg = message.lower().replace(' ', '')

        # 匹配数字+万/w（如 3w、3万、3.5万）
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:万|w)', msg)
        if match:
            return float(match.group(1)) * 10000

        # 匹配数字+千/k（如 5k、5千）
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:千|k)', msg)
        if match:
            return float(match.group(1)) * 1000

        # 匹配数字+元/块/¥/￥
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:元|块|¥|￥)', message)
        if match:
            return float(match.group(1))

        # 匹配纯数字（超过10的数字才认为是金额）
        match = re.search(r'(\d{3,})', message)
        if match:
            return float(match.group(1))

        return None

    def _parse_autonomous_task(self, message: str) -> str:
        """解析自主任务描述 - 支持更多旅行目的地和表达方式"""
        msg = message.lower()

        # 差旅相关
        if "出差" in message:
            return "出差行程安排（机票+酒店+用车）"

        # 旅游/旅行相关（包括国内外目的地）
        if any(kw in msg for kw in ["旅游", "旅行", "去", "规划", "安排", "巴哈马", "马尔代夫", "日本", "泰国", "欧洲", "美国", "新加坡", "巴厘岛", "夏威夷", "迪拜"]):
            # 提取目的地
            destinations = ["巴哈马", "马尔代夫", "日本", "泰国", "欧洲", "美国", "新加坡", "巴厘岛", "夏威夷", "迪拜", "香港", "澳门", "台湾", "韩国", "英国", "法国", "德国", "意大利", "西班牙", "瑞士", "新西兰", "澳大利亚", "三亚", "丽江", "大理", "成都", "重庆", "西安", "北京", "上海", "广州", "深圳", "杭州", "厦门", "青岛", "大连", "桂林", "张家界", "西藏", "新疆"]
            found_dest = None
            for dest in destinations:
                if dest in message:
                    found_dest = dest
                    break

            if found_dest:
                return f"{found_dest}旅行行程规划（交通+住宿+门票+餐饮）"
            return "旅行行程规划（交通+住宿+门票+餐饮）"

        # 预订相关
        if "订" in message and ("机票" in message or "酒店" in message):
            return "出行预订（机票+酒店）"

        # 默认
        return "综合性任务执行"

    def _generate_mock_iac(self, action: Dict, pretty: bool = False) -> str:
        """生成模拟的IAC JWT"""
        iac_data = {
            "header": {
                "alg": "ES256",
                "typ": "IAC",
                "kid": "did:act:psp:example#key1"
            },
            "payload": {
                "iat": int(time.time()),
                "exp": int(time.time()) + 30 * 24 * 3600,
                "iss": "did:act:psp:example",
                "sub": action.get("delegation_id"),
                "principal": "did:act:user:example",
                "agent": "did:act:agent:example",
                "max_total_amount": action.get("max_total"),
                "max_single_amount": action.get("max_single"),
                "delegation_mode": "SPECIFIED" if action.get("type") == "delegated_payment_setup" else "BOUNDED"
            }
        }

        if pretty:
            return json.dumps(iac_data, ensure_ascii=False, indent=2)

        return json.dumps(iac_data, ensure_ascii=False)


# ==================== Streamlit UI ====================

def init_session_state():
    """初始化Session State"""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if "current_role" not in st.session_state:
        st.session_state.current_role = None

    if "agent" not in st.session_state:
        st.session_state.agent = None

    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"

    # 加载持久化数据
    data = load_demo_data()
    if "products" not in st.session_state:
        st.session_state.products = data.get("products", [])
    if "orders" not in st.session_state:
        st.session_state.orders = data.get("orders", [])

    # 初始化模型配置
    init_model_config()

    # 调试开关
    if "show_llm_debug" not in st.session_state:
        st.session_state.show_llm_debug = False


def render_chat_based_demo():
    """
    渲染基于对话的ACT协议演示
    """
    init_session_state()

    st.set_page_config(
        page_title="ACT协议 - GPT对话式演示",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 自定义样式
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .protocol-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }
    .instant-badge { background-color: #e3f2fd; color: #1976d2; }
    .delegated-badge { background-color: #fef3e2; color: #f57c00; }
    .a2a-badge { background-color: #e8f5e9; color: #388e3c; }
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

    # 顶部标题
    st.markdown('<div class="main-header">ACT协议 - GPT对话式演示</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #666; margin-bottom: 1rem;">三种支付模式：即时支付 <span class="protocol-badge instant-badge">PSD-PAY-INS</span> | 委托支付 <span class="protocol-badge delegated-badge">PSD-PAY-DEL</span> | 自主支付 <span class="protocol-badge a2a-badge">PSD-PAY-A2A</span></div>', unsafe_allow_html=True)

    # 角色选择
    if st.session_state.current_role is None:
        render_role_selection()
        return

    # 主界面
    col1, col2 = st.columns([4, 1])

    with col2:
        render_sidebar()

    with col1:
        render_chat_interface()


def create_agent_with_llm(user_id: str, role: str) -> ACTChatAgent:
    """创建Agent，根据配置决定是否使用LLM"""
    config = st.session_state.get("model_config", {})

    # 诊断信息
    if config.get("use_llm", False) and config.get("provider") != "mock":
        api_key = config.get("api_key", "")
        provider = config.get("provider", "")
        if not api_key:
            st.warning(f"⚠️ 警告：已启用{provider}但未配置API Key，将回退到Mock模式")
        else:
            st.success(f"✅ 已配置{provider}，API Key已设置 ({api_key[:8]}...)")

    llm_client = get_llm_client(config) if config.get("use_llm", False) else None

    # 显示创建的客户端类型
    if llm_client:
        client_type = type(llm_client).__name__
        is_mock = getattr(llm_client, 'is_mock', True)
        if is_mock and config.get("provider") != "mock":
            st.info(f"ℹ️ 创建的是 MockLLMClient（真实API配置可能不完整）")
        elif not is_mock:
            st.success(f"✅ 成功创建 RealLLMClient ({config.get('provider')})")

    return ACTChatAgent(user_id, role, llm_client=llm_client)


def render_role_selection():
    """渲染角色选择界面"""
    st.markdown("---")
    st.subheader("👤 请选择您的角色")

    col1, col2 = st.columns(2)

    # 检查是否启用了LLM，并区分是Mock还是真实LLM
    config = st.session_state.get("model_config", {})
    llm_enabled = config.get("use_llm", False)
    provider = config.get("provider", "mock")

    if llm_enabled:
        if provider == "mock":
            mode_badge_user = "<br><span style=\"color: #1976d2;\">🧠 Mock 智能模式</span><br><span style=\"font-size: 0.8rem; color: #999;\">(本地模拟，无需API Key)</span>"
            mode_desc_user = "Mock 智能模式"
        else:
            mode_badge_user = f"<br><span style=\"color: #1976d2;\">🤖 AI 智能模式</span><br><span style=\"font-size: 0.8rem; color: #999;\">({provider})</span>"
            mode_desc_user = f"AI 智能模式 ({provider})"
    else:
        mode_badge_user = "<br><span style=\"color: #666;\">⚙️ 规则模式</span>"
        mode_desc_user = "规则模式"

    mode_badge_merchant = mode_badge_user
    mode_desc_merchant = mode_desc_user

    with col1:
        st.markdown(f"""
        <div style="padding: 2rem; border: 2px solid #e3f2fd; border-radius: 1rem; text-align: center; background-color: #f8fbff;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🛒</div>
            <h3>我是用户</h3>
            <p style="color: #666;">体验ACT协议的三种支付模式：<br>即时支付、委托支付、自主A2A支付{mode_badge_user}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("选择用户角色", type="primary", use_container_width=True):
            st.session_state.current_role = "user"
            st.session_state.agent = create_agent_with_llm(
                st.session_state.user_id,
                "user"
            )
            # 添加欢迎消息
            welcome_msg = ChatMessage(
                role="assistant",
                content=f"嗨！我是您的ACT协议智能购物助手 🤖（当前使用：**{mode_desc_user}**）\n\n我可以帮您体验三种不同的支付模式：\n\n1. 💸 **即时支付** - 您在场，实时确认购买\n2. 💼 **委托支付** - 预先授权，智能体代您支付\n3. 🤖 **自主支付** - 复杂任务，智能体A2A自主决策\n\n输入\"帮助\"查看详细说明，或直接告诉我您想做什么！"
            )
            st.session_state.chat_messages.append(welcome_msg)
            st.rerun()

    with col2:
        st.markdown(f"""
        <div style="padding: 2rem; border: 2px solid #f3e5f5; border-radius: 1rem; text-align: center; background-color: #fcf5ff;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🏪</div>
            <h3>我是商户</h3>
            <p style="color: #666;">管理商品和订单<br>查看各种支付模式下的交易{mode_badge_merchant}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("选择商户角色", type="primary", use_container_width=True):
            st.session_state.current_role = "merchant"
            st.session_state.agent = create_agent_with_llm(
                st.session_state.user_id,
                "merchant"
            )
            welcome_msg = ChatMessage(
                role="assistant",
                content=f"您好！我是商户管理助手 🏪（当前使用：**{mode_desc_merchant}**）\n\n您可以：\n- 查看各类订单（即时支付、委托支付、A2A支付）\n- 管理商品上架\n- 向用户推送通知\n\n输入\"查看订单\"开始管理吧！"
            )
            st.session_state.chat_messages.append(welcome_msg)
            st.rerun()


def render_sidebar():
    """渲染侧边栏"""
    # 当前角色显示
    role_display = "👤 用户" if st.session_state.current_role == "user" else "🏪 商户"
    st.markdown(f"### 当前角色：{role_display}")

    # 切换角色按钮
    if st.button("⇄ 切换角色", use_container_width=True):
        new_role = "merchant" if st.session_state.current_role == "user" else "user"
        st.session_state.current_role = new_role
        st.session_state.agent = create_agent_with_llm(
            st.session_state.user_id,
            new_role
        )
        st.session_state.chat_messages = []
        st.rerun()

    st.markdown("---")

    # 模型配置
    render_llm_config_sidebar()

    st.markdown("---")

    # 支付模式说明
    if st.session_state.current_role == "user":
        st.markdown("### 💡 快速提示")
        st.markdown("""
试试说：
- "买iPhone" → 即时支付
- "授权买咖啡，额度500元" → 委托支付
- "帮我安排出差，预算5000元" → A2A支付
        """)

    st.markdown("---")

    # 显示实时数据
    st.markdown("### 📊 实时数据")

    data = load_demo_data()

    # 提示数据持久化状态
    total_orders = len(data["orders"])
    if total_orders > 0:
        st.caption(f"💾 数据已持久化存储，共 {total_orders} 条历史订单")

    st.metric("商品数量", len(data["products"]))

    # 区分显示：当前用户订单 vs 总订单
    if st.session_state.current_role == "user":
        user_orders = [o for o in data["orders"] if o.get("user_id") == st.session_state.user_id and o.get("type") != "autonomous_task"]
        total_user_orders = len(user_orders)

        # 如果当前用户没有订单但系统有历史订单，显示提示
        if total_user_orders == 0 and total_orders > 0:
            st.info(f"ℹ️ 您是新用户，但系统有 {total_orders} 条其他用户的订单记录")

        st.metric("我的订单", total_user_orders, help=f"总订单数: {total_orders}")
    else:
        st.metric("总订单数", total_orders)

    if st.session_state.current_role == "user":
        user_delegations = [d for d in data["delegations"] if d.get("user_id") == st.session_state.user_id and d.get("status") == "active"]
        st.metric("有效委托", len(user_delegations))

    # 数据管理
    st.markdown("---")
    st.markdown("### 🔧 数据管理")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ 清空我的数据", use_container_width=True, help="清空当前用户的订单和委托"):
            data = load_demo_data()
            # 只删除当前用户的订单和委托
            data["orders"] = [o for o in data["orders"] if o.get("user_id") != st.session_state.user_id]
            data["delegations"] = [d for d in data["delegations"] if d.get("user_id") != st.session_state.user_id]
            # 删除当前用户的子账户
            for key in list(data.get("sub_accounts", {}).keys()):
                # 子账户没有user_id，需要关联task_id
                user_tasks = [o for o in data.get("orders", []) if o.get("user_id") == st.session_state.user_id and o.get("type") == "autonomous_task"]
                task_ids = [t.get("id") for t in user_tasks]
                if key in task_ids or any(t.get("sub_account_id") == key for t in user_tasks):
                    data["sub_accounts"].pop(key, None)
            save_demo_data(data)
            st.success("✅ 已清空您的数据")
            st.rerun()

    with col2:
        if st.button("🗑️ 清空全部数据", use_container_width=True, help="清空所有用户的订单、委托和商品"):
            # 重置为初始数据
            initial_data = {
                "products": [
                    {"id": "p1", "name": "iPhone 15 Pro", "price": 8999.0, "stock": 10, "merchant_id": "m1"},
                    {"id": "p2", "name": "MacBook Pro M3", "price": 14999.0, "stock": 5, "merchant_id": "m1"},
                    {"id": "p3", "name": "AirPods Pro 2", "price": 1899.0, "stock": 20, "merchant_id": "m1"},
                    {"id": "p4", "name": "星巴克大杯拿铁", "price": 38.0, "stock": 100, "merchant_id": "m2"},
                    {"id": "p5", "name": "奈雪的茶", "price": 32.0, "stock": 50, "merchant_id": "m2"},
                ],
                "orders": [],
                "delegations": [],
                "sub_accounts": {},
                "notifications": []
            }
            save_demo_data(initial_data)
            st.success("✅ 已重置所有数据")
            st.rerun()


def render_chat_interface():
    """渲染聊天界面 - 对话框固定在底部"""

    # 添加CSS样式，使聊天区域可滚动，输入框固定在底部
    st.markdown("""
    <style>
    .chat-history {
        max-height: calc(100vh - 250px);
        overflow-y: auto;
        padding-bottom: 20px;
    }
    .chat-input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        padding: 10px 20px;
        border-top: 1px solid #e0e0e0;
        z-index: 100;
    }
    .main-content {
        padding-bottom: 80px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 主内容区域
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # 聊天历史容器（可滚动）
    chat_container = st.container()
    chat_container.markdown('<div class="chat-history">', unsafe_allow_html=True)

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg.role):
            # 如果有协议标签，显示徽章
            if msg.metadata and msg.metadata.get("protocol"):
                protocol = msg.metadata["protocol"]
                badge_class = "instant-badge" if "INS" in protocol else ("delegated-badge" if "DEL" in protocol else "a2a-badge")
                st.markdown(f'<span class="protocol-badge {badge_class}">{protocol}</span>', unsafe_allow_html=True)

            # 如果使用了LLM，显示LLM标识
            if msg.metadata:
                if msg.metadata.get("llm_used"):
                    llm_intent = msg.metadata.get("llm_intent", "")
                    llm_confidence = msg.metadata.get("llm_confidence", 0)
                    st.markdown(f'<span style="font-size: 0.75rem; color: #1976d2; background: #e3f2fd; padding: 2px 6px; border-radius: 4px; margin-right: 4px;">🧠 LLM识别: {llm_intent} ({llm_confidence:.0%})</span>', unsafe_allow_html=True)

                # 如果回复内容也是LLM生成的，额外显示
                if msg.metadata.get("llm_generated"):
                    st.markdown(f'<span style="font-size: 0.75rem; color: #388e3c; background: #e8f5e9; padding: 2px 6px; border-radius: 4px;">✨ AI生成回复</span>', unsafe_allow_html=True)

            st.markdown(msg.content)

    chat_container.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 输入框固定在底部
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    if prompt := st.chat_input("请输入您的消息...", key="chat_input_bottom"):
        # 添加用户消息
        user_msg = ChatMessage(role="user", content=prompt)
        st.session_state.chat_messages.append(user_msg)

        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 处理消息并显示回复
        handle_user_input(prompt)

        # 重新渲染以更新聊天历史
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def handle_user_input(prompt: str):
    """处理用户输入"""
    agent = st.session_state.agent

    # 特殊命令处理
    prompt_lower = prompt.lower().strip()

    # 确认支付
    if prompt_lower in ["确认支付", "确认", "pay", "ok"]:
        if agent and agent.pending_action:
            with st.chat_message("assistant"):
                with st.spinner("正在处理..."):
                    response = agent.confirm_pending_action()
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
            return
        else:
            response = ChatMessage(role="assistant", content="没有待确认的操作。请告诉我您想做什么？")
            with st.chat_message("assistant"):
                st.markdown(response.content)
            st.session_state.chat_messages.append(response)
            return

    # 确认取消委托
    if prompt_lower in ["确认取消", "确认取消委托", "确定取消"]:
        if agent and agent.pending_action and agent.pending_action.get("type") == "cancel_delegation":
            with st.chat_message("assistant"):
                with st.spinner("正在取消委托..."):
                    response = agent.confirm_pending_action()
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
            return
        else:
            response = ChatMessage(role="assistant", content="没有待取消的委托。请告诉我您想做什么？")
            with st.chat_message("assistant"):
                st.markdown(response.content)
            st.session_state.chat_messages.append(response)
            return

    # 签发委托
    if prompt_lower in ["签发委托", "确认创建", "签发", "创建委托"]:
        if agent and agent.pending_action and agent.pending_action.get("type") == "delegated_payment_setup":
            with st.chat_message("assistant"):
                with st.spinner("正在签发IAC..."):
                    response = agent.confirm_pending_action()
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
            return

    # 处理A2A预算输入（当处于等待预算状态时）
    if agent and agent.pending_action and agent.pending_action.get("type") == "autonomous_payment_setup_pending_budget":
        budget = agent._parse_amount_from_message(prompt)
        if budget and budget > 0:
            # 有预算输入，创建任务
            task_id = f"did:act:task:{uuid.uuid4().hex[:16]}"
            task_desc = agent.pending_action.get("task_desc", "旅行任务")
            agent.pending_action = {
                "type": "autonomous_payment_setup",
                "task_id": task_id,
                "budget": budget,
                "description": task_desc
            }
            with st.chat_message("assistant"):
                with st.spinner("正在创建任务..."):
                    response = agent.confirm_pending_action()
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
                    # 保存任务ID用于后续执行
                    st.session_state["last_a2a_task_id"] = task_id
            return
        else:
            # 没有识别到预算，提示用户
            response = ChatMessage(
                role="assistant",
                content='请输入有效的预算金额，例如："预算5000元" 或 "10000块"'
            )
            with st.chat_message("assistant"):
                st.markdown(response.content)
            st.session_state.chat_messages.append(response)
            return

    # 创建自主任务（已有预算）
    if prompt_lower in ["确认创建任务", "创建任务", "开始任务"]:
        if agent and agent.pending_action and agent.pending_action.get("type") == "autonomous_payment_setup":
            # 获取任务ID用于保存
            task_id = agent.pending_action.get("task_id")
            with st.chat_message("assistant"):
                with st.spinner("正在创建任务..."):
                    response = agent.confirm_pending_action()
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
                    # 保存任务ID用于后续执行
                    if task_id:
                        st.session_state["last_a2a_task_id"] = task_id
            return

    # 开始执行A2A任务（首次执行 - 机票预订）
    if prompt_lower in ["开始执行", "开始执行任务", "执行任务"]:
        task_id = st.session_state.get("last_a2a_task_id")
        if agent:
            with st.chat_message("assistant"):
                with st.spinner("正在执行A2A机票预订任务..."):
                    response = agent.simulate_autonomous_execution(task_id, step="flight")
                    st.session_state["a2a_current_step"] = "hotel"  # 标记下一步是酒店
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
            return

    # 继续执行A2A任务（下一步子任务）
    if prompt_lower in ["继续执行", "下一步", "继续"]:
        current_step = st.session_state.get("a2a_current_step", "flight")
        task_id = st.session_state.get("last_a2a_task_id")
        if agent:
            with st.chat_message("assistant"):
                with st.spinner(f"正在执行子任务..."):
                    if current_step == "hotel":
                        response = agent.simulate_autonomous_execution(task_id, step="hotel")
                        st.session_state["a2a_current_step"] = "car"  # 下一步是用车
                    elif current_step == "car":
                        response = agent.simulate_autonomous_execution(task_id, step="car")
                        st.session_state["a2a_current_step"] = "complete"  # 任务完成
                    else:
                        response = ChatMessage(
                            role="assistant",
                            content="""
🎉 **A2A自主支付任务全部完成！**

**执行汇总**：
- ✅ 子任务1（机票）：¥800
- ✅ 子任务2（酒店）：¥1200
- ✅ 子任务3（用车）：¥300

**总计支出：¥2300**
**子账户剩余：¥2700**

所有支付均通过A2A协议自动完成，无需您逐笔介入。
                            """.strip()
                        )
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
            return

    # 取消操作
    if prompt_lower in ["取消", "cancel", "不", "不要"]:
        if agent:
            agent.pending_action = None
        response = ChatMessage(role="assistant", content="已取消操作。还有什么可以帮您的？")
        with st.chat_message("assistant"):
            st.markdown(response.content)
        st.session_state.chat_messages.append(response)
        return

    # 修改额度处理
    if prompt_lower.startswith("修改额度") or prompt_lower.startswith("修改预算"):
        new_amount = agent._parse_amount_from_message(prompt) if agent else None
        if new_amount and agent and agent.pending_action:
            action_type = agent.pending_action.get("type", "")
            if "max_total" in agent.pending_action:
                # 委托支付设置
                agent.pending_action["max_total"] = new_amount
                agent.pending_action["max_single"] = new_amount / 5
                response = ChatMessage(
                    role="assistant",
                    content=f"已修改为总额度 ¥{new_amount:.2f}，单笔上限 ¥{new_amount/5:.2f}。请回复\"签发委托\"继续。"
                )
            elif "budget" in agent.pending_action:
                # A2A自主支付任务设置
                agent.pending_action["budget"] = new_amount
                response = ChatMessage(
                    role="assistant",
                    content=f"已修改预算为 ¥{new_amount:.2f}。请回复\"确认创建任务\"继续。"
                )
            else:
                response = ChatMessage(role="assistant", content="无法修改，请重新创建。")
        else:
            response = ChatMessage(role="assistant", content="请输入有效的金额，例如：修改额度 1000 或 修改预算 3000")
        with st.chat_message("assistant"):
            st.markdown(response.content)
        st.session_state.chat_messages.append(response)
        return

    # 常规消息处理（包括使用委托购买等，现在都通过agent.process_message路由）
    if agent:
        with st.chat_message("assistant"):
            with st.spinner("智能体思考中..."):
                response = agent.process_message(prompt)
                st.markdown(response.content)

                # 如果是A2A任务创建，保存任务ID
                if response.metadata and response.metadata.get("autonomous_task_created"):
                    if agent.pending_action:
                        st.session_state["last_a2a_task_id"] = agent.pending_action.get("task_id")

        st.session_state.chat_messages.append(response)


if __name__ == "__main__":
    render_chat_based_demo()
