# Agent Payment alignment

> Status: Preview / Non-normative  
> Public baseline: official Alipay wallet and payment Skill/CLI

## 1. Supported conference scope

The conference preview covers the public Skill/CLI route documented by Alipay. Other Agent platform SDKs or device integrations can be added later as separate Bindings without changing ACT Core.

## 2. ACT domain coverage

This product path composes ACT domains; it is not a PSD-only integration:

| ACT domain | Components used by the preview | Product/Profile relationship |
|---|---|---|
| ADD | `ADD-INT-ICS` | The host Agent captures and presents the current payment intent. IAC issuance and lifecycle are future delegated-payment work. |
| CID | `CID-MER-CAT`, `CID-INT-XFR`, `CID-PCA-NEG`, `CID-CART-CFM` | The host commerce flow supplies the product, merchant, order and payment-capability context consumed by the payment Skill. |
| PSD | `PSD-PMT-BND`, `PSD-PAY-INS`, candidate `PSD-PAY-A402` | User-present payment is the scenario baseline; A402 is the candidate access protocol. Alipay wallet onboarding remains a product lifecycle rather than being wholly standardized by `PSD-PMT-BND`. |
| TSD | Primarily `TSD-ATT-EVT`; other trust services depend on the deployment | ACT records may link intent, order, payment and fulfillment evidence. Alipay product records are evidence inputs, not automatic TSD conformance. |

When Agent Payment consumes an HTTP 402 requirement, the 402 interaction skeleton and the authorization/execution level must remain distinct. The v2.1 revision direction models the preview as `PSD-PAY-INS` referencing candidate `PSD-PAY-A402`; the public specification must be published before this becomes a normative conformance claim. See [two-sided capability-to-domain mapping](../mappings/domains.md#3-买方-agent-支付能力映射).

## 3. Developer journey alignment

| Stage | Public product behavior | Source | ACT working semantic | Layer | Dependency/status | Validation |
|---|---|---|---|---|---|---|
| Install | Install official Agent Payment capabilities | AP-SRC-001, 003, 004 | Capability installation | Skill/CLI Binding | `PUBLIC-FACT` | Clean-environment install |
| Wallet check | Agent may check wallet access during standalone onboarding or diagnosis; payment commands handle readiness during actual payment | AP-SRC-003, 004 | Capability availability | Profile + Binding | `PUBLIC-FACT`; discovery model `PROTOCOL-PENDING` | CLI result fixtures + live check |
| Wallet application | Agent requests wallet activation when needed | AP-SRC-003, 004 | Wallet authorization request | Profile | `PUBLIC-FACT`; Core ownership `PROTOCOL-PENDING` | Official flow |
| User authorization | User opens the Alipay authorization flow and authenticates | AP-SRC-003 | Human authorization | Product UI | `PUBLIC-FACT` | User test account |
| Agent binding | Agent submits the user-provided binding instruction | AP-SRC-003, 004 | Authorization binding | Profile + Binding | `PUBLIC-FACT` | Official flow |
| Payment detection | Agent recognizes an Alipay cashier link or HTTP 402 requirement | AP-SRC-004, 006, 010 | Payment requirement detection | Skill/CLI or HTTP Binding | `PUBLIC-FACT`; common message `PROTOCOL-PENDING` | Positive and negative fixtures |
| Intent presentation | Agent presents the payment target, amount and context before payment | AP-SRC-002, 004 | Payment intent / human confirmation | ACT Core + Profile | L1 Candidate mapped | UX and audit assertion |
| Cashier payment | Official payment capability handles a supported cashier link | AP-SRC-004, 010 | Payment execution | Skill/CLI Binding | `PUBLIC-FACT` | Official test path |
| HTTP 402 payment | Official payment capability handles `Payment-Needed` and returns/reuses proof | AP-SRC-004, 006 | Requirement acceptance and proof acquisition | Core + Profile + Binding | `PUBLIC-FACT`; A402 Candidate mapped | Optional end-to-end sandbox |
| Status query | Agent queries payment status rather than assuming success | AP-SRC-004 | Payment outcome query | Profile + Binding | `PUBLIC-FACT`; Candidate recovery mapped | Pending/success/failure cases |
| Task resume | Agent resumes the original task only after a verified payment outcome | AP-SRC-004, 006 | Continuation / next action | ACT Core | A402 Candidate mapped | End-to-end scenario |
| Reauthorization | Missing or invalid wallet access routes back to wallet authorization | AP-SRC-003, 004 | Recovery action | Core + Profile | `PUBLIC-FACT`; Candidate recovery + Profile extension | Expired/unbound case |
| Close/unbind | User or Agent closes the wallet relationship through the supported product flow | AP-SRC-003, 004 | Authorization revocation | Profile | `PUBLIC-FACT`; lifecycle ownership `PROTOCOL-PENDING` | Official flow if testable |

## 4. Binding boundary

The Skill/CLI Binding is responsible for:

- invoking the official wallet and payment capability;
- preserving the original paid-resource request when processing HTTP 402;
- passing product inputs without inventing values;
- treating official command output as the product result;
- returning structured status to the Agent runtime.

It is not responsible for:

- defining ACT payment semantics;
- fabricating user authorization or payment success;
- storing merchant private keys for the paid-resource provider;
- redefining Alipay wallet lifecycle rules.

## 5. Minimum Agent behavior for the preview

An Agent integration shown at the conference must:

1. use the official public installation path;
2. use the official payment command's wallet-readiness result, without inserting a standalone wallet check before every payment;
3. obtain user authorization through the official flow when required;
4. present a comprehensible payment intent;
5. distinguish pending, successful and failed outcomes;
6. never report payment success from a local mock;
7. preserve enough context to continue the original paid-resource request;
8. avoid logging binding secrets, credentials or complete payment proofs.

## 6. Protocol handoff to the ACT owner

The protocol revision needs to decide:

- whether wallet authorization is in Core or an optional payment-method extension;
- the minimum payment-intent object required before execution;
- how a Skill/CLI capability declares compatibility and supported payment modes;
- the common outcome envelope used by Skill, MCP and HTTP Bindings;
- the representation of `valid_next_actions` for authorize, retry, query and abort;
- how authorization revocation affects in-flight payments.
- the final identifier, version, common state machine and backward-compatibility rules for candidate `PSD-PAY-A402`.

Until those decisions are accepted, the terms in this document are working semantics only.
