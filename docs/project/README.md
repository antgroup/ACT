# 项目路线与修订状态

> 状态：Active / Non-normative；最后更新：2026-08-03

本目录公开记录 ACT 协议修订期间的路线、决策、审计和阶段发布信息。这里不是 ACT 正式规范；正式语义和 Schema 只通过协议治理进入 `specs/`。

## 当前入口

| 文档 | 作用 | 状态 |
|---|---|---|
| [阶段路线图](roadmap.md) | 阶段、交付物、责任和分级验收条件 | Active |
| [修订状态](revision-status.md) | 决策、开放问题和变更记录 | Active |
| [目标信息架构](target-architecture.md) | 协议修订稳定后的长期目标目录 | Future-state Draft |
| [A402 最小机器契约决策包](decisions/protocol-decision-brief.md) | 完成版协议关闭项与 Candidate Core/Binding 选择 | Candidate decisions complete |
| [A402 机器决策 Register](decisions/a402-decision-register.json) | 来源结论、Candidate 选择、阻塞资产和正式 ADR 追踪 | Candidate complete |
| [A402 评审执行指南](decisions/a402-review-guide.md) | Issue、会议、Accept/Defer 和 ADR 的可执行流程 | Active |
| [架构原则](../architecture/principles.md) | 开源重构目标、边界和判断标准 | Active |
| [支付宝公开接入基线](../../profiles/alipay-ai-pay/sources/integration-baseline.md) | 官网事实如何进入 Profile | Active |
| [分级发布门禁](releases/release-readiness.json) | ACT Candidate、Profile Preview、Sandbox Verified 与 SEP Candidate 的独立门禁 | Active；public publication blocked |
| [ACT 2.1 Candidate 当前发布说明](releases/2026-08-03-candidate-publication.md) | 当前范围、允许主张和剩余阻塞 | Active |
| [ACT 2.1 PSD July Preview 候选发布说明](releases/2026-07-31-july-preview.md) | 2026-07-31 历史发布快照 | Historical |
| [外滩大会支付域执行计划](releases/2026-bund-payment-open-source-plan.md) | PSD、Quickstart、Demo、沙箱和发布倒排 | Active |

## 分类记录

- `decisions/`：协议修订方向、可表决决策包、机器 Register 和被接受后的 ADR。
- `audits/`：仓库结构、内容和发布可信度审计。
- `releases/`：特定发布节点的范围、冻结和验收说明。

## 使用约束

- 产品要求必须能追溯到公开官网或官方开源实现。
- 未决协议内容记录在[修订状态](revision-status.md)，不能由 Quickstart 代码替代协议决定。
- 项目计划中的负责人、日期和范围不构成 ACT 规范承诺。
- 已完成的历史记录保留用于追踪，但开发者接入应从[接入指南](../getting-started/README.md)开始。

文档状态定义：`Draft` 表示可讨论草案，`Active` 表示持续维护，`Accepted` 表示项目层面已评审，`Normative` 只能由正式协议发布流程授予。
