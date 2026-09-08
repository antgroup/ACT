# 快速开始

除非另有说明，以下命令均从 `act-protocol/` 仓库根目录执行。

## 环境

- Node.js `>= 22.18`
- npm

项目零第三方依赖，不需要执行 `npm install`，也不需要构建。

```bash
node --version
npm --prefix code/samples/tsd-crd-reference test
```

## 运行 Demo

```bash
npm --prefix code/samples/tsd-crd-reference run demo
```

默认 Demo 使用 `ATTESTED_CONFIRMATION`：

1. 创建包含虚构主体和 Agent 的信用关联申请。
2. Mock 确认服务完成主体身份核验和交互确认。
3. 固定映射规则生成带 `ASSOCIATED_CREDIT` 标记的关联信用。
4. 测试签发方对凭证做外层签名，凭证进入 `ACTIVE`。
5. 执行凭证级验证。
6. 演示缺少查询授权、完成授权和再次验证。
7. 撤销凭证并确认它不能再得到新的 `PASS`。

默认 Demo 不生成 Agent 私钥，不执行 nonce 挑战。可选 Agent 持钥扩展不属于 P0。

## 启动 Sandbox

```bash
npm --prefix code/samples/tsd-crd-reference run start
```

Sandbox 只监听本地开发接口，具体路径以 `reference-v1` [OpenAPI](../../code/schemas/tsd-crd/reference-v1/openapi/openapi.yaml) 为准。

创建一笔 ATTESTED 申请：

```bash
curl -sS http://127.0.0.1:8787/v1/association-applications \
  -H 'content-type: application/json' \
  --data-binary @code/samples/tsd-crd-reference/examples/association-application-sandbox.json
```

确认并签发凭证：

```bash
curl -sS http://127.0.0.1:8787/v1/association-applications/association-application-demo-001/confirmations \
  -H 'content-type: application/json' \
  -d '{"confirmationMethod":"ATTESTED_CONFIRMATION"}'
```

常用入口：

| 操作 | 方法和路径 |
| --- | --- |
| 创建信用关联申请 | `POST /v1/association-applications` |
| 提交主体确认 | `POST /v1/association-applications/{applicationId}/confirmations` |
| 查询凭证状态 | `GET /v1/association-credentials/{credentialId}/status` |
| 创建信用查询授权 | `POST /v1/credit-query-authorizations` |
| 执行验证 | `POST /v1/verifications` |

所有数据保存在内存中。停止进程后，申请、凭证、授权和验证记录可以丢失。

示例文件中的签名占位值只用于展示报文结构，不能提交给受保护接口。Sandbox 对验证请求、DIRECT 主体确认、授权创建/撤销和凭证状态变更采用失败关闭策略；调用方必须通过 `resolveRelyingPartyPublicKey` 或 `resolveSubjectPublicKey` 注入可信身份—公钥绑定，否则请求会以 `REQUEST_PROOF_INVALID` 被拒绝。Demo 会生成临时测试密钥、显式注册测试身份并执行真实 Ed25519 签名。响应证明、状态证明和凭证签名也使用运行时临时测试密钥真实生成。

## 运行一致性测试

```bash
npm --prefix code/samples/tsd-crd-reference run conformance
```

Runner 读取：

- [`reference-v1/test-vectors/valid/`](../../code/schemas/tsd-crd/reference-v1/test-vectors/valid/) 中的正常向量。
- [`reference-v1/test-vectors/invalid/`](../../code/schemas/tsd-crd/reference-v1/test-vectors/invalid/) 中的篡改、过期、撤销和越权向量。

Agent 密钥持有扩展不计入基础一致性结果。

## 运行全部测试

```bash
npm --prefix code/samples/tsd-crd-reference test
```

测试失败时先检查：

- Node.js 版本是否满足要求。
- 测试向量声明的 Profile 版本是否匹配。
- 本地时钟是否被测试固定时钟覆盖。
- 是否误把 Agent 密钥持有证明等非 P0 设计当作核心要求。

## 数据安全

只使用仓库自带的虚构数据和测试密钥。不要把真实身份、账号、信用数据、私钥或内部服务地址放入请求、日志或测试向量。
