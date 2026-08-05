---
name: A402 协议决策评审
about: 评审 DP-A402-NNN 的现有选项，记录兼容、安全、产品输入和 ADR 结果
title: '[A402 Decision] DP-A402-NNN: '
labels: specification
---

> 本 Issue 是非规范性决策输入。推荐项不等于 Accepted；只有公开批准记录和 ADR 完成后，才能驱动 Core、Schema、Binding 或 TCK 变更。不要在 Issue 中提交密钥、完整 Proof、支付凭证或未公开产品材料。

## Decision ID

<!-- 只选择一个，并将标题中的 NNN 替换为实际编号 -->

- [ ] `DP-A402-001` Canonical machine-contract source
- [ ] `DP-A402-002` Header envelope 与编码
- [ ] `DP-A402-003` `method_id`、版本与发现
- [ ] `DP-A402-004` 原请求关联、幂等与防重放
- [ ] `DP-A402-005` 验证结果与履约边界
- [ ] `DP-A402-006` 状态、错误与恢复动作
- [ ] `DP-A402-007` CID 已确认事实与跨域关联
- [ ] `DP-A402-008` L1/L2/L3 发布范围
- [ ] `DP-A402-009` 工作流 Binding 封装与证据

决策包章节：

机器 Register 版本/Commit：

## Selected action

- [ ] Accept Option A
- [ ] Accept Option B
- [ ] Accept Option C
- [ ] Revise options
- [ ] Defer
- [ ] Reject scope

## Problem and sources

<!-- 链接协议候选、Pending Decision、公开产品事实和相关 Issue。不要只引用 Quickstart 代码。 -->

## Option assessment

| Option | Interoperability | Compatibility/migration | Security/privacy | Implementation/TCK cost |
|---|---|---|---|---|
| A |  |  |  |  |
| B |  |  |  |  |
| C |  |  |  |  |

## Required product input

<!-- 如果不需要产品输入，明确写 None。未公开事实只能标记待确认，不能粘贴进公开 Issue。 -->

## Impact

- [ ] ACT Core specification
- [ ] Canonical Schema/code generation
- [ ] HTTP or workflow Binding
- [ ] Product Profiles
- [ ] backward compatibility and upgrade impact
- [ ] Security, replay, idempotency, or privacy
- [ ] Candidate assertions/TCK
- [ ] No implementation change until another decision

具体影响：

## Decision record

Decision owner role：

Reviewers and represented roles：

Public meeting/PR record：

Decision date：

Reasoning, including rejected alternatives：

## Follow-up

- [ ] 已建立 ADR，或本 Issue 仍保持非终态
- [ ] 已更新 `a402-decision-register.json`
- [ ] 已更新对应 `PD-2.1-*`
- [ ] 已列出规范、Schema、Binding、Profile、迁移和测试任务
- [ ] 已运行 `python3 scripts/check_repository.py`

ADR path：

Deferred/re-review condition：
