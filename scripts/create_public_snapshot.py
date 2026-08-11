#!/usr/bin/env python3
"""Create and validate a publication-safe ACT repository snapshot."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PREFIXES = ("governance/internal/",)
SENSITIVE_NAMES = {".env", "id_rsa", "id_ed25519"}
SENSITIVE_SUFFIXES = {".key", ".p12", ".pfx"}


def repository_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths: list[Path] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        relative = Path(raw.decode("utf-8"))
        portable = relative.as_posix()
        if portable.startswith(PRIVATE_PREFIXES):
            continue
        source = ROOT / relative
        if source.is_file() or source.is_symlink():
            paths.append(relative)
    return sorted(set(paths))


def validate_path(relative: Path) -> None:
    if relative.name in SENSITIVE_NAMES and relative.name != ".env.example":
        raise RuntimeError(f"refusing to publish sensitive file name: {relative}")
    if relative.suffix.lower() in SENSITIVE_SUFFIXES:
        raise RuntimeError(f"refusing to publish credential-like file: {relative}")


def build_snapshot(destination: Path) -> int:
    destination = destination.resolve()
    if destination == ROOT or destination.is_relative_to(ROOT):
        raise RuntimeError("snapshot destination must be outside the source repository")
    if destination.exists():
        raise RuntimeError(f"snapshot destination already exists: {destination}")

    paths = repository_paths()
    destination.mkdir(parents=True)
    for relative in paths:
        validate_path(relative)
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target, follow_symlinks=False)

    if (destination / "governance/internal").exists():
        raise RuntimeError("private governance material leaked into public snapshot")
    return len(paths)


def verify_snapshot(destination: Path) -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_repository.py"],
        cwd=destination,
        check=False,
        text=True,
    )
    if result.returncode:
        raise RuntimeError("public snapshot repository checks failed")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an explicit public snapshot without private or ignored files."
    )
    parser.add_argument("destination", nargs="?", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="build a temporary snapshot and run repository checks inside it",
    )
    args = parser.parse_args()

    if args.check and args.destination is not None:
        parser.error("destination cannot be used with --check")
    if not args.check and args.destination is None:
        parser.error("provide an output directory or use --check")

    try:
        if args.check:
            with tempfile.TemporaryDirectory(prefix="act-public-snapshot-") as temp:
                destination = Path(temp) / "act-protocol"
                count = build_snapshot(destination)
                verify_snapshot(destination)
                print(f"Public snapshot check passed ({count} files).")
        else:
            destination = args.destination.resolve()
            count = build_snapshot(destination)
            verify_snapshot(destination)
            print(f"Created validated public snapshot at {destination} ({count} files).")
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Public snapshot failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
