# ACT 2.1 Commerce-to-Payment Connection Rules

[中文](commerce-payment-negotiation.md) | English

> **Status: ACT 2.1 / Final / Non-normative cross-domain guide**
> This guide summarizes the connection between the Commerce Interaction Domain and Payment Services Domain without adding normative semantics. See the complete [Commerce Interaction Domain](../../docs/specification/commerce-interaction.en.md) and [Payment Services Domain](../../docs/specification/payment-services.en.md); those domain specifications control if this guide differs.
> **Translation status: Official English translation / Informative. If a translation discrepancy is found, the Chinese ACT 2.1 publication remains controlling until the translation is corrected in a subsequent repository release.**

## 1. Purpose

`CID-PCA-NEG` determines the mutually usable payment method and access information before the parties enter payment interaction. The Payment Services Domain treats this component, or an equivalent mechanism, as a prerequisite for A402 and allows INS, DEL, and AUP to select Skill, A402, a conventional merchant-platform order-and-pay flow, or the corresponding MCP/OpenAPI interface.

The negotiation result in the source documentation covers at least:

| Field | Normative meaning | ACT 2.1 status |
|---|---|---|
| `method_id` | Identifier of the selected payment method | Semantics are final; non-normative repository artifacts use a stable namespaced ID and a separate `method_version` |
| `psp_id` | Identifier of the selected payment service provider | CID semantics are defined; ACT 2.1 does not define cross-organization registration or conflict resolution |
| `endpoint` | Subsequent payment or method endpoint | CID requires source and consistency checks; ACT 2.1 does not define wire rules for authentication, redirection, or reachability |
| `method_schema_url` | Description of the method payload structure | CID requires consistency checks; ACT 2.1 does not define wire rules for integrity, caching, or versioning |

These fields belong to ACT 2.1 semantics. They do not mean that an Alipay product payload must contain properties with the same names.

## 2. Relationship to A402

The flow is:

```text
Commerce context and transaction conditions
→ CID-PCA-NEG (or equivalent mechanism)
→ select method_id / PSP / endpoint / method schema
→ INS, DEL, or AUP completes scenario authorization checks
→ A402 or the corresponding interface provides payment access
```

A402 uses the negotiation result to interpret method-specific payloads and select a PSP or verification endpoint. It is not responsible for:

- product or service discovery;
- user-intent generation;
- cart or transaction-condition confirmation;
- INS/L1 user confirmation;
- DEL/L2 or AUP/L3 IAC boundaries.

## 3. `Payment-Needed` and transaction confirmation

ACT 2.1 defines the minimum correlation for two access paths:

- a conventional merchant-platform order-and-pay flow uses a merchant order number;
- an A402 flow returns order or resource identifiers such as `out_trade_no` and `resource_id` in `Payment-Needed`.

The protocol does not require a payment request to carry the complete cart and does not define `Payment-Needed` as a complete `CID-CART-CFM` object. The repository's non-normative A402 artifacts establish minimum commerce correlation through `out_trade_no`, `resource_id`, `amount`, and `currency`, and allow `commerce_confirmation` to reference an independent confirmation object. If the order, resource, or amount changes, a new payment requirement MUST be created; an old bill MUST NOT be silently rewritten.

## 4. External commerce protocols are not merged into ACT

The Payment Services Domain does not define fields from external commerce protocols. This document does not copy rules from external protocols such as UTP and does not add external-protocol fields to ACT Core.

## 5. Capability-declaration security

- Before using `act-payment-capability.json`, the implementation MUST verify that it came from the merchant-declared `capability_url`.
- When parsing `supported_methods`, the implementation SHOULD check consistency among `psp_id`, `endpoint`, and `method_schema_url` to prevent forgery, tampering, or substitution.
- If the source cannot be verified or a critical-field check fails, capability matching and payment MUST NOT continue.

Capability declarations use the standard field names `psp_id`, `endpoint`, and `method_schema_url`; there is no second set of fields without underscores.

## 6. ACT 2.1 machine-contract boundary

ACT 2.1 does not define:

- a formal JSON Schema, version, or signed scope for capability declarations and negotiation requests;
- cross-organization registration, conflict resolution, or a long-lived discovery service for `method_id` and `psp_id`;
- ranking, selection, or fallback among multiple PSPs or methods;
- authentication, redirection, integrity, or caching rules for `endpoint` and `method_schema_url`;
- versioning and signing rules for a formal CID confirmation object;
- whether automatic renegotiation is allowed after negotiation expires or a method becomes unavailable.

Together, these limitations define the boundary of payment-capability negotiation. Implementations MUST NOT infer undefined wire fields from examples.

## 7. Sources

- Related CID website reference: [Commerce Interaction Domain](https://www.act-protocol.com/documentation/commerce); content not labeled ACT 2.1 is not a normative source for this release
- Related PSD website reference: [Payment Services Domain](https://www.act-protocol.com/documentation/payment); content not labeled ACT 2.1 is not a normative source for this release
- Cross-domain reference: [Protocol Overview](https://www.act-protocol.com/documentation/overview)
