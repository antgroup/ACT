# Working error and recovery mapping

> Status: Preview / Non-normative  
> Product error names come from public Alipay API documentation. ACT Core error categories, retryability and `valid_next_actions` are defined by the 2.1 Candidate; this file maps product observations without redefining them.

本页的机器可读来源是 [`error-mapping.preview.json`](../schemas/error-mapping.preview.json)。仓库检查会验证每个产品错误都引用 [`error-catalog.json`](../../../../specs/2.1/a402/schemas/error-catalog.json) 中存在的 Core Candidate 错误 ID；本页仅提供阅读说明。

## 1. Candidate recovery action vocabulary

| Action | Meaning |
|---|---|
| `RETRY_SAME_REQUEST` | Retry with the same idempotent inputs after transient failure |
| `QUERY_PAYMENT_STATUS` | Query authoritative product state before making another payment |
| `AUTHORIZE_WALLET` | Start or resume wallet authorization/binding |
| `OBTAIN_NEW_PROOF` | Obtain the proof associated with the completed intended payment |
| `CREATE_NEW_REQUIREMENT` | Ask the provider for a new, non-expired bill |
| `CORRECT_REQUEST` | Fix an invalid field before retrying |
| `DO_NOT_DELIVER` | Stop resource delivery because verification is not trustworthy |
| `RETURN_PRIOR_RESULT` | Return an idempotently stored prior fulfillment result |
| `CONTACT_SUPPORT` | Escalate a non-recoverable product/account mismatch |
| `ABORT` | End the current payment attempt safely |

These Profile-friendly names are aliases for developer guidance, not a second Core vocabulary. Implementations emitting ACT Candidate errors must use [`error-catalog.json`](../../../../specs/2.1/a402/schemas/error-catalog.json); product-only actions such as `AUTHORIZE_WALLET` remain Profile extensions.

## 2. Payment verification API

| Alipay error | Candidate ACT category | Retryability | Candidate actions | Provider rule |
|---|---|---|---|---|
| `SYSTEM_ERROR` | `ACT-A402-SYSTEM_UNAVAILABLE` | Query first | `QUERY_PAYMENT_STATUS`, `RETRY_VALIDATION`, `DO_NOT_DELIVER` | Keep the same verification inputs; do not deliver |
| `INVALID_PARAMETER` | `ACT-A402-REQUEST_INVALID` | After correction | `CORRECT_REQUEST`, `DO_NOT_DELIVER` | Validate local construction before retry |
| `CLIENT_SESSION_IS_EMPTY` | `ACT-A402-REQUEST_INVALID` | After correction/confirmation | `CORRECT_REQUEST`, `DO_NOT_DELIVER` | Resolve product optionality before verified claim |
| `PAYMENT_PROOF_AGENT_MISMATCH` | `ACT-A402-PROOF_INVALID` | Not with same proof | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER`, `CONTACT_SUPPORT` | Never deliver |
| `PAYMENT_PROOF_BUYER_MISMATCH` | `ACT-A402-PROOF_INVALID` | Not with same proof | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER`, `CONTACT_SUPPORT` | Never deliver |
| `PAYMENT_PROOF_EMPTY` | `ACT-A402-PROOF_INVALID` | After correction | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Never infer payment success |
| `PAYMENT_PROOF_ID_MISMATCH` | `ACT-A402-PROOF_INVALID` | Not with same inputs | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Never deliver |
| `PAYMENT_PROOF_INVALID` | `ACT-A402-PROOF_INVALID` | Not with same proof | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Never deliver |
| `PAYMENT_PROOF_NOT_FOUND` | `ACT-A402-PROOF_INVALID` | Query/temporary depending on product state | `QUERY_PAYMENT_STATUS`, `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Avoid automatic duplicate payment |
| `PAYMENT_PROOF_STATUS_INVALID` | `ACT-A402-PROOF_INVALID` | Product-dependent | `QUERY_PAYMENT_STATUS`, `DO_NOT_DELIVER`, `CONTACT_SUPPORT` | Never deliver |
| `PAYMENT_PROOF_TRADE_NO_MISMATCH` | `ACT-A402-PROOF_INVALID` | Not with same inputs | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Never deliver |
| `TRADE_NOT_FOUND` | `ACT-A402-STATE_CONFLICT` | Query/temporary depending on timing | `QUERY_PAYMENT_STATUS`, `DO_NOT_DELIVER` | Do not create a second payment automatically |
| `TRADE_NO_EMPTY` | `ACT-A402-REQUEST_INVALID` | After correction | `CORRECT_REQUEST`, `DO_NOT_DELIVER` | Validate before API call |
| `TRADE_NO_INVALID` | `ACT-A402-REQUEST_INVALID` | After correction | `CORRECT_REQUEST`, `DO_NOT_DELIVER` | Validate before API call |
| `TRADE_STATUS_CLOSED` | `ACT-A402-STATE_CONFLICT` | Terminal for current trade | `CREATE_NEW_REQUIREMENT`, `ABORT`, `DO_NOT_DELIVER` | New payment requires a new controlled attempt |
| `TRADE_STATUS_UNPAID` | `ACT-A402-STATE_CONFLICT` | User/product dependent | `QUERY_PAYMENT_STATUS`, `ABORT`, `DO_NOT_DELIVER` | Do not deliver or claim success |

## 3. Local business verification failures

| Failure | Candidate category | Candidate actions | Mandatory safety behavior |
|---|---|---|---|
| `active` is false | `ACT-A402-STATE_CONFLICT` | `QUERY_PAYMENT_STATUS`, `DO_NOT_DELIVER` | Do not deliver |
| Amount differs from original bill | `ACT-A402-PROOF_INVALID` | `DO_NOT_DELIVER`, `CONTACT_SUPPORT` | Never accept partial/over payment silently |
| Merchant order differs | `ACT-A402-PROOF_INVALID` | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Do not associate with another order |
| Resource differs | `ACT-A402-PROOF_INVALID` | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Do not disclose requested resource |
| Transaction already fulfilled | `ACT-A402-PROOF_INVALID` | `RETURN_PRIOR_RESULT` or `DO_NOT_DELIVER` | Never perform a second non-idempotent delivery |
| Requirement expired before payment | `ACT-A402-REQUEST_INVALID` | `CREATE_NEW_REQUIREMENT`, `ABORT` | Do not mutate the old bill silently |

## 4. Fulfillment confirmation API

| Alipay error | Candidate ACT category | Retryability | Candidate actions | Provider rule |
|---|---|---|---|---|
| `SYSTEM_ERROR` | `ACT-A402-SYSTEM_UNAVAILABLE` | Query first | `RETRY_FULFILLMENT`, `QUERY_PAYMENT_STATUS`, `CONTACT_SUPPORT` | Retry idempotently with the same trade number |
| `INVALID_PARAMETER` | `ACT-A402-REQUEST_INVALID` | After correction | `CORRECT_REQUEST`, `CONTACT_SUPPORT` | Do not invent a replacement transaction |
| `SELLER_IDENTITY_MISMATCH` | `ACT-A402-PARTICIPANT_INVALID` | Not without configuration fix | `CONTACT_SUPPORT` | Preserve delivery audit evidence |
| `SELLER_ID_EMPTY` | `ACT-A402-PARTICIPANT_INVALID` | After configuration fix | `CORRECT_REQUEST`, `CONTACT_SUPPORT` | Validate merchant context |
| `TRADE_NOT_FOUND` | `ACT-A402-STATE_CONFLICT` | Query first | `QUERY_PAYMENT_STATUS`, `CONTACT_SUPPORT` | Preserve delivery audit evidence |
| `TRADE_NO_EMPTY` | `ACT-A402-REQUEST_INVALID` | After correction | `CORRECT_REQUEST` | Validate locally |
| `TRADE_NO_INVALID` | `ACT-A402-REQUEST_INVALID` | After correction | `CORRECT_REQUEST` | Validate locally |
| `TRADE_STATUS_INVALID` | `ACT-A402-STATE_CONFLICT` | Query first | `QUERY_PAYMENT_STATUS`, `CONTACT_SUPPORT` | Do not claim confirmation succeeded |

## 5. Agent-side capability errors

The official Skill/CLI output remains authoritative. The conference Profile needs fixtures for at least:

| Condition | Candidate category | Candidate actions |
|---|---|---|
| Wallet not activated or bound | `ACT-A402-PARTICIPANT_INVALID` | `AUTHORIZE_WALLET`, `ABORT` |
| Wallet service temporarily unavailable | `ACT-A402-SYSTEM_UNAVAILABLE` | `QUERY_PAYMENT_STATUS`, `ABORT` |
| User declines authorization/payment | `ACT-A402-AUTHORIZATION_REJECTED` | `ABORT` |
| Payment remains pending | `ACT-A402-STATE_CONFLICT` | `QUERY_PAYMENT_STATUS`, `ABORT` |
| Payment requirement expired | `ACT-A402-REQUEST_INVALID` | `CREATE_NEW_REQUIREMENT`, `ABORT` |
| Skill/CLI output is malformed | `ACT-A402-REQUEST_INVALID` | `ABORT`, `CONTACT_SUPPORT` |

Exact CLI error identifiers and output schemas require official runtime evidence before a `Sandbox Verified` claim. Their absence does not block the `0.9-preview.1` mapping release.

## 6. Remaining Product Profile validation

- Capture exact official CLI error identifiers and sanitized output shapes.
- Confirm product retry delays and maximum attempts when publicly observable.
- Confirm which product error details may be shown to users versus retained in protected diagnostics.
- Verify the product response for an idempotently returned prior fulfillment.

Core retryability and recovery action shape are no longer protocol Pending Decisions; these remaining questions affect only the product mapping and Sandbox Verified evidence.
