# A402 Candidate 机器契约

> 状态：Candidate Working Draft / Non-normative  
> Schema：JSON Schema Draft 2020-12  
> 协议版本：`2.1-candidate.1`

本目录是 ACT 2.1 HTTP-first A402 Candidate 的唯一机器契约源。它约束 **Base64URL 解码后的 UTF-8 JSON**；HTTP Header 名称和编码由 [HTTP A402 Binding](../../../../bindings/http-a402/README.md)定义，支付宝产品差异由 Alipay Profile 映射。

权威入口：

- `payment-needed.schema.json`
- `payment-proof.schema.json`
- `payment-validation.schema.json`
- `error.schema.json`
- `transaction-state.schema.json`
- `workflow-binding-manifest.schema.json`

`common.schema.json` 只承载共享 `$defs`。`error-catalog.json` 是十一类来源错误语义到机器代码、阶段、重试性和合法下一动作的 Candidate 词典。

运行：

```bash
python3 scripts/validate_a402_contract.py
```

校验器会检查 Schema 自身、有效/无效 fixtures、三类 Header 的 Base64URL 无填充往返、跨消息关联、状态转移、错误目录和 Workflow Binding manifest。任何 Schema、fixture、错误目录或清单单边修改都会使仓库验证失败。

Schema 与文字冲突时，Candidate 实现以本目录的机器约束为准并登记差异；正式治理可用新版本替代，但不得静默改写为 Stable。
