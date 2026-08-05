# A402 source resolution — 2026-08-03

> Status: Source-settled / Non-normative repository record  
> Scope: `DP-A402-002`, former `PD-2.1-001`, `PD-2.1-002`, `PD-2.1-008`

## Authority and reason

The protocol maintainer's completed [Payment Services Domain](https://yuque.antfin.com/hknzlf/fvle20/dve0b9g2u1t3cs33) was published on 2026-08-03 and now contains the integrated PSD 2.1 revision. This record does not create a new repository governance decision. It records that earlier repository questions have been superseded by the protocol fact source.

Tracked source metadata:

- document ID: `545380168`;
- `content_updated_at`: `2026-08-03T07:05:43.000Z`;
- body SHA-256: `8d39bbafe0bd5c344a78355c4a68371e07b927cc97bb394b3fdbfb0bfb776d06`.

## Source-settled facts

1. `Payment-Needed`, `Payment-Proof`, and `Payment-Validation` Header values use Base64URL-encoded UTF-8 JSON.
2. Before encoding, all three payloads use a `protocol` + `method` two-layer structure.
3. `Payment-Validation` is an optional seller response Header after proof validation.
4. Traditional merchant-order payment uses the merchant order number; A402 can return `out_trade_no`, `resource_id`, and equivalent order/resource identifiers in `Payment-Needed`.
5. The payment request is not required to carry a complete shopping cart.

## Source boundary and subsequent Candidate decision

The source itself does not freeze Header-specific field placement and requiredness, a `method_id` namespace/version model, canonical request fingerprints, replay-window persistence, standard wire error objects, or the TSD fulfillment-evidence mapping. The repository subsequently selected these items for the executable Working Draft in the [Candidate machine-contract decision](candidate-machine-contract-resolution-2026-08-03.md). That later record is a Candidate engineering decision, not a fact attributed to the source and not a formal Accepted ADR.

## Product compatibility boundary

The current Alipay guide describes `Payment-Proof` encoding differently and does not publish a `Payment-Validation` Header. Alipay implementations continue to follow the official product guide and Alipay Product Profile; product differences do not reopen the ACT protocol facts above.
