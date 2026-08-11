#!/usr/bin/env python3
"""Detect visible-text drift on the official ACT protocol publication pages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "governance/protocol-sources.json"
IGNORED_TAGS = {"script", "style", "noscript", "svg", "template"}


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in IGNORED_TAGS:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in IGNORED_TAGS and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)


def normalized_visible_text(body: str) -> str:
    parser = VisibleTextParser()
    parser.feed(body)
    text = unicodedata.normalize("NFC", " ".join(parser.parts))
    return re.sub(r"\s+", " ", text).strip()


def fetch_page(url: str, timeout: float) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": "ACT-Protocol-Source-Drift/1.0"})
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
    visible_text = normalized_visible_text(body)
    digest = hashlib.sha256(visible_text.encode("utf-8")).hexdigest()
    return visible_text, digest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--print-current",
        action="store_true",
        help="Print the currently observed page digests without comparing them.",
    )
    args = parser.parse_args()

    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        pages = registry["pages"]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"Protocol source drift check failed: {exc}", file=sys.stderr)
        return 1

    observed: list[dict[str, str]] = []
    errors: list[str] = []
    for page in pages:
        try:
            visible_text, digest = fetch_page(page["url"], args.timeout)
        except (OSError, KeyError, ValueError) as exc:
            errors.append(f"{page.get('id', 'unknown')}: fetch failed: {exc}")
            continue
        if page["title_marker"] not in visible_text:
            errors.append(
                f"{page['id']}: title marker {page['title_marker']!r} is missing"
            )
        observed.append(
            {"id": page["id"], "visible_text_sha256": digest, "url": page["url"]}
        )
        if not args.print_current and digest != page["visible_text_sha256"]:
            errors.append(
                f"{page['id']}: official page changed; recorded "
                f"{page['visible_text_sha256']}, observed {digest}"
            )

    if args.print_current:
        print(json.dumps(observed, ensure_ascii=False, indent=2))
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1 if errors else 0
    if errors:
        print("Protocol source drift detected:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print(
            "Run a human structure and semantic diff before updating the Candidate or registry.",
            file=sys.stderr,
        )
        return 1
    print(f"Official ACT protocol pages match {len(observed)} recorded snapshots.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
