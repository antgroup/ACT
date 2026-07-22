# Alipay AI Pay Profile

> Status: Preview / Non-normative  
> Profile version: `0.1-working-draft`  
> Product source snapshot: 2026-07-22
> Compatible ACT version: pending ACT Core 2.1 revision

This directory records how the public Alipay AI Pay products relate to ACT working semantics. It is an alignment workspace for the July Preview, not a published ACT Product Profile.

支付宝产品不是 ACT 的第五个域。Agent 支付赋予买方 Agent 支付能力，AI 按量付费赋予卖方服务接受机器支付的能力；二者是同一机器支付闭环的两侧，通过 Product Profile 组合 ADD、CID、PSD、TSD 的语义。先阅读[双侧能力与 ACT 四域映射](domain-mapping.md)。

ACT v2.1 修订方向将支付场景与接入协议解耦：大会首期按 L1 `PSD-PAY-INS` + 候选 `PSD-PAY-A402` + 官方 Skill/CLI Binding + Alipay AI Pay Profile 组织。A402 尚未进入公开正式规范，因此这里只表达候选映射，不构成规范性声明。

## Scope

The first preview covers one end-to-end machine-payment loop with two public integration sides:

| Capability side | Participant | Public integration baseline | Main ACT coverage |
|---|---|---|---|
| Agent Payment | Buyer Agent | Official Alipay wallet and payment Skill/CLI | ADD intent; CID transaction context; PSD INS scenario + candidate A402; TSD evidence |
| AI Metered Payment | Paid resource provider | HTTP 402, `Payment-Needed`, `Payment-Proof`, payment verification and fulfillment confirmation | CID resource/capability/transaction; candidate PSD A402 and verification; TSD payment/fulfillment evidence |

The two capability sides form one payment loop:

```mermaid
sequenceDiagram
    participant Agent as Buyer Agent
    participant Resource as Paid Resource
    participant Alipay as Alipay AI Pay

    Agent->>Resource: Request resource
    Resource-->>Agent: 402 + Payment-Needed
    Agent->>Alipay: User-authorized payment via official Skill
    Alipay-->>Agent: Payment-Proof
    Agent->>Resource: Retry original request with proof
    Resource->>Alipay: Verify proof
    Alipay-->>Resource: Payment facts
    Resource-->>Agent: Deliver resource
    Resource->>Alipay: Confirm fulfillment
```

## Documents

| Document | Purpose |
|---|---|
| [End-to-end capability contract](end-to-end-capability-contract.md) | Working contract for buyer Agent payment, seller machine-payment and end-to-end evidence |
| [Two-sided capability-to-domain mapping](domain-mapping.md) | Primary map from buyer Agent payment and seller machine-payment capabilities to ADD, CID, PSD and TSD |
| [Official sources](official-sources.md) | Public product sources and snapshot policy |
| [2026-07-21 product fact audit](product-fact-audit-2026-07-21.md) | Checked public facts, discrepancies and validation gaps |
| [2026-07-21 Skill/CLI behavior audit](skill-cli-behavior-audit-2026-07-21.md) | Real public buyer workflow, command boundary and validation gaps |
| [Agent Payment alignment](agent-payment-alignment.md) | Wallet, Skill/CLI and buyer payment path |
| [Metered Payment alignment](metered-payment-alignment.md) | HTTP 402 provider path |
| [Field mapping](field-mapping.md) | Working ACT-to-Alipay field mapping |
| [Lifecycle mapping](lifecycle-mapping.md) | Product events and working ACT states |
| [Error mapping](error-mapping.md) | Product errors and candidate recovery actions |

## Layer boundary

| Layer | Owns | Must not own |
|---|---|---|
| ACT Core | Cross-product meaning, lifecycle, verification responsibility, recovery semantics | Alipay API names, merchant identifiers, RSA2 details |
| Alipay AI Pay Profile | Product fields, API calls, Skill/CLI capabilities, signatures and product error mapping | Redefinition of Core semantics |
| Binding | HTTP Header or Skill/CLI packaging and transport behavior | Product onboarding policy |
| Official product documentation | Onboarding, credentials, sandbox operation and current product procedures | ACT protocol definitions |

## Status labels

| Label | Meaning |
|---|---|
| `PUBLIC-FACT` | Directly supported by a public Alipay source |
| `PRODUCT-REVIEW` | Interpretation of public material that needs Alipay product confirmation |
| `PROTOCOL-PENDING` | Depends on the ACT Core revision led by the protocol owner |
| `VALIDATION-PENDING` | Must be verified with the official sandbox or Skill/CLI |

## Compatibility statement

An implementation cannot claim conformance to this working draft. Conference release conformance will require:

1. a reviewed ACT Core candidate;
2. a versioned Alipay AI Pay Profile;
3. a declared Binding;
4. successful profile tests using the official public integration path.

During the July Preview, use the three scoped working claims in the [end-to-end capability contract](end-to-end-capability-contract.md#9-分级验收声明) instead of a general ACT conformance claim.
