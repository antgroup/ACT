#!/usr/bin/env python3
"""Run dependency-free repository integrity checks.

This checker deliberately validates only facts that can be established without
installing project dependencies: local Markdown links, UTF-8/JSON syntax and
Python syntax. Schema-to-example conformance is tracked separately.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".venv", "node_modules", "__pycache__"}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


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
    implementation = ROOT / "impl" / "python"
    if not implementation.exists():
        return errors

    for path in sorted(implementation.rglob("*.py")):
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
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


def main() -> int:
    checks = [
        ("Markdown local links", markdown_link_errors),
        ("UTF-8 and JSON syntax", json_errors),
        ("Python syntax", python_syntax_errors),
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
