# 支付宝 Sandbox 端到端验证

> 状态：Validation checklist / Non-normative  
> 范围：L1 `PSD-PAY-INS` + `PSD-PAY-A402` + 支付宝 AI 按量付费实现

支付宝沙箱的开通、配置、账号、服务注册和联调步骤统一引用 [AIPay 官网 AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)。本仓库不复制官网沙箱教程，也不实现独立沙箱。

本文只补充 ACT 开源项目自身的验收要求。

## 本地就绪检查

执行以下命令检查官方 CLI、卖方运行时、配置字段和密钥文件是否存在：

```bash
node integrations/alipay/validation/sandbox-preflight.mjs
```

该命令不读取或输出密钥内容，不创建订单、不发起支付。只有输出 `local-preflight-passed` 后，才进入官网沙箱订单与用户逐笔授权步骤；它本身不构成任何支付或兼容性证据。

配置入口：

```bash
cd integrations/alipay/seller-java
./run.sh init
```

随后只在本地 `.env` 中填写官网分配的应用、商户、服务、资源、金额和密钥文件路径；该文件不得提交仓库。

本仓库不实现或复制支付宝 Sandbox、测试账号、沙箱 App、控制台和密钥分配。以上产品操作统一使用 [AIPay 官网](https://aipay.alipay.com/callpay)及其接入文档。真实 E2E 证据用于说明特定版本的互操作结果，不改变 ACT 2.1 的规范状态。

## ACT 验收链路

同一笔官网沙箱交易应当能够关联：

```text
资源请求
→ 402 + Payment-Needed
→ 用户逐笔确认
→ 官方 Agent Payment Skill/CLI 支付并恢复原请求
→ 卖方完成 payment.verify
→ 返回资源
→ 完成 fulfillment.confirm
```

仅运行本地测试、使用 Mock、手工构造 Proof 或只观察到单侧支付成功，都不能声明 ACT × Alipay AI Pay 端到端兼容。

## 开源项目需要额外记录的证据

产品操作按官网完成后，使用[端到端证据模板](evidence-template.md)记录：

- ACT、支付宝接入示例和官方 Skill/CLI 的精确版本；
- 仓库维护的 `act-integration:a402/alipay-ai-pay` 映射版本与对应 Commit；
- 原资源请求、账单、订单、交易、验款和履约之间的脱敏关联；
- `active`、金额、订单、资源和防重复履约检查结果；
- pending、失败、过期、字段不匹配和重放场景的恢复行为；
- 未解决问题属于 Protocol、Product、Binding 还是 Implementation。

不得记录账号、密钥、绑定码、支付密码、完整 Proof、`client_session` 或可重放请求。

Demo 的脱敏事件格式见 [Demo 事件格式](../../../code/web-client/alipay-ai-pay-showcase/event-format.md)。Replay 只能来自已通过的官网沙箱链路。

完整 Live 链路通过后，使用 Demo Bridge 的 `GET /events/export` 导出 NDJSON。人工完成脱敏复核后，再通过 `prepare-replay.mjs` 添加原验证编号和复核记录；未完成链路、未明确确认脱敏或包含明显敏感文本的文件不能生成合法 Replay。
