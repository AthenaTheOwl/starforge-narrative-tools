#!/usr/bin/env python3
"""Validate that the public Starforge tools exhibit stays Act 1-only."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UNRELEASED_PATTERN = re.compile(r"act([2-9]|[1-9][0-9])", re.IGNORECASE)
FORBIDDEN_NAMES = {".godot", ".beads", "renpy-8.5.2-sdk"}
IGNORED_GENERATED_DIRS = {"__pycache__", ".pytest_cache"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".rpyc", ".rpyb", ".save"}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    errors: list[str] = []

    prose_dirs = sorted(path.name for path in (ROOT / "prose").glob("act*") if path.is_dir())
    if prose_dirs != ["act1"]:
        errors.append(f"expected only prose/act1, found: {prose_dirs}")

    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if any(part in IGNORED_GENERATED_DIRS for part in path.parts):
            continue
        if any(part in FORBIDDEN_NAMES for part in path.parts):
            errors.append(f"forbidden generated artifact: {rel(path)}")
        if path.is_file() and path.suffix in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden generated file: {rel(path)}")
        if any(UNRELEASED_PATTERN.search(part) for part in path.parts):
            if "README.md" in path.parts or "docs" in path.parts or "spec" in path.parts:
                continue
            errors.append(f"unreleased act reference in public source path: {rel(path)}")

    if errors:
        print("public-scope validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("public-scope validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
