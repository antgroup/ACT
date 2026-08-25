# ACT 2.1 Specification Overview

[中文](overview.md) | English

> **Source status: ACT 2.1 / Final**
> **Translation status: Official English translation / Informative. If a translation discrepancy is found, the Chinese ACT 2.1 publication remains controlling until the discrepancy is resolved through project governance.**

ACT (Agentic Commerce Trust Protocol) defines the authorization, transaction, payment, and trust-coordination semantics for commercial activities involving agents. ACT 2.1 contains four capability domains connected into complete business flows through cross-domain components.

## Normative language

The Chinese ACT 2.1 publication uses the following requirement strengths. Every domain specification and cross-domain connection rule is interpreted according to this table:

| Chinese source term | Requirement strength | English equivalent |
|---|---|---|
| 应, 必须 | mandatory | `MUST` |
| 不应, 不得 | prohibited | `MUST NOT` |
| 宜 | recommended | `SHOULD` |
| 不宜 | discouraged | `SHOULD NOT` |
| 可, 可以 | optional | `MAY` |

For field presence, “required” means the field MUST be present with a valid value; “conditionally required” means it MUST be present with a valid value when the stated condition holds; and “optional” means it MAY be present and, when present, MUST have a valid value. Uppercase normative terms in this translation preserve the requirement strength of the Chinese versioned publication. If a translation discrepancy is found, the Chinese publication controls.

## 1. Four capability domains

| Domain | Responsibility | Specification |
|---|---|---|
| ADD | Express user intent and issue and manage authorization credentials that an Agent can execute | [Authorization & Delegation Domain](authorization-delegation.en.md) |
| CID | Discover goods or services, transfer intent, negotiate payment capabilities, and confirm transactions | [Commerce Interaction Domain](commerce-interaction.en.md) |
| PSD | Manage payment tools, authorization levels, payment execution, validation, state, and error recovery | [Payment Services Domain](payment-services.en.md) |
| TSD | Provide trustworthy evidence and trust associations for cross-domain facts | [Trust Services Domain](trust-services.en.md) |

The [scenario guide](../flows/scenarios.en.md) explains how the four domains compose. If a scenario description conflicts with a domain specification, the corresponding domain specification controls.

## 2. Payment Services components

| Type | Component | Meaning |
|---|---|---|
| Payment tool | `PSD-PMT-BND` | Establish a restricted payment-tool reference so the Agent does not handle raw account credentials |
| Account isolation | `PSD-AGT-SUB` | Provide an optional dedicated sub-account and lifecycle management for an Agent |
| L1 | `PSD-PAY-INS` | The user is present and completes per-payment identity and authorization confirmation before funds are processed |
| L2 | `PSD-PAY-DEL` | The transaction intent, including goods, merchant, and amount, is explicit, and the Agent pays automatically within the authorization boundary |
| L3 | `PSD-PAY-AUP` | The Agent autonomously selects and pays within task, budget, and policy boundaries |
| Payment access | `PSD-PAY-A402` | Use HTTP 402 to exchange payment requirements, payment proof, and validation results |

L1, L2, and L3 answer *why the Agent is authorized to pay*. A402 answers *how payment requirements and proof are exchanged*. A402 can be used by all three authorization levels and is not itself an authorization level.

## 3. Basic A402 flow

```text
Buyer Agent → Paid Service: request resource
Paid Service → Buyer Agent: 402 + Payment-Needed
Buyer Agent → Payment Service: authorized payment
Payment Service → Buyer Agent: payment result / proof
Buyer Agent → Paid Service: retry original request + Payment-Proof
Paid Service → Payment Service: verify proof
Paid Service → Buyer Agent: deliver resource
```

See the [A402 payment access protocol](a402.en.md) for the complete requirements. See [CID–PSD negotiation](commerce-payment-negotiation.en.md) for the connection rules between commerce interaction and payment.

## 4. Protocol and implementation boundary

- `docs/specification/` defines ACT 2.1.
- `code/schemas/` provides JSON Schemas, fixtures, and test-support artifacts.
- `integrations/` connects ACT to specific products.
- `code/samples/` and `code/web-client/` demonstrate implementation approaches and business flows.

Machine-readable artifacts, product code, and demos MUST NOT add or modify protocol requirements. Alipay fields, APIs, signing, onboarding, and sandbox behavior are governed by the [official AIPay materials](https://aipay.alipay.com/callpay) and are not part of the ACT specification.

## 5. Developer entry points

| Goal | Entry point |
|---|---|
| Understand A402 locally | [Local A402 Sample](../../code/samples/local-a402/README.md) |
| Run the interactive demo | [Machine Payment Showcase](../../code/web-client/alipay-ai-pay-showcase/README.md) |
| Integrate Alipay buyer capabilities | [Alipay Buyer Agent](../../integrations/alipay/buyer-agent/README.md) |
| Integrate an Alipay seller | [Alipay Seller Java](../../integrations/alipay/seller-java/README.md) |
| Validate an Alipay sandbox flow | [Alipay Validation](../../integrations/alipay/validation/README.md) |

Return to the [documentation index](../README.md).
