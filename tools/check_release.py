#!/usr/bin/env python3
"""Run deterministic release gates for the narrative-tools repo."""

from __future__ import annotations

import subprocess
import sys
import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str]) -> int:
    print(f"\n== {label} ==")
    print("+ " + " ".join(command))
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="Accepted for cluster consistency; this repo has no generated engine artifacts to clean.")
    parser.add_argument("--fail-on-generated", action="store_true", help="Accepted for cluster consistency; this repo has no generated engine artifacts to allow.")
    parser.parse_args()

    checks = [
        ("Python tests", [sys.executable, "-m", "pytest"]),
        ("Public-scope validation", [sys.executable, "tools/validate_public_scope.py"]),
        ("Tool compilation", [sys.executable, "-m", "compileall", "tools"]),
    ]

    failures = 0
    for label, command in checks:
        failures += 1 if run(label, command) else 0

    if failures:
        print(f"\nrelease gate failed: {failures} check(s) failed")
        return 1

    print("\nrelease gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
