# A402 Candidate / Alipay Product Adapter

> Status: Profile Preview / Non-normative  
> Scope: evidence and semantic mapping only; this adapter does not change Alipay product wire payloads.

The Alipay `Payment-Needed` and `Payment-Proof` payloads continue to follow the public product guide and the Profile Preview schemas. They are not ACT Core payloads. An implementation that demonstrates ACT 2.1 Candidate behavior must keep a separate trusted mapping context instead of adding undocumented fields to the Alipay payload.

## Mapping boundary

| Candidate evidence fact | Alipay product source | Adapter responsibility |
|---|---|---|
| `method_id`, `method_version`, PSP and endpoint/schema references | `CID-PCA-NEG` or an equivalent validated capability source | Validate the source and preserve the selected method context outside the product payload |
| `out_trade_no`, amount, currency and `resource_id` | decoded Alipay `Payment-Needed` | Store a redacted order reference and compare later verification results |
| `request_fingerprint` | original protected-resource request | Compute and store the Candidate fingerprint in trusted seller context; the current Alipay payload does not carry this field |
| Proof reference and transaction reference | official payment workflow and Alipay `Payment-Proof` | Store only redacted references; never expose the complete Proof or `client_session` |
| validation fact | `alipay.aipay.agent.payment.verify` result plus local bill checks | Require `active` and order/resource/amount consistency before delivery |
| delivery fact | seller application | Atomically occupy the fulfillment key and persist an independent delivery result |
| method fulfillment confirmation | `alipay.aipay.agent.fulfillment.confirm` | Record separately from delivery and from optional TSD evidence |

## Required honesty boundary

- Product Profile mapping is not Core wire conformance.
- The current product payload must not be described as containing Candidate-only `method_id`, `method_version` or `request_fingerprint` fields.
- `Payment-Validation` is an ACT Candidate semantic mapping; the current public Alipay guide does not define that response Header.
- TSD evidence is optional and asynchronous. It is not created merely because `fulfillment.confirm` succeeded.
- The example method identifier `example:a402/alipay-ai-pay` is for Guided Preview and tests only. A Sandbox Verified or production claim must use a governed method identifier and version obtained from the validated capability source.

## Demo evidence invariants

The showcase evidence chain requires one stable correlation reference and checks that method, version, order, resource, amount, currency, request fingerprint and transaction references do not change across steps. The idempotent replay scene includes a second request and must prove `NO_NEW_PAYMENT`, `RETURN_PRIOR_RESULT` and `NOT_REPEATED` fulfillment confirmation.
