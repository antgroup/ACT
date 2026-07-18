# AI 按量付费 Getting Started

> 状态：July Preview / Non-normative  
> 公开接入基线：支付宝 AI 按量付费 HTTP 402 方案

本指南面向希望让 API、MCP Tool、Skill、数字内容或算力资源按调用收费的服务提供方。开户、产品签约、密钥和沙箱操作以支付宝官网为准；本文只补充 ACT/Profile 责任和验收边界。

## 1. 完成后你将得到什么？

你的服务应能够：

- 对未支付的资源请求返回 HTTP 402 和 `Payment-Needed`。
- 对账单关键字段按支付宝规则进行签名。
- 接收 Agent 携带 `Payment-Proof` 的原请求重试。
- 调用支付宝支付凭证验证 API。
- 核对金额、商户订单、资源和支付状态。
- 阻止相同交易被重复用于非幂等交付。
- 返回资源并调用支付宝履约确认 API。

## 2. 选择接入方式

支付宝官网当前提供两条公开入口：

### Agent 自动集成

按照[官网产品接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)安装支付宝 AI 付 Skill，并让 AI 编程工具协助项目集成和沙箱测试。

### 手动服务端集成

服务端自行实现官网规定的三个步骤：

1. 返回 402 账单。
2. 读取并验证支付凭证。
3. 资源交付后确认履约。

无论采用哪种方式，ACT/Profile 的安全和验证责任相同。

## 3. 产品前置条件

在支付宝官网完成或准备：

- 选择 AI 按量付费产品。
- 准备自研应用，或按官网支持的第三方代调用方式接入。
- 使用官网提供的 Sandbox 完成技术验证。
- 注册收费服务并取得产品要求的服务标识。
- 配置应用和支付宝公钥/私钥等产品凭证。

这些步骤可能随产品更新变化，本仓库不复制具体页面和密钥配置。请从[支付宝 AI 付产品概览](https://aipay.alipay.com/docs/overview.html)和[按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)进入。

## 4. ACT 四域覆盖

AI 按量付费也不是只属于 PSD。卖方接入主要落在 CID、PSD 和 TSD，并消费买方 Agent 在 ADD 中形成的授权上下文：

| ACT 域 | 首期关系 | 卖方边界 |
|---|---|---|
| ADD | 买方捕获购买意图并决定是否有权支付 | 卖方不替用户签发授权 |
| CID | 描述收费资源，确认金额/订单/收款方，声明支付宝支付能力 | 402 账单需要可追溯到同一交易和资源 |
| PSD | 返回 402、接收 Proof、调用支付宝验款并确认履约 | 支付宝字段、RSA2 和 API 属于 Product Profile |
| TSD | 形成支付完成和资源履约的可关联证据 | 产品日志/回调不自动等同于 ACT TSD 记录 |

ACT 官网目前把 402 基础框架放在 `PSD-PAY-AUP`。本项目复用该交互框架，但买方实际采用 `PSD-PAY-INS`、`PSD-PAY-DEL` 还是 `PSD-PAY-AUP`，取决于授权级别。组件级说明见[产品与 ACT 四域映射](../../profiles/alipay-ai-pay/domain-mapping.md#4-ai-按量付费映射)。

## 5. 第一步：返回支付要求

没有可验证支付凭证时，服务返回：

```http
HTTP/1.1 402 Payment Required
Payment-Needed: <base64url encoded Alipay bill>
Content-Type: application/json
```

ACT 将其理解为产品无关的 Payment Requirement；`Payment-Needed` 的 `protocol`、`method`、商户身份和 RSA2 签名属于 Alipay AI Pay Profile 与 HTTP Binding。

实现时需要确保：

- 商户订单号可唯一定位原账单。
- `resource_id` 唯一对应准备交付的资源。
- 金额、币种、支付截止时间和收款方来自服务端可信配置。
- 使用官网规定的字段集合和顺序签名。
- 私钥只在安全的服务端环境中使用。
- 账单过期后不会静默修改旧账单并继续支付。

准确字段和签名规则直接查阅[官网第一步：返回 402 账单](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)。ACT 工作映射见 [Field mapping](../../profiles/alipay-ai-pay/field-mapping.md)。

## 6. 第二步：验证支付凭证

Agent 支付后会携带 `Payment-Proof` 重试资源请求。服务端必须把它视为不可信输入：

1. 按官网格式解码 Header。
2. 取得 `payment_proof`、`trade_no` 和产品要求的客户端会话信息。
3. 调用 [`alipay.aipay.agent.payment.verify`](https://ideservice.alipay.com/cms/site/0j7uot)。
4. API 调用成功后继续核对业务字段。

至少检查：

- `active` 为真。
- 返回金额与原账单完全一致。
- `out_trade_no` 与服务端保存的原账单一致。
- `resource_id` 与本次请求资源一致。
- `trade_no` 没有被用于重复履约。

任何检查失败都不能交付资源。接口调用成功不等于 ACT 业务验证成功。

## 7. 第三步：交付和履约确认

验证和本地一致性检查全部通过后：

1. 原子地记录交易与资源的履约占用，防止并发重放。
2. 返回对应的付费资源。
3. 异步调用 [`alipay.aipay.agent.fulfillment.confirm`](https://ideservice.alipay.com/cms/site/0j7sw0)。
4. 履约确认失败时保留交付证据，并按相同交易号幂等重试。

当前公开履约接口主要使用 `trade_no`。部分交付、交付失败和 Profile 幂等字段仍在产品/协议待确认清单中，不能由示例代码自行扩展成官方字段。

## 8. MCP Tool 和 Skill

在大会首期范围内：

- MCP Tool 或 Skill 可以提供需要付费的资源能力。
- 收费链路复用官网 HTTP 402 方案。
- 业务 Tool/Skill 负责资源输入输出；支付语义由 ACT/Profile 承接。
- 不声明支付宝已经公开独立的原生 MCP 支付 Transport。

如果实际运行时无法直接暴露 HTTP 402，应由对应 Binding 明确封装规则，而不是改变 `Payment-Needed`、`Payment-Proof` 和验款语义。

## 9. 验收清单

- [ ] 产品开通、服务注册、密钥和沙箱来自支付宝官网当前流程。
- [ ] 未支付请求真实返回 402 和合法 `Payment-Needed` Header。
- [ ] 账单由服务端签名，私钥不出现在代码、日志和测试产物中。
- [ ] `Payment-Proof` 来自真实沙箱支付，不是本地伪造。
- [ ] 服务实际调用支付宝支付验证 API。
- [ ] API 成功后继续校验 active、金额、订单和资源。
- [ ] 并发或重复 `trade_no` 不会造成重复交付。
- [ ] 资源交付后实际调用履约确认 API。
- [ ] 过期、无效、未支付、错金额、错资源和重放场景均有测试证据。

## 10. 不要这样实现

- 不要看到 `Payment-Proof` Header 就直接返回资源。
- 不要只检查支付宝 API 的通用成功码。
- 不要信任 Agent 传入的金额、商户订单或资源标识。
- 不要在验款失败时复用原订单并自动修改金额。
- 不要把同一支付用于多个不同资源。
- 不要使用 `impl/python/` 的 Mock 支付作为沙箱验证。

## 11. 下一步

- 联合验证 Agent 买方：[端到端 402 验证](end-to-end-402.md)
- 查看生命周期：[Lifecycle mapping](../../profiles/alipay-ai-pay/lifecycle-mapping.md)
- 查看错误恢复：[Error mapping](../../profiles/alipay-ai-pay/error-mapping.md)
- 查看支付宝官方示例：[aipay-402-example](https://github.com/alipay/ai/tree/main/code_example/aipay-402-example)
