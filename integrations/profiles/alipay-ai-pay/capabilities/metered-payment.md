# AI Metered Payment alignment

> Status: Preview / Non-normative  
> Public baseline: Alipay HTTP 402 provider integration

## 1. ACT domain coverage

The provider path consumes ADD context and directly implements responsibilities across CID, PSD and TSD:

| ACT domain | Components used by the preview | Product/Profile relationship |
|---|---|---|
| ADD | Upstream `ADD-INT-ICS`; future IAC components | The buyer Agent owns user intent and delegation. The paid resource does not issue user authorization. |
| CID | `CID-MER-CAT`, `CID-INT-XFR`, `CID-PCA-NEG`, `CID-CART-CFM` | The provider describes the resource and binds the payment requirement to a resource, price, order and supported payment method. |
| PSD | Candidate `PSD-PAY-A402` | The v2.1 direction separates the A402 access protocol from INS/DEL/AUP scenarios. The Alipay Profile supplies `Payment-Needed`, `Payment-Proof`, RSA2 and verification/fulfillment APIs. |
| TSD | Primarily `TSD-ATT-EVT`; other trust services depend on the deployment | Payment and fulfillment evidence can feed ACT events; the product callback itself is not automatically a TSD attestation. |

The relationship between `Payment-Needed` and `CID-CART-CFM`, and between the fulfillment API and TSD events, remains protocol-pending. See [two-sided capability-to-domain mapping](../mappings/domains.md#4-卖方机器支付能力映射).

## 2. Provider journey alignment

| Stage | Public product behavior | Source | ACT working semantic | Layer | Dependency/status | Validation |
|---|---|---|---|---|---|---|
| Product onboarding | Provider opens the product and registers/configures the paid service using the official process | AP-SRC-001, 005, 006 | Product enrollment | Official product docs | `PUBLIC-FACT` | Link and account check |
| Resource request | Agent sends the original request to the paid resource | AP-SRC-006 | Resource invocation | Application + Binding | `PUBLIC-FACT` | HTTP fixture |
| Payment required | Provider returns HTTP 402 with `Payment-Needed` | AP-SRC-005, 006 | Payment Requirement | Core + HTTP Binding + Profile | `PUBLIC-FACT`; `CANDIDATE-MAPPED` | 402 contract fixture |
| Bill encoding | Provider encodes the product bill for the Header | AP-SRC-006 | Requirement serialization | HTTP Binding + Profile | `PUBLIC-FACT`; encoding detail `PRODUCT-REVIEW` | Decode/round-trip test |
| Bill signature | Provider signs the documented field set with RSA2 | AP-SRC-006 | Requirement integrity | Alipay Profile | `PUBLIC-FACT` | Official sample and negative tests |
| Agent payment | Buyer Agent uses the official payment capability | AP-SRC-003, 004, 006 | Payment execution | Agent Payment Profile | `PUBLIC-FACT` | Official Skill/CLI |
| Request retry | Agent retries the original request with `Payment-Proof` | AP-SRC-004, 006 | Proof presentation | Core + HTTP Binding + Profile | `PUBLIC-FACT`; Candidate fingerprint/idempotency mapped | Local contract + optional sandbox |
| Proof extraction | Provider decodes and validates the proof envelope before API verification | AP-SRC-006 | Proof parsing | HTTP Binding + Profile | `PUBLIC-FACT`; exact encoding `PRODUCT-REVIEW` | Invalid encoding fixtures |
| Product verification | Provider calls `alipay.aipay.agent.payment.verify` | AP-SRC-006, 007 | Proof verification | Alipay Profile | `PUBLIC-FACT` | Sandbox API |
| Business validation | Provider matches active status, amount, order and resource against the original bill | AP-SRC-006, 007 | Verification policy | Core responsibility + Profile mapping | `PUBLIC-FACT`; `CANDIDATE-MAPPED` | Mismatch tests |
| Replay prevention | Provider prevents one trade from producing repeated fulfillment | AP-SRC-006 | Proof replay prevention | Core security + implementation | `PUBLIC-FACT`; retention details `PRODUCT-REVIEW` | Concurrent replay test |
| Resource delivery | Provider returns the paid resource only after successful verification | AP-SRC-006 | Fulfillment | ACT Core/application | `PUBLIC-FACT`; Candidate phase boundary mapped | Local + optional sandbox |
| Fulfillment confirmation | Provider calls `alipay.aipay.agent.fulfillment.confirm` | AP-SRC-006, 008 | Fulfillment Receipt | Core + Alipay Profile | `PUBLIC-FACT`; Product relationship `PRODUCT-REVIEW` | Optional sandbox API |
| Recovery | Provider returns a retryable or terminal result without delivering on invalid proof | AP-SRC-006—008 | Protocol Error + next actions | Core + Profile | Candidate error contract mapped | Error matrix tests |

## 3. Provider responsibilities

For the conference preview, the paid-resource provider must demonstrate that it:

- creates a unique merchant order and resource identifier;
- uses the official product format and signing rules for `Payment-Needed`;
- treats `Payment-Proof` as untrusted input until verified;
- calls the official verification API;
- matches the verified facts to the stored original bill;
- prevents concurrent and repeated fulfillment for one payment;
- delivers only the requested resource;
- calls the official fulfillment confirmation API after delivery;
- handles retryable platform errors without fabricating a result;
- does not expose private keys or full proofs in logs.

## 4. API, MCP Tool and Skill boundary

The paid resource may be presented as an API, MCP Tool or Skill. In the conference scope:

- HTTP 402 is the product payment baseline.
- An MCP Tool or Skill may invoke or expose a resource protected by this flow.
- ACT does not claim a separate native MCP payment transport unless a public product specification exists.
- Resource-specific input and output remain application concerns; payment requirement, proof and fulfillment semantics belong to ACT/Profile.

## 5. Protocol handoff to the ACT owner

The protocol revision needs to decide:

- the minimum product-neutral Payment Requirement;
- the minimum Payment Proof and whether verification is a separate message;
- the canonical lifecycle from requirement to fulfillment;
- idempotency keys and replay-prevention responsibilities;
- how synchronous resource delivery relates to an asynchronous fulfillment event;
- the common error envelope and `valid_next_actions`;
- which fields are Core and which may be Profile extensions.
- whether `Payment-Needed` is or references the `CID-CART-CFM` transaction confirmation result;
- how product fulfillment confirmation maps to PSD receipts and independent TSD events.
