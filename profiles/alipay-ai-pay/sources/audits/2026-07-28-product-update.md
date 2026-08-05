# Alipay AI Pay 官网核对（2026-07-28）

> 状态：Completed source audit / Sandbox validation pending  
> 核对时间：2026-07-28  
> 用途：记录 ACT 2.1 首次候选同步时的支付宝公开产品事实

## 1. 来源状态

| 来源 | 结果 |
|---|---|
| [AI 按量付费产品页](https://aipay.alipay.com/callpay) | 可访问（HTTP 200） |
| [AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html) | 页面显示更新时间 `2026-07-23 21:43:40` |

仓库没有保存 2026-07-22 官网正文快照，因此不能声称已完成逐字差异比较。本次只记录可验证的页面更新时间变化，并重新核对影响 ACT/Profile 的关键事实。

## 2. 关键产品事实复核

- 未支付或 Proof 验证失败时返回 HTTP 402 和 `Payment-Needed`。
- `Payment-Needed` 为 Base64URL 编码账单。
- 支付完成后携带 `Payment-Proof` 重试资源请求。
- 卖方调用 `alipay.aipay.agent.payment.verify`，并检查 `active`、金额、商户订单、资源和交易防重。
- 资源返回后异步调用 `alipay.aipay.agent.fulfillment.confirm`。
- 官网没有定义 `Payment-Validation` Header。
- 官网沙箱和产品接入只引用，不在 ACT 仓库重复实现。

## 3. 对 ACT 2.1 候选的影响

上述事实与仓库现有 Alipay Profile、Quickstart 和 Demo 分层一致。需要继续保留：

- `Payment-Proof` 的 Base64 / Base64URL 编码差异为 `PRODUCT-REVIEW`；
- `Payment-Validation` 只作为 ACT 候选语义映射，不声明为支付宝产品 Header；
- 金额单位、`client_session` 必填性、防重保存周期和履约重试规则继续等待产品或沙箱证据。

本次未因官网更新时间变化修改 Quickstart 产品逻辑。
