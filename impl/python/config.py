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