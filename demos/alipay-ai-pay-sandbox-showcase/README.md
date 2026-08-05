# Alipay AI Pay Sandbox Showcase

> 状态：Web showcase、Buyer/Seller 事件适配和证据工具已实现 / Agent Runtime 接线与沙箱证据待完成；面向场景：2026 外滩大会 ACT v2.1 支付服务域演示

本 Demo 用于向观众展示买方 Agent 与卖方收费服务如何通过 ACT A402 和支付宝 AI 付形成一条机器支付闭环。它不实现钱包、支付、验凭证或沙箱，只消费 Quickstart 与支付宝官方能力产生的脱敏事件。

页面顶部先固定展示三个互不替代的概念：

- 场景组件：`PSD-PAY-INS / L1`；
- 访问协议：独立的 `PSD-PAY-A402`；
- 产品 Profile：支付宝 Agent 支付 + AI 按量付费。

主页面采用“协议过程舞台”，阅读顺序固定为：

1. 阶段导航：CID 上下文、A402 出账、INS/L1 支付、A402 验款、履约；
2. 参与方：用户、Buyer Agent、收费服务与支付宝 PSP；
3. 当前消息：明确展示发送方、接收方、消息方向和线上的协议消息；
4. 三层映射：同一动作对应的 ACT 组件、HTTP/Binding 与支付宝产品能力；
5. 业务结果：资源保持锁定、成功交付或因异常拒绝交付；
6. 关联与证据：请求、订单、资源、支付交易与履约的脱敏关联链。

11 步时间线保留为舞台下方的进度导航，不再与当前协议消息争夺视觉焦点。

## 开箱即用的三种模式

| 模式 | 是否开箱可用 | 数据含义 |
|---|---|---|
| `GUIDED_PREVIEW` | 是 | 内置说明性数据，用于完整体验页面与讲解路径；始终标注 `NOT PAYMENT EVIDENCE` |
| `LIVE_SANDBOX` | 需要事件 Adapter | 消费官网沙箱与 Quickstart 产生的真实脱敏 SSE |
| `SANITIZED_REPLAY` | 需要真实证据文件 | 播放已经通过验证的官网沙箱脱敏记录 |

`GUIDED_PREVIEW` 解决首次运行时的空白问题，但不会被证据校验器接受，也不能用于任何产品兼容声明。

## 成功演示链路

```text
CAPABILITY_NEGOTIATED
→ ORDER_CONFIRMED
→ RESOURCE_REQUESTED
→ PAYMENT_REQUIRED
→ USER_AUTHORIZATION_REQUIRED
→ PAYMENT_PROCESSING
→ PAYMENT_RESULT_RECEIVED
→ RESOURCE_REQUEST_RETRIED
→ PAYMENT_VERIFIED
→ RESOURCE_DELIVERED
→ FULFILLMENT_CONFIRMED
```

状态必须来自实际 Quickstart 事件，不得由 UI 定时器自动推进为成功。

Guided Preview 还可切换：

- 支付结果待确认：查询原交易，禁止重复支付；
- Proof 不匹配：拒绝交付；
- 验款暂不可用：返回可重试错误，禁止猜测成功；
- 幂等重放：返回既有交付结果，不重复扣款或交付。

## 两种运行模式

| 模式 | 事件来源 | 用途 | 展示要求 |
|---|---|---|---|
| `LIVE_SANDBOX` | 官方 Skill/CLI、卖方 Quickstart、支付宝 Sandbox/OpenAPI | 大会主演示 | 显示 Sandbox，不输出凭证和密钥 |
| `SANITIZED_REPLAY` | 已验证链路的脱敏事件记录 | 网络或沙箱异常时备用 | 全程明显显示 Replay，不冒充实时支付 |

## 运行证据校验器

本目录不附带虚构成功数据。第一次沙箱验证后，将每个状态写成一行 NDJSON，再运行：

```bash
npm test
node validate-evidence.mjs /absolute/path/to/sanitized-events.ndjson
```

校验器按场景要求状态严格有序、关联引用非空，并拒绝 `MOCK` 模式、明显的密钥字段和完整 `Payment-Proof`。成功场景要求 11 个状态；失败场景必须停在对应失败终态，不能补造交付事件。事件最小格式见 [`event-format.md`](event-format.md)。它证明的是演示证据完整性，不代替支付验款或 ACT 一致性认证。

## 启动 Web 演示台

需要 Node.js 18 或更高版本，不需要安装第三方依赖：

```bash
cd demos/alipay-ai-pay-sandbox-showcase
npm test
npm run build
npm run demo
```

浏览器打开终端输出的本地地址，默认选择 `GUIDED_PREVIEW`。选择场景并点击“播放当前场景”即可观看完整状态机，不需要账号、密钥、沙箱或 Replay 文件。

### Live Sandbox

`npm run demo` 同时启动仅监听 `127.0.0.1` 的脱敏事件 Bridge：

```text
GET  /events        SSE 事件流
POST /events        提交下一个脱敏事件
GET  /events/state  查询当前序号
GET  /events/export 完整链路导出为 Live NDJSON；未完成时返回 409
POST /events/reset  开始一条新链路
```

页面切换到 Live 后，默认连接同源 `/events`。Bridge 会补充序号、Sandbox 模式和观察时间，严格拒绝乱序、Mock 来源和敏感字段；它不接收或代理支付请求。

开始一次新验证：

```bash
curl -X POST http://127.0.0.1:4173/events/reset
```

Live 事件由 Quickstart Adapter 或演示编排器生成；官方 Skill/CLI、卖方服务和支付宝 OpenAPI 仍是产品行为来源。

#### 买方 Agent Adapter

先为本次验证生成只用于证据关联的脱敏引用，例如：

```bash
export ACT_DEMO_CORRELATION_REF=corr-sha256-a1b2
export ACT_DEMO_VALIDATION_ID=E2E-YYYYMMDD-NNN
```

Buyer Adapter 接受宿主 Agent 产生的脱敏结构化信号，并把它们转换为 Demo 状态。它不调用支付、不解析 CLI 对客文本，也不接受完整 Proof。

```bash
npm run adapt:buyer -- /absolute/path/to/sanitized-buyer-signal.json
```

双方确认支付能力时，宿主 Agent 提交：

```json
{
  "signal": "CAPABILITY_SELECTED",
  "observed_from": "HOST_AGENT",
  "source": "your-agent-runtime",
  "evidence_ref": "E2E-YYYYMMDD-NNN#capability",
  "correlation_ref": "corr-sha256-a1b2",
  "method_id": "alipay-ai-pay",
  "psp_id": "alipay"
}
```

订单确认使用 `ORDER_CONFIRMED` 信号，并提供 `request_ref` 和 `order_ref`。卖方第一次收到资源请求后自动输出 `RESOURCE_REQUESTED` 和 `PAYMENT_REQUIRED`。

宿主 Agent 只有在官方支付宝支付工作流产生对应真实状态后，才能依次提交：

| Adapter 信号 | `observed_from` | Demo 状态 |
|---|---|---|
| `AUTHORIZATION_REQUIRED` | `OFFICIAL_ALIPAY_PAYMENT_SKILL` | `USER_AUTHORIZATION_REQUIRED` |
| `PAYMENT_STARTED` | `OFFICIAL_ALIPAY_PAYMENT_SKILL` | `PAYMENT_PROCESSING` |
| `PAYMENT_SUCCEEDED` | `OFFICIAL_ALIPAY_PAYMENT_SKILL` | `PAYMENT_RESULT_RECEIVED` |
| `PAYMENT_PENDING` | `OFFICIAL_ALIPAY_PAYMENT_SKILL` | `PAYMENT_PENDING` |

`PAYMENT_SUCCEEDED` 必须提供脱敏 `transaction_ref`；`PAYMENT_PENDING` 必须提供 `recovery_action`。错误来源、敏感字段、缺失关联字段或乱序事件都会被拒绝。当前仓库提供的是运行时无关 Adapter 契约；首次 Live 联调还需要在选定的 Agent Runtime 中，于真实官方 Skill/CLI 状态边界调用该命令。

#### 卖方 Quickstart Adapter

在卖方服务的本地环境中增加：

```bash
ACT_DEMO_BRIDGE_URL=http://127.0.0.1:4173/events
ACT_DEMO_VALIDATION_ID=E2E-YYYYMMDD-NNN
```

启用后，卖方 Quickstart 会以非阻断方式输出：

- 首次资源请求；
- 402 账单；
- 携 Proof 的原请求重试；
- 官方验款通过；
- 资源交付；
- 卖方履约确认。

验款拒绝时输出 `PROOF_REJECTED`；验款服务不可用时输出 `VERIFICATION_UNAVAILABLE`。失败终态不再输出资源交付。

未配置这两个变量时，卖方行为与之前完全一致。Adapter 连接失败不会改变支付、验款或交付结果。

### Sanitized Replay

在页面切换到 Replay，选择通过校验器的 NDJSON 文件。页面会先验证所选场景的完整状态链，再允许逐步或自动播放，并始终显示 `SANITIZED REPLAY`。

仓库不附带成功 Replay。第一份 Replay 必须来自已经通过的官网沙箱验证。

完成一条 Live 链路后，先导出原始脱敏事件：

```bash
curl --fail http://127.0.0.1:4173/events/export \
  --output /absolute/path/to/live-sandbox-evidence.ndjson
node validate-evidence.mjs /absolute/path/to/live-sandbox-evidence.ndjson
```

人工复核文件不含密钥、令牌、完整 Proof、完整业务标识或可重放请求后，生成 Replay：

```bash
npm run prepare:replay -- /absolute/path/to/live-sandbox-evidence.ndjson \
  --validation-id E2E-YYYYMMDD-NNN \
  --reviewed-by review-record-ref \
  --ack-sanitized \
  > /absolute/path/to/sanitized-replay.ndjson
node validate-evidence.mjs /absolute/path/to/sanitized-replay.ndjson
```

`--ack-sanitized` 是人工复核声明，不是自动脱敏功能。工具会再次检查完整性和明显敏感文本，但不能代替安全审查。

## 复用的 Quickstart

- [买方 Agent Payment](../../quickstarts/alipay/agent-payment/README.md)
- [卖方 Metered REST Provider](../../quickstarts/alipay/metered-rest-provider/README.md)
- [端到端 402](../../quickstarts/alipay/end-to-end-402/README.md)

Demo 不能复制这些目录中的协议或产品逻辑。需要改变支付处理时先修改并验证 Quickstart，再由 Demo 消费其事件。

沙箱联调使用 [AIPay 官网接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)；完成后按 [ACT 沙箱验证补充](../../quickstarts/alipay/end-to-end-402/sandbox-validation.md)生成大会证据。

## 安全边界

不得进入 Demo 制品、日志、录屏或 Replay 数据：

- 私钥、公钥文件路径以外的密钥内容；
- 绑定码、支付密码、访问令牌和 `app_auth_token`；
- 完整 `Payment-Proof` 或 `client_session`；
- 可重放 HTTP 请求；
- 完整订单号、交易号和用户标识。

## 大会验收清单

- [ ] LIVE 模式完成一次官方沙箱闭环；
- [ ] Replay 数据来自该闭环并通过脱敏复核；
- [ ] 正常链路在 3 分钟内完成；
- [ ] 连续运行 10 次无阻断；
- [ ] 失败、超时或需要重新授权时不会显示成功；
- [ ] UI 清楚区分协议步骤、支付宝产品步骤和资源交付；
- [ ] Demo 机器不依赖个人目录、隐式登录态或未记录配置；
- [ ] 现场网络异常时可以切换 Replay，且不改变演示口径。

## 协议候选项与产品事实

ACT v2.1 修订候选引入 `method_id`、`CID-PCA-NEG` 和 `Payment-Validation`。Demo 对前两者建立显式事件与页面映射；对于 `Payment-Validation`，当前只展示：

```text
ACT candidate Payment-Validation → Alipay payment.verify result
```

这不是在声明支付宝官网已支持同名响应 Header。产品接入、沙箱与正式接口事实始终以 AIPay 官网为准。

## 当前状态

Guided Preview、Live Bridge、多场景状态机、Buyer Runtime Adapter 契约、卖方 Quickstart Adapter、完整证据导出和 Replay 准备工具已经建立。下一步是在选定的 Agent Runtime 中把官方 Skill/CLI 真实状态接到 Buyer Adapter，并使用官网沙箱生成首份 Replay；在此之前页面只标记 `TARGET BASELINE`，不提交虚构的成功事件夹具。
