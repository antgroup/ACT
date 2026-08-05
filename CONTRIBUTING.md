# 贡献指南 (Contributing Guide)

感谢您对 ACT Protocol 的关注！本文档详细说明如何参与协议的演进和改进。

## 目录

- [快速开始](#快速开始)
- [贡献类型](#贡献类型)
- [贡献流程](#贡献流程)
- [提交规范](#提交规范)
- [评审标准](#评审标准)
- [社区资源](#社区资源)

## 快速开始

### 在您开始之前

- 阅读我们的[行为准则](CODE_OF_CONDUCT.md)
- 了解项目的[治理规范](GOVERNANCE.md)
- 查看仓库现有 Issues 和公开项目状态，避免重复提案

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/act-protocol/act-protocol.git
cd act-protocol

# 运行仓库与全部 Quickstart 检查
./scripts/verify.sh
```

## 贡献类型

### 📋 规范文档贡献

- **勘误**：修正文档中的文字错误、链接失效等问题
- **澄清**：对模糊表述进行解释说明，不引入新功能
- **改进**：优化文档结构、增加示例、改进可读性
- **新增**：添加新的协议组件、字段或流程
- **变更**：修改现有规范的语义（需特别审慎）

### 🔧 技术实现贡献

- Quickstart、Binding 和开发者工具
- 通过一致性测试并声明覆盖范围的参考实现
- 已标记 Mock 边界的 Demo 修复
- 新语言的参考实现
- 测试用例和测试工具
- 开发者工具和 SDK

### 🧪 案例与验证

- 实际应用场景案例
- 实现兼容性测试报告
- 安全审计报告

## 贡献流程

### 1. 识别需求

- **Bug/问题**：先搜索现有 Issues，避免重复
- **新功能**：先创建 Issue 公开讨论范围和兼容性影响
- **安全问题**：参考[安全披露](SECURITY.md)流程

### 2. 创建 Issue

使用对应的 Issue 模板：

| 类型 | 模板 | 适用场景 |
|------|------|---------|
| 规范问题或提案 | `.github/ISSUE_TEMPLATE/spec-issue.md` | 规范勘误、澄清或变更建议 |
| A402 协议决策 | `.github/ISSUE_TEMPLATE/a402-protocol-decision.md` | 评审现有 `DP-A402-NNN` 选项并形成 ADR 输入 |
| 实现与工具问题 | `.github/ISSUE_TEMPLATE/implementation-issue.md` | Quickstart、Demo、Binding 或工具问题 |

安全漏洞不要创建公开 Issue，应按照 [SECURITY.md](SECURITY.md) 中经维护者确认的渠道报告。

### 3. ACT SEP（Specification Enhancement Proposal）

ACT Protocol 使用 SEP 作为协议变更的标准流程。SEP 用于管理所有规范级变更，包括：

- 新能力设计
- 协议扩展
- 跨域协调变更
- Breaking Change
- 治理规则调整

> [!IMPORTANT]
> `specs/2.1/` 中的 **Candidate Working Draft / Non-normative** 是公开评审内容标签，不等同于下方 SEP 生命周期的 **Candidate（RC）** 阶段。只有满足两个独立实现验证及相应评审门槛后，才能声明进入 SEP Candidate。

#### SEP 生命周期

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
│  提案    │ →  │  草案    │ →  │  评审    │ →  │  候选    │ →  │  正式发布    │
│ Proposal │    │  Draft   │    │  Review  │    │Candidate │    │Recommendation│
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────────┘
     │               │               │               │                │
     ▼               ▼               ▼               ▼                ▼
  讨论方向       完整实现         社区反馈         生产验证          投票通过
  Maintainer     代码+测试       2-4周           2个实现           TSC通过
  认可方向
```

#### 各阶段说明

| 阶段 | 说明 | 产出物 | 评审期 | 进入条件 |
|------|------|--------|--------|---------|
| **Proposal** | 变更提案 | 设计文档 | 1周讨论 | Maintainer 认可方向 |
| **Draft** | 规范草案 | 规范+Schema+示例 | 2周评审 | 内容完整，通过 CI |
| **Review** | 社区评审 | 修订版 | 2-4周 | DWG 初审通过 |
| **Candidate** | 候选版本 | RC版本 | 4周 | 2个独立实现验证 |
| **Recommendation** | 正式版本 | 正式发布 | - | TSC 投票通过 |

#### SEP 基本要求

每个 SEP 应包含：

- 背景与问题定义
- 设计方案
- 兼容性影响分析
- 安全与风险考虑
- 实现建议（可选）

### 3.1 A402 Candidate 决策评审

A402 2.1 的开放语义使用[决策包](docs/project/decisions/protocol-decision-brief.md)、[机器 Register](docs/project/decisions/a402-decision-register.json)和[评审执行指南](docs/project/decisions/a402-review-guide.md)推进。参与者应为每个 `DP-A402-NNN` 建立独立公开 Issue。

- 推荐项不是正式 Accepted 决策；仓库可以用 `Candidate Accepted` 冻结可执行 Working Draft，但必须继续标记 Non-normative；
- Product Profile 事实不能替代 Core 选择；
- 正式投票权未登记时，会议只能形成等待治理确认的推荐结论；
- Accepted/Rejected/Superseded 结果必须链接 ADR 或等价正式记录；
- 没有 Source-settled、Candidate Accepted 或正式 Accepted 记录时，不得修改对应 Core 语义或发布 Candidate Schema；只有正式 Accepted ADR 才能驱动 Stable/Recommendation 资产。

### 4. 提交 Pull Request

#### PR 准备清单

- [ ] 基于最新 `main` 分支创建特性分支
- [ ] 遵循[提交规范](#提交规范)
- [ ] 规范变更必须同步更新 JSON Schema
- [ ] Schema 变更必须同步更新示例
- [ ] 新增字段须提供至少2个示例（正常场景+边界场景）
- [ ] 破坏性变更须附带迁移说明；迁移目录将在版本策略确定后建立
- [ ] 所有测试通过
- [ ] 如项目发布了 CLA 签署机制，已按公开指引完成；当前机制仍待维护者确认

#### PR 审查流程

1. **自动检查**：CI 检查仓库完整性，并运行 Node 与 Java Quickstart 测试；Schema 和正式协议一致性验证仍在建设
2. **DWG 评审**：相关领域工作组技术评审；治理主体未确认时只能形成 Candidate recommendation
3. **Maintainer 评审**：代码/规范质量把关
4. **社区反馈**：公开征集意见（重大变更）
5. **合并**：获得足够批准后合并

## 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 类型 (Type)

| 类型 | 说明 | 适用场景 |
|------|------|---------|
| `feat` | 新功能 | 规范新增、实现新增 |
| `fix` | Bug修复 | 错误修正、安全修复 |
| `docs` | 文档 | 纯文档改进（无代码变更） |
| `style` | 格式 | 代码格式化（不影响功能） |
| `refactor` | 重构 | 代码重构，不新增功能或修复 bug |
| `perf` | 性能 | 性能优化 |
| `test` | 测试 | 添加或更新测试 |
| `chore` | 杂项 | 构建、CI、依赖更新等 |

#### 范围 (Scope)

- `specs` - 规范文档（如 `feat(specs): 新增委托支付流程`）
- `add` - 委托授权域
- `cid` - 商业交互域
- `psd` - 支付服务域
- `tsd` - 信任服务域
- `schema` - JSON Schema
- `impl` - 参考实现（可细分为 `impl-py`, `impl-go` 等）
- `docs` - 非规范文档
- `ci` - 持续集成

#### 示例

```
feat(psd): 新增A2A支付流程支持

- 定义PSD-PAY-A2A组件
- 新增HTTP 402支付诉求语义
- 添加子账户转账协议字段
- 提供Python实现示例

Closes #123
```

```
fix(schema): 修正DelegationPayRequest字段类型

amount字段应为decimal而非integer，支持小数金额

Fixes #456
```

## 评审标准

### 规范变更评审清单

**Maintainer 将检查以下方面：**

#### 技术正确性
- [ ] 设计与协议架构保持一致
- [ ] 与现有规范无冲突
- [ ] 考虑了安全性（加密、认证、授权）
- [ ] 考虑了互操作性

#### 完整性
- [ ] 规范文档完整
- [ ] JSON Schema 已更新
- [ ] 示例已提供
- [ ] 边界情况已考虑

#### 质量
- [ ] 文档清晰、无歧义
- [ ] 术语使用一致
- [ ] 中英文术语对照明确

### 代码贡献评审清单

- [ ] 代码遵循项目编码规范
- [ ] 单元测试通过率100%
- [ ] 新增功能有对应测试覆盖
- [ ] 无安全漏洞（通过自动扫描）
- [ ] 性能影响已评估（关键路径）

## 社区资源

### 沟通渠道

- **GitHub Issues**：规范问题、实现缺陷和功能建议。
- **安全披露**：使用 [SECURITY.md](SECURITY.md) 中经确认的私密渠道；不要公开漏洞细节。

### 工作组 (DWG) 会议

工作组结构仍处于治理草案阶段。正式会议频率、公开议程和纪要入口将在治理机制确认后发布，不在贡献指南中预先承诺。

### 相关资源

- [协议规范](specs/)
- [Product Profile Preview Schema](profiles/alipay-ai-pay/schemas/)
- [Quickstart](quickstarts/)
- [Demo](demos/)
- [治理规范](GOVERNANCE.md)

## 许可

通过向 ACT Protocol 项目提交贡献，您确认有权提交相关内容，并同意贡献按照 [LICENSE](LICENSE) 中与文件类型和目录对应的许可证发布。正式贡献者协议或 CLA 机制仍需维护者确认。

---

*感谢所有为 ACT Protocol 做出贡献的社区成员！*

*最后更新：2026年5月*
