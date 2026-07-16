# ACT 协议（Agentic Commerce Trust Protocol）

面向智能体商业的开放协议框架。

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0%20%7C%20CC%20BY%204.0-blue.svg" alt="License"></a>
  <a href="https://www.act-protocol.com/"><img src="https://img.shields.io/badge/Website-www.act--protocol.com-orange" alt="Website"></a>
  <a href="https://www.act-protocol.com/documentation/delegation"><img src="https://img.shields.io/badge/Documentation-Online-green" alt="Documentation"></a>
</p>

> [!IMPORTANT]
> ACT 协议正在修订。面向开源重构的目标、边界、支付宝 AI 付公开接入基线和阶段计划，见
> [开源重构工作区](docs/open-source-restructure/README.md)。该工作区当前为非规范性草案，不修改或替代现有协议正文。

## 概述

智能体商业（Agentic Commerce）正在成为继移动电商之后的下一次范式升级。ACT 协议为智能体商业提供从用户意图授权到支付结算、争议仲裁的端到端信任协议栈。

### 什么是ACT协议？

ACT协议是一套技术规范，定义了：
- 用户如何安全地将购物意图授权给智能体
- 智能体如何与其他智能体或商户完成商业交互
- 如何在智能体之间安全地进行支付
- 如何建立跨机构、跨平台的信任机制

### 协议栈架构

协议由四个核心域组成：

| 域 | 缩写 | 核心诉求 | 主要协议组件 |
|---|---|---|---|
| [委托授权域](specs/2.0/authorization-delegation-domain-spec.md) | ADD | 用户意图如何可信地授权给智能体 | ADD-INT-EAC, ADD-INT-ISR, ADD-IAC-ISS, ADD-IAC-LCM |
| [商业交互域](specs/2.0/commerce-interaction-domain-spec.md) | CID | 智能体如何与商户/其他智能体交互 | CID-MER-CAT, CID-INT-RUT, CID-CART-CFM, CID-PCA-NEG |
| [支付服务域](specs/2.0/payment-services-domain-spec.md) | PSD | 智能体如何安全完成支付 | PSD-PMT-BND, PSD-AGT-SUB, PSD-PAY-INS, PSD-PAY-DEL, PSD-PAY-A2A |
| [信任服务域](specs/2.0/trust-services-domain-spec.md) | TSD | 如何建立跨机构信任 | TSD-ATT-EVT, TSD-ATT-OFF, TSD-ATT-OCA, TSD-ATT-SVF, TSD-DSP-CTR, TSD-IDM-AID |

## 快速开始

### 了解协议

1. **阅读协议概览** → [specs/2.0/overview.md](specs/2.0/overview.md) | [在线文档](https://www.act-protocol.com/documentation/delegation)
2. **查看典型场景** → [examples/scenarios/](examples/scenarios/)
3. **了解数据结构** → [schemas/](schemas/)
4. **运行示例代码** → [impl/python/](impl/python/)

### 使用场景

| 场景 | 描述 | 相关文档 |
|------|------|----------|
| [即时支付](examples/scenarios/common/01-instant-payment.md) | 用户在场，实时确认支付 | PSD-PAY-INS |
| [平台委托支付](examples/scenarios/common/02-platform-delegated-payment.md) | 用户授权平台型智能体代为支付 | PSD-PAY-DEL |
| [专属委托支付](examples/scenarios/common/03-dedicated-delegated-payment.md) | 用户授权专属智能体使用子账户支付 | PSD-PAY-DEL + PSD-AGT-SUB |
| [自主A2A支付](examples/scenarios/common/04-autonomous-delegation.md) | 智能体自主决策完成复杂任务 | PSD-PAY-A2A |

### 角色场景

ACT协议定义了多个参与角色，各角色有不同的关注点和交互场景：

| 角色 | 职责 | 典型场景 | 相关文档 |
|------|------|---------|----------|
| **用户 (User)** | 意图发起方，授权智能体代为执行商业活动 | [即时购买](examples/scenarios/role/buyer-agent/README.md)、[委托授权](examples/scenarios/role/agent/README.md) | ADD, CID |
| **买方智能体 (Buyer Agent)** | 代表用户完成商品发现、比较、购买 | [智能购物](examples/scenarios/role/buyer-agent/README.md)、[A2A协商](examples/scenarios/role/agent/README.md) | CID, PSD |
| **卖方智能体 (Seller Agent)** | 代表商户提供商品和服务，处理交易 | [商品上架](examples/scenarios/role/seller-agent/README.md)、[订单处理](examples/scenarios/role/merchant/README.md) | CID, PSD |
| **商户 (Merchant)** | 提供实际商品/服务，承担履约责任 | [库存管理](examples/scenarios/role/merchant/README.md)、[收款结算](examples/scenarios/role/psp) | CID, PSD |
| **平台智能体 (Platform Agent)** | 为多个委托人提供共享智能体服务 | [多租户委托](examples/scenarios/role/platform-agent/README.md)、[风险管理](examples/scenarios/role/platform-agent/README.md) | ADD, PSD |
| **支付服务方 (PSP)** | 处理支付授权、资金划拨、结算 | [支付处理](examples/scenarios/role/psp/README.md)、[IAC核验](examples/scenarios/role/psp/README.md) | PSD, TSD |
| **存证服务方 (TSP)** | 提供可信存证和争议仲裁 | [存证记录](examples/scenarios/role/tsd-provider/README.md)、[争议裁决](examples/scenarios/role/tsd-provider/README.md) | TSD |

详细角色场景文档：[examples/scenarios/role/README.md](examples/scenarios/role/README.md)

### 交互式演示

我们提供对话式的交互演示，让您体验三种支付模式：

```bash
cd impl/python
streamlit run chat_based_demo.py
```

## 仓库结构

```
act-protocol/
├── README.md                    # 本文件
├── LICENSE                      # 许可证说明
├── CODE_OF_CONDUCT.md           # 行为准则
├── CONTRIBUTING.md              # 贡献指南
├── GOVERNANCE.md                # 治理模型
├── SECURITY.md                  # 安全披露政策
│
├── specs/                       # 规范文档 📚
│   └── 2.0/                     # v2.0版本规范
│       ├── overview.md          # 协议概览 [开始阅读]
│       ├── authorization-delegation-domain-spec.md      # ADD委托授权域规范
│       ├── commerce-interaction-domain-spec.md          # CID商业交互域规范
│       ├── payment-services-domain-spec.md              # PSD支付服务域规范
│       ├── trust-services-domain-spec.md                # TSD信任服务域规范
│       ├── appendix/
│       │   └── security-interfaces.md
│       └── schemas/             # 每个域的伴生Schema
│           ├── authorization-delegation-domain/
│           ├── commerce-interaction-domain/
│           ├── payment-services-domain/
│           └── trust-services-domain/
│
├── examples/                    # 示例与场景 📖
│   ├── scenarios/               # 业务场景文档
│   │   ├── common/              # 通用场景（按流程分类）
│   │   │   ├── 01-instant-payment.md
│   │   │   ├── 02-platform-delegated-payment.md
│   │   │   ├── 03-dedicated-delegated-payment.md
│   │   │   ├── 04-autonomous-delegation.md
│   │   │   └── e2e-walkthrough.md
│   │   └── role/                # 角色场景（按角色分类）
│   │       ├── README.md
│   │       ├── agent/           # 智能体角色场景
│   │       ├── buyer-agent/     # 买方智能体场景
│   │       ├── merchant/        # 商户角色场景
│   │       ├── platform-agent/  # 平台智能体场景
│   │       ├── psp/             # 支付服务方场景
│   │       ├── seller-agent/    # 卖方智能体场景
│   │       └── tsd-provider/    # 存证服务方场景
│   └── payloads/                # JSON报文示例
│       ├── add/                 # ADD域报文示例
│       ├── cid/                 # CID域报文示例
│       ├── psd/                 # PSD域报文示例
│       └── tsd/                 # TSD域报文示例
│
├── impl/                        # 参考实现 💻
│   └── python/                  # Python参考实现
│       ├── assistant_agent/     # 助理智能体实现
│       ├── market_service/      # 市场服务
│       ├── merchant_service/    # 商户服务
│       ├── payment_service/     # 支付服务
│       │   ├── instant_payment.py
│       │   ├── delegated_payment.py
│       │   └── autonomous_payment.py
│       ├── psd/                 # PSD域核心实现
│       │   └── delegated_payment/
│       └── ui/                  # 交互式演示界面
│           ├── app.py           # Streamlit主应用
│           ├── chat_based_demo.py  # 对话式演示
│           ├── identity_select.py
│           ├── merchant_service_ui.py
│           ├── payment_demo.py
│           └── shopping_assistant.py
│
└── tmp/                         # 临时文件/草稿
    │   ├── add/                 # 委托授权实现
    │   ├── cid/                 # 商业交互实现
    │   ├── psd/                 # 支付服务实现
    │   ├── tsd/                 # 信任服务实现
    │   └── chat_based_demo.py   # 交互式演示
    └── typescript/              # TypeScript参考实现
```

## 规范文档导航

### 核心规格

| 文档 | 说明 | 相关Schema | 示例场景 |
|------|------|-----------|----------|
| [协议概览](specs/2.0/overview.md) | 背景、设计原则、协议框架 | - | - |
| [委托授权域规范](specs/2.0/authorization-delegation-domain-spec.md) | ISR构造与验证、IAC签发与生命周期 | [schemas/add/](schemas/add/) | [场景1-4](examples/scenarios/) |
| [商业交互域规范](specs/2.0/commerce-interaction-domain-spec.md) | 商品目录、意图传递、购物车确认、支付能力协商 | [schemas/cid/](schemas/cid/) | [场景1-4](examples/scenarios/) |
| [支付服务域规范](specs/2.0/payment-services-domain-spec.md) | 支付绑定、即时/委托/A2A支付 | [schemas/psd/](schemas/psd/) | [场景1-4](examples/scenarios/) |
| [信任服务域规范](specs/2.0/trust-services-domain-spec.md) | 存证、身份管理、争议处理 | [schemas/tsd/](schemas/tsd/) | [场景1-4](examples/scenarios/) |
| [安全接口附录](specs/appendix/security-interfaces.md) | 外部安全接口抽象 | - | - |

### 快速导航

```
┌─────────────────────────────────────────────────────────────┐
│                        ACT 协议文档体系                      │
├─────────────────────────────────────────────────────────────┤
│  README.md (入口)                                            │
│      │                                                       │
│      ▼                                                       │
│  specs/2.0/overview.md ────────────┐                        │
│      │                             │                        │
│      ▼                             ▼                        │
│  specs/2.0/*-domain-spec.md       examples/scenarios/       │
│      │                                                          │
│      ▼                                                          │
│  schemas/{add,cid,psd,tsd}/                                     │
│      │                                                          │
│      ▼                                                          │
│  examples/payloads/                                              │
└─────────────────────────────────────────────────────────────┘
```

## 规范状态

| 规范 | 版本 | 状态 | 说明 |
|------|------|------|------|
| ADD (委托授权域) | v1.0.0 | ✅ 稳定 | 已发布，可供生产使用 |
| CID (商业交互域) | v1.0.0 | ✅ 稳定 | 已发布，可供生产使用 |
| PSD (支付服务域) | v1.0.0 | ✅ 稳定 | 已发布，可供生产使用 |
| TSD (信任服务域) | v0.9.0 | 🚧 候选 | 功能完整，验证中 |

## 参考实现

### Python实现

位于 `impl/python/`，提供完整的协议实现：

```bash
cd impl/python
pip install -r requirements.txt
python -m pytest
```

主要模块：
- `add/` - ISR/IAC签发与验证、IAC生命周期管理
- `cid/` - 意图上下文传递、购物车确认
- `psd/` - 即时支付、委托支付、A2A支付
- `tsd/` - 存证记录、DID解析
- `chat_based_demo.py` - 对话式交互演示

## 贡献

我们欢迎各种形式的贡献！请阅读以下文档开始：

- [行为准则](CODE_OF Conduct.md) - 社区参与规范
- [贡献指南](CONTRIBUTING.md) - 如何提交Issue/PR
- [治理模型](GOVERNANCE.md) - 项目治理结构
- [安全披露](SECURITY.md) - 如何报告安全问题

### 快速贡献

1. **发现问题**？提交Issue到当前仓库或发送邮件至 dev@actprotocol.org
2. **有改进想法**？联系维护者团队讨论
3. **想贡献代码**？Fork → 修改 → 提交 PR
4. **发现安全问题**？查看 [SECURITY.md](SECURITY.md) 安全披露流程

## 社区

- 💬 **技术讨论**：联系维护者团队或发送邮件至 dev@actprotocol.org
- 🐛 **问题反馈**：提交Issue到当前仓库或联系 tc@actprotocol.org
- 🌐 **官方网站**：[https://www.act-protocol.com](https://www.act-protocol.com)
- 📖 **在线文档**：[https://www.act-protocol.com/documentation/delegation](https://www.act-protocol.com/documentation/delegation)

## 许可证

本仓库采用双许可证：

| 内容 | 许可证 | 说明 |
|------|--------|------|
| 规范文档（`specs/`）| [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 可自由分享和改编，需署名 |
| 代码与Schema（`impl/`、`schemas/`、`examples/`）| [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) | 可自由使用和修改，需保留版权声明 |

详见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  <b>ACT Protocol</b> - 为智能体商业构建信任基础设施
</p>
