#!/usr/bin/env python3
"""Dependency-free integrity checks for the public ACT repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
IGNORED = {".git", ".tmp", ".venv", ".codefuse", "node_modules", "__pycache__", "output", "target"}
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING = re.compile(r"^(#{1,6})\s+", re.M)
CODE_SPAN = re.compile(r"`([^`\n]+)`")


def files(pattern: str) -> list[Path]:
    return sorted(p for p in ROOT.rglob(pattern) if not any(part in IGNORED for part in p.parts))


def markdown_errors() -> list[str]:
    errors = []
    for path in files("*.md"):
        text = path.read_text(encoding="utf-8")
        for raw in LINK.findall(text):
            target = raw.strip().strip("<>")
            target = re.split(r"\s+[\"']", target, maxsplit=1)[0]
            parsed = urlparse(target)
            if parsed.scheme or target.startswith("#") or not parsed.path:
                continue
            local = unquote(parsed.path)
            resolved = (ROOT / local.lstrip("/") if local.startswith("/") else path.parent / local).resolve()
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken local link -> {local}")
    return errors


def syntax_errors() -> list[str]:
    errors = []
    for path in files("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON/UTF-8 ({exc})")
    for path in files("*.py"):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (UnicodeDecodeError, SyntaxError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid Python/UTF-8 ({exc})")
    return errors


def structure_errors() -> list[str]:
    required = [
        "README.md", "README.en.md", "LICENSE", "SECURITY.md", "release-manifest.json",
        "docs/specification/README.md",
        "docs/specification/overview.md", "docs/specification/overview.en.md",
        "docs/specification/authorization-delegation.md", "docs/specification/authorization-delegation.en.md",
        "docs/specification/commerce-interaction.md", "docs/specification/commerce-interaction.en.md",
        "docs/specification/payment-services.md", "docs/specification/payment-services.en.md",
        "docs/specification/trust-services.md", "docs/specification/trust-services.en.md",
        "docs/specification/a402.md", "docs/specification/a402.en.md",
        "docs/specification/commerce-payment-negotiation.md",
        "docs/specification/commerce-payment-negotiation.en.md",
        "integrations/tsd-crd/README.md",
        "code/schemas/a402/README.md", "code/schemas/a402/payment-needed.schema.json",
        "code/schemas/tsd-crd/reference-v1/README.md",
        "code/schemas/tsd-crd/reference-v1/schemas/association-credential.schema.json",
        "code/samples/local-a402/package.json", "code/web-client/alipay-ai-pay-showcase/package.json",
        "code/samples/tsd-crd-reference/package.json",
        "integrations/alipay/buyer-agent/package.json", "integrations/alipay/seller-java/pom.xml",
        "integrations/alipay/validation/README.md",
        "tools/verify.sh",
        "tools/quality/check_repository.py",
        "tools/quality/create_public_snapshot.py",
        "tools/a402/validate_contract.py",
        "tools/tsd-crd/validate_contract.py",
    ]
    errors = [f"missing required asset: {p}" for p in required if not (ROOT / p).is_file()]
    forbidden = [
        "specs", "code/examples", "integrations/profiles", "integrations/bindings",
        "docs/architecture", "docs/getting-started", "docs/project",
        "code/samples/tsd-crd-reference/docs",
        "docs/reference-implementations/tsd-crd",
    ]
    errors += [
        f"obsolete release path contains publishable files: {p}"
        for p in forbidden
        if (ROOT / p).exists()
        and any(
            child.is_file() and not any(part in IGNORED for part in child.parts)
            for child in (ROOT / p).rglob("*")
        )
    ]
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "specs/" in license_text:
        errors.append("LICENSE: refers to the removed specs/ release layout")
    conduct_text = (ROOT / "CODE_OF_CONDUCT.md").read_text(encoding="utf-8")
    if "尚未确认私密行为准则报告渠道" in conduct_text:
        errors.append("CODE_OF_CONDUCT.md: private reporting channel is unresolved")
    seller_pom = (ROOT / "integrations/alipay/seller-java/pom.xml").read_text(encoding="utf-8")
    if "-SNAPSHOT" in seller_pom:
        errors.append("integrations/alipay/seller-java/pom.xml: release version must not be a SNAPSHOT")
    return errors


def manifest_errors() -> list[str]:
    path = ROOT / "release-manifest.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"release-manifest.json: {exc}"]
    errors = []
    if manifest.get("release") != "ACT 2.1":
        errors.append("release-manifest.json: release must be ACT 2.1")
    if manifest.get("release_date") != "2026-08-14":
        errors.append("release-manifest.json: release date must match the ACT 2.1 release note")
    if manifest.get("specification_finalized") != "2026-08-11":
        errors.append("release-manifest.json: specification finalization date is missing")
    languages = manifest.get("languages", {})
    if languages.get("normative") != "zh-CN":
        errors.append("release-manifest.json: normative language must be zh-CN")
    if "en" not in languages.get("official_informative_translations", []):
        errors.append("release-manifest.json: English informative translation is missing")
    release_authority = manifest.get("authorities", {}).get("act_2_1_versioned_release")
    if not isinstance(release_authority, str) or not (ROOT / release_authority).is_file():
        errors.append("release-manifest.json: invalid ACT 2.1 versioned release authority")
    for name, component in manifest.get("components", {}).items():
        target = component.get("path")
        if not isinstance(target, str) or not (ROOT / target).is_file():
            errors.append(f"release-manifest.json: invalid component path for {name}")
        translation_of = component.get("translation_of")
        if translation_of is not None and (
            not isinstance(translation_of, str) or not (ROOT / translation_of).is_file()
        ):
            errors.append(f"release-manifest.json: invalid translation source for {name}")
    required_normative = {
        "docs/specification/overview.md",
        "docs/specification/authorization-delegation.md",
        "docs/specification/commerce-interaction.md",
        "docs/specification/payment-services.md",
        "docs/specification/trust-services.md",
    }
    declared_normative = {
        component.get("path")
        for component in manifest.get("components", {}).values()
        if component.get("normative") is True
    }
    if declared_normative != required_normative:
        errors.append("release-manifest.json: normative specification set is incomplete or incorrect")
    return errors


def translation_errors() -> list[str]:
    """Keep official informative translations structurally tied to Chinese sources."""
    errors = []
    pairs = [
        ("docs/specification/overview.md", "docs/specification/overview.en.md"),
        ("docs/specification/authorization-delegation.md", "docs/specification/authorization-delegation.en.md"),
        ("docs/specification/commerce-interaction.md", "docs/specification/commerce-interaction.en.md"),
        ("docs/specification/payment-services.md", "docs/specification/payment-services.en.md"),
        ("docs/specification/trust-services.md", "docs/specification/trust-services.en.md"),
        ("docs/specification/a402.md", "docs/specification/a402.en.md"),
        (
            "docs/specification/commerce-payment-negotiation.md",
            "docs/specification/commerce-payment-negotiation.en.md",
        ),
    ]
    translation_marker = "Translation status: Official English translation / Informative"
    for source_name, translation_name in pairs:
        source = (ROOT / source_name).read_text(encoding="utf-8")
        translation = (ROOT / translation_name).read_text(encoding="utf-8")
        if translation_marker not in translation:
            errors.append(f"{translation_name}: missing official informative translation marker")
        if "Chinese ACT 2.1 publication remains controlling" not in translation:
            errors.append(f"{translation_name}: missing Chinese controlling-language notice")
        source_headings = HEADING.findall(source)
        translation_headings = HEADING.findall(translation)
        if source_headings != translation_headings:
            errors.append(f"{translation_name}: heading structure differs from {source_name}")
        source_tokens = set(CODE_SPAN.findall(source))
        translation_tokens = set(CODE_SPAN.findall(translation))
        if source_tokens != translation_tokens:
            errors.append(f"{translation_name}: wire/code tokens differ from {source_name}")
    return errors


def release_wording_errors() -> list[str]:
    errors = []
    patterns = {
        "Candidate Working Draft": re.compile(r"Candidate Working Draft", re.I),
        "GUIDED_PREVIEW": re.compile(r"GUIDED_PREVIEW"),
        "Profile Preview": re.compile(r"Profile Preview", re.I),
        "legacy specs path": re.compile(r"specs/2\.1/"),
        "process status marker": re.compile(
            r"^(?:>\s*)?(?:\*\*)?(?:状态|status)(?:\*\*)?\s*[:：][^\n]*"
            r"(?:candidate|draft|preview|provisional|blocked|pending)",
            re.I | re.M,
        ),
        "pending-decision field": re.compile(r'"pending_decision"\s*:'),
        "website-sync dependency": re.compile(r"官网同步完成前"),
        "historical revision evidence": re.compile(r"历史修订证据"),
        "highlight revision note": re.compile(r"(?:本轮黄色修订|黄色(?:高亮|段落|安全段落))"),
        "website as protocol authority": re.compile(
            r"(?:持续更新的公共协议入口|continuously updated public protocol entry|"
            r"public protocol entry point[^\n]*(?:authority|controls)|官网同步完成前)", re.I
        ),
    }
    checked = files("*.md")
    checked += files("*.json")
    for path in checked:
        text = path.read_text(encoding="utf-8")
        for label, pattern in patterns.items():
            if pattern.search(text):
                errors.append(f"{path.relative_to(ROOT)}: release wording contains {label}")
    return errors


def main() -> int:
    checks = [
        ("Markdown local links", markdown_errors),
        ("JSON and Python syntax", syntax_errors),
        ("Release structure", structure_errors),
        ("Release manifest", manifest_errors),
        ("Official English translations", translation_errors),
        ("Release wording", release_wording_errors),
    ]
    failures = 0
    for name, check in checks:
        errors = check()
        if errors:
            failures += len(errors)
            print(f"[FAIL] {name}: {len(errors)} issue(s)")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"[PASS] {name}")
    if failures:
        print(f"\nRepository checks failed with {failures} issue(s).")
        return 1
    print("\nRepository checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
