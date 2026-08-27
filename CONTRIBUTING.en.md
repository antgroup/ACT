# Contributing to ACT Protocol

[简体中文](CONTRIBUTING.md) | English

Thank you for contributing to ACT Protocol. Read the [Code of Conduct](CODE_OF_CONDUCT.en.md) and existing issues before starting.

## Submit a Change

1. Open an issue before proposing protocol semantics, new behavior, or a breaking change. Security vulnerabilities must use the private channel specified in [SECURITY.md](SECURITY.md).
2. Keep each pull request focused and identify whether it changes the protocol, machine-readable artifacts, a product integration, or documentation.
3. Add tests appropriate to the change and run `./tools/verify.sh`.
4. Explain compatibility and security impact in the pull request.

ACT 2.1 is final. Typographical corrections and clarifications that do not change meaning may be applied. New normative behavior must target a future protocol version. JSON Schema, integrations, and examples must not add requirements that are absent from the specification.

Product integrations must cite current official product sources, keep credentials out of the repository, and avoid presenting local tests as real sandbox evidence.

Contributors confirm that they have the right to submit their material. Accepted contributions use the license assigned to the relevant file or directory by [LICENSE](LICENSE). No additional CLA or DCO sign-off is currently required.
