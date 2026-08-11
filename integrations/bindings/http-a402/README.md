# HTTP A402 Binding

> Kind: Binding；Status: Preview / Non-normative；Version: `0.2-working-draft`；Depends on: ACT Core 2.1 Candidate

This Binding carries the candidate `PSD-PAY-A402` interaction over HTTP:

1. The buyer requests a paid resource.
2. The provider returns `402 Payment Required` with `Payment-Needed`.
3. The buyer pays through an authorized payment capability.
4. The buyer retries the same resource request with `Payment-Proof`.
5. The provider verifies the proof, enforces bill consistency and replay protection, then delivers the resource.

For ACT-native A402 messages, all three Header values are Base64URL-encoded UTF-8 JSON using a `protocol` + `method` envelope:

| Header | Direction | Requirement |
|---|---|---|
| `Payment-Needed` | provider → buyer in HTTP 402 | Carries the payment requirement |
| `Payment-Proof` | buyer → provider on the new request to the original resource or service | Carries the payment authorization-result proof |
| `Payment-Validation` | provider → buyer after proof validation | Optional on a successful response; carries machine-readable validation and fulfillment status |

The Binding owns HTTP status and Header serialization. The Candidate machine contract now fixes a canonical request fingerprint, a separate idempotency key for non-safe methods, replay-key retention rules, six-state transitions, and structured wire errors. See the [A402 Candidate schemas](../../../specs/2.1/a402/schemas/README.md) and [Candidate decision record](../../../governance/decisions/candidate-machine-contract-resolution-2026-08-03.md). These remain non-normative until governance accepts them.

The [Alipay AI Pay Profile](../../profiles/alipay-ai-pay/README.md) owns Alipay fields, RSA2, verification and fulfillment APIs. The selected INS/DEL/AUP component owns the authorization gate. INS/L1 is the current executable publication baseline; DEL/L2 and AUP/L3 remain validation-pending.

Current product serialization must follow the [public Alipay AI Metered Payment guide](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html). That guide currently describes `Payment-Proof` encoding differently and does not publish a `Payment-Validation` Header; an Alipay implementation must therefore follow the Product Profile mapping rather than infer unsupported product behavior from the ACT Candidate.

Runnable entry: [Alipay Metered REST provider Quickstart](../../../code/examples/alipay/metered-rest-provider/README.md).
