# 支付宝 Skill/CLI Binding

> Kind: Product Workflow Binding；Status: Preview / Non-normative；Version: `0.9-preview.1`；Depends on: ACT Core `2.1-candidate.1`, Alipay AI Pay Profile `0.9-preview.1`

大会买方接入基线使用支付宝官方钱包与支付 Skill。这是 **Alipay AI Pay Profile 下的产品工作流 Binding**，不是 ACT 跨产品通用 Binding。一次命令或 Skill 调用可以封装钱包准备、用户授权、支付执行、结果查询、凭证提交、原请求重试和结果交付。

宿主 Agent 仍然必须保存：

- 用户原始意图；
- 用户可理解的交易摘要；
- 原始付费资源请求；
- 处理中、成功、失败和需要授权等结果的明确区分；
- 足以恢复或审计任务的非敏感证据。

宿主不得从日志提取密钥，不得伪造 `Payment-Proof`，也不得将本地 Mock 结果当作真实支付成功。

官方安装方式和行为由 [alipay/payment-skills](https://github.com/alipay/payment-skills) 维护。本仓库不复制官方安装文档，只维护 ACT/产品映射和验证入口。可运行入口见 [Agent Payment Quickstart](../../../../quickstarts/alipay/agent-payment/README.md)。

本 Binding 可以封装多步，覆盖范围由 ACT Candidate 的 Workflow Binding manifest 约束；真实官方 CLI 状态和结果仍需在 Sandbox Verified 证据中记录，不阻塞 Preview 发布。
