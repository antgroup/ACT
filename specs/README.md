# ACT 规范

本目录保存当前公开协议候选。旧版规范不包含在本开源包中。

| 版本 | 状态 | 入口 |
|---|---|---|
| 2.1 | Candidate Working Draft / Non-normative；尚未进入 SEP Candidate，不得声明正式 Conformance | [候选概览](2.1/overview.md) · [A402 机器契约](2.1/schemas/a402/README.md) · [修订状态](2.1/revision-status.md) · [候选断言](2.1/assertions/README.md) |

`specs/2.1/` 是为公开评审建立的候选工作目录，包含 A402 Candidate Core JSON Schema、fixtures 和断言；`Candidate Working Draft` 是内容标签，不代表已经满足 SEP Candidate 的独立实现门槛。

支付服务域以 2026-08-03 完成修订的[《支付服务域》](https://yuque.antfin.com/hknzlf/fvle20/dve0b9g2u1t3cs33)为完整协议事实源；[v2.1 修订分析](https://yuque.antfin.com/hknzlf/fvle20/dh5iwcigwa65hkds)只用于演进追溯。公开包不包含 `specs/2.0`。来源没有决定的字段分布、`method_id`、幂等键和错误对象已形成可执行 Candidate 工程决议；它们不是来源事实或正式治理结论。

产品字段和接口映射位于 [`profiles/`](../profiles/README.md)，传输与运行时封装位于 [`bindings/`](../bindings/README.md)。
