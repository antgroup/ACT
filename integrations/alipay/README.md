# Alipay Reference Integration

This directory demonstrates how ACT 2.1 can be connected to the public Alipay AI Pay product surface. It is product-specific implementation material, not ACT protocol text.

| Directory | Purpose |
|---|---|
| [`a402.md`](a402.md) / [`a402.en.md`](a402.en.md) | Non-normative ACT A402 integration guide used by this reference integration |
| [`commerce-payment-negotiation.md`](commerce-payment-negotiation.md) / [`commerce-payment-negotiation.en.md`](commerce-payment-negotiation.en.md) | Non-normative guide connecting commerce negotiation to payment |
| [`buyer-agent/`](buyer-agent/README.md) | Preflight and handoff to the official Alipay Agent Payment installer |
| [`seller-java/`](seller-java/README.md) | Java seller service using the Alipay SDK for proof verification and fulfillment confirmation |
| [`validation/`](validation/README.md) | Sandbox preflight and sanitized evidence guidance |

## Product authority

Use the official sources for current product behavior:

- [AIPay](https://aipay.alipay.com/callpay)
- [AI wallet guide](https://aipay.alipay.com/wallet-guide)
- [AI metered-payment integration guide](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)
- [Official Agent Payment package](https://github.com/alipay/payment-skills)

This repository does not duplicate account opening, application registration, credential issuance, or the official sandbox. Never commit application private keys, Alipay public keys, tokens, complete payment proofs, or replayable payment URLs.

The two Markdown integration guides in this directory explain ACT semantics for implementers. They are not Alipay product documentation and do not override either the ACT domain specifications or the official Alipay sources above.

## Boundary

ACT defines cross-product roles and interaction semantics. Alipay documentation defines product fields, APIs, signing, authorization, and operational behavior. If the two layers differ, the integration must expose the mapping explicitly; product behavior must not be rewritten into the ACT specification.

## ACT 2.1 to Alipay product mapping

| ACT 2.1 concept | Alipay AI metered-payment implementation | Boundary |
|---|---|---|
| `402 Payment Required` + `Payment-Needed` | The seller returns the product-defined bill as Base64URL-encoded JSON. | Alipay defines the required bill fields and RSA2 signing input. |
| `Payment-Proof` | The buyer retries the resource request with the Alipay proof payload encoded as standard Base64 JSON. | This product encoding differs from the generic ACT 2.1 Base64URL rule; integrations must follow the current Alipay product guide at this boundary. |
| Proof validation | `alipay.aipay.agent.payment.verify` returns `active`, amount, merchant order, Alipay trade number, and resource ID. | The seller must compare all returned facts with its stored bill before delivery. |
| `Payment-Validation` | The verification API result supplies the corresponding validation facts. This sample does not claim that Alipay exposes a `Payment-Validation` HTTP Header. | An ACT adapter may express a validation result, but must not attribute that Header to the Alipay product. |
| `method_id` and method version | The repository-owned mapping uses `act-integration:a402/alipay-ai-pay` / `1.0.0` for correlation, replay and demo artifacts. | This stable integration identifier is not an Alipay product field or an ACT global registration; it is never added to product bill, proof, verification or fulfillment payloads. |
| Fulfillment confirmation | After returning the resource, the seller asynchronously calls `alipay.aipay.agent.fulfillment.confirm`. | Payment verification and resource delivery remain separate observable outcomes. |

The current seller payload and APIs are sourced from the [official AI metered-payment integration guide](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html). Re-check that guide when the product or SDK version changes.

## Verify

```bash
npm --prefix integrations/alipay/buyer-agent test
mvn -f integrations/alipay/seller-java/pom.xml test
node --test integrations/alipay/validation/*.test.mjs
```

Passing local tests does not claim real sandbox interoperability. Such a claim requires a completed, sanitized evidence record.
