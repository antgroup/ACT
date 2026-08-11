# A402 Candidate 机器契约决议（2026-08-03）

> 状态：Candidate Accepted / Non-normative  
> 适用范围：ACT 2.1 Candidate Working Draft  
> 不构成：正式 DWG Accepted ADR、Stable、Recommendation 或 Conformance

## 1. 决议依据

本记录依据 2026-08-03 完成版《支付服务域》已经明确的 A402 独立性、三类 Header、Base64URL UTF-8 JSON、`protocol` + `method` 信封、14 个基础字段、六状态与十一类错误语义，关闭阻塞开源 Candidate 机器契约的工程选项。

用户对“先做 1—3”的实施授权用于接受本记录的 **Candidate 工程选择**。由于当前没有公开 Issue、PR、DWG 会议纪要和正式签署，本记录不得升级为治理状态 `Accepted`。

## 2. 选择结果

| 决策 | 选择 | Candidate 结论 |
|---|---|---|
| DP-A402-001 | B | Draft 2020-12 JSON Schema 是 HTTP-first Candidate 的唯一机器源；fixtures 和 validator 必须由其约束并执行漂移检查。 |
| DP-A402-002 | Source-settled | 三类 ACT 原生 Header 统一使用 Base64URL UTF-8 JSON 和 `protocol` + `method` 信封；`Payment-Validation` 可选。 |
| DP-A402-003 | A | `method_id` 使用稳定、全局命名空间标识；`method_version` 独立使用 SemVer。三类载荷均回显二者。 |
| DP-A402-004 | B | 原请求使用规范化请求指纹关联；非幂等操作另需幂等键。Proof 不保存或回放授权 Header、Cookie 和逐跳 Header。 |
| DP-A402-005 | B | 支付验凭、资源交付、方法履约确认和 TSD 证据是四个可关联但不可互相冒充的事实。 |
| DP-A402-006 | C | 六状态保留为公共兼容投影；机器错误另携阶段、可重试性和合法下一动作。 |
| DP-A402-007 | C | `out_trade_no`、`resource_id`、金额与币种构成最小商业关联；可选引用独立 CID 确认对象，但不上传完整购物车。 |
| DP-A402-008 | B | 开源 Candidate 的可执行基线仅声明 INS/L1；DEL/L2、AUP/L3 保持 Validation-pending，直到公开 ASL 依赖和安全证据完备。 |
| DP-A402-009 | B | Workflow Binding 可封装多步，但必须发布覆盖、输入、可观察结果、证据和脱敏规则。 |

## 3. 请求指纹和防重放规则

请求指纹为 `sha-256:<base64url-no-padding>`，输入是下列 UTF-8 行按顺序连接后的 SHA-256：

```text
UPPERCASE_HTTP_METHOD\n
normalized_target_uri\n
lowercase_content_type_or_empty\n
sha256_base64url_of_body
```

`normalized_target_uri` 的 scheme 和 host 小写、移除默认端口、保留 path 和 query；不得包含 fragment。不得把 Authorization、Cookie、Proxy-Authorization、Proof、签名密钥、逐跳 Header 或完整可重放请求写入指纹材料或公开证据。

- `Payment-Needed` 生成并声明 `request_fingerprint`。
- `Payment-Proof` 必须回显同一指纹、`out_trade_no` 和 `resource_id`。
- 非 GET/HEAD/OPTIONS 的交付请求必须使用业务幂等键；Binding 可以承载该键，但不得把它等同于支付交易号。
- 防重复履约的权威占用键是 `(method_id, trade_no, out_trade_no, resource_id)`；交付幂等键是 `(method_id, trade_no, request_fingerprint)`。
- 已使用交易记录至少保存到 `max(expires_at, fulfillment/evidence retention deadline)`；具体时长由方法 Profile 声明。期限未声明时实现不得声称跨重启防重放。
- 并发请求必须原子地占用权威键；重复请求返回既有结果或明确冲突，不重复非幂等交付。

## 4. 生命周期触发

| 转移 | 触发 |
|---|---|
| `CREATE → WAIT_BUYER_PAY` | 已持久化账单并发送 `Payment-Needed` |
| `WAIT_BUYER_PAY → WAIT_SELLER_FULFILLMENT` | PSP 或受信验证方权威确认支付及 Proof 有效 |
| `WAIT_BUYER_PAY → TRADE_CLOSED` | 账单过期、取消或支付终态失败 |
| `WAIT_SELLER_FULFILLMENT → WAIT_BUYER_RECEIPT` | 对应资源交付已幂等提交 |
| `WAIT_SELLER_FULFILLMENT → TRADE_CLOSED` | 已完成退款/补偿且不再交付 |
| `WAIT_BUYER_RECEIPT → TRADE_FINISHED` | 方法规定的履约或买方回执已确认 |
| `WAIT_BUYER_RECEIPT → TRADE_CLOSED` | 已完成取消、退款或终止补偿 |

终态不得反向转移。超时或网络错误本身不证明支付失败；未知结果必须先查询权威状态，再选择错误词典允许的下一动作。

## 5. 兼容、安全与迁移后果

- Core Candidate Schema 不直接替代支付宝产品 Schema；Alipay Profile 继续按官网 Base64/Base64URL、字段和 API 事实映射。
- `Payment-Validation` 的缺失不能推断支付或交付失败；产品 Profile 可用服务端验凭结果映射其语义。
- 新增 `method_version`、请求指纹、结构化错误和阶段结果属于 Candidate 冻结，不得回写到已经移除的 ACT 2.0。
- L2/L3 的结构可以公开阅读，但不得宣称完成安全验证或支付宝产品兼容。
- 正式 DWG 若否决任一选择，必须用新的 ADR 和 Schema `$id`/版本迁移，不能静默改写现有 Candidate 制品。

## 6. 必须验证的资产

- 三类 Header 解码载荷 Schema；
- 有效和无效 fixtures；
- Base64URL 无填充编码往返；
- 六状态允许转移和终态约束；
- 十一类错误与合法恢复动作；
- 请求指纹一致性、Proof 关联、重放和非幂等幂等键；
- Product Profile 不把 Core Candidate 字段伪装成支付宝官网字段。

正式治理入口仍为[A402 决策包](protocol-decision-brief.md)。
