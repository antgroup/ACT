# Copyright, licensing, and contribution policy

> Status: Accepted project policy / Non-normative  
> Updated: 2026-08-11

This record states the publication-safe project decision. It is not legal advice.

## Confirmed policy

- Copyright holder: `Ant Group Co., Ltd.`
- Specifications and documentation: Creative Commons Attribution 4.0 International, subject to the directory allocation in [`LICENSE`](../../LICENSE).
- Code, JSON Schema, fixtures, scripts, and executable examples: Apache License 2.0, subject to the directory allocation in [`LICENSE`](../../LICENSE).
- Inbound contributions: no additional contributor agreement or DCO sign-off is currently required. Contributors represent that they have the right to submit the material and accepted contributions use the license applicable to the contributed file or directory.

This removes the former signing and pull-request verification dependency. Normal review, provenance checks, third-party notice requirements, and maintainer approval still apply.

## Publication boundary

This decision is sufficient to describe ownership and outbound licensing in a public source snapshot. The following operational values remain external configuration and must not be guessed in repository content:

- public repository URL;
- public repository URL.

The private security reporting channel is [AntSRC](https://security.alipay.com/), operated by the Ant Group Security Emergency Response Center.

Their current state is machine-readable in [`publication-config.json`](../publication-config.json) and [`release-readiness.json`](../release-readiness.json).
