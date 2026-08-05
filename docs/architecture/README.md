# ACT 项目框架

> 状态：Current Repository Architecture / Non-normative；最后核对：2026-08-03

本页是当前仓库结构的唯一事实入口。当前开源主轴是支付服务域（PSD）：开发者按买方/卖方任务进入 Quickstart，协议贡献者按“PSD Core → A402 → Binding → Profile”定位变更；支付宝接入细节继续以公开官网为准。

## 1. 六层结构

| 层次 | 核心问题 | 仓库位置 | 当前状态 |
|---|---|---|---|
| PSD Core | 跨产品的支付工具、账户、场景、对象和安全语义是什么 | `specs/2.1/payment-services-domain-spec.md` | 六组件 Candidate Working Draft |
| Payment Foundations | Agent 使用什么受限支付工具，是否需要账户隔离 | PSD PMT-BND / AGT-SUB | 完成版协议；Candidate / Non-normative |
| Payment Scenarios | 用户是否在场，Agent 基于什么授权支付 | PSD INS / DEL / AUP | L1/L2/L3 Candidate |
| Access Protocol | 支付要求、凭证、验证和状态如何交换 | 候选 A402；`bindings/http-a402/` | Preview |
| Binding | HTTP 等运行时如何承载协议 | `bindings/` | 首期公共 Binding 为 HTTP A402 |
| Product Profile | 具体产品字段、接口、签名、状态和错误如何映射 | `profiles/alipay-ai-pay/` | Preview / Non-normative |

ADD、CID、TSD 当前只维护支付闭环需要的 IAC、交易确认/能力协商和证据边界，不作为首期 PSD 接入的完整发布前置。支付宝 AI 付位于协议层之外的产品实现端，不形成新的 ACT 域。

## 2. 首期可运行组合

```text
PSD-PMT-BND 支付工具准备
  + L1 PSD-PAY-INS 场景
  + candidate PSD-PAY-A402 access protocol
  + official Alipay Skill/CLI buyer Binding
  + HTTP A402 seller Binding
  + Alipay AI Pay Product Profile
  + official Alipay Sandbox / OpenAPI
```

其中，用户授权和支付由官方买方能力完成；卖方 Quickstart 生成 RSA2 账单、调用官方验凭证接口、执行一致性和防重校验、交付资源并确认履约。

## 3. 目录责任

| 目录 | 可以包含 | 不能据此声明 |
|---|---|---|
| `specs/` | 经过治理的规范和 Schema | 未发布候选已经稳定 |
| `profiles/` | 产品到 ACT 的字段/API/状态映射及产品专属工作流 Binding | 产品操作手册或 ACT Core 重定义 |
| `bindings/` | Transport 与工作流封装规则 | 产品已经支持未公开的接入形式 |
| `quickstarts/` | 连接官方产品或 Sandbox 的最短代码路径 | 完整参考实现或生产就绪 |
| `demos/` | Mock 或体验性演示 | 真实支付、参考实现和产品兼容性 |

## 4. 依赖方向

协议场景引用支付接入协议；Binding 承载协议；Product Profile 映射具体产品；Quickstart 组合这些层但不重新定义它们。产品字段变化先更新公开事实审计和 Profile，协议语义变化通过治理进入规范，不能直接由 Quickstart 代码反向定义。

## 5. 开发者入口

- 支付宝 AI 付产品总入口：[Alipay AI Pay Quickstart](../../quickstarts/alipay/README.md)
- 买方 Agent：[Agent Payment Quickstart](../../quickstarts/alipay/agent-payment/README.md)
- 卖方服务：[Metered REST Provider Quickstart](../../quickstarts/alipay/metered-rest-provider/README.md)
- 双侧互通：[End-to-end 402 Quickstart](../../quickstarts/alipay/end-to-end-402/README.md)
- 版本和组件依赖：[机器可读 Release Manifest](../../release-manifest.json)
- 协议与产品映射：[Alipay AI Pay 双侧能力与四域映射](../../profiles/alipay-ai-pay/mappings/domains.md)
- 修订状态：[ACT 修订状态](../project/revision-status.md)

## 6. 当前目录与后续迁移

| 主题 | 当前实际位置 | 后续目标 | 触发条件 |
|---|---|---|---|
| 2.1 PSD 公开候选 | `specs/2.1/` | 经治理后发布正式版本 | Candidate Schema 已完成；正式 DWG/SEP ratification |
| 支付宝产品映射 | `profiles/alipay-ai-pay/{capabilities,mappings,sources}/` | 形成版本化 Profile | ACT 2.1 候选语义和产品复核完成 |
| 大会演示 | `demos/alipay-ai-pay-sandbox-showcase/` | 保持 Guided Preview 与官方沙箱证据边界 | 随产品和 Profile 对齐维护 |
| 候选断言 | `specs/2.1/assertions/` | Core、Profile、Binding Conformance 测试集 | 补齐可执行覆盖并取得独立实现证据 |

`specs/2.1/` 当前是 Candidate Working Draft / Non-normative，已经包含 A402 Candidate 消息 Schema、fixtures 和 validator。它们不代表 SEP Candidate 或正式 Conformance；现有断言目录只给不变量分配稳定测试 ID。正式版本形成前，不创建 `specs/current` 或顶层 `schemas/`，也不通过移动目录暗示协议已经定稿。
