# ACT Protocol

[简体中文](README.md) | English

ACT (Agentic Commerce Trust Protocol) is an open protocol for agentic commerce. ACT 2.1 defines four cooperating domains: Authorization & Delegation, Commerce Interaction, Payment Services, and Trust Services. This repository uses an agent discovering and purchasing paid digital resources as its end-to-end scenario, while keeping the specification, product-neutral safety sample, interactive demo, and Alipay reference integration separate.

## Start here

| Goal | Entry |
|---|---|
| Experience the ACT flow online | [ACT website demo](https://www.act-protocol.com/demo) |
| Read ACT 2.1 | [Specification overview](docs/specification/overview.en.md) |
| Understand end-to-end flows | [Scenarios and Business Flows](docs/specification/scenarios.en.md) |
| Run the safe local A402 sample | [Local A402 Sample](code/samples/local-a402/README.md) |
| Run the interactive demo locally | [Web Showcase](code/web-client/alipay-ai-pay-showcase/README.en.md) |
| Run the TSD-CRD credit-association reference flow | [TSD-CRD Reference Implementation](code/samples/tsd-crd-reference/README.md) |
| Integrate Alipay | [Alipay Reference Integration](integrations/alipay/README.md) |

For a first visit:

1. Open the [ACT website demo](https://www.act-protocol.com/demo) to see the business steps, participants, and protocol components together.
2. Read the [English overview](docs/specification/overview.en.md) to distinguish ADD, CID, PSD, TSD, and A402; keep the [bilingual glossary](docs/glossary.md) open for abbreviations.
3. Read [Scenarios and Business Flows](docs/specification/scenarios.en.md) to map the demo onto complete protocol flows.
4. Run the Local A402 Sample or TSD-CRD Reference Implementation depending on whether you are exploring the safe payment path or credit association.
5. For a real successful payment flow, choose the [Alipay buyer](integrations/alipay/buyer-agent/README.md) or [Java seller](integrations/alipay/seller-java/README.md) integration and complete authorization and payment in the official sandbox.

The Local A402 Sample intentionally rejects fake proof instead of manufacturing payment success. A successful paid delivery requires verified proof from the official product workflow. The TSD-CRD Reference Implementation uses only mock capabilities and test keys; it is not a production credit service.

The five human-readable specification documents and the non-normative scenario guide live in `docs/specification/`. A402 and commerce-to-payment integration guides are grouped with the Alipay reference integration under `integrations/alipay/`. JSON Schemas, fixtures, and tests live in `code/schemas/`; they support implementation without adding requirements that are absent from the specification.

ACT 2.1 is available in both [Chinese](docs/specification/overview.md) and [English](docs/specification/overview.en.md). The English documents are official informative translations of the final 2.1 publication; if a translation discrepancy is found, the Chinese publication remains controlling until the translation is corrected in a subsequent repository release.

The overview and four domain specifications under `docs/specification/` are the versioned ACT 2.1 normative publication; the scenario guide is non-normative. [act-protocol.com](https://www.act-protocol.com/) provides project information and the online demo; it does not replace the versioned specification in this repository.

## Repository layout

```text
docs/specification/   ACT 2.1 specification and non-normative scenarios
code/schemas/         Machine-readable implementation artifacts
code/samples/         Runnable protocol samples
code/web-client/      Interactive demo
integrations/tsd-crd/ TSD-CRD reference implementation guidance
integrations/alipay/  Integration guides, Alipay reference code, and validation
tools/                Repository quality and release tooling
```

The dependency direction is specification → artifacts → product integration → sample/demo. Product code, demos, and repository tools do not define ACT semantics.

## Online demo

Open the [ACT website demo](https://www.act-protocol.com/demo) to experience the protocol flow without downloading or installing anything. The website demo is an interactive walkthrough, not a payment implementation or conformance certification.

## Run locally

The following Node.js programs have no third-party runtime dependencies, so `npm install` is not required. Download or clone the repository and run the commands from its root.

### Local A402 Sample

Requires Node.js 18 or later:

```bash
npm --prefix code/samples/local-a402 run local
```

The sample returns `402 Payment Required`, decodes `Payment-Needed`, and verifies that a fake `Payment-Proof` does not deliver the paid resource. It never connects to a payment product or performs payment.

### TSD-CRD Reference Implementation

Requires Node.js 22.18 or later. Run its tests, baseline conformance checks, and local demo:

```bash
npm --prefix code/samples/tsd-crd-reference run check
npm --prefix code/samples/tsd-crd-reference run demo
```

It uses Mock providers, in-memory state, temporary test keys, and the optional non-normative `reference-v1` machine profile. Passing its tests is not a claim of full ACT 2.1 conformance or production readiness.

### Web Showcase

Requires Node.js 18 or later. To inspect or modify the interactive demo locally, run:

```bash
npm --prefix code/web-client/alipay-ai-pay-showcase run demo
```

Open `http://127.0.0.1:4173/`. The local Showcase explains the protocol flow and is not a payment implementation or conformance certification.

## Alipay reference integration

`integrations/alipay/` separates the two sides of the product integration:

- `buyer-agent/` checks the environment and hands off to the buyer wallet and payment package `@alipay/agent-payment`.
- `seller-java/` uses the Alipay Java SDK for Machine Pay proof verification and fulfillment confirmation. The official seller integration assistant `@alipay/alipay-aipay` is referenced as an external tool only.
- `validation/` provides sandbox preflight and sanitized evidence guidance.

For Alipay onboarding, credentials, sandbox operation, and current product behavior, use the [AIPay website](https://aipay.alipay.com/callpay) and its [official integration guide](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html).

## Quality checks

Run all checks with Python 3, Node.js 22.18+, JDK 8+, and Maven 3.8+. The suite covers repository structure, internal links, key official external links, schemas, samples, integrations, and the demo:

```bash
./tools/verify.sh
```

See [CONTRIBUTING.en.md](CONTRIBUTING.en.md), [SECURITY.md](SECURITY.md), and [CODE_OF_CONDUCT.en.md](CODE_OF_CONDUCT.en.md). Documentation is licensed under CC BY 4.0; code is licensed under Apache License 2.0. Copyright Ant Group Co., Ltd.
