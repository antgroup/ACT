# 目标信息架构

> 状态：Draft / Non-normative。注意：本页描述协议修订稳定后的目标，不是当前目录清单。当前仓库结构以 [ACT 项目框架](../architecture/README.md) 为唯一事实来源。

## 1. 开发者入口

目标首页按任务而不是按组件编号组织：

```text
Start
├── I build an Agent
│   └── Agent Payment
├── I provide a paid API, MCP Tool, or Skill
│   └── AI Metered Payment
├── I implement ACT
│   ├── ACT Core
│   ├── Product Profiles
│   └── Transport Bindings
└── I contribute to ACT
    ├── Revision status
    ├── Open decisions
    └── Conformance work
```

开发者不需要先理解 ADD、CID、PSD、TSD 的所有内容，才能完成一个最小产品接入。

### 1.1 支付能力的逻辑分层

| 层次 | 回答的问题 | 首期内容 |
|---|---|---|
| 支付基础 | Agent 如何获得不暴露原始账户的支付工具 | `PSD-PMT-BND`；`PSD-AGT-SUB` 为后续可选隔离能力 |
| 场景组件 | 用户是否在场，Agent 依据什么授权执行 | L1 `PSD-PAY-INS`；L2 DEL、L3 AUP 后续演进 |
| 支付接入协议 | 支付要求、凭证、验证、状态和错误如何交换 | 候选 `PSD-PAY-A402` |
| Binding | 协议语义如何被具体运行时承载或封装 | 官方 Skill/CLI；HTTP 402 |
| Product Profile | 产品字段、API、签名和状态如何映射 | Alipay AI Pay Profile |

这些层组合后才构成可运行的产品接入，不能把 A402 接入方式等同于 AUP 自主支付场景，也不能把支付宝钱包聚合产品整体等同于 PMT-BND，或把支付宝产品字段写入 ACT 中立语义。

## 2. 目标仓库结构

下面是协议修订稳定后的目标形态，不要求在框架阶段一次性迁移：

| 规划项 | 当前状态 | 迁移条件 |
|---|---|---|
| `docs/concepts/` | 尚未建立；概念边界暂由 `docs/architecture/` 承载 | 核心概念经协议修订确认 |
| 协议版本目录 | 当前公开基线为 `specs/2.1/` Candidate | 候选正式进入发布治理 |
| Schema 版本策略 | 当前没有 2.1 Core 消息 Schema | Canonical source 与版本规则确定 |
| Profile 分目录 | 已按 `capabilities/`、`mappings/`、`sources/` 整理 | Profile 进入候选版本时增加版本元数据 |
| MCP Binding | 尚未进入首期公开基线 | 形成跨产品协议承载规范并有可公开验证的接入形式 |
| Conformance 目录 | 当前不建立空顶层目录 | 可测试的规范断言形成后再创建 |

```text
act-protocol/
├── README.md
├── docs/
│   ├── getting-started/
│   │   ├── choose-your-integration.md
│   │   ├── agent-payment.md
│   │   ├── metered-payment.md
│   │   └── end-to-end-payment.md
│   ├── concepts/
│   │   ├── roles.md
│   │   ├── protocol-vs-product.md
│   │   └── lifecycle.md
│   └── project/
├── specs/
│   ├── README.md
│   └── 2.1/
├── profiles/
│   └── alipay-ai-pay/
│       ├── capabilities/
│       ├── bindings/
│       ├── mappings/
│       └── sources/
├── bindings/
│   └── http-a402/
├── quickstarts/
│   └── alipay/
│       ├── agent-payment/
│       ├── metered-rest-provider/
│       └── end-to-end-402/
├── demos/
│   └── alipay-ai-pay-sandbox-showcase/
└── scripts/
```

`conformance/` 和 `reference-implementations/` 只有在出现首个真实资产时才进入顶层，避免用空目录暗示项目已经具备一致性认证或参考实现。

## 3. 内容所有权

| 目录 | 回答的问题 | 禁止混入的内容 |
|---|---|---|
| `docs/getting-started` | 如何选择和完成接入 | 大段协议定义、模拟产品行为 |
| `docs/concepts` | 如何理解核心概念 | 产品专有字段 |
| `specs` | 实现必须遵守什么语义 | 教程、营销描述、单一产品 API |
| `specs/<version>/schemas` | 对应协议版本的消息如何被机器验证 | 业务教程、未定稿字段 |
| `profiles` | 产品如何实现 ACT | 中立协议的重复定义 |
| `bindings` | 跨产品协议消息如何传输和包装 | 产品开户、业务签约和单一产品工作流 |
| `profiles/<product>/bindings` | 特定产品入口如何封装 ACT 与产品工作流 | 冒充跨产品通用 Binding 的产品逻辑 |
| `quickstarts` | 如何以最短路径连接真实产品 | 假支付、静态成功响应 |
| `reference-implementations` | 如何完整实现特定规范范围 | 未声明覆盖范围的“完整实现” |
| `demos` | 如何体验业务场景 | 生产可用声明 |
| `conformance` | 如何证明符合规范/Profile | 只验证 JSON 语法的弱测试 |

## 4. 首期文档导航

### 4.1 Agent 开发者

```text
README
  → Choose your integration
  → Agent Payment overview
  → Alipay Agent Payment Profile
  → Wallet and Payment Skill Quickstart
  → End-to-end 402 example
```

### 4.2 收费服务提供方

```text
README
  → Choose your integration
  → Metered Payment overview
  → Alipay Metered Payment Profile
  → REST provider Quickstart
  → Sandbox verification
  → Profile conformance tests
```

### 4.3 协议实现者

```text
README
  → Architecture
  → PSD Candidate specification
  → A402 Candidate
  → Product Profile contract
  → Transport binding
  → Candidate assertions
```

## 5. 版本与稳定性呈现

每份规范和 Profile 应在顶部包含统一元数据：

```yaml
title: Payment Proof
kind: core-spec | product-profile | binding | guide
status: draft | candidate | stable | deprecated
version: 0.1.0
last_updated: YYYY-MM-DD
depends_on:
  - act-core@x.y
supersedes: null
```

当前仓库在版本整理完成前，不继续使用没有发布证据支撑的“稳定、生产可用、完整实现”等状态描述。

## 6. 渐进迁移方式

### 阶段 A：建立新入口

新增架构、接入基线和计划文档。

### 阶段 B：建立并行草案

协议修订形成候选结论后，在 `specs/2.1/` 中建立 Core Candidate，并同步 Profile 和 Binding。

### 阶段 C：验证与迁移

通过 Quickstart、Schema 和一致性测试验证候选规范，同时明确向后兼容和升级影响。

### 阶段 D：发布

达到发布门槛后更新默认文档入口；未随公开包提供的历史版本继续保留在 Git 历史中。
