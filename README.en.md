# ACT Protocol

[简体中文](README.md) | English

ACT (Agentic Commerce Trust Protocol) is an open protocol for agentic commerce. ACT 2.1 defines four cooperating domains: Authorization & Delegation, Commerce Interaction, Payment Services, and Trust Services. This repository uses an agent discovering and purchasing paid digital resources as its end-to-end scenario, while keeping the specification, product-neutral safety sample, interactive demo, and Alipay reference integration separate.

## Start here

| Goal | Entry |
|---|---|
| Read ACT 2.1 | [Specification overview](docs/specification/overview.md) |
| Understand end-to-end flows | [Scenarios](docs/flows/scenarios.md) |
| Run the safe local A402 sample | [Local A402 Sample](code/samples/local-a402/README.md) |
| Explore the interactive flow | [Web Showcase](code/web-client/alipay-ai-pay-showcase/README.md) |
| Integrate Alipay | [Alipay Reference Integration](integrations/alipay/README.md) |

For a first visit: read the [overview](docs/specification/overview.md), keep the [bilingual glossary](docs/glossary.md) open, run the local sample, and then choose the buyer or seller Alipay integration. The local sample intentionally demonstrates safe rejection rather than manufacturing payment success; a successful paid delivery requires verified proof from the official product workflow.

Human-readable protocol text lives in `docs/specification/`. JSON Schemas, fixtures, and tests live in `code/schemas/`; they support implementation without adding requirements that are absent from the specification.

The normative ACT 2.1 specification in this release is currently published in Chinese. This English README is an informative navigation summary and does not replace the normative text.

The files under `docs/specification/` in this repository release are the versioned ACT 2.1 publication. [act-protocol.com](https://www.act-protocol.com/) is the continuously updated public protocol portal. If portal content differs from a repository release, interpret each by its stated version; unversioned portal content does not silently replace this release's ACT 2.1 text.

## Repository layout

```text
docs/                 ACT 2.1 specification, flows, and supporting material
code/schemas/         Machine-readable implementation artifacts
code/samples/         Runnable protocol samples
code/web-client/      Interactive demo
integrations/alipay/  Alipay reference integration and validation
governance/           Accepted project decisions and release records
tools/                Repository quality and release tooling
```

The dependency direction is specification → artifacts → product integration → sample/demo. Product code, demos, and repository tools do not define ACT semantics.

## Run locally

After downloading or cloning this repository, run from the repository root using Node.js 18 or later:

```bash
npm --prefix code/samples/local-a402 run local
npm --prefix code/web-client/alipay-ai-pay-showcase run demo
```

The local A402 sample performs no payment. The Showcase explains the protocol flow and does not constitute a payment implementation or conformance claim.

For Alipay onboarding, credentials, sandbox operation, and current product behavior, use the [AIPay website](https://aipay.alipay.com/callpay) and its [official integration guide](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html).

Run all checks with:

```bash
./tools/verify.sh
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [GOVERNANCE.md](GOVERNANCE.md), and [SECURITY.md](SECURITY.md). Documentation is licensed under CC BY 4.0; code is licensed under Apache License 2.0. Copyright Ant Group Co., Ltd.
