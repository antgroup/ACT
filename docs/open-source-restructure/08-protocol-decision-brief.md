# ACT 双侧机器支付协议决策简报

> 状态：Partially aligned / Non-normative
> 面向：观岳牵头的 ACT Core 修订  
> 产品基线：Alipay AI Pay 双侧能力接入契约 v0.1  
> 建议评审日期：2026-07-25

## 1. 评审目标

本简报不要求一次性完成 ACT 全部修订，只请求决定外滩大会版本所需的最小边界，使以下公开产品能力可以被准确映射：

- 买方 Agent 通过官方工作流级 Skill/CLI 完成授权、支付和资源请求恢复。
- 卖方服务通过 HTTP 402 出账、验款、防重、交付和确认履约。
- 双方能够在同一交易中关联 ADD、CID、PSD、TSD 证据。

每项决定应产出：选择的方案、Core/Profile/Binding 归属、兼容性影响、需要更新的规范和测试。

## 2. 待决定事项总览

| ID | 决策 | 推荐方向 | 阻塞产物 |
|---|---|---|---|
| PD-001 | 402 与 INS/DEL/AUP 的关系 | 修订方向已对齐：候选 `PSD-PAY-A402` 与三种场景组件解耦 | PSD Core、HTTP Binding |
| PD-002 | CID 交易确认与 `Payment-Needed` 的关系 | `Payment-Needed` 引用或携带已确认交易事实，不直接等同整个 CID 对象 | CID/PSD 边界、Profile |
| PD-003 | 工作流级 Binding 能否封装多步协议 | 允许，但必须声明覆盖组件、输入输出和证据 | Skill/CLI Binding |
| PD-004 | Payment Validation 是否为独立语义 | Core 定义验证结果语义，Binding 可在工作流内部消费而不暴露完整消息 | PSD 状态机、测试 |
| PD-005 | 双侧履约调用如何解释 | 先完成支付宝产品确认，再决定单一权威回执和观察事件 | PSD/TSD、端到端实现 |
| PD-006 | 跨域最小关联标识 | Core 定义关联责任，Profile 映射产品标识，不强制产品报文承载所有 ACT ID | 四域追踪、TSD |
| PD-007 | 恢复动作如何表达 | 结构化 `valid_next_actions`，同时声明执行者和约束 | Common Message、错误模型 |

## 3. PD-001：402 与授权执行级别

ACT v2.0 官网当前把 `Payment-Needed`、`Payment-Proof`、`Payment-Validation` 的 402 框架放在 `PSD-PAY-AUP`，但首期支付宝公开链路是用户逐笔确认，执行语义更接近 `PSD-PAY-INS`，未来还需要支持 `PSD-PAY-DEL`。

方案：

- A：402 只属于 `PSD-PAY-AUP`，INS/DEL 分别定义另一套交互。
- B：抽出产品无关的支付要求、凭证和验证框架，由 INS/DEL/AUP 选择不同授权门禁和执行规则。
- C：保持现状，由 Product Profile 声明跨组件复用。

最新 v2.1 修订方向已选择 B，并提出独立的候选组件 `PSD-PAY-A402`。支付要求和凭证交换描述“如何完成一次机器支付”，INS/DEL/AUP 描述“凭什么授权执行”。剩余决策不再是“是否抽出”，而是正式编号、版本、公共状态机、Schema、与 v2.0 AUP 的兼容迁移，以及关联 MCP/API 接口方式的边界。

## 4. PD-002：CID 交易确认与支付要求

卖方 `Payment-Needed` 包含资源、金额、币种、商户订单和收款方，但它是否已经构成 `CID-CART-CFM` 的全部交易确认结果尚不明确。

方案：

- A：`Payment-Needed` 就是交易确认对象。
- B：交易确认对象独立存在，`Payment-Needed` 只引用它。
- C：Core 定义最小交易事实，Binding 可以引用或内嵌，Profile 说明具体映射。

推荐 C。HTTP Header 可以保持紧凑，同时允许 Skill、MCP 或未来 Binding 使用不同封装；无论封装形式如何，金额、资源、商户和订单必须指向同一份已确认事实。

## 5. PD-003：工作流级 Binding

官方 Skill/CLI 会封装账单保存、支付、状态查询、Proof 提交、原请求恢复、资源透传和履约动作。宿主 Agent 不一定直接看到每个 Core 消息。

方案：

- A：Binding 必须一条命令对应一个 Core 消息。
- B：Binding 可以封装多个组件，但必须提供覆盖声明和可验证证据。
- C：把 Skill 工作流整体放入 Product Profile，不定义 Binding 覆盖规则。

推荐 B。Binding manifest 至少声明：

- 覆盖的 ACT 组件和版本。
- 需要宿主提供的意图、交易和原请求上下文。
- 哪些中间对象对宿主可见或被内部封装。
- 可能返回的终态、中间态和恢复动作。
- 如何生成不泄露敏感数据的合规证据。

## 6. PD-004：Payment Validation

卖方必须调用支付宝接口并核对原账单，但官方 Skill/CLI 可能只把最终资源或状态返回宿主 Agent。是否要求卖方将完整验证结果回传买方尚不明确。

推荐 Core 定义验证结果的最小语义和卖方交付门禁；HTTP 或 Skill/CLI Binding 可以在内部消费验证结果，只向买方暴露足以继续任务的状态。TSD/证据层应能证明验证发生，但不要求公开敏感 Proof 或完整产品响应。

## 7. PD-005：履约确认与可信事件

已知冲突：

- 卖方官网指南要求资源交付后调用 `alipay.aipay.agent.fulfillment.confirm`。
- 买方官方 Skill 定义资源获取后的 `402-buyer-fulfillment-ack`。

评审前需要支付宝产品确认两者是否是同一接口、是否允许重复、各自表达“卖方已交付”还是“买方已收到”，以及最终权威状态。

暂定原则：

- PSD 支付完成、业务资源交付、产品履约确认和 TSD 事件是不同语义。
- 产品确认前不删除任意一侧调用，也不把两次调用解释成两个独立履约。
- 一致性测试必须使用同一 `trade_no` 验证重复调用结果。

## 8. PD-006：跨域标识

建议 Core 规定以下关联责任，而不强制支付宝产品报文直接携带所有 ACT ID：

```text
intent_id
  → optional delegation_id
  → out_trade_no + resource_id + service_id
  → trade_no + payment_proof
  → fulfillment evidence
```

- `intent_id`、`delegation_id` 属于 ACT 侧上下文。
- `out_trade_no`、`resource_id`、`service_id` 由卖方交易上下文提供。
- `trade_no`、`payment_proof` 属于支付宝产品结果。
- Profile 定义字段映射；TSD 定义事件关联和证据来源。

## 9. PD-007：恢复动作

建议 `valid_next_actions` 是结构化集合，每个动作至少包含：

- 动作类型，例如 query、authorize、retry-same、new-requirement、do-not-deliver、abort。
- 允许执行的角色。
- 是否必须复用幂等输入。
- 最早重试时间、最大次数或截止时间（适用时）。
- 是否需要重新获得用户授权。

仅提供 retryable 布尔值不足以避免重复支付和重复履约。

## 10. 评审输出模板

| 决策 ID | 结论 | 负责人 | 日期 | Core 影响 | Profile/Binding 影响 | 测试影响 |
|---|---|---|---|---|---|---|
| PD-001 | Direction aligned; publication details pending | 观岳 | 2026-07-22 | 候选 `PSD-PAY-A402` | Profile/Binding 改为引用接入协议 | 待状态机与 Schema |
| PD-002 | Pending | 观岳 |  |  |  |  |
| PD-003 | Pending | 观岳 |  |  |  |  |
| PD-004 | Pending | 观岳 |  |  |  |  |
| PD-005 | Pending product input | 观岳 + 支付宝产品 |  |  |  |  |
| PD-006 | Pending | 观岳 |  |  |  |  |
| PD-007 | Pending | 观岳 |  |  |  |  |
