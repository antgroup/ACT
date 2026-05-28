"""
助理 Agent 模块
负责与用户对话，协调商户服务和支付服务
"""
from typing import Dict, Any
import re
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 尝试导入agentscope（可选）
try:
    import agentscope
    from agentscope.agents import DialogAgent
    from agentscope.message import Msg
    HAS_AGENTSCOPE = True
except ImportError:
    HAS_AGENTSCOPE = False

# 导入独立的服务模块
from merchant_service.service import merchant_service
from payment_service.service import PaymentService


class AssistantAgent:
    """
    电商助理 Agent
    职责：
    1. 理解用户意图
    2. 调用商户服务查询商品、创建订单
    3. 调用支付服务处理支付
    4. 将结果友好地呈现给用户
    """

    def __init__(self, model_config: Dict[str, Any] = None):
        """
        初始化助理 Agent

        Args:
            model_config: 模型配置（可选，如果不提供则使用简化模式）
        """
        self.name = "小购助手"
        self.use_llm = model_config is not None

        # 初始化服务连接
        self.merchant_service = merchant_service
        self.payment_service = PaymentService(merchant_service)

        # 对话上下文
        self.conversation_history = []
        self.current_order_id = None
        self.current_order_amount = None

        if self.use_llm:
            # 使用 LLM 模式
            self._init_llm_agent(model_config)

        print(f"[助理Agent] {self.name} 初始化完成，模式: {'LLM' if self.use_llm else '规则'}")

    def _init_llm_agent(self, model_config: Dict[str, Any]):
        """初始化 LLM Agent"""
        if not HAS_AGENTSCOPE:
            raise ImportError("agentscope 未安装，无法使用 LLM 模式。请使用规则模式或安装 agentscope：pip install agentscope")

        # 初始化 Agentscope
        agentscope.init(
            model_configs=model_config,
            project="ecommerce_assistant",
            save_code=False,
            save_api_invoke=False,
            use_monitor=False
        )

        # 定义系统提示词
        system_prompt = """你是一个专业的电商购物助手，名字叫"小购"。

你的职责：
1. 帮助用户查询商品信息
2. 协助用户创建订单
3. 处理订单支付

你可以调用以下服务：

【商户服务】
- 查询商品列表
- 根据商品ID创建订单
- 查询订单状态

【支付服务】
- 处理订单支付
- 查询支付记录

工作流程：
1. 用户询问商品 -> 调用商户服务获取商品列表
2. 用户购买商品 -> 调用商户服务创建订单
3. 用户支付订单 -> 调用支付服务处理支付

注意事项：
- 始终保持友好和专业
- 清晰展示商品信息（ID、名称、价格、库存）
- 下单前确认用户意图
- 支付时验证金额
- 用中文交流

请根据用户需求，智能地协调各个服务完成任务。"""

        # 创建 DialogAgent
        self.llm_agent = DialogAgent(
            name="AssistantAgent",
            sys_prompt=system_prompt,
            model_config_name=model_config["config_name"],
            use_memory=True
        )

    def chat(self, user_input: str) -> str:
        """
        处理用户输入

        Args:
            user_input: 用户输入的文本

        Returns:
            str: Agent 的响应
        """
        if self.use_llm:
            return self._chat_with_llm(user_input)
        else:
            return self._chat_with_rules(user_input)

    def _chat_with_llm(self, user_input: str) -> str:
        """使用 LLM 处理对话"""
        try:
            # 创建用户消息
            user_msg = Msg(
                name="User",
                content=user_input,
                role="user"
            )

            # Agent 处理
            response = self.llm_agent(user_msg)

            # 提取响应内容
            if isinstance(response, Msg):
                return response.content
            elif isinstance(response, dict):
                return response.get("content", str(response))
            else:
                return str(response)

        except Exception as e:
            return f"抱歉，处理您的请求时出现错误: {str(e)}"

    def _chat_with_rules(self, user_input: str) -> str:
        """使用规则处理对话（简化模式）"""
        user_input_lower = user_input.lower()

        # 规则1: 查询商品
        if any(keyword in user_input_lower for keyword in ["商品", "产品", "有什么", "买什么", "看看", "列表", "货"]):
            return self._handle_product_query()

        # 规则2: 下单
        elif any(keyword in user_input_lower for keyword in ["买", "购买", "下单", "要"]):
            return self._handle_create_order(user_input)

        # 规则3: 支付
        elif any(keyword in user_input_lower for keyword in ["支付", "付款", "付钱", "pay"]):
            return self._handle_payment()

        # 规则4: 查询订单
        elif "订单" in user_input_lower and any(keyword in user_input_lower for keyword in ["查询", "查看", "状态"]):
            return self._handle_order_query(user_input)

        # 默认响应
        else:
            return self._get_welcome_message()

    def _handle_product_query(self) -> str:
        """处理商品查询"""
        print(f"[助理Agent] 调用商户服务 -> 查询商品列表")

        result = self.merchant_service.get_product_list()

        if not result["success"]:
            return f"❌ 抱歉，{result['message']}"

        products = result["data"]
        response = "📦 **当前可售商品列表**\n\n"

        for product in products:
            response += f"🔹 **{product['name']}**\n"
            response += f"   • 商品ID: `{product['item_id']}`\n"
            response += f"   • 价格: ¥{product['price']}\n"
            response += f"   • 库存: {product['stock']} 件\n"
            response += f"   • 描述: {product['description']}\n\n"

        response += "💡 您想购买哪个商品呢？请告诉我商品ID和数量（例如：我要买 P001）"

        return response

    def _handle_create_order(self, user_input: str) -> str:
        """处理创建订单"""
        # 提取商品ID和数量
        item_match = re.search(r'p\d{3}', user_input.lower())
        quantity_match = re.search(r'(\d+)\s*个', user_input)

        if not item_match:
            return "请告诉我您想购买的商品ID（例如：P001）和数量。\n\n💡 提示：先说「看看商品」查看商品列表"

        item_id = item_match.group(0).upper()
        quantity = int(quantity_match.group(1)) if quantity_match else 1

        print(f"[助理Agent] 调用商户服务 -> 创建订单: {item_id} x {quantity}")

        result = self.merchant_service.create_order(item_id, quantity)

        if not result["success"]:
            return f"❌ 下单失败：{result['message']}"

        order = result["data"]
        self.current_order_id = order["order_id"]
        self.current_order_amount = order["total_amount"]

        response = f"✅ **订单创建成功！**\n\n"
        response += f"📋 **订单详情**\n"
        response += f"   • 订单号: `{order['order_id']}`\n"
        response += f"   • 商品: {order['product_name']}\n"
        response += f"   • 数量: {order['quantity']} 件\n"
        response += f"   • 单价: ¥{order['unit_price']}\n"
        response += f"   • 总金额: **¥{order['total_amount']:.2f}**\n"
        response += f"   • 状态: 待支付\n\n"
        response += f"💰 请问您要支付这个订单吗？（说「支付」即可）"

        return response

    def _handle_payment(self) -> str:
        """处理支付"""
        if not self.current_order_id:
            return "❌ 您还没有待支付的订单。\n\n💡 请先选择商品下单（说「看看商品」查看商品列表）"

        print(f"[助理Agent] 调用支付服务 -> 支付订单: {self.current_order_id}")

        result = self.payment_service.process_payment(
            order_id=self.current_order_id,
            amount=self.current_order_amount
        )

        if not result["success"]:
            return f"❌ 支付失败：{result['message']}"

        payment = result["data"]

        response = f"💰 **支付成功！**\n\n"
        response += f"💳 **支付详情**\n"
        response += f"   • 支付流水号: `{payment['payment_id']}`\n"
        response += f"   • 订单号: `{payment['order_id']}`\n"
        response += f"   • 支付金额: ¥{payment['amount']:.2f}\n"
        response += f"   • 支付方式: {payment['payment_method']}\n"
        response += f"   • 支付状态: ✅ 成功\n\n"
        response += f"🎉 感谢您的购买！还需要其他帮助吗？"

        # 清空当前订单
        self.current_order_id = None
        self.current_order_amount = None

        return response

    def _handle_order_query(self, user_input: str) -> str:
        """处理订单查询"""
        # 提取订单ID
        order_match = re.search(r'ord\d{8}', user_input.lower())

        if order_match:
            order_id = order_match.group(0).upper()
        elif self.current_order_id:
            order_id = self.current_order_id
        else:
            return "请提供订单号（例如：查询订单 ORD12345678）"

        print(f"[助理Agent] 调用商户服务 -> 查询订单: {order_id}")

        result = self.merchant_service.get_order(order_id)

        if not result["success"]:
            return f"❌ {result['message']}"

        order = result["data"]

        status_map = {
            "pending_payment": "⏳ 待支付",
            "paid": "✅ 已支付",
            "cancelled": "❌ 已取消",
            "refunded": "↩️ 已退款"
        }

        response = f"📋 **订单详情**\n\n"
        response += f"   • 订单号: `{order['order_id']}`\n"
        response += f"   • 商品: {order['product_name']}\n"
        response += f"   • 数量: {order['quantity']} 件\n"
        response += f"   • 总金额: ¥{order['total_amount']:.2f}\n"
        response += f"   • 订单状态: {status_map.get(order['status'], order['status'])}\n"

        if "payment_id" in order:
            response += f"   • 支付流水号: `{order['payment_id']}`\n"

        return response

    def _get_welcome_message(self) -> str:
        """获取欢迎消息"""
        return """👋 您好！我是**小购**，您的电商购物助手。

我可以帮您：
1. 📦 **查看商品** - 说「看看商品」或「有什么产品」
2. 🛒 **购买商品** - 说「我要买 P001」或「购买 P002 2个」
3. 💰 **支付订单** - 下单后说「支付」或「付款」
4. 📋 **查询订单** - 说「查询订单 ORD12345678」

**模块说明：**
- 🤖 **我（助理Agent）**：负责理解您的需求，协调各个服务
- 🏪 **商户服务**：管理商品和订单
- 💳 **支付服务**：处理支付流程

请问您需要什么帮助？"""

    def reset(self):
        """重置对话状态"""
        self.conversation_history = []
        self.current_order_id = None
        self.current_order_amount = None

        if self.use_llm and hasattr(self, 'llm_agent'):
            if hasattr(self.llm_agent, 'memory'):
                self.llm_agent.memory.clear()

        print(f"[助理Agent] 对话状态已重置")


def create_assistant_agent(
    api_key: str = None,
    model: str = None,
    base_url: str = None,
    provider: str = "openai"
) -> AssistantAgent:
    """
    创建助理 Agent 实例

    支持两种模型提供商：
    - openai: OpenAI / Azure OpenAI / 兼容 OpenAI 接口的服务
    - dashscope: 阿里云 DashScope (通义千问、DeepSeek 等)

    Args:
        api_key: API Key（可选，不提供则使用规则模式）
        model: 模型名称（可选，默认使用配置中的模型）
        base_url: API 基础URL（可选）
        provider: 模型提供商 ("openai" | "dashscope")

    Returns:
        AssistantAgent: 助理 Agent 实例

    使用示例：
        # OpenAI 模式
        agent = create_assistant_agent(
            api_key="sk-xxxx",
            provider="openai"
        )

        # DashScope (阿里系模型)
        agent = create_assistant_agent(
            api_key="sk-xxxx",
            model="qwen-turbo",
            provider="dashscope"
        )
    """
    if not api_key:
        # 使用规则模式
        return AssistantAgent()

    if provider == "dashscope":
        # DashScope 模式 (阿里系模型)
        return _create_dashscope_agent(api_key, model)
    else:
        # OpenAI 模式
        return _create_openai_agent(api_key, model, base_url)


def _create_openai_agent(api_key: str, model: str = None, base_url: str = None) -> AssistantAgent:
    """创建 OpenAI 模式的 Agent"""
    # 导入配置中的默认值
    try:
        from config import OPENAI_MODEL
        default_model = OPENAI_MODEL
    except ImportError:
        default_model = "gpt-3.5-turbo"

    # 使用 LLM 模式
    model_config = {
        "config_name": "ecommerce_model",
        "model_type": "openai_chat",
        "model_name": model or default_model,
        "api_key": api_key,
        "organization": None,
        "client_args": {}
    }

    if base_url:
        model_config["client_args"]["base_url"] = base_url

    print(f"[助理Agent] 使用 OpenAI 模型: {model_config['model_name']}")
    return AssistantAgent(model_config=[model_config])


def _create_dashscope_agent(api_key: str, model: str = None) -> AssistantAgent:
    """创建 DashScope (阿里系模型) 模式的 Agent"""
    # 导入配置中的默认值
    try:
        from config import DASHSCOPE_MODEL
        default_model = DASHSCOPE_MODEL
    except ImportError:
        default_model = "qwen-turbo"

    try:
        import dashscope
        dashscope.api_key = api_key
    except ImportError:
        raise ImportError(
            "dashscope 未安装，无法使用阿里系模型。\n"
            "请安装：pip install dashscope>=1.19.0"
        )

    # DashScope 通过 agentscope 的 openai_chat 类型配置
    # 因为 DashScope 提供 OpenAI 兼容接口
    model_name = model or default_model
    model_config = {
        "config_name": "dashscope_model",
        "model_type": "openai_chat",
        "model_name": model_name,
        "api_key": api_key,
        "client_args": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
        }
    }

    print(f"[助理Agent] 使用 DashScope 模型: {model_name}")
    print(f"[助理Agent] 模型说明: {get_dashscope_model_desc(model_name)}")
    return AssistantAgent(model_config=[model_config])


def get_dashscope_model_desc(model: str) -> str:
    """获取 DashScope 模型描述"""
    descriptions = {
        "qwen-turbo": "通义千问 Turbo - 速度快、成本低，适合大多数场景",
        "qwen-plus": "通义千问 Plus - 性能均衡，复杂任务表现更好",
        "qwen-max": "通义千问 Max - 最强能力版，处理复杂推理",
        "qwen-long": "通义千问 Long - 长文本专用，支持百万 token",
        "qwen-coder-plus": "通义千问 Coder - 专为编码优化",
        "qwen-math-plus": "通义千问 Math - 数学和逻辑推理",
        "deepseek-r1": "DeepSeek R1 - 开源推理模型，逻辑能力强",
        "deepseek-v3": "DeepSeek V3 - 开源通用模型，性价比高"
    }
    return descriptions.get(model, f"DashScope 模型: {model}")


# 保持旧函数兼容
def create_assistant_agent_legacy(api_key: str = None, model: str = "gpt-3.5-turbo", base_url: str = None) -> AssistantAgent:
    """
    创建助理 Agent 实例 (兼容旧版本)

    Args:
        api_key: OpenAI API Key（可选，不提供则使用规则模式）
        model: 模型名称
        base_url: API 基础URL

    Returns:
        AssistantAgent: 助理 Agent 实例
    """
    return create_assistant_agent(api_key=api_key, model=model, base_url=base_url, provider="openai")
