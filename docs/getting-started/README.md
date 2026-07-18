# 选择你的接入路径

> 状态：July Preview / Non-normative  
> 支付宝产品资料快照：2026-07-16

ACT 仓库负责解释协议语义、产品映射和验证边界；支付宝官网负责维护开户、钱包授权、沙箱、密钥、API 参数和当前产品操作步骤。

两个产品都不是单独的 ACT 域，而是跨 ADD、CID、PSD、TSD 组合实现。协议开发者和需要判断组件边界的实现者应先查看[产品与 ACT 四域映射](../../profiles/alipay-ai-pay/domain-mapping.md)。

## 你属于哪一类开发者？

| 你的目标 | 接入路径 | 主要角色 | 从这里开始 |
|---|---|---|---|
| 让 Agent 代表用户完成支付 | Agent 支付 | 买方 Agent / Agent 开发者 | [Agent 支付 Getting Started](agent-payment.md) |
| 让 API、MCP Tool 或 Skill 按调用收费 | AI 按量付费 | 付费资源提供方 | [AI 按量付费 Getting Started](metered-payment.md) |
| 同时验证买方支付与卖方收费 | HTTP 402 闭环 | Agent + 资源提供方 | [端到端 402 验证](end-to-end-402.md) |
| 实现 ACT 或支付宝 Profile | 协议/Profile 实现 | 协议开发者 | [Alipay AI Pay Profile](../../profiles/alipay-ai-pay/README.md) |

## 从产品路径进入四域

| 产品路径 | ADD | CID | PSD | TSD |
|---|---|---|---|---|
| Agent 支付 | 当前支付意图；未来委托授权 | 商品、订单和支付方式上下文 | 钱包绑定与用户确认支付 | 关联意图、订单、支付和履约证据 |
| AI 按量付费 | 消费买方授权上下文 | 收费资源、价格、订单和支付能力 | 402、支付凭证、验款与履约确认 | 支付完成和资源履约事件 |

详细组件级映射和首期/后续边界见[产品与 ACT 四域映射](../../profiles/alipay-ai-pay/domain-mapping.md)。

## 两个产品如何组合？

```text
Agent 支付（买方）
  → 识别付费要求
  → 获取用户授权并支付
  → 携带支付凭证重试

AI 按量付费（卖方）
  → 返回付费要求
  → 验证支付凭证
  → 返回资源并确认履约
```

在大会版本中：

- Agent 支付以支付宝官方 Skill/CLI 为公开基线。
- AI 按量付费以支付宝官网 HTTP 402 方案为公开基线。
- MCP Tool 和 Skill 可以作为收费资源形态复用 402 链路；当前不声明独立的原生 MCP 支付 Binding。
- ACT Core 仍在修订，当前文档不构成最终协议字段或兼容性承诺。

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

如果本仓库与支付宝官网的产品操作发生冲突，以官网和支付宝开放平台当前文档为产品事实源，并在 [Profile 官方资料表](../../profiles/alipay-ai-pay/official-sources.md)登记变化。
