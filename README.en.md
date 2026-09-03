# ACT Protocol

[简体中文](README.md) | English

ACT (Agentic Commerce Trust Protocol) is an open protocol for agentic commerce. ACT 2.1 defines four cooperating domains: Authorization & Delegation, Commerce Interaction, Payment Services, and Trust Services. This repository uses an agent discovering and purchasing paid digital resources as its end-to-end scenario, while keeping the specification, product-neutral safety sample, interactive demo, and Alipay reference integration separate.

## Start here

| Goal | Entry |
|---|---|
| Read ACT 2.1 | [Specification overview](docs/specification/overview.en.md) |
| Understand end-to-end flows | [Scenarios and Business Flows](docs/specification/scenarios.en.md) |
| Run the safe local A402 sample | [Local A402 Sample](code/samples/local-a402/README.md) |
| Explore the interactive flow | [Web Showcase](code/web-client/alipay-ai-pay-showcase/README.md) |
| Integrate Alipay | [Alipay Reference Integration](integrations/alipay/README.md) |

For a first visit: read the [English overview](docs/specification/overview.en.md), keep the [bilingual glossary](docs/glossary.md) open, run the local sample, and then choose the buyer or seller Alipay integration. The local sample intentionally demonstrates safe rejection rather than manufacturing payment success; a successful paid delivery requires verified proof from the official product workflow.

The five human-readable specification documents and the non-normative scenario guide live in `docs/specification/`. A402 and commerce-to-payment integration guides are grouped with the Alipay reference integration under `integrations/alipay/`. JSON Schemas, fixtures, and tests live in `code/schemas/`; they support implementation without adding requirements that are absent from the specification.

ACT 2.1 is available in both [Chinese](docs/specification/overview.md) and [English](docs/specification/overview.en.md). The English documents are official informative translations of the final 2.1 publication; if a translation discrepancy is found, the Chinese publication remains controlling until the translation is corrected in a subsequent repository release.

The overview and four domain specifications under `docs/specification/` are the sole versioned ACT 2.1 normative publication in this repository release; the scenario guide is explicitly non-normative. [act-protocol.com](https://www.act-protocol.com/) is a project-information entry point. Website content that is not explicitly labeled ACT 2.1 is informative and is not a normative source for this release. If a web page omits a component, uses a different structure, or conflicts with this release, it MUST NOT override or interpret the repository's ACT 2.1 requirements.

## Repository layout

```text
docs/specification/   ACT 2.1 specification and non-normative scenarios
code/schemas/         Machine-readable implementation artifacts
code/samples/         Runnable protocol samples
code/web-client/      Interactive demo
integrations/alipay/  Integration guides, Alipay reference code, and validation
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

See [CONTRIBUTING.en.md](CONTRIBUTING.en.md), [SECURITY.md](SECURITY.md), and [CODE_OF_CONDUCT.en.md](CODE_OF_CONDUCT.en.md). Documentation is licensed under CC BY 4.0; code is licensed under Apache License 2.0. Copyright Ant Group Co., Ltd.
