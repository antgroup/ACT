# ACT 2.1 候选断言目录

> 状态：Candidate Working Draft / Non-normative

[`a402-core-assertions.json`](a402-core-assertions.json)保留历史文件名，但目录现在同时编码两类稳定 ID：

- `A402-CAND-*`：A402 接入不变量；
- `PSD-CAND-*`：支付域六组件、支付工具、INS/L1、DEL/L2 和 AUP/L3 的继承/修订不变量。

这些 ID 供文档评审、测试命名和后续 Conformance 设计引用。

这些断言不是 2.1 消息 Schema。A402 Candidate 的字段分布、状态触发、错误对象和幂等键现在由 [`schemas/a402/`](../schemas/a402/README.md)提供唯一机器源；断言目录只表达测试意图。带有 `pending_decision` 的非 A402 项仍不能成为正式一致性要求。

[`assertion-catalog.schema.json`](assertion-catalog.schema.json)只约束目录自身的机器可读格式，不定义 ACT 线上消息。

每条断言包含前置条件、输入、预期输出和可选的 `executable_check`。[`features/a402-local-preview.feature`](features/a402-local-preview.feature)为已有本地测试提供可读场景；当前验证脚本检查 Feature 标签、断言 ID 和 Node.js 测试之间的追踪关系，但不把它冒充为完整 Gherkin TCK。

`test_level` 表示验证所需环境，不等同于 RFC 2119 的 MUST/SHOULD/MAY。规范约束强度只能由治理后的规范文本决定，不能由测试类型反推。
