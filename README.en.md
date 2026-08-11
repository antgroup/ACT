# ACT Protocol

[简体中文](README.md) | English

ACT (Agentic Commerce Trust Protocol) is an open protocol project for agentic commerce. The current implementation path is payment-services-first: the ACT 2.1 Candidate defines payment instruments, L1/L2/L3 authorization scenarios, and the independent A402 payment interaction; product profiles and runnable examples connect those semantics to public Alipay AI Pay capabilities.

> [!IMPORTANT]
> This repository contains an unreleased **ACT 2.1 Candidate Working Draft / Non-normative**. It is not Stable, a Recommendation, production certified, or an ACT conformance claim. The public tree intentionally excludes ACT 2.0 assets.

The [ACT Protocol website](https://www.act-protocol.com/) is the public protocol source of truth. Files under `specs/2.1/` are reviewable Candidate snapshots, not an authoritative website mirror. An official-page change requires a structure and semantic diff before this repository is updated.

## Choose your path

| Goal | Start here | What is authoritative |
|---|---|---|
| Add payment capability to an Agent | [Agent Payment Getting Started](docs/getting-started/agent-payment.md) | ACT Candidate for protocol semantics; the [Alipay wallet guide](https://aipay.alipay.com/wallet-guide) for product behavior |
| Charge for an API, MCP Tool, Skill, or digital resource | [Metered Payment Getting Started](docs/getting-started/metered-payment.md) | ACT Candidate and HTTP A402 Binding for protocol transport; the [Alipay metered-payment guide](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html) for product behavior |
| Understand ACT 2.1 | [Candidate overview](specs/2.1/overview.md) | The [ACT Protocol website](https://www.act-protocol.com/); `specs/2.1/` is the reviewable Candidate snapshot |
| Review status and publication gates | [Release readiness](governance/release-readiness.json) | Machine-readable component and gate state |

## One machine-payment loop

The buyer Agent requests a paid resource, the seller returns `402 Payment Required` plus `Payment-Needed`, the buyer pays through an official product capability and retries the original request with `Payment-Proof`, and the seller verifies the proof before delivering the resource and confirming fulfillment.

ACT keeps the layers separate:

- `specs/`: product-neutral Candidate semantics and A402 machine contracts;
- `integrations/bindings/`: cross-product transport bindings;
- `integrations/profiles/`: current product fields, APIs, errors, and workflows;
- `code/examples/`: runnable onboarding and validation paths;
- `code/web-client/`: a Guided Preview and sanitized evidence replay, not a payment implementation;
- `docs/`: developer guidance; `governance/`: decisions and release state.

Alipay's official site is the source of truth for wallet authorization, sandbox access, credentials, payment execution, verification, and fulfillment APIs. This repository links to that product environment; it does not reproduce it.

## Run locally

Run the safe, non-payable A402 Golden Path without credentials:

```bash
npm --prefix code/examples/alipay/end-to-end-402 run local
```

Run all repository, contract, example, and Showcase checks:

```bash
./scripts/verify.sh
```

## Maturity and contribution

The four ACT domains have semantic Candidate coverage. A402 additionally has Candidate JSON Schemas, fixtures, validation, errors, and state transitions. ADD, CID, and TSD do not yet publish stable wire schemas. L2/L3 are protocol Candidate scenarios and are not claimed as verified Alipay product capabilities.

Before contributing, read [CONTRIBUTING.md](CONTRIBUTING.md), [GOVERNANCE.md](GOVERNANCE.md), [MAINTAINERS.md](MAINTAINERS.md), and [SECURITY.md](SECURITY.md). No additional contributor agreement or sign-off is currently required. Security issues must be reported privately through [AntSRC](https://security.alipay.com/), not a public issue.

Copyright (c) 2026 Ant Group Co., Ltd. Specifications and documentation use CC BY 4.0; code, Schema, and executable examples use Apache 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
