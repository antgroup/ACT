# Alipay Metered REST Provider Quickstart

> Scope: seller-side HTTP 402 + Alipay Sandbox/OpenAPI verification and fulfillment

This is a small runnable provider, not a Mock payment service. A resource is released only after `alipay.aipay.agent.payment.verify` succeeds and the verified amount, merchant order, resource and trade number match the stored bill.

The implementation follows the current public [AI Metered Payment integration guide](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html). The guide requires Alipay Java SDK `4.38.0.ALL` or newer; this Quickstart pins `4.40.720.ALL`, which contains the generated AI Pay request and response types used here. Product fields remain an Alipay Profile concern; candidate `PSD-PAY-A402` supplies the protocol position.

## 1. Prerequisites

- JDK 8 or newer and Maven 3.8+.
- An Alipay application configured for the official Sandbox or OpenAPI environment.
- AI Metered Payment product access and a registered `service_id`.
- Application private key and Alipay public key stored outside the repository.
- Seller ID and the product-defined price/resource information.

Complete product onboarding and credentials through the [AIPay documentation](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html). This repository does not recreate the console or Sandbox.

## 2. Configure

Copy `.env.example` to `.env`, replace every placeholder and use absolute key-file paths. `.env` and `*.pem` are ignored by Git.

```bash
cd quickstarts/alipay/metered-rest-provider
cp .env.example .env
```

Load the file into the current shell:

```bash
set -a
. ./.env
set +a
```

The Quickstart accepts `ALIPAY_PRIVATE_KEY_FILE` and `ALIPAY_PUBLIC_KEY_FILE`, which are safer than inline key environment variables. `ALIPAY_APP_AUTH_TOKEN` is optional and only applies to the documented third-party application mode.

The `ALIPAY_AMOUNT` value is passed exactly as a string. Follow the current product console and API definition; do not silently convert units in the Quickstart.

## 3. Test and run

```bash
mvn test
mvn package
java -jar target/alipay-metered-rest-provider-0.1.0-SNAPSHOT.jar
```

Check the unpaid response:

```bash
curl -i http://127.0.0.1:8080/paid-resource
```

Expected result:

- HTTP `402 Payment Required`;
- a Base64URL `Payment-Needed` Header;
- a JSON diagnostic body that contains no key or proof.

Use the [end-to-end 402 Quickstart](../end-to-end-402/README.md) and official Agent Payment Skill/CLI to perform the authorized payment and retry.

## 4. Implemented safety gates

- RSA2 signs the exact public guide field set in sorted-key order.
- `Payment-Proof` is parsed as untrusted Base64 JSON.
- The official verification API is called before delivery.
- The documented `client_session` is forwarded in `biz_content`; this avoids dropping it when a generated SDK model lags the public API field.
- `active`, amount, merchant order, resource ID and trade number are matched.
- A trade cannot be used for a different resource.
- Idempotent retries return the same resource without scheduling a second fulfillment confirmation.
- Fulfillment confirmation runs asynchronously after resource delivery.
- Logs redact trade numbers and never print keys or complete proofs.

## 5. Production gaps

This Quickstart deliberately uses in-memory bill and fulfillment records. Before production use, replace them with durable, atomic storage and add:

- persisted fulfillment jobs with bounded retry/backoff;
- multi-instance idempotency and replay locking;
- bill expiration cleanup and retention policy;
- authentication, rate limiting and request-size limits at the edge;
- structured sanitized observability and alerting;
- key management rather than process environment variables;
- product-specific disaster recovery and reconciliation.

Until these gaps are addressed and Sandbox evidence passes, this code is a Quickstart rather than a reference implementation.
