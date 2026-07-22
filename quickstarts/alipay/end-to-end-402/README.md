# End-to-end 402 Quickstart

> Goal: connect the official buyer Skill/CLI to a real seller 402 endpoint and collect reproducible Sandbox evidence

## 1. Start the seller

Configure and run the [Metered REST Provider](../metered-rest-provider/README.md). Confirm its health endpoint:

```bash
curl http://127.0.0.1:8080/health
```

## 2. Inspect the payment requirement

Requires Node.js 18+.

```bash
cd quickstarts/alipay/end-to-end-402
npm run inspect -- http://127.0.0.1:8080/paid-resource
```

The inspector performs no payment. It checks the real HTTP status, decodes `Payment-Needed`, validates the public required field shape, and prints only a sanitized summary.

## 3. Install and invoke the buyer capability

Follow the [Agent Payment Quickstart](../agent-payment/README.md), then ask the Agent using the installed official Skill/CLI to access the paid-resource URL. The human user must see and authorize the actual Sandbox payment.

The official buyer workflow may keep `Payment-Proof` internal. Do not copy it from logs or reconstruct it manually. The seller will release the resource only after official verification.

## 4. Record the result

Copy the repository [evidence template](../../../docs/getting-started/end-to-end-evidence-template.md) outside any public artifact directory and record:

- repository commit and Quickstart version;
- official package/Skill/CLI version or integrity information;
- sanitized order, trade and resource identifiers;
- 402, authorization, verification, delivery and fulfillment timestamps;
- actual recovery behavior for at least one invalid or expired case.

Never record private keys, binding codes, payment passwords, `app_auth_token`, complete `Payment-Proof`, `client_session`, or a replayable HTTP request.

## 5. Pass criteria

The result is an end-to-end pass only when:

- the buyer used the official Alipay capability;
- the payment was authorized through the official product flow;
- the provider called the official verification API;
- verified facts matched the original bill;
- exactly the intended resource was delivered;
- fulfillment confirmation succeeded or entered an auditable persisted retry path;
- all evidence is sanitized and publicly reproducible from official documentation.

Local unit tests and the inspector alone do not satisfy these criteria.
