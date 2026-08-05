# 选择你的接入路径

> 状态：July Preview / Non-normative  
> 支付宝产品资料快照：2026-07-28

ACT 仓库负责解释协议语义、产品映射和验证边界；支付宝官网负责维护开户、钱包授权、沙箱、密钥、API 参数和当前产品操作步骤。

Agent 支付与 AI 按量付费是同一机器支付闭环的两侧能力，不是彼此孤立的产品流程：前者让买方 Agent 能够支付，后者让卖方服务能够接受和验证机器支付。两侧共同跨 ADD、CID、PSD、TSD 协作。协议开发者和需要判断组件边界的实现者应先查看[双侧能力与 ACT 四域映射](../../profiles/alipay-ai-pay/mappings/domains.md)。

## 你属于哪一类开发者？

| 你的目标 | 接入路径 | 主要角色 | 从这里开始 |
|---|---|---|---|
| 让 Agent 代表用户完成支付 | Agent 支付 | 买方 Agent / Agent 开发者 | [Agent 支付 Getting Started](agent-payment.md) |
| 让 API、MCP Tool 或 Skill 按调用收费 | AI 按量付费 | 付费资源提供方 | [AI 按量付费 Getting Started](metered-payment.md) |
| 同时验证买方支付与卖方收费 | HTTP 402 闭环 | Agent + 资源提供方 | [端到端 402 验证](end-to-end-402.md) |
| 实现 ACT 或支付宝 Profile | 协议/Profile 实现 | 协议开发者 | [Alipay AI Pay Profile](../../profiles/alipay-ai-pay/README.md) |

## 从双侧能力进入四域

| 能力侧 | ADD | CID | PSD | TSD |
|---|---|---|---|---|
| 买方 Agent 支付能力 | 当前支付意图；未来委托授权 | 理解商品、订单和卖方支付能力 | 钱包绑定、支付执行和凭证获取 | 产生并关联意图与支付证据 |
| 卖方机器支付能力 | 消费买方授权上下文 | 发布收费资源、价格、订单和支付能力 | 402 出账、凭证验证与履约确认 | 产生并关联支付与履约证据 |

详细组件级映射和首期/后续边界见[双侧能力与 ACT 四域映射](../../profiles/alipay-ai-pay/mappings/domains.md)。

## 两侧能力如何协作？

```text
卖方机器支付能力：发布收费资源并返回机器可读的付费要求
  → 买方 Agent 支付能力：理解要求、获得授权、执行支付
  → 买方 Agent：携带支付凭证重试原请求
  → 卖方机器支付能力：验证凭证、交付资源、确认履约
```

在大会版本中：

- Agent 支付以支付宝官方 Skill/CLI 为公开基线。
- AI 按量付费以支付宝官网 HTTP 402 方案为公开基线。
- 单独安装支付 Skill 只证明 Agent 获得买方支付能力；单独实现 402 只证明卖方具备机器收款能力。端到端声明必须验证两侧能够互通。
- MCP Tool 和 Skill 可以作为收费资源形态复用 402 链路；当前不声明独立的原生 MCP 支付 Binding。
- ACT Core 仍在修订，当前文档不构成最终协议字段或兼容性承诺。

两侧最小责任、关联标识和分级验收口径见[双侧能力接入契约 v0.1](../../profiles/alipay-ai-pay/capabilities/end-to-end-contract.md)。

准备真实验证时使用[端到端证据模板](end-to-end-evidence-template.md)，确保版本、关联标识、异常和双侧履约证据可复核。

## 可运行入口

| 路径 | 本仓库可运行资产 | 外部真实步骤 |
|---|---|---|
| 本地安全预览 | [Non-payable A402 Golden Path](../../quickstarts/alipay/end-to-end-402/README.md#0-先跑本地非支付闭环) | 无；只检查挑战结构和拒绝假 Proof |
| 买方 Agent | [Agent Payment Quickstart](../../quickstarts/alipay/agent-payment/README.md) | 安装官方 Skill/CLI 并完成用户授权 |
| 卖方服务 | [Metered REST Provider Quickstart](../../quickstarts/alipay/metered-rest-provider/README.md) | 配置支付宝 Sandbox 应用、服务和密钥 |
| 双侧闭环 | [End-to-end 402 Quickstart](../../quickstarts/alipay/end-to-end-402/README.md) | 执行一笔真实授权的 Sandbox 支付并保存脱敏证据 |

## 不属于首期范围

- AI 订阅付费。
- 移动应用或网页应用的普通收款。
- 尚未公开的 Agent Platform SDK 或智能硬件 SDK。
- L2/L3 长期额度和完全自主授权。
- 多支付渠道互操作实现。

其他支付宝 AI 付产品请从[官方产品概览](https://aipay.alipay.com/docs/overview.html)选择，不应套用本目录中的支付路径。

## 阅读原则

每份 Getting Started 都分为三类内容：

| 标识 | 含义 |
|---|---|
| 支付宝官方步骤 | 跳转官网执行，以官网当前页面为准 |
| ACT 接入责任 | 解释实现需要保留的协议语义和安全边界 |
| 验收证据 | 判断是否真正连接产品，而不是运行 Mock |

如果本仓库与支付宝官网的产品操作发生冲突，以官网和支付宝开放平台当前文档为产品事实源，并在 [Profile 官方资料表](../../profiles/alipay-ai-pay/sources/README.md)登记变化。
