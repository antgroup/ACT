# Repository tools

This directory contains maintainer and CI tooling for the repository. These files are active infrastructure, not deprecated protocol implementations.

- `verify.sh`: the single local and CI verification entry point.
- `quality/check_repository.py`: repository structure, links, JSON, Python and release-wording checks.
- `quality/create_public_snapshot.py`: public-release snapshot and sensitive-content checks.
- `a402/validate_contract.py`: validation for the non-normative A402 schemas, fixtures and executable assertions.

Tools may validate protocol artifacts, but they do not define ACT semantics. Normative text remains under `docs/specification/`; machine-readable implementation artifacts remain under `code/schemas/`.
