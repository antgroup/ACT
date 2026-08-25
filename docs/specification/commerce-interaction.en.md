# ACT 2.1 Commerce Interaction Domain

[中文](commerce-interaction.md) | English

> **Chinese source publication: ACT 2.1 Specification / Final / Normative**
> **The protocol content is final. Conformance with this specification requires independent conformance evidence.**
> **Version baseline: 2026-08-11 (UTC+8).**
> **Translation status: Official English translation / Informative. If a translation discrepancy is found, the Chinese ACT 2.1 publication remains controlling until the discrepancy is resolved through project governance.**

The Commerce Interaction Domain (CID) specifies the commercial-interaction semantics that precede payment execution: how goods or services become machine-readable candidates, how intent context is transferred, how the parties align payment capabilities, and how a transaction is finally confirmed before entering the Payment Services Domain.

This document is the official informative English translation of the normative ACT 2.1 Commerce Interaction Domain text in this release. The [ACT Protocol Commerce Interaction page](https://www.act-protocol.com/documentation/commerce) is an unversioned informative reference.

## 1. Scope and boundaries

CID covers:

- minimum information requirements for product and service discovery results;
- organization and transfer of intent context and return of candidate results;
- declaration, confirmation, and negotiation of payment capabilities;
- cart confirmation, preflight rule validation, and transaction-confirmation results;
- objects, state semantics, and cross-domain references needed for commercial consensus before payment.

CID does not specify:

- an Agent's internal reasoning, ranking, preference inference, or decision algorithms;
- a merchant's internal operations, inventory deduction, order management, or fulfillment implementation;
- general multi-Agent collaboration, task orchestration, or service-discovery protocols;
- payment execution, credential validation, or funds processing, which belong to the [Payment Services Domain](payment-services.en.md);
- common structures and governance for trustworthy events, which belong to the Trust Services Domain.

## 2. Components and core objects

| Component | Purpose | Primary output |
|---|---|---|
| `CID-MER-CAT` | Product and service catalog interface; specifies minimum discovery-result information without defining one catalog protocol | Candidate product or service results |
| `CID-INT-XFR` | Transfer the current task's intent context to a merchant or platform and receive candidates | Request-correlated candidate results or errors |
| `CID-PCA-NEG` | Align payment methods, providers, endpoints, and payload modes before payment | Payment-capability negotiation result |
| `CID-CART-CFM` | Finally confirm the transaction subject, amount, fulfillment terms, and authorization constraints | Transaction-confirmation result that PSD can reference |

The domain uses four core object types:

| Object | Produced by | Primarily used by |
|---|---|---|
| Intent context | `ADD-INT-ICS`, or locally constructed by the Buyer Agent from upstream intent | `CID-INT-XFR`, `CID-CART-CFM`, and candidate matching |
| Candidate product or service result | `CID-MER-CAT`, `CID-INT-XFR` | Local buyer decision and `CID-CART-CFM` |
| Payment-capability negotiation result | `CID-PCA-NEG` | Payment-request construction and path selection |
| Transaction-confirmation result | `CID-CART-CFM` | PSD and subsequent evidence and dispute handling |

ADD provides ISR and related constraint context to CID. PSD consumes the transaction-confirmation result, order transaction number, and payment-capability negotiation result. TSD maintains event types and evidence-governance rules; CID does not redefine them.

## 3. `CID-MER-CAT`: product and service catalog interface

### 3.1 Minimum information requirements

Each product or service detail that a Buyer Agent can consume MUST contain:

- a product or service identifier uniquely resolvable globally or within the merchant domain;
- a product or service name;
- a category or classification usable for matching intent constraints;
- an explicit listed price and currency unit.

The result SHOULD additionally contain:

- inventory, saleability, or service-availability state;
- price-expiration time or quote-update time;
- delivery, fulfillment, or service-completion time;
- merchant identifier, merchant-reference URL, or detail-reference URL.

A result that does not satisfy the minimum information requirements SHOULD NOT directly enter `CID-CART-CFM`. If the result can only be displayed, the implementation SHOULD first obtain the information needed for preflight rule validation.

### 3.2 Content intentionally not standardized

ACT 2.1 does not specify a common catalog path, HTTP method, authentication, pagination, retrieval ranking, recommendation algorithm, or merchant-internal product model. Implementations MAY reuse an industry protocol, merchant API, or platform catalog, provided that the result satisfies the minimum information requirements above.

## 4. `CID-INT-XFR`: intent-context transfer

### 4.1 Intent context

Intent context is organized around the current task and commonly includes:

- purchase or service requirements explicitly expressed by the user;
- supplemental requirements inferred by the Agent from confirmed context;
- constraints such as amount, category, merchant, and fulfillment timing;
- background strictly necessary for candidate matching;
- preference information that the implementation permits and that is applicable.

Explicit requirements and constraints SHOULD be primary. Implicit requirements or preferences MUST NOT conflict with user-confirmed constraints or ISR/IAC authorization boundaries. The implementation is responsible for informed consent and data protection.

### 4.2 Requests, responses, and updates

A request SHOULD include a unique request identifier, intent context, necessary cross-domain correlation identifiers, constraints, response-format requirements, and source-authentication information. The response MUST be correlatable to the original request and MUST at least return candidate details that can be filtered and confirmed. If the request cannot be processed, the response MUST return machine-recognizable error semantics.

Each multi-turn update MUST receive a new request identifier and correlate to the preceding request. It SHOULD carry only changes from the current turn. Error semantics SHOULD cover malformed input, no matches, restricted access, constraint conflicts, and excessive request frequency. The Buyer Agent MAY use these errors to retry, switch merchants, adjust the request, or notify the user.

The Buyer Agent MAY query multiple merchants or platforms concurrently. Candidate aggregation, comparison, and final decision remain local implementation concerns and are not CID protocol rules.

## 5. `CID-PCA-NEG`: payment-capability negotiation

### 5.1 Capability declaration

A seller, merchant, or its Agent MAY declare payment-negotiation capabilities under an Agent Card `capabilities` node, or publish `act-payment-capability.json` at an agreed location. The declaration MUST express:

- negotiation mode;
- supported payment methods;
- the payment service provider for each method;
- payment-interface endpoints;
- payload mode or structure description.

An Agent Card MAY use `capability_url` to reference a one-way capability declaration, or `negotiation_endpoint` to reference a two-way negotiation interface. The source documentation provides structural examples; it does not provide a JSON Schema, version-negotiation mechanism, or signature format that can independently establish formal compatibility.

### 5.2 One-way declaration

The Buyer Agent reads the seller's published capabilities and filters `supported_methods` for methods that satisfy the transaction conditions and upstream authorization constraints. The selected result MUST at least identify:

- `method_id`: payment-method identifier;
- `psp_id`: payment service provider identifier;
- `endpoint`: endpoint for the subsequent payment request;
- `method_schema_url`: description of the method payload structure.

If no method matches, the Buyer Agent MUST NOT proceed to payment.

### 5.3 Two-way negotiation

The Buyer Agent sends a request to `negotiation_endpoint`. The request semantics include the Buyer Agent identifier, buyer-supported methods, currency, and estimated amount. The seller returns the method, PSP, endpoint, and method Schema that match the current transaction conditions.

If the parties share no method, the Buyer Agent MUST NOT proceed to payment and MUST switch methods, switch counterparties, or terminate the transaction according to business policy. When multiple results exist, final ranking and selection are handled locally by the Buyer Agent.

### 5.4 Security requirements

Before using a capability declaration, the Buyer Agent MUST verify that it came from the capability address declared by the merchant. When parsing the result, it MUST check consistency among critical fields such as `psp_id`, `endpoint`, and `method_schema_url` to prevent forgery, tampering, or substitution. If the source cannot be verified or a critical-field check fails, capability matching and payment MUST NOT continue.

## 6. `CID-CART-CFM`: cart confirmation

### 6.1 Preflight rule validation

Before payment, the Buyer Agent MUST validate the proposed transaction against:

- per-transaction and cumulative amount boundaries;
- allowed and forbidden categories;
- allowed and forbidden merchants;
- delivery, completion, or service-fulfillment timing;
- whether the final price is within the permitted tolerance;
- ISR/IAC authorization boundaries in delegated-payment scenarios.

If any validation fails, the transaction MUST NOT proceed directly to payment. If an out-of-bounds policy already exists, that policy MUST be applied. `PAUSE_AND_NOTIFY` waits for the user to reconfirm or adjust constraints; `AUTO_CANCEL` records the reason and terminates. If there is no explicit policy, the implementation SHOULD pause and notify by default.

### 6.2 Submission, locking, and result

After validation passes, the confirmation request SHOULD include product or service details, final price, currency, fulfillment requirements, and necessary correlation context. After accepting, the counterparty MUST lock the order-level price, inventory, or service capacity and return a stably referenceable order transaction number. If locking fails, the counterparty MUST return an explicit failure and MUST NOT treat the transaction as confirmed.

The transaction-confirmation result SHOULD at least contain:

- confirmed product or service details;
- final amount and currency;
- counterparty identifier;
- order transaction number;
- confirmation time;
- necessary cross-domain correlation identifiers.

This does not require the payment request to contain the entire cart. A402 establishes minimum correlation through order, resource, amount, and currency, and MAY reference a separate confirmation object through `commerce_confirmation`. See the [commerce-to-payment connection rules](commerce-payment-negotiation.en.md).

## 7. Current machine-contract boundary

Two-way negotiation requests use `currency`; responses and the “no common method” decision use `supported_methods`. `amount_currency` and `matched_methods` are not ACT 2.1 field names.

This document consistently uses the existing field names `capability_url`, `psp_id`, and `method_schema_url`. Spellings without underscores are not additional wire fields. ACT 2.1 does not publish the corresponding JSON Schema, version negotiation, signature, authentication, redirect, or cache rules. Implementations MUST NOT expand examples into additional normative requirements.

The source mentions `act:commerce:decision-logged` and `act:commerce:cart-confirmed` as event identifiers that later evidence may reference. Event structure and governance remain part of TSD.

## 8. Sources

- Related CID website reference: [Commerce Interaction Domain](https://www.act-protocol.com/documentation/commerce); content not labeled ACT 2.1 is not a normative source for this release
- Related PSD website reference: [Payment Services Domain](https://www.act-protocol.com/documentation/payment); content not labeled ACT 2.1 is not a normative source for this release
- Cross-domain reference: [Protocol Overview](https://www.act-protocol.com/documentation/overview)
