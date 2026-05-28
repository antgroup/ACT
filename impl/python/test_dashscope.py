#!/usr/bin/env python3
"""
DashScope (阿里系模型) 接入测试脚本

使用方法:
    1. 确保已安装依赖: pip install dashscope>=1.19.0
    2. 设置环境变量: export DASHSCOPE_API_KEY=sk-your-key
    3. 运行测试: python test_dashscope.py
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DASHSCOPE_API_KEY
from assistant_agent.agent import create_assistant_agent, get_dashscope_model_desc


def test_models():
    """测试可用的 DashScope 模型"""

    # 测试的模型列表
    models_to_test = [
        "qwen-turbo",
        "qwen-plus",
        "deepseek-r1",
    ]

    print("=" * 60)
    print("DashScope (阿里系模型) 接入测试")
    print("=" * 60)

    # 检查 API Key
    if not DASHSCOPE_API_KEY:
        print("\n❌ 错误: 未设置 DASHSCOPE_API_KEY")
        print("请设置环境变量: export DASHSCOPE_API_KEY=sk-your-key")
        return

    print(f"\n📝 当前 API Key: {DASHSCOPE_API_KEY[:10]}...{DASHSCOPE_API_KEY[-4:]}")
    print("\n" + "-" * 60)

    for model in models_to_test:
        print(f"\n🔍 测试模型: {model}")
        print(f"   说明: {get_dashscope_model_desc(model)}")

        try:
            # 创建 Agent
            agent = create_assistant_agent(
                api_key=DASHSCOPE_API_KEY,
                model=model,
                provider="dashscope"
            )

            # 测试对话
            test_message = "你好！请简单介绍一下自己。"
            print(f"\n   用户: {test_message}")

            response = agent.chat(test_message)
            print(f"   助理: {response[:100]}...")  # 只显示前100字符

            print(f"   ✅ {model} 测试通过")

        except Exception as e:
            print(f"   ❌ {model} 测试失败: {str(e)}")

        print("-" * 60)


def interactive_demo():
    """交互式演示"""
    print("\n" + "=" * 60)
    print("交互式演示")
    print("=" * 60)

    if not DASHSCOPE_API_KEY:
        print("\n❌ 未设置 DASHSCOPE_API_KEY")
        return

    # 使用推荐的模型
    model = "qwen-turbo"
    print(f"\n使用模型: {model}")
    print(f"说明: {get_dashscope_model_desc(model)}")
    print("\n输入 'quit' 退出\n")

    agent = create_assistant_agent(
        api_key=DASHSCOPE_API_KEY,
        model=model,
        provider="dashscope"
    )

    while True:
        user_input = input("\n用户: ").strip()

        if user_input.lower() in ['quit', 'exit', '退出']:
            print("再见！")
            break

        if not user_input:
            continue

        print("助理: ", end="")
        try:
            response = agent.chat(user_input)
            print(response)
        except Exception as e:
            print(f"错误: {str(e)}")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        test_models()
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        print("\n提示: 运行交互式演示请使用:")
        print("  python test_dashscope.py --interactive")


if __name__ == "__main__":
    main()
