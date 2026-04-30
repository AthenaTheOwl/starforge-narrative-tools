import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_act1_prose_corpus_present() -> None:
    prose_root = ROOT / "prose"
    act_dirs = sorted(path for path in prose_root.glob("act*") if path.is_dir())
    markdown_files = sorted(prose_root.rglob("*.md"))

    assert [path.name for path in act_dirs] == ["act1"]
    assert len(markdown_files) >= 60
    assert (prose_root / "act1" / "act1_combined.md").exists()
    assert all(path.stat().st_size > 0 for path in markdown_files)


def test_public_specs_present() -> None:
    spec_root = ROOT / "spec"
    spec_files = sorted(spec_root.rglob("*.md"))

    assert len(spec_files) >= 2
    assert all(path.stat().st_size > 0 for path in spec_files)


def test_unreleased_act_paths_are_not_present() -> None:
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if "site-packages" not in path.parts
        and any(re.search(r"act([2-9]|[1-9][0-9])", part, re.IGNORECASE) for part in path.parts)
    ]

    assert offenders == []


def test_unreleased_act_tokens_are_not_present_in_source() -> None:
    offenders: list[str] = []
    for path in ROOT.rglob("*"):
        if "tests" in path.parts:
            continue
        if not path.is_file() or path.suffix not in {".py", ".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        if any(token in text for token in ("act2_", "act3_", "acts 1-3", "full corpus")):
            offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == []


def test_public_scope_validator_passes() -> None:
    result = subprocess.run(
        [sys.executable, "tools/validate_public_scope.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_no_generated_runtime_artifacts() -> None:
    forbidden_suffixes = {".pyc", ".pyo", ".rpyc", ".rpyb", ".save"}
    forbidden_names = {".godot", ".beads", "renpy-8.5.2-sdk"}

    offenders: list[str] = []
    for path in ROOT.rglob("*"):
        if "__pycache__" in path.parts or ".pytest_cache" in path.parts:
            continue
        if any(part in forbidden_names for part in path.parts):
            offenders.append(str(path.relative_to(ROOT)))
        if path.is_file() and path.suffix in forbidden_suffixes:
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []
