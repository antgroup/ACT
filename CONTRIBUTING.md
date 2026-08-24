# Contributing to ACT Protocol

Thank you for contributing. Read the [Code of Conduct](CODE_OF_CONDUCT.md), [governance rules](GOVERNANCE.md), and existing issues before starting.

## Repository map

- `docs/`: ACT 2.1 specification, flows and explanatory material.
- `code/`: machine artifacts, product-neutral samples and demos.
- `integrations/`: provider-specific integrations, including Alipay.
- `tools/`: active repository quality and release tooling; it does not define protocol semantics.

## Workflow

1. Open an issue for protocol semantics, new behavior or a breaking change. Security vulnerabilities must use the private channel in [SECURITY.md](SECURITY.md).
2. Keep each pull request focused and identify whether it changes protocol, implementation artifacts, a product integration or documentation.
3. Add tests appropriate to the change and run `./tools/verify.sh`.
4. Explain compatibility, security and source impact in the pull request.

ACT 2.1 is final. Typographical fixes and clarifications may update it without changing meaning; new normative behavior requires a future version and an accepted public decision. JSON Schema and examples must not silently expand normative requirements.

Product integrations must cite current official product sources, keep credentials out of the repository and avoid presenting local tests as real sandbox evidence.

Contributors confirm they have the right to submit their material. Accepted contributions use the license assigned to the relevant file or directory by [LICENSE](LICENSE). No additional CLA or DCO sign-off is currently required.
