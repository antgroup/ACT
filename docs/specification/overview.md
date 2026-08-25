# ACT 2.1 规范概览

中文 | [English](overview.en.md)

> **状态：ACT 2.1 / Final**

ACT（Agentic Commerce Trust Protocol）定义智能体参与商业活动时的授权、交易、支付和信任协作语义。ACT 2.1 包含四个能力域，并以跨域组件连接完整业务流程。

## 规范性用语

ACT 2.1 的中文规范采用以下要求强度，所有域正文和跨域连接规则均按本表解释：

| 中文用语 | 要求强度 | 英文等价用语 |
|---|---|---|
| 应、必须 | 强制满足 | `MUST` |
| 不应、不得 | 强制禁止 | `MUST NOT` |
| 宜 | 推荐满足 | `SHOULD` |
| 不宜 | 建议避免 | `SHOULD NOT` |
| 可、可以 | 可选 | `MAY` |

字段存在性中的“必备”表示字段必须存在且具有有效值；“条件必备”表示条件成立时必须存在且具有有效值；“可选”表示允许存在，存在时其值必须有效。英文翻译中的大写规范词必须保持相同要求强度；翻译差异仍以中文版本化正文为准。

## 1. 四个能力域

| 域 | 职责 | 规范入口 |
|---|---|---|
| ADD | 表达用户意图，签发并管理 Agent 可执行的授权凭证 | [委托授权域](authorization-delegation.md) |
| CID | 商品或服务发现、意图传递、支付能力协商和交易确认 | [商业交互域](commerce-interaction.md) |
| PSD | 支付工具、授权等级、支付执行、验证、状态和错误恢复 | [支付服务域](payment-services.md) |
| TSD | 为跨域事实提供可信存证和信用关联能力 | [信任服务域](trust-services.md) |

[典型场景](../flows/scenarios.md)说明四个域如何组合。场景说明与域正文冲突时，以对应域正文为准。

## 2. 支付服务域组件

| 类型 | 组件 | 含义 |
|---|---|---|
| 支付工具 | `PSD-PMT-BND` | 建立受限的支付工具引用，避免 Agent 接触原始账户凭证 |
| 账户隔离 | `PSD-AGT-SUB` | 为 Agent 提供可选的专属子账户与生命周期管理 |
| L1 | `PSD-PAY-INS` | 用户在场，资金处理前逐笔核身确认 |
| L2 | `PSD-PAY-DEL` | 商品、商户、金额等交易意图已明确，Agent 在授权范围内自动支付 |
| L3 | `PSD-PAY-AUP` | Agent 在任务、预算和策略边界内自主选择并支付 |
| 支付接入 | `PSD-PAY-A402` | 使用 HTTP 402 交换支付要求、支付证明和验证结果 |

L1、L2 和 L3 回答“Agent 凭什么支付”；A402 回答“支付要求和证明如何交换”。A402 可以被三个授权等级引用，不属于其中任何一个等级。

## 3. A402 基本流程

```text
Buyer Agent → Paid Service: request resource
Paid Service → Buyer Agent: 402 + Payment-Needed
Buyer Agent → Payment Service: authorized payment
Payment Service → Buyer Agent: payment result / proof
Buyer Agent → Paid Service: retry original request + Payment-Proof
Paid Service → Payment Service: verify proof
Paid Service → Buyer Agent: deliver resource
```

完整要求见 [A402 接入协议](a402.md)。商业交互到支付的连接规则见 [CID–PSD 协商](commerce-payment-negotiation.md)。

## 4. 协议与实现边界

- `docs/specification/` 定义 ACT 2.1。
- `code/schemas/` 提供 JSON Schema、fixtures 和测试辅助资产。
- `integrations/` 连接具体产品。
- `code/samples/` 和 `code/web-client/` 展示实现方式和业务流程。

机器资产、产品代码和 Demo 不得增加或修改协议要求。支付宝字段、API、签名、开户和沙箱行为以 [AIPay 官方资料](https://aipay.alipay.com/callpay)为准，不属于 ACT 规范。

## 5. 开发者入口

| 目标 | 入口 |
|---|---|
| 本地理解 A402 | [Local A402 Sample](../../code/samples/local-a402/README.md) |
| 运行交互 Demo | [Machine Payment Showcase](../../code/web-client/alipay-ai-pay-showcase/README.md) |
| 接入支付宝买方能力 | [Alipay Buyer Agent](../../integrations/alipay/buyer-agent/README.md) |
| 接入支付宝卖方能力 | [Alipay Seller Java](../../integrations/alipay/seller-java/README.md) |
| 验证支付宝沙箱链路 | [Alipay Validation](../../integrations/alipay/validation/README.md) |

返回[文档导航](../README.md)。
