# Showcase 事件格式

> 状态：Demo event format / Non-normative。该格式只服务于演示编排与证据审查，不是 ACT 协议消息。

本格式只接受 `LIVE_SANDBOX` 和 `SANITIZED_REPLAY` 作为证据模式。Web 演示台内置的 `GUIDED_DEMO` 是说明性 UI 数据，校验器会拒绝将其作为支付证据。

证据文件使用 NDJSON，每行一个对象。成功闭环必须按顺序包含 11 个状态：

```json
{"sequence":1,"state":"CAPABILITY_NEGOTIATED","scenario":"SUCCESS","mode":"LIVE_SANDBOX","source":"buyer-agent-quickstart","environment":"SANDBOX","occurred_at":"2026-07-22T12:00:00Z","evidence_ref":"E2E-20260722-001#step-1","correlation_ref":"corr-sha256-a1b2","method_id":"act-integration:a402/alipay-ai-pay","method_version":"1.0.0","psp_id":"alipay","endpoint_ref":"endpoint-sha256-redacted","method_schema_ref":"schema-sha256-redacted","capability_source_ref":"capability-sha256-redacted","capability_source_validated":true}
```

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

| 字段 | 要求 |
|---|---|
| `sequence` | 从 1 开始连续递增 |
| `state` | 必须属于所选场景的状态机，并严格有序 |
| `scenario` | `SUCCESS`、`PAYMENT_PENDING`、`PROOF_MISMATCH`、`VERIFICATION_UNAVAILABLE` 或 `IDEMPOTENT_REPLAY`；缺省为 `SUCCESS` |
| `mode` | 全文件统一为 `LIVE_SANDBOX` 或 `SANITIZED_REPLAY` |
| `source` | 产生该事件的接入示例、官方能力或验款步骤；不得为 Mock |
| `environment` | Live 模式必须为 `SANDBOX` |
| `occurred_at` | 可解析的 ISO 8601 时间，且不得倒序 |
| `evidence_ref` | 指向脱敏验证记录的引用，不得包含凭证或可重放 URL |
| `correlation_ref` | 同一链路共享的脱敏关联引用；不得使用完整业务订单号或交易号 |
| `sanitized` | Replay 模式必须为 `true` |
| `origin_validation_id` | Replay 模式必须引用原沙箱验证编号 |
| `method_id`、`method_version` | 所有状态必须保持一致；ID 使用非规范性 A402 artifact 命名空间格式，版本使用 SemVer |
| `psp_id`、`endpoint_ref`、`method_schema_ref` | `CAPABILITY_NEGOTIATED` 必填，使用脱敏引用展示协商结果 |
| `capability_source_ref`、`capability_source_validated` | 证明能力声明来自已验证来源；未验证不得进入支付 |
| `commerce_confirmation_ref` | `ORDER_CONFIRMED` 必填，是独立 CID 商业确认引用，不是 A402 请求指纹 |
| `request_fingerprint` | 从 `PAYMENT_REQUIRED` 到验款、交付保持一致，格式为 `sha-256:<base64url-no-padding>` |
| `order_ref`、`resource_id` | 从 `PAYMENT_REQUIRED` 开始稳定关联原账单与收费资源 |
| `proof_ref`、`transaction_ref` | 支付成功后必填，只允许脱敏引用 |
| `delivery_ref`、`fulfillment_ref` | 分别记录资源交付和产品履约确认，二者不得互相替代 |

向本地 Live Bridge 的 `POST /events` 提交事件时，只需发送 `state`、`source`、`evidence_ref` 和允许的展示字段。Bridge 会补充 `sequence`、`mode=LIVE_SANDBOX`、`environment=SANDBOX` 和 `occurred_at`。这些是观察器元数据，不代替产品交易时间。

完整链路可通过 `GET /events/export` 导出；链路未到合法终态时接口返回 `409 evidence_incomplete`，避免将半条链路误作成功证据。Buyer Agent 应优先使用 [`buyer-event-adapter.mjs`](buyer-event-adapter.mjs) 接入结构化运行时状态，而不是直接拼装 Demo 状态。

页面允许下列可选展示字段，它们必须是脱敏摘要：

| 字段 | 用途 |
|---|---|
| `amount`、`currency` | 展示账单金额，不表达金额单位换算规则 |
| `resource_id` | 展示脱敏资源标识 |
| `goods_name`、`seller_name` | 展示用户可理解的交易摘要 |
| `result_summary` | 展示不含敏感数据的交付或校验结论 |
| `method_id`、`psp_id` | 展示支付方法与 PSP 的发现、选择和回显 |
| `request_ref`、`request_digest`、`http_method` | 证明支付前后的原请求保持一致 |
| `order_ref`、`transaction_ref`、`fulfillment_ref` | 构成订单、支付与履约的脱敏关联链 |
| `validation_mapping` | 说明 ACT 2.1 `Payment-Validation` 语义与支付宝 `payment.verify` 的产品映射 |
| `profile_mapping` | 明确当前事实来自 Alipay integration mapping，而不是支付宝报文中的 ACT artifact 字段 |
| `idempotent_replay`、`payment_action`、`delivery_action`、`fulfillment_action` | 第二次请求证明没有新支付、没有重复非幂等交付、没有重复履约确认 |
| `recovery_action` | 失败终态对应的机器可执行恢复动作 |

失败链路是合法证据，不得补造成功事件：

- `PAYMENT_PENDING`：终止于 `PAYMENT_PENDING`，查询原交易且不得再次付款；
- `PROOF_MISMATCH`：终止于 `PROOF_REJECTED`，不得交付；
- `VERIFICATION_UNAVAILABLE`：终止于 `VERIFICATION_UNAVAILABLE`，按原交易重试验款且不得交付。
- `IDEMPOTENT_REPLAY`：先完成 11 步正常链路，再追加第二次 `RESOURCE_REQUEST_RETRIED → PAYMENT_VERIFIED → RESOURCE_DELIVERED`；最终事件必须声明 `idempotent_replay=true`、`NO_NEW_PAYMENT`、`RETURN_PRIOR_RESULT` 和 `NOT_REPEATED`。

TSD 证据不属于上述 11/14 步成功条件。若实现异步形成脱敏 TSD 证据，可以使用独立 `tsd_evidence_ref` 展示，但不得由 `fulfillment.confirm` 自动推导或冒充。

页面不显示任意扩展字段，并递归拒绝明显的密钥、令牌、完整 Proof、`client_session`、绑定码和密码字段。

不要写入业务响应全文。金额、订单和资源关联结论应保存在[端到端验证证据](../../../integrations/alipay/validation/evidence-template.md)中，事件仅保留引用。
