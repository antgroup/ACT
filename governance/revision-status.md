# ACT 修订与开源重构追踪

> 状态：Active / Non-normative  
> 最后更新：2026-08-11

本文件连接“协议修订”“支付宝产品接入”和“开源工程交付”。它不替代正式决策记录；当某项结论被接受后，应建立独立 ADR、Issue 或 PR，并从本表链接到证据。

## 1. 修订主题追踪

| ID | 修订主题 | 当前项目问题 | 预期产物 | 影响区域 | 状态 |
|---|---|---|---|---|---|
| REV-001 | 协议重新定位 | 协议、产品和 Demo 边界不清 | Core/Profile/Binding 定位 | README、架构 | Done |
| REV-002 | Core 与 Extension | 所有能力在同一层级呈现 | 最小 Core 与扩展规则 | Specs、Profiles | Done for A402 Candidate |
| REV-003 | Common Message | Skill、MCP、OpenAPI 可能重复定义消息 | 通用消息封装和验证规则 | Core、Bindings | Done for A402 envelope; broader scope deferred |
| REV-004 | Agent Discovery/Profile | 缺少能力发现与兼容性声明 | Agent/Profile 描述模型 | ADD、CID、Profiles | Deferred beyond PSD-first publication |
| REV-005 | Payment Requirement | 账单、支付挑战和产品字段混杂 | 中立支付要求语义 | PSD、HTTP Binding | Done for Candidate |
| REV-006 | Payment Proof | 凭证结构、验证者和校验责任不完整 | Proof 与 Verification 模型 | PSD、Profiles | Done for Candidate |
| REV-007 | Lifecycle | 协议状态与产品状态混杂 | 通用生命周期和映射规则 | Core、Profiles | Done for Candidate; Product mapping review remains |
| REV-008 | Callback/Event | 异步支付和履约结果边界不清 | Callback/Event 模型 | Core、Bindings | Deferred to TSD/event work |
| REV-009 | Error Recovery | 错误主要依靠文字说明 | 结构化错误和恢复动作 | Core、Profiles | Done for Candidate |
| REV-010 | `valid_next_actions` | Agent 不知道失败后能做什么 | 可执行的下一步动作模型 | Common Message | Done for Candidate |
| REV-011 | Field Mapping | ACT 对产品字段缺少显式映射 | Profile 映射规范 | Profiles | Done for Profile Preview |
| REV-012 | Conformance | 示例不能证明协议兼容 | Core/Profile 测试套件 | Conformance | In progress; Candidate checks exist, independent TCK pending |
| REV-013 | Compatibility | 现有组件、Schema 和示例命名不一致 | 版本和迁移策略 | 全仓库 | Done for Candidate manifest |
| REV-014 | 402 与支付授权级别 | 旧版模型将 402 与 AUP 场景耦合 | 候选 `PSD-PAY-A402`，供 INS/DEL/AUP 引用 | PSD、Bindings、Profiles | Done for Candidate; formal ratification pending |
| REV-015 | CID 交易确认与 Payment Requirement | `Payment-Needed` 与交易确认结果的关系不明确 | CID-CART-CFM 到 PSD 的引用规则 | CID、PSD、Profiles | Done for Candidate minimum correlation |
| REV-016 | 产品履约回调与 TSD | 产品履约确认、支付回执和可信事件容易混为一层 | PSD 回执、业务履约与 TSD 事件边界 | PSD、TSD、Profiles | Candidate boundary done; Product review remains |
| REV-017 | 工作流级 Binding | 官方 Skill/CLI 封装支付、Proof 提交、资源重试和履约动作 | Binding 覆盖声明与 Core 消息封装规则 | Bindings、PSD、Profiles | Done for Candidate manifest |
| REV-018 | PSD 修订事实源 | 曾误将修订分析当作完整协议，随后又长期保留“基线 + 增量”模型 | 2026-08-03 完成版《支付服务域》作为单一协议事实源，修订分析仅作追溯 | PSD、Profile、Quickstarts | Candidate aligned |
| REV-019 | 支付域一键接入 | 本地 402 可一键预览；官方产品操作由 AIPay 官网负责 | smoke / buyer / seller / sandbox E2E 四级入口 | README、Quickstarts、Tests | Done for open-source Preview; Sandbox Verified pending |
| REV-020 | CID 协议事实源 | 仓库原先只有 `CID-PCA-NEG` 支付边界，未覆盖语雀已明确的完整商业交互域 | CID 四组件、核心对象、跨域边界和来源指纹 | CID、PSD、Profiles | Candidate aligned; wire Schema decisions pending |
| REV-021 | CID 黄色安全修订 | 曾把整篇 CID 基线误记为本轮变化，维护者确认只有黄色部分是修改点 | 能力声明来源校验、关键字段一致性、失败关闭 | CID-PCA-NEG、Profiles、安全检查 | Candidate aligned and regression-checked |
| REV-022 | ADD 协议事实源 | 仓库原先只维护 IAC 支付依赖，未公开完整意图、ISR、签发与生命周期语义 | ADD 三组件、来源指纹、黄色字段修订 | ADD、CID、PSD、TSD | Candidate aligned; machine contract pending |
| REV-023 | 跨域典型场景 | 域组件齐备但开发者缺少按用户在场/授权级别选择流程的入口 | 四类端到端场景与来源优先级 | README、Specs、Profiles | Candidate guide aligned |
| REV-024 | TSD 子篇结构 | 仓库把可信存证缩减成支付证据边界，且未体现信用关联新增子篇 | 可信存证五组件 + 信用关联五组件 | TSD、跨域证据、风控引用 | Candidate aligned; machine contracts pending |
| REV-025 | TSD 实现边界 | 来源提及 ACT Trust Chain、信用服务与验证报文，但公开接口和 Schema 未冻结 | 明确语义 Candidate 与可运行实现的边界 | Specs、Release、Tests | Pending protocol decisions; no fake implementation |
| REV-026 | 协议公开事实源 | 活动文档仍把内部语雀作为权威入口，外部开发者无法独立核对 | `act-protocol.com` 作为公开事实源；语雀仅保留历史同步证据；官网漂移检查 | README、Specs、Profiles、CI | Source switched; official semantic refresh pending |

## 2. 开源重构工作项

| ID | 工作项 | 阶段 | 依赖 | 状态 | 交付证据 |
|---|---|---|---|---|---|
| ACT-OSR-001 | 建立重构工作分支 | Phase 0 | 无 | Done | `codex/open-source-restructure` |
| ACT-OSR-002 | 建立目标、架构、产品基线和计划文档 | Phase 0 | 无 | Done | 本目录 |
| ACT-OSR-003 | 从根 README 提供重构入口 | Phase 0 | ACT-OSR-002 | Done | `README.md` |
| ACT-OSR-003A | 建立外滩大会发布章程 | Phase 0 | DEC-001—012 | Historical internal planning | 不进入公开发布快照 |
| ACT-OSR-003B | 建立 Alipay AI Pay 对齐矩阵初稿 | Phase 0 | ACT-OSR-002 | Done | `integrations/profiles/alipay-ai-pay/` |
| ACT-OSR-003C | 建立产品到 ACT 四域组件映射 | Phase 0 | ACT-OSR-003B | Done | `integrations/profiles/alipay-ai-pay/mappings/domains.md` |
| ACT-OSR-004 | 审计断链和虚构目录 | Phase 1 | 无 | Done | `audits/repository-audit.md` |
| ACT-OSR-005 | 校正规范和实现成熟度描述 | Phase 1 | 治理确认 | Done for current Candidate labels | README、Manifest、target-based release gates |
| ACT-OSR-006 | 从公开主线移除旧 Python 2.0 Mock Demo | Phase 1 | 无 | Done | 历史代码保留在 Git；当前入口为 `code/web-client/alipay-ai-pay-showcase/` |
| ACT-OSR-007 | 建立基础 CI | Phase 1 | ACT-OSR-004 | Done | `scripts/check_repository.py`、workflow |
| ACT-OSR-008 | 编写接入路径选择页 | Phase 2 | REV-001 | Done | `docs/getting-started/README.md` |
| ACT-OSR-009 | 编写 Agent 支付 Getting Started | Phase 2 | 支付宝公开资料复核 | Done | `docs/getting-started/agent-payment.md` |
| ACT-OSR-010 | 编写 AI 按量付费 Getting Started | Phase 2 | 支付宝公开资料复核 | Done | `docs/getting-started/metered-payment.md` |
| ACT-OSR-010A | 编写端到端 402 验证计划 | Phase 2 | ACT-OSR-009、010 | Done | `docs/getting-started/end-to-end-402.md` |
| ACT-OSR-010B | 建立双侧能力接入契约 v0.1 | Phase 2 | ACT-OSR-003C、010A | Done | `integrations/profiles/alipay-ai-pay/capabilities/end-to-end-contract.md` |
| ACT-OSR-010C | 复核双侧契约对应的官网产品事实 | Phase 2 | ACT-OSR-010B | Done | `integrations/profiles/alipay-ai-pay/sources/audits/2026-07-21-product.md` |
| ACT-OSR-010D | 核对官方 Agent Payment Skill/CLI 行为 | Phase 2 | ACT-OSR-010B | Done | `integrations/profiles/alipay-ai-pay/sources/audits/2026-07-21-skill-cli.md` |
| ACT-OSR-010E | 建立真实端到端验证证据模板 | Phase 2 | ACT-OSR-010B、010D | Done | `docs/getting-started/end-to-end-evidence-template.md` |
| ACT-OSR-010F | 整理协议最小决策简报 | Phase 2 | REV-014—017 | Candidate decisions complete; DWG ratification pending | `decisions/protocol-decision-brief.md`、`decisions/a402-decision-register.json` |
| ACT-OSR-010G | 将 v2.1 修订方向对齐开源框架 | Phase 2 | REV-014—017 | Done | `decisions/v2.1-alignment.md` |
| ACT-OSR-011 | 建立 ACT Core 候选草案 | Phase 3 | REV-002—REV-010 | Initial candidate established; governance pending | `specs/2.1/` |
| ACT-OSR-012 | 建立 Alipay AI Pay Profile | Phase 4 | ACT-OSR-011、产品复核 | Preview established; Product review remains | `integrations/profiles/alipay-ai-pay/` |
| ACT-OSR-013 | 实现 Agent Payment Quickstart | Phase 5 | 官方 Skill/CLI | Done for Preview; Sandbox evidence is a separate claim | `code/examples/alipay/agent-payment/` |
| ACT-OSR-014 | 实现 Metered REST Quickstart | Phase 5 | Alipay Profile 工作映射 | Done for Preview; Sandbox evidence is a separate claim | `code/examples/alipay/metered-rest-provider/` |
| ACT-OSR-015 | 实现端到端 402 Quickstart | Phase 5 | ACT-OSR-013、014 | Done for local Preview; official Sandbox not verified | `code/examples/alipay/end-to-end-402/` |
| ACT-OSR-016 | 建立一致性测试 | Phase 6 | REV-012、v2.1 候选规范 | Candidate contract checks implemented | A402 Schema/fixtures/validator 与 Quickstart 测试已建立；正式 Conformance 待独立实现 |
| ACT-OSR-017 | 建立外滩大会支付服务域执行方案与倒排计划 | Phase 0 | DEC-001—014 | Historical internal planning | 不进入公开发布快照 |
| ACT-OSR-018 | 建立支付宝大会 Web Demo 与验收契约 | Phase 5 | ACT-OSR-013—015 | Web、双侧 Adapter 和证据工具已实现；Runtime 接线与沙箱证据待完成 | `code/web-client/alipay-ai-pay-showcase/` |
| ACT-OSR-019 | 将支付宝专属 Skill/CLI Binding 归入产品 Profile | Phase 1 | DEC-002、REV-017 | Done | `integrations/profiles/alipay-ai-pay/bindings/skill-cli/` |
| ACT-OSR-020 | 使用官网沙箱完成端到端验证并沉淀脱敏证据 | Phase 6 | ACT-OSR-018、AIPay 官网沙箱 | Optional claim gate; not completed | 只阻塞 `alipay-sandbox-verified`，不阻塞 ACT Candidate/Profile Preview |
| ACT-OSR-021 | 将 A402 Pending Decision 转为可逐项表决的决策包、机器 Register 和 ADR 流程 | Phase 3 | ACT-OSR-010F、011 | Candidate decisions complete; formal DWG ratification pending | `decisions/README.md`、`decisions/protocol-decision-brief.md`、`decisions/a402-decision-register.json` |
| ACT-OSR-022 | 建立 A402 公开决策 Issue、DWG 评审执行和会议纪要流程 | Phase 3 | ACT-OSR-021、治理角色确认 | Workflow ready; formal decision authority pending | `.github/ISSUE_TEMPLATE/a402-protocol-decision.md`、`decisions/a402-review-guide.md`、`decisions/a402-review-minutes-template.md` |
| ACT-OSR-023 | 从公开包移除旧版规范、Schema、示例和迁移草案，公开依赖统一指向 2.1 Candidate | Phase 1 | 维护者范围决定 | Done for current tree; history decision deferred | `specs/2.1/`、`release-manifest.json`；历史处理见 DEC-024 |
| ACT-OSR-024 | 按支付服务域基线重新建立 2.1 PSD 六组件候选，并恢复 A402 字段/状态/错误语义 | Phase 3 | REV-018 | Done | `specs/2.1/domains/payment-services.md`、`specs/2.1/a402/specification.md`、`scripts/check_repository.py` |
| ACT-OSR-025 | 收敛 L1 + A402 一键接入路径 | Phase 5 | REV-019、官方产品前置条件 | Done for Preview | 仓库提供代码入口；开户、密钥与沙箱操作统一引用官网 |
| ACT-OSR-026 | 自动检查真实沙箱运行前置条件，且不读取或输出密钥值、不创建订单、不发起支付 | Phase 6 | ACT-OSR-014、015、020 | Done | `code/examples/alipay/end-to-end-402/sandbox-preflight.mjs`、`sandbox-preflight.test.mjs` |
| ACT-OSR-027 | 复核 2026-07-28 20:57:32 版支付宝 AI 按量付费指南并同步 Product Source Registry | Phase 2 | DEC-004、011 | Done | `integrations/profiles/alipay-ai-pay/sources/audits/2026-07-31-product-update.md` |
| ACT-OSR-028 | 建立 July Preview 发布说明、Changelog 和机器可读发布门禁 | Phase 7 | ACT-OSR-007、021、026 | Historical snapshot; superseded by target gates | `releases/2026-07-31-july-preview.md`、`governance/release-readiness.json` |
| ACT-OSR-029 | 对齐 2026-08-03 完成版支付服务域并收敛过期 Pending | Phase 3 | REV-018 | Done | `specs/2.1/`、`decisions/source-resolution-2026-08-03.md`、`scripts/check_repository.py` |
| ACT-OSR-030 | 复核 2026-07-31 11:54:36 版支付宝指南并确认买方/卖方安装包边界 | Phase 2 | DEC-004、011 | Done | `integrations/profiles/alipay-ai-pay/sources/audits/2026-08-03-product-update.md` |
| ACT-OSR-031 | 接受 A402 Candidate 机器契约选择并登记正式治理边界 | Phase 3 | ACT-OSR-021、029 | Done for Candidate | `decisions/candidate-machine-contract-resolution-2026-08-03.md` |
| ACT-OSR-032 | 实现三类 Header Schema、fixtures、validator、错误词典和漂移检查 | Phase 6 | ACT-OSR-031 | Done for Candidate | `specs/2.1/a402/schemas/`、`specs/2.1/a402/fixtures/`、`scripts/validate_a402_contract.py` |
| ACT-OSR-033 | 拆分 ACT Candidate、Profile Preview、Sandbox Verified 和 SEP Candidate 发布门禁 | Phase 7 | ACT-OSR-028、032 | Done | `governance/release-readiness.json`、`scripts/release_readiness.py` |
| ACT-OSR-034 | 收敛审计、路线图、Profile、Binding、Quickstart 和 Demo 状态文档 | Phase 7 | ACT-OSR-033 | Done | 2026-08-03 状态审计与仓库检查 |
| ACT-OSR-035 | 将 Alipay 产品错误映射与 Profile review 状态机器可读化并校验 Core 引用 | Phase 6 | ACT-OSR-032、034 | Done for Preview | `integrations/profiles/alipay-ai-pay/profile-review-status.json`、`integrations/profiles/alipay-ai-pay/schemas/error-mapping.preview.json` |
| ACT-OSR-036 | 对齐语雀《商业交互域》，登记来源指纹并补齐 CID 四组件公开候选 | Phase 3 | REV-020 | Done for Candidate | `specs/2.1/domains/commerce-interaction.md`、`specs/2.1/revision-status.md` |
| ACT-OSR-037 | 建立版权主体、双许可证与入站贡献政策记录 | Phase 7 | 项目负责人、开源办公室 | Done for publication；无额外签署前置 | `governance/decisions/legal-and-contribution-policy.md` |
| ACT-OSR-042 | 复核 2026-08-07 版支付宝指南并增加产品来源漂移检查 | Phase 2 | DEC-004、011 | Done | `integrations/profiles/alipay-ai-pay/sources/audits/2026-08-08-product-update.md`、`scripts/check_product_source_drift.py` |
| ACT-OSR-043 | 建立可复验的公开发布快照并移除公开内容对内部材料的依赖 | Phase 7 | ACT-OSR-037 | Done for tooling；release commit pending | `scripts/create_public_snapshot.py`、`governance/decisions/legal-and-contribution-policy.md` |
| ACT-OSR-038 | 按维护者黄色标识重分 CID 基线与修订增量，并保护三条安全语义 | Phase 3 | REV-021 | Done for Candidate | `specs/2.1/domains/commerce-interaction.md`、`scripts/check_repository.py` |
| ACT-OSR-039 | 对齐语雀《委托授权域》并补齐 ADD 三组件公开候选 | Phase 3 | REV-022 | Done for Candidate | `specs/2.1/domains/authorization-delegation.md`、`specs/2.1/revision-status.md` |
| ACT-OSR-040 | 对齐《典型场景与业务流程》并建立四域场景导航 | Phase 3 | REV-023 | Done for Candidate | `specs/2.1/scenarios.md` |
| ACT-OSR-041 | 对齐 TSD 可信存证与新增信用关联子篇 | Phase 3 | REV-024、025 | Done for semantic Candidate; machine contracts pending | `specs/2.1/domains/trust-services.md`、`specs/2.1/revision-status.md` |
| ACT-OSR-044 | 将协议事实源切换为 `act-protocol.com` 并建立官网内容漂移检查 | Phase 3 | REV-026、DEC-028 | Done for source routing; official semantic refresh pending | `governance/protocol-sources.json`、`scripts/check_protocol_source_drift.py` |
| ACT-OSR-045 | 配置 AntSRC 私密安全报告入口并移除额外贡献签署门禁 | Phase 7 | DEC-029 | Done | `SECURITY.md`、`CONTRIBUTING.md`、`governance/publication-config.json`、`governance/release-readiness.json` |

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
| DEC-013 | Agent 支付和 AI 按量付费是同一机器支付闭环的买方与卖方能力，不作为孤立产品流程设计 | 2026-07-18 | 文档架构、四域映射和端到端验收以双侧互通为主线 |
| DEC-014 | 开源框架跟踪 v2.1“场景组件与支付接入协议解耦”的方向，并使用候选 `PSD-PAY-A402` 表达 402 接入层 | 2026-07-22 | 正式合规仍等待公开规范，产品事实仍以 AIPay 官网为准 |
| DEC-015 | 大会可验证基线为 L1 `PSD-PAY-INS` + 候选 `PSD-PAY-A402` + Alipay AI Pay Profile + 官方 Skill/CLI + HTTP 402 + 支付宝沙箱 | 2026-07-22 | DEL/AUP 可展示结构，但没有公开产品证据前不声明兼容 |
| DEC-016 | 顶层 `integrations/bindings/` 只保存跨产品协议承载；支付宝专属 Skill/CLI Binding 归入 Alipay Profile | 2026-07-22 | 避免将产品工作流误表述为 ACT 通用 Binding |
| DEC-017 | 大会 Demo 复用三个 Quickstart 与支付宝沙箱，支持真实沙箱和明确标识的脱敏回放，不实现假支付逻辑 | 2026-07-22 | Demo 负责可讲解性，Quickstart 负责可复制性，证据负责可信度 |
| DEC-018 | 开源包只发布 ACT 2.1 Candidate，不再包含旧版规范、Schema、示例或迁移草案 | 2026-07-30 | 当前工作树依赖统一指向 2.1；最终 Git 历史处理由 DEC-024 延后决定 |
| DEC-019 | PSD 2.1 Candidate 使用《支付服务域》作为继承基线、v2.1 修订方案作为增量覆盖；删除公开 2.0 不得删除有效 PSD 语义 | 2026-07-30 | 历史纠偏决定；语义模型已被 DEC-021 取代 |
| DEC-020 | 当前开源交付采用 PSD-first，首期实现路径聚焦 L1 `PSD-PMT-BND + PSD-PAY-INS + PSD-PAY-A402` | 2026-07-30 | PSD 仍是一键接入主轴；四域语义范围后由 DEC-023、026、027 扩展同步 |
| DEC-021 | 2026-08-03 完成版《支付服务域》取代“继承基线 + 增量修订”的语义模型；Header 编码/两层结构、可选 Validation 和无完整购物车要求按来源直接同步 | 2026-08-03 | 关闭 PD-2.1-001/002/008，产品差异继续由 Profile 处理 |
| DEC-022 | 以 `Candidate Accepted` 关闭 A402 开源机器契约工程选择：JSON Schema 权威、稳定 `method_id`、请求指纹、幂等防重、六态投影、结构化错误、四类证据事实、L1 发布基线和 Workflow manifest | 2026-08-03 | 允许生成 Candidate Schema/fixtures/validator；正式 DWG 治理和 Stable 声明仍未完成 |
| DEC-023 | ACT 2.1 官网尚未更新期间，CID 与 PSD 暂以观岳维护的对应语雀域正文为协议事实源；支付宝产品事实仍以 AIPay 官网为准 | 2026-08-06 | 协议层与产品层分别追溯；官网更新后需先做差异评审，不能静默切源 |
| DEC-024 | Git 历史清理留到协议、Profile 和发布内容完全确定后执行 | 2026-08-06 | 当前阶段不重写历史；发布冻结时再评估敏感内容和旧 2.0 历史处理 |
| DEC-025 | 《商业交互域》中只有黄色高亮的“安全考虑”是本轮修改；其他正文属于既有 CID 基线 | 2026-08-06 | 状态文档必须区分“仓库补齐基线”和“协议修订增量”，不得把整篇同步记成新增协议决策 |
| DEC-026 | ACT 2.1 官网未更新期间，ADD、CID、PSD 与 TSD 分别以观岳维护的对应语雀域正文为事实源；《典型场景》只解释跨域组合 | 2026-08-06 | 域正文优先于场景清单和修订分析；支付宝产品事实仍只以 AIPay 官网为准 |
| DEC-027 | TSD 当前由可信存证与信用关联两个并列子篇构成；仓库只同步语义 Candidate，不实现未公开的 ACT Trust Chain、信用模型或报文 Schema | 2026-08-06 | 避免将产品日志、链服务或信用结果误称为 TSD 实现 |
| DEC-028 | `act-protocol.com` 是 ACT 协议公开事实源；语雀仅保留为 Candidate 演进证据，不作为外部开发者前置；官网变化必须先做人工语义差异评审 | 2026-08-10 | 取代 DEC-023、DEC-026 的临时来源安排；当前官网未发布的 Candidate 差异保持 Pending Publication Sync |
| DEC-029 | 私密安全漏洞统一通过 `https://security.alipay.com/`（AntSRC）报告；当前不启用额外贡献协议或 DCO sign-off 前置 | 2026-08-11 | 安全报告门禁通过；移除签署入口、PR 校验和外部贡献合并阻塞 |

## 4. 待决定问题

| ID | 问题 | 需要的输入 | 阻塞内容 | 状态 |
|---|---|---|---|---|
| OQ-001 | ACT Core 的最小对象集合是什么 | 四域语义 Candidate 已同步；只有 A402 具备机器契约 | 全域 Core | Semantic Candidate closed / broader machine contract pending |
| OQ-002 | Product Profile 是协议扩展还是独立合规层 | 已采用独立映射与声明层 | 目录、版本、测试 | Candidate closed |
| OQ-003 | Transport 与 Product Profile 如何组合声明版本 | `release-manifest.json` 已固定依赖组合 | 兼容性矩阵 | Candidate closed |
| OQ-004 | Agent Discovery/Profile 的最小公开字段是什么 | CID 支付能力声明与信用关联依赖身份解析，但来源未冻结通用 Agent Profile | Agent 能力协商、TSD 身份解析 | Pending broader machine contract |
| OQ-005 | `Payment-Validation` 的字段分布、必填项和产品映射如何版本化 | Candidate Schema 已固定字段；支付宝产品仍无同名 Header | Profile、正式治理 | Candidate closed / Product review |
| OQ-006 | 履约回执属于 Core 还是商业扩展 | Candidate 已区分验凭、交付、履约确认和证据 | Metered Profile | Candidate closed / Product mapping review |
| OQ-007 | `valid_next_actions` 是通用信封字段还是错误字段 | Candidate 已固定在错误对象 | Agent 自动恢复 | Candidate closed |
| OQ-008 | 首个 Quickstart 选择哪个支持官方 Skill/CLI 的 Agent 运行时 | 已选择官方 `@alipay/agent-payment` Skill/CLI 路径 | Quickstart 验证入口 | Closed |
| OQ-009 | 支付宝产品字段歧义如何获得公开确认 | 官网为事实源；未公开部分保持 `PRODUCT-REVIEW` | Alipay Profile | Product review; non-blocking for Preview |
| OQ-010 | `PSD-PAY-A402` 的版本、字段必填性、状态触发与向后兼容规则是什么 | Candidate Schema 和决议已固定；正式治理仍需 ratify | Stable Core | Candidate closed |
| OQ-011 | `Payment-Needed` 是否还需引用独立 CID 交易确认对象 | Candidate 允许可选引用，不要求完整购物车 | 正式 CID 对象 | Candidate closed |
| OQ-012 | 产品履约确认 API 与 PSD 回执、TSD 事件如何映射 | Candidate 边界已确定；具体产品调用仍需验证 | Profile 生命周期和存证 | Candidate closed / Product review |
| OQ-013 | ACT 可选 `Payment-Validation` Header 如何映射支付宝服务端验款结果 | 产品复核；官网未定义同名 Header | 402 响应和一致性测试 | Product review |
| OQ-014 | `intent_id`、委托、资源、订单和交易号的最小关联规则 | ADD、场景与 TSD 已明确语义关联；统一 wire 字段和事件 Schema 未冻结 | 端到端追踪与争议处理 | Semantic Candidate closed / wire contract pending |
| OQ-015 | Binding 能否封装多个 Core 消息和资源重试 | Candidate 允许，但强制 coverage/evidence/redaction manifest | 官方 Skill/CLI 的准确 ACT 覆盖声明 | Candidate closed |
| OQ-016 | 买方与卖方履约调用的关系和幂等责任是什么 | 支付宝产品复核 | 端到端履约实现和测试 | Product review; blocks Sandbox Verified only |
| OQ-017 | DEL/AUP 依赖的身份、连接、授权和密钥安全能力如何公开 | L2/L3 不属于当前可执行发布基线 | L2/L3 开发者路径和合规验证 | Validation-pending / deferred |
| OQ-018 | ACT 当前版权主体和入站贡献政策是什么 | `Copyright (c) 2026 Ant Group Co., Ltd.`；文档 CC BY 4.0；代码/Schema Apache 2.0；当前不要求额外贡献协议或 DCO sign-off，贡献者确认有权提交并按对应许可证贡献 | 外部贡献 | Resolved |
| OQ-019 | CID 双向协商和确认对象的正式 wire 契约是什么 | 观岳确认字段差异、Schema、版本、签名和安全规则 | CID-PCA-NEG、CID-CART-CFM、Profile | Pending CID decision; does not block semantic Candidate sync |
| OQ-020 | ADD ISR/IAC 的正式 wire 契约是什么 | 观岳确认 Schema、版本、封装、算法套件和状态查询协议 | ADD、DEL/AUP、TSD | Pending ADD decision; does not block semantic Candidate sync |
| OQ-021 | 可信存证如何形成可公开实现的机器契约 | 观岳确认事件 Schema、JWS 字段、ACT Trust Chain 接口/网络/认证和隐私通道 | TSD-ATT、跨域证据、实现 | Pending TSD decision; no implementation claim |
| OQ-022 | 信用关联如何形成可公开实现的机器契约 | 观岳确认凭证/声明/授权/验证 Schema、算法、身份/状态解析和规则注册 | TSD-CRD、风险引用 | Pending TSD decision; no implementation claim |

支付宝产品侧的详细问题见[公开接入基线](../integrations/profiles/alipay-ai-pay/sources/integration-baseline.md#6-待支付宝产品复核的问题)。

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
| 2026-07-18 | 按 ACT 官网四域框架重构产品映射并记录跨域协议问题 | ACT-OSR-003C、REV-014—016 |
| 2026-07-18 | 明确 Agent 支付与 AI 按量付费为同一机器支付闭环的双侧能力 | DEC-013 |
| 2026-07-21 | 建立双侧能力、关联标识、恢复规则和分级验收接入契约 | ACT-OSR-010B |
| 2026-07-21 | 完成官网产品事实复核并记录金额、编码、API 与沙箱差异 | ACT-OSR-010C、AP-001—003 |
| 2026-07-21 | 核对官方 Skill/CLI 工作流并识别 Binding 封装和双侧履约问题 | ACT-OSR-010D、REV-017、OQ-015—016 |
| 2026-07-21 | 建立端到端证据模板和观岳协议决策简报 | ACT-OSR-010E—010F |
| 2026-07-22 | 按 v2.1 修订方向拆分 PSD 场景组件与候选 A402 接入协议，并同步开源框架、Profile 与接入指南 | ACT-OSR-010G、DEC-014、REV-014 |
| 2026-07-22 | 落成项目框架、官方 Skill/CLI 买方入口、Java SDK 卖方 402 服务和端到端检查器 | ACT-OSR-013—016 |
| 2026-07-22 | 建立大会支付服务域执行计划、沙箱 Demo 骨架，并将产品专属 Skill/CLI Binding 迁入 Alipay Profile | ACT-OSR-017—019、DEC-015—017 |
| 2026-07-22 | 对齐官网卖方接入 Skill 与沙箱入口；仓库仅保留 ACT/Profile 验收和证据要求 | ACT-OSR-020、AP-001—003、009 |
| 2026-07-25 | 落成大会三栏 Web 演示台，支持真实 SSE 事件流与脱敏 Replay，并禁止 UI 自行生成支付成功 | ACT-OSR-018、DEC-017 |
| 2026-07-27 | 落成 Buyer Runtime 结构化事件适配、完整 Live 证据导出与经人工复核的 Replay 准备工具 | ACT-OSR-018、020 |
| 2026-07-28 | 建立 `specs/2.1/` 最小公开候选结构，并记录协议源基线、迁移边界与 Pending Decision | ACT-OSR-011、REV-014—017 |
| 2026-07-28 | 将 A402 最小机器契约重组为九项可表决门槛，建立机器 Register、ADR 模板和自动覆盖检查 | ACT-OSR-021、PD-2.1-001—012 |
| 2026-07-28 | 建立 A402 决策 Issue、评审批次、Accept/Defer 门槛、利益冲突记录和会后 ADR 流程 | ACT-OSR-022 |
| 2026-07-30 | 纠正 PSD 修订基线：登记《支付服务域》继承源，恢复六组件及 A402 字段、状态和错误语义 | ACT-OSR-024、REV-018、DEC-019 |
| 2026-07-30 | 将开源主轴收敛为 PSD-first 与 L1 + A402 一键接入 | ACT-OSR-025、REV-019、DEC-020 |
| 2026-07-30 | 修正 A402 决策包的基线与 Pending 映射，并增加真实沙箱本地前置条件检查 | ACT-OSR-020、021、026 |
| 2026-07-31 | 同步支付宝接入指南最新页面时间与公开事实；未发现需修改 Quickstart 产品逻辑的新事实 | ACT-OSR-027 |
| 2026-07-31 | 建立 July Preview 候选发布说明、Changelog 和显式阻塞的机器发布门禁 | ACT-OSR-028 |
| 2026-08-03 | 对齐完成版《支付服务域》，同步 A402 Header/场景流程并关闭过期 Pending | ACT-OSR-029、REV-018、DEC-021 |
| 2026-08-03 | 复核支付宝官网最新公开页面；更新时间变化，产品流程与买方/卖方包边界无须修改运行逻辑 | ACT-OSR-030 |
| 2026-08-03 | 完成 A402 Candidate 机器契约、8/8 A402 断言追踪和幂等防重复履约测试 | ACT-OSR-031、032 |
| 2026-08-03 | 将发布门禁拆为 ACT Candidate、Profile Preview、Sandbox Verified 和 SEP Candidate，并建立当前发布说明 | ACT-OSR-033、034 |
| 2026-08-03 | 建立 Profile 决策状态和产品错误映射的机器校验，产品待复核项按主张范围阻塞 | ACT-OSR-035 |
| 2026-08-06 | 以语雀《商业交互域》为当前 2.1 事实源，补齐 CID 四组件候选并记录来源字段冲突 | REV-020、ACT-OSR-036、DEC-023、OQ-019 |
| 2026-08-06 | 建立版权主体与贡献政策确认模板，并将 Git 历史清理延期到内容冻结后 | ACT-OSR-037、DEC-024、OQ-018 |
| 2026-08-06 | 按维护者说明确认 CID 黄色修改仅为能力声明安全三条，重分基线补齐与修订增量并增加回归检查 | REV-021、ACT-OSR-038、DEC-025 |
| 2026-08-06 | 对齐委托授权域、典型场景、可信存证和新增信用关联子篇，补齐四域语义 Candidate 并登记未冻结机器契约 | REV-022—025、ACT-OSR-039—041、DEC-026—027、OQ-020—022 |
| 2026-08-08 | 复核支付宝官网 `2026-08-07 21:51:27` 版指南；确认时间戳变化但接入语义未变，并建立每日漂移检查 | ACT-OSR-042 |
| 2026-08-08 | 建立可复验公开快照，移除公开门禁对内部材料的依赖，补齐英文入口、Showcase Manifest 和临时维护分工 | ACT-OSR-043 |
| 2026-08-10 | 将 ACT 协议公开事实源切换为 `act-protocol.com`，语雀降级为历史证据，并建立官网页面漂移检查 | REV-026、ACT-OSR-044、DEC-028 |
| 2026-08-11 | 配置 AntSRC 私密安全报告入口，关闭安全渠道阻塞，并移除额外贡献签署门禁 | ACT-OSR-045、DEC-029、OQ-018 |
