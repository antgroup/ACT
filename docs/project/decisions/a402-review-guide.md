# A402 决策评审执行指南

> 状态：Active process guide / Non-normative  
> 适用范围：`DP-A402-001`—`DP-A402-009`

本指南把[A402 最小机器契约决策包](protocol-decision-brief.md)转为可执行的公开评审流程。它不授予治理席位；在 [GOVERNANCE.md](../../../GOVERNANCE.md) 的正式成员和投票权尚未确认时，会议只能形成“推荐结论，等待有权主体确认”，不能自行标记 Accepted。

## 1. 评审前准备

发起人应：

1. 固定评审使用的仓库 Commit 和 [`a402-decision-register.json`](a402-decision-register.json) 版本；
2. 为每个计划讨论的 `DP-A402-NNN` 创建独立公开 Issue，使用 [A402 决策模板](../../../.github/ISSUE_TEMPLATE/a402-protocol-decision.md)；
3. 在 Issue 中链接对应 `PD-2.1-*`、候选规范、产品公开资料和已知实现证据；
4. 产品事实只用于验证 Product Profile 映射，不阻塞 Core/Binding 职责分层的评审；只收集可公开引用的产品事实，未公开输入不得复制到仓库；
5. 运行：

   ```bash
   python3 scripts/check_repository.py
   ```

6. 至少在会议前明确决策 owner role、记录人、所需 DWG 和产品事实提供角色。

## 2. 角色

| 角色 | 责任 | 是否自动拥有决策权 |
|---|---|---|
| Decision owner | 确认问题归属、选项完整性和最终审批路径 | 否；以正式治理登记为准 |
| Facilitator | 控制范围、顺序和时间，避免把实现偏好当产品事实 | 否 |
| Recorder | 使用会议模板记录选择、异议、证据和行动项 | 否 |
| Core/DWG reviewer | 评估语义、兼容、迁移和跨域影响 | 以治理登记为准 |
| Product fact reviewer | 提供可公开引用的产品事实和差异 | 只确认产品事实，不替 Core 决策 |
| Security reviewer | 评估重放、幂等、隐私、密钥和未知结果 | 否 |
| Implementer/TCK reviewer | 判断选项能否形成 Schema、SDK 和可执行测试 | 否 |

任何参与者都应披露其所代表的组织或产品利益。无法确认正式决策权时，纪要必须写 `Recommendation pending governance confirmation`。

## 3. 评审批次

建议分三批，避免下游决定依赖尚未选择的 canonical model：

| 批次 | 决策 | 目标 |
|---|---|---|
| Gate 1 | `DP-A402-001` | 确定机器契约的唯一权威源和版本方法 |
| Gate 2 | `DP-A402-002`、`003`、`007` | 确定 envelope、支付方法身份和已确认商业事实 |
| Gate 3 | `DP-A402-004`、`005`、`006`、`008`、`009` | 确定安全重试、验证/履约、恢复、发布范围和 Binding 封装 |

Gate 1 未接受时，Gate 2/3 可以讨论，但不得开始创建“权威 Core Schema”。Gate 2 未稳定时，不应接受依赖具体字段的 Gate 3 方案。

完整决策范围：

| ID | 本次只回答 |
|---|---|
| `DP-A402-001` | 机器契约的唯一权威源 |
| `DP-A402-002` | Core、Binding、Profile 对 Header envelope/编码的分工 |
| `DP-A402-003` | `method_id` 身份、版本、Schema 解析与发现 |
| `DP-A402-004` | 原请求关联、幂等与防重放 |
| `DP-A402-005` | 验证结果可见性与支付/交付/履约边界 |
| `DP-A402-006` | 公共状态、错误和恢复动作 |
| `DP-A402-007` | CID 已确认事实与跨域关联 |
| `DP-A402-008` | L1/L2/L3 的首个发布与验证范围 |
| `DP-A402-009` | 工作流 Binding 的封装和证据责任 |

## 4. 单项评审步骤

每项按以下顺序进行：

1. **Confirm scope**：问题是否属于 A402，是否与其他 Decision 重叠；
2. **Confirm sources**：区分协议修订事实、Product Profile 事实和实现观察；
3. **Review options**：确认 A/B/C 是否覆盖真实选择空间；
4. **Threat and failure review**：检查未知支付结果、重放、重复交付、产品不可用和敏感数据；
5. **Compatibility review**：检查 2.1 Working Draft、现有 Profile、Binding、Quickstart 和外部实现；
6. **Testability review**：每个结论如何生成 Schema、fixture 和可执行断言；
7. **Select action**：Accept A/B/C、Revise、Defer 或 Reject scope；
8. **Record dissent**：记录重要反对意见及其处理，不能只写“已达成一致”；
9. **Assign artifacts**：明确 ADR、规范、Schema、Binding、Profile、迁移和测试任务。

## 5. Accept / Defer 门槛

### Accept

只有同时满足下列条件，才可推荐 Accept：

- 选择对应现有 Option，或已先公开修订选项；
- 兼容、安全、隐私、幂等和迁移影响明确；
- 所需产品事实有公开来源或被明确排除出 Core；
- 至少定义一个正例、一个边界/失败测试意图；
- 决策 owner 与批准路径明确；
- 没有把 Recommendation、Product Preview 或 Quickstart 行为当成规范事实。

### Defer

Defer 必须写明：

- 缺少的具体输入；
- 负责提供输入的公开角色；
- 被阻塞资产；
- 未决定期间实现必须遵守的安全下限；
- 重新评审的客观条件。

“以后再说”不是有效 Defer。

## 6. 会后处理

记录人应在同一公开 Issue 中：

1. 发布[会议纪要](a402-review-minutes-template.md)；
2. 对终态结论建立 ADR；
3. 更新 Register 的 decision status；首个终态出现后 Register 改为 `partially-decided`；
4. 更新 `specs/2.1/revision-status.md` 的关联状态；
5. 创建落地任务，但在 ADR 合入前不修改 Core 语义；
6. 运行 `./scripts/verify.sh`；
7. 在所有九项终态完成时，才把 Register 标为 `complete`。

## 7. 第一场评审建议

第一场只要求处理 `DP-A402-001`：

- 是否接受 JSON Schema 作为 HTTP-first Candidate canonical source；
- JSON Schema Draft/Format 策略；
- `additionalProperties` 默认策略；
- 生成产物是否入库；
- Schema 与规范文字冲突时的发布门禁；
- 版本 `$id` 和 Breaking Change 规则。

如果任何一项无法回答，应选择 Revise 或 Defer，而不是以“方向同意”标记 Accepted。
