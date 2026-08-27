# Contributing to ACT Protocol

Thank you for contributing. Read the [Code of Conduct](CODE_OF_CONDUCT.md) and existing issues before starting.

## Submit a change

1. Open an issue before proposing protocol semantics, new behavior or a breaking change. Security vulnerabilities must use the private channel in [SECURITY.md](SECURITY.md).
2. Keep each pull request focused and identify whether it changes protocol, implementation artifacts, a product integration or documentation.
3. Add tests appropriate to the change and run `./tools/verify.sh`.
4. Explain compatibility and security impact in the pull request.

ACT 2.1 is final. Typographical corrections and clarifications may update it without changing meaning. New normative behavior must target a future protocol version. JSON Schema, integrations and examples must not add requirements that are absent from the specification.

Product integrations must cite current official product sources, keep credentials out of the repository and avoid presenting local tests as real sandbox evidence.

Contributors confirm they have the right to submit their material. Accepted contributions use the license assigned to the relevant file or directory by [LICENSE](LICENSE). No additional CLA or DCO sign-off is currently required.
