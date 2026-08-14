# ACT 2.1 委托授权域

> **状态：ACT 2.1 Specification / Final / Normative**
> **协议内容已经定稿；是否符合本规范需要独立 Conformance 证据。**
> 版本基线：2026-08-11（UTC+8）

委托授权域（Authorization & Delegation Domain，ADD）规定用户意图的表达、确认、结构化约束、授权凭证签发和生命周期管理，为 Agent 代表用户开展商业活动提供可表达、可约束、可验证、可追溯的授权基础。

本域是 ACT 2.1 的规范性委托授权域文本。本 Release 中的本文是 2.1 版本化正文；[ACT Protocol 委托授权域](https://www.act-protocol.com/documentation/delegation)是持续更新的公开入口。

## 1. 范围与边界

ADD 覆盖：

- 用户原始意图的获取、澄清、确认和结构化表达；
- 意图结构化结果（Intent Structured Result，ISR）的生成与引用；
- 意图授权凭证（Intent Authorization Credential，IAC）的构造、签发和封装；
- IAC 的生命周期状态、状态迁移和有效性检查。

ADD 不规范前端样式、提示词工程、模型推理和多模态识别算法，也不规定身份基础设施、私钥托管或签名服务的内部实现。商品发现和交易确认属于 CID；支付与资金处理属于 PSD；存证事件结构和治理属于 TSD。

## 2. 组件与核心对象

| 组件 | 作用 | 主要输出 |
|---|---|---|
| `ADD-INT-ICS` | 获取、澄清、确认并结构化用户意图 | 用户原始意图、ISR、`intent_id` |
| `ADD-IAC-ISS` | 从最终 ISR 选择授权边界，完成规范化、签名和封装 | IAC、`delegation_id` |
| `ADD-IAC-LCM` | 管理 IAC 的有效、暂停、恢复、吊销和到期 | 可查询的授权状态 |

| 对象或标识 | 规范语义 | 下游引用 |
|---|---|---|
| 用户原始意图 | 用户以自然语言或其他方式表达的原始商业意图 | ADD 内部及必要的事后核查 |
| `intent_id` | 贯穿意图确认、ISR 和跨域流程的意图标识 | CID、PSD、TSD |
| ISR | 用户目标、约束和边界的结构化规则表达 | IAC 签发、CID 规则检验 |
| IAC | 对授权边界进行可验证封装后的凭证 | PSD 的 DEL/AUP、TSD |
| `delegation_id` | 一份 IAC 及其生命周期的唯一标识 | LCM、PSD、TSD |
| 授权状态 | IAC 当前是否可以被接受 | CID、PSD 及其他核验方 |

## 3. `ADD-INT-ICS`：意图获取及结构化表达

### 3.1 用户原始意图

`conversation_history` 用于承载用户原始内容，或其可校验摘要和上下文引用：

| 字段 | 存在性 | 规范语义 |
|---|---|---|
| `user_intent_raw` | 条件必备 | 与 `user_intent_raw_digest` 至少一项存在 |
| `user_intent_raw_digest` | 条件必备 | 原始意图摘要；与 `user_intent_raw` 至少一项存在 |
| `input_mode` | 可选 | `TEXT`、`VOICE`、`IMAGE`、`INTERACTIVE_CARD`、`OTHER`，可组合 |
| `context_ref` | 条件必备 | 有摘要时必备；所指内容应能得到相同摘要 |

扩展输入模式不得改变既有字段的基础语义。完整原文不便传递时，可以只传摘要和引用，但实现方仍应保护原始记录的可验证性、访问控制和留存周期。

### 3.2 ISR 数据字典

ACT 2.1 将 ISR 定义为数据字典，而不是冻结的 wire Schema：它规定名称、类型和语义，但不统一规定本表全部字段的存在性。场景规则、IAC 签发规则和下游组件负责进一步约束。

| 字段 | 规范语义 |
|---|---|
| `conversation_history` | 用户原始意图对象 |
| `intent_id` | 当前意图链路内唯一标识 |
| `delegation_mode` | `SPECIFIED` 或 `BOUNDED` |
| `validity_start_time` / `validity_end_time` | ISO 8601 UTC 有效时间窗，结束晚于开始 |
| `max_total_amount` / `currency` | 授权总金额上限及 ISO 4217 币种 |
| `allowed_payment_methods` | 允许的支付方式 |
| `agent_id` | 执行 Agent 标识 |
| `user_confirmation_method` / `user_confirmation_timestamp` | 用户确认方式与时间 |
| `ext` | 标准和私有扩展命名空间 |

`SPECIFIED` 用于目标、商户或交易边界已明确的定向委托；`BOUNDED` 用于用户只确定任务目标和行为边界、具体选择由 Agent 在边界内决定的委托。

### 3.3 标准扩展

| 扩展块 | 字段 |
|---|---|
| `ext.commerce` | `max_single_amount`、`min_single_amount`、`allowed_categories`、`forbidden_categories`、`allowed_merchants`、`forbidden_merchants` |
| `ext.agent_behavior` | `price_deviation_tolerance`、`price_deviation_action`、`on_payment_failure`、`max_retry_count` |
| `ext.fulfillment` | `delivery_time_requirement`、`delivery_address` |

`price_deviation_action` 使用 `PAUSE_AND_NOTIFY` 或 `AUTO_CANCEL`；`on_payment_failure` 使用 `AUTO_RETRY` 或 `CANCEL`。`ext.vendor_private` 可承载私有扩展，但不得改变核心字段或标准扩展的语义；不认识且不影响核心约束的私有字段可以忽略。

### 3.4 处理要求

1. 用户侧 Agent 获取原始意图并形成 `conversation_history`。
2. Agent 生成 ISR 草稿；遇到歧义、关键约束缺失或冲突时进行澄清并更新草稿。
3. Agent 以用户可理解的方式展示核心目标和边界，取得确认后生成最终 ISR。
4. 后续需要 IAC 时，`ADD-IAC-ISS` 以最终 ISR 为输入依据。
5. 原始意图或其可验证引用宜在合理争议周期内受控留存；具体时长和介质由实现方依据法律与治理要求决定。

## 4. `ADD-IAC-ISS`：意图授权凭证签发

### 4.1 签发边界

IAC 不是最终 ISR 的无差别复制。只有构成授权边界、执行约束和后续核验依据的内容才进入待签名载荷。用户对最终 ISR 的一次确认可以直接触发签发，不宜因流程设计要求用户对同一事项重复确认。

签发前应已经明确受托 Agent、委托模式、有效期和主要约束；签名私钥必须由受控密钥管理能力托管，并在可信执行环境或等效受控环境中使用，业务应用不得明文持有签发私钥。

### 4.2 IAC 待签名载荷

| 字段 | 存在性 | 规范语义 |
|---|---|---|
| `delegation_id` | 必备 | IAC 与授权生命周期的唯一标识 |
| `intent_id` | 可选 | 与上游 ISR 建立关联 |
| `conversation_history` | 条件必备 | 无 `intent_id` 且直接携原始意图对象时使用 |
| `delegator_identity` | 必备 | 委托人或代表其签发的主体标识 |
| `agent_id` | 必备 | 被授权执行动作的 Agent 标识 |
| `delegation_mode` | 可选 | `SPECIFIED` / `BOUNDED`；缺省为 `SPECIFIED` |
| `validity_start_time` / `validity_end_time` | 必备 | ISO 8601 UTC 授权时间窗 |
| `max_total_amount` | 必备 | 授权总金额上限 |
| `currency` | 可选 | ISO 4217；缺省为 `CNY` |
| `allowed_payment_methods` | 可选 | 进入签名范围时沿用 ISR 语义 |
| `user_confirmation_method` / `user_confirmation_timestamp` | 可选 / 条件必备 | 用户确认方式与时间 |
| `source_isr_digest` | 可选 | 上游 ISR 或约定摘要范围的摘要值 |
| `ext` | 可选 | 影响授权核验的 ISR 扩展约束 |

是否把某一 `ext` 字段纳入签名范围，取决于它是否影响后续授权核验；不要求将 ISR 的所有扩展字段全部签入 IAC。

### 4.3 最终 IAC 与签名

最终 IAC 可由以下部分组成：`protected_header`、`credential_metadata`、`credential_subject`、`proof`、`status_reference`，以及高风险场景可选的 `control_proof_ref`。来源只定义这些部分的语义边界，暂不冻结字段级最终封装。

签名前必须对约定签名范围执行确定性规范化；JSON 载荷宜采用 RFC 8785 JCS。同一部署的签发方和验证方必须保持字段名称、规范化规则和签名输入边界一致。实现可以映射到可验证凭证类封装、JWS 类封装或等价形式；W3C VC-JWT 是推荐方式之一，不是唯一格式。

## 5. `ADD-IAC-LCM`：生命周期管理

### 5.1 状态和转移

| 状态 | 语义 | 可恢复性 |
|---|---|---|
| `Active` | 在有效时间窗内且未暂停/吊销，可供后续使用 | — |
| `Suspended` | 临时不可使用 | 可恢复到 `Active` |
| `Revoked` | 永久吊销 | 终态 |
| `Expired` | 到达 `validity_end_time` | 终态 |

允许的迁移是：`Active → Suspended`、`Suspended → Active`、`Active/Suspended → Revoked`、`Active/Suspended → Expired`。`Revoked` 和 `Expired` 不得恢复。

### 5.2 状态处理和校验

- `Suspended`、`Revoked` 或 `Expired` IAC 不得继续用于商业交互、支付执行或授权校验。
- 暂停、恢复、吊销和到期宜异步上报 `act:delegation:delegation-suspended`、`delegation-resumed`、`delegation-revoked`、`delegation-expired`；事件结构由 TSD 定义。
- 引用 IAC 的处理方至少检查有效时间窗、当前状态为 `Active`，以及是否存在已知暂停、吊销或到期结果。
- 最终判断前应通过 `status_reference` 获取当前状态。状态服务暂时不可达时，可使用本地最近一次成功结果和 `validity_end_time` 做临时风险控制，但这不是永久忽略状态检查的依据。

## 6. 当前机器契约边界

ACT 2.1 明确了数据字典、存在性和处理语义，但没有发布 ISR/IAC JSON Schema、封装版本、算法套件、状态查询协议、事件 Schema 或标准错误对象。本仓库不从示例或描述推造这些机器契约。

## 7. 来源

- 当前 ADD 协议事实源：[委托授权域](https://www.act-protocol.com/documentation/delegation)
- 跨域场景参考：[典型场景与业务流程](https://www.act-protocol.com/documentation/scenarios)
- CID：[商业交互域](https://www.act-protocol.com/documentation/commerce)
- PSD：[支付服务域](https://www.act-protocol.com/documentation/payment)
- TSD：[信任服务域](https://www.act-protocol.com/documentation/trust)
