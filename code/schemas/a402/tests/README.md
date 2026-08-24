# ACT 2.1 A402 测试断言目录

> 状态：Implementation Artifact / Non-normative

[`a402-assertions.json`](a402-assertions.json)编码两类稳定测试 ID：

- `A402-TEST-*`：A402 接入不变量；
- `PSD-TEST-*`：支付域六组件、支付工具、INS/L1、DEL/L2 和 AUP/L3 不变量。

这些 ID 供文档评审、测试命名和后续 Conformance 设计引用。

这些断言不是 2.1 消息 Schema。A402 的非规范性字段分布、状态触发、错误对象和幂等键由 [`code/schemas/a402/`](../README.md)提供机器源；断言目录只表达测试意图，不能成为正式一致性要求。

[`assertion-catalog.schema.json`](assertion-catalog.schema.json)只约束目录自身的机器可读格式，不定义 ACT 线上消息。

每条断言均标记为稳定的 `test-assertion`，包含前置条件、输入和预期输出；已有自动化覆盖时使用可选的 `executable_check` 建立追踪。[`a402-local-sample.feature`](a402-local-sample.feature)为已有本地测试提供可读场景，但不构成完整 Gherkin TCK。

目录只保存已定稿的测试断言。ACT 2.1 未标准化的消息形态、依赖路径或机器错误对象属于明确的规范边界，不在本目录追踪规范演进事项。

`test_level` 表示验证所需环境，不等同于 RFC 2119 的 MUST/SHOULD/MAY。规范约束强度只能由治理后的规范文本决定，不能由测试类型反推。
