#!/bin/bash
# -*- coding: utf-8 -*-
# 简化的电商购物助手启动脚本

echo "🚀 启动电商购物助手"
echo "========================"

# 设置虚拟环境 Python 路径
VENV_PYTHON="./venv/bin/python"

# 检查虚拟环境是否存在
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo "📦 安装依赖..."
    ./install_deps.sh
fi

# 检查依赖
echo "🔍 检查依赖..."
if ! $VENV_PYTHON -c "import streamlit" 2>/dev/null; then
    echo "📥 缺少依赖，正在安装..."
    ./install_deps.sh
fi

# 启动应用
echo "🎯 启动应用..."
echo ""
echo "📍 访问地址: http://localhost:8501"
echo "📍 或者访问: http://127.0.0.1:8501"
echo ""
echo "💡 使用说明："
echo "1. 选择「规则模式」（推荐，无需 API Key）"
echo "2. 点击「🚀 初始化助理 Agent」"
echo "3. 开始对话测试"
echo ""
echo "⏹️  按 Ctrl+C 停止应用"
echo "========================"

# 启动 streamlit
$VENV_PYTHON -m streamlit run test_app.py --server.port 8501 --server.address 0.0.0.0