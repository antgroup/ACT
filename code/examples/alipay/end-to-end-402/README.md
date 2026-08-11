# 端到端 402 Quickstart

> 目标：将官方买方 Skill/CLI 连接到真实卖方 402 端点，并收集可复现的沙箱证据

沙箱开通与联调直接使用 [AIPay 官网接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)，本仓库不复述或实现产品沙箱。官网联调完成后，按 [ACT 沙箱验证补充](sandbox-validation.md)记录协议和 Profile 证据。没有执行真实链路时，ACT Candidate 和 Profile Preview 仍可发布，但不得声明 Sandbox Verified。

## 沙箱本地预检

在进入真实订单和用户授权前运行：

```bash
npm --prefix code/examples/alipay/end-to-end-402 run sandbox:preflight
```

预检只报告官方 CLI、Java/Maven、卖方 `.env` 必填项和密钥文件是否就绪，不输出配置值，也不会创建订单、发起支付或声称沙箱成功。需要机器可读结果时运行 `npm --prefix code/examples/alipay/end-to-end-402 run sandbox:preflight:json`。

预检失败时先按字段名完成官网开通和本地配置；预检通过后仍必须由用户明确授权真实沙箱支付。

## 0. 先跑本地非支付闭环

在仓库根目录运行：

```bash
npm --prefix code/examples/alipay/end-to-end-402 run local
```

它会启动临时本地服务、检查 `402 + Payment-Needed`，再提交一个明确无效的假 `Payment-Proof`，确认服务仍返回 `402` 且没有交付资源。整个过程不需要密钥、不访问支付宝、不发起支付，也没有“Mock 支付成功”分支。

通过本步骤只说明开发环境和公开挑战结构可以工作，不满足真实产品接入或端到端验证标准。

需要观察原始 HTTP 时，先在一个终端运行：

```bash
npm --prefix code/examples/alipay/end-to-end-402 run preview
```

然后在另一个终端依次执行“请求 → 解码 402 → 携假 Proof 重试”：

```bash
curl -i http://127.0.0.1:18080/paid-resource
node code/examples/alipay/end-to-end-402/inspect-402.mjs \
  http://127.0.0.1:18080/paid-resource
curl -i -H 'Payment-Proof: NON_PAYABLE_FAKE_PROOF' \
  http://127.0.0.1:18080/paid-resource
```

第一次和第三次请求都应得到 `402`；第三次响应的 `resource_delivered` 必须为 `false`。支持 REST Client 的编辑器也可以直接运行 [`local-preview.http`](local-preview.http)。

检查器需要的支付宝产品字段来自 [Alipay AI Pay Payment-Needed Profile Preview Schema](../../../../integrations/profiles/alipay-ai-pay/schemas/payment-needed.preview.schema.json)，不再由 Quickstart 维护另一份必填字段列表。该 Schema 是 Product Profile Preview，不是 ACT 2.1 Core Schema。

## 1. 启动卖方服务

配置并运行[AI 按量付费服务端](../metered-rest-provider/README.md)，然后确认健康检查端点：

```bash
curl http://127.0.0.1:8080/health
```

## 2. 检查支付要求

需要 Node.js 18 或更高版本。

```bash
cd code/examples/alipay/end-to-end-402
npm run inspect -- http://127.0.0.1:8080/paid-resource
```

检查器不会发起支付。它只检查真实 HTTP 状态、解码 `Payment-Needed`、验证公开必填字段结构，并输出脱敏摘要。

## 3. 安装并调用买方能力

按照 [Agent 支付 Quickstart](../agent-payment/README.md)完成买方配置，然后让使用官方 Skill/CLI 的 Agent 访问收费资源 URL。真实沙箱支付必须由用户看到并授权。

官方买方流程可能在内部持有 `Payment-Proof`。不要从日志复制或手工重建凭证。卖方只有在官方验凭证通过后才会交付资源。

## 4. 记录验证结果

将仓库中的[证据模板](../../../../docs/getting-started/end-to-end-evidence-template.md)复制到公开制品目录之外，并记录：

- 仓库 Commit 和 Quickstart 版本；
- 官方软件包、Skill 或 CLI 的版本或完整性信息；
- 脱敏后的订单、交易和资源标识；
- 402、授权、验凭证、交付和履约确认时间；
- 至少一个无效或过期场景的实际恢复行为。

不得记录私钥、绑定码、支付密码、`app_auth_token`、完整 `Payment-Proof`、`client_session` 或可重放的 HTTP 请求。

## 5. 通过标准

只有同时满足以下条件，才能声明端到端验证通过：

- 买方使用支付宝官方能力；
- 支付通过官方产品流程获得授权；
- 服务端调用官方验凭证 API；
- 验证事实与原始账单一致；
- 只交付预期资源；
- 履约确认成功，或进入可审计、持久化的重试路径；
- 所有证据已脱敏，并可依据官方文档公开复现。

仅通过本地单元测试和检查器不满足上述标准。
