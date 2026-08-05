# Alipay AI Pay 官网核对（2026-08-03）

> 状态：Completed source audit / Sandbox validation pending  
> 核对时间：2026-08-03（UTC+8）  
> 用途：完成版 ACT 2.1 支付服务域同步后的产品事实边界复核

## 1. 来源状态

| 来源 | 本次结果 |
|---|---|
| [Agent 支付产品页](https://aipay.alipay.com/agentpay) | 可访问；公开 `@alipay/agent-payment@latest install-experience` 体验入口 |
| [支付宝 Agent 支付用户指南](https://aipay.alipay.com/wallet-guide) | 可访问；正式安装/开通路径仍为 `@alipay/agent-payment@latest install` |
| [AI 按量付费产品页](https://aipay.alipay.com/callpay) | 可访问；卖方自动集成入口仍为 `@alipay/alipay-aipay@latest install` |
| [AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html) | 可访问；页面显示更新时间 `2026-07-31 11:54:36` |

上一份审计记录的指南更新时间是 `2026-07-28 20:57:32`。本次确认页面时间戳变化并复核影响 ACT/Profile/Quickstart 的公开事实；仓库不保存官网全文。

## 2. 关键事实结论

1. 买方正式安装路径仍是 `npx -y @alipay/agent-payment@latest install`；产品页新增/强调的 `install-experience` 是体验入口，不替代钱包指南中的正式安装命令。
2. 卖方自动集成仍使用 `npx -y @alipay/alipay-aipay@latest install`，与买方包职责不同。
3. 未支付或 Proof 验证失败时仍返回 `402 Payment Required` 和 `Payment-Needed`。
4. `Payment-Needed` 明确为 Base64URL；`Payment-Proof` 正文仍写作 Base64，并均使用 `protocol` + `method` 产品结构。
5. 卖方继续调用 `alipay.aipay.agent.payment.verify`，并检查 `active`、金额、`out_trade_no`、`resource_id` 和 `trade_no` 防重复履约。
6. 资源交付后继续异步调用 `alipay.aipay.agent.fulfillment.confirm`。
7. 官网仍没有定义 `Payment-Validation` Header。

## 3. 与完成版 ACT 2.1 的边界

- ACT Candidate 的三类 Header Base64URL 规则不覆盖支付宝当前 `Payment-Proof` 产品文案；Alipay Profile 继续记录为 `PRODUCT-REVIEW`。
- ACT Candidate 的可选 `Payment-Validation` Header 映射为产品服务端验凭语义，但当前支付宝实现不得声称发送同名 Header。
- ACT 的 14 字段基础清单不是支付宝字段必填表；Product Profile Preview 通过独立的 Payment-Needed、Payment-Proof 和验款结果 Schema 维护当前产品结构事实。

## 4. 仓库处理

- 更新产品 Source Registry、Profile 核对日期、Release Manifest 和协议修订状态中的产品时间戳；
- 保留买方 `@alipay/agent-payment` 与卖方 `@alipay/alipay-aipay` 的职责分离；
- 不修改 Quickstart 支付逻辑，不创建真实订单，不发起真实支付；
- 真实支付、验凭、资源交付和履约证据继续标记为 Sandbox pending。
