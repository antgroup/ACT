# Working lifecycle mapping

> Status: Preview / Non-normative  
> ACT states are placeholders pending the Core 2.1 revision.

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

## 2. Candidate terminal and recovery states

| Condition | ACT working state | Candidate next actions | Status |
|---|---|---|---|
| Payment deadline elapsed | `REQUIREMENT_EXPIRED` | request a new requirement, abort | `PROTOCOL-PENDING` |
| User declines or product rejects payment | `PAYMENT_REJECTED` | revise intent, retry if permitted, abort | `PROTOCOL-PENDING` |
| Payment still processing | `PAYMENT_PENDING` | query, wait, abort if permitted | `PROTOCOL-PENDING` |
| Proof cannot be parsed or verified | `PROOF_INVALID` | pay again only when product permits, obtain new proof, abort | `PROTOCOL-PENDING` |
| Proof/payment does not match bill | `PROOF_MISMATCH` | do not deliver, obtain correct proof, support/escalate | `PROTOCOL-PENDING` |
| Payment already used for fulfillment | `PROOF_REPLAYED` | return prior idempotent result or reject; never deliver twice | `PROTOCOL-PENDING` |
| Resource delivery fails after verification | `DELIVERY_FAILED` | retry idempotently, compensate/escalate | Core/product responsibility open |
| Fulfillment confirmation fails | `FULFILLMENT_CONFIRMATION_PENDING` | retry same confirmation, query/support | `PRODUCT-REVIEW` |

## 3. Required invariants

The candidate Core/Profile must preserve these invariants:

1. No resource delivery before a successful product verification and local bill match.
2. A successful payment does not by itself prove that fulfillment occurred.
3. Verification API transport success does not replace business validation.
4. A transaction cannot cause multiple non-idempotent deliveries.
5. Retrying a request must not create an unrelated bill without clearly communicating the new requirement.
6. Wallet authorization state and transaction payment state are distinct.
7. Product state remains authoritative for payment outcome; local Demo state is never authoritative.

## 4. Protocol decisions required

- Which states are normative Core states versus Profile observations?
- Is `PAYMENT_SUCCEEDED` observable by the buyer only, or must the provider treat `PROOF_VERIFIED` as the first trustworthy paid state?
- How are asynchronous callbacks represented alongside synchronous HTTP retries?
- Does the fulfillment receipt describe resource delivery, product confirmation, or both?
- What is the idempotent response when a verified proof is replayed after successful delivery?
- How are timeout and compensation responsibilities divided among Agent, provider and PSP?
