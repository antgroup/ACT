# Contributing to ACT Protocol

[简体中文](CONTRIBUTING.md) | English

Thank you for contributing to ACT Protocol. Read the [Code of Conduct](CODE_OF_CONDUCT.en.md) and existing issues before starting.

## Choose the Right Entry Point

- Specification errata, clarifications, or proposals for a future version: [Specification issue template](.github/ISSUE_TEMPLATE/spec-issue.md)
- Samples, Schema, product integrations, demos, or tooling: [Implementation issue template](.github/ISSUE_TEMPLATE/implementation-issue.md)
- A change ready for submission: [Pull request template](.github/PULL_REQUEST_TEMPLATE.md)
- Security vulnerabilities: do not open a public issue; follow the private process in the [Security Policy](SECURITY.md)

## Submit a Change

1. Open an issue before proposing protocol semantics, new behavior, or a breaking change. Security vulnerabilities must use the private channel specified in [SECURITY.md](SECURITY.md).
2. Keep each pull request focused and identify whether it changes the protocol, machine-readable artifacts, a product integration, or documentation.
3. Add tests appropriate to the change and run `./tools/verify.sh`.
4. Explain compatibility and security impact in the pull request.

ACT 2.1 is final. Typographical corrections and clarifications that do not change meaning may be applied. New normative behavior must target a future protocol version. JSON Schema, integrations, and examples must not add requirements that are absent from the specification.

Product integrations must cite current official product sources, keep credentials out of the repository, and avoid presenting local tests as real sandbox evidence.

Contributors confirm that they have the right to submit their material. Accepted contributions use the license assigned to the relevant file or directory by [LICENSE](LICENSE). No additional CLA or DCO sign-off is currently required.

## AI-Assisted Contributions and Reviews

AI tools may be used to assist with code, specification text, documentation, tests, and reviews. They do not replace the judgment or responsibility of contributors and reviewers.

- Disclose the areas in which AI materially contributed to the pull request, such as code generation, translation, test generation, research organization, or review suggestions. Routine completion that did not produce material content does not need to be disclosed.
- Before submission, personally review generated content, run the appropriate tests, and take responsibility for accuracy, security, license compliance, and the final result.
- Do not provide secrets, tokens, payment credentials, personal information, unsanitized evidence, or other sensitive material to an AI service that has not been approved for that data.
- Do not directly rely on AI-generated protocol semantics, product APIs, error codes, links, citations, or compatibility conclusions. Verify each of them against the ACT specification, official product sources, and actual test results.
- Treat AI review output as advisory. Reviewers should pay particular attention to fabricated facts, missed edge cases, inadequate tests, insecure code, incorrect translations, and attempts to let machine artifacts or product behavior redefine protocol semantics.
- The pull request author remains responsible for the submitted content. The project maintainer makes the final acceptance decision.
