from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "tools" / "demo.py"


def run_demo(env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DEMO)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def test_demo_exits_zero() -> None:
    result = run_demo()

    assert result.returncode == 0, result.stderr


def test_demo_stdout_contains_header() -> None:
    result = run_demo()

    assert result.returncode == 0, result.stderr
    assert "capability demo" in result.stdout


def test_demo_survives_narrow_encoding() -> None:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "ascii"
    env["PYTHONUTF8"] = "0"

    result = run_demo(env=env)

    assert result.returncode == 0, result.stderr
    assert "UnicodeEncodeError" not in result.stderr
    assert "capability demo" in result.stdout
