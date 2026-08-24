# ACT 2.1 Machine Payment Showcase

> 类型：Demo / Non-normative。支持内置场景演示和脱敏证据回放。

本 Demo 用于向观众展示买方 Agent 与卖方收费服务如何通过 ACT 支付服务域和 A402 形成一条机器支付闭环。它不实现钱包、支付、验凭证或沙箱，只消费接入示例与官方产品能力产生的脱敏事件。

引导演示可切换三个授权级别：

- `L1`：`PSD-PMT-BND + PSD-PAY-INS + A402`。用户逐笔在场、笔笔核身确认，Agent 不可自动扣款；首次使用还展示官方开通与绑定路径，所有二维码均为不可扫码的 UI 占位图；
- `L2`：`ADD + PSD-PAY-DEL + A402`。用户预先明确商品、商户、金额和次数并签发 `SPECIFIED IAC`，完全匹配后由 Agent 自动执行这一笔；
- `L3`：`ADD + PSD-PAY-AUP + A402`。用户只定义任务目标与预算边界，Agent 自主选择服务并执行多笔子支付，每笔重新校验边界。

支付宝公开产品事实仅覆盖页面明确映射的 L1 开通绑定、Agent 支付与 AI 按量付费。本仓库不提供支付宝 L2/L3 接入实现；页面中的 L2/L3 只演示 ACT 2.1 已定稿的协议语义，不代表支付宝产品能力。真实开通、绑定和二维码以[支付宝钱包指南](https://aipay.alipay.com/wallet-guide)及官方支付页面为准。

主页面采用“协议过程舞台”，阅读顺序固定为：

1. 阶段导航：按所选级别展示 PMT-BND/ADD、CID、A402、INS/DEL/AUP 和履约；
2. 参与方：用户、Buyer Agent、收费服务、PSP，以及 L2/L3 的授权服务；
3. 当前消息：明确展示发送方、接收方、消息方向和线上的协议消息；
4. 四层映射：同一动作对应的 ACT 2.1、integration mapping、HTTP/Workflow 与支付宝产品能力；
5. 业务结果：资源保持锁定、成功交付或因异常拒绝交付；
6. 关联与证据：请求、订单、资源、支付交易与履约的脱敏关联链。

引导模式的 L1 成功路径为 16 步，L2/L3 为 14 步；异常场景会在对应恢复状态停止。官方沙箱事件和证据回放使用 Adapter 的 11 步 L1 证据基线，幂等重放共 14 步，避免 UI 说明步骤改变既有证据接口。

## 开箱即用的三种模式

| 模式 | 是否开箱可用 | 数据含义 |
|---|---|---|
| `GUIDED_DEMO` | 是 | 内置说明性数据，用于完整体验页面与讲解路径；始终标注 `NOT PAYMENT EVIDENCE` |
| `LIVE_SANDBOX` | 需要事件 Adapter | 消费官网沙箱与接入示例产生的真实脱敏 SSE；仓库本身不提供沙箱 |
| `SANITIZED_REPLAY` | 需要真实证据文件 | 播放已经通过验证的官网沙箱脱敏记录 |

`GUIDED_DEMO` 解决首次运行时的空白问题，但不会被证据校验器接受，也不能用于任何产品兼容声明。

## 官方沙箱事件 / Replay 的 L1 证据链路

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

状态必须来自实际接入事件，不得由 UI 定时器自动推进为成功。

Guided Demo 还可切换：

- 首次绑定：检查支付能力、打开官方授权二维码、返回不落日志的短时绑定指令；
- L2 定向委托：签发和验证 `SPECIFIED IAC`，再由 DEL 执行指定交易；
- L3 自主支付：签发 `BOUNDED IAC`，每笔检查任务范围和剩余预算后由 AUP 执行；
- 支付结果待确认：查询原交易，禁止重复支付；
- Proof 不匹配：拒绝交付；
- 验款暂不可用：返回可重试错误，禁止猜测成功；
- 幂等重放：完成首轮 11 步后再次提交同一请求，形成 14 步证据；返回既有结果且不重复扣款、交付或履约确认。

## 两种证据运行模式

| 模式 | 事件来源 | 用途 | 展示要求 |
|---|---|---|---|
| `LIVE_SANDBOX` | 官方 Skill/CLI、卖方接入示例、支付宝 Sandbox/OpenAPI | 联调观察 | 显示 Sandbox，不输出凭证和密钥 |
| `SANITIZED_REPLAY` | 已验证链路的脱敏事件记录 | 网络或沙箱异常时备用 | 全程明显显示 Replay，不冒充实时支付 |

## 运行证据校验器

本目录不附带虚构成功数据。第一次沙箱验证后，将每个状态写成一行 NDJSON，再运行：

```bash
npm test
node validate-evidence.mjs /absolute/path/to/sanitized-events.ndjson
```

校验器按场景要求状态严格有序，验证能力来源、非规范性 artifact 方法格式、请求指纹以及订单/资源/金额/交易关联不变量，并拒绝 `MOCK` 模式、明显的密钥字段和完整 `Payment-Proof`。成功场景要求 11 个状态；幂等重放要求 14 个状态和不重复副作用证据；失败场景必须停在对应失败终态。它证明的是演示证据完整性和映射一致性，不代替支付验款或 ACT Conformance。

## 启动 Web 演示台

需要 Node.js 18 或更高版本，不需要安装第三方依赖：

```bash
cd code/web-client/alipay-ai-pay-showcase
npm test
npm run build
npm run demo
```

浏览器打开终端输出的本地地址，默认选择 `GUIDED_DEMO`。选择场景并点击“播放当前场景”即可观看完整状态机，不需要账号、密钥、沙箱或 Replay 文件。

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

Live 事件由接入 Adapter 或演示编排器生成；官方 Skill/CLI、卖方服务和支付宝 OpenAPI 仍是产品行为来源。

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
  "method_id": "act-integration:a402/alipay-ai-pay",
  "method_version": "1.0.0",
  "psp_id": "alipay",
  "endpoint_ref": "endpoint-sha256-redacted",
  "method_schema_ref": "schema-sha256-redacted",
  "capability_source_ref": "capability-sha256-redacted",
  "capability_source_validated": true
}
```

`act-integration:a402/alipay-ai-pay` 是本仓库为 ACT A402 与支付宝 AI 按量付费映射维护的非规范性集成标识，不是支付宝产品报文字段，也不代表 ACT 全局注册。官方沙箱联调证据必须固定使用已发布的映射版本，并同时记录仓库 Commit 和已核验的支付宝产品来源。订单确认使用 `ORDER_CONFIRMED` 信号并提供独立 `commerce_confirmation_ref`；A402 `request_fingerprint` 与支付订单引用由卖方在生成 `Payment-Needed` 时建立，不能伪装成 CID 确认摘要。

宿主 Agent 只有在官方支付宝支付工作流产生对应真实状态后，才能依次提交：

| Adapter 信号 | `observed_from` | Demo 状态 |
|---|---|---|
| `AUTHORIZATION_REQUIRED` | `OFFICIAL_ALIPAY_PAYMENT_SKILL` | `USER_AUTHORIZATION_REQUIRED` |
| `PAYMENT_STARTED` | `OFFICIAL_ALIPAY_PAYMENT_SKILL` | `PAYMENT_PROCESSING` |
| `PAYMENT_SUCCEEDED` | `OFFICIAL_ALIPAY_PAYMENT_SKILL` | `PAYMENT_RESULT_RECEIVED` |
| `PAYMENT_PENDING` | `OFFICIAL_ALIPAY_PAYMENT_SKILL` | `PAYMENT_PENDING` |

`PAYMENT_SUCCEEDED` 必须提供脱敏 `transaction_ref` 和 `proof_ref`；`PAYMENT_PENDING` 必须提供 `recovery_action`。错误来源、能力声明来源未验证、关联事实漂移、敏感字段或乱序事件都会被拒绝。

#### 卖方接入 Adapter

在卖方服务的本地环境中增加：

```bash
ACT_DEMO_BRIDGE_URL=http://127.0.0.1:4173/events
ACT_DEMO_VALIDATION_ID=E2E-YYYYMMDD-NNN
ACT_DEMO_CORRELATION_REF=corr-sha256-redacted
```

启用后，卖方接入示例会以非阻断方式输出：

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

## 复用的接入与样例

- [买方 Agent Payment](../../../integrations/alipay/buyer-agent/README.md)
- [卖方 Metered REST Provider](../../../integrations/alipay/seller-java/README.md)
- [通用本地 A402 样例](../../samples/local-a402/README.md)

Demo 不能复制这些目录中的协议或产品逻辑。需要改变支付处理时先修改并验证相应接入，再由 Demo 消费其事件。

沙箱联调使用 [AIPay 官网接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)；完成后按 [ACT 沙箱验证补充](../../../integrations/alipay/validation/README.md)生成脱敏证据。

## 安全边界

不得进入 Demo 制品、日志、录屏或 Replay 数据：

- 私钥、公钥文件路径以外的密钥内容；
- 绑定码、支付密码、访问令牌和 `app_auth_token`；
- 完整 `Payment-Proof` 或 `client_session`；
- 可重放 HTTP 请求；
- 完整订单号、交易号和用户标识。

## ACT 2.1 与产品事实

ACT 2.1 使用 `method_id`、`CID-PCA-NEG` 和 `Payment-Validation`。Demo 在界面中并列展示 ACT 语义和支付宝实现映射，不修改支付宝官网产品报文；对于 `Payment-Validation`，当前只展示：

```text
ACT 2.1 Payment-Validation → Alipay payment.verify result
```

这不是在声明支付宝官网已支持同名响应 Header。产品接入、沙箱与正式接口事实始终以 AIPay 官网为准。

## 能力边界

Guided Demo、Live Bridge、多场景状态机、Buyer Runtime Adapter、卖方接入 Adapter、完整证据导出和 Replay 准备工具均已提供。Guided Demo 是说明性数据；Live 与 Replay 只有在接入官方 Skill/CLI 和官网沙箱产生真实脱敏事件后，才能作为特定版本的互操作证据。
