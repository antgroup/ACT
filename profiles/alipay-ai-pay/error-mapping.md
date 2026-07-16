# Working error and recovery mapping

> Status: Preview / Non-normative  
> Product error names come from public Alipay API documentation; ACT categories and actions are candidates.

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

These names are not normative `valid_next_actions` until the ACT revision accepts them.

## 2. Payment verification API

| Alipay error | Candidate ACT category | Retryability | Candidate actions | Provider rule |
|---|---|---|---|---|
| `SYSTEM_ERROR` | `TEMPORARY_PROVIDER_ERROR` | Retryable | `RETRY_SAME_REQUEST` | Keep the same verification inputs; do not deliver |
| `INVALID_PARAMETER` | `INVALID_REQUEST` | After correction | `CORRECT_REQUEST`, `DO_NOT_DELIVER` | Validate local construction before retry |
| `CLIENT_SESSION_IS_EMPTY` | `MISSING_REQUIRED_CONTEXT` | After correction/confirmation | `CORRECT_REQUEST`, `DO_NOT_DELIVER` | Resolve product optionality before profile release |
| `PAYMENT_PROOF_AGENT_MISMATCH` | `PROOF_SUBJECT_MISMATCH` | Not with same proof | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER`, `CONTACT_SUPPORT` | Never deliver |
| `PAYMENT_PROOF_BUYER_MISMATCH` | `PROOF_SUBJECT_MISMATCH` | Not with same proof | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER`, `CONTACT_SUPPORT` | Never deliver |
| `PAYMENT_PROOF_EMPTY` | `MISSING_PROOF` | After correction | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Never infer payment success |
| `PAYMENT_PROOF_ID_MISMATCH` | `PROOF_MISMATCH` | Not with same inputs | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Never deliver |
| `PAYMENT_PROOF_INVALID` | `INVALID_PROOF` | Not with same proof | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Never deliver |
| `PAYMENT_PROOF_NOT_FOUND` | `PROOF_NOT_FOUND` | Query/temporary depending on product state | `QUERY_PAYMENT_STATUS`, `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Avoid automatic duplicate payment |
| `PAYMENT_PROOF_STATUS_INVALID` | `PROOF_STATE_INVALID` | Product-dependent | `QUERY_PAYMENT_STATUS`, `DO_NOT_DELIVER`, `CONTACT_SUPPORT` | Never deliver |
| `PAYMENT_PROOF_TRADE_NO_MISMATCH` | `PROOF_MISMATCH` | Not with same inputs | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Never deliver |
| `TRADE_NOT_FOUND` | `PAYMENT_NOT_FOUND` | Query/temporary depending on timing | `QUERY_PAYMENT_STATUS`, `DO_NOT_DELIVER` | Do not create a second payment automatically |
| `TRADE_NO_EMPTY` | `INVALID_REQUEST` | After correction | `CORRECT_REQUEST`, `DO_NOT_DELIVER` | Validate before API call |
| `TRADE_NO_INVALID` | `INVALID_REQUEST` | After correction | `CORRECT_REQUEST`, `DO_NOT_DELIVER` | Validate before API call |
| `TRADE_STATUS_CLOSED` | `PAYMENT_CLOSED` | Terminal for current trade | `CREATE_NEW_REQUIREMENT`, `ABORT`, `DO_NOT_DELIVER` | New payment requires a new controlled attempt |
| `TRADE_STATUS_UNPAID` | `PAYMENT_NOT_COMPLETED` | User/product dependent | `QUERY_PAYMENT_STATUS`, `ABORT`, `DO_NOT_DELIVER` | Do not deliver or claim success |

## 3. Local business verification failures

| Failure | Candidate category | Candidate actions | Mandatory safety behavior |
|---|---|---|---|
| `active` is false | `PAYMENT_NOT_ACTIVE` | `QUERY_PAYMENT_STATUS`, `DO_NOT_DELIVER` | Do not deliver |
| Amount differs from original bill | `AMOUNT_MISMATCH` | `DO_NOT_DELIVER`, `CONTACT_SUPPORT` | Never accept partial/over payment silently |
| Merchant order differs | `REQUIREMENT_MISMATCH` | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Do not associate with another order |
| Resource differs | `RESOURCE_MISMATCH` | `OBTAIN_NEW_PROOF`, `DO_NOT_DELIVER` | Do not disclose requested resource |
| Transaction already fulfilled | `PROOF_REPLAYED` | `RETURN_PRIOR_RESULT` or `DO_NOT_DELIVER` | Never perform a second non-idempotent delivery |
| Requirement expired before payment | `REQUIREMENT_EXPIRED` | `CREATE_NEW_REQUIREMENT`, `ABORT` | Do not mutate the old bill silently |

## 4. Fulfillment confirmation API

| Alipay error | Candidate ACT category | Retryability | Candidate actions | Provider rule |
|---|---|---|---|---|
| `SYSTEM_ERROR` | `TEMPORARY_PROVIDER_ERROR` | Retryable | `RETRY_SAME_REQUEST` | Retry idempotently with the same trade number |
| `INVALID_PARAMETER` | `INVALID_REQUEST` | After correction | `CORRECT_REQUEST`, `CONTACT_SUPPORT` | Do not invent a replacement transaction |
| `SELLER_IDENTITY_MISMATCH` | `PAYEE_IDENTITY_MISMATCH` | Not without configuration fix | `CONTACT_SUPPORT` | Preserve delivery audit evidence |
| `SELLER_ID_EMPTY` | `PAYEE_IDENTITY_MISSING` | After configuration fix | `CORRECT_REQUEST`, `CONTACT_SUPPORT` | Validate merchant context |
| `TRADE_NOT_FOUND` | `PAYMENT_NOT_FOUND` | Product-dependent | `QUERY_PAYMENT_STATUS`, `CONTACT_SUPPORT` | Preserve delivery audit evidence |
| `TRADE_NO_EMPTY` | `INVALID_REQUEST` | After correction | `CORRECT_REQUEST` | Validate locally |
| `TRADE_NO_INVALID` | `INVALID_REQUEST` | After correction | `CORRECT_REQUEST` | Validate locally |
| `TRADE_STATUS_INVALID` | `PAYMENT_STATE_INVALID` | Product-dependent | `QUERY_PAYMENT_STATUS`, `CONTACT_SUPPORT` | Do not claim confirmation succeeded |

## 5. Agent-side capability errors

The official Skill/CLI output remains authoritative. The conference Profile needs fixtures for at least:

| Condition | Candidate category | Candidate actions |
|---|---|---|
| Wallet not activated or bound | `AUTHORIZATION_REQUIRED` | `AUTHORIZE_WALLET`, `ABORT` |
| Wallet service temporarily unavailable | `TEMPORARY_PROVIDER_ERROR` | `RETRY_SAME_REQUEST`, `ABORT` |
| User declines authorization/payment | `USER_DECLINED` | `ABORT` |
| Payment remains pending | `PAYMENT_PENDING` | `QUERY_PAYMENT_STATUS`, `ABORT` |
| Payment requirement expired | `REQUIREMENT_EXPIRED` | `CREATE_NEW_REQUIREMENT`, `ABORT` |
| Skill/CLI output is malformed | `BINDING_ERROR` | `ABORT`, `CONTACT_SUPPORT` |

Exact CLI error identifiers and output schemas require validation against the public package before the 0.9 Profile release.

## 6. Open protocol decisions

- Is retryability a boolean, an enum, or derived from `valid_next_actions`?
- Which actor is allowed to execute each recovery action?
- How are retry delay, expiration and maximum attempts represented?
- Should sensitive product error details be hidden from the end user while remaining available to the Agent?
- How is an idempotently returned prior result distinguished from a new fulfillment?
