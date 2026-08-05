#!/usr/bin/env python3
"""Report release gates without turning unresolved decisions into success claims."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "docs/project/releases/release-readiness.json"
PASSING = {"passed"}


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def evaluate(target: str) -> dict:
    data = json.loads(READINESS.read_text(encoding="utf-8"))
    target_metadata = data["targets"][target]
    gates = []
    for gate in data["gates"]:
        if target not in gate["required_for"]:
            continue
        item = {
            "id": gate["id"],
            "title": gate["title"],
            "status": gate["status"],
            "blocker": gate.get("blocker"),
        }
        missing_evidence = [
            path for path in gate["evidence"] if not (ROOT / path).is_file()
        ]
        if missing_evidence:
            item["status"] = "failed"
            item["blocker"] = f"Missing evidence: {', '.join(missing_evidence)}"
        gates.append(item)

    worktree_entries = [
        line for line in git_output("status", "--porcelain=v1").splitlines() if line
    ]
    snapshot = next((gate for gate in gates if gate["id"] == "release-snapshot"), None)
    if snapshot is not None:
        snapshot["dynamic"] = {
            "worktree_clean": not worktree_entries,
            "changed_entries": len(worktree_entries),
        }
        if worktree_entries:
            snapshot["status"] = "pending-local"
            snapshot["blocker"] = (
                f"Worktree contains {len(worktree_entries)} changed entries."
            )

    remotes = git_output("remote", "-v").splitlines()
    public_remote = any(
        "github.com" in line or "gitlab.com" in line for line in remotes
    )
    distribution = next(
        (gate for gate in gates if gate["id"] == "public-distribution"), None
    )
    if distribution is not None:
        distribution["dynamic"] = {"public_remote_detected": public_remote}
        if not public_remote:
            distribution["status"] = "blocked-external"

    blockers = [gate for gate in gates if gate["status"] not in PASSING]
    return {
        "target": target,
        "candidate": data["candidate"],
        "allowed_claim": target_metadata["allowed_claim"],
        "ready": not blockers,
        "gates": gates,
        "blockers": blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target",
        choices=(
            "act-candidate-publication",
            "alipay-profile-preview",
            "alipay-sandbox-verified",
            "act-sep-candidate",
        ),
        default="act-candidate-publication",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = evaluate(args.target)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Release target: {result['target']}")
        print(f"Candidate: {result['candidate']}")
        print(f"Allowed claim: {result['allowed_claim']}")
        for gate in result["gates"]:
            print(f"{gate['status'].upper()}: {gate['id']} — {gate['title']}")
            if gate.get("blocker") and gate["status"] not in PASSING:
                print(f"  {gate['blocker']}")
        print("READY" if result["ready"] else "NOT READY")
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
