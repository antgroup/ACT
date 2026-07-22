# HTTP A402 Binding

> Status: Preview / Non-normative

This Binding carries the candidate `PSD-PAY-A402` interaction over HTTP:

1. The buyer requests a paid resource.
2. The provider returns `402 Payment Required` with `Payment-Needed`.
3. The buyer pays through an authorized payment capability.
4. The buyer retries the same resource request with `Payment-Proof`.
5. The provider verifies the proof, enforces bill consistency and replay protection, then delivers the resource.

The Binding owns HTTP status, Header serialization, preservation of the original request, and retry behavior. The [Alipay AI Pay Profile](../../profiles/alipay-ai-pay/README.md) owns Alipay fields, RSA2, verification and fulfillment APIs. The selected INS/DEL/AUP component owns the authorization gate.

Current product serialization must follow the [public Alipay AI Metered Payment guide](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html). Candidate ACT v2.1 serialization must not override that guide before a public specification is released.

Runnable entry: [Alipay Metered REST provider Quickstart](../../quickstarts/alipay/metered-rest-provider/README.md).
