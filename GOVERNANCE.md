# ACT Protocol 社区治理规范 (Governance)

本文档描述 ACT Protocol 项目的治理结构、决策流程和角色职责。

## 1. 概述（Overview）

ACT Protocol 是一个面向 AI Agent 与数字商业生态的开放协议，旨在为智能体之间的用户意图表达与授权、商业交互与协商、支付执行与结算、信任与身份体系，提供统一、可组合、可扩展的协议标准。

ACT 通过"能力域拆分 + 轻量治理协调"的方式，支持复杂商业系统在多方参与下的长期演进。

## 2. 治理原则（Governance Principles）

ACT Protocol 遵循以下核心原则：

### 2.1 开放性（Openness）
协议设计与演进过程完全公开透明，任何人均可参与讨论与贡献。

### 2.2 中立性（Neutrality）
ACT Protocol 不属于任何单一公司或组织，致力于成为行业级开放标准。

### 2.3 能力域自治（Domain Autonomy）
协议按照能力域划分，由各 Domain Working Group（DWG）独立负责设计与演进。

### 2.4 跨域一致性（Cross-domain Consistency）
不同能力域之间必须保持语义一致性与协议兼容性，由 TSC 统一协调。

### 2.5 可组合性（Composability）
协议设计优先支持模块化能力拆分与组合扩展。

## 3. 技术指导委员会（Technical Steering Committee, TSC）

### 3.1 定位

TSC 是 ACT Protocol 的技术协调与架构治理机构，负责协议整体架构一致性与跨域协作协调。

### 3.2 职责范围

TSC 主要负责：

#### （1）协议架构治理
- ACT 整体协议架构设计与演进
- 四大能力域边界定义与调整
- 跨域依赖关系管理

#### （2）跨域冲突协调
- DWG 之间的协议冲突裁决
- schema / interface 冲突处理
- capability 重叠与归属问题判断

#### （3）版本治理
- ACT 协议版本发布审批
- Breaking Change 审核
- 升级与迁移策略制定

#### （4）DWG 管理
- DWG 的设立、调整与合并
- DWG Maintainer 任命与调整

### 3.3 决策机制

TSC 在治理决策上遵循"**共识优先（Consensus-first）**"原则。

在无法达成共识时，可通过投票机制进行决策：

1. **投票机制**：每位 TSC Voting Member 拥有一票，投票仅限 Voting Members。
2. **法定人数**：TSC 会议需满足至少 50% 的 Voting Members 出席会议。若未达到法定人数，会议可以继续进行讨论，但不得做出任何正式决策。
3. **决策通过规则**：在满足法定人数的前提下，50% 以上投票通过即为通过。

### 3.4 当前 TSC 成员

ACT Protocol 当前技术指导委员会成员包括：

- Ant Group
- Alibaba Group

### 3.5 加入 TSC

欢迎对 ACT Protocol 有长期技术贡献与生态建设意愿的组织与个人参与相关治理工作。TSC 扩展机制将逐步开放。

## 4. 领域工作组 Domain Working Groups（DWGs）

ACT Protocol 按能力域划分四个 Domain Working Groups（DWG），每个 DWG 负责其领域协议的设计与演进。

DWG 具有一定自治权，但必须遵循 ACT 全局架构原则，并接受 TSC 的协调与监督。

### 4.1 委托授权域 DWG（Delegation & Authorization DWG）

负责用户意图表达与授权链路标准，确保智能体能够以可验证方式代表用户执行商业行为。

**主要职责：**
- 意图结构化表达规范
- 用户授权凭证（Intent Credential）标准
- 授权生命周期管理（生效、挂起、撤销、过期）

### 4.2 商业交互域 DWG（Commerce Interaction DWG）

负责智能体与商户之间的商业交互协议标准。

**主要职责：**
- 商品与服务目录接口标准
- 意图上下文传递机制
- 购物车与交易确认流程
- 商业协商与能力匹配机制

### 4.3 支付服务域 DWG（Payment Services DWG）

负责智能体支付行为的协议标准与执行流程。

**主要职责：**
- 支付能力绑定机制
- 支付执行流程规范
- 支持支付模式：
  - 即时支付（Real-time Payment）
  - 委托支付（Delegated Payment）
  - 智能体自主支付（Autonomous Payment）
- 支付结果验证与对账机制

### 4.4 信任服务域 DWG（Trust Services DWG）

负责 ACT 生态中的信任基础设施协议设计。

**主要职责：**
- 可信存证机制（Tamper-proof Logging）
- 智能体身份管理标准
- 声誉与风险评估机制（扩展方向）

### 4.5 DWG 协作机制

- 每个 DWG 独立演进自身能力域协议
- 涉及跨域影响的变更需进行 Cross-DWG Review
- 最终由 TSC 确认跨域一致性

## 5. 角色与职责

### 5.1 Lead Maintainer

- 项目整体技术方向的最终决策者
- 由 TSC 任命
- 负责协调 TSC 和各 DWG 的工作

### 5.2 Core Maintainers

**标准：**
- 对项目有长期持续贡献（至少6个月）
- 深入理解协议规范和设计哲学
- 得到 TSC 认可

**权限与义务：**
- PR 合并权限（需遵循评审规则）
- Issue 标签管理
- CI/CD 配置管理
- 发布管理
- 参与技术指导委员会投票
- 维护规范和代码质量

### 5.3 Maintainers

**标准：**
- 对项目有持续贡献（至少3个月）
- 熟悉特定能力域的协议与实现
- 得到 Core Maintainers 认可

**权限与义务：**
- 负责特定 DWG 内的评审与合并
- 回应社区在本领域的 Issue
- 推动 DWG 内达成共识
- 参与工作组会议

### 5.4 Contributors

- 任何提交过 PR/Issue 并被合并的人
- 参与社区讨论
- 可参与 DWG 会议

### 5.5 Adopters

- 在实际产品/服务中实现或使用 ACT 协议的组织/个人
- 反馈生产环境使用经验

## 6. 决策流程

### 6.1 变更分级

| 级别 | 描述 | 评审要求 | 决策人 |
|------|------|---------|--------|
| **P0 - 勘误** | 错别字、格式修正 | 1名 Maintainer | 任意 Maintainer |
| **P1 - 澄清** | 明确表述，不增功能 | DWG 评审 | DWG Lead |
| **P2 - 新增** | 新字段/组件/流程 | 全社区评审2周 | TSC 1/2多数 |
| **P3 - 重大变更** | 破坏性变更、架构调整 | 全社区评审4周 | TSC 2/3多数 |

### 6.2 ACT SEP（Specification Enhancement Proposal）

ACT Protocol 使用 SEP（Specification Enhancement Proposal）作为协议变更的标准流程。

SEP 用于管理 ACT Protocol 的所有规范级变更，包括：

- 新能力设计
- 协议扩展
- 跨域协调变更
- Breaking Change
- 治理规则调整

#### SEP 生命周期

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  提案    │ →  │  草案    │ →  │  评审    │ →  │  候选    │ →  │  正式    │
│ Proposal │    │  Draft   │    │  Review  │    │Candidate │    │   Rec    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
  新建Issue      提交Draft PR    公开评审       实现验证       投票发布
  讨论方向      （WIP标记）      收集反馈      （2+实现）      版本发布
```

#### SEP 基本要求

每个 SEP 应包含：

- 背景与问题定义
- 设计方案
- 兼容性影响分析
- 安全与风险考虑
- 实现建议（可选）

#### 阶段转换条件

| 阶段 | 说明 | 产出物 | 评审期 | 进入条件 |
|------|------|--------|--------|---------|
| **Proposal** | 变更提案 | 设计文档 | 1周讨论 | Maintainer 认可方向 |
| **Draft** | 规范草案 | 规范+Schema+示例 | 2周评审 | 内容完整，通过CI |
| **Review** | 社区评审 | 修订版 | 2-4周 | DWG 初审通过 |
| **Candidate** | 候选版本 | RC版本 | 4周 | 2个独立实现验证 |
| **Recommendation** | 正式版本 | 正式发布 | - | TSC 投票通过 |

### 6.3 投票机制

**参与资格：**
- TSC 投票：仅 TSC Voting Members
- DWG 决策：DWG 成员
- 社区意见征集：所有 Contributors

**投票方式：**
- 普通决议：GitHub PR 评论 +1/-1
- 正式投票：邮件列表或专门投票工具
- 沉默即同意：投票期结束无反对视为通过

**记录：**
- 所有正式投票结果记录在 `governance/decisions/` 目录
- 包含投票人、投票结果、主要意见汇总

## 7. 参与机制（Contribution & Participation）

ACT Protocol 欢迎社区通过以下方式参与：

- 提交 ACT SEP
- 参与 DWG 讨论与评审
- 提交 Issue / Pull Request
- 参与公开治理会议

有关贡献的具体政策与流程（包括代码贡献、提案规范、评审机制等）将在 `CONTRIBUTING.md` 文件中统一说明。

## 8. 沟通与透明机制（Communication & Transparency）

### 8.1 公开原则

ACT Protocol 所有治理活动遵循：

- 默认公开
- 默认可追溯
- 默认可审计

### 8.2 会议机制

ACT 的治理会议包括：

- TSC 会议
- DWG 会议
- Cross-DWG Review 会议

### 8.3 会议记录规范

所有会议必须：

- 在 GitHub 仓库中公开存档
- 形成会议纪要（Meeting Notes）
- 包含关键决策记录（Decision Log）
- 可关联相关 SEP 或 Issue

## 9. 版本发布

### 9.1 版本号规范

遵循语义化版本（Semantic Versioning）：`MAJOR.MINOR.PATCH`

- **MAJOR**：破坏性变更，不向后兼容
- **MINOR**：新增功能，向后兼容
- **PATCH**：Bug修复、澄清、优化

### 9.2 发布周期

| 版本类型 | 发布频率 | 发布时间 | 负责人 |
|---------|---------|---------|--------|
| **Patch** | 按需 | 积累足够修复后 | Release Manager |
| **Minor** | 每季度 | 每季度末 | Release Manager |
| **Major** | 每年 | 年度规划后 | TSC |

### 9.3 发布流程

1. **冻结期**：发布前2周特性冻结，仅接受Bug修复
2. **RC版本**：发布候选版，供社区验证
3. **发布投票**：TSC 对发布进行投票
4. **正式发布**：合并发布分支，打标签，生成发布说明
5. **发布公告**：邮件列表、社区论坛、社交媒体

## 10. 争议解决

### 10.1 技术争议

1. **DWG 内解决**：首先在相关工作组内讨论
2. **TSC 介入**：DWG 无法达成一致时升级至 TSC
3. **透明记录**：争议过程和最终决策记录在案

### 10.2 行为准则争议

参考[行为准则](CODE_OF_CONDUCT.md)中的执行流程。

## 11. 项目资产

### 11.1 知识产权

- 所有贡献采用 [Apache 2.0 许可证](LICENSE)
- 所有贡献者需签署 CLA（贡献者许可协议）
- 项目保留统一的品牌和商标使用权

### 11.2 代码仓库

| 仓库 | 用途 | 权限 |
|------|------|------|
| `act-protocol/act-protocol` | 主仓库，规范和实现 | TSC 维护 |
| `act-protocol/website` | 官方网站 | 网站工作组 |
| `act-protocol/test-suites` | 兼容性测试套件 | 实现者 DWG |

## 12. 协议演进与版本管理

- ACT Protocol 强调向后兼容性（Backward Compatibility）
- Breaking Change 必须经过 TSC 审核
- 重大版本升级需提供迁移路径与说明

## 13. 社区健康

### 13.1 透明度

- 所有技术决策在 GitHub 公开进行
- 会议纪要公开（敏感安全信息除外）
- 财务信息（如有）定期公开报告

### 13.2 包容性

- 鼓励多元化参与
- 新贡献者有导师引导
- 定期举办社区活动（线上/线下 meetup）

### 13.3 可持续性

- 培养新维护者
- 知识文档化
- 关键角色有备份

## 14. 治理演进

本治理文档自身也遵循变更流程：

- 治理变更需 TSC 2/3 多数通过
- 年度评审，根据项目发展阶段调整

## 联系

- 技术指导委员会：tsc@actprotocol.org
- 一般咨询：community@actprotocol.org
- 安全披露：security@actprotocol.org

---

*本治理模型参考了以下项目的最佳实践：*
- [MCP Governance](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/GOVERNANCE.md)
- [UCP Governance](https://github.com/Universal-Commerce-Protocol/.github/blob/main/GOVERNANCE.md)
- [ACP Governance](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/blob/main/docs/governance.md)
- [CNCF Governance](https://github.com/cncf/foundation/blob/main/charter.md)
- [Apache Project Governance](https://www.apache.org/foundation/governance/)

*最后更新：2026年5月*
