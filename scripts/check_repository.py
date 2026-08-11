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
            document = json.loads(text)
        except json.JSONDecodeError as exc:
            errors.append(
                f"{path.relative_to(ROOT)}: invalid JSON at "
                f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
            )
            continue
        if isinstance(document, dict) and "$schema" in document and "$id" in document:
            if document["$id"] != path.name:
                errors.append(
                    f"{path.relative_to(ROOT)}: JSON Schema $id must be the local "
                    f"filename {path.name!r}, found {document['$id']!r}"
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
        "MAINTAINERS.md",
        "README.en.md",
        "release-manifest.json",
        "code/README.md",
        "docs/README.md",
        "governance/README.md",
        "integrations/README.md",
        "specs/README.md",
        "integrations/profiles/README.md",
        "LICENSE-APACHE-2.0",
        "LICENSE-CC-BY-4.0",
        "integrations/bindings/http-a402/README.md",
        "integrations/profiles/alipay-ai-pay/bindings/skill-cli/README.md",
        "integrations/profiles/alipay-ai-pay/schemas/payment-needed.preview.schema.json",
        "integrations/profiles/alipay-ai-pay/schemas/payment-proof.preview.schema.json",
        "integrations/profiles/alipay-ai-pay/schemas/payment-verification-result.preview.schema.json",
        "integrations/profiles/alipay-ai-pay/schemas/error-mapping.preview.json",
        "integrations/profiles/alipay-ai-pay/profile-review-status.json",
        "code/examples/alipay/README.md",
        "code/examples/alipay/agent-payment/package.json",
        "code/examples/alipay/agent-payment/run.sh",
        "code/examples/alipay/agent-payment/preflight.mjs",
        "code/examples/alipay/metered-rest-provider/pom.xml",
        "code/examples/alipay/metered-rest-provider/.env.example",
        "code/examples/alipay/metered-rest-provider/run.sh",
        "code/examples/alipay/end-to-end-402/package.json",
        "code/examples/alipay/end-to-end-402/run.sh",
        "code/examples/alipay/end-to-end-402/inspect-402.mjs",
        "code/examples/alipay/end-to-end-402/local-golden-path.mjs",
        "code/examples/alipay/end-to-end-402/local-preview.http",
        "code/examples/alipay/end-to-end-402/sandbox-preflight.mjs",
        "code/examples/alipay/end-to-end-402/sandbox-preflight.test.mjs",
        "specs/2.1/a402/assertions/a402-core-assertions.json",
        "specs/2.1/domains/authorization-delegation.md",
        "specs/2.1/domains/commerce-interaction.md",
        "specs/2.1/domains/trust-services.md",
        "specs/2.1/scenarios.md",
        "specs/2.1/a402/assertions/features/a402-local-preview.feature",
        "specs/2.1/a402/schemas/README.md",
        "specs/2.1/a402/schemas/payment-needed.schema.json",
        "specs/2.1/a402/schemas/payment-proof.schema.json",
        "specs/2.1/a402/schemas/payment-validation.schema.json",
        "specs/2.1/a402/schemas/error.schema.json",
        "specs/2.1/a402/schemas/error-catalog.json",
        "specs/2.1/a402/fixtures/valid/payment-needed.json",
        "specs/2.1/a402/fixtures/valid/payment-proof.json",
        "specs/2.1/a402/fixtures/valid/payment-validation.json",
        "scripts/validate_a402_contract.py",
        "code/web-client/alipay-ai-pay-showcase/README.md",
        "code/web-client/alipay-ai-pay-showcase/public/index.html",
        "code/web-client/alipay-ai-pay-showcase/public/app.js",
        "code/web-client/alipay-ai-pay-showcase/bridge-server.mjs",
        "governance/releases/2026-07-31-july-preview.md",
        "governance/releases/2026-08-03-candidate-publication.md",
        "governance/release-readiness.json",
        "governance/publication-config.json",
        "governance/decisions/legal-and-contribution-policy.md",
        "scripts/create_public_snapshot.py",
        "scripts/check_protocol_source_drift.py",
        "scripts/check_product_source_drift.py",
        ".github/workflows/product-source-drift.yml",
        "governance/protocol-sources.json",
        "scripts/release_readiness.py",
        "integrations/profiles/alipay-ai-pay/sources/audits/2026-08-08-product-update.md",
        "governance/decisions/README.md",
        "governance/decisions/protocol-decision-brief.md",
        "governance/decisions/a402-decision-register.json",
        "governance/decisions/a402-decision-register.schema.json",
        "governance/decisions/candidate-machine-contract-resolution-2026-08-03.md",
        "governance/decisions/adr-template.md",
        "governance/decisions/a402-review-guide.md",
        "governance/decisions/a402-review-minutes-template.md",
        ".github/ISSUE_TEMPLATE/a402-protocol-decision.md",
        "governance/releases/evidence/2026-08-03-sandbox-preflight.json",
    ]
    errors = [
        f"missing required repository asset: {path}"
        for path in required
        if not (ROOT / path).is_file()
    ]
    forbidden_directories = [
        "impl",
        "conformance",
        "reference-implementations",
        "bindings",
        "profiles",
        "quickstarts",
        "demos",
        "docs/project",
    ]
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


def protocol_source_registry_errors() -> list[str]:
    """Keep the public ACT source registry complete and free of placeholders."""

    path = ROOT / "governance/protocol-sources.json"
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"governance/protocol-sources.json: cannot validate ({exc})"]

    errors: list[str] = []
    if registry.get("authority") != "https://www.act-protocol.com/":
        errors.append("governance/protocol-sources.json: invalid ACT authority")
    if registry.get("source_of_truth") != "official-publication":
        errors.append("governance/protocol-sources.json: source_of_truth must be official-publication")
    expected_pages = {
        "overview": "https://www.act-protocol.com/documentation/overview",
        "scenarios": "https://www.act-protocol.com/documentation/scenarios",
        "delegation": "https://www.act-protocol.com/documentation/delegation",
        "commerce": "https://www.act-protocol.com/documentation/commerce",
        "payment": "https://www.act-protocol.com/documentation/payment",
        "trust": "https://www.act-protocol.com/documentation/trust",
    }
    pages = registry.get("pages")
    if not isinstance(pages, list):
        return errors + ["governance/protocol-sources.json: pages must be an array"]
    observed: dict[str, str] = {}
    for page in pages:
        if not isinstance(page, dict):
            errors.append("governance/protocol-sources.json: each page must be an object")
            continue
        page_id = page.get("id")
        if not isinstance(page_id, str) or page_id in observed:
            errors.append(f"governance/protocol-sources.json: invalid/duplicate page id {page_id!r}")
            continue
        observed[page_id] = page.get("url")
        if not re.fullmatch(r"[0-9a-f]{64}", str(page.get("visible_text_sha256", ""))):
            errors.append(
                f"governance/protocol-sources.json: {page_id} has no captured SHA-256"
            )
        if not page.get("title_marker"):
            errors.append(
                f"governance/protocol-sources.json: {page_id} has no title marker"
            )
    if observed != expected_pages:
        errors.append(
            "governance/protocol-sources.json: official page inventory does not match "
            f"{expected_pages}"
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
    completed_source_url = "https://www.act-protocol.com/documentation/payment"

    tracked_paths = [
        ROOT / "specs/2.1/overview.md",
        ROOT / "specs/2.1/domains/payment-services.md",
        ROOT / "specs/2.1/a402/specification.md",
        ROOT / "specs/2.1/revision-status.md",
    ]
    tracked_texts: dict[Path, str] = {}
    for path in tracked_paths:
        text = decode_text(path, errors)
        if text is None:
            continue
        tracked_texts[path] = text
        if completed_source_url not in text:
            errors.append(
                f"{path.relative_to(ROOT)}: missing PSD source {completed_source_url}"
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
        "specs/2.1/domains/payment-services.md",
    ):
        path = ROOT / relative_path
        text = tracked_texts.get(path, "")
        missing = sorted(component for component in expected_components if component not in text)
        if missing:
            errors.append(
                f"{relative_path}: incomplete PSD component inventory; missing {missing}"
            )

    profile_path = ROOT / "integrations/profiles/alipay-ai-pay/mappings/domains.md"
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

    a402_path = ROOT / "specs/2.1/a402/specification.md"
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
        ROOT / "code/examples/alipay/metered-rest-provider/run.sh"
    )
    seller_script = decode_text(seller_script_path, errors) or ""
    for mode in ("init", "test", "package", "run"):
        if mode not in seller_script:
            errors.append(
                f"{seller_script_path.relative_to(ROOT)}: missing mode {mode}"
            )

    assertion_path = ROOT / "specs/2.1/a402/assertions/a402-core-assertions.json"
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


def commerce_interaction_domain_errors() -> list[str]:
    """Protect the official CID source alignment from silent regression."""

    errors: list[str] = []
    source_url = "https://www.act-protocol.com/documentation/commerce"
    expected_components = {
        "CID-MER-CAT",
        "CID-INT-XFR",
        "CID-PCA-NEG",
        "CID-CART-CFM",
    }
    tracked_paths = [
        ROOT / "specs/2.1/overview.md",
        ROOT / "specs/2.1/domains/commerce-interaction.md",
        ROOT / "specs/2.1/domains/commerce-payment-negotiation.md",
        ROOT / "specs/2.1/revision-status.md",
        ROOT / "integrations/profiles/alipay-ai-pay/mappings/domains.md",
    ]
    tracked_texts: dict[Path, str] = {}
    for path in tracked_paths:
        text = decode_text(path, errors)
        if text is None:
            continue
        tracked_texts[path] = text
        if source_url not in text:
            errors.append(f"{path.relative_to(ROOT)}: missing CID source {source_url}")

    cid_path = ROOT / "specs/2.1/domains/commerce-interaction.md"
    cid_text = tracked_texts.get(cid_path, "")
    for marker in ("Candidate Working Draft", "Non-normative"):
        if marker not in cid_text:
            errors.append(f"{cid_path.relative_to(ROOT)}: missing status {marker}")
    missing_components = sorted(
        component for component in expected_components if component not in cid_text
    )
    if missing_components:
        errors.append(
            f"{cid_path.relative_to(ROOT)}: incomplete CID component inventory; "
            f"missing {missing_components}"
        )
    for semantic_field in (
        "capability_url",
        "negotiation_endpoint",
        "supported_methods",
        "method_id",
        "psp_id",
        "endpoint",
        "method_schema_url",
        "commerce_confirmation",
    ):
        if f"`{semantic_field}`" not in cid_text:
            errors.append(
                f"{cid_path.relative_to(ROOT)}: missing CID semantic field "
                f"{semantic_field}"
            )
    for highlighted_security_fact in (
        "历史修订证据",
        "商户已声明的能力地址",
        "伪造、篡改或替换",
        "不得继续能力匹配或支付",
    ):
        if highlighted_security_fact not in cid_text:
            errors.append(
                f"{cid_path.relative_to(ROOT)}: missing highlighted CID security "
                f"fact {highlighted_security_fact}"
            )

    revision_path = ROOT / "specs/2.1/revision-status.md"
    revision_text = tracked_texts.get(revision_path, "")
    for source_fact in (
        "545380139",
        "2026-05-20T02:50:37.000Z",
        "2026-05-19T07:27:46.000Z",
        "7a7259c4d2b6ea5bdd1ab3e88ad1be72b327558a0493293ed73db6e75d210113",
        "6,701",
    ):
        if source_fact not in revision_text:
            errors.append(
                f"{revision_path.relative_to(ROOT)}: missing CID source fact "
                f"{source_fact}"
            )
    for pending_id in ("PD-2.1-013", "PD-2.1-014", "PD-2.1-015"):
        if pending_id not in revision_text:
            errors.append(
                f"{revision_path.relative_to(ROOT)}: missing CID pending decision "
                f"{pending_id}"
            )

    profile_path = ROOT / "integrations/profiles/alipay-ai-pay/mappings/domains.md"
    profile_text = tracked_texts.get(profile_path, "")
    profile_components = set(re.findall(r"CID-[A-Z]+-[A-Z]+", profile_text))
    missing_profile_components = sorted(expected_components - profile_components)
    if missing_profile_components:
        errors.append(
            f"{profile_path.relative_to(ROOT)}: missing CID mappings "
            f"{missing_profile_components}"
        )

    return errors


def additional_domain_source_errors() -> list[str]:
    """Protect ADD, TSD, and cross-domain scenario source alignment."""

    errors: list[str] = []
    sources = {
        "add": "https://www.act-protocol.com/documentation/delegation",
        "scenarios": "https://www.act-protocol.com/documentation/scenarios",
        "trust": "https://www.act-protocol.com/documentation/trust",
    }
    paths = {
        "overview": ROOT / "specs/2.1/overview.md",
        "add": ROOT / "specs/2.1/domains/authorization-delegation.md",
        "tsd": ROOT / "specs/2.1/domains/trust-services.md",
        "scenarios": ROOT / "specs/2.1/scenarios.md",
        "revision": ROOT / "specs/2.1/revision-status.md",
        "profile": ROOT / "integrations/profiles/alipay-ai-pay/mappings/domains.md",
    }
    texts: dict[str, str] = {}
    for name, path in paths.items():
        text = decode_text(path, errors)
        if text is not None:
            texts[name] = text

    for name in ("add", "tsd", "scenarios"):
        text = texts.get(name, "")
        for marker in ("Candidate Working Draft", "Non-normative"):
            if marker not in text:
                errors.append(f"{paths[name].relative_to(ROOT)}: missing status {marker}")

    for name in ("overview", "revision"):
        for source_url in sources.values():
            if source_url not in texts.get(name, ""):
                errors.append(
                    f"{paths[name].relative_to(ROOT)}: missing domain source {source_url}"
                )

    add_text = texts.get("add", "")
    for component in ("ADD-INT-ICS", "ADD-IAC-ISS", "ADD-IAC-LCM"):
        if component not in add_text:
            errors.append(f"{paths['add'].relative_to(ROOT)}: missing {component}")
    for fact in (
        "price_deviation_tolerance",
        "price_deviation_action",
        "source_isr_digest",
        "status_reference",
        "Active",
        "Suspended",
        "Revoked",
        "Expired",
        "历史修订证据",
    ):
        if fact not in add_text:
            errors.append(f"{paths['add'].relative_to(ROOT)}: missing ADD fact {fact}")

    tsd_text = texts.get("tsd", "")
    tsd_components = {
        "TSD-ATT-EVT",
        "TSD-ATT-OFF",
        "TSD-ATT-OCA",
        "TSD-ATT-SVF",
        "TSD-ATT-DSP",
        "TSD-CRD-ASC",
        "TSD-CRD-MAP",
        "TSD-CRD-LCM",
        "TSD-CRD-VER",
        "TSD-CRD-AUTH",
    }
    for component in sorted(tsd_components):
        if component not in tsd_text:
            errors.append(f"{paths['tsd'].relative_to(ROOT)}: missing {component}")
    for fact in (
        "链下完整记录 + 链上摘要锚定",
        "ASSOCIATED_CREDIT",
        "DIRECT_SIGNATURE",
        "ATTESTED_CONFIRMATION",
        "逐次授权",
        "平台代理查询",
        "不生成虚构",
    ):
        if fact not in tsd_text:
            errors.append(f"{paths['tsd'].relative_to(ROOT)}: missing TSD fact {fact}")

    scenario_text = texts.get("scenarios", "")
    for fact in (
        "用户在场的即时支付",
        "平台或多租户 Agent 的定向委托",
        "用户专属 Agent 的定向委托",
        "自主化委托支付",
        "PSD-PAY-A402",
        "以对应域正文为准",
        "异步、非阻塞",
    ):
        if fact not in scenario_text:
            errors.append(
                f"{paths['scenarios'].relative_to(ROOT)}: missing scenario fact {fact}"
            )

    revision_text = texts.get("revision", "")
    for source_fact in (
        "545380123",
        "bad030eca08f1b4b723a97fd3f53f2348922b00622f1d2a5d53c299797a6b0af",
        "545380100",
        "41ef13fd14d2d7d87fca1237ab40912b80c387c4ff623e9e1ae6db0027159494",
        "545380294",
        "d312af952b242e1d31af6a95e3dabc64ff4028686955e142a29f33c731f15282",
        "565985641",
        "1e024d74f813ff4ae41ce54e446f9f8ed5242927e0b8abb7fa722a641fcda3dd",
        "PD-2.1-016",
        "PD-2.1-017",
        "PD-2.1-018",
    ):
        if source_fact not in revision_text:
            errors.append(
                f"{paths['revision'].relative_to(ROOT)}: missing source/pending fact "
                f"{source_fact}"
            )

    profile_text = texts.get("profile", "")
    for source_url in (sources["add"], sources["trust"]):
        if source_url not in profile_text:
            errors.append(
                f"{paths['profile'].relative_to(ROOT)}: missing domain source {source_url}"
            )
    for component in ("ADD-INT-ICS", "ADD-IAC-ISS", "ADD-IAC-LCM"):
        if component not in profile_text:
            errors.append(
                f"{paths['profile'].relative_to(ROOT)}: missing ADD mapping {component}"
            )
    for family in ("TSD-ATT-*", "TSD-CRD-*"):
        if family not in profile_text:
            errors.append(
                f"{paths['profile'].relative_to(ROOT)}: missing TSD mapping {family}"
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

    showcase = components.get("alipay-ai-pay-showcase", {})
    if showcase.get("kind") != "demo":
        errors.append("release-manifest.json: Showcase must be declared as a demo")
    if showcase.get("status") != "guided-preview-and-evidence-replay":
        errors.append(
            "release-manifest.json: Showcase status must preserve its preview boundary"
        )
    if showcase.get("normative") is not False:
        errors.append("release-manifest.json: Showcase must remain non-normative")

    product = manifest.get("external_dependencies", {}).get(
        "alipay-ai-pay-product", {}
    )
    if product.get("last_checked") != "2026-08-08":
        errors.append(
            "release-manifest.json: Alipay product source must record 2026-08-08 review"
        )
    if product.get("integration_guide_updated_at") != "2026-08-07T21:51:27+08:00":
        errors.append(
            "release-manifest.json: Alipay guide timestamp must match the latest audit"
        )

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


def publication_configuration_errors() -> list[str]:
    """Keep public endpoints explicit without accepting placeholders as real config."""

    errors: list[str] = []
    config_path = ROOT / "governance/publication-config.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{config_path.relative_to(ROOT)}: cannot validate ({exc})"]

    if config.get("config_version") != "1":
        errors.append(f"{config_path.relative_to(ROOT)}: config_version must be '1'")
    required = {
        "public_repository_url",
        "security_reporting_url",
        "security_contact",
    }
    missing = sorted(required - set(config))
    if missing:
        errors.append(
            f"{config_path.relative_to(ROOT)}: missing publication keys {missing}"
        )

    for field in (
        "public_repository_url",
        "security_reporting_url",
    ):
        value = config.get(field)
        if value is not None and (
            not isinstance(value, str)
            or not value.startswith("https://")
            or "<" in value
            or "example." in value
        ):
            errors.append(
                f"{config_path.relative_to(ROOT)}: {field} must be null or a real HTTPS URL"
            )
    contact = config.get("security_contact")
    if contact is not None and (not isinstance(contact, str) or not contact.strip()):
        errors.append(
            f"{config_path.relative_to(ROOT)}: security_contact must be null or non-empty"
        )
    if config.get("security_reporting_url") != "https://security.alipay.com/":
        errors.append(
            f"{config_path.relative_to(ROOT)}: security reporting must use AntSRC"
        )
    return errors


def public_snapshot_boundary_errors() -> list[str]:
    """Ensure public documents and gates do not depend on excluded private files."""

    errors: list[str] = []
    private_root = ROOT / "governance/internal"
    for pattern in ("*.md", "*.json"):
        for path in repository_files(pattern):
            if private_root in path.parents:
                continue
            text = decode_text(path, errors)
            if text is None:
                continue
            if "governance/internal/" in text or "](internal/" in text or "](../internal/" in text:
                errors.append(
                    f"{path.relative_to(ROOT)}: public content depends on private governance material"
                )
    return errors


def release_readiness_errors() -> list[str]:
    errors: list[str] = []
    readiness_path = ROOT / "governance/release-readiness.json"
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
    catalog_path = ROOT / "specs/2.1/a402/assertions/a402-core-assertions.json"
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

    feature_path = ROOT / "specs/2.1/a402/assertions/features/a402-local-preview.feature"
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
        schema_path = ROOT / "integrations/profiles/alipay-ai-pay/schemas" / schema_name
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

    schema_path = ROOT / "integrations/profiles/alipay-ai-pay/schemas/payment-needed.preview.schema.json"
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
                "integrations/profiles/alipay-ai-pay/schemas/payment-proof.preview.schema.json: "
                f"protocol must require {field}"
            )

    verification_schema = schemas.get(
        "payment-verification-result.preview.schema.json", {}
    )
    verification_required = verification_schema.get("required", [])
    for field in ("trade_no", "out_trade_no", "amount", "resource_id", "active"):
        if field not in verification_required:
            errors.append(
                "integrations/profiles/alipay-ai-pay/schemas/"
                "payment-verification-result.preview.schema.json: "
                f"must require {field}"
            )

    inspector_path = (
        ROOT / "code/examples/alipay/end-to-end-402/inspect-402.mjs"
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

    review_path = ROOT / "integrations/profiles/alipay-ai-pay/profile-review-status.json"
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
        ROOT / "integrations/profiles/alipay-ai-pay/schemas/error-mapping.preview.json"
    )
    core_error_catalog_path = ROOT / "specs/2.1/a402/schemas/error-catalog.json"
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

    public_roots = [ROOT / "docs/getting-started", ROOT / "code/examples"]
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
    register_path = ROOT / "governance/decisions/a402-decision-register.json"
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
    brief_path = ROOT / "governance/decisions/protocol-decision-brief.md"
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
        "guide": ROOT / "governance/decisions/a402-review-guide.md",
        "minutes": ROOT / "governance/decisions/a402-review-minutes-template.md",
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
        ("Official ACT source registry", protocol_source_registry_errors),
        ("Completed PSD source alignment", payment_services_domain_errors),
        ("Current CID source alignment", commerce_interaction_domain_errors),
        ("ADD, TSD, and scenario source alignment", additional_domain_source_errors),
        ("Release manifest", release_manifest_errors),
        ("Publication configuration", publication_configuration_errors),
        ("Public snapshot boundary", public_snapshot_boundary_errors),
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
