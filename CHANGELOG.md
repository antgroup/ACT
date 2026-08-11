# Changelog

本项目的公开版本变化记录在此。协议成熟度、规范性和生产认证状态以 [`release-manifest.json`](release-manifest.json) 为准。

## Unreleased — ACT 2.1 Candidate

> Candidate Working Draft / Non-normative。当前尚未发布 Tag，不得声明 ACT 2.1 Stable、Recommendation、正式 Conformance 或 Production Certified。

### Added

- 将 ACT 协议公开事实源切换为 `act-protocol.com`，内部语雀仅保留为历史同步证据，并增加官网页面内容漂移检查。
- 建立 `specs/2.1/` 支付服务域公开候选，显式包含 `PSD-PMT-BND`、`PSD-AGT-SUB`、INS/L1、DEL/L2、AUP/L3 和独立 `PSD-PAY-A402`。
- 建立商业交互域公开候选，覆盖 `CID-MER-CAT`、`CID-INT-XFR`、`CID-PCA-NEG`、`CID-CART-CFM` 和 CID→PSD 连接边界。
- 建立委托授权域公开候选，覆盖 `ADD-INT-ICS`、`ADD-IAC-ISS`、`ADD-IAC-LCM`、ISR/IAC 边界和生命周期。
- 建立信任服务域公开候选，区分可信存证和新增信用关联两个子篇，并覆盖十个 TSD 组件。
- 建立四域典型场景指南，区分用户在场、平台定向委托、专属 Agent 定向委托和自主化委托支付。
- 建立 HTTP A402 Binding Preview、Alipay AI Pay Profile Preview、买方/卖方 Quickstart 和端到端本地 Golden Path。
- 建立候选断言、A402 决策 Register、评审工作流、沙箱证据模板和 Showcase 证据校验工具。
- 建立 A402 Candidate JSON Schema、有效/无效 fixtures、校验器、11 类错误目录、六态投影和 Workflow Binding manifest。
- 建立 Alipay AI Pay Profile `0.9-preview.1` 的 Payment-Needed、Payment-Proof、验款结果和产品错误映射机器契约。
- 建立机器可读发布清单和 ACT Candidate、Profile Preview、Sandbox Verified、SEP Candidate 四级发布门禁。
- 建立版权主体、双许可证分配与入站贡献政策记录。
- 建立英文根入口、公开版权/贡献政策记录、临时维护分工和可配置的公开仓库/安全运营门禁。
- 建立可复验公开快照和支付宝产品文档每日漂移检查；公开快照排除内部筹备材料与 Git 忽略文件。

### Changed

- 参考 AP2 的文档/代码分层，将仓库收敛为 `specs/`、`docs/`、`integrations/`、`code/`、`governance/`、`scripts/` 六个主干；A402 的规范、Schema、fixtures 和断言聚合到 `specs/2.1/a402/`，每个可运行示例提供 README 与统一 `run.sh` 入口。
- 历史阶段曾以 2026-08-03 完成版维护稿同步支付服务域，并用 v2.1 修订分析追溯演进；当前公开事实源已经切换为 `act-protocol.com`。
- 历史阶段曾以维护稿补齐 CID 四组件，并只把黄色高亮的能力声明来源校验、关键字段一致性和失败关闭记作修订增量。
- 历史阶段曾以维护稿补齐 ADD、典型场景和 TSD Candidate；这些内部链接现在只保留在修订追踪中，不是外部开发者前置条件。
- 同步三类 A402 Header 的 Base64URL UTF-8 JSON 编码、`protocol` + `method` 两层结构、可选 `Payment-Validation`，并按完成版协议校正 INS/DEL/AUP 步骤。
- 关闭旧 PD-2.1-001、PD-2.1-002、PD-2.1-008，并以 Candidate 决策固定字段分布、稳定 `method_id`、请求指纹、精确重试/幂等和错误对象；正式治理仍待 ratification。
- 开源入口收敛为 PSD-first 与 L1 + A402 主路径。
- 支付宝专属 Skill/CLI 工作流归入 Product Profile，顶层 Binding 只表达跨产品承载。
- 支付宝产品事实同步至 2026-08-08 核对结果；产品指南页面更新时间为 `2026-08-07 21:51:27`，买方/卖方安装包职责与 402 产品逻辑未变化。
- 将 Sandbox Showcase 纳入 Release Manifest，明确 L1 可接真实证据，L2/L3 仅作 Candidate / Product-pending 引导演示。
- 官方支付宝沙箱改为外部产品事实与可选验证目标；仓库不复制沙箱，真实证据只阻塞 Sandbox Verified 主张。
- A402 8/8 Candidate 断言已链接检查或测试；产品待复核项按受影响主张记录，不再整体阻塞 Profile Preview。
- 版权主体确定为 `Ant Group Co., Ltd.`，文档/代码分别采用 CC BY 4.0 与 Apache 2.0；当前取消额外贡献协议和 DCO sign-off 前置，贡献者按对应文件许可证提交。
- 安全披露入口确定为蚂蚁集团安全应急响应中心 `https://security.alipay.com/`，安全报告门禁通过。

### Removed

- 从公开候选包移除 ACT 2.0 规范、旧 Schema、旧示例和旧 Python Mock Demo。
- 移除虚构或空的 Reference Implementation / Conformance 入口；相关能力在真实产物建立后再发布。

### Known limitations

- A402 Candidate 机器契约已完成，但仍为 Non-normative，尚无正式 SEP ratification 或独立跨实现 TCK。
- Alipay AI Pay Profile、Quickstart 和 Binding 均为 Preview。
- 尚无真实支付宝沙箱闭环和脱敏发布证据，因此不得声明 Sandbox Verified。
- 版权主体、许可证分配、入站贡献条款和私密安全披露渠道已经确定。公开发布仍待公开仓库目标和干净发布快照。
- CID 正式 JSON Schema、双向协商字段冲突、签名和版本规则仍待观岳/CID 治理确认。
- ADD 的 ISR/IAC wire Schema、TSD 的对象 Schema、ACT Trust Chain 公开接口和信用关联封装仍待协议治理确认。
- Git 历史清理按维护者决定留到内容完全确定后；当前尚未形成最终发布提交。

详细发布状态见 [`governance/releases/2026-08-03-candidate-publication.md`](governance/releases/2026-08-03-candidate-publication.md)。
