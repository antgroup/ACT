# Python 交互 Demo

> [!WARNING]
> 本目录是用于展示 ACT 业务概念的本地模拟 Demo，不是 ACT 的完整参考实现，也不是支付宝 AI 付的实际接入代码。支付、账户、JWT、签名和部分服务结果使用 Mock；请勿用于真实资金交易或生产系统。

## Demo 展示内容

- 本地商品、购物车和订单交互。
- 即时支付、委托支付和自主支付的概念差异。
- 可选的规则模式、DashScope 或 OpenAI 对话体验。
- 面向协议讨论的示意性状态和载荷。

本 Demo 不会：

- 开通或绑定支付宝 AI 钱包。
- 调用支付宝官方 Payment Skill/CLI。
- 生成真实 `Payment-Needed` 或 `Payment-Proof`。
- 调用支付宝支付验证或履约确认 API。
- 执行真实扣款、退款或资金结算。

真实产品接入请从以下资料开始：

- [ACT Agent Payment alignment](../../profiles/alipay-ai-pay/agent-payment-alignment.md)
- [ACT Metered Payment alignment](../../profiles/alipay-ai-pay/metered-payment-alignment.md)
- [支付宝 AI 钱包使用指南](https://aipay.alipay.com/wallet-guide)
- [支付宝 AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)

## 运行环境

- Python 3.9+
- 依赖见 `requirements.txt`

建议使用虚拟环境：

```bash
cd impl/python
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

启动主要界面：

```bash
streamlit run ui/app.py
```

启动对话式 Demo：

```bash
streamlit run chat_based_demo.py
```

模型 API Key 只影响对话体验；不配置时可以使用本地规则或 Mock 模式。不要提交 `.env`、API Key 或其他凭证。

## 目录说明

| 目录/文件 | 作用 | 边界 |
|---|---|---|
| `ui/` | Streamlit 页面 | 演示界面 |
| `assistant_agent/` | 对话与流程协调 | 可使用规则或模型 |
| `merchant_service/` | 本地商品和订单数据 | 模拟商户服务 |
| `market_service/` | 本地市场与任务数据 | 模拟市场服务 |
| `payment_service/` | 支付流程演示 | 模拟支付，不连接 PSP |
| `psd/delegated_payment/` | 委托支付概念代码 | 包含 Mock JWT、Mock 账户和 Mock 扣款 |
| `chat_based_demo.py` | 对话式体验 | 包含大量模拟数据与结果 |

## 已知限制

- 组件名称和消息字段可能随 ACT 修订变化。
- Demo 测试文件以流程演示为主，尚未构成协议一致性测试。
- 依赖版本尚未锁定，安装结果可能受上游版本影响。
- 本地状态不能作为支付结果、授权凭证或履约证明。

问题和改造计划见[仓库审计](../../docs/open-source-restructure/07-repository-audit.md)。
