# ACT 修订与开源重构追踪

> 状态：Active / Non-normative  
> 最后更新：2026-07-15

本文件连接“协议修订”“支付宝产品接入”和“开源工程交付”。它不替代正式决策记录；当某项结论被接受后，应建立独立 ADR、Issue 或 PR，并从本表链接到证据。

## 1. 修订主题追踪

| ID | 修订主题 | 当前项目问题 | 预期产物 | 影响区域 | 状态 |
|---|---|---|---|---|---|
| REV-001 | 协议重新定位 | 协议、产品和 Demo 边界不清 | Core/Profile/Binding 定位 | README、架构 | Proposed |
| REV-002 | Core 与 Extension | 所有能力在同一层级呈现 | 最小 Core 与扩展规则 | Specs、Profiles | Proposed |
| REV-003 | Common Message | Skill、MCP、OpenAPI 可能重复定义消息 | 通用消息封装和验证规则 | Core、Bindings | Proposed |
| REV-004 | Agent Discovery/Profile | 缺少能力发现与兼容性声明 | Agent/Profile 描述模型 | ADD、CID、Profiles | Proposed |
| REV-005 | Payment Requirement | 账单、支付挑战和产品字段混杂 | 中立支付要求语义 | PSD、HTTP Binding | Proposed |
| REV-006 | Payment Proof | 凭证结构、验证者和校验责任不完整 | Proof 与 Verification 模型 | PSD、Profiles | Proposed |
| REV-007 | Lifecycle | 协议状态与产品状态混杂 | 通用生命周期和映射规则 | Core、Profiles | Proposed |
| REV-008 | Callback/Event | 异步支付和履约结果边界不清 | Callback/Event 模型 | Core、Bindings | Proposed |
| REV-009 | Error Recovery | 错误主要依靠文字说明 | 结构化错误和恢复动作 | Core、Profiles | Proposed |
| REV-010 | `valid_next_actions` | Agent 不知道失败后能做什么 | 可执行的下一步动作模型 | Common Message | Proposed |
| REV-011 | Field Mapping | ACT 对产品字段缺少显式映射 | Profile 映射规范 | Profiles | Proposed |
| REV-012 | Conformance | 示例不能证明协议兼容 | Core/Profile 测试套件 | Conformance | Proposed |
| REV-013 | Compatibility | 现有组件、Schema 和示例命名不一致 | 版本和迁移策略 | 全仓库 | Proposed |

## 2. 开源重构工作项

| ID | 工作项 | 阶段 | 依赖 | 状态 | 交付证据 |
|---|---|---|---|---|---|
| ACT-OSR-001 | 建立重构工作分支 | Phase 0 | 无 | Done | `codex/open-source-restructure` |
| ACT-OSR-002 | 建立目标、架构、产品基线和计划文档 | Phase 0 | 无 | Done | 本目录 |
| ACT-OSR-003 | 从根 README 提供重构入口 | Phase 0 | ACT-OSR-002 | Done | `README.md` |
| ACT-OSR-003A | 建立外滩大会发布章程 | Phase 0 | DEC-001—012 | Done | `06-bund-release-charter.md` |
| ACT-OSR-003B | 建立 Alipay AI Pay 对齐矩阵初稿 | Phase 0 | ACT-OSR-002 | Done | `profiles/alipay-ai-pay/` |
| ACT-OSR-004 | 审计断链和虚构目录 | Phase 1 | 无 | Done | `07-repository-audit.md` |
| ACT-OSR-005 | 校正规范和实现成熟度描述 | Phase 1 | 治理确认 | In progress | README 已处理，治理文件待复核 |
| ACT-OSR-006 | 标记并隔离模拟 Demo | Phase 1 | 无 | Done | `impl/python/README.md` |
| ACT-OSR-007 | 建立基础 CI | Phase 1 | ACT-OSR-004 | Done | `scripts/check_repository.py`、workflow |
| ACT-OSR-008 | 编写接入路径选择页 | Phase 2 | REV-001 | Done | `docs/getting-started/README.md` |
| ACT-OSR-009 | 编写 Agent 支付 Getting Started | Phase 2 | 支付宝公开资料复核 | Done | `docs/getting-started/agent-payment.md` |
| ACT-OSR-010 | 编写 AI 按量付费 Getting Started | Phase 2 | 支付宝公开资料复核 | Done | `docs/getting-started/metered-payment.md` |
| ACT-OSR-010A | 编写端到端 402 验证计划 | Phase 2 | ACT-OSR-009、010 | Done | `docs/getting-started/end-to-end-402.md` |
| ACT-OSR-011 | 建立 ACT Core 候选草案 | Phase 3 | REV-002—REV-010 | Blocked by revision | 待协议决定 |
| ACT-OSR-012 | 建立 Alipay AI Pay Profile | Phase 4 | ACT-OSR-011、产品复核 | Blocked | 待 Core 候选 |
| ACT-OSR-013 | 实现 Agent Payment Quickstart | Phase 5 | ACT-OSR-012 | Blocked | 待 Profile 候选 |
| ACT-OSR-014 | 实现 Metered REST Quickstart | Phase 5 | ACT-OSR-012 | Blocked | 待 Profile 候选 |
| ACT-OSR-015 | 实现端到端 402 Quickstart | Phase 5 | ACT-OSR-013、014 | Blocked | 待前置实现 |
| ACT-OSR-016 | 建立一致性测试 | Phase 6 | REV-012、Quickstarts | Blocked | 待候选规范 |

这里的 `Blocked` 表示存在明确前置依赖，不代表工作被取消。

## 3. 已接受的工作决策

| Decision | 内容 | 日期 | 影响 |
|---|---|---|---|
| DEC-001 | 首期覆盖 Agent 支付与 AI 按量付费 | 2026-07-15 | 控制产品和实现范围 |
| DEC-002 | 采用 ACT Core 与支付宝产品 Profile 分层 | 2026-07-15 | Core 保持产品中立 |
| DEC-003 | 开源接入资料必须完全公开 | 2026-07-15 | 不以内部文档作为外部开发者前置条件 |
| DEC-004 | 支付宝官网和公开官方实现是产品接入事实基线 | 2026-07-15 | Profile 要求必须可追溯 |
| DEC-005 | 协议修订期间先建立框架，不直接修改协议 | 2026-07-15 | 当前分支以文档和追踪为主 |
| DEC-006 | 大会版本采用 ACT Core 2.1 Draft/RC + Alipay AI Pay Profile 0.9 Preview | 2026-07-15 | 不提前宣布 Stable |
| DEC-007 | Agent 支付首期以官方 Skill/CLI 为公开接入基线 | 2026-07-15 | 其他接入形式后续迭代 |
| DEC-008 | AI 按量付费首期采用官网公开的 HTTP 402 流程 | 2026-07-15 | 不另行设计大会版支付 Transport |
| DEC-009 | 使用支付宝官网现有沙箱和接入方案 | 2026-07-15 | ACT 不重复实现产品能力和沙箱 |
| DEC-010 | 大会前中文全量，英文覆盖关键入口和摘要 | 2026-07-15 | 控制双语范围 |
| DEC-011 | 官网不能同步修改，ACT 仓库单向对齐官网 | 2026-07-15 | 建立官网漂移检查 |
| DEC-012 | 协议由观岳牵头，其余开源、Profile、验证与发布由念箴牵头 | 2026-07-15 | 明确决策和交付责任 |

## 4. 待决定问题

| ID | 问题 | 需要的输入 | 阻塞内容 | 状态 |
|---|---|---|---|---|
| OQ-001 | ACT Core 的最小对象集合是什么 | 协议修订结论 | Core 草案 | Open |
| OQ-002 | Product Profile 是协议扩展还是独立合规层 | 架构评审 | 目录、版本、测试 | Open |
| OQ-003 | Transport 与 Product Profile 如何组合声明版本 | Common Message 方案 | 兼容性矩阵 | Open |
| OQ-004 | Agent Discovery/Profile 的最小公开字段是什么 | Discovery 修订 | Agent 能力协商 | Open |
| OQ-005 | Proof 验证结果是否为独立消息 | Payment Proof 修订 | 状态机、Schema | Open |
| OQ-006 | 履约回执属于 Core 还是商业扩展 | 生命周期修订 | Metered Profile | Open |
| OQ-007 | `valid_next_actions` 是通用信封字段还是错误字段 | Error Recovery 修订 | Agent 自动恢复 | Open |
| OQ-008 | 首个 Quickstart 选择哪个支持官方 Skill/CLI 的 Agent 运行时 | 公开能力和维护成本评估 | Quickstart 验证入口 | Open |
| OQ-009 | 支付宝产品字段歧义如何获得公开确认 | 产品与开放平台复核 | Alipay Profile | Open |

支付宝产品侧的详细问题见[公开接入基线](03-alipay-integration-baseline.md#6-待支付宝产品复核的问题)。

## 5. 决策准入规则

一项协议或产品映射只有满足下列条件，才能从 Proposed/Open 变为 Accepted：

1. 有明确的问题陈述和备选方案。
2. 说明对 Core、Profile、Binding、实现和兼容性的影响。
3. 有公开可引用的产品事实，或明确标记为产品待确认。
4. 至少有一个端到端场景验证结论不会产生死路。
5. 错误、超时、重试、幂等和安全责任已被考虑。
6. 有可执行测试或明确的后续测试计划。
7. 由协议治理或对应产品负责人确认责任范围。

## 6. 变更日志

| 日期 | 变更 | 关联项 |
|---|---|---|
| 2026-07-15 | 建立重构分支与文档框架 | ACT-OSR-001—003 |
| 2026-07-15 | 记录首期范围、分层和公开资料原则 | DEC-001—005 |
| 2026-07-15 | 确认大会版本、接入基线、沙箱复用、双语范围和负责人 | DEC-006—012 |
| 2026-07-16 | 建立 Agent 支付、按量付费、字段、生命周期和错误映射初稿 | ACT-OSR-003B |
| 2026-07-18 | 完成首轮仓库可信度审计、Demo 标记和基础 CI | ACT-OSR-004—007 |
| 2026-07-18 | 完成接入选择、Agent 支付、按量付费和端到端 402 指南 | ACT-OSR-008—010A |
