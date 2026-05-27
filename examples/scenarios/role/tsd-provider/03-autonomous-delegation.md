# 场景三：信任服务提供商视角 - 自主委托 A2A 支付

## 场景描述

作为信任服务提供商（TSD），我在自主委托 A2A 场景中提供多智能体间的身份互信建立、复杂交易链条的可信存证、以及 A2A 协作争议的调解服务。重点建立适合智能体协作的可计算信任框架。

## 角色定位

- **我是**：信任服务提供商（Trust Services Provider, TSD）
- **服务对象**：A2A 生态中的多智能体网络（买方智能体、多个卖方智能体、PSP）
- **核心能力**：A2A 智能体身份互信、多跳交易存证、A2A 协作存证、复杂争议处理
- **功能定位**：多智能体协作的信任基础设施和可计算信任评估者

## A2A 场景下的信任挑战

```
┌────────────────────────────────────────────────────────────────┐
│                   A2A 多智能体协作的信任问题                    │
│                                                                │
│  问题1: 陌生智能体间的初始信任                                  │
│    买方智能体: "我从没和这个卖方智能体交易过，能信任它吗？"      │
│    → 需要: 基于历史存证的声誉评估 + DID 身份验证               │
│                                                                │
│  问题2: 多跳交易的可追溯性                                      │
│    用户: "我委托买机票，出问题了，是航司问题还是酒店问题？"      │
│    → 需要: 任务拆解-执行-支付-履约的完整关联存证链             │
│                                                                │
│  问题3: 支付-履约分离的担保需求                                 │
│    买方智能体: "钱付了，卖方不履约怎么办？"                     │
│    卖方智能体: "履约了，买方不付款怎么办？"                     │
│    → 需要: 支付担保机制 + 资金托管存证                         │
│                                                                │
│  问题4: 自主决策的可审计性                                      │
│    用户: "智能体花光了我的预算买了不必要的东西"                 │
│    → 需要: 决策过程的全量存证，可回溯智能体的决策链            │
│                                                                │
│  问题5: 跨智能体的责任归属                                      │
│    任务链: 买方A → 卖方B → 第三方C (外包)→ 失败               │
│    → 需要: 多参与方事件关联图谱，责任可界定                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## 我的核心职责

### 1. A2A 智能体身份与声誉管理

#### 1.1 智能体身份注册与验证
- 为参与 A2A 的智能体建立/验证 `did:act` 身份
- 验证智能体的服务声明和能力声明真实性
- 维护智能体身份的激活/吊销状态

#### 1.2 可计算声誉评估
基于历史存证数据，提供智能体声誉评估：

```json
{
  "agent_reputation": {
    "agent_did": "did:act:seller-flight-001",

    "overall_score": 4.8,
    "confidence": 0.95,
    "last_updated": "2024-01-15T10:00:00Z",

    "dimensions": {
      "fulfillment_rate": {
        "score": 0.98,
        "total_transactions": 5000,
        "successful_fulfillments": 4900
      },
      "dispute_rate": {
        "score": 0.99,
        "total_disputes": 2,
        "resolved_in_favor": 2
      },
      "response_time": {
        "score": 0.95,
        "avg_response_ms": 150
      },
      "payment_honesty": {
        "score": 1.0,
        "payment_failures": 0
      }
    },

    "attestation_chain": [
      "att-anchor-2024-01-01",
      "att-anchor-2024-01-15"
    ]
  }
}
```

#### 1.3 声誉查询服务
买方智能体在 A2A 发现阶段可查询卖方声誉：

```
请求: GET /tsd/v1/reputation/{did:act:seller-xxx}

响应: 声誉评分、历史统计、置信度
```

### 2. 自主委托 IAC 特殊存证

自主委托（`delegation_mode: BOUNDED`）IAC 的增强存证：

```json
{
  "event_type": "add_iac_issued_bounded",
  "iac_id": "iac-bounded-2024-001",

  "bounded_authorization": {
    "mode": "BOUNDED",
    "budget_limit": "5000.00",
    "currency": "CNY",

    "task_scope": {
      "description": "出差安排",
      "subtask_categories": ["flight", "hotel", "transport"],
      "excluded_categories": ["entertainment", "shopping"]
    },

    "decision_constraints": {
      "max_subtask_count": 10,
      "single_subtask_limit": "3000.00",
      "requires_all_subtasks": false
    },

    "reporting": {
      "report_frequency": "per_completion",
      "user_notification": "async_summary"
    }
  },

  "principal_confirmations": {
    "intent_confirmation": "2024-01-01T10:00:00Z",
    "boundary_acknowledged": true,
    "risk_acknowledged": true
  },

  "tsd_attestation": "..."
}
```

### 3. 任务拆解与执行关联存证

#### 3.1 任务规划存证
买方智能体将复杂任务拆解时的记录：

```json
{
  "event_type": "complex_task_decomposition",
  "task_id": "task-2024-001-business-trip",
  "parent_iac": "iac-bounded-2024-001",
  "principal_did": "did:act:principal-001",
  "buyer_agent_did": "did:act:buyer-agent-001",

  "decomposition": {
    "original_goal": "安排下周出差，预算5000元",
    "subtasks": [
      {
        "subtask_id": "st-001",
        "type": "flight",
        "description": "北京-上海往返机票",
        "allocated_budget": "2000.00",
        "depends_on": []
      },
      {
        "subtask_id": "st-002",
        "type": "hotel",
        "description": "上海酒店预订2晚",
        "allocated_budget": "1500.00",
        "depends_on": ["st-001"]
      },
      {
        "subtask_id": "st-003",
        "type": "transport",
        "description": "接送机用车",
        "allocated_budget": "500.00",
        "depends_on": ["st-001"]
      }
    ],
    "total_allocated": "4000.00",
    "contingency_reserve": "1000.00"
  },

  "decomposition_timestamp": "2024-01-08T09:00:00Z"
}
```

#### 3.2 子任务执行链存证
每个子任务的完整生命周期关联存证：

```
Task: 安排出差 (task-2024-001-business-trip)
│
├── Subtask: st-001 机票预订
│   ├── 1. 服务发现
│   │      存证: 发现卖方智能体 S1, S2, S3
│   │      存证: 查询S1声誉评分 4.8, S2评分 4.5, S3评分 4.2
│   │
│   ├── 2. 支付能力协商 (存证: TSD-EVT-CID-PCA)
│   │      买方A ←→ 卖方S1: 支付方式匹配成功
│   │
│   ├── 3. 交易确认 (存证: TSD-EVT-CID-CART-CFM)
│   │      商品: CA1234航班，价格 ¥1999
│   │
│   ├── 4. HTTP 402支付诉求 (存证: 诉求内容哈希)
│   │      卖方S1返回支付诉求
│   │
│   ├── 5. A2A支付执行 (存证: TSD-EVT-PSD-PAY-A2A)
│   │      - 支付请求
│   │      - 子账户扣款
│   │      - 支付凭证生成
│   │
│   ├── 6. 支付凭证传递 (存证: 凭证传递记录)
│   │
│   ├── 7. 履约验证 (存证: TSD-EVT-MER-FULFILL)
│   │      卖方S1: 出票完成，票号 999-1234567890
│   │
│   └── 8. 结果上报 (存证: 子任务完成)
│          预算消耗: 1999/2000, 剩余: 1
│
├── Subtask: st-002 酒店预订 (依赖st-001完成)
│   ├── ... (类似存证链)
│   └── 存证: 完成, 预算消耗 1200/1500
│
└── Subtask: st-003 用车预订 (依赖st-001完成)
    ├── ... (类似存证链)
    └── 存证: 完成, 预算消耗 300/500

总结存证: 任务完成报告
- 总预算: 5000
- 实际消耗: 3499 (1999+1200+300)
- 剩余: 1501 (含备用金1000)
```

### 4. A2A 支付凭证的可信验证

#### 4.1 凭证验证服务
为卖方智能体提供支付凭证的可信验证：

```
POST /tsd/v1/a2a/verify-payment-proof
{
  "payment_proof": {
    "claim_id": "claim-flight-20240115-001",
    "transaction_id": "txn-psp-abc123",
    "buyer_agent": "did:act:buyer-agent-001"
  },
  "verification_requester": "did:act:seller-flight-001"
}

响应:
{
  "verified": true,
  "verification_timestamp": "2024-01-15T10:05:00Z",
  "payment_status": "settled",
  "settled_amount": "1999.00",
  "iacs_referenced": ["iac-bounded-2024-001"],
  "verification_chain": [
    {"type": "signature", "result": "valid"},
    {"type": "psp_confirm", "result": "confirmed"},
    {"type": "iac_scope", "result": "within_bounds"}
  ],
  "tsd_attestation": "sig-tsd..."
}
```

#### 4.2 凭证防重放验证
确保同一支付凭证不被重复使用：

```
凭证使用记录:
- claim-flight-20240115-001: 已验证1次 (2024-01-15T10:00:00)
- claim-hotel-20240115-002: 已验证1次 (2024-01-15T11:30:00)
- claim-flight-20240115-001: 重复验证尝试被拒绝
```

### 5. 支付-履约分离的担保机制存证

#### 5.1 担保支付存证
当采用担保模式时的特殊存证：

```json
{
  "event_type": "a2a_guaranteed_payment",
  "guarantee_id": "guar-2024-001",

  "payment_phases": {
    "phase1_commit": {
      "status": "funds_frozen",
      "amount": "1999.00",
      "frozen_at": "2024-01-15T10:00:00Z",
      "freeze_expiry": "2024-01-22T10:00:00Z"
    },
    "phase2_fulfillment": {
      "delivery_confirmed": true,
      "confirmed_at": "2024-01-15T10:05:00Z",
      "confirmation_method": "ticket_delivered"
    },
    "phase3_release": {
      "status": "funds_released",
      "released_at": "2024-01-15T10:06:00Z",
      "released_to": "did:act:seller-flight-001"
    }
  },

  "dispute_window": {
    "open_until": "2024-01-22T10:00:00Z",
    "dispute_submitted": null
  }
}
```

### 6. 复杂争议处理（`TSD-ATT-DSP`）

#### 6.1 A2A 多参与方争议

**场景**：用户说"智能体花了冤枉钱"，质疑某子任务交易的必要性

**TSD 的争议处理流程**：

```
Phase 1: 争议提交
├── 委托人提交争议申诉 (存证)
├── 争议类型: BUDGET_MISUSE
├── 质疑对象: 子任务 st-004 (某餐厅预订 ¥800)
└── 存证: 争议案件号 disp-2024-001

Phase 2: 证据收集
├── 调取 IAC 内容 (自主委托授权范围)
├── 调取任务拆解规划 (st-004是否在规划中)
│   发现: 原规划中无此子任务
├── 调取买方智能体决策过程存证
│   发现: 智能体自主添加，理由是"用户可能喜欢"
└── 调取交易流水凭证

Phase 3: 裁决分析
├── IAC 授权: 预算5000，品类排除"entertainment"
├── 争议交易: 餐厅预订属于可接受品类
├── 但: 超出用户预期的"任务边界"理解
└── 裁决: 部分支持 - 智能体应事前明确沟通

Phase 4: 结果执行
├── 退款: 卖方餐厅部分退款 ¥600 (存证)
├── 买方智能体: 信用分调整 (存证)
├── 委托人: 通知处理结果
└── 存证: 争议结案 disp-2024-001-CLOSED
```

#### 6.2 智能体决策透明化

为争议处理提供决策溯源存证：

```json
{
  "event_type": "agent_decision_trace",
  "decision_id": "dec-20240115-add-restaurant",
  "buyer_agent": "did:act:buyer-agent-001",

  "decision_context": {
    "trigger": "hotel_booking_completed",
    "trigger_timestamp": "2024-01-15T11:00:00Z",
    "remaining_budget": "1501.00"
  },

  "reasoning_chain": [
    {
      "step": 1,
      "observation": "hotel_near_restaurant_district",
      "inference": "dining_options_available"
    },
    {
      "step": 2,
      "observation": "budget_remaining_1500",
      "inference": "sufficient_for_quality_meal"
    },
    {
      "step": 3,
      "llm_reasoning": "User may appreciate a nice dinner after travel",
      "confidence": 0.7
    },
    {
      "step": 4,
      "decision": "add_dining_subtask",
      "estimated_cost": "800.00"
    }
  ],

  "decision_outcome": {
    "action": "initiated_restaurant_search",
    "executed": true,
    "user_notified": "delayed_in_summary"
  }
}
```

### 7. 智能体协作的可信存证网络

#### 7.1 多智能体存证协调
当任务涉及的多方都上报存证时，构建关联图谱：

```
交易网络存证图谱:

节点:
- N1: 委托人 (did:act:principal-001)
- N2: 买方智能体 (did:act:buyer-agent-001)
- N3: 航司卖方智能体 (did:act:seller-flight-001)
- N4: 酒店卖方智能体 (did:act:seller-hotel-001)
- N5: PSP (did:act:psp-001)
- N6: TSD 存证锚点 (att-anchor-2024-01-15)

边 (存证事件关联):
- E1: N1 --授权--> N2 (IAC存证)
- E2: N2 --发起支付--> N3 (A2A支付存证)
- E3: N2 --发起支付--> N4 (A2A支付存证)
- E4: N3 --收款确认--> N5 (PSP通知存证)
- E5: N4 --收款确认--> N5 (PSP通知存证)
- E6: N1,N2,N3,N4,N5 --共同锚定--> N6 (链上锚定)
```

#### 7.2 可信时间线重建
争议时根据多方存证重建时间线：

```
时间线重建 (争议: st-004 超预算)

T+00:00 买方智能体: 任务拆解规划 (存证)
T+00:30 买方智能体: 开始执行st-001机票
...
T+02:00 买方智能体: st-001完成, 预算余3001
T+02:05 买方智能体: 自主决策添加餐厅 (决策存证)
         └─ LLM推理: "用户可能喜欢"
T+02:10 买方智能体: 发现餐厅卖方S4 (市场发现存证)
T+02:15 卖方S4: 返回报价 ¥800 (报价存证)
         ⚠️ 此时累计将超: 已用2000+1200+300+800 = 4300 > 原规划4000
T+02:16 买方智能体: 规则自检通过 (IAC总预算5000, 未超) (自检存证)
T+02:20 买方智能体: 发起A2A支付 (支付存证)
T+02:25 PSP: 扣款成功 (支付成功存证)
T+02:30 卖方S4: 履约完成 (履约存证)

========= 裁决依据 =========
- 未超IAC总预算: 符合
- 自主决策未事前告知用户: 有争议空间
- 决策过程有存证: 可审查
```

### 8. 智能体信用累积与跨平台共享

基于 TSD 存证，支持智能体信用的跨平台流动：

```json
{
  "portable_reputation": {
    "agent_did": "did:act:buyer-agent-001",
    "reputation_bundle": {
      "transaction_count": 150,
      "fulfillment_score": 4.9,
      "dispute_resolution_score": 4.8,

      "historical_attestations": [
        "att-anchor-2024-01-01",
        "att-anchor-2024-02-01"
      ],

      "issuing_tsd": "did:act:tsd-provider-001",
      "bundle_signature": "sig-tsd-001...",
      "expiry": "2024-04-01T00:00:00Z"
    }
  }
}
```

新的 A2A 平台可以验证并承认智能体的跨平台声誉。

## 与场景一/二的差异总结

| 维度 | 即时支付 | 定向委托 | 自主委托 A2A |
|------|---------|---------|-------------|
| 参与方数 | 3-4方 | 3-4方，固定 | 多方，动态变化 |
| 交易复杂度 | 单次，简单 | 多笔，有序列 | 多笔，网状依赖 |
| 存证关联 | 单事件链 | 账户关联 | 任务图关联 |
| 争议类型 | 交易执行 | 授权边界 | 决策合理性+执行+多跳 |
| 信任重点 | 不可否认性 | 授权合规性 | 协作可信度+声誉 |
| TSD 服务 | 存证+验证 | 存证+验证+审计 | 存证+验证+审计+声誉+复杂争议 |

## 面向未来的扩展

- **智能体声誉的 NFT 化**：将高声誉分数 token 化，可交易或抵押
- **预测性信任评估**：基于存证数据训练模型，预测智能体的履约概率
- **智能体间信任联盟**：高信任智能体形成联盟，简化内部验证流程
