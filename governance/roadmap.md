# 开源重构阶段计划

> 状态：Active delivery roadmap / Non-normative；最后收敛：2026-08-10

## 1. 总体策略

协议修订和开源工程重构并行推进，当前采用 PSD-first：

- [ACT Protocol 官网](https://www.act-protocol.com/)是公开协议事实源；2026-08-03 完成版维护稿和 v2.1 修订方案仅作为 Candidate 演进证据。
- 公开 2.0 目录不恢复；有效 PSD 语义在 2.1 Candidate 中显式维护。
- 近期协议工作聚焦 PMT-BND、AGT-SUB、INS/L1、DEL/L2、AUP/L3 和独立 A402。
- ADD、CID、TSD 已同步完整语义 Candidate，但不强制首期 L1 + A402 一键接入实现全部域；未冻结的机器契约继续单独治理。
- 开源重构先解决入口、边界、产品事实和追踪机制。
- Quickstart 和一致性测试用于验证协议候选结论。
- 未经治理的 Candidate 不得伪装成正式规范。
- 支付宝官网已经提供的开户、沙箱、产品接入和 API 文档不在 ACT 仓库重复维护；ACT 提供稳定导航、协议解释、字段映射和验证证据。

## 1.1 2026 外滩大会倒排

当前公开里程碑以[机器可读发布门禁](release-readiness.json)和[Candidate 发布说明](releases/2026-08-03-candidate-publication.md)为准。以下日期是历史项目计划，不构成协议或公开发布承诺：

| 日期 | 里程碑 | 必须完成的结果 |
|---|---|---|
| 2026-07-31 | July Preview | 开源入口、两条开发者路径、Profile 骨架、官网映射初版 |
| 2026-08-07 | Core Candidate | 最小 Core 候选语义可供 Profile 映射 |
| 2026-08-14 | Profile Preview | Alipay AI Pay Profile 主要映射和 Binding 完成 |
| 2026-08-21 | Integration Verified | 官方沙箱完成端到端验证，形成可公开证据 |
| 2026-08-28 | Release Candidate | 文档、映射、验证和发布材料冻结 |
| 2026-09-04 | Conference Release | 大会版本正式发布 |
| 2026-09-05—08 | Buffer | 只修复阻断、安全和严重文档问题 |

责任分工：

- ACT 协议修订和 Core 候选：观岳牵头。
- 支付宝 Profile、开源信息架构、官网映射、验证和发布：念箴牵头。

## 1.2 当前落地状态（2026-08-08）

| 工作项 | 状态 | 证据/入口 |
|---|---|---|
| 当前项目框架成为唯一结构事实来源 | Done | [ACT 项目框架](../docs/architecture/README.md) |
| 支付宝 AI 付产品级 Quickstart 入口 | Done | [支付宝 AI 付 Quickstart](../code/examples/alipay/README.md) |
| Agent 支付、AI 按量付费、端到端 402 中文主路径 | Done | [Quickstart 导航](../code/examples/README.md) |
| 旧版示例与真实产品接入隔离 | Done（旧版示例已退出公开包） | Git 历史 |
| 开发者与 CI 共用统一验证命令 | Done | `./scripts/verify.sh` |
| 旧版规范、示例和 Python Mock Demo 退出公开主线 | Done | 历史材料保留在 Git 历史 |
| Alipay Profile 目录拆分 | Done | `capabilities/`、`mappings/`、`sources/` |
| Buyer/Seller Demo Adapter 与证据导出工具 | Done | `code/web-client/alipay-ai-pay-showcase/` |
| 完成版 PSD 协议源、六组件和 A402 语义 | Done as Candidate | `specs/2.1/`、`scripts/check_repository.py` |
| A402 三类载荷 Schema、错误词典、fixtures 与 validator | Done as Candidate | `specs/2.1/a402/schemas/`、`scripts/validate_a402_contract.py` |
| Alipay Profile Preview 与产品字段机器契约 | Done for Preview；产品复核项保留 | `integrations/profiles/alipay-ai-pay/` |
| 卖方凭证配置后单命令启动 | Done | `code/examples/alipay/metered-rest-provider/run.sh` |
| 官方沙箱端到端证据 | Optional validation claim pending | 只阻塞 `alipay-sandbox-verified` |
| ACT Candidate / Profile Preview / Sandbox Verified 分级门禁 | Done | `governance/release-readiness.json` |

## 2. 工作阶段

### Phase 0：建立重构工作区

目标：让重构范围、决策和未决问题可追踪。

交付物：

- 重构目标与原则。
- 目标信息架构。
- 支付宝 AI 付公开接入基线。
- 阶段计划和修订追踪表。
- 根 README 的重构入口。

验收条件：

- 文档明确标注非规范性状态。
- 不修改协议正文和 Schema。
- 所有产品事实均有公开来源。
- 所有未决协议项进入追踪表。

### Phase 1：恢复开源可信度

目标：消除仓库中会误导开发者的结构和状态信息。

计划工作：

- 审计并修复断链、缺失文件和错误目录说明。
- 统一 README 与规范正文中的组件导航，但涉及重命名的内容等待修订决定。
- 标注 Demo、Quickstart 和 Reference Implementation 的真实属性。
- 修复无法运行的示例和基础语法错误。
- 补齐许可证文件及贡献文档中的实际流程。
- 建立最小 CI：Markdown 链接、JSON/Schema、代码语法和测试。

验收条件：

- README 中列出的文件和命令真实存在且可执行。
- Demo 不再被描述为真实支付宝接入。
- 主分支基础检查可重复执行。
- 不再使用无证据支撑的“稳定”“完整”“生产可用”描述。

### Phase 2：建立开发者入口

目标：开发者能够按角色找到唯一接入路径。

计划工作：

- `Choose your integration` 决策页。
- Agent 支付 Getting Started。
- AI 按量付费 Getting Started。
- Agent 支付与按量付费端到端关系说明。
- 产品开户、协议接入、Transport、业务履约的职责边界。
- 为官网已有开户、沙箱和接入说明提供准确链接，不在仓库复制完整步骤。

验收条件：

- 新开发者无需先阅读全部四域规范即可选择接入路径。
- 每条路径明确前置条件、步骤、成功结果和下一步。
- 所有支付宝接入引用均公开可访问。

### Phase 3：形成完整 PSD Core 候选

前置条件：协议修订在对应主题上形成可评审结论。

计划工作：

- 维护 PMT-BND、AGT-SUB、INS/L1、DEL/L2、AUP/L3 六组件结构。
- 将 HTTP 402 接入层完整抽取到 A402。
- 维护支付工具、请求、结果、Proof、状态和错误的 Candidate 语义。
- 关闭字段分布、`method_id`、精确重试/幂等和错误对象等剩余 wire-level 决策；Header 编码已由完成版协议明确。
- 为首期 `PMT-BND + INS + A402` 建立可执行覆盖。

验收条件：

- 每个候选对象有明确责任、状态和安全约束。
- Core 不依赖支付宝产品字段。
- 未决问题不进入规范性 Schema。
- 完成版支付域协议源有可追踪元数据、正文哈希和自动回归检查；修订分析作为历史背景保留。

### Phase 4：建立 Alipay AI Pay Profile

目标：把 ACT 候选语义映射为真实支付宝接入。

计划工作：

- Agent Payment Profile。
- Metered Payment Profile。
- HTTP 402 Binding。
- 官方 Skill/CLI Binding。
- 字段、状态和错误码映射。
- 商户签名、凭证验证、防重放和履约要求。
- 沙箱和生产环境配置清单。

验收条件：

- Profile 中每项产品要求可追溯至公开官方资料。
- 产品方完成关键字段和生命周期复核。
- 不依赖内部文档即可完成接入。

### Phase 5：实现可运行 Quickstart

目标：使用官网已提供的接入方案和官方沙箱验证 ACT/Profile 闭环，避免重复实现支付宝产品能力。

当前进度（2026-08-03）：三个入口及本地自动化测试已经落成；卖方 Java SDK 项目已完成编译、测试和可执行 JAR 打包。真实 Sandbox 支付、验款和履约证据是独立的产品兼容声明门禁，不是发布 ACT Candidate 或 Alipay Profile Preview 的前置条件。

计划交付三个最小验证入口：

1. Agent 钱包与 Payment Skill Quickstart。
2. AI 按量付费 REST Provider Quickstart。
3. Agent 调用收费 API 的端到端 402 Quickstart。

验收条件：

- 使用官方公开 Skill、SDK/API 或沙箱。
- 开户、沙箱和 API 操作优先链接支付宝官网，不复制可能发生漂移的产品文档。
- 不伪造支付成功、支付凭证或验证响应。
- 提供一键检查或清晰的自动化测试命令。
- 安全日志不输出私钥、访问令牌和完整支付凭证。

### Phase 6：一致性测试与候选发布

目标：分别验证 ACT Candidate、Product Profile Preview 和特定产品 Sandbox 兼容声明，禁止把三者合并为“接入 ACT 即自动接入产品”。

计划工作：

- Core Schema 和语义测试。
- Alipay Profile 测试夹具。
- 正向、异常、超时、重试和重放测试。
- 兼容性矩阵和版本元数据。
- 发布说明及迁移指南。

验收条件：

- 实现通过 Core 与 Alipay Profile 的对应测试套件。
- Quickstart 在干净环境中可重复运行。
- 候选规范、Profile 和实现版本依赖明确。
- 协议治理流程批准发布。

## 3. 建议里程碑

| 里程碑 | 主要结果 | 依赖 |
|---|---|---|
| M0 Framework | 重构工作区和追踪机制 | 无 |
| M1 Trustworthy Repository | 文档、链接、状态和基础检查可信 | M0 |
| M2 Developer Journey | 一条机器支付闭环及买卖双方接入路径清晰 | M1 |
| M3 Core Candidate | 修订结论进入候选规范 | 协议修订 |
| M4 Alipay Profile Candidate | 产品映射完成并复核 | M3、产品复核 |
| M5 Runnable Integration | 三个 Quickstart 已实现；真实 Sandbox 作为可选兼容声明待验证 | M4 |
| M6 Candidate Publication | Candidate/Profile 内容与公开发布治理门禁完成 | M4、公开远端、发布快照；AntSRC 安全渠道已通过 |
| M7 Sandbox Verified | 官方 Sandbox 闭环和脱敏证据完成 | M5、官方沙箱能力 |
| M8 SEP Candidate | 独立实现、公开评审和正式治理完成 | M6、治理批准 |

## 4. 任务追踪字段

后续 Issue 或工作项建议统一记录：

```yaml
id: ACT-OSR-000
title: concise task title
phase: 0-6
area: docs | core | profile | binding | quickstart | conformance
status: proposed | accepted | in-progress | blocked | done
normative_impact: none | candidate | normative
product_dependency: none | alipay-review | alipay-sandbox
protocol_dependency: related revision topic or none
owner: unassigned
evidence: public URL, test, or PR
```

## 5. 完成定义

单项工作只有同时满足以下条件才标记为完成：

- 产物已进入仓库并可从文档入口找到。
- 所有链接和命令通过自动检查。
- 状态标签与实际成熟度一致。
- 产品事实有公开来源或验证证据。
- 未决问题没有被实现代码悄悄决定。
- 涉及协议语义时，已关联对应修订决定。
