# ACT Protocol Governance

ACT Protocol is an Ant Group open-source project. This document governs maintenance of the published ACT 2.1 specification and future protocol evolution.

## Principles

- Protocol discussions and decisions are public except for security or legally restricted material.
- ACT Core remains product-neutral. Product documentation cannot redefine protocol semantics.
- Changes preserve cross-domain consistency across ADD, CID, PSD and TSD.
- Normative text, implementation artifacts and product integrations are reviewed as separate layers.

## Roles

Maintainers listed in [MAINTAINERS.md](MAINTAINERS.md) review changes, keep releases coherent and resolve repository issues. Domain experts may review protocol changes. Additional maintainers are added through a public, recorded decision based on sustained contribution.

## Changes

- Editorial fixes and broken links may be merged with one maintainer approval.
- Clarifications must not add requirements and require review by a maintainer familiar with the affected domain.
- New fields, components, wire behavior or breaking changes require a public proposal, compatibility and security analysis, cross-domain review, implementation evidence where applicable, and an accepted decision record.
- Product integration changes require current official product sources and must not modify ACT Core to match one provider.

ACT 2.1 is final. Normative changes beyond errata are published in a new protocol version. Machine schemas in `code/` remain implementation artifacts unless a future specification explicitly incorporates them.

## Decisions and releases

Accepted protocol and project decisions are recorded in `governance/decisions/`. Release notes are recorded in `governance/releases/`. Every release must pass repository checks, preserve licensing and security guidance, and state the evidence behind implementation or interoperability claims.
