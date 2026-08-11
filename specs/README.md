# ACT 规范

本目录保存当前公开协议候选。旧版规范不包含在本开源包中。

| 版本 | 状态 | 入口 |
|---|---|---|
| 2.1 | Candidate Working Draft / Non-normative；尚未进入 SEP Candidate，不得声明正式 Conformance | [候选概览](2.1/overview.md) · [委托授权域](2.1/domains/authorization-delegation.md) · [商业交互域](2.1/domains/commerce-interaction.md) · [支付服务域](2.1/domains/payment-services.md) · [信任服务域](2.1/domains/trust-services.md) · [典型场景](2.1/scenarios.md) · [A402 机器契约](2.1/a402/schemas/README.md) · [修订状态](2.1/revision-status.md) |

`specs/2.1/` 是为公开评审建立的候选工作目录，包含 A402 Candidate Core JSON Schema、fixtures 和断言；`Candidate Working Draft` 是内容标签，不代表已经满足 SEP Candidate 的独立实现门槛。

[ACT Protocol 官网](https://www.act-protocol.com/)是公开协议事实源，固定入口包括[协议概览](https://www.act-protocol.com/documentation/overview)、[典型场景](https://www.act-protocol.com/documentation/scenarios)、[委托授权域](https://www.act-protocol.com/documentation/delegation)、[商业交互域](https://www.act-protocol.com/documentation/commerce)、[支付服务域](https://www.act-protocol.com/documentation/payment)和[信任服务域](https://www.act-protocol.com/documentation/trust)。`specs/2.1/` 是 Candidate 快照，不是官网镜像或正式发布；历史维护文档仅作为同步证据保留在[修订状态](2.1/revision-status.md)，外部开发者无需访问内部资料。公开包不包含 `specs/2.0`。官网尚未发布或存在冲突的 wire 细节保持 Pending，A402 已接受的工程选择仍不是正式治理结论。

产品字段和接口映射位于 [`integrations/profiles/`](../integrations/profiles/README.md)，传输与运行时封装位于 [`integrations/bindings/`](../integrations/bindings/README.md)。
