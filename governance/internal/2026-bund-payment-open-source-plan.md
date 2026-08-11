# 2026 外滩大会支付服务域开源执行计划

> 状态：Active / Non-normative；执行周期：2026-07-22—2026-09-12；目标发布日期：2026-09-04

## 1. 目标

大会前完成 ACT v2.1 支付服务域与支付宝 AI 付公开产品的对齐，交付一条开发者可理解、可运行、可验证、可演示的机器支付闭环。

大会最终互操作主张限定为：

> 实现 ACT v2.1 A402，采用 Alipay AI Pay Profile 和声明的 Binding，并通过支付宝沙箱验证，即具备接入支付宝 AI 付的兼容基础。

仅实现 ACT Core、仅安装买方 Skill、仅运行本地单元测试或仅返回模拟 402，均不能声明已接入支付宝 AI 付。但 ACT Candidate 和 Alipay Profile Preview 可以在明确标注非规范性、未通过沙箱的前提下独立发布。

## 2. 大会验证基线

```text
PSD-PAY-INS（L1 用户逐笔确认）
  + PSD-PAY-A402（HTTP 402 支付接入协议）
  + HTTP A402 Binding
  + Alipay AI Pay Profile 0.9 Preview
  + 支付宝官方 Agent Payment Skill/CLI
  + 支付宝 AI 按量付费 Sandbox/OpenAPI
```

支付场景与接入协议必须解耦：INS、DEL、AUP 分别描述 L1、L2、L3 场景语义，A402 描述可被三个场景引用的 HTTP 支付接入交互。MCP 和 OpenAPI 是产品或运行时接入形式，大会版本不为它们另造一套 ACT 支付协议。

大会只对 L1 + A402 作端到端兼容验证。DEL/L2 和 AUP/L3 可以进入协议结构，但在官方公开能力和沙箱证据完备前不作已验证产品兼容声明。

## 3. 发布物

| 层次 | 大会交付 | 负责人 | 发布状态 |
|---|---|---|---|
| 协议 | ACT v2.1 支付服务域、A402、INS/DEL/AUP 修订和兼容边界 | 观岳 | `2.1 Candidate Working Draft / Non-normative`；正式 SEP Candidate 需治理批准 |
| Product Profile | Alipay AI Pay 能力、字段、状态、错误和公开来源映射 | 念箴 | `0.9 Preview` |
| Binding | 公共 HTTP A402 Binding；支付宝专属 Skill/CLI 工作流 Binding | 观岳 / 念箴 | Preview |
| Quickstart | Agent Payment、Metered REST Provider、End-to-end 402 | 念箴 | `0.9` |
| Demo | Alipay AI Pay Sandbox Showcase | 念箴 | Live Sandbox + Sanitized Replay |
| 证据 | 正向、异常、重试、防重放和履约确认的脱敏记录 | 念箴 | 发布快照 |

## 4. 协议侧最小完成范围

`PSD-PAY-A402` 在 8 月意见征求前至少明确：

- HTTP 402 触发和响应约束；
- `Payment-Needed`、`Payment-Proof` 和验证结果的最小语义；
- Header 编码、字段格式和完整性保护；
- `method_id` 的发现、选择、回显和不支持处理；
- 订单、资源、交易和原请求之间的绑定；
- 待支付、处理中、成功、失败和过期状态；
- 超时、幂等、防重放、重复支付和重复履约规则；
- 原请求恢复、资源交付和履约确认的责任边界；
- 标准错误、恢复动作和 INS/DEL/AUP 引用方式。

协议负责人决定 Core 和 A402 语义。Profile、Quickstart 和 Demo 只能实现或记录候选结论，不能通过代码反向决定协议。

## 5. Product Profile 工作包

`integrations/profiles/alipay-ai-pay/` 负责把协议落到支付宝产品：

- `capabilities/`：Agent 支付、AI 按量付费和双侧能力契约；
- `mappings/`：四域、字段、生命周期和错误映射；
- `integrations/bindings/`：支付宝专属 Skill/CLI 工作流封装；
- `sources/`：官网资料、快照和事实审计。

8 月必须关闭或明确降级以下差异：

- Proof 使用 Base64 还是 Base64URL；
- 官网没有独立 `Payment-Validation` Header 时如何映射验证结果；
- 金额单位和字符串格式；
- `client_session`、`out_trade_no`、`trade_no`、`resource_id` 的关联规则；
- 官方 Skill/CLI 是否向宿主 Agent 暴露 Proof；
- 未知支付结果的查询和防重复支付；
- 履约确认失败后的持久化重试责任。

## 6. Quickstart 计划

### 6.1 买方 Agent

位置：`code/examples/alipay/agent-payment/`

必须证明：

- 干净环境可以检查并安装官方 Payment Skill/CLI；
- Agent 能识别 402 并保留原始 Method、URL、Body 和必要 Header；
- 用户能够理解并授权真实沙箱支付；
- 结果未知时先查询，禁止再次付款；
- Proof 可以由官方工作流内部提交，不要求开发者复制敏感凭证；
- 成功后恢复原请求，失败时返回结构化结果。

### 6.2 卖方服务

位置：`code/examples/alipay/metered-rest-provider/`

必须证明：

- 返回真实 `402 + Payment-Needed`；
- 按官网要求签名和编码；
- 把 `Payment-Proof` 当作不可信输入；
- 交付前调用官方验凭证 API；
- 校验状态、金额、订单、资源和交易号；
- 防止 Proof 被用于其他资源或重复履约；
- 资源交付后执行履约确认；
- 日志中没有密钥、完整 Proof 或可重放请求。

### 6.3 端到端验证

位置：`code/examples/alipay/end-to-end-402/`

沙箱产品接入直接引用 AIPay 官网；本项目仅维护 `code/examples/alipay/end-to-end-402/sandbox-validation.md` 中的 ACT/Profile 验收补充。

通过链路：

```text
Resource Request
  → 402 + Payment-Needed
  → 用户授权
  → 官方支付
  → Payment-Proof
  → 官方验凭证
  → Resource Delivery
  → Fulfillment Confirmation
```

本地测试只验证解析和控制流。端到端通过必须使用官方 Skill/CLI、Sandbox/OpenAPI，并填写脱敏证据模板。

## 7. 大会 Demo 计划

位置：`code/web-client/alipay-ai-pay-showcase/`

Demo 不实现支付，只编排三个 Quickstart 并展示以下状态：

```text
RESOURCE_REQUESTED
→ PAYMENT_REQUIRED
→ USER_AUTHORIZATION_REQUIRED
→ PAYMENT_PROCESSING
→ PAYMENT_VERIFIED
→ RESOURCE_DELIVERED
→ FULFILLMENT_CONFIRMED
```

运行模式：

- `LIVE_SANDBOX`：使用支付宝官方沙箱执行真实链路，是大会主模式；
- `SANITIZED_REPLAY`：使用已验证且脱敏的事件记录，是网络或沙箱异常时的备用模式，界面必须明显标注 Replay。

Demo 禁止复制官方支付实现、手工构造成功 Proof、静态返回支付成功或将 Replay 冒充现场支付。旧 Python 2.0 Mock Demo 已退出公开主线，历史代码仅保留在 Git；大会主 Demo 只保留 Guided Preview 与官方沙箱证据回放。

## 8. 倒排里程碑

| 时间 | 里程碑 | 协议侧 | Quickstart / Demo / Profile 验收 |
|---|---|---|---|
| 07-22—07-31 | July Preview | A402 解耦结构、最小字段/状态/错误征求意见稿；INS/DEL/AUP 关系明确 | 三个 Quickstart 本地测试通过；Profile 骨架完成；Demo 状态模型和 Replay 空壳完成 |
| 08-03—08-12 | Joint Review + Sandbox 1 | 联合共建单位意见征求 | 第一次真实支付、验凭证、资源交付和履约确认；第一轮陌生开发者试用 |
| 08-13—08-21 | Integration Verified | 处理意见并形成协议修改稿 | 正向和关键异常通过；证据包完成；Demo Live/Replay 连续演练通过 |
| 08-24—09-04 | Release Candidate | 内外部确认、形成定稿并同步官网 | Profile/Quickstart 冻结；兼容矩阵、迁移指南、发布说明和 clean-room 测试完成 |
| 09-05—09-08 | Buffer | 只处理阻断、安全和严重文档问题 | 不增加字段、产品范围、Binding 或 Demo 场景 |
| 09-09—09-12 | Conference Release | 发布 ACT v2.1 或明确标注 RC | 发布 Profile、Quickstart、Demo 和脱敏证据摘要 |

## 9. 固定工作节奏

- 每日：异步更新修订状态，协议与官网差异当天登记；
- 每周二：协议—Profile 对齐，只处理字段、状态、错误和责任边界；
- 每周四：Quickstart 与官方沙箱联调；
- 每周五：形成可运行 Snapshot、测试报告、风险和降级清单；
- 里程碑前一日：冻结输入，只做验收。

每周至少产出一个可运行版本、一份差异清单、一份测试结果和一段可演示链路。

## 10. 发布门槛与降级

发布采用分级门槛，不再用沙箱阻塞全部开源内容：

| 发布目标 | 必须满足 | 不要求 |
|---|---|---|
| ACT Candidate Publication | 协议内容、机器契约、本地检查及公开发布治理通过 | 支付宝账号、密钥或真实沙箱证据 |
| Alipay Profile Preview | Candidate 对齐、公开产品来源、Profile/Binding/Quickstart 检查及公开发布治理通过 | 真实互操作或生产可用声明 |
| Alipay Sandbox Verified | Profile Preview 条件，加官方沙箱正向、异常、重试、防重放和履约证据 | 不适用 |
| ACT SEP Candidate | Candidate 条件，加正式治理表决和独立实现验证 | 支付宝产品验证（协议治理本身不依赖单一产品） |

所有公开目标共同要求：

- 仓库完整检查和 Quickstart 测试全部通过；
- Profile 与协议不存在未说明冲突；
- 官网链接、许可证、治理和安全披露渠道完成发布复核；
- 陌生开发者不依赖语雀或内部资料即可完成公开接入。

只有 `Alipay Sandbox Verified` 和以真实支付为主张的 Demo 还要求：

- 至少一条 L1 + A402 官方沙箱闭环；
- 无效、过期、金额不符、资源不符和重复履约已验证；
- Demo 不依赖个人机器的隐式配置，并有明确 Replay 备用模式。

如果 ACT v2.1 未在 09-04 前完成治理确认，协议保持 `Candidate Working Draft / Non-normative`，不能称为正式 SEP Candidate。Profile、Quickstart 和 Demo 可以按 Preview 发布，但不得使用 Stable、Sandbox Verified 或正式 Conformance 表述；Demo 只有获得真实沙箱证据后才可升级相应主张。

## 11. 责任分工

- 观岳：ACT v2.1 支付服务域、A402、INS/DEL/AUP、状态机、错误和版本迁移；
- 念箴：开源结构、Alipay Profile、官网映射、Quickstart、Demo、沙箱证据和发布；
- 待指定：支付宝产品/API 复核人、安全披露渠道负责人、许可证/治理确认人和 clean-room 试用开发者。

协议结论与开源实现通过显式交接：观岳提供可评审候选和变更说明，念箴据此更新 Profile、Quickstart、Demo 和证据；未确定的问题保持开放，不由代码默认决定。
