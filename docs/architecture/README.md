# ACT 项目框架

> 状态：Preview / Non-normative

本页是开源项目的稳定结构入口。开发者按任务进入 Quickstart；协议贡献者按层定位变更；支付宝接入细节继续以公开官网为准。

## 1. 五层结构

| 层次 | 核心问题 | 仓库位置 | 当前状态 |
|---|---|---|---|
| ACT Domains | 跨产品的授权、商业交互、支付和信任语义是什么 | `specs/2.0/` | 2.0 工作版本，修订中 |
| Payment Scenarios | 用户是否在场，Agent 基于什么授权支付 | PSD INS / DEL / AUP | v2.1 修订方向 |
| Access Protocol | 支付要求、凭证、验证和状态如何交换 | 候选 A402；`bindings/http-a402/` | Preview |
| Binding | HTTP、Skill/CLI 等运行时如何承载或封装协议 | `bindings/` | 首期已有 HTTP A402 与 Skill/CLI |
| Product Profile | 具体产品字段、接口、签名、状态和错误如何映射 | `profiles/alipay-ai-pay/` | Preview / Non-normative |

支付宝 AI 付产品位于这些层之外的产品实现端：Agent 支付提供买方能力，AI 按量付费提供卖方机器收款能力。二者组合四个 ACT 域，不形成第五个域。

## 2. 首期可运行组合

```text
L1 PSD-PAY-INS 场景
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
| `profiles/` | 产品到 ACT 的字段/API/状态映射 | 产品操作手册或 ACT Core 重定义 |
| `bindings/` | Transport 与工作流封装规则 | 产品已经支持未公开的接入形式 |
| `quickstarts/` | 连接官方产品或 Sandbox 的最短代码路径 | 完整参考实现或生产就绪 |
| `conformance/` | Core/Profile/Binding 一致性测试 | 仅凭本地语法测试即可合规 |
| `reference-implementations/` | 声明覆盖版本且通过一致性测试的实现 | 未声明覆盖范围的“完整实现” |
| `demos/`、`impl/python/` | Mock 或体验性演示 | 真实支付和产品兼容性 |
| `examples/` | 报文和业务场景说明 | 已通过端到端产品验证 |

## 4. 依赖方向

协议场景引用支付接入协议；Binding 承载协议；Product Profile 映射具体产品；Quickstart 组合这些层但不重新定义它们。产品字段变化先更新公开事实审计和 Profile，协议语义变化通过治理进入规范，不能直接由 Quickstart 代码反向定义。

## 5. 开发者入口

- 买方 Agent：[Agent Payment Quickstart](../../quickstarts/alipay/agent-payment/README.md)
- 卖方服务：[Metered REST Provider Quickstart](../../quickstarts/alipay/metered-rest-provider/README.md)
- 双侧互通：[End-to-end 402 Quickstart](../../quickstarts/alipay/end-to-end-402/README.md)
- 协议与产品映射：[Alipay AI Pay 双侧能力与四域映射](../../profiles/alipay-ai-pay/domain-mapping.md)
- 修订状态：[ACT 修订与开源重构追踪](../open-source-restructure/05-revision-tracker.md)
