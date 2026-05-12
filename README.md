# ACT 协议（Agentic Commerce Trust Protocol）

面向智能体商业的开放协议框架。

## 概述

智能体商业（Agentic Commerce）正在成为继移动电商之后的下一次范式升级。ACT 协议为智能体商业提供从用户意图授权到支付结算、争议仲裁的端到端信任协议栈。

协议栈由四个域组成：

| 域 | 缩写 | 核心诉求 | 协议组件 |
|---|---|---|---|
| 委托授权域 | ADD | 用户意图如何可信地授权给智能体 | ADD-INT-EAC, ADD-INT-ISR, ADD-IAC-ISS, ADD-IAC-LCM |
| 商业交互域 | CID | 智能体如何与商户/其他智能体交互 | CID-MER-CAT, CID-INT-RUT, CID-CART-CFM, CID-PCA-NEG |
| 支付服务域 | PSD | 智能体如何安全完成支付 | PSD-PMT-BND, PSD-AGT-SUB, PSD-PAY-INS, PSD-PAY-DEL, PSD-PAY-A2A |
| 信任服务域 | TSD | 如何建立跨机构信任 | TSD-ATT-EVT, TSD-ATT-OFF, TSD-ATT-OCA, TSD-ATT-SVF, TSD-DSP-CTR, TSD-IDM-AID |

## 仓库结构

```
act-protocol/
├── README.md
├── LICENSE
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── GOVERNANCE.md
├── SECURITY.md
│
├── specs/                           # 规范文档
│   ├── overview.md                  # 协议概览
│   ├── add/spec.md                  # 委托授权域
│   ├── cid/spec.md                  # 商业交互域
│   ├── psd/spec.md                  # 支付服务域
│   ├── tsd/spec.md                  # 信任服务域
│   └── appendix/
│       └── security-interfaces.md   # 外部安全接口定义
│
├── schemas/                         # JSON Schema
│   ├── add/                         # ISR, IAC
│   ├── cid/                         # 意图上下文, 支付能力
│   ├── psd/                         # A2A 支付载荷
│   ├── tsd/                         # 存证, DID Document
│   └── openapi/                     # OpenAPI 规范
│
├── examples/                        # 示例
│   ├── scenarios/                   # 场景文档
│   └── payloads/                    # JSON 报文示例
│
├── method-specs/                    # A2A 支付方法规范
│
├── impl/                            # 参考实现
│   └── typescript/
│
└── .github/                         # GitHub 配置
```

## 规范文档

| 文档 | 说明 |
|------|------|
| [协议概览](specs/overview.md) | 背景、设计原则、协议框架 |
| [委托授权域](specs/add/spec.md) | ISR、IAC 签发、IAC 生命周期 |
| [商业交互域](specs/cid/spec.md) | 商品目录、意图传递、购物车确认、支付能力协商 |
| [支付服务域](specs/psd/spec.md) | 支付绑定、即时/委托/A2A 支付 |
| [信任服务域](specs/tsd/spec.md) | 可信存证、身份管理、争议处理 |

## 参考实现

TypeScript 参考实现位于 `impl/typescript/`，提供以下模块：

- **add/**: ISR 构造与验证、IAC 签发与验证、IAC 生命周期管理
- **cid/**: 意图上下文传递、购物车确认与规则自检、支付能力协商
- **psd/**: 支付方式绑定、即时支付、委托支付、A2A 支付
- **tsd/**: 存证记录构造/签名/核验、链上锚点、DID 解析
- **crypto/**: 外部安全接口抽象（SecurityProvider）

```bash
cd impl/typescript
npm install
npm test
```

## 贡献

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

- 规范文档（`specs/` 目录）：[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
- 代码与 Schema（`impl/`、`schemas/`、`examples/` 目录）：[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)