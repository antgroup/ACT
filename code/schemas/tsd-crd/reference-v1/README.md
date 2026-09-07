# Reference Profile v1

> **状态：Implementation Artifact / Non-normative**

本目录为 ACT 2.1 信任服务域的 TSD-CRD（信用关联）子篇提供首版机器可读参考格式。ACT 2.1 的规范性要求仍以[信任服务域正文](../../../../docs/specification/trust-services.md)为准；本 Profile 不会把正文未规定的字段名、算法或 HTTP 路径变成 ACT 要求。

`reference-v1` 是实现 Profile 版本，不是 ACT 协议版本。只有明确采用本目录字段、签名投影、Ed25519 算法套件和 HTTP 绑定的实现，才能声明支持该 Profile。

## 编码

- 报文使用 UTF-8 JSON。
- 时间使用 UTC RFC 3339。
- 签名算法使用 Ed25519。
- 公钥使用 PEM SPKI，`format` 为 `pem-spki`。
- 签名值使用无填充 Base64URL。

## 确定性 JSON

签名前先执行[参考实现](../../../samples/tsd-crd-reference/src/core/canonical.ts)中的确定性序列化：

1. 对象键按 JavaScript UTF-16 码元顺序升序排列。
2. 不输出空白。
3. 数组保持原顺序。
4. 字符串和有限数字使用 ECMAScript `JSON.stringify` 表达。
5. 拒绝负零、非有限数字、稀疏数组、循环引用、非普通对象、未配对代理项和非 JSON 类型。

这是 RFC 8785 兼容的受限 JSON 子集，不把未覆盖的输入类型纳入互操作范围。

## 签名投影

| 证明 | 签名前删除的字段 |
| --- | --- |
| DIRECT 主体内层签名 | `subjectPublicKey`、主体签名字段、签发方签名字段、`previousCredentialRef` |
| 凭证签发方外层签名 | 签发方签名字段、`statusQuery`、`previousCredentialRef` |
| 查询授权证明 | `authorizationProof`、运行时 `status` |
| 验证请求证明 | `requestProof` |
| 验证响应证明 | `responseProof` |
| 状态证明 | `statusProof` |

DIRECT 待签名包由 `/v1/association-applications/{applicationId}/preparations` 返回。除 `associationApplicationId` 外，签名包还必须携带 `associationApplicationRequestedAt` 和 `associationApplicationAntiReplay`，把原申请时间及 nonce/幂等键直接纳入主体内层签名。服务端冻结草稿后不得静默改写再复用主体签名。

## 签名层数

- `ATTESTED_CONFIRMATION`：只有签发方外层签名。
- `DIRECT_SIGNATURE`：主体内层签名和签发方外层签名。

Agent 公钥登记和 Agent 持钥证明不属于本 Profile。

## 信任解析

Schema 中的 `keyId` 只是标识。Reference Suite 必须从可信目录解析公钥并校验身份—公钥绑定；未配置解析器、无法解析或验签失败时失败关闭。Demo 使用的进程内测试目录不能作为生产信任依据。

## 目录

- `schemas/`：JSON Schema 2020-12。
- `openapi/`：OpenAPI 3.1 HTTP 绑定。
- `examples/`：结构示例，签名占位值不用于真实验签。
- `test-vectors/`：固定正常/异常向量；其中已签名载荷和历史 `urn:acp:*` 示例值作为不可透明改写的兼容性测试数据保留，不代表 ACT 的命名空间要求。

本目录由独立 TSD-CRD 仓库提交 `fdf7006d97ae06645dce82400fac2dff964691f2` 迁入。迁入时保留 `camelCase` wire 字段与签名向量，避免静默破坏互操作性；如需更改这些内容，应发布新的 Profile 主版本。
