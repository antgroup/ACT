#!/usr/bin/env python3
"""Check stable public entry points without making transient network failures fatal."""

from __future__ import annotations

import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

URLS = {
    "ACT website demo": "https://www.act-protocol.com/demo",
    "AIPay website": "https://aipay.alipay.com/callpay",
    "AIPay Machine Pay guide": "https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html",
    "Alipay payment skills": "https://github.com/alipay/payment-skills",
}
USER_AGENT = "ACT-Repository-Link-Check/1.0"


def check(label: str, url: str) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=10) as response:
            response.read(1)
            return "PASS", f"{label}: HTTP {response.status}"
    except HTTPError as exc:
        if exc.code in {404, 410}:
            return "FAIL", f"{label}: HTTP {exc.code} -> {url}"
        return "SKIP", f"{label}: reachable but returned HTTP {exc.code}"
    except (URLError, TimeoutError, OSError) as exc:
        return "SKIP", f"{label}: network unavailable ({exc.__class__.__name__})"


def main() -> int:
    failures = 0
    for label, url in URLS.items():
        status, message = check(label, url)
        print(f"[{status}] {message}")
        if status == "FAIL":
            failures += 1
    if failures:
        print(f"\nExternal link checks failed with {failures} broken link(s).")
        return 1
    print("\nExternal link checks completed; transient or access-controlled responses are non-fatal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
