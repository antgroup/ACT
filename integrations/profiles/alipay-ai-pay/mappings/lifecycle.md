# Working lifecycle mapping

> Status: Preview / Non-normative  
> ACT six-state transaction projection is defined by the 2.1 Candidate; the finer-grained Profile observations below are non-normative mappings.

## 1. End-to-end lifecycle

| Sequence | Product event | ACT working state | State owner | Evidence/status |
|---|---|---|---|---|
| 1 | Provider constructs a payable bill | `REQUIREMENT_CREATED` | Paid-resource provider | AP-SRC-006, `PUBLIC-FACT` |
| 2 | Provider returns HTTP 402 | `PAYMENT_REQUIRED` | Provider/HTTP Binding | AP-SRC-006, `PUBLIC-FACT` |
| 3 | Wallet is unavailable or not authorized | `AUTHORIZATION_REQUIRED` | Buyer Agent/Profile | AP-SRC-003, 004, `PUBLIC-FACT` |
| 4 | User authorizes and binds wallet | `PAYMENT_CAPABILITY_READY` | Alipay product | AP-SRC-003, `PUBLIC-FACT` |
| 5 | Agent submits the payment | `PAYMENT_PENDING` | Buyer Agent/Profile | AP-SRC-004, `PUBLIC-FACT` |
| 6 | Product returns a successful payment outcome/proof | `PAYMENT_SUCCEEDED` | Alipay product | AP-SRC-004, 006, `PUBLIC-FACT` |
| 7 | Agent retries with proof | `PROOF_PRESENTED` | Buyer Agent/HTTP Binding | AP-SRC-006, `PUBLIC-FACT` |
| 8 | Provider verifies proof and original bill facts | `PROOF_VERIFIED` | Provider/Profile | AP-SRC-006, 007, `PUBLIC-FACT` |
| 9 | Provider commits replay protection and delivers | `RESOURCE_DELIVERED` | Provider/application | AP-SRC-006, `PUBLIC-FACT` |
| 10 | Provider confirms fulfillment | `FULFILLMENT_CONFIRMED` | Provider/Profile | AP-SRC-006, 008, `PUBLIC-FACT` |

## 2. ACT Candidate state projection

| ACT Candidate state | Product observations mapped into it |
|---|---|
| `CREATE` | `REQUIREMENT_CREATED` |
| `WAIT_BUYER_PAY` | `PAYMENT_REQUIRED`, `AUTHORIZATION_REQUIRED`, `PAYMENT_CAPABILITY_READY`, `PAYMENT_PENDING` |
| `WAIT_SELLER_FULFILLMENT` | `PAYMENT_SUCCEEDED`, `PROOF_PRESENTED`, `PROOF_VERIFIED` |
| `WAIT_BUYER_RECEIPT` | `RESOURCE_DELIVERED` |
| `TRADE_FINISHED` | `FULFILLMENT_CONFIRMED` |
| `TRADE_CLOSED` | cancelled, refunded, expired or terminally rejected transaction |

ACT transition triggers are fixed by the Candidate state contract. This table remains a Product Profile mapping because the public Alipay observations do not expose every ACT transition as a product event.

## 3. Candidate terminal and recovery observations

| Condition | ACT working state | Candidate next actions | Status |
|---|---|---|---|
| Payment deadline elapsed | `REQUIREMENT_EXPIRED` | request a new requirement, abort | `CANDIDATE-MAPPED` |
| User declines or product rejects payment | `PAYMENT_REJECTED` | revise intent, retry if permitted, abort | `CANDIDATE-MAPPED` |
| Payment still processing | `PAYMENT_PENDING` | query, wait, abort if permitted | `CANDIDATE-MAPPED` |
| Proof cannot be parsed or verified | `PROOF_INVALID` | pay again only when product permits, obtain new proof, abort | `CANDIDATE-MAPPED` |
| Proof/payment does not match bill | `PROOF_MISMATCH` | do not deliver, obtain correct proof, support/escalate | `CANDIDATE-MAPPED` |
| Payment already used for fulfillment | `PROOF_REPLAYED` | return prior idempotent result or reject; never deliver twice | `CANDIDATE-MAPPED` |
| Resource delivery fails after verification | `DELIVERY_FAILED` | retry idempotently, compensate/escalate | `CANDIDATE-MAPPED`; product behavior varies |
| Fulfillment confirmation fails | `FULFILLMENT_CONFIRMATION_PENDING` | retry same confirmation, query/support | `PRODUCT-REVIEW` |

## 4. Required invariants

The candidate Core/Profile must preserve these invariants:

1. No resource delivery before a successful product verification and local bill match.
2. A successful payment does not by itself prove that fulfillment occurred.
3. Verification API transport success does not replace business validation.
4. A transaction cannot cause multiple non-idempotent deliveries.
5. Retrying a request must not create an unrelated bill without clearly communicating the new requirement.
6. Wallet authorization state and transaction payment state are distinct.
7. Product state remains authoritative for payment outcome; local Demo state is never authoritative.

## 5. Remaining Product Profile validation

- Validate concurrent callback/retry observations in the official sandbox.
- Confirm whether `PAYMENT_SUCCEEDED` is observable outside the official buyer workflow.
- Confirm the exact relationship between buyer fulfillment ack and seller fulfillment confirm.
- Record actual timeout and compensation behavior without changing the ACT Candidate state machine.

These items block only `Alipay AI Pay Sandbox Verified`, not Profile Preview publication.
