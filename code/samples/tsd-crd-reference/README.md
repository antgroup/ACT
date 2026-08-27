# TSD-CRD Reference Implementation

ACT 2.1 信用关联子篇（TSD-CRD）的可执行参考实现、本地 Sandbox 和基础一致性测试套件。

本项目帮助协议实现者完成三件事：

1. 在本地跑通信用关联、映射、生命周期、查询授权和验证流程。
2. 查看 Reference Profile、标准报文和状态变化。
3. 使用固定测试向量检查自己的实现是否符合 `reference-v1` Profile 的基础约束。

> **状态：Reference Implementation / Non-normative / Non-production。**
> 项目只使用虚构身份、虚构信用数据和临时测试密钥；测试通过不等于 ACT 2.1 全量 Conformance 或生产就绪。

## 协议基线

当前实现基于 ACT 2.1 [信任服务域中的信用关联子篇](../../../docs/specification/trust-services.md)，覆盖五个组件：

| 组件 | 作用 |
| --- | --- |
| `TSD-CRD-ASC` | 信用关联申请、确认和凭证签发 |
| `TSD-CRD-MAP` | 关联信用映射、来源标记和规则版本 |
| `TSD-CRD-LCM` | 凭证状态、暂停、恢复、撤销、过期和替换 |
| `TSD-CRD-AUTH` | 逐次授权和平台代理查询授权 |
| `TSD-CRD-VER` | 凭证级验证和关联信用信息验证 |

协议正文规定业务语义；[`code/schemas/tsd-crd/reference-v1`](../../schemas/tsd-crd/reference-v1/README.md) 补充一套非规范性机器可读格式；本目录提供其中一种可运行实现。三者冲突时，以 ACT 2.1 协议正文为准。

详细说明见[参考实现基线](../../../docs/reference-implementations/tsd-crd/implementation-baseline.md)和 [Reference Profile v1](../../schemas/tsd-crd/reference-v1/README.md)。本目录由独立 TSD-CRD 仓库提交 `fdf7006d97ae06645dce82400fac2dff964691f2` 迁入；迁入时保留 `reference-v1` 的 wire 字段和固定签名向量。

## 两种主体确认方式

| 模式 | 关联主体如何确认 | 凭证签名层数 |
| --- | --- | --- |
| `ATTESTED_CONFIRMATION` | 可信确认服务完成主体身份核验和交互确认 | 一层：签发方外层签名 |
| `DIRECT_SIGNATURE` | 关联主体使用可信主体私钥签署关联关键内容 | 两层：主体内层签名 + 签发方外层签名 |

这里的“一层”和“两层”只指信用关联凭证的签名结构，不包括 HTTPS、回调验签或其他传输层保护。

协议不要求 Agent 提交公钥、使用 Agent 私钥签署挑战值或完成 `AgentControlProof`。基于 nonce 的 Agent 密钥持有证明属于可选安全扩展，不在 P0 默认流程和基础一致性测试范围内。当前仓库只有[设计说明](../../../docs/reference-implementations/tsd-crd/agent-key-possession-extension.md)，尚未实现对应代码。它不能替代主体确认或签发方签名。

## P0 范围

P0 包含：

- 五个协议组件的对象、字段和不变量校验。
- `ATTESTED_CONFIRMATION` 和 `DIRECT_SIGNATURE` 两种主体确认方式。
- 关联信用映射三要素及 `ASSOCIATED_CREDIT` 来源标记。
- `PENDING`、`ACTIVE`、`SUSPENDED`、`REVOKED`、`EXPIRED` 生命周期。
- 逐次授权和平台代理查询授权。
- 凭证级验证、关联信用信息验证、标准结果和原因码。
- 最小披露、状态查询和验证记录。
- 本地 Sandbox、HTTP 示例、CLI 和固定测试向量。
- 基础一致性测试 Runner。

P0 不包含：

- Agent 密钥持有证明扩展。
- 真实身份核验、真实信用数据或真实映射模型。
- 支付宝受理台真实接入。
- Agent 独立信用或独立声誉。
- 授信、支付、交易准入、反欺诈或反洗钱决策。
- 生产数据库、KMS/HSM、多租户和高可用部署。

## 快速开始

要求：

- Node.js `>= 22.18`
- npm（随 Node.js 提供）

项目没有第三方运行时或开发依赖，不需要执行 `npm install` 或构建命令。

```bash
# 运行全部测试
npm test

# 运行基础一致性测试
npm run conformance

# 跑通本地端到端 Demo
npm run demo

# 启动本地 Sandbox 服务
npm run start
```

Demo 默认使用 `ATTESTED_CONFIRMATION`，通过 Mock 主体确认服务完成身份核验和确认。所有身份、信用值、签名密钥和授权记录都是测试数据。

Sandbox 对验证请求、DIRECT 主体确认、查询授权及生命周期变更采用失败关闭策略：必须注入可信公钥解析器并完成身份—公钥绑定和 Ed25519 验签；未配置解析器、无法解析密钥或证明无效时直接拒绝。Demo 使用进程内临时测试密钥和显式测试身份绑定，生产实现必须替换为可信密钥目录或等效信任来源。

更多运行说明见[快速开始](../../../docs/reference-implementations/tsd-crd/quickstart.md)。Sandbox 的接口以 `reference-v1` [OpenAPI](../../schemas/tsd-crd/reference-v1/openapi/openapi.yaml) 为准，创建申请使用 `POST /v1/association-applications`。

## 目录结构

```text
act-protocol/
├── docs/reference-implementations/tsd-crd/    # 实现指南、架构和安全边界
├── code/schemas/tsd-crd/reference-v1/
│   ├── schemas/                     # JSON Schema
│   ├── openapi/                     # HTTP API 描述
│   ├── examples/                    # 标准报文示例
│   └── test-vectors/                # 正常/异常固定向量
└── code/samples/tsd-crd-reference/
    ├── src/
    │   ├── core/                    # 协议对象、规则和状态机
    │   ├── application/             # 五个组件的用例编排
    │   ├── adapters/                # 内存和 Mock 适配器
    │   ├── http/                    # 本地 Sandbox HTTP 入口
    │   ├── cli/                     # CLI 和 Demo 入口
    │   └── conformance/             # 一致性测试 Runner
    ├── test/                        # 单元和集成测试
    └── examples/                    # 可运行示例
```

架构和依赖边界见 [架构说明](../../../docs/reference-implementations/tsd-crd/architecture.md)。

## 非生产边界

本仓库是协议参考实现，不是信用服务产品。

- 不要输入真实姓名、证件号、账号、手机号或信用数据。
- 不要把测试密钥用于任何真实系统。
- 不要把 Demo 验证结果用于授信、交易准入或支付决策。
- 不要把内存存储、Mock 身份确认和固定映射规则用于生产。
- 生产实现必须自行补充密钥管理、数据保护、审计、合规、可用性和风险控制。

详见[安全模型](../../../docs/reference-implementations/tsd-crd/security-model.md)和仓库的[安全政策](../../../SECURITY.md)。

## 参与贡献

提交代码前请阅读仓库的[贡献指南](../../../CONTRIBUTING.md)。安全问题请按[安全政策](../../../SECURITY.md)私下报告。

## 许可证

本目录代码适用仓库 [Apache License 2.0](../../../LICENSE)。协议文本、项目名称和商标可能适用独立规则；代码许可证不自动授予商标使用权。
