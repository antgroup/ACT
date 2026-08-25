# ACT 2.1 Authorization & Delegation Domain

[中文](authorization-delegation.md) | English

> **Chinese source publication: ACT 2.1 Specification / Final / Normative**
> **The protocol content is final. Conformance with this specification requires independent conformance evidence.**
> **Version baseline: 2026-08-11 (UTC+8).**
> **Translation status: Official English translation / Informative. If a translation discrepancy is found, the Chinese ACT 2.1 publication remains controlling until the discrepancy is resolved through project governance.**

The Authorization & Delegation Domain (ADD) specifies the expression, confirmation, and structured constraints of user intent, the issuance of authorization credentials, and their lifecycle management. It provides an expressive, constrained, verifiable, and traceable authorization foundation for an Agent acting on behalf of a user in commercial activities.

This document is the official informative English translation of the normative ACT 2.1 Authorization & Delegation Domain text in this release. The [ACT Protocol Authorization & Delegation page](https://www.act-protocol.com/documentation/delegation) is an unversioned informative reference.

## 1. Scope and boundaries

ADD covers:

- capture, clarification, confirmation, and structured expression of the user's original intent;
- creation and referencing of an Intent Structured Result (ISR);
- construction, issuance, and packaging of an Intent Authorization Credential (IAC);
- IAC lifecycle states, state transitions, and validity checks.

ADD does not specify front-end presentation, prompt engineering, model reasoning, or multimodal recognition algorithms. It also does not specify the internal implementation of identity infrastructure, private-key custody, or signing services. Product discovery and transaction confirmation belong to CID; payment and funds processing belong to PSD; evidence event structures and governance belong to TSD.

## 2. Components and core objects

| Component | Purpose | Primary output |
|---|---|---|
| `ADD-INT-ICS` | Capture, clarify, confirm, and structure user intent | Original user intent, ISR, `intent_id` |
| `ADD-IAC-ISS` | Select authorization boundaries from the final ISR, normalize, sign, and package them | IAC, `delegation_id` |
| `ADD-IAC-LCM` | Manage active, suspended, resumed, revoked, and expired IAC states | Queryable authorization state |

| Object or identifier | Normative semantics | Downstream use |
|---|---|---|
| Original user intent | The original commercial intent expressed by the user through natural language or another modality | ADD processing and necessary retrospective review |
| `intent_id` | Identifier spanning intent confirmation, ISR, and cross-domain flows | CID, PSD, TSD |
| ISR | Structured rule expression of the user's goals, constraints, and boundaries | IAC issuance and CID rule validation |
| IAC | Verifiable packaging of authorization boundaries | PSD DEL/AUP and TSD |
| `delegation_id` | Unique identifier for one IAC and its lifecycle | LCM, PSD, TSD |
| Authorization state | Whether the IAC can currently be accepted | CID, PSD, and other verifiers |

## 3. `ADD-INT-ICS`: intent capture and structured expression

### 3.1 Original user intent

`conversation_history` carries the user's original content, or a verifiable digest and contextual reference to that content:

| Field | Presence | Normative semantics |
|---|---|---|
| `user_intent_raw` | Conditionally required | At least one of `user_intent_raw` and `user_intent_raw_digest` MUST be present |
| `user_intent_raw_digest` | Conditionally required | Digest of the original intent; at least one of this field and `user_intent_raw` MUST be present |
| `input_mode` | Optional | `TEXT`, `VOICE`, `IMAGE`, `INTERACTIVE_CARD`, or `OTHER`; values may be combined |
| `context_ref` | Conditionally required | Required when a digest is present; the referenced content MUST reproduce the same digest |

Additional input modes MUST NOT change the basic semantics of existing fields. When the complete original content cannot be transferred, only the digest and reference MAY be transferred, but the implementation MUST still protect the verifiability, access control, and retention period of the original record.

### 3.2 ISR data dictionary

ACT 2.1 defines ISR as a data dictionary, not a frozen wire schema. It specifies names, types, and semantics, but does not assign uniform presence requirements to every field in this table. Scenario rules, IAC issuance rules, and downstream components apply further constraints.

| Field | Normative semantics |
|---|---|
| `conversation_history` | Original user-intent object |
| `intent_id` | Identifier unique within the current intent chain |
| `delegation_mode` | `SPECIFIED` or `BOUNDED` |
| `validity_start_time` / `validity_end_time` | ISO 8601 UTC validity window; the end MUST be later than the start |
| `max_total_amount` / `currency` | Maximum total authorized amount and ISO 4217 currency |
| `allowed_payment_methods` | Permitted payment methods |
| `agent_id` | Identifier of the executing Agent |
| `user_confirmation_method` / `user_confirmation_timestamp` | User confirmation method and time |
| `ext` | Namespaces for standard and private extensions |

`SPECIFIED` applies when the target, merchant, or transaction boundary is explicit. `BOUNDED` applies when the user specifies a task goal and behavioral boundaries while allowing the Agent to make concrete choices within those boundaries.

### 3.3 Standard extensions

| Extension block | Fields |
|---|---|
| `ext.commerce` | `max_single_amount`, `min_single_amount`, `allowed_categories`, `forbidden_categories`, `allowed_merchants`, `forbidden_merchants` |
| `ext.agent_behavior` | `price_deviation_tolerance`, `price_deviation_action`, `on_payment_failure`, `max_retry_count` |
| `ext.fulfillment` | `delivery_time_requirement`, `delivery_address` |

`price_deviation_action` uses `PAUSE_AND_NOTIFY` or `AUTO_CANCEL`. `on_payment_failure` uses `AUTO_RETRY` or `CANCEL`. `ext.vendor_private` MAY carry private extensions, but MUST NOT change the semantics of core fields or standard extensions. Unrecognized private fields that do not affect core constraints MAY be ignored.

### 3.4 Processing requirements

1. The user-side Agent captures the original intent and forms `conversation_history`.
2. The Agent creates an ISR draft. If it encounters ambiguity, missing critical constraints, or conflicts, it clarifies them and updates the draft.
3. The Agent presents the primary goals and boundaries in a form the user can understand and creates the final ISR after obtaining confirmation.
4. When a downstream IAC is needed, `ADD-IAC-ISS` uses the final ISR as its input basis.
5. The original intent, or a verifiable reference to it, SHOULD be retained under access control for a reasonable dispute period. The implementation determines the exact duration and medium according to applicable legal and governance requirements.

## 4. `ADD-IAC-ISS`: Intent Authorization Credential issuance

### 4.1 Issuance boundary

An IAC is not an indiscriminate copy of the final ISR. Only content that forms the authorization boundary, execution constraints, and basis for downstream verification enters the payload to be signed. A single user confirmation of the final ISR MAY directly trigger issuance; the workflow SHOULD NOT require the user to reconfirm the same matter solely because of process design.

Before issuance, the delegated Agent, delegation mode, validity period, and principal constraints MUST already be explicit. The signing private key MUST be held by a controlled key-management capability and used within a trusted execution environment or an equivalently controlled environment. Business applications MUST NOT hold the issuance private key in plaintext.

### 4.2 IAC payload to be signed

| Field | Presence | Normative semantics |
|---|---|---|
| `delegation_id` | Required | Unique identifier for the IAC and authorization lifecycle |
| `intent_id` | Optional | Correlates the IAC with the upstream ISR |
| `conversation_history` | Conditionally required | Used when no `intent_id` is present and the original-intent object is carried directly |
| `delegator_identity` | Required | Identifier of the delegator or the subject issuing on the delegator's behalf |
| `agent_id` | Required | Identifier of the Agent authorized to act |
| `delegation_mode` | Optional | `SPECIFIED` / `BOUNDED`; defaults to `SPECIFIED` |
| `validity_start_time` / `validity_end_time` | Required | ISO 8601 UTC authorization window |
| `max_total_amount` | Required | Maximum total authorized amount |
| `currency` | Optional | ISO 4217; defaults to `CNY` |
| `allowed_payment_methods` | Optional | Retains ISR semantics when included in the signed scope |
| `user_confirmation_method` / `user_confirmation_timestamp` | Optional / conditionally required | User confirmation method and time |
| `source_isr_digest` | Optional | Digest of the upstream ISR or an agreed digest scope |
| `ext` | Optional | ISR extension constraints that affect authorization verification |

Whether an `ext` field is included in the signed scope depends on whether it affects downstream authorization verification. The IAC is not required to sign every ISR extension field.

### 4.3 Final IAC and signatures

The final IAC MAY consist of `protected_header`, `credential_metadata`, `credential_subject`, `proof`, `status_reference`, and, in high-risk scenarios, an optional `control_proof_ref`. The source specification defines the semantic boundaries of these parts but does not yet freeze a final field-level envelope.

Before signing, the agreed signing scope MUST be deterministically canonicalized. JSON payloads SHOULD use RFC 8785 JCS. Issuers and verifiers in the same deployment MUST use consistent field names, canonicalization rules, and signing-input boundaries. Implementations MAY map the IAC to a verifiable-credential envelope, a JWS-style envelope, or an equivalent representation. W3C VC-JWT is one recommended approach, not the only allowed format.

## 5. `ADD-IAC-LCM`: lifecycle management

### 5.1 States and transitions

| State | Semantics | Recoverability |
|---|---|---|
| `Active` | Within the validity window and neither suspended nor revoked; available for downstream use | — |
| `Suspended` | Temporarily unavailable | MAY return to `Active` |
| `Revoked` | Permanently revoked | Terminal |
| `Expired` | `validity_end_time` has been reached | Terminal |

Allowed transitions are `Active → Suspended`, `Suspended → Active`, `Active/Suspended → Revoked`, and `Active/Suspended → Expired`. `Revoked` and `Expired` MUST NOT return to another state.

### 5.2 State handling and validation

- A `Suspended`, `Revoked`, or `Expired` IAC MUST NOT continue to be used for commerce interaction, payment execution, or authorization validation.
- Suspension, resumption, revocation, and expiration SHOULD be reported asynchronously as `act:delegation:delegation-suspended`, `delegation-resumed`, `delegation-revoked`, and `delegation-expired`. TSD defines the event structure.
- A processor that references an IAC MUST at least check the validity window, confirm that the current state is `Active`, and check for known suspension, revocation, or expiration results.
- Before making a final decision, the processor MUST obtain the current state through `status_reference`. If the state service is temporarily unavailable, the latest locally successful result and `validity_end_time` MAY be used for temporary risk control, but this is not a basis for permanently omitting state checks.

## 6. Current machine-contract boundary

ACT 2.1 defines the data dictionaries, presence requirements, and processing semantics, but does not publish an ISR/IAC JSON Schema, envelope version, algorithm suite, state-query protocol, event Schema, or standard error object. This repository does not invent those machine contracts from examples or descriptive text.

## 7. Sources

- Related ADD website reference: [Authorization & Delegation Domain](https://www.act-protocol.com/documentation/delegation); content not labeled ACT 2.1 is not a normative source for this release
- Cross-domain scenarios: [Scenarios and business flows](https://www.act-protocol.com/documentation/scenarios)
- CID: [Commerce Interaction Domain](https://www.act-protocol.com/documentation/commerce)
- PSD: [Payment Services Domain](https://www.act-protocol.com/documentation/payment)
- TSD: [Trust Services Domain](https://www.act-protocol.com/documentation/trust)
