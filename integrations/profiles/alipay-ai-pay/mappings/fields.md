# Working field mapping

> Status: Preview / Non-normative  
> Warning: ACT 2.1 now has a Candidate A402 Core Schema, but the working object paths below are semantic mapping labels rather than literal Core paths. Alipay wire fields still follow the official product guide.

## 1. `Payment-Needed`

| ACT working path | Alipay field | Product meaning | Layer | Status/question |
|---|---|---|---|---|
| `payment_requirement.id` | `protocol.out_trade_no` | Provider merchant order number | Core mapping + Profile | `PUBLIC-FACT` |
| `payment_requirement.amount.value` | `protocol.amount` | Amount requested | Core mapping + Profile | Unit/format `PRODUCT-REVIEW` |
| `payment_requirement.amount.currency` | `protocol.currency` | Payment currency | Core mapping + Profile | `PUBLIC-FACT` |
| `payment_requirement.resource.id` | `protocol.resource_id` | Paid resource identifier | Core mapping + Profile | `PUBLIC-FACT` |
| `payment_requirement.expires_at` | `protocol.pay_before` | Payment deadline | Core mapping + Profile | Time format/clock rules need tests |
| `payment_requirement.integrity.signature` | `protocol.seller_signature` | Provider bill signature | Alipay Profile | `PUBLIC-FACT` |
| `payment_requirement.integrity.algorithm` | `protocol.seller_sign_type` | Alipay signing algorithm, currently RSA2 in the documented path | Alipay Profile | `PUBLIC-FACT` |
| `payment_requirement.payee.product_id` | `protocol.seller_unique_id` | Product-specific payee identity | Alipay Profile | Relationship to seller ID `PRODUCT-REVIEW` |
| `payment_requirement.payee.display_name` | `method.seller_name` | Provider display name | Profile extension | `PUBLIC-FACT` |
| `payment_requirement.payee.merchant_id` | `method.seller_id` | Alipay merchant identity | Alipay Profile | `PUBLIC-FACT` |
| `payment_requirement.payee.app_id` | `method.seller_app_id` | Alipay application identity | Alipay Profile | Third-party authorization relation `PRODUCT-REVIEW` |
| `payment_requirement.description` | `method.goods_name` | Paid item/resource description | Profile extension | `PUBLIC-FACT` |
| `payment_requirement.payee.id_type` | `method.seller_unique_id_key` | Meaning of the unique identity field | Alipay Profile | Allowed values need public confirmation |
| `payment_requirement.service.id` | `method.service_id` | Registered AI Pay service | Alipay Profile | `PUBLIC-FACT` |

The `protocol` and `method` envelope is now also an ACT 2.1 Candidate protocol fact. The fields in this table remain Alipay product serialization: their placement and requiredness are not automatically inherited by the provider-neutral [A402 Candidate Schema](../../../../specs/2.1/a402/schemas/README.md). The Profile must explicitly adapt between the two contracts.

The executable evidence boundary and fields that remain outside the product payload are defined by the [A402 Candidate / Alipay Product Adapter](a402-candidate-adapter.md).

## 2. `Payment-Proof`

| ACT working path | Alipay field | Product meaning | Layer | Status/question |
|---|---|---|---|---|
| `payment_proof.proof` | `protocol.payment_proof` | Product-issued payment proof | Core mapping + Profile | Length/format `PUBLIC-FACT`; confidentiality rules pending |
| `payment_proof.transaction_id` | `protocol.trade_no` | Alipay transaction number | Core mapping + Profile | Format `PUBLIC-FACT` |
| `payment_proof.client_context` | `method.client_session` | Product client session/context | Profile extension | Optionality `PRODUCT-REVIEW` |

## 3. Payment verification API

### Request

| ACT working input | Alipay API parameter | Status |
|---|---|---|
| `payment_proof.transaction_id` | `trade_no` | `PUBLIC-FACT` |
| `payment_proof.proof` | `payment_proof` | `PUBLIC-FACT` |
| `payment_proof.client_context` | `client_session` | Requirement conditions `PRODUCT-REVIEW` |

### Response

| ACT working result | Alipay response field | Required provider check |
|---|---|---|
| `verification.transaction_id` | `trade_no` | Matches the presented proof/expected transaction |
| `verification.amount.value` | `amount` | Exactly matches the stored original bill |
| `verification.resource.id` | `resource_id` | Exactly matches the requested resource |
| `verification.active` | `active` | Must be true before delivery |
| `verification.payment_requirement_id` | `out_trade_no` | Exactly matches the stored original bill |

An API success code alone is not a successful ACT verification result.

The API result maps to ACT `Payment-Validation` semantics. The current Alipay guide does not define a buyer-visible `Payment-Validation` Header, so this Profile must not emit or require that Header unless a future public product version documents it.

## 4. Fulfillment confirmation API

| ACT working field | Alipay API field | Status/question |
|---|---|---|
| `fulfillment.payment_transaction_id` | `trade_no` | `PUBLIC-FACT` |
| `fulfillment.id` | no documented direct field | Profile/application correlation extension |
| `fulfillment.resource_id` | no documented direct field | Provider correlates through stored verified payment |
| `fulfillment.status` | no documented direct field in the current request | Failure/partial delivery semantics `PRODUCT-REVIEW` |
| `fulfillment.idempotency_key` | no documented direct field | Implementation/Profile responsibility pending |

## 5. Encoding and authorization questions

| ID | Question | Blocking artifact |
|---|---|---|
| FM-001 | Is every amount a decimal CNY major-unit string, despite wording that may imply minimum units? | Profile Schema and monetary tests |
| FM-002 | ACT Candidate requires Base64URL, while the current Alipay guide describes `Payment-Proof` as Base64; which encoding is accepted by every public Alipay client? | Product Profile compatibility tests |
| FM-003 | When is `client_session` required? | Verification client and error recovery |
| FM-004 | How does third-party `app_auth_token` relate to `seller_app_id` and merchant identity? | Platform/ISV profile extension |
| FM-005 | What are the allowed `seller_unique_id_key` values? | Profile validation |
| FM-006 | What canonical timestamp and skew rules apply to `pay_before`? | Expiration conformance tests |
