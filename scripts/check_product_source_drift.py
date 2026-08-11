#!/usr/bin/env python3
"""Fail when the official Alipay integration guide timestamp drifts."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html"
TIMESTAMP = re.compile(r"更新时间\s*[：:]\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})")
STRUCTURED_TIMESTAMP = re.compile(
    r'(?:updateTime|updatedAt)["\'\\:\s]+(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})'
)


def expected_timestamp() -> datetime:
    manifest = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
    raw = manifest["external_dependencies"]["alipay-ai-pay-product"][
        "integration_guide_updated_at"
    ]
    return datetime.fromisoformat(raw)


def fetch_timestamp(url: str, timeout: float) -> datetime:
    request = Request(url, headers={"User-Agent": "ACT-Protocol-Source-Drift/1.0"})
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
    visible = html.unescape(re.sub(r"<[^>]+>", " ", body))
    match = TIMESTAMP.search(visible) or STRUCTURED_TIMESTAMP.search(body)
    if match is None:
        raise RuntimeError("could not find the guide update timestamp")
    return datetime.fromisoformat(match.group(1).replace(" ", "T"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()
    try:
        expected = expected_timestamp()
        observed = fetch_timestamp(args.url, args.timeout)
    except (OSError, KeyError, ValueError, RuntimeError) as exc:
        print(f"Product source drift check failed: {exc}", file=sys.stderr)
        return 1

    expected_naive = expected.replace(tzinfo=None)
    if observed != expected_naive:
        relation = "newer" if observed > expected_naive else "different"
        print(
            "Product source drift detected: official guide is "
            f"{relation} ({observed.isoformat()}) than recorded "
            f"({expected_naive.isoformat()}). Run a human source audit.",
            file=sys.stderr,
        )
        return 1
    print(f"Product source timestamp matches: {observed.isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
