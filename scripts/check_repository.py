#!/usr/bin/env python3
"""Run dependency-free repository integrity checks.

This checker deliberately validates only facts that can be established without
installing project dependencies: local Markdown links, UTF-8/JSON syntax,
Python syntax and required Quickstart structure. Semantic conformance is tracked
separately.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {
    ".git",
    ".tmp",
    ".venv",
    "node_modules",
    "__pycache__",
    "output",
    "target",
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


def repository_files(pattern: str) -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob(pattern)
        if not any(part in IGNORED_PARTS for part in path.parts)
    )


def decode_text(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid UTF-8 ({exc})")
        return None


def markdown_link_errors() -> list[str]:
    errors: list[str] = []
    for path in repository_files("*.md"):
        text = decode_text(path, errors)
        if text is None:
            continue

        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]

            # Markdown titles are not currently used for local repository links.
            # Strip a quoted title if one is added later.
            target = re.split(r"\s+[\"']", target, maxsplit=1)[0]
            parsed = urlparse(target)
            if parsed.scheme or target.startswith("#"):
                continue

            relative_target = unquote(parsed.path)
            if not relative_target:
                continue

            resolved = (
                ROOT / relative_target.lstrip("/")
                if relative_target.startswith("/")
                else path.parent / relative_target
            ).resolve()

            if not resolved.exists():
                errors.append(
                    f"{path.relative_to(ROOT)}: broken local link -> {relative_target}"
                )
    return errors


def json_errors() -> list[str]:
    errors: list[str] = []
    for path in repository_files("*.json"):
        text = decode_text(path, errors)
        if text is None:
            continue
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            errors.append(
                f"{path.relative_to(ROOT)}: invalid JSON at "
                f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
            )
    return errors


def python_syntax_errors() -> list[str]:
    errors: list[str] = []
    for path in repository_files("*.py"):
        text = decode_text(path, errors)
        if text is None:
            continue
        try:
            compile(text, str(path), "exec")
        except SyntaxError as exc:
            errors.append(
                f"{path.relative_to(ROOT)}: Python syntax error at "
                f"line {exc.lineno}: {exc.msg}"
            )
    return errors


def repository_structure_errors() -> list[str]:
    required = [
        "CHANGELOG.md",
        "release-manifest.json",
        "docs/README.md",
        "specs/README.md",
        "profiles/README.md",
        "LICENSE-APACHE-2.0",
        "LICENSE-CC-BY-4.0",
        "bindings/http-a402/README.md",
        "profiles/alipay-ai-pay/bindings/skill-cli/README.md",
        "profiles/alipay-ai-pay/schemas/payment-needed.preview.schema.json",
        "profiles/alipay-ai-pay/schemas/payment-proof.preview.schema.json",
        "profiles/alipay-ai-pay/schemas/payment-verification-result.preview.schema.json",
        "profiles/alipay-ai-pay/schemas/error-mapping.preview.json",
        "profiles/alipay-ai-pay/profile-review-status.json",
        "quickstarts/alipay/README.md",
        "quickstarts/alipay/agent-payment/package.json",
        "quickstarts/alipay/agent-payment/preflight.mjs",
        "quickstarts/alipay/metered-rest-provider/pom.xml",
        "quickstarts/alipay/metered-rest-provider/.env.example",
        "quickstarts/alipay/metered-rest-provider/run.sh",
        "quickstarts/alipay/end-to-end-402/package.json",
        "quickstarts/alipay/end-to-end-402/inspect-402.mjs",
        "quickstarts/alipay/end-to-end-402/local-golden-path.mjs",
        "quickstarts/alipay/end-to-end-402/local-preview.http",
        "quickstarts/alipay/end-to-end-402/sandbox-preflight.mjs",
        "quickstarts/alipay/end-to-end-402/sandbox-preflight.test.mjs",
        "specs/2.1/assertions/a402-core-assertions.json",
        "specs/2.1/assertions/features/a402-local-preview.feature",
        "specs/2.1/schemas/a402/README.md",
        "specs/2.1/schemas/a402/payment-needed.schema.json",
        "specs/2.1/schemas/a402/payment-proof.schema.json",
        "specs/2.1/schemas/a402/payment-validation.schema.json",
        "specs/2.1/schemas/a402/error.schema.json",
        "specs/2.1/schemas/a402/error-catalog.json",
        "specs/2.1/fixtures/a402/valid/payment-needed.json",
        "specs/2.1/fixtures/a402/valid/payment-proof.json",
        "specs/2.1/fixtures/a402/valid/payment-validation.json",
        "scripts/validate_a402_contract.py",
        "demos/alipay-ai-pay-sandbox-showcase/README.md",
        "demos/alipay-ai-pay-sandbox-showcase/public/index.html",
        "demos/alipay-ai-pay-sandbox-showcase/public/app.js",
        "demos/alipay-ai-pay-sandbox-showcase/bridge-server.mjs",
        "docs/project/releases/2026-bund-payment-open-source-plan.md",
        "docs/project/releases/2026-07-31-july-preview.md",
        "docs/project/releases/2026-08-03-candidate-publication.md",
        "docs/project/releases/release-readiness.json",
        "scripts/release_readiness.py",
        "profiles/alipay-ai-pay/sources/audits/2026-08-03-product-update.md",
        "docs/project/decisions/README.md",
        "docs/project/decisions/protocol-decision-brief.md",
        "docs/project/decisions/a402-decision-register.json",
        "docs/project/decisions/a402-decision-register.schema.json",
        "docs/project/decisions/candidate-machine-contract-resolution-2026-08-03.md",
        "docs/project/decisions/adr-template.md",
        "docs/project/decisions/a402-review-guide.md",
        "docs/project/decisions/a402-review-minutes-template.md",
        ".github/ISSUE_TEMPLATE/a402-protocol-decision.md",
        "docs/project/releases/evidence/2026-08-03-sandbox-preflight.json",
    ]
    errors = [
        f"missing required repository asset: {path}"
        for path in required
        if not (ROOT / path).is_file()
    ]
    forbidden_directories = ["impl", "conformance", "reference-implementations"]
    errors.extend(
        f"obsolete or empty top-level directory must not be published: {path}"
        for path in forbidden_directories
        if (ROOT / path).exists()
    )
    removed_legacy_assets = [
        "specs/2.0",
        "examples/2.0",
        "specs/2.1/migration-from-2.0.md",
    ]
    errors.extend(
        f"legacy ACT asset must not be published: {path}"
        for path in removed_legacy_assets
        if (ROOT / path).exists()
    )
    return errors


def payment_services_domain_errors() -> list[str]:
    """Protect the completed PSD source alignment from silent regression."""

    # A402-CAND-001 / PSD-CAND-001: A402 remains independent and the PSD
    # inventory retains six distinct components across Core and Profile.
    errors: list[str] = []
    expected_components = {
        "PSD-PMT-BND",
        "PSD-AGT-SUB",
        "PSD-PAY-INS",
        "PSD-PAY-DEL",
        "PSD-PAY-AUP",
        "PSD-PAY-A402",
    }
    completed_source_url = (
        "https://yuque.antfin.com/hknzlf/fvle20/dve0b9g2u1t3cs33"
    )
    revision_history_url = (
        "https://yuque.antfin.com/hknzlf/fvle20/dh5iwcigwa65hkds"
    )

    tracked_paths = [
        ROOT / "specs/2.1/overview.md",
        ROOT / "specs/2.1/payment-services-domain-spec.md",
        ROOT / "specs/2.1/a402-binding.md",
        ROOT / "specs/2.1/revision-status.md",
    ]
    tracked_texts: dict[Path, str] = {}
    for path in tracked_paths:
        text = decode_text(path, errors)
        if text is None:
            continue
        tracked_texts[path] = text
        for source_url in (completed_source_url, revision_history_url):
            if source_url not in text:
                errors.append(
                    f"{path.relative_to(ROOT)}: missing PSD source {source_url}"
                )

    revision_status = tracked_texts.get(ROOT / "specs/2.1/revision-status.md", "")
    for source_fact in (
        "2026-08-03T07:05:44.000Z",
        "2026-08-03T07:05:43.000Z",
        "8d39bbafe0bd5c344a78355c4a68371e07b927cc97bb394b3fdbfb0bfb776d06",
        "16,197",
    ):
        if source_fact not in revision_status:
            errors.append(
                "specs/2.1/revision-status.md: missing completed PSD source fact "
                f"{source_fact}"
            )
    for closed_pending in ("PD-2.1-001", "PD-2.1-002", "PD-2.1-008"):
        closed_section = revision_status.partition(
            "## 4. 已由完成版协议关闭的旧 Pending"
        )[2].partition("## 5. 剩余 Pending Decision")[0]
        if closed_pending not in closed_section:
            errors.append(
                "specs/2.1/revision-status.md: completed PSD source must close "
                f"{closed_pending}"
            )

    for relative_path in (
        "specs/2.1/overview.md",
        "specs/2.1/payment-services-domain-spec.md",
    ):
        path = ROOT / relative_path
        text = tracked_texts.get(path, "")
        missing = sorted(component for component in expected_components if component not in text)
        if missing:
            errors.append(
                f"{relative_path}: incomplete PSD component inventory; missing {missing}"
            )

    profile_path = ROOT / "profiles/alipay-ai-pay/mappings/domains.md"
    profile_text = decode_text(profile_path, errors) or ""
    profile_components = set(
        re.findall(r"PSD-(?:PMT|AGT|PAY)-[A-Z0-9]+", profile_text)
    )
    missing_profile_components = sorted(expected_components - profile_components)
    unknown_profile_components = sorted(profile_components - expected_components)
    if missing_profile_components:
        errors.append(
            f"{profile_path.relative_to(ROOT)}: missing PSD mappings "
            f"{missing_profile_components}"
        )
    if unknown_profile_components:
        errors.append(
            f"{profile_path.relative_to(ROOT)}: references unknown PSD components "
            f"{unknown_profile_components}"
        )

    a402_path = ROOT / "specs/2.1/a402-binding.md"
    a402_text = tracked_texts.get(a402_path, "")
    base_fields = {
        "method_id",
        "out_trade_no",
        "amount",
        "currency",
        "resource_id",
        "pay_before",
        "seller_unique_id",
        "buyer_unique_id",
        "payment_proof",
        "trade_no",
        "expires_at",
        "signer_id",
        "signature_content",
        "signature_type",
    }
    missing_fields = sorted(
        field for field in base_fields if f"`{field}`" not in a402_text
    )
    if missing_fields:
        errors.append(
            f"{a402_path.relative_to(ROOT)}: missing inherited Candidate fields "
            f"{missing_fields}"
        )

    states = {
        "CREATE",
        "WAIT_BUYER_PAY",
        "WAIT_SELLER_FULFILLMENT",
        "WAIT_BUYER_RECEIPT",
        "TRADE_FINISHED",
        "TRADE_CLOSED",
    }
    missing_states = sorted(state for state in states if f"`{state}`" not in a402_text)
    if missing_states:
        errors.append(
            f"{a402_path.relative_to(ROOT)}: missing inherited transaction states "
            f"{missing_states}"
        )
    expected_transitions = (
        "| `CREATE` |",
        "`WAIT_SELLER_FULFILLMENT`、`TRADE_CLOSED`",
        "`WAIT_BUYER_RECEIPT`、`TRADE_CLOSED`",
        "`TRADE_FINISHED`、`TRADE_CLOSED`",
    )
    for transition in expected_transitions:
        if transition not in a402_text:
            errors.append(
                f"{a402_path.relative_to(ROOT)}: missing inherited state transition "
                f"{transition}"
            )

    error_categories = (
        "签名校验错误",
        "请求参数错误",
        "协议/方法错误",
        "Agent/服务方身份错误",
        "额度与资产错误",
        "限权与风控错误",
        "交易状态错误",
        "退款错误",
        "履约回执错误",
        "Proof 验证错误",
        "系统错误",
    )
    for category in error_categories:
        if category not in a402_text:
            errors.append(
                f"{a402_path.relative_to(ROOT)}: missing inherited error category "
                f"{category}"
            )

    seller_script_path = (
        ROOT / "quickstarts/alipay/metered-rest-provider/run.sh"
    )
    seller_script = decode_text(seller_script_path, errors) or ""
    for mode in ("init", "test", "package", "run"):
        if mode not in seller_script:
            errors.append(
                f"{seller_script_path.relative_to(ROOT)}: missing mode {mode}"
            )

    assertion_path = ROOT / "specs/2.1/assertions/a402-core-assertions.json"
    assertion_text = decode_text(assertion_path, errors) or ""
    for assertion_id in (
        "PSD-CAND-001",
        "PSD-CAND-002",
        "PSD-CAND-003",
        "PSD-CAND-004",
        "PSD-CAND-005",
    ):
        if assertion_id not in assertion_text:
            errors.append(
                f"{assertion_path.relative_to(ROOT)}: missing {assertion_id}"
            )

    return errors


def markdown_heading_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    duplicates: dict[str, int] = {}
    for heading in MARKDOWN_HEADING.findall(text):
        slug = heading.strip().lower()
        slug = re.sub(r"[^\w\u4e00-\u9fff -]", "", slug)
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        duplicate_number = duplicates.get(slug, 0)
        anchors.add(slug if duplicate_number == 0 else f"{slug}-{duplicate_number}")
        duplicates[slug] = duplicate_number + 1
    return anchors


def release_manifest_errors() -> list[str]:
    errors: list[str] = []
    manifest_path = ROOT / "release-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"release-manifest.json: cannot validate ({exc})"]

    if manifest.get("manifest_version") != "1":
        errors.append("release-manifest.json: manifest_version must be '1'")

    components = manifest.get("components")
    if not isinstance(components, dict) or not components:
        return errors + ["release-manifest.json: components must be a non-empty object"]

    for component_id, component in components.items():
        if not isinstance(component, dict):
            errors.append(f"release-manifest.json: component {component_id} must be an object")
            continue
        for field in ("kind", "version", "status", "path", "normative", "depends_on"):
            if field not in component:
                errors.append(
                    f"release-manifest.json: component {component_id} is missing {field}"
                )
        component_path = component.get("path")
        if isinstance(component_path, str) and not (ROOT / component_path).is_file():
            errors.append(
                f"release-manifest.json: component {component_id} path does not exist: "
                f"{component_path}"
            )
        dependencies = component.get("depends_on", [])
        if not isinstance(dependencies, list):
            errors.append(
                f"release-manifest.json: component {component_id} depends_on must be an array"
            )
        else:
            for dependency in dependencies:
                if dependency not in components:
                    errors.append(
                        f"release-manifest.json: component {component_id} references "
                        f"unknown dependency {dependency}"
                    )

    candidate = components.get("act-2.1", {})
    if candidate.get("normative") is not False:
        errors.append("release-manifest.json: act-2.1 must remain non-normative")
    if candidate.get("status") != "candidate-working-draft":
        errors.append(
            "release-manifest.json: act-2.1 status must be candidate-working-draft"
        )
    if "act-2.0" in components:
        errors.append("release-manifest.json: legacy act-2.0 must not be published")

    readiness = manifest.get("release_readiness")
    if not isinstance(readiness, dict):
        errors.append("release-manifest.json: release_readiness must be an object")
    else:
        readiness_path = readiness.get("path")
        if not isinstance(readiness_path, str) or not (ROOT / readiness_path).is_file():
            errors.append(
                "release-manifest.json: release_readiness.path must reference "
                "an existing file"
            )
        if isinstance(readiness_path, str) and (ROOT / readiness_path).is_file():
            try:
                readiness_state = json.loads(
                    (ROOT / readiness_path).read_text(encoding="utf-8")
                ).get("publication_status")
            except json.JSONDecodeError:
                readiness_state = None
            if readiness.get("status") != readiness_state:
                errors.append(
                    "release-manifest.json: release_readiness.status must match "
                    "the readiness document publication_status"
                )

    return errors


def release_readiness_errors() -> list[str]:
    errors: list[str] = []
    readiness_path = ROOT / "docs/project/releases/release-readiness.json"
    try:
        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{readiness_path.relative_to(ROOT)}: cannot validate ({exc})"]

    if readiness.get("readiness_version") != "1":
        errors.append(
            f"{readiness_path.relative_to(ROOT)}: readiness_version must be '1'"
        )

    gates = readiness.get("gates")
    if not isinstance(gates, list) or not gates:
        return errors + [f"{readiness_path.relative_to(ROOT)}: gates must not be empty"]

    allowed_statuses = {
        "passed",
        "pending-local",
        "blocked-external",
        "not-started",
    }
    targets = readiness.get("targets")
    required_targets = {
        "act-candidate-publication",
        "alipay-profile-preview",
        "alipay-sandbox-verified",
        "act-sep-candidate",
    }
    if not isinstance(targets, dict) or set(targets) != required_targets:
        errors.append(
            f"{readiness_path.relative_to(ROOT)}: targets must be "
            f"{sorted(required_targets)}"
        )
        targets = {}
    for target_id, target in targets.items():
        if not isinstance(target, dict) or not isinstance(target.get("allowed_claim"), str):
            errors.append(
                f"{readiness_path.relative_to(ROOT)}: {target_id} needs allowed_claim"
            )

    required_publication_gates = {
        "protocol-sources",
        "candidate-content",
        "local-verification",
        "legal",
        "security-reporting",
        "public-distribution",
        "release-snapshot",
        "protocol-decisions",
        "core-machine-contract",
    }
    actual_ids: set[str] = set()
    publication_blockers = []
    for gate in gates:
        if not isinstance(gate, dict):
            errors.append(
                f"{readiness_path.relative_to(ROOT)}: each gate must be an object"
            )
            continue
        gate_id = gate.get("id")
        if not isinstance(gate_id, str):
            errors.append(
                f"{readiness_path.relative_to(ROOT)}: gate is missing a string id"
            )
            continue
        if gate_id in actual_ids:
            errors.append(
                f"{readiness_path.relative_to(ROOT)}: duplicate gate {gate_id}"
            )
        actual_ids.add(gate_id)
        if gate.get("status") not in allowed_statuses:
            errors.append(
                f"{readiness_path.relative_to(ROOT)}: {gate_id} has invalid status"
            )
        required_for = gate.get("required_for")
        if not isinstance(required_for, list) or not required_for:
            errors.append(
                f"{readiness_path.relative_to(ROOT)}: {gate_id} needs required_for"
            )
            required_for = []
        else:
            unknown_targets = sorted(set(required_for) - required_targets)
            if unknown_targets:
                errors.append(
                    f"{readiness_path.relative_to(ROOT)}: {gate_id} references "
                    f"unknown targets {unknown_targets}"
                )
        evidence = gate.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(
                f"{readiness_path.relative_to(ROOT)}: {gate_id} needs evidence"
            )
        else:
            for evidence_path in evidence:
                if not isinstance(evidence_path, str) or not (ROOT / evidence_path).is_file():
                    errors.append(
                        f"{readiness_path.relative_to(ROOT)}: {gate_id} evidence "
                        f"does not exist: {evidence_path}"
                    )
        if (
            "act-candidate-publication" in required_for
            and gate.get("status") != "passed"
        ):
            publication_blockers.append(gate_id)

    missing_publication_gates = sorted(required_publication_gates - actual_ids)
    if missing_publication_gates:
        errors.append(
            f"{readiness_path.relative_to(ROOT)}: missing ACT Candidate publication "
            f"gates {missing_publication_gates}"
        )
    if publication_blockers and readiness.get("publication_status") != "blocked":
        errors.append(
            f"{readiness_path.relative_to(ROOT)}: publication_status must be blocked "
            f"while gates remain unresolved: {sorted(publication_blockers)}"
        )
    if not publication_blockers and readiness.get("publication_status") != "ready":
        errors.append(
            f"{readiness_path.relative_to(ROOT)}: publication_status must be ready "
            "after every ACT Candidate publication gate passes"
        )

    forbidden_claims = readiness.get("forbidden_claims")
    for claim in ("Stable", "Recommendation", "Production Certified"):
        if not isinstance(forbidden_claims, list) or claim not in forbidden_claims:
            errors.append(
                f"{readiness_path.relative_to(ROOT)}: missing forbidden claim {claim}"
            )

    return errors


def candidate_assertion_errors() -> list[str]:
    errors: list[str] = []
    catalog_path = ROOT / "specs/2.1/assertions/a402-core-assertions.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{catalog_path.relative_to(ROOT)}: cannot validate ({exc})"]

    if catalog.get("status") != "candidate-working-draft":
        errors.append(f"{catalog_path.relative_to(ROOT)}: invalid catalog status")
    if catalog.get("normative") is not False:
        errors.append(f"{catalog_path.relative_to(ROOT)}: must be non-normative")

    seen: set[str] = set()
    assertions = catalog.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        return errors + [f"{catalog_path.relative_to(ROOT)}: assertions must not be empty"]

    for assertion in assertions:
        assertion_id = assertion.get("id") if isinstance(assertion, dict) else None
        if not isinstance(assertion_id, str) or not re.fullmatch(
            r"[A-Z0-9]+-CAND-[0-9]{3}", assertion_id
        ):
            errors.append(
                f"{catalog_path.relative_to(ROOT)}: invalid assertion id {assertion_id!r}"
            )
            continue
        if assertion_id in seen:
            errors.append(
                f"{catalog_path.relative_to(ROOT)}: duplicate assertion id {assertion_id}"
            )
        seen.add(assertion_id)
        if assertion.get("status") != "candidate":
            errors.append(
                f"{catalog_path.relative_to(ROOT)}: {assertion_id} must be candidate"
            )
        if not assertion.get("statement"):
            errors.append(
                f"{catalog_path.relative_to(ROOT)}: {assertion_id} needs a statement"
            )
        for field in ("preconditions", "inputs", "expected_output"):
            value = assertion.get(field)
            if not isinstance(value, list) or not value or not all(
                isinstance(item, str) and item for item in value
            ):
                errors.append(
                    f"{catalog_path.relative_to(ROOT)}: {assertion_id} needs "
                    f"a non-empty {field} array"
                )

        source = assertion.get("source")
        if not isinstance(source, str) or "#" not in source:
            errors.append(
                f"{catalog_path.relative_to(ROOT)}: {assertion_id} needs "
                "a source path with an anchor"
            )
        else:
            source_path_text, source_anchor = source.split("#", 1)
            source_path = (catalog_path.parent / source_path_text).resolve()
            if not source_path.is_file():
                errors.append(
                    f"{catalog_path.relative_to(ROOT)}: {assertion_id} source "
                    f"does not exist: {source_path_text}"
                )
            else:
                source_text = decode_text(source_path, errors)
                if source_text is not None and source_anchor not in markdown_heading_anchors(
                    source_text
                ):
                    errors.append(
                        f"{catalog_path.relative_to(ROOT)}: {assertion_id} source "
                        f"anchor does not exist: {source}"
                    )

        executable_check = assertion.get("executable_check")
        if executable_check is not None:
            if not isinstance(executable_check, str) or "#" not in executable_check:
                errors.append(
                    f"{catalog_path.relative_to(ROOT)}: {assertion_id} has an "
                    "invalid executable_check"
                )
            else:
                executable_path_text, executable_token = executable_check.split("#", 1)
                executable_path = ROOT / executable_path_text
                if not executable_path.is_file():
                    errors.append(
                        f"{catalog_path.relative_to(ROOT)}: {assertion_id} executable "
                        f"path does not exist: {executable_path_text}"
                    )
                else:
                    executable_text = decode_text(executable_path, errors)
                    if executable_text is not None and executable_token not in executable_text:
                        errors.append(
                            f"{catalog_path.relative_to(ROOT)}: {assertion_id} executable "
                            f"token is missing: {executable_token}"
                        )

    feature_path = ROOT / "specs/2.1/assertions/features/a402-local-preview.feature"
    feature_text = decode_text(feature_path, errors) if feature_path.is_file() else None
    if feature_text is not None:
        for executable_id in ("A402-CAND-002", "A402-CAND-003"):
            if f"@{executable_id}" not in feature_text:
                errors.append(
                    f"{feature_path.relative_to(ROOT)}: missing tag @{executable_id}"
                )

    return errors


def profile_preview_schema_errors() -> list[str]:
    errors: list[str] = []
    schema_names = (
        "payment-needed.preview.schema.json",
        "payment-proof.preview.schema.json",
        "payment-verification-result.preview.schema.json",
    )
    schemas = {}
    for schema_name in schema_names:
        schema_path = ROOT / "profiles/alipay-ai-pay/schemas" / schema_name
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{schema_path.relative_to(ROOT)}: cannot validate ({exc})")
            continue
        schemas[schema_name] = schema
        if schema.get("x-act-status") != "preview-non-normative":
            errors.append(
                f"{schema_path.relative_to(ROOT)}: must remain preview-non-normative"
            )
        if schema.get("x-act-version") != "0.9-preview.1":
            errors.append(
                f"{schema_path.relative_to(ROOT)}: must use Profile 0.9-preview.1"
            )

    schema_path = ROOT / "profiles/alipay-ai-pay/schemas/payment-needed.preview.schema.json"
    schema = schemas.get("payment-needed.preview.schema.json", {})
    if schema.get("x-act-header") != "Payment-Needed":
        errors.append(f"{schema_path.relative_to(ROOT)}: unexpected header mapping")
    if schema.get("x-act-header-encoding") != "base64url":
        errors.append(f"{schema_path.relative_to(ROOT)}: unexpected header encoding")

    for section in ("protocol", "method"):
        section_schema = schema.get("properties", {}).get(section, {})
        required = section_schema.get("required")
        if not isinstance(required, list) or not required:
            errors.append(
                f"{schema_path.relative_to(ROOT)}: {section}.required must not be empty"
            )

    proof_schema = schemas.get("payment-proof.preview.schema.json", {})
    proof_protocol_required = (
        proof_schema.get("properties", {}).get("protocol", {}).get("required", [])
    )
    for field in ("payment_proof", "trade_no"):
        if field not in proof_protocol_required:
            errors.append(
                "profiles/alipay-ai-pay/schemas/payment-proof.preview.schema.json: "
                f"protocol must require {field}"
            )

    verification_schema = schemas.get(
        "payment-verification-result.preview.schema.json", {}
    )
    verification_required = verification_schema.get("required", [])
    for field in ("trade_no", "out_trade_no", "amount", "resource_id", "active"):
        if field not in verification_required:
            errors.append(
                "profiles/alipay-ai-pay/schemas/"
                "payment-verification-result.preview.schema.json: "
                f"must require {field}"
            )

    inspector_path = (
        ROOT / "quickstarts/alipay/end-to-end-402/inspect-402.mjs"
    )
    inspector_text = decode_text(inspector_path, errors)
    if inspector_text is not None:
        if "payment-needed.preview.schema.json" not in inspector_text:
            errors.append(
                f"{inspector_path.relative_to(ROOT)}: must consume the Profile Preview Schema"
            )
        if re.search(r"const REQUIRED_(PROTOCOL|METHOD)_FIELDS\s*=\s*\[", inspector_text):
            errors.append(
                f"{inspector_path.relative_to(ROOT)}: required fields must not be "
                "duplicated as hard-coded arrays"
            )

    review_path = ROOT / "profiles/alipay-ai-pay/profile-review-status.json"
    try:
        review_status = json.loads(review_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{review_path.relative_to(ROOT)}: cannot validate ({exc})")
    else:
        if review_status.get("profile_version") != "0.9-preview.1":
            errors.append(
                f"{review_path.relative_to(ROOT)}: must use Profile 0.9-preview.1"
            )
        items = review_status.get("items")
        expected_ids = {f"AP-{index:03d}" for index in range(1, 11)}
        actual_ids = (
            [item.get("id") for item in items if isinstance(item, dict)]
            if isinstance(items, list)
            else []
        )
        if len(actual_ids) != len(expected_ids) or set(actual_ids) != expected_ids:
            errors.append(
                f"{review_path.relative_to(ROOT)}: must contain AP-001 through AP-010 "
                "exactly once"
            )
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    errors.append(
                        f"{review_path.relative_to(ROOT)}: every review item must be an object"
                    )
                    continue
                item_id = item.get("id", "unknown")
                if not isinstance(item.get("safe_preview_rule"), str) or not item.get(
                    "safe_preview_rule"
                ):
                    errors.append(
                        f"{review_path.relative_to(ROOT)}: {item_id} needs a "
                        "safe_preview_rule"
                    )
                blocks = item.get("blocks")
                if not isinstance(blocks, list) or not blocks or not all(
                    isinstance(blocked_claim, str) and blocked_claim
                    for blocked_claim in blocks
                ):
                    errors.append(
                        f"{review_path.relative_to(ROOT)}: {item_id} needs a "
                        "non-empty blocks array"
                    )

    error_mapping_path = (
        ROOT / "profiles/alipay-ai-pay/schemas/error-mapping.preview.json"
    )
    core_error_catalog_path = ROOT / "specs/2.1/schemas/a402/error-catalog.json"
    try:
        error_mapping = json.loads(error_mapping_path.read_text(encoding="utf-8"))
        core_error_catalog = json.loads(
            core_error_catalog_path.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(
            f"{error_mapping_path.relative_to(ROOT)}: cannot validate ({exc})"
        )
    else:
        if error_mapping.get("x-act-status") != "preview-non-normative":
            errors.append(
                f"{error_mapping_path.relative_to(ROOT)}: must remain "
                "preview-non-normative"
            )
        if error_mapping.get("x-act-version") != "0.9-preview.1":
            errors.append(
                f"{error_mapping_path.relative_to(ROOT)}: must use Profile 0.9-preview.1"
            )
        core_error_ids = {
            entry.get("error_id")
            for entry in core_error_catalog.get("errors", [])
            if isinstance(entry, dict)
        }
        mappings = error_mapping.get("mappings")
        mapping_keys: list[tuple[object, object]] = []
        if not isinstance(mappings, list) or not mappings:
            errors.append(
                f"{error_mapping_path.relative_to(ROOT)}: mappings must not be empty"
            )
        else:
            for mapping in mappings:
                if not isinstance(mapping, dict):
                    errors.append(
                        f"{error_mapping_path.relative_to(ROOT)}: every mapping must be an object"
                    )
                    continue
                key = (mapping.get("operation"), mapping.get("product_error"))
                mapping_keys.append(key)
                if mapping.get("core_error_id") not in core_error_ids:
                    errors.append(
                        f"{error_mapping_path.relative_to(ROOT)}: {key} references "
                        "an unknown Core error"
                    )
                actions = mapping.get("profile_actions")
                if not isinstance(actions, list) or not actions:
                    errors.append(
                        f"{error_mapping_path.relative_to(ROOT)}: {key} needs "
                        "profile_actions"
                    )
            if len(mapping_keys) != len(set(mapping_keys)):
                errors.append(
                    f"{error_mapping_path.relative_to(ROOT)}: duplicate operation/error mapping"
                )

    return errors


def repository_hygiene_errors() -> list[str]:
    errors: list[str] = []
    gitignore_path = ROOT / ".gitignore"
    gitignore_text = decode_text(gitignore_path, errors)
    if gitignore_text is not None:
        patterns = {line.strip() for line in gitignore_text.splitlines()}
        for required_pattern in (".tmp/", "output/", "target/"):
            if required_pattern not in patterns:
                errors.append(f".gitignore: missing {required_pattern}")

    public_roots = [ROOT / "docs/getting-started", ROOT / "quickstarts"]
    for public_root in public_roots:
        for path in sorted(public_root.rglob("*.md")):
            text = decode_text(path, errors)
            if text is None:
                continue
            for internal_name in ("观岳", "念箴"):
                if internal_name in text:
                    errors.append(
                        f"{path.relative_to(ROOT)}: public onboarding must use "
                        f"a role, not internal owner name {internal_name}"
                    )
            if "大会 Demo" in text:
                errors.append(
                    f"{path.relative_to(ROOT)}: use Sandbox Showcase instead of 大会 Demo"
                )

    readme_path = ROOT / "README.md"
    readme_text = decode_text(readme_path, errors)
    if readme_text is not None:
        role_headings = (
            "我在开发 Agent，需要支付能力",
            "我提供收费 API、MCP Tool 或 Skill",
            "我要理解或实现 ACT",
        )
        for heading in role_headings:
            match = re.search(
                rf"^### {re.escape(heading)}\s*$([\s\S]*?)(?=^### |^## |\Z)",
                readme_text,
                re.MULTILINE,
            )
            if match is None:
                errors.append(f"README.md: missing role heading {heading}")
                continue
            link_count = len(MARKDOWN_LINK.findall(match.group(1)))
            if link_count > 2:
                errors.append(
                    f"README.md: role {heading} exposes {link_count} links; maximum is 2"
                )

    return errors


def a402_decision_register_errors() -> list[str]:
    errors: list[str] = []
    register_path = ROOT / "docs/project/decisions/a402-decision-register.json"
    try:
        register = json.loads(register_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{register_path.relative_to(ROOT)}: cannot validate ({exc})"]

    if register.get("register_version") != "1":
        errors.append(f"{register_path.relative_to(ROOT)}: register_version must be '1'")
    register_status = register.get("status")
    if register_status not in {
        "ready-for-review",
        "partially-decided",
        "candidate-complete",
        "complete",
    }:
        errors.append(
            f"{register_path.relative_to(ROOT)}: invalid register status "
            f"{register_status!r}"
        )

    decisions = register.get("decisions")
    if not isinstance(decisions, list):
        return errors + [f"{register_path.relative_to(ROOT)}: decisions must be an array"]

    expected_ids = {f"DP-A402-{number:03d}" for number in range(1, 10)}
    actual_ids: set[str] = set()
    mapped_pending: list[str] = []
    decisions_by_id: dict[str, dict] = {}
    brief_path = ROOT / "docs/project/decisions/protocol-decision-brief.md"
    brief_text = decode_text(brief_path, errors)

    for decision in decisions:
        decision_id = decision.get("id") if isinstance(decision, dict) else None
        if not isinstance(decision_id, str):
            errors.append(f"{register_path.relative_to(ROOT)}: decision is missing id")
            continue
        if decision_id in actual_ids:
            errors.append(
                f"{register_path.relative_to(ROOT)}: duplicate decision {decision_id}"
            )
        actual_ids.add(decision_id)
        decisions_by_id[decision_id] = decision

        options = decision.get("options")
        option_ids = (
            [option.get("id") for option in options if isinstance(option, dict)]
            if isinstance(options, list)
            else []
        )
        if len(option_ids) < 2 or len(option_ids) != len(set(option_ids)):
            errors.append(
                f"{register_path.relative_to(ROOT)}: {decision_id} needs at least "
                "two unique options"
            )
        recommended = decision.get("recommended_option")
        if recommended is not None and recommended not in option_ids:
            errors.append(
                f"{register_path.relative_to(ROOT)}: {decision_id} recommends "
                f"unknown option {recommended}"
            )

        status = decision.get("status")
        decision_record = decision.get("decision_record")
        if status in {
            "source-settled",
            "candidate-accepted",
            "accepted",
            "rejected",
            "superseded",
        }:
            if not isinstance(decision_record, str):
                errors.append(
                    f"{register_path.relative_to(ROOT)}: terminal {decision_id} "
                    "must reference a decision record"
                )
            elif not (register_path.parent / decision_record).is_file():
                errors.append(
                    f"{register_path.relative_to(ROOT)}: {decision_id} ADR does not "
                    f"exist: {decision_record}"
                )
        elif decision_record is not None:
            errors.append(
                f"{register_path.relative_to(ROOT)}: non-accepted {decision_id} "
                "must not claim a decision_record"
            )

        mapped = decision.get("maps_pending_decisions")
        if not isinstance(mapped, list):
            errors.append(
                f"{register_path.relative_to(ROOT)}: {decision_id} "
                "maps_pending_decisions must be an array"
            )
        else:
            mapped_pending.extend(mapped)

        if brief_text is not None and not re.search(
            rf"^## (?:[0-9]+\.\s+)?{re.escape(decision_id)}：",
            brief_text,
            re.MULTILINE,
        ):
            errors.append(
                f"{brief_path.relative_to(ROOT)}: missing section for {decision_id}"
            )

    if actual_ids != expected_ids:
        errors.append(
            f"{register_path.relative_to(ROOT)}: decision IDs must be "
            f"{sorted(expected_ids)}, found {sorted(actual_ids)}"
        )

    for decision_id in ("DP-A402-002", "DP-A402-005"):
        status = decisions_by_id.get(decision_id, {}).get("status")
        if status == "needs-product-input":
            errors.append(
                f"{register_path.relative_to(ROOT)}: {decision_id} product facts "
                "may block an Alipay Profile mapping, but must not block review of "
                "the recommended Core/Binding separation"
            )

    decision_statuses = {
        decision.get("status")
        for decision in decisions
        if isinstance(decision, dict)
    }
    terminal_statuses = {
        "source-settled",
        "candidate-accepted",
        "accepted",
        "rejected",
        "superseded",
    }
    if register_status == "ready-for-review" and decision_statuses & terminal_statuses:
        errors.append(
            f"{register_path.relative_to(ROOT)}: use partially-decided after the "
            "first terminal decision"
        )
    if register_status == "complete" and not decision_statuses <= terminal_statuses:
        errors.append(
            f"{register_path.relative_to(ROOT)}: complete requires every decision "
            "to be accepted, rejected, or superseded"
        )
    if register_status == "candidate-complete" and not decision_statuses <= terminal_statuses:
        errors.append(
            f"{register_path.relative_to(ROOT)}: candidate-complete requires every "
            "decision to have a terminal Candidate or governance status"
        )
    if register_status == "candidate-complete" and "candidate-accepted" not in decision_statuses:
        errors.append(
            f"{register_path.relative_to(ROOT)}: candidate-complete must contain at "
            "least one candidate-accepted decision"
        )

    expected_mapped = {
        "PD-2.1-003",
        "PD-2.1-004",
        "PD-2.1-005",
        "PD-2.1-006",
        "PD-2.1-007",
        "PD-2.1-009",
        "PD-2.1-010",
    }
    if set(mapped_pending) != expected_mapped:
        errors.append(
            f"{register_path.relative_to(ROOT)}: mapped Pending Decisions must cover "
            f"{sorted(expected_mapped)}, found {sorted(set(mapped_pending))}"
        )
    if len(mapped_pending) != len(set(mapped_pending)):
        errors.append(
            f"{register_path.relative_to(ROOT)}: Pending Decision mappings "
            "must not be duplicated"
        )

    deferred = register.get("deferred_pending_decisions")
    deferred_ids = {
        item.get("id")
        for item in deferred
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    } if isinstance(deferred, list) else set()
    if deferred_ids != {"PD-2.1-011", "PD-2.1-012"}:
        errors.append(
            f"{register_path.relative_to(ROOT)}: deferred decisions must be "
            "PD-2.1-011 and PD-2.1-012"
        )

    baseline = register.get("accepted_baseline")
    if not isinstance(baseline, list) or not baseline:
        errors.append(
            f"{register_path.relative_to(ROOT)}: accepted_baseline must not be empty"
        )
    else:
        baseline_ids = {
            item.get("id")
            for item in baseline
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        expected_baseline_ids = {
            "BASE-A402-001",
            "BASE-A402-002",
            "BASE-A402-003",
            "BASE-A402-004",
            "BASE-A402-005",
            "BASE-A402-006",
        }
        if baseline_ids != expected_baseline_ids:
            errors.append(
                f"{register_path.relative_to(ROOT)}: accepted_baseline must preserve "
                "A402 independence, completed-source fields, six-state transitions, "
                "error/recovery categories, Header encoding, and optional validation"
            )
        for item in baseline:
            source = item.get("source") if isinstance(item, dict) else None
            if not isinstance(source, str) or "#" not in source:
                errors.append(
                    f"{register_path.relative_to(ROOT)}: baseline source needs an anchor"
                )
                continue
            source_path_text, source_anchor = source.split("#", 1)
            source_path = (register_path.parent / source_path_text).resolve()
            if not source_path.is_file():
                errors.append(
                    f"{register_path.relative_to(ROOT)}: baseline source missing: {source}"
                )
                continue
            source_text = decode_text(source_path, errors)
            if source_text is not None and source_anchor not in markdown_heading_anchors(
                source_text
            ):
                errors.append(
                    f"{register_path.relative_to(ROOT)}: baseline anchor missing: {source}"
                )

    return errors


def a402_review_workflow_errors() -> list[str]:
    errors: list[str] = []
    workflow_files = {
        "issue": ROOT / ".github/ISSUE_TEMPLATE/a402-protocol-decision.md",
        "guide": ROOT / "docs/project/decisions/a402-review-guide.md",
        "minutes": ROOT / "docs/project/decisions/a402-review-minutes-template.md",
        "contributing": ROOT / "CONTRIBUTING.md",
        "governance": ROOT / "GOVERNANCE.md",
    }
    texts: dict[str, str] = {}
    for name, path in workflow_files.items():
        text = decode_text(path, errors)
        if text is not None:
            texts[name] = text

    decision_ids = [f"DP-A402-{number:03d}" for number in range(1, 10)]
    for name in ("issue", "guide", "minutes"):
        text = texts.get(name)
        if text is None:
            continue
        for decision_id in decision_ids:
            if decision_id not in text:
                errors.append(
                    f"{workflow_files[name].relative_to(ROOT)}: missing {decision_id}"
                )

    issue_text = texts.get("issue", "")
    for required_phrase in (
        "推荐项不等于 Accepted",
        "Accept Option A",
        "Revise options",
        "Defer",
        "ADR path",
    ):
        if required_phrase not in issue_text:
            errors.append(
                f"{workflow_files['issue'].relative_to(ROOT)}: missing workflow "
                f"phrase {required_phrase!r}"
            )

    guide_text = texts.get("guide", "")
    for required_phrase in (
        "Recommendation pending governance confirmation",
        "Gate 1",
        "Accept / Defer 门槛",
        "DP-A402-001",
    ):
        if required_phrase not in guide_text:
            errors.append(
                f"{workflow_files['guide'].relative_to(ROOT)}: missing workflow "
                f"phrase {required_phrase!r}"
            )

    minutes_text = texts.get("minutes", "")
    for required_phrase in (
        "利益冲突披露",
        "Dissent and resolution",
        "Register and ADR updates",
        "Recommendation pending governance confirmation",
    ):
        if required_phrase not in minutes_text:
            errors.append(
                f"{workflow_files['minutes'].relative_to(ROOT)}: missing workflow "
                f"phrase {required_phrase!r}"
            )

    if "a402-protocol-decision.md" not in texts.get("contributing", ""):
        errors.append("CONTRIBUTING.md: missing A402 decision Issue template")
    if "a402-review-guide.md" not in texts.get("governance", ""):
        errors.append("GOVERNANCE.md: missing non-authoritative A402 review guide link")

    return errors


def main() -> int:
    checks = [
        ("Markdown local links", markdown_link_errors),
        ("UTF-8 and JSON syntax", json_errors),
        ("Python syntax", python_syntax_errors),
        ("Repository structure", repository_structure_errors),
        ("Completed PSD source alignment", payment_services_domain_errors),
        ("Release manifest", release_manifest_errors),
        ("Release readiness gates", release_readiness_errors),
        ("ACT 2.1 candidate assertions", candidate_assertion_errors),
        ("Alipay Profile Preview Schema", profile_preview_schema_errors),
        ("Repository hygiene", repository_hygiene_errors),
        ("A402 decision register", a402_decision_register_errors),
        ("A402 decision review workflow", a402_review_workflow_errors),
    ]
    failure_count = 0

    for name, check in checks:
        errors = check()
        if errors:
            failure_count += len(errors)
            print(f"[FAIL] {name}: {len(errors)} issue(s)")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"[PASS] {name}")

    if failure_count:
        print(f"\nRepository checks failed with {failure_count} issue(s).")
        return 1

    print("\nRepository checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
