# 治理模型

## 角色

| 角色 | 说明 |
|------|------|
| **Maintainer** | 核心维护者，负责规范质量把关、PR 合并、版本发布。初始维护者由项目发起方指定。 |
| **Contributor** | 社区贡献者，通过提交 PR/Issue 参与规范演进。 |
| **Adopter** | 采用方，在实际产品中实现协议并反馈实施经验。 |

## 规范演进流程

```
Issue 提出 → Maintainer 评估 → Proposal → Draft → Candidate → Recommendation
                                          ≥2周评审    ≥4周评审    Maintainer 2/3投票
```

| 阶段 | 说明 | 进入条件 |
|------|------|---------|
| Proposal | 变更提案，描述动机和方案 | Maintainer 认可提案方向 |
| Draft | 完整的规范修改草案 | 包含文档、Schema、示例 |
| Candidate | 经社区评审的候选版本 | 至少 2 个独立实现验证通过 |
| Recommendation | 正式发布的推荐版本 | Maintainer 团队 2/3 投票通过 |

## 工作组

| 工作组 | 职责 |
|--------|------|
| ADD Working Group | 委托授权域规范演进 |
| CID Working Group | 商业交互域规范演进 |
| PSD Working Group | 支付服务域规范演进 |
| TSD Working Group | 信任服务域规范演进 |

工作组对各自域内的规范变更具有初审权，跨域变更需相关工作组联合评审。

## 决策机制

- 常规变更：1 名 Maintainer 审批即可合并
- 规范新增或破坏性变更：至少 2 名 Maintainer 审批
- 版本发布：Maintainer 团队 2/3 多数投票通过
- 投票周期：至少 7 天

## 版本管理

- 规范版本号遵循语义化版本（SemVer）：`MAJOR.MINOR.PATCH`
- 新增字段或组件：`MINOR` 版本升级
- 破坏性变更：`MAJOR` 版本升级
- 勘误或澄清：`PATCH` 版本升级