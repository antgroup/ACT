# Alipay AI Pay Profile

> 状态：Profile Preview / Non-normative；Profile 版本：`0.9-preview.1`；产品资料核对：2026-08-03；ACT 兼容版本：ACT Core `2.1-candidate.1`

本目录记录支付宝 AI 付公开产品如何映射 ACT 工作语义。它是公开 Preview 阶段的产品 Profile 工作区，不是已经发布的规范性 Product Profile。

支付宝产品不是 ACT 的第五个域。Agent 支付赋予买方 Agent 支付能力，AI 按量付费赋予卖方服务接受机器支付的能力；二者是同一机器支付闭环的两侧，通过 Product Profile 组合 ADD、CID、PSD、TSD。先阅读[双侧能力与 ACT 四域映射](mappings/domains.md)。

ACT v2.1 完成版支付服务域将支付场景与接入协议解耦：首期按 L1 `PSD-PAY-INS` + 候选 `PSD-PAY-A402` + 官方 Skill/CLI Binding + Alipay AI Pay Profile 组织。仓库公开规范仍为 Candidate / Non-normative，因此这里只表达候选映射，不构成正式 Conformance 声明。

## 目录

| 区域 | 内容 | 推荐入口 |
|---|---|---|
| `capabilities/` | 买方、卖方及端到端最小能力契约 | [双侧能力接入契约](capabilities/end-to-end-contract.md) |
| `mappings/` | ACT 四域、产品字段、生命周期和错误映射 | [四域映射](mappings/domains.md) |
| `bindings/` | 支付宝产品特定的 Skill/CLI 工作流封装 | [Skill/CLI Binding](bindings/skill-cli/README.md) |
| `schemas/` | 当前产品报文、验款事实和错误映射的机器可读 Preview 契约，不是 ACT Core Schema | [Payment-Needed](schemas/payment-needed.preview.schema.json) · [Payment-Proof](schemas/payment-proof.preview.schema.json) · [Verification Result](schemas/payment-verification-result.preview.schema.json) · [Error Mapping](schemas/error-mapping.preview.json) |
| `sources/` | 官网资料、快照策略和事实审计 | [官方资料表](sources/README.md) |

产品待复核事项的机器状态和安全下限见 [`profile-review-status.json`](profile-review-status.json)。这些事项按影响分别阻塞 Sandbox Verified、生产声明或未来扩展，不再笼统阻塞 Profile Preview。

### 能力

- [Agent 支付能力](capabilities/agent-payment.md)
- [AI 按量付费能力](capabilities/metered-payment.md)
- [双侧能力接入契约](capabilities/end-to-end-contract.md)

### 映射

- [双侧能力与 ACT 四域](mappings/domains.md)
- [字段映射](mappings/fields.md)
- [生命周期映射](mappings/lifecycle.md)
- [错误映射](mappings/errors.md)

## 分层边界

| 层次 | 负责 | 不负责 |
|---|---|---|
| ACT Core | 跨产品语义、生命周期、验证责任和恢复语义 | 支付宝 API 名称、商户标识和 RSA2 细节 |
| Alipay AI Pay Profile | 产品字段、API、Skill/CLI、签名和产品错误映射 | 重定义 Core 语义 |
| Binding | HTTP Header 或 Skill/CLI 的封装和传输行为 | 产品开户规则 |
| 支付宝官方文档 | 开户、凭证、沙箱和当前产品操作 | ACT 协议定义 |

## 状态标签

| 标签 | 含义 |
|---|---|
| `PUBLIC-FACT` | 有公开支付宝资料直接支持 |
| `CANDIDATE-MAPPED` | 已映射到 ACT `2.1-candidate.1` 机器契约，仍为非规范性候选 |
| `PRODUCT-REVIEW` | 对公开资料的解释仍需产品复核 |
| `PROTOCOL-PENDING` | 依赖未进入当前 A402 Candidate 范围的后续 ACT 协议决策 |
| `VALIDATION-PENDING` | 仅相应 Sandbox Verified 或更高等级主张必须通过官方沙箱或 Skill/CLI 验证 |

实现可以声明“映射到 Alipay Profile Preview”，但不能据此声明已通过真实沙箱、ACT SEP Candidate 或生产 Conformance。真实互操作声明必须使用[双侧能力接入契约中的分级声明](capabilities/end-to-end-contract.md#9-分级验收声明)并附相应证据。
