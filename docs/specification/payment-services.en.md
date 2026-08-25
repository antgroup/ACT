# ACT 2.1 Payment Services Domain

[中文](payment-services.md) | English

> **Chinese source publication: ACT 2.1 Specification / Final / Normative**
> **Version baseline: 2026-08-11 (UTC+8).** This document is the official informative English translation of the normative ACT 2.1 PSD text. The terms **MUST**, **MUST NOT**, **SHOULD**, and **SHOULD NOT** preserve the corresponding requirement strengths from the Chinese publication. Product compatibility and conformance still require independent evidence.
> **Translation status: Official English translation / Informative. If a translation discrepancy is found, the Chinese ACT 2.1 publication remains controlling until the discrepancy is resolved through project governance.**

## 1. Scope and boundaries

The Payment Services Domain (PSD) describes payment-tool preparation, account isolation, payment-authorization checks, payment execution, result return, credential validation, and related state semantics after commercial confirmation.

This domain covers:

- payment-method binding and payment-tool references;
- Agent-dedicated sub-accounts and supporting verification capabilities;
- the INS/L1, DEL/L2, and AUP/L3 payment scenarios;
- A402 payment requirements, Proof, validation, and resource-recovery access;
- payment requests, results, states, errors, and cross-domain references.

This domain does not define merchant-internal inventory and fulfillment systems, underlying clearing networks, or PSP-internal risk and routing implementations. It also does not redefine Alipay onboarding, sandbox, or API operations.

Version and implementation boundaries:

1. This document is the versioned ACT 2.1 text in this release. The [Payment Services Domain](https://www.act-protocol.com/documentation/payment) on the ACT Protocol website is an unversioned informative reference.
2. `PSD-PAY-A402` is an independent access component that INS/L1, DEL/L2, and AUP/L3 can use.
3. Alipay channel fields, APIs, signatures, and sandbox flows belong only to the Alipay implementation layer and MUST NOT rewrite this specification.
4. The public package does not restore `specs/2.0`, legacy Schemas, or legacy examples. Wire details not defined by ACT 2.1 are non-normative implementation artifacts or future-version work.

## 2. Component overview

| Component | Type | Normative responsibility | Normative boundary |
|---|---|---|---|
| `PSD-PMT-BND` | Payment tool | Establish a restricted payment-tool reference and manage its valid state | A wallet-aggregation product is not equivalent to this entire component |
| `PSD-AGT-SUB` | Account isolation | Establish an optional Agent-dedicated sub-account and verification-key lifecycle | Optional; not required for AUP |
| `PSD-PAY-INS` | L1 scenario | Immediate payment with the user present and confirming each payment | May use A402, MCP, or API access |
| `PSD-PAY-DEL` | L2 scenario | Directed delegated payment for an explicitly identified subject | May use A402, MCP, or API access |
| `PSD-PAY-AUP` | L3 scenario | Autonomous delegated payment under a `BOUNDED` IAC | Defines authorization and payment semantics; access interactions are carried by A402 or another component |
| `PSD-PAY-A402` | Access protocol | HTTP 402, three Header types, payloads, state, idempotency, and error recovery | Independent component usable by INS, DEL, and AUP |

## 3. Core objects and cross-domain references

| Object or identifier | Normative semantics | Produced by / source | Primary consumer |
|---|---|---|---|
| Payment-tool reference | Restricted payment instrument that does not reveal raw account data; may be a token, sub-account identifier, or equivalent credential | `PSD-PMT-BND`, `PSD-AGT-SUB` | INS, DEL, AUP |
| Merchant order information | Merchant order number and necessary context correlating the transaction subject, amount, and payment handling | Commerce interaction or Seller Service | All three payment scenarios |
| Payment-capability negotiation result | Selected payment method, PSP, endpoint, and method Schema | `CID-PCA-NEG` or equivalent mechanism | A402, DEL, AUP, and INS when needed |
| IAC | Delegated-authorization boundary | `ADD-IAC-ISS` | DEL, AUP |
| `delegation_id` | Stable correlation for one delegated-authorization lifecycle | Authorization & Delegation Domain | DEL, AUP, later evidence |
| Payment request | Combination of transaction, tool, amount, time, unique request identifier, and integrity material | INS, DEL, AUP | PSP or payment acceptor |
| Payment result | PSP-provided transaction number, order correlation, state, and time | PSP | Buyer, merchant, later evidence |
| Payment requirement / Proof / validation result | Resource-payment requirement, payment evidence, and validation or recovery result | A402 and the payment method | Buyer, seller, PSP |

A conventional merchant-platform order flow connects commerce interaction and payment through a merchant order number. With A402, the seller MAY return order or resource identifiers such as `out_trade_no` and `resource_id` in `Payment-Needed`. ACT 2.1 does not require the three payment-scenario requests to carry a complete cart and does not define `Payment-Needed` as a complete `CID-CART-CFM` object.

## 4. `PSD-PMT-BND`: payment-method binding

### 4.1 Purpose and prerequisites

This component establishes a usable payment-tool reference for an Agent, allowing it to pay within authorization boundaries without directly holding the delegator's raw payment-account information.

Prerequisites:

- the delegator actively expresses the intention to enable payment for a specified Agent;
- the Agent has an identity that the account service provider or PSP can identify consistently;
- the provider can verify the delegator, generate a reference, manage the binding, and query its valid state.

### 4.2 Flow

1. The delegator actively initiates enablement and is redirected or connected to a trusted confirmation interface of the account service provider or PSP.
2. The provider verifies the delegator's identity and binding intent and displays the Agent and authorization scope to be bound.
3. After successful verification, the provider generates a payment token or equivalent reference bound to the real account, Agent identity, and limits such as validity, amount, and merchant scope.
4. Only the restricted reference is delivered to the Agent; raw account credentials are not delivered.
5. On every subsequent payment, the PSP rechecks the reference state and its binding to the initiating Agent.

Identity-verification failure, unregistered Agent identity, account or amount restrictions, and reference-generation failure MUST NOT produce a valid reference that can continue to payment. Later payment checks MUST detect expiration, freezing, closure, or identity mismatch.

### 4.3 Product boundary

Enablement, authorization, checking, and unbinding in the Alipay AI wallet form an aggregated product lifecycle. An Alipay integration MAY map relevant results to “payment tool ready,” but MUST NOT claim that the complete wallet product is identical to a `PSD-PMT-BND` protocol message.

## 5. `PSD-AGT-SUB`: Agent-dedicated sub-account

### 5.1 Purpose and prerequisites

This component provides account-level funds isolation for a highly autonomous Agent. It is an optional risk-control mechanism for DEL/AUP, not an A402 transport and not mandatory for every AUP implementation.

Prerequisites:

- the delegator actively requests a separate funds boundary for a specified Agent;
- the Agent has a stable, bindable identity;
- the PSP supports sub-account opening, funding or limits, freezing, unfreezing, closure, and state queries.

### 5.2 Management and key requirements

- A sub-account MUST bind the delegator, Agent identity, and current state.
- The delegator MAY fund it or set an available limit; the Agent can pay only within the available balance or limit.
- A payment MAY submit the sub-account identifier and authorization material generated by a dedicated key.
- The PSP MUST validate the sub-account state, Agent binding, and authorization material together.
- When the sub-account is frozen or closed, or the Agent identity becomes invalid, associated verification keys MUST become invalid as well.
- Keys SHOULD be generated and used in a protected environment. The relevant security capability determines the specific KMS or secure-execution implementation; PSD does not prescribe an algorithm or hardware.

Failure results MUST at least distinguish account-opening or state failure, insufficient balance or limit, binding mismatch, invalid authorization material, and invalidated keys. A failure MUST NOT bypass the main-account isolation boundary and continue debiting funds.

## 6. `PSD-PAY-INS`: instant payment / L1

### 6.1 Scenario and prerequisites

INS applies when the user is present in real time and decides on one payment. Its authorization basis is the user's confirmation for that payment, obtained by the PSP before funds processing; a pre-issued IAC is not required.

Before the flow begins:

- preflight commerce rules and cart confirmation have been completed and merchant order information is available; with A402, order or resource identifiers may instead be obtained from `Payment-Needed`;
- the Agent holds a valid payment-tool reference produced by `PSD-PMT-BND`;
- the PSP can validate the Agent, request integrity, and payment-tool reference and can provide a user-confirmation interface;
- when A402, MCP, or an API is used, the selected access approach has been determined.

The payment request uses the merchant order number and necessary payment facts such as amount and currency. A complete cart is not a payment-request field specified by this component. An implementation MUST NOT invent product-upload fields merely because the preceding flow included cart confirmation.

### 6.2 Five-step flow

1. **Payment preparation:** a conventional merchant-platform order flow obtains a merchant order number; an A402 flow obtains identifiers such as `out_trade_no` and `resource_id` from `Payment-Needed`.
2. **Construct and send the instant-payment request:** correlate at least a unique request identifier, merchant order, payment-tool reference, amount, currency, timestamp, Agent identity, and a signature over critical facts.
3. **PSP baseline validation:** check replay protection, freshness, Agent signature, tool state, and identity binding. On failure, user confirmation MUST NOT begin.
4. **Per-payment user confirmation:** display amount, currency, payee, and payment method. Identity and authorization confirmation for this payment MUST complete before funds processing. The PSP determines the concrete identity-verification method.
5. **Payment execution and state return:** the PSP debits or reserves funds, returns transaction number, order, state, and time to the buyer, and SHOULD also notify the merchant.

Resource access after payment is not a sixth INS payment step. With A402, the Buyer retries the original resource request with `Payment-Proof`, and the seller validates it before delivery. A conventional merchant-platform order flow fulfills according to its own interface rules.

### 6.3 Handling and error semantics

The amount, currency, order, and information displayed to the user MUST be consistent with the confirmed transaction. Error semantics SHOULD at least include:

| Category | Handling and recovery |
|---|---|
| Duplicate request | Do not replay payment directly; first query the existing result or start a new business request with a new request identifier |
| Expired request | Confirm that the transaction remains valid, then create new time context |
| Invalid Agent signature or integrity | Repair identity, key, or signature material before retrying |
| Invalid payment tool or identity mismatch | Rebind or choose another valid tool; do not open the confirmation interface |
| Amount or order differs from the confirmation result | Reconfirm the transaction; do not silently rewrite it |
| User cancellation, identity-verification failure, or timeout | Do not debit; product policy determines whether confirmation can be retried |
| Payment-execution failure or unknown result | Query the authoritative result first; a timeout MUST NOT directly create a second payment |

## 7. `PSD-PAY-DEL`: directed delegated payment / L2

### 7.1 Scenario and prerequisites

DEL expresses the L2 pattern in which a person first determines an explicit subject and the Agent executes. The user MAY be absent during execution and per-payment identity verification is not required. The authorization basis is an IAC that remains valid at execution time.

Prerequisites:

- the user has confirmed an explicit subject and an effective IAC has been issued;
- a merchant order and transaction confirmation exist;
- the Agent holds a payment-tool reference, or an available dedicated sub-account and authorization material;
- the A402, MCP, or API access approach has been selected;
- identity, connection, authorization, and key implementations support signatures, binding, and IAC validation.

### 7.2 Four-step flow

1. **Agent local preflight:** check IAC state and validity, per-payment and cumulative limits, merchant scope, payment method, and tool state. On failure, do not send a payment request.
2. **Construct the payment request:** correlate a unique request identifier, merchant order, complete IAC and `delegation_id`, amount and currency, payment tool, timestamp, Agent identity, and signature over critical fields.
3. **PSP authoritative authorization validation:** in order, check replay protection, Agent signature, IAC signature/state/delegate, financial constraints, necessary semantic constraints, and sub-account authorization material.
4. **Payment execution and state return:** after successful validation, debit or reserve funds and return transaction number, delegation identifier, order, state, and time. The Agent updates its local cumulative amount only from a successful PSP result. The PSP SHOULD also notify the merchant.

After payment, an A402 flow retries with Proof and validates before delivery; a conventional merchant-platform order flow fulfills according to its interface. The access flow does not change DEL's IAC authorization boundary.

### 7.3 Handling and error semantics

An Agent's local preflight cannot replace authoritative PSP validation. The PSP's cumulative-limit decision MUST use authoritative historical successful amounts.

In addition to INS errors, DEL retains at least these semantics:

| Category | Handling and recovery |
|---|---|
| IAC expired, revoked, or suspended | Do not retry directly; wait for restoration or obtain new authorization |
| Delegated Agent identity mismatch | Repair authorization or binding; do not blindly retry under another identity |
| Per-payment or cumulative amount exceeded | Adjust the transaction or obtain new authorization |
| Merchant or payment method outside authorization scope | Change the transaction approach or obtain new authorization |
| Insufficient balance | Add funds or choose another permitted payment tool before deciding whether to retry |
| Order or amount differs from confirmed snapshot | Reconfirm the transaction; do not silently reuse old authorization |
| Invalid sub-account or authorization material | Restore account or key state, or terminate the transaction |

## 8. `PSD-PAY-AUP`: autonomous delegated payment / L3

### 8.1 Scenario and prerequisites

AUP expresses goal-driven L3 autonomous decision and execution. The user confirms a task in advance and issues a `BOUNDED` IAC. The Agent MAY determine the counterparty, time, and execution path within the authorization boundary, and multiple payments MAY occur during one task lifecycle.

Prerequisites:

- a valid `BOUNDED` IAC is used; a `SPECIFIED` IAC does not form the authorization basis of this component;
- the Agent has decomposed the task, but the complete transaction subject need not be known initially;
- the Agent holds an available payment tool and uses a dedicated sub-account when needed;
- `CID-PCA-NEG` or equivalent negotiation has completed when dynamic selection is required;
- the normal path does not require real-time identity verification for every payment, but risk anomalies, ambiguous authorization, significant price changes, or near-limit conditions MAY pause and escalate to the user.

### 8.2 Five-step flow

1. The seller returns a payment requirement associated with a resource or service through A402, MCP, or an API.
2. The Agent performs a real-time self-check against the `BOUNDED` IAC, task state, cumulative budget, per-payment limit, counterparty, service category, payment method, and tool state.
3. After the self-check passes, the Agent submits a payment request containing the `BOUNDED` IAC, `delegation_id`, transaction identifier, amount and currency, tool, time, and signature material.
4. The PSP checks replay protection, Agent and IAC authorization, financial and semantic constraints, account state, and risk.
5. After validation passes, the PSP processes funds and returns a payment-authorization result credential, transaction number, delegation identifier, state, and time. The Agent updates its local cumulative amount only from a successful PSP result. The PSP SHOULD also notify the merchant.

After payment, the A402 flow handles Proof retry, seller validation, resource delivery, and fulfillment confirmation. A conventional merchant-platform order flow follows its interface rules. Payment, Proof validation, resource delivery, and fulfillment confirmation remain distinct facts.

The [A402 protocol](a402.en.md) defines access-layer Headers, baseline payloads, common states, and error categories. AUP does not redefine them.

### 8.3 Handling and error boundaries

AUP reuses DEL error semantics for an expired, revoked, or suspended IAC; identity mismatch; per-payment or cumulative amount violations; insufficient balance; and merchant-scope violations. A402 or the corresponding access approach defines access-specific errors such as Proof-validation failures. ACT 2.1 does not freeze AUP-specific machine error codes. An implementation MUST report the stage in which failure occurred and MUST NOT equate payment success with resource delivery.

## 9. Common security and processing invariants

1. Scenario authorization checks occur before funds processing.
2. Agent-local checks cannot replace authoritative PSP validation.
3. A unique request identifier, time window, and signature or equivalent integrity protection provide replay and tamper resistance.
4. Payment success, valid Proof, delivered resource, and confirmed fulfillment are distinct facts.
5. Payment-request retry, original-resource-request retry, and fulfillment-confirmation retry are different operations.
6. Selecting A402, MCP, or an API MUST NOT change the INS/DEL/AUP authorization level.
7. Raw account data, private keys, and complete Proof MUST NOT enter an untrusted Agent context, logs, or demo events.
8. If the authoritative payment result is unknown, query it first; do not automatically create a second payment because of a timeout.

## 10. A402 reference

When A402 is used, the scenario component supplies the [A402 access protocol](a402.en.md) with a completed authorization decision and payment-method context. A402 is responsible for:

- `402 Payment Required`;
- `Payment-Needed`, `Payment-Proof`, and optional `Payment-Validation`;
- `method_id` and method extensions;
- Proof validation, replay protection, original-request correlation, and resource release;
- common state, errors, timeouts, idempotency, and recovery semantics.

When MCP or an API is used, it MUST provide equivalent results and an explicit mapping to the common states. ACT 2.1 does not define a new message format for those interfaces.

## 11. Sources

- Related PSD website reference: [Payment Services Domain](https://www.act-protocol.com/documentation/payment); content not labeled ACT 2.1 is not a normative source for this release
- Higher-level reference: [Protocol Overview](https://www.act-protocol.com/documentation/overview)
- Alipay product facts: [AI metered-payment integration guide](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)
