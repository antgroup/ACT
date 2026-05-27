# 场景二：信任服务提供商视角 - 委托支付

## 场景描述

作为信任服务提供商（TSD），我在委托支付场景中提供 IAC 生命周期存证、委托执行过程的可信记录，以及授权边界争议的调解服务。重点保障委托人授权意图的可追溯性和智能体执行行为的可审计性。

## 角色定位

- **我是**：信任服务提供商（Trust Services Provider, TSD）
- **服务对象**：持有 IAC 的各方（委托人、受托智能体、PSP、商户）
- **核心能力**：IAC 状态存证、委托执行审计、授权边界验证、授权争议处理
- **功能定位**：委托从授权到执行全生命周期的信任基础设施

## 委托场景下的信任挑战

```
┌─────────────────────────────────────────────────────────────┐
│                    委托支付的信任问题                       │
│                                                             │
│  问题1: 授权不可否认性                                      │
│    智能体: "用户授权我这么做的"                            │
│    用户:   "我什么时候授权了？"                            │
│    → 需要: IAC 签发的可信存证                              │
│                                                             │
│  问题2: 执行边界争议                                        │
│    用户:   "我只授权了 100 元，为什么扣了 200？"            │
│    智能体: "额度就是 200，你看凭证上写的"                   │
│    → 需要: 授权内容哈希存证 + 执行记录                     │
│                                                             │
│  问题3: 执行真实性                                          │
│    用户:   "我取消了授权，为什么还在扣费？"                 │
│    智能体: "撤销前已经发起的交易无法阻止"                   │
│    → 需要: 时间线清晰的存证记录                            │
│                                                             │
│  问题4: 多参与方责任归属                                    │
│    用户:   "钱扣了但服务没到账，谁的责任？"                 │
│    → 需要: 全流程多方存证，责任可界定                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 我的核心职责

### 1. IAC 签发存证（`TSD-ATT-OFF` + `ADD-IAC-ISS`）

当委托人签发 IAC 时，记录签发事件的完整上下文：

```json
{
  "event_type": "add_iac_issued",
  "domain": "ADD",
  "component": "ADD-IAC-ISS",

  "content": {
    "iac_id": "iac-2024-001-xyz",
    "iac_hash": "sha256:abc123...",

    "principal": {
      "did": "did:act:principal-001",
      "authentication_method": "biometric+pin",
      "device_binding": "device-id-abc"
    },

    "delegate_agent": {
      "did": "did:act:buyer-agent-001",
      "type": "platform_agent"
    },

    "authorization": {
      "mode": "SPECIFIED",
      "merchant_allowlist": ["did:act:merchant-001", "did:act:merchant-002"],
      "amount_limit": "500.00",
      "currency": "CNY",
      "period": "monthly",
      "valid_from": "2024-01-01T00:00:00Z",
      "valid_until": "2024-12-31T23:59:59Z"
    },

    "issuance_context": {
      "timestamp": "2024-01-01T10:00:00Z",
      "client_ip": "192.168.1.1",
      "device_fingerprint": "fp-xyz123"
    }
  },

  "signatures": {
    "principal": "sig-principal...",
    "add_issuer_service": "sig-service...",
    "tsd": "sig-tsd..."
  }
}
```

**存证重点**：
- IAC 内容的哈希（不存明文，可调取验证）
- 委托人核身方法的详细记录
- 签发时的设备/上下文信息（用于争议时的身份验证追溯）

### 2. IAC 生命周期状态存证（`TSD-ATT-OFF` + `ADD-IAC-LCM`）

记录 IAC 从生到灭的全状态流转：

```
IAC 生命周期状态图 (存证视角)

[CREATED] 创建
    │
    ▼ 签发确认存证
[ACTIVE] 生效 ────存证───── 签发事件 + 生效事件
    │
    ├── 每次委托执行 ────存证───── 执行事件
    │
    ├── 额度更新 ────存证───── 额度消耗事件
    │
    ├── [SUSPENDED] 挂起 ────存证───── 挂起事件（用户主动/风控触发）
    │      │
    │      ▼ 恢复
    │   [ACTIVE] 生效 ────存证───── 恢复事件
    │
    ├── [REVOKED] 撤销 ────存证───── 撤销事件
    │
    └── [EXPIRED] 过期 ────存证───── 过期事件
```

**关键状态变更存证事件**：

- **生效事件**（`add_iac_activated`）：IAC 开始可以被执行
- **执行事件**（`add_iac_executed`）：每次委托执行发生时
- **额度消耗事件**（`add_iac_quota_consumed`）：记录额度变动
- **挂起事件**（`add_iac_suspended`）：IAC 暂停执行
- **恢复事件**（`add_iac_resumed`）：IAC 恢复执行
- **撤销事件**（`add_iac_revoked`）：IAC 被委托人撤销
- **过期事件**（`add_iac_expired`）：IAC 自然过期

### 3. 委托执行过程存证

每笔委托支付执行的完整存证链：

```json
{
  "event_type": "delegated_payment_execution",
  "iac_id": "iac-2024-001-xyz",

  "execution": {
    "execution_id": "exec-20240115-001",
    "sequence_no": 5,
    "trigger_time": "2024-01-15T00:00:00Z",
    "trigger_type": "scheduled_monthly"
  },

  "rule_self_check": {
    "merchant_check": {
      "requested": "did:act:merchant-001",
      "in_allowlist": true,
      "timestamp": "2024-01-15T00:00:01Z"
    },
    "quota_check": {
      "amount": "99.00",
      "consumed_before": "396.00",
      "remaining_before": "104.00",
      "would_exceed": false,
      "timestamp": "2024-01-15T00:00:01Z"
    },
    "validity_check": {
      "checked_at": "2024-01-15T00:00:01Z",
      "iac_status": "ACTIVE",
      "in_valid_period": true
    }
  },

  "payment": {
    "status": "success",
    "psp_transaction_id": "psp-txn-abc123",
    "executed_at": "2024-01-15T00:00:05Z"
  },

  "participants": {
    "delegate_agent": "did:act:buyer-agent-001",
    "psp": "did:act:psp-001",
    "merchant": "did:act:merchant-001"
  }
}
```

### 4. 授权边界验证服务

提供运行时验证接口，供智能体在执行前核验授权边界：

```
验证请求:
POST /tsd/v1/iac/validate
{
  "iac_id": "iac-2024-001-xyz",
  "proposed_action": {
    "merchant": "did:act:merchant-001",
    "amount": "99.00",
    "currency": "CNY",
    "category": "telecom_service"
  }
}

验证响应:
{
  "valid": true/false,
  "iac_status": "ACTIVE",
  "constraints": {
    "merchant_in_allowlist": true,
    "amount_within_quota": true,
    "in_valid_period": true,
    "category_allowed": true
  },
  "current_quota": {
    "limit": "500.00",
    "consumed": "396.00",
    "proposed_consumption": "99.00",
    "would_remain": "5.00"
  },
  "tsd_attestation": "sig-tsd..."
}
```

### 5. 多参与方事件关联

将同一委托链路上的多方事件关联索引：

```
委托执行关联图谱 (以一次月度话费续费为例)

IAC: iac-2024-001-xyz
└── Execution: exec-20240115-001
    ├── Event 1: add_iac_executed (买方智能体上报)
    │   └── 时间: 00:00:00, 触发条件: monthly_schedule
    │
    ├── Event 2: cid_cart_confirmed (商户侧存证)
    │   └── 时间: 00:00:02, 商品: 话费套餐99元
    │
    ├── Event 3: psd_pay_del_request (PSD域存证)
    │   └── 时间: 00:00:03, IAC 引用, 目标商户
    │
    ├── Event 4: psd_payment_success (PSP 上报)
    │   └── 时间: 00:00:05, 流水号: psp-txn-abc123
    │
    ├── Event 5: merchant_fulfillment (商户上报)
    │   └── 时间: 00:00:06, 状态: 充值成功
    │
    └── Event 6: iac_quota_updated (额度更新)
        └── 时间: 00:00:07, 已用额度: 396→495
```

### 6. 争议处理支持（`TSD-ATT-DSP`）

#### 6.1 委托授权争议

**场景**：用户否认签发过某 IAC

**TSD 支持**：
- 提供 IAC 签发存证记录
- 提供签发时的核身记录（生物识别日志、设备指纹）
- 提供签发的时空上下文（IP、设备、时间）

#### 6.2 执行边界争议

**场景**：用户认为执行超出授权范围

**TSD 支持**：
- 提供 IAC 原文哈希与当前执行请求的比照
- 提供每次执行的规则自检记录（白名单检查、额度检查）
- 提供额度累计消耗的时间线

#### 6.3 执行时间争议

**场景**：用户已撤销 IAC，但之后又发生了扣款

**TSD 支持**：
- 精确的时间线存证：撤销请求时间 vs 支付发起时间
- 证明交易是在撤销前已发起还是撤销后违规发起
- 区分"撤销前已发起的交易继续执行"与"撤销后的新交易"

### 7. 可信时间戳服务

为所有存证事件提供可信时间戳：
- 与国家标准时间源同步
- 时间戳包含 TSD 签名
- 支持时间戳的独立验证

## 委托场景下的特殊存证需求

### 周期性委托的连续性存证
对于每月自动续费这类周期性委托：
- 记录每次执行的时间、金额、商户
- 累积记录形成完整的执行历史
- 支持年度/季度维度的执行报告生成

### 额度消耗的精确追踪
```
额度追踪存证示例:

IAC 限额: CNY 500/月

2024-01-01 10:00  IAC 签发        存证: 限额 500, 已用 0
2024-01-05 09:00  执行 #1 -50     存证: 已用 50,  剩余 450
2024-01-12 14:00  执行 #2 -99     存证: 已用 149, 剩余 351
2024-01-15 00:00  执行 #3 -99     存证: 已用 248, 剩余 252
2024-01-20 18:00  执行 #4 -150    存证: 已用 398, 剩余 102
2024-01-28 10:00  执行 #5 -50     存证: 已用 448, 剩余 52
2024-02-01 00:00  额度重置       存证: 已用 0,   剩余 500
```

### 撤销与熔断的紧急响应
- 撤销指令的接收立即存证
- 撤销后的执行尝试立即标记为违规
- 支持紧急熔断指令（用户级的全局停止）

## 链上锚定策略

委托场景的存证锚定特殊考虑：

- **高频周期执行**：月度/季度批量锚定，而非每笔上链
- **关键状态变更**：IAC 签发、撤销等重要事件优先锚定
- **争议预防**：接近额度上限的执行及时锚定
- **用户可控**：允许用户要求特定存证立即上链（增值服务）

## 与即时支付场景的差异

| 维度 | 即时支付场景 | 委托支付场景 |
|------|-------------|-------------|
| 核心存证 | 单次交易事件 | IAC 生命周期 + 多次执行事件 |
| 存证复杂度 | 低（单次） | 高（持续跟踪） |
| 时间敏感度 | 实时记录即可 | 撤销点/执行点的时间顺序关键 |
| 争议重点 | 交易是否发生 | 是否在授权范围内执行 |
| 链上锚定 | 批量锚定 | 关键事件优先锚定 |
| 参与方长期关系 | 一次性 | 持续的委托关系管理 |
