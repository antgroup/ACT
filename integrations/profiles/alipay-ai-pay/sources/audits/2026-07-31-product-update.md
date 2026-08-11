# Alipay AI Pay 官网核对（2026-07-31）

> 状态：Completed source audit / Sandbox validation pending  
> 核对时间：2026-07-31（UTC+8）  
> 用途：July Preview 候选发布前的支付宝公开产品事实复核

## 1. 来源状态

| 来源 | 本次结果 |
|---|---|
| [AI 按量付费产品页](https://aipay.alipay.com/callpay) | 本轮自动抓取超时；未用该页面新增或覆盖产品事实 |
| [AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html) | 可访问；页面显示更新时间 `2026-07-28 20:57:32` |
| [官方 AI Pay 402 示例](https://github.com/alipay/ai/tree/main/code_example/aipay-402-example) | 可访问；继续作为示例参考，不作为协议事实源 |

上一份审计记录的接入指南更新时间是 `2026-07-23 21:43:40`。因此本轮确认产品文档存在时间戳变化，并重新核对影响 ACT/Profile 的公开事实。仓库不保存官网全文，不声称完成逐字差异比较。

## 2. 关键产品事实复核

接入指南当前仍公开以下流程：

1. 未支付或 Proof 验证失败时返回 `402 Payment Required` 和 `Payment-Needed`。
2. `Payment-Needed` 使用 Base64URL 编码。
3. 支付完成后携带 `Payment-Proof` 重新请求资源；页面仍将其描述为 Base64 编码。
4. 卖方调用 `alipay.aipay.agent.payment.verify`，除接口调用成功外还检查 `active`、金额、商户订单、资源和 `trade_no` 防重复履约。
5. 资源返回后异步调用 `alipay.aipay.agent.fulfillment.confirm`。
6. 官网没有定义 `Payment-Validation` Header。
7. 卖方 Vibe-coding 推荐入口仍为 `npx -y @alipay/alipay-aipay@latest install`；它不是买方 `@alipay/agent-payment`。

## 3. 与仓库的差异

本轮没有发现需要改变 Quickstart 产品逻辑的新事实。以下差异继续保持开放：

- `Payment-Needed` 为 Base64URL，而 `Payment-Proof` 文案为 Base64；
- `amount` 字段说明与 `0.01 CNY` 示例之间仍可能造成主单位/最小单位歧义；
- 官网没有 `Payment-Validation` Header；
- `trade_no` 防重保存周期、并发规则和履约确认失败后的持久化重试责任未公开冻结；
- 买方履约确认与卖方履约确认的关系仍需真实沙箱证据或产品确认。

## 4. 本轮处理

- 更新产品 Source Registry 的最后核对日期和指南更新时间；
- 更新 `release-manifest.json` 的产品事实快照；
- 不修改 ACT Core Candidate 语义；
- 不把官网产品报文反向固化为 ACT 2.1 Core Schema；
- 真实支付、验凭、资源交付和履约证据继续标记为 Sandbox pending。
