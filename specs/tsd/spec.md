# 信任服务域（Trust Services Domain, TSD）

## 1 范围

信任服务域（Trust Services Domain，TSD）为 ACT 协议的其他三个域（委托授权域、商业交互域、支付服务域）提供底层的信任基础设施，包括智能体身份管理、可信存证、存证验证与争议解决等核心能力。

**本域范围：**

- 定义 `did:act` 去中心化身份标识方法规范；
- 定义智能体身份文档（DID Document）的结构与解析规则；
- 定义可信存证事件的结构化表达与上链流程；
- 定义存证服务方的接入规范与存证记录管理；
- 定义链上存证锚的生成与验证机制；
- 定义争议解决的交互流程与争议中心的管理规范。

## 2 术语和定义

### 存证事件 Attestation Event

各协议域在关键业务节点产生的、需要被可信记录的结构化事件。存证事件由事件产生方异步上报至存证服务方，经存证服务方处理后写入 ACT Trust Chain。

### 存证服务方 Attestation Service Provider

为 ACT 协议生态提供可信存证服务的机构或系统组件。其职责包括接收存证事件、验证事件格式与签名、生成存证记录、将存证锚写入 ACT Trust Chain，以及响应存证验证请求。

### 存证记录 Attestation Record

存证服务方在处理存证事件后生成的结构化记录，包含事件摘要、存证时间戳、存证服务方签名等信息，作为事件已被可信记录的证据。

### 存证锚 Attestation Anchor

存证服务方定期将一批存证记录的聚合摘要写入 ACT Trust Chain 后生成的链上锚点。存证锚为存证记录提供不可篡改的链上证明，是信任服务域信任链的根锚。

### ACT Trust Chain

由信任服务域构建的联盟链，用于承载存证锚的写入与验证。ACT Trust Chain 为参与方提供去中心化的信任锚定能力，确保存证记录的不可篡改性与可验证性。

### 争议中心 Dispute Center

为 ACT 协议生态中的参与方提供争议提交、调解与裁决服务的机构或平台。争议中心接收买卖双方提交的争议申请，依据协议规则与存证证据进行裁决。

### did:act

ACT 协议定义的去中心化身份标识方法，基于 W3C DID v1.1 规范，用于为智能体、委托人、商户等参与方提供全局唯一、可验证、可解析的身份标识。

## 3 本域协议组件列表

| 协议组件 | 组件描述 |
|---------|---------|
| `TSD-ATT-EVT`：存证事件定义 | 定义各协议域产生的存证事件的结构化表达格式与上报规范。 |
| `TSD-ATT-OFF`：存证服务接入 | 规范存证服务方的接入要求、存证事件接收与存证记录生成流程。 |
| `TSD-ATT-OCA`：链上存证锚 | 定义存证锚的生成、写入 ACT Trust Chain 及验证机制。 |
| `TSD-ATT-SVF`：存证验证服务 | 规范存证记录与存证锚的验证接口与验证流程。 |
| `TSD-DSP-CTR`：争议中心 | 定义争议提交、调解与裁决的交互流程。 |
| `TSD-IDM-AID`：智能体身份管理 | 定义 `did:act` 身份标识方法、DID Document 结构与解析规则。 |

## 4 域内协议组件描述

### 4.1 TSD-ATT-EVT：存证事件定义

#### 概述

存证事件定义（Attestation Event）规范了 ACT 协议各域在关键业务节点产生的存证事件的结构化表达格式。存证事件是信任服务域的输入，由事件产生方（智能体、PSP、商户或其代理存证服务商）异步上报至存证服务方。

#### 存证事件结构

每个存证事件应包含以下字段：

| 字段名 | 类型 | 存在性 | 说明 |
|--------|------|--------|------|
| `event_id` | string | 必备 | 存证事件的全局唯一标识符 |
| `event_type` | string | 必备 | 事件类型标识，采用反向域名格式（如 `act:delegation:delegation-issued`） |
| `event_time` | string | 必备 | 事件发生时间（ISO 8601 UTC） |
| `event_source` | string | 必备 | 事件产生方的身份标识 |
| `domain` | string | 必备 | 所属协议域（`ADD` / `CID` / `PSD` / `TSD`） |
| `payload` | object | 必备 | 事件载荷，包含与事件类型对应的业务数据 |
| `payload_digest` | string | 必备 | 事件载荷的数字摘要 |
| `related_ids` | array[string] | 可选 | 关联的业务标识列表（如 intent_id、delegation_id、trade_no 等） |
| `signature` | string | 必备 | 事件产生方对事件核心字段的数字签名 |

#### 事件类型注册表

以下为当前已注册的存证事件类型：

| 事件类型标识 | 所属域 | 触发时机 |
|-------------|--------|---------|
| `act:delegation:intent-created` | ADD | 用户意图确认完成 |
| `act:delegation:delegation-issued` | ADD | IAC 完成签发 |
| `act:delegation:delegation-suspended` | ADD | IAC 被临时挂起 |
| `act:delegation:delegation-resumed` | ADD | IAC 恢复为 Active |
| `act:delegation:delegation-revoked` | ADD | IAC 被永久吊销 |
| `act:delegation:delegation-expired` | ADD | IAC 自动过期 |
| `act:commerce:decision-logged` | CID | 买方智能体完成多候选比较决策 |
| `act:commerce:cart-confirmed` | CID | 购物车确认完成，订单交易号生成 |
| `act:commerce:fulfillment-completed` | CID | 商户侧完成商品/服务交付 |
| `act:payment:transaction-completed` | PSD | 支付交易完成 |

新增事件类型的注册应由相应域的工作组提出，经维护者审核后纳入注册表。

### 4.2 TSD-ATT-OFF：存证服务接入

#### 概述

存证服务接入（Attestation Offering）规范了存证服务方的接入要求与存证事件的处理流程。

#### 存证服务方要求

存证服务方应满足以下要求：

- 具备合法的运营资质与安全合规能力；
- 维护与 ACT Trust Chain 的写入连接；
- 提供符合本规范定义的存证事件接收接口；
- 对接收到的存证事件执行格式校验与签名验证；
- 在规定时间内生成存证记录并返回确认；
- 定期将存证记录聚合为存证锚写入 ACT Trust Chain。

#### 存证事件处理流程

1. **事件接收**：存证服务方通过标准化接口接收事件产生方上报的存证事件。
2. **格式校验**：验证事件结构符合本规范定义的存证事件结构要求。
3. **签名验证**：验证事件产生方签名的有效性，确认事件来源可信。
4. **去重处理**：基于 `event_id` 进行幂等校验，防止重复存证。
5. **记录生成**：生成存证记录，包含事件摘要、存证时间戳、存证服务方签名。
6. **确认返回**：向事件产生方返回存证确认，包含存证记录标识。

### 4.3 TSD-ATT-OCA：链上存证锚

#### 概述

链上存证锚（On-Chain Attestation Anchor）定义存证锚的生成、写入与验证机制。存证锚是存证记录获得链上不可篡改证明的关键环节。

#### 存证锚结构

| 字段名 | 类型 | 存在性 | 说明 |
|--------|------|--------|------|
| `anchor_id` | string | 必备 | 存证锚唯一标识符 |
| `chain_id` | string | 必备 | ACT Trust Chain 网络标识 |
| `block_height` | integer | 必备 | 链上区块高度 |
| `block_hash` | string | 必备 | 链上区块哈希 |
| `merkle_root` | string | 必备 | 本批次存证记录的 Merkle 根哈希 |
| `record_count` | integer | 必备 | 本批次包含的存证记录数量 |
| `anchor_time` | string | 必备 | 存证锚生成时间（ISO 8601 UTC） |
| `attestation_provider_id` | string | 必备 | 生成该锚的存证服务方标识 |

#### 锚生成规则

存证服务方应按以下规则生成存证锚：

1. 定期（如每 10 分钟或每 1000 条记录）将待锚定的存证记录聚合成 Merkle 树；
2. 计算 Merkle 根哈希；
3. 构造存证锚交易并提交至 ACT Trust Chain；
4. 链上确认后，记录区块高度与区块哈希；
5. 为该批次中每条存证记录生成对应的 Merkle 证明路径。

### 4.4 TSD-ATT-SVF：存证验证服务

#### 概述

存证验证服务（Attestation Verification Service）规范了存证记录与存证锚的验证接口与验证流程，供参与方在需要时验证特定存证事件的可信性。

#### 验证流程

1. **存证记录查询**：验证方通过存证记录标识向存证服务方查询存证记录。
2. **签名验证**：验证存证服务方对存证记录的签名有效性。
3. **Merkle 证明验证**：使用存证锚中的 Merkle 根哈希与存证记录的 Merkle 证明路径，验证存证记录确实包含在该批次中。
4. **链上锚验证**：查询 ACT Trust Chain 上对应区块高度的区块哈希，与存证锚中记录的区块哈希比对，确认锚未被篡改。

验证通过后，验证方可确认该存证事件在声明的时间点已被可信记录且未被篡改。

### 4.5 TSD-DSP-CTR：争议中心

#### 概述

争议中心（Dispute Center）为 ACT 协议生态中的参与方提供争议提交、调解与裁决服务。

#### 争议提交

当交易参与方对交易结果存在异议时，可向争议中心提交争议申请。争议申请应包含以下要素：

- 争议方身份标识；
- 关联的交易标识（如订单号、交易流水号等）；
- 争议类型与争议描述；
- 相关存证事件标识列表，作为争议证据；
- 争议方签名。

#### 争议类型

| 争议类型 | 说明 |
|---------|------|
| 未授权交易 | 委托人声称某笔交易未获其授权 |
| 履约争议 | 买方声称卖方未完成商品/服务交付 |
| 金额争议 | 交易金额与约定不一致 |
| 凭证争议 | 对意图授权凭证的有效性存在异议 |

#### 裁决依据

争议中心在进行裁决时，应综合考量以下依据：

- 相关存证事件的完整链路证据；
- 意图授权凭证的有效性及约束范围；
- 支付交易记录与购物车确认记录的一致性；
- 各参与方的身份验证记录。

### 4.6 TSD-IDM-AID：智能体身份管理

#### 概述

智能体身份管理（Agent Identity Management）定义了 `did:act` 去中心化身份标识方法，为 ACT 协议生态中的参与方提供全局唯一、可验证、可解析的身份标识。

本方法基于 W3C DID v1.1 规范，定义了 `did:act` 方法的标识符格式、DID Document 结构与解析规则。

#### did:act 标识符格式

```
did:act:<domain>/<identifier>
```

其中：

- `did`：固定前缀，符合 W3C DID 规范；
- `act`：方法名称，标识本方法；
- `<domain>`：方法特定标识，通常为域名或组织标识；
- `<identifier>`：方法特定身份标识，由域内管理机构分配。

示例：

- `did:act:example.com/user-alice`：委托人 Alice 的身份标识
- `did:act:example.com/agent-alice-001`：智能体 Alice-001 的身份标识
- `did:act:example.com/merchant-shop-001`：商户 Shop-001 的身份标识

#### DID Document 结构

DID Document 描述了与 `did:act` 标识符关联的验证方法与服务端点。DID Document 应包含以下核心字段：

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://specs.actprotocol.org/ns/did/act/v1"
  ],
  "id": "did:act:example.com/agent-alice-001",
  "controller": "did:act:example.com/user-alice",
  "verificationMethod": [
    {
      "id": "did:act:example.com/agent-alice-001#key-1",
      "type": "JsonWebKey2020",
      "controller": "did:act:example.com/agent-alice-001",
      "publicKeyJwk": {
        "kty": "EC",
        "crv": "P-256",
        "x": "U1V6Ul...=",
        "y": "Wk9XQl...="
      }
    }
  ],
  "authentication": [
    "did:act:example.com/agent-alice-001#key-1"
  ],
  "assertionMethod": [
    "did:act:example.com/agent-alice-001#key-1"
  ],
  "service": [
    {
      "id": "did:act:example.com/agent-alice-001#agent-card",
      "type": "AgentCard",
      "serviceEndpoint": "https://agent.example.com/.well-known/agent.json"
    }
  ]
}
```

#### DID Document 解析

`did:act` 标识符的解析通过以下方式实现：

- **Well-Known URI**：通过 `https://<domain>/.well-known/did-act/<identifier>` 路径获取 DID Document；
- **可验证注册表**：通过 ACT Trust Chain 上的身份注册表查询 DID Document 的当前状态。

解析过程应遵循以下规则：

1. 从 `did:act` 标识符中提取 `<domain>` 和 `<identifier>`；
2. 通过 Well-Known URI 或可验证注册表获取 DID Document；
3. 验证 DID Document 的签名与完整性；
4. 返回当前有效的 DID Document。

#### 密钥轮换

当智能体的验证密钥需要更新时，应通过以下流程完成密钥轮换：

1. 在 DID Document 中添加新的验证方法条目；
2. 将 `authentication` 和 `assertionMethod` 引用更新为新密钥；
3. 使用当前有效密钥对更新后的 DID Document 进行签名；
4. 将更新后的 DID Document 发布至解析端点。

旧密钥在轮换完成后应标记为失效，但 DID Document 中宜保留其历史记录以支持历史签名验证。

## 5 本域涉及的存证事件定义

本域自身不产生额外的存证事件类型。本域的核心职责是为其他域产生的存证事件提供可信记录与验证服务。

存证事件类型注册表由本域维护，参见 4.1 节。