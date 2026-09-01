# TSD-CRD Reference Implementation Guide

本目录集中说明 ACT 2.1 TSD-CRD（信用关联）参考实现的实现基线、架构、运行方式、安全边界和可选扩展。

> **状态：Implementation guidance / Informative / Non-production。**
> TSD-CRD 是 ACT 2.1 的规范性协议内容；本目录只解释仓库中的 `reference-v1` Profile 和 Reference Implementation，不增加、替代或修改 ACT 2.1 的协议要求。

## 权威关系

| 层次 | 入口 | 定位 |
| --- | --- | --- |
| ACT 2.1 TSD-CRD 协议正文 | [信任服务域](../../docs/specification/trust-services.md) | 规范性协议要求 |
| `reference-v1` | [机器可读 Profile](../../code/schemas/tsd-crd/reference-v1/README.md) | 可选的机器表达和互操作 Profile |
| Reference Implementation | [可运行实现](../../code/samples/tsd-crd-reference/README.md) | 非生产参考实现、Sandbox、CLI 和测试 |

发生冲突时，以 ACT 2.1 信任服务域正文为准。采用 `reference-v1` 的实现还必须满足该 Profile 的字段、签名投影和固定向量约束。

## 文档导航

- [参考实现基线](implementation-baseline.md)：协议正文、机器 Profile 和参考实现之间的边界。
- [架构说明](architecture.md)：代码分层、组件映射、依赖方向和可替换能力。
- [快速开始](quickstart.md)：从仓库根目录运行测试、Demo、Sandbox 和基础一致性检查。
- [安全模型](security-model.md)：参考实现的信任边界、威胁控制和生产实现责任。
- [可选 Agent 密钥持有证明扩展](agent-key-possession-extension.md)：尚未纳入 P0 或基础一致性检查的扩展设计。

## 范围边界

这些文档和参考实现不提供真实身份核验、真实信用服务、生产密钥管理、持久化、高可用或完整 ACT 2.1 Conformance 证明。验证结果只能作为业务输入，不直接构成交易准入、授信、支付批准或风险判断。
