# A402 非规范性机器产物

> 状态：Implementation Artifact / Non-normative
> Schema：JSON Schema Draft 2020-12  
> 产物版本：`2.1-artifact.1`；对应规范：ACT 2.1

本目录是 ACT 2.1 A402 的 HTTP-first 实现辅助产物。它约束 **Base64URL 解码后的 UTF-8 JSON**；对应接入说明见 [ACT 2.1 A402](../../../integrations/alipay/a402.md)，规范语义以[支付服务域](../../../docs/specification/payment-services.md)为准。产品接入可以映射这些语义，但不得反向改变规范。它不是 ACT 2.1 的规范性 Schema，也不构成 Conformance 契约。

权威入口：

- `payment-needed.schema.json`
- `payment-proof.schema.json`
- `payment-validation.schema.json`
- `error.schema.json`
- `transaction-state.schema.json`
- `workflow-binding-manifest.schema.json`

`common.schema.json` 只承载共享 `$defs`。`error-catalog.json` 是十一类规范错误语义到机器代码、阶段、重试性和合法下一动作的非规范性映射词典。

所有 `$id` 都使用同目录相对 URI，由 Schema 文件的实际获取位置作为解析基址；标准 JSON Schema 工具可直接加载本目录，不依赖外部 Schema 域名。`2.1-artifact.1` 是非规范性机器产物版本，不是另一个 ACT 协议版本。

关键跨字段约束同时进入 Schema：非幂等原请求必须带 `idempotency_key`；`Payment-Validation` 必须分别表达验证、交付和履约状态；`VALID` 不得携带 `error`，`INVALID` / `UNKNOWN` 必须携带 `error`。仓库校验器保留等价检查，用于提供更直接的错误信息和防止实现漂移。

运行：

```bash
python3 tools/a402/validate_contract.py
```

校验器会检查 Schema 自身、有效/无效 fixtures、三类 Header 的 Base64URL 无填充往返、跨消息关联、状态转移、错误目录和 Workflow Binding manifest。任何 Schema、fixture、错误目录或清单单边修改都会使仓库验证失败。

Schema 与 ACT 2.1 规范文字冲突时，以规范文字为准，并登记和修复机器产物差异。实现可以声明使用本产物版本，但不得把该声明表述为 ACT Conformance。
