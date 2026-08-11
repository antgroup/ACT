# ACT 2.1 A402 最小机器契约决策包

> 状态：Candidate decisions complete / Non-normative  
> 更新日期：2026-08-03  
> 决策主体：ACT Core spec owner 与相关 DWG；涉及产品事实时由 Product Profile maintainer 提供输入  
> 机器索引：[A402 Decision Register](a402-decision-register.json)  
> 结果格式：[ADR 模板](adr-template.md)

## 1. 目标与使用规则

本决策包保留 A402 Candidate Working Draft 中机器契约、Schema、SDK 和 TCK 的九个决策槽位。2026-08-03 已按[Candidate 机器契约决议](candidate-machine-contract-resolution-2026-08-03.md)选择工程选项并生成可执行资产；这些选择继续供正式 DWG 评审，不把支付宝产品行为写成 ACT Core，也不冒充正式 Accepted ADR。

评审人应对每项作出以下一种处理：

- **Accept Option A/B/C**：选择现有选项，并建立 Accepted ADR；
- **Revise**：现有选项不足，先补充或修改选项，不得在会议结论中口头创造第四种方案；
- **Defer**：给出所缺输入、责任角色和重新评审条件；
- **Reject scope**：明确该问题不属于 A402，并指定权威归属。

只有满足以下条件，决定才算生效：

1. 有公开 Issue、PR 或会议记录；
2. 决策主体和日期明确；
3. 建立 ADR，并写明兼容、安全、迁移和测试后果；
4. 更新 [`a402-decision-register.json`](a402-decision-register.json) 的 `status` 与 `decision_record`；
5. Core、Binding、Profile 和测试只实现 ADR 接受的范围。

## 2. 已对齐基线，不重复表决

`BASE-A402-001`：`PSD-PAY-A402` 是与 INS/L1、DEL/L2、AUP/L3 授权场景解耦的候选支付接入协议。场景决定“凭什么支付”，A402 决定“如何交换支付要求、Proof、验证与履约结果”。

此外，完成版支付服务域已经给出以下不能再被视为“完全未知”的 Candidate 语义：

- 14 个共享基础载荷字段及其语义，但尚未冻结 Header 分布、必填性和 wire schema；
- `CREATE`、`WAIT_BUYER_PAY`、`WAIT_SELLER_FULFILLMENT`、`WAIT_BUYER_RECEIPT`、`TRADE_FINISHED`、`TRADE_CLOSED` 六状态及允许转移；
- 签名、参数、协议/方法、身份、资产、风控、交易状态、退款、履约、Proof 验证和系统错误类别及恢复方向。
- 三类 Header 均采用 Base64URL 编码的 UTF-8 JSON，并使用 `protocol` + `method` 两层结构；`Payment-Validation` 是验凭后的可选响应 Header。
- 支付请求不要求传完整购物车：传统流程关联商户侧订单号，A402 可在 `Payment-Needed` 中返回订单或资源标识。

正式版本和治理接受仍待完成；机器契约、状态触发、错误对象和迁移下限已经形成 Candidate 选择并可由正式评审修订。不得重新表决已继承语义，也不得把 Candidate 表述为 2.1 已发布。

## 3. 推荐决策顺序

```text
DP-A402-001 Canonical source
  ├── DP-A402-002 HTTP envelope / encoding (source-settled)
  ├── DP-A402-003 method_id / discovery
  └── DP-A402-007 confirmed commerce facts
        ↓
DP-A402-004 retry / idempotency / replay
DP-A402-005 validation / fulfillment
DP-A402-006 lifecycle / errors / recovery
        ↓
DP-A402-008 L1/L2/L3 publication scope
DP-A402-009 workflow Binding coverage
        ↓
Candidate Schema + fixtures + validator + migration + TCK
```

`DP-A402-001` 应先决定，因为其余决策的产物最终需要落入同一权威机器源。`DP-A402-008/009` 可以讨论，但应在核心对象边界稳定后接受。

## 4. 决策总览

| ID | 决策 | 推荐项（非结论） | 对应 Pending Decision | 状态 |
|---|---|---|---|---|
| DP-A402-001 | Canonical machine-contract source | B：JSON Schema 为 HTTP-first Candidate 权威源 | 新增工程决策门槛 | Candidate accepted |
| DP-A402-002 | Header envelope 与编码 | 完成版协议：Base64URL UTF-8 JSON + `protocol` / `method` | 已关闭 PD-2.1-002 | Source-settled |
| DP-A402-003 | `method_id`、版本与发现 | A：稳定命名空间 ID + 独立版本 | PD-2.1-003 | Candidate accepted |
| DP-A402-004 | 原请求关联、幂等与防重放 | B：规范化请求指纹 + 非幂等控制 | PD-2.1-005/006 | Candidate accepted |
| DP-A402-005 | 履约确认与证据边界 | B：验凭、交付、履约确认和 TSD 证据保持独立 | PD-2.1-009 | Candidate accepted；Validation Header 已由来源明确 |
| DP-A402-006 | 状态、错误与恢复动作 | C：保留六状态公共投影 + 结构化阶段结果与恢复 | PD-2.1-004 | Candidate accepted |
| DP-A402-007 | CID 已确认事实与跨域关联 | C：最小订单/资源关联 + 可选 CID 引用 | PD-2.1-007 | Candidate accepted；完整购物车问题已关闭 |
| DP-A402-008 | L1/L2/L3 发布范围 | B：L1 原型基线，L2/L3 等待公开安全依赖 | PD-2.1-010 | Candidate accepted |
| DP-A402-009 | 工作流 Binding 封装与证据 | B：允许多步封装，但必须发布覆盖声明 | REV-017 / OQ-015 | Candidate accepted |

`PD-2.1-011` 的 PMT-BND/支付宝钱包映射属于 PSD Foundation + Alipay Profile；`PD-2.1-012` 的 AUP 场景错误属于 AUP 规范。二者不由最小 A402 wire-contract 决策包直接关闭，继续在[修订状态](../../specs/2.1/revision-status.md)追踪。

## 5. DP-A402-001：Canonical machine-contract source

### 决策问题

ACT 2.1 A402 的字段、类型和兼容变化应以什么为唯一权威机器源？

| Option | 定义 | 兼容与工具影响 | 主要风险 |
|---|---|---|---|
| A | Protobuf 权威；JSON Schema、文档和语言类型全部生成 | 强 codegen、多语言类型清晰 | HTTP Header 的开放 JSON 扩展和 `oneOf` 演进成本较高 |
| B | JSON Schema 权威；语言类型、示例校验器和文档由 Schema 生成 | 直接适配 HTTP/JSON，现有资产迁移最短 | 需要严格控制手写 Schema 漂移和代码生成规则 |
| C | 规范文字权威；机器文件仅 illustrative | 文档自由度最高 | Agent、SDK 和 TCK 缺少确定输入，不解决本次根因 |

### 非约束性推荐

推荐 **B**，作为 HTTP-first Candidate 的最小路径；同时要求：

- 每个权威 Schema 有 `$id`、协议版本和状态；
- examples、生成类型与 validator 不得手工复制字段；
- Breaking Change 通过版本目录或新的 `$id` 发布；
- 如果后续需要 Protobuf，必须由新 ADR 决定迁移，不得形成双权威源。

### 接受前必须回答

- JSON Schema Draft 版本和 Format 校验是否强制？
- 扩展字段默认 `additionalProperties` 策略是什么？
- Schema 与规范文字冲突时哪一方阻止发布？
- 生成产物是否提交仓库，如何验证无漂移？

### 接受后的产物

`specs/2.1/schemas/` 或治理选定目录、生成/校验脚本、example-to-schema 映射、版本与兼容规则、ADR。

## 6. DP-A402-002：Header envelope 与编码

### 决策问题

该问题已被 2026-08-03 完成版《支付服务域》取代，不再从下列历史选项中表决。

| Option | 定义 | 互操作性 | 产品兼容风险 |
|---|---|---|---|
| A | 三个 Header 统一 Base64URL UTF-8 JSON，共享 Core envelope | ACT-native HTTP 最统一 | 可能与既有产品的 Base64/字段结构冲突 |
| B | Core 定义逻辑对象；每个版本化 Binding 定义 Header 名、编码和 envelope | 可支持 HTTP、Skill/CLI 和未来 Binding | 必须防止不同 Binding 暗中产生不等价语义 |
| C | 每个 Product Profile 自行定义 | 产品接入最自由 | ACT 无跨产品 HTTP 互操作契约 |

### 来源结论

三个 Header 统一采用 Base64URL 编码的 UTF-8 JSON，并共享 `protocol` + `method` 两层结构；`Payment-Validation` 是成功验凭后的可选响应 Header。记录见[2026-08-03 source resolution](source-resolution-2026-08-03.md)。

### Alipay Profile 落地所需产品输入（不阻塞 Core/Binding 分层决策）

- `Payment-Proof` 当前权威编码是否是标准 Base64、Base64URL，还是官方实现兼容两者；
- 官方 Skill/CLI 是否向宿主暴露完整 Proof；
- 产品是否存在可映射为 `Payment-Validation` 的买方可见结果；
- Header 最大尺寸和未知字段处理。

### 同步产物

三类逻辑对象 Schema、HTTP Binding 编码规则、Alipay Profile 映射、正反例 fixtures、跨 Binding 等价性测试。

## 7. DP-A402-003：`method_id`、版本与发现

### 决策问题

支付方法如何获得稳定身份、版本协商、Schema 解析和未知方法处理？

| Option | 定义 | 优点 | 风险 |
|---|---|---|---|
| A | `method_id` 是带命名空间的稳定 ID；版本是独立字段 | 标识稳定、版本选择清晰 | 需定义命名空间治理和版本兼容 |
| B | 版本嵌入 `method_id` | 单字段即可定位契约 | 兼容范围和别名管理复杂 |
| C | `method_id` 仅在 Product Profile 内有效 | 产品实现简单 | 无法跨 Profile 协商或缓存 Schema |

### 非约束性推荐

推荐 **A**。本决策只确定模型，不在本包中抢先规定字符串语法。语法、版本范围、未知/弃用错误以及 `method_schema_url` 的 HTTPS、缓存、完整性和失效规则应作为同一 ADR 的必填内容。

### 接受前必须回答

- 谁分配命名空间；
- method version 使用 SemVer、整数还是日期；
- 买方是否必须在 Proof 中回显方法和版本；
- Schema 获取失败时是重新协商、终止还是回退；
- discovery 采用 `.well-known`、CID 对象还是其他机制。

### 接受后的产物

`CID-PCA-NEG` Candidate Schema、method registry/namespace 规则、发现安全规则、未知方法 fixtures。

## 8. DP-A402-004：原请求关联、幂等与防重放

### 决策问题

携 Proof 重试时，如何证明它仍对应原资源请求，并避免重复支付或重复非幂等交付？

| Option | 定义 | 安全性 | 实现代价 |
|---|---|---|---|
| A | Method、URL、选定 Header 和 Body 必须字节级一致 | 判定直接 | 动态 Header、流式 Body 和代理重写难以兼容 |
| B | 对规范化请求生成稳定指纹；非幂等交付另有幂等控制 | 能排除无关资源并适应正常传输变化 | 必须定义 canonicalization、敏感字段和存储期限 |
| C | 只要求同一业务资源；细节留给 Profile | 产品自由 | 跨产品重放和重复交付行为不一致 |

### 非约束性推荐

推荐 **B**。ADR 必须明确“请求关联”和“支付/履约幂等”是两个控制面，不能只引入一个布尔 `retryable`。具体字段名由 canonical Schema 决定，本包不预建字段。

### 接受前必须回答

- 哪些 Method 允许自动重试；
- URL query、Body、Content-Type 和业务 Header 如何规范化；
- Authorization、Cookie、逐跳 Header 是否禁止保存；
- 指纹、账单、Proof、交易号和交付记录的保存期限；
- 并发重试由谁原子去重；
- 原请求事实变化时是否必须生成新 Payment Requirement。

### 接受后的产物

请求关联 Schema、HTTP 重试规范、安全存储要求、并发/重放 fixtures、非幂等 TCK。

## 9. DP-A402-005：验证结果与履约边界

### 决策问题

`Payment-Validation` 的可选 Header 形态已经由完成版协议明确。本项只继续决定支付验证、资源交付、方法特定履约确认和 TSD 证据如何区分与关联。

| Option | 定义 | 优点 | 风险 |
|---|---|---|---|
| A | `Payment-Validation` 成功同时证明业务履约并关闭证据生命周期 | 单一成功态简单 | 混淆验凭、交付与履约事实 |
| B | 验凭、资源交付、方法特定履约确认和 TSD 证据是相互关联但独立的事实 | 阶段和责任清晰 | 需要定义关联标识和最低证据 |
| C | A402 交付后的一切履约与证据完全留给 Product Profile | Core 最小 | 跨产品审计和争议语义缺失 |

### 非约束性推荐

推荐 **B**。验证通过是交付前置条件，但“支付已验证”“资源已交付”“产品履约已确认”“买方已收到”必须是不同事实，不能由单一 `success` 合并。

### Alipay Profile 落地所需产品输入（不阻塞 Core/Binding 分层决策）

- Alipay 服务端验凭结果中可公开映射的最小字段；
- `alipay.aipay.agent.fulfillment.confirm` 与买方 fulfillment ack 的关系；
- 重复确认的幂等行为和权威状态；
- 哪些信息只能留在服务端证据中。

### 接受后的产物

逻辑 Validation Schema、HTTP/Skill Binding 映射、PSD/TSD 事件边界、产品履约 fixtures、证据脱敏规则。

## 10. DP-A402-006：状态、错误与恢复动作

### 决策问题

A402 应定义一个完整交易状态机、多个阶段状态机，还是最小公共状态加 Product Profile 映射？

| Option | 定义 | 优点 | 风险 |
|---|---|---|---|
| A | 采用现有 `CREATE → ... → TRADE_FINISHED/CLOSED` 六状态 | 与修订源候选一致、理解直接 | 混合支付、交付、确认与收货阶段 |
| B | 支付、验证、交付、履约分别建状态机 | 语义最精确 | 组合复杂，首版实现和测试成本高 |
| C | Core 保留六状态作为公共兼容投影，并增加结构化阶段结果与恢复动作；Profile 映射详细状态 | 保留基线兼容性，同时区分支付/验证/交付/履约结果 | 必须严格定义投影规则、unknown/terminal 和阶段一致性 |

### 非约束性推荐

推荐 **C**。六状态及基线允许转移继续作为 Candidate 公共兼容投影，不重新表决是否存在；本决策只确定如何表达精确触发、超时、补偿、分阶段结果和 Profile 映射。结构化错误至少需要类别、发生阶段、是否终止、允许动作、动作执行者和适用期限；`retry_after`、最大次数与授权要求是否进入 Core 由本 ADR 一并决定。

### 接受前必须回答

- 未知支付结果与验证 API 暂不可用是否使用不同状态；
- `valid_next_actions` 属于错误对象还是通用结果；
- 谁允许执行 query/retry/new-requirement/abort；
- Profile 详细状态无法映射时如何保留原始状态；
- 状态迁移与幂等记录如何关联。

### 接受后的产物

状态与错误 Schema、机器错误词典、状态映射模板、正反状态转换 fixtures、恢复动作 TCK。

## 11. DP-A402-007：CID 已确认事实与跨域关联

### 决策问题

`Payment-Needed` 已可承载商户订单号和资源标识，但是否必须另外引用独立 CID 交易确认对象？关键交易事实变化时如何保持同一事实来源？

| Option | 定义 | 优点 | 风险 |
|---|---|---|---|
| A | `Payment-Needed` 的订单/资源最小事实足够，不引用独立 CID 对象 | 处理最简单 | 复杂交易可能缺少确认链 |
| B | `Payment-Needed` 除最小事实外必须引用独立确认对象 | 边界清晰 | 增加获取、缓存、完整性与失效问题 |
| C | 保留协议已明确的订单/资源最小事实；未来 CID 规则可按场景增加内嵌或引用 | 兼顾紧凑与复杂交易 | 必须定义可选引用的完整性 |

### 非约束性推荐

推荐 **C**。完成版协议已经排除“完整购物车必须复制进支付报文”的解释；本项不再重新表决该结论，只决定复杂商业确认是否需要额外引用。

### 接受前必须回答

- 最小 confirmed facts；
- 引用对象的身份、摘要/签名、有效期和获取权限；
- 部分金额、优惠、税费、运费变化如何处理；
- `intent_id`、`delegation_id`、订单、资源、交易和履约证据的最小关联责任。

### 接受后的产物

CID→PSD Candidate 映射、confirmed-facts Schema、变更失效规则、跨域证据 fixtures。

## 12. DP-A402-008：L1/L2/L3 发布与 Conformance 范围

### 决策问题

DEL/L2 和 AUP/L3 的 ASL/身份/授权/密钥依赖尚未形成同等清晰的公开规范时，A402 2.1 应声明什么范围？

| Option | 定义 | 优点 | 风险 |
|---|---|---|---|
| A | L1/L2/L3 同时发布、同等 Conformance | 版本叙事完整 | 对未公开安全依赖产生虚假完备声明 |
| B | L1 是可原型化基线；L2/L3 保留候选组合但 Validation pending | 诚实匹配现有产品和证据 | 需要清晰的分级声明 |
| C | 等待 L1/L2/L3 全部完整后再发布任何 Candidate | 一致性最高 | 阻塞已可验证的 L1 反馈 |

### 非约束性推荐

推荐 **B**。这不会把 L1 自动升级为 SEP Candidate；它只是定义首个可执行原型范围。DEL/AUP 在公开 ASL 依赖、授权约束和独立验证证据完成前不得声明 Conformance。

### 接受后的产物

Overview 发布范围、Profile 分级声明、测试矩阵、DEL/AUP Pending 依赖清单。

## 13. DP-A402-009：工作流 Binding 封装与证据

### 决策问题

Skill/CLI 等工作流是否可以在一次命令中封装支付、状态查询、Proof 提交和原请求恢复，而宿主看不到每个 Core 对象？

| Option | 定义 | 优点 | 风险 |
|---|---|---|---|
| A | 一条 Binding 操作只能映射一个 Core 消息 | 可观察性强 | 不适配真实工作流型产品 |
| B | 允许封装多步，但必须发布覆盖、输入、可观察输出、错误和证据规则 | 兼容产品工作流并保持可审计 | 需要 Binding manifest 和分层测试 |
| C | 完全由 Product Profile 自行解释，无 ACT 覆盖声明 | 接入最自由 | 无法判断它实现了哪些 ACT 语义 |

### 非约束性推荐

推荐 **B**。Binding manifest 至少声明：

- 覆盖的 Core 组件、版本和 Candidate 状态；
- 宿主必须提供的意图、交易和原请求上下文；
- 被内部封装和对宿主可见的对象；
- 中间态、终态、恢复动作和取消语义；
- 可公开的脱敏证据与不可导出的敏感数据；
- 对 DP-A402-004/005/006 的实现责任。

### 接受后的产物

Binding manifest Schema、Alipay Skill/CLI manifest、host adapter contract、Binding 级测试。

## 14. Pending Decision 覆盖矩阵

| Revision status ID | 本包处理 | 备注 |
|---|---|---|
| PD-2.1-001 | Source-settled | 可选 `Payment-Validation` Header |
| PD-2.1-002 | DP-A402-002 / Source-settled | Base64URL UTF-8 JSON + 两层结构 |
| PD-2.1-003 | DP-A402-003 | `method_id` 与发现 |
| PD-2.1-004 | DP-A402-006 | 状态、错误、恢复 |
| PD-2.1-005 | DP-A402-004 | 原请求重试 |
| PD-2.1-006 | DP-A402-004 | Proof 防重与履约幂等 |
| PD-2.1-007 | DP-A402-007 | CID 确认关系 |
| PD-2.1-008 | Source-settled | 不要求支付请求传完整购物车 |
| PD-2.1-009 | DP-A402-005 | 支付、交付、履约与 TSD |
| PD-2.1-010 | DP-A402-008 | DEL/AUP 安全依赖 |
| PD-2.1-011 | Deferred outside A402 | PMT-BND 与支付宝钱包生命周期映射 |
| PD-2.1-012 | Partial: DP-A402-006 + AUP spec | A402 公共错误信封与 AUP 场景错误分层 |

## 15. 单项评审记录

复制以下区块到公开 Issue 或会议记录，并在接受后建立 ADR：

```text
Decision ID:
Selected action: Accept A / Accept B / Accept C / Revise / Defer / Reject scope
Decision owner role:
Reviewers:
Date:
Public discussion URL:

Reasoning:
Compatibility impact:
Security and privacy impact:
Migration impact:
Required product input:
Required specification changes:
Required Schema/code generation changes:
Required tests:
Re-review condition (if deferred):
```

## 16. 整包退出条件

九项不要求在同一次会议全部接受，但只有满足以下条件后，才能开始生成 A402 Core Candidate 机器契约：

- DP-A402-001 必须 Accepted；
- DP-A402-002 已由完成版协议取代；DP-A402-003—007 必须 Accepted，或有明确、不影响首个 Candidate 的 Defer 范围；
- DP-A402-008 明确首个发布/验证范围；
- DP-A402-009 明确工作流 Binding 是否在首个 Profile 范围；
- 每个 Accepted 项有 ADR 和公开批准记录；
- `a402-decision-register.json` 与 ADR、规范 Pending Decision 一致；
- 没有把 Alipay Product Profile Preview Schema 当作 Core canonical source。

满足门槛后，按同一批决定生成 Core Schema、fixtures、validator、字段级迁移表和 Candidate TCK；任一产物出现新语义时必须退回决策阶段。
