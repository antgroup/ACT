"""
配置文件
存储项目的全局配置
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# OpenAI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)

# 阿里 DashScope 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_MODEL = os.getenv("DASHSCOPE_MODEL", "qwen-turbo")
# 可选模型：
# - qwen-turbo: 通义千问 Turbo，速度快、成本低
# - qwen-plus: 通义千问 Plus，能力强
# - qwen-max: 通义千问 Max，最强能力
# - deepseek-r1: DeepSeek R1 推理模型
# - deepseek-v3: DeepSeek V3 通用模型

# 模型提供商选择 (openai | dashscope)
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")

# Agent 配置
AGENT_NAME = "EcommerceAssistant"
AGENT_DESCRIPTION = "电商购物助手"

# 应用配置
APP_TITLE = "电商购物助手"
APP_ICON = "🛒"
APP_LAYOUT = "centered"

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "ecommerce_agent.log"