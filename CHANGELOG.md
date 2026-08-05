# Changelog

本项目的公开版本变化记录在此。协议成熟度、规范性和生产认证状态以 [`release-manifest.json`](release-manifest.json) 为准。

## Unreleased — ACT 2.1 PSD Candidate

> Candidate Working Draft / Non-normative。当前尚未发布 Tag，不得声明 ACT 2.1 Stable、Recommendation、正式 Conformance 或 Production Certified。

### Added

- 建立 `specs/2.1/` 支付服务域公开候选，显式包含 `PSD-PMT-BND`、`PSD-AGT-SUB`、INS/L1、DEL/L2、AUP/L3 和独立 `PSD-PAY-A402`。
- 建立 HTTP A402 Binding Preview、Alipay AI Pay Profile Preview、买方/卖方 Quickstart 和端到端本地 Golden Path。
- 建立候选断言、A402 决策 Register、评审工作流、沙箱证据模板和 Showcase 证据校验工具。
- 建立 A402 Candidate JSON Schema、有效/无效 fixtures、校验器、11 类错误目录、六态投影和 Workflow Binding manifest。
- 建立 Alipay AI Pay Profile `0.9-preview.1` 的 Payment-Needed、Payment-Proof、验款结果和产品错误映射机器契约。
- 建立机器可读发布清单和 ACT Candidate、Profile Preview、Sandbox Verified、SEP Candidate 四级发布门禁。

### Changed

- 支付服务域切换为 2026-08-03 完成版《支付服务域》单一协议事实源；v2.1 修订分析保留为演进追溯。
- 同步三类 A402 Header 的 Base64URL UTF-8 JSON 编码、`protocol` + `method` 两层结构、可选 `Payment-Validation`，并按完成版协议校正 INS/DEL/AUP 步骤。
- 关闭旧 PD-2.1-001、PD-2.1-002、PD-2.1-008，并以 Candidate 决策固定字段分布、稳定 `method_id`、请求指纹、精确重试/幂等和错误对象；正式治理仍待 ratification。
- 开源入口收敛为 PSD-first 与 L1 + A402 主路径。
- 支付宝专属 Skill/CLI 工作流归入 Product Profile，顶层 Binding 只表达跨产品承载。
- 支付宝产品事实同步至 2026-08-03 核对结果；产品指南页面更新时间为 `2026-07-31 11:54:36`，买方/卖方安装包职责与 402 产品逻辑未变化。
- 官方支付宝沙箱改为外部产品事实与可选验证目标；仓库不复制沙箱，真实证据只阻塞 Sandbox Verified 主张。
- A402 8/8 Candidate 断言已链接检查或测试；产品待复核项按受影响主张记录，不再整体阻塞 Profile Preview。

### Removed

- 从公开候选包移除 ACT 2.0 规范、旧 Schema、旧示例和旧 Python Mock Demo。
- 移除虚构或空的 Reference Implementation / Conformance 入口；相关能力在真实产物建立后再发布。

### Known limitations

- A402 Candidate 机器契约已完成，但仍为 Non-normative，尚无正式 SEP ratification 或独立跨实现 TCK。
- Alipay AI Pay Profile、Quickstart 和 Binding 均为 Preview。
- 尚无真实支付宝沙箱闭环和脱敏发布证据，因此不得声明 Sandbox Verified。
- 版权主体、许可证分配、贡献者机制、私密安全披露渠道和公开发布远端仍待维护者确认。
- 当前工作树尚未形成干净、经评审并通过公开 CI 的发布提交。

详细发布状态见 [`docs/project/releases/2026-08-03-candidate-publication.md`](docs/project/releases/2026-08-03-candidate-publication.md)。
