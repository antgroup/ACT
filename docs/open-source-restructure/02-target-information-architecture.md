# 目标信息架构

> 状态：Draft / Non-normative

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

## 2. 目标仓库结构

下面是协议修订稳定后的目标形态，不要求在框架阶段一次性迁移：

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
│   └── open-source-restructure/
├── specs/
│   ├── current/
│   └── versions/
├── schemas/
│   └── current/
├── profiles/
│   └── alipay-ai-pay/
│       ├── agent-payment/
│       ├── metered-payment/
│       └── mappings/
├── bindings/
│   ├── http/
│   ├── skill/
│   └── mcp/
├── quickstarts/
│   └── alipay/
│       ├── agent-payment/
│       ├── metered-rest-provider/
│       └── end-to-end-402/
├── reference-implementations/
├── demos/
├── conformance/
│   ├── core/
│   └── profiles/alipay-ai-pay/
└── examples/
```

## 3. 内容所有权

| 目录 | 回答的问题 | 禁止混入的内容 |
|---|---|---|
| `docs/getting-started` | 如何选择和完成接入 | 大段协议定义、模拟产品行为 |
| `docs/concepts` | 如何理解核心概念 | 产品专有字段 |
| `specs` | 实现必须遵守什么语义 | 教程、营销描述、单一产品 API |
| `schemas` | 消息如何被机器验证 | 业务教程、未定稿字段 |
| `profiles` | 产品如何实现 ACT | 中立协议的重复定义 |
| `bindings` | 消息如何传输和包装 | 产品开户和业务签约 |
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
  → ACT Core specification
  → Common message model
  → Lifecycle and recovery
  → Product Profile contract
  → Transport binding
  → Conformance suite
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

新增架构、接入基线和计划文档；现有规范保持原位。

### 阶段 B：建立并行草案

协议修订形成候选结论后，在独立草案目录中建立 Core、Profile 和 Binding，不覆盖 `specs/2.0/`。

### 阶段 C：验证与迁移

通过 Quickstart、Schema 和一致性测试验证候选规范，同时建立旧组件到新模型的迁移表。

### 阶段 D：发布

达到发布门槛后更新默认文档入口，保留历史版本和迁移指南，不删除可追溯历史。
