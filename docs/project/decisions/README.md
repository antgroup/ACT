# ACT 项目决策记录

> 状态：Active / Non-normative

本目录保存进入正式规范前的决策输入、机器可读追踪和被治理接受后的 ADR。`Candidate Accepted` 允许开源 Working Draft 形成可执行 Schema 和测试，但不是正式协议结论；只有具备公开讨论和批准记录的 `Accepted` ADR 才能驱动 Stable Core 和正式 Conformance。

## 当前入口

| 资产 | 作用 | 状态 |
|---|---|---|
| [A402 决策包](protocol-decision-brief.md) | 逐项评审选项、影响和签署模板 | Candidate decisions complete |
| [A402 决策 Register](a402-decision-register.json) | Pending Decision、来源关闭项、选项和阻塞资产的机器可读索引 | Candidate complete |
| [2026-08-03 Candidate 机器契约决议](candidate-machine-contract-resolution-2026-08-03.md) | 关闭 Candidate 实施选择并明确正式治理边界 | Candidate Accepted |
| [2026-08-03 来源结论](source-resolution-2026-08-03.md) | 记录完成版协议直接关闭的 Header 编码、Validation 形态和完整购物车问题 | Source-settled |
| [A402 评审执行指南](a402-review-guide.md) | 评审角色、批次、Accept/Defer 门槛和会后流程 | Active process guide |
| [A402 评审纪要模板](a402-review-minutes-template.md) | 记录参与角色、证据、异议、决定和行动项 | Template |
| [ADR 模板](adr-template.md) | 被接受决定的持久化格式 | Template |
| [v2.1 对齐记录](v2.1-alignment.md) | 修订方向对开源架构的影响 | Active / Non-normative |

## 状态转换

```text
Open/Pending
  → Ready for review
  → Source-settled（由明确的协议事实源直接回答原问题）
  → Candidate Accepted（可执行 Working Draft；尚未完成公开治理）
  → Accepted | Rejected | Deferred
  → Superseded（仅由后续 Accepted ADR 替代）
```

每个 `DP-A402-NNN` 进入 `Accepted` 前必须：

1. 明确选择一个列出的 Option，或先修订决策包增加新 Option；
2. 链接公开 Issue、PR 或会议记录；
3. 使用 [`adr-template.md`](adr-template.md)建立 ADR；
4. 写明 Core、Binding、Profile、迁移和测试影响；
5. 在 Register 的 `decision_record` 填入 ADR 路径并更新状态；
6. 通过仓库检查，且不得把 Product Profile 事实冒充为 Core 决定。

ADR 编号按正式接受顺序分配，不预建空 ADR，也不把 `Candidate Accepted` 占位为正式 `Accepted`。

发起公开讨论时使用 [A402 协议决策 Issue 模板](../../../.github/ISSUE_TEMPLATE/a402-protocol-decision.md)。第一场评审只处理 `DP-A402-001`，其余项可以提供输入，但不越过 canonical source 门槛创建 Core Schema。
