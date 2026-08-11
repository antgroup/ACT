# ACT Protocol 开源项目申请

> 状态：内部申请材料草稿；生成日期：2026-08-04；内容最后同步：2026-08-06
> 模板来源：[XX 开源项目申请模版 v1.0](https://yuque.antfin.com/open-source/workgroup-admin/bzisub9qvrf6od8t)，模板更新时间：2026-07-29  
> 本文不属于 ACT 规范，不随本文授予任何正式治理席位、开源发布许可或合规结论。

### 项目名称

ACT Protocol（Agentic Commerce Trust Protocol）

#### 背景

AI Agent 正在从信息获取走向商品选择、服务调用和交易执行。传统支付接入主要面向人操作页面或固定业务系统，Agent 在面对收费 API、MCP Tool、Skill 或数字服务时，仍缺少一套跨产品、可机读、可验证的方式回答以下问题：

- 当前资源为什么需要支付、应付多少、可以使用什么支付方法；
- Agent 获得何种用户授权后可以发起支付；
- 支付凭证如何与原请求、订单和资源关联；
- 服务方如何验凭、交付、防重放并进行错误恢复；
- 协议语义、支付产品、传输 Binding 和演示代码之间如何避免相互混淆。

ACT 采用四个能力域组织智能体商业交互：委托授权域（ADD）、商业交互域（CID）、支付服务域（PSD）和信任服务域（TSD）。当前开源版本采用 PSD-first，以支付服务域作为开发者一键接入的主轴，首先公开支付工具绑定、Agent 子账户、INS/L1、DEL/L2、AUP/L3 和独立 A402 接入协议。

支付宝 AI 付是首个公开 Product Profile 和接入验证对象，但不是 ACT Core 的组成部分。协议事实、支付宝产品事实和 Quickstart/Demo 实现保持分层：ACT 定义跨产品语义，Product Profile 负责产品映射，支付宝官网继续负责开户、凭证、沙箱和产品 API 操作。

#### slogan 和定位是什么？

**Slogan：让 Agent 支付像调用 API 一样可理解、可验证、可接入。**

ACT Protocol 定位为面向智能体商业交互的开放协议与开发者契约，首期重点解决 Agent 与收费服务之间的机器支付接入问题：

- 对 Agent/应用开发者，提供可机读的支付要求、Proof、验证、重试和错误恢复语义；
- 对收费 API、MCP Tool 和 Skill 提供者，提供从 HTTP 402 出账到验凭、交付和履约确认的安全基线；
- 对支付服务方，提供将产品字段和能力映射到统一协议语义的 Product Profile 机制；
- 对协议实现者，提供 Schema、Fixture、断言和验证工具，降低不同实现之间的语义漂移。

ACT 不是支付产品、钱包或清结算系统，也不复制任何支付机构的开户与沙箱能力。

#### 开源的目标是什么？

**长期目标（3 年方向）**

1. 建立供应商中立、可组合的智能体商业交互协议，使 Agent、商户服务和支付服务方能够围绕统一语义互操作。
2. 形成开放的规范治理、Product Profile、Binding 和一致性测试机制，使协议演进不依赖单一产品实现。
3. 推动至少两个独立实现和多个公开 Product Profile 共享同一 Core 契约；达到社区治理条件后，评估向中立基金会或行业组织捐献。

**开源后 12 个月目标**

| 时间 | 目标 | 可验证指标 |
|---|---|---|
| 0—1 个月 | 完成 ACT 2.1 Candidate Working Draft 和 Alipay AI Pay Profile Preview 的公开发布 | 安全渠道、公开仓库和发布快照门禁完成；所有公开资产明确标记 Candidate/Preview/Non-normative |
| 1—3 个月 | 验证开发者能够独立理解并运行 L1 + A402 接入路径 | 至少 3 名非项目开发者完成 clean-room 试用；本地 Quickstart 完成率不低于 80%；问题有可追踪记录 |
| 3—6 个月 | 收集真实采用反馈并形成下一阶段协议提案 | 至少 2 个外部团队提交接入反馈；至少 1 个独立实现或公开适配器进入持续验证 |
| 6—12 个月 | 建立跨实现验证与外部共建机制 | 争取达到 2 个独立实现；形成可执行 TCK 雏形；至少 1 名外部长期贡献者进入 Maintainer 培育流程 |

目标以“独立实现和可复现接入”为核心，不以 GitHub Star 数作为协议成功的唯一指标。若独立采用没有发生，项目应收缩范围或进入归档评估，而不是通过扩大协议范围制造表面进展。

#### 开源内容

计划开源以下内容：

| 类型 | 内容 | 当前状态 |
|---|---|---|
| ACT 2.1 Candidate | ADD/CID/PSD/TSD 四域语义、典型场景、A402、跨域连接规则和修订状态 | Candidate Working Draft / Non-normative |
| 机器契约 | A402 JSON Schema、有效/无效 Fixture、错误目录、状态转换和校验器 | Candidate / Non-normative |
| Bindings | 跨产品 HTTP A402 Binding | Preview |
| Product Profile | Alipay AI Pay 字段、生命周期、错误、Skill/CLI 和产品事实映射 | `0.9-preview.1` / Non-normative |
| Quickstarts | 买方 Agent、卖方 Metered REST Provider、端到端本地 402 路径 | Preview；本地路径不支付 |
| Demo | Guided Preview 与经过脱敏审查的官方沙箱证据回放工具 | 不实现或模拟支付成功 |
| 工程工具 | 仓库检查、Schema/Fixture 验证、发布门禁、沙箱前置条件检查 | 已建立本地验证入口 |
| 社区材料 | README、贡献指南、行为准则、治理草案、安全披露说明和 SEP 流程 | AntSRC 安全渠道已确认；正式治理待确认 |

明确不进入开源范围的内容：

- ACT 2.0 旧版目录、旧 Schema 和旧 Mock Demo；
- 支付宝或其他机构的专有支付、风控、账户、清结算实现；
- 支付宝官网已经维护的开户、密钥申请、沙箱账号和产品操作教程；
- 测试或生产私钥、访问令牌、完整 Payment-Proof、真实商户配置和未脱敏交易证据；
- 仅存在于内部讨论、尚未通过治理或无法公开追溯的协议决定。

### 项目 ReadMe

项目开源后的根 README 已按开发者任务组织，计划持续包含：

1. 项目一句话定位、Candidate/Preview 状态和禁止使用的合规声明；
2. Agent 开发者、收费服务提供者和协议实现者三条入口；
3. 一条无需密钥、不会发起支付的本地 Golden Path；
4. Agent 支付与 AI 按量付费如何组成同一 HTTP 402 闭环；
5. Core、Binding、Product Profile、Quickstart、Demo 和 Conformance 的边界；
6. 当前版本、Normative、Production Certified 状态和建议实现基线；
7. 仓库结构、完整验证命令、贡献流程、治理、安全和许可证入口；
8. 支付产品开户、沙箱和 API 操作的官方链接，不在仓库重复维护产品手册。

当前 README 草稿见仓库根目录 `README.md`。本地验证入口为：

```bash
npm --prefix code/examples/alipay/end-to-end-402 run local
./scripts/verify.sh
```

第一条命令只验证 402 解析和假 Proof 不得交付资源；第二条命令运行仓库、Candidate 机器契约、Node、Java 和 Demo 检查。

### Antcode 地址

当前内部仓库 remote：

```text
git@code.alipay.com:act-group/act-protocol.git
```

公开 GitHub 仓库地址：**申请前待确认**。公开地址确认前，README 和贡献指南中的 GitHub URL 仅视为计划地址，不代表仓库已经公开。

### 开源投入同学信息 GitHub Login

| **同学花名** | **职责** | **GitHub URL** |
|---|---|---|
| 观岳 | ACT 2.1 四域协议正文、典型场景、A402、状态机和错误恢复 | 申请前待补充 |
| 念箴 | 开源信息架构、Alipay Profile、Quickstart、Demo、验证和发布 | 申请前待补充 |

说明：正式申请前需由项目负责人确认完整投入名单、GitHub Login、持续投入时间和替补维护者。不能仅以历史提交记录推定正式 Maintainer 或治理席位。

### 当前进展

截至 2026-08-06，项目处于“内容 Candidate/Preview 已形成，尚未公开发布”的阶段：

- ACT 2.1 官网尚未更新时，已以观岳维护的《委托授权域》《商业交互域》《支付服务域》《可信存证》《信用关联》语雀正文为对应域事实源，建立四域语义 Candidate 和典型场景指南；公开包不再包含 2.0。
- ADD、CID 和 TSD 尚未冻结正式机器 Schema；仓库不实现来源未公开的 ACT Trust Chain、信用模型或信用服务，不据此声明全域 Conformance。
- 已实现 A402 三类 Header 的 Candidate Schema、Fixture、错误目录、六态转换和本地校验器。
- 8/8 A402 Candidate 断言已经链接到检查或测试；仍不等同于正式跨实现 TCK。
- 已建立 Alipay AI Pay Profile `0.9-preview.1`、三类产品 Preview Schema、产品错误映射和机器可读复核状态。
- 已建立买方、卖方和端到端 Quickstart；支付宝官网沙箱只作为外部验证源，仓库不复制沙箱。
- 最近一次全量验证通过：31 项 Node/Java/Demo 测试通过，仓库链接、JSON、Python 和 A402 契约检查通过。
- 已拆分 ACT Candidate、Profile Preview、Sandbox Verified 和 SEP Candidate 四类发布门禁，避免用沙箱阻塞协议 Candidate，也避免把本地测试冒充真实互操作。

当前公开发布仍受以下事项阻塞：

1. 项目已确认 `Ant Group Co., Ltd.`、CC BY 4.0 / Apache 2.0；当前不启用额外贡献协议或 DCO sign-off；
2. 确认公开 GitHub 仓库、组织归属和发布权限；
3. 形成干净、经评审并通过公开 CI 的发布提交；
4. 正式 TSC/DWG 名单、投票权和对外治理承诺尚未确认。

支付宝真实沙箱证据只阻塞 `Sandbox Verified` 主张，不阻塞 ACT Candidate 或 Alipay Profile Preview 内容准备。

### 后续计划

#### Roadmap/技术路线

**开源发布前**

- 关闭安全渠道、公开仓库和发布快照三项剩余 P0 门禁；
- 对公开包执行敏感信息、内部链接、许可证和依赖供应链复核；
- 完成至少一轮非项目开发者 clean-room onboarding；
- 冻结 ACT Candidate 和 Profile Preview 的版本、Changelog 与发布说明。

**开源后 0—3 个月**

- 以 L1 + A402 作为唯一推荐实现主路径，持续修复开发者接入断点；
- 通过公开 Issue/PR 收集 A402 字段、幂等、防重放和错误恢复反馈；
- 在具备官方账号和证据条件后，完成 Alipay Sandbox Verified 的独立声明，不把它升级为 ACT Conformance；
- 补齐英文 README、架构摘要、两条 Getting Started 和 Profile 摘要。

**开源后 3—6 个月**

- 推进 capability discovery、`method_schema_url` 安全与缓存规则的 SEP 提案；
- 基于真实接入需求评估 provider-neutral codec/SDK，未经包名、版本和供应链评审不发布 npm 包；
- 邀请至少两个外部团队进行接入或协议 review；
- 建立可公开复现的兼容矩阵和问题分类数据。

**开源后 6—12 个月**

- 以两个独立实现为目标推进 SEP Candidate，而不是由单一 Product Profile 证明协议成熟；
- 将现有 Candidate 断言演进为可跨实现执行的 TCK；
- 评估第二个真实 Product Profile，禁止使用虚构 PSP 证明跨产品能力；
- 根据外部贡献情况调整 Maintainer、DWG 和 TSC 构成，并决定是否启动基金会捐献提案。

#### 资源投入

建议项目发起方在申请时确认以下最低持续投入；下列比例是申请草案，不代表已经完成资源承诺：

| 角色 | 建议投入 | 主要责任 |
|---|---:|---|
| 协议 Maintainer | 0.3 FTE | PSD/A402 议题、Schema 语义、SEP 和版本评审 |
| Profile/工程 Maintainer | 0.5 FTE（发布期） | Product Profile、Quickstart、测试、发布和依赖维护 |
| Developer Relations / 社区运营 | 0.2 FTE | 文档、Issue triage、Office Hours、案例和活动 |
| 安全接口人 | 按需 + 明确 SLA | 私密漏洞接收、分级、修复协调和公告 |
| 法务/开源办公室 | 发布门禁评审 | 版权、许可证、入站贡献条款、商标和第三方依赖 |

建议运行节奏：每周一次 Issue/PR triage，每月一次公开 Office Hours，每季度一次路线图与治理复盘。首年需要至少两名具备合并权限的维护者，避免单点维护风险。

#### 社区增长规划

**我们的北极星指标是？**

北极星指标：**能够在公开版本和测试条件下复现的独立兼容实现数。**

辅助指标：

- 非项目开发者完成 Getting Started 的成功率和中位耗时；
- 外部实现/接入报告数量；
- 外部提交的有效 Issue、PR 和被合并贡献者数量；
- Issue 首次响应时间与阻塞问题关闭时间；
- 使用相同 Core 契约的公开 Product Profile 数量。

**我们的关键运营 TA（目标用户）是？关键指标是？**

TA：

1. 开发可执行交易的 Agent、Agent Framework 和 AI 应用团队；
2. 提供收费 API、MCP Tool、Skill 或数字内容的服务团队；
3. 支付服务方、钱包、收单和机器支付基础设施团队；
4. 研究 Agent 安全、授权、身份和协议互操作的开源开发者与机构。

指标：

- 首年完成不少于 3 次 clean-room onboarding；
- 6 个月内获得至少 2 个外部团队的结构化接入反馈；
- 首年争取形成 2 个独立实现或持续验证中的实现分支；
- 工作日 Issue 首次响应中位数不超过 5 天；
- 首年培养至少 1 名非发起团队的长期贡献者。

**我们计划采用的主要增长手段包括：**

- 在 2026 外滩大会及相关 Agent/支付开发者活动进行协议和真实接入分享；
- 发布“L1 + A402 五分钟接入”“Proof 防重放”“协议层与产品层如何解耦”等技术文章；
- 围绕公开 Candidate 决策运行 Issue/SEP review、线上 Office Hours 和实现者圆桌；
- 与 Agent Framework、MCP Tool/Skill 开发者和收费 API 团队开展联合 Quickstart；
- 以脱敏、可复现的接入报告替代不可验证的产品宣传；
- 在 GitHub Release、Discussions 和公开路线图中持续披露成熟度、Pending Decision 和兼容范围。

**d. 社区治理机制**

项目建议采用分阶段治理，不在申请阶段虚构已经存在的中立社区：

1. **启动期：蚂蚁发起、公开决策。** 蚂蚁承担首个公开版本、法务、安全和发布责任；规范决定通过公开 Issue、PR、决策记录和 SEP 流程留痕。Candidate Working Draft 不等同于正式 Recommendation。
2. **共建期：按贡献获得角色。** 外部参与者可以从 Contributor 进入 Maintainer 培育流程；协议域由 DWG 评审，跨域和版本问题由 TSC 协调。正式成员、任期、投票权和利益冲突必须公开登记。
3. **中立化评估期：满足条件后提案。** 当至少两个外部组织持续共建、存在两个独立实现且发布流程稳定后，由公开治理提案决定是否捐献基金会或行业组织；在正式批准前不对外承诺具体基金会和时间表。

正式发布前必须确认首届 Maintainer/TSC 名单、决策法定人数、商标与域名管理、行为准则执行人、安全接口人以及项目归档机制。

## 申请前待补充清单

- [ ] 公开 GitHub 组织与仓库 URL；
- [ ] 所有持续投入同学的花名、GitHub Login 和投入比例；
- [x] 确定版权主体 `Ant Group Co., Ltd.`、许可证目录分配和入站贡献条款；当前无额外签署前置；
- [x] 私密安全报告平台确定为 `https://security.alipay.com/`（AntSRC）；
- [ ] 首届 Maintainer、TSC/DWG 名单、投票权和利益冲突披露；
- [ ] 商标、Logo、域名和社交账号归属；
- [ ] 公开发布日、Release owner 和回滚/归档责任；
- [ ] 第一批外部共建或 clean-room 试用团队。
