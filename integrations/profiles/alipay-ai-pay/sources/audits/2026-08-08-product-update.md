# Alipay AI Pay 官网核对（2026-08-08）

> 状态：Completed source audit / Sandbox validation pending  
> 核对时间：2026-08-08（UTC+8）  
> 用途：ACT 2.1 Candidate 公开前的支付宝产品事实复核

## 1. 来源状态

| 来源 | 本次结果 |
|---|---|
| [Agent 支付产品页](https://aipay.alipay.com/agentpay) | 可访问；继续提供 Agent 支付产品入口 |
| [支付宝 Agent 支付用户指南](https://aipay.alipay.com/wallet-guide) | 可访问；正式安装命令仍为 `npx -y @alipay/agent-payment@latest install`；开通、身份核验和短时绑定码仍由官方流程处理 |
| [Official Payment Skills repository](https://github.com/alipay/payment-skills) | 可访问；继续作为买方钱包与支付 Skill 的公开实现来源 |
| [AI 按量付费产品页](https://aipay.alipay.com/callpay) | 可访问；继续作为卖方按量付费产品入口 |
| [AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html) | 可访问；页面显示更新时间 `2026-08-07 21:51:27` |

上一份审计记录的指南更新时间为 `2026-07-31 11:54:36`。本次确认页面时间戳变化，并逐项复核影响 ACT、Profile、Quickstart 和 Showcase 的公开事实；仓库不保存或转发官网全文。

## 2. 变化结论

本次未发现需要修改运行逻辑或 Candidate 协议语义的产品变化：

1. 买方正式安装路径仍使用 `@alipay/agent-payment`，卖方自动集成仍使用 `@alipay/alipay-aipay`，两者职责不得互换。
2. 未支付或 Proof 验证失败时，卖方仍返回 `402 Payment Required` 和 `Payment-Needed`。
3. `Payment-Needed` 仍明确为 Base64URL；`Payment-Proof` 正文仍写作 Base64；产品载荷仍使用 `protocol` + `method` 结构。
4. 买方完成支付后仍携带 `Payment-Proof` 重试原请求。
5. 卖方仍调用 `alipay.aipay.agent.payment.verify`，并核对支付状态、金额、商户订单、资源与交易标识以防重复履约。
6. 资源交付后仍异步调用 `alipay.aipay.agent.fulfillment.confirm`。
7. 官网仍未定义 `Payment-Validation` 响应 Header。

## 3. ACT 与产品边界

- ACT 2.1 Candidate 的三类 Header Base64URL 规则不覆盖支付宝当前 `Payment-Proof` 产品文案；Alipay Profile 继续将该差异保留为 `PRODUCT-REVIEW`。
- ACT Candidate 的可选 `Payment-Validation` Header 只映射产品服务端验凭语义；当前 Profile 不声称支付宝发送同名 Header。
- ACT Candidate 的 INS/L1、DEL/L2、AUP/L3 是协议授权场景。当前公开支付宝材料只能支持仓库声明的 L1 产品路径；Showcase 中 L2/L3 继续标记 Candidate / Product pending。
- 官网沙箱、账号、密钥、支付执行和产品验款由支付宝提供；本仓库只引用，不复制实现。

## 4. 仓库处理

- 将产品资料最后核对日期更新为 `2026-08-08`，指南页面时间更新为 `2026-08-07 21:51:27`；
- 保留现有 Profile、Quickstart 和 Showcase 运行逻辑；
- 增加机器可执行的产品来源时间戳漂移检查，发现官网时间晚于仓库记录时失败并要求人工审计；
- 不创建订单、不发起支付、不把本次文档复核声明为 Sandbox Verified。
