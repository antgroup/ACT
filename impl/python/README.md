# 🛒 电商购物助手 - Agentscope Multi-Agent MVP

基于 [Agentscope](https://github.com/agentscope-ai/agentscope) 框架开发的电商场景 Multi-Agent 系统演示项目。

## 📋 项目简介

这是一个具备"函数调用 (Function Calling)"能力的 Multi-Agent 系统，包含**四个独立模块**：

- **🖥️ 用户界面 (ui/)**：Streamlit Web UI，提供聊天交互界面
- **🤖 助理 Agent (assistant_agent/)**：唯一的 Agent，负责对话和协调
- **🏪 商户服务 (merchant_service/)**：独立服务模块，管理商品和订单
- **💳 支付服务 (payment_service/)**：独立服务模块，处理支付流程

用户通过 Web 界面与助理 Agent 对话，Agent 协调商户服务和支付服务完成购物流程。

## 🚀 快速开始

### � 安装

#### 1. 克隆项目
```bash
git clone <项目地址>
cd  <本地项目地址>
```

#### 2. 安装依赖

**方案一：使用启动脚本（推荐）**
```bash
./run.sh
```

**方案二：手动安装**
```bash
# 基础依赖
pip install streamlit==1.29.0 openai>=1.0.0 python-dotenv==1.0.0

# Agentscope 安装（如果 pip 失败，使用 GitHub 安装）
pip install git+https://github.com/agentscope-ai/agentscope.git
```

**方案三：无 agentscope 运行**
```bash
# 只安装基础依赖，使用规则模式
pip install streamlit==1.29.0 openai>=1.0.0 python-dotenv==1.0.0
```

#### 3. 启动应用

```bash
# 方式一：使用启动脚本
./run.sh

# 方式二：直接启动
  streamlit run ui/app.py
  
# 方式三：使用主入口
python main.py
```

### 完整启动流程
````
1. 进入项目目录
cd <项目空间>/impl/python

2. 创建虚拟环境
python3 -m venv .venv

3. 激活虚拟环境
source .venv/bin/activate

4. 安装依赖
pip install -r requirements.txt

5. 启动应用
streamlit run ui/app.py

应用将自动在浏览器中打开：http://localhost:8501
````

### 🎯 使用流程

1. **启动应用** → 浏览器自动打开 `http://localhost:8501`
2. **选择模式** → 规则模式（无需 API Key）或 LLM 模式
3. **初始化 Agent** → 点击「初始化助理 Agent」按钮
4. **开始对话** → 查看商品、下单、支付

## 📁 项目结构

```
ace_demo/
│
├── 🖥️ ui/                          # 用户界面模块
│   ├── __init__.py
│   └── app.py                      # Streamlit Web UI
│
├── 🤖 assistant_agent/             # 助理 Agent 模块
│   ├── __init__.py
│   └── agent.py                    # Agent 实现
│
├── 🏪 merchant_service/            # 商户服务模块
│   ├── __init__.py
│   └── service.py                  # 商品和订单管理
│
├── 💳 payment_service/             # 支付服务模块
│   ├── __init__.py
│   └── service.py                  # 支付处理
│
├── 📚 文档和配置
│   ├── README.md                   # 项目说明
│   ├── INSTALLATION_GUIDE.md       # 安装指南
│   ├── ARCHITECTURE.md             # 架构详解
│   ├── PROJECT_STRUCTURE.md        # 结构说明
│   ├── PROJECT_SUMMARY.md          # 项目总结
│   ├── COMPLETION_SUMMARY.md       # 完成总结
│   ├── requirements.txt            # 依赖包
│   ├── config.py                   # 配置管理
│   ├── .env.example                # 环境变量模板
│   ├── .gitignore                  # Git 忽略规则
│   ├── main.py                     # 主入口
│   └── run.sh                      # 启动脚本
```

## 💡 使用示例

### 1️⃣ 查看商品
```
用户：看看有什么商品
助理：📦 当前可售商品列表...
      🔹 Apple - 商品ID: P001, 价格: ¥5.99
      🔹 Banana - 商品ID: P002, 价格: ¥3.99
      🔹 Orange - 商品ID: P003, 价格: ¥4.99
      🔹 Grape - 商品ID: P004, 价格: ¥8.99
```

### 2️⃣ 购买商品
```
用户：我要买 P001
助理：✅ 订单创建成功！
      📋 订单详情：
         订单号: ORD12345678
         商品: Apple
         总金额: ¥5.99
```

### 3️⃣ 支付订单
```
用户：支付
助理：💰 支付成功！
      💳 支付详情：
         支付流水号: PAY1234567890
         支付金额: ¥5.99
```

## 🛠️ 技术栈

- **Agent 框架**：Agentscope（可选，支持规则模式）
- **UI 框架**：Streamlit 1.29.0
- **语言模型**：
  - OpenAI GPT-3.5/GPT-4（可选）
  - **阿里云 DashScope** - 通义千问、DeepSeek 等（推荐）
- **Python 版本**：3.9+

## 🤖 模型配置

### 支持的模型提供商

| 提供商 | 模型 | 推荐场景 |
|--------|------|----------|
| **DashScope** | `qwen-turbo` | 快速响应，低成本 |
| **DashScope** | `qwen-plus` | 均衡性能 |
| **DashScope** | `qwen-max` | 复杂推理 |
| **DashScope** | `deepseek-r1` | 逻辑推理 |
| OpenAI | `gpt-3.5-turbo` | OpenAI 服务 |
| OpenAI | `gpt-4` | 高精度任务 |

### 快速配置 DashScope (阿里系模型)

```bash
# 1. 获取 API Key
# 访问 https://dashscope.console.aliyun.com/api-key

# 2. 设置环境变量
export DASHSCOPE_API_KEY=sk-your-dashscope-api-key
export MODEL_PROVIDER=dashscope
export DASHSCOPE_MODEL=qwen-turbo

# 3. 安装依赖
pip install dashscope>=1.19.0

# 4. 运行应用
streamlit run ui/app.py
```

### 配置文件

复制 `.env.example` 为 `.env`，填写你的 API Key：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 API Key
```

### 快速测试

```python
from assistant_agent.agent import create_assistant_agent

# 使用 DashScope (通义千问)
agent = create_assistant_agent(
    api_key="sk-your-dashscope-key",
    model="qwen-turbo",
    provider="dashscope"
)

# 使用 OpenAI
agent = create_assistant_agent(
    api_key="sk-your-openai-key",
    provider="openai"
)

# 测试对话
print(agent.chat("你好，有什么商品？"))
```

## 🎯 项目特色

- **四个独立模块**：每个模块职责明确
- **开箱即用**：复制代码即可运行
- **双模式支持**：规则模式（无需 API Key）+ LLM 模式
- **完整文档**：详细的说明和注释
- **易于扩展**：可以轻松添加新模块

## 📖 相关文档

- [`INSTALLATION_GUIDE.md`](INSTALLATION_GUIDE.md) - 详细安装指南
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - 系统架构详解
- [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) - 项目结构说明
- [`PROJECT_SUMMARY.md`](PROJECT_SUMMARY.md) - 项目总结

## 🎊 项目完成！

✅ **四个独立模块**已创建完成
✅ **职责清晰分离**已实现
✅ **完整文档**已提供
✅ **多种启动方式**已支持

**启动命令**：
```bash
./run.sh
# 或
streamlit run ui/app.py
```

项目已完全准备好，可以直接运行！