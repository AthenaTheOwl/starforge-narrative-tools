#!/usr/bin/env python3
"""demo.py — zero-argument capability tour of the Starforge narrative toolkit.

Run with no arguments to see the conversion pipeline work end to end against the
released Act 1 prose slice. This is a read-only demonstration: it converts prose
in memory and prints a summary, it does not write any files.

    python tools/demo.py

The toolkit itself has no runtime dependencies (Python stdlib only).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
PROSE_ACT1 = ROOT / "prose" / "act1"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=" * 70)
    print("Starforge Narrative Tools — capability demo")
    print("=" * 70)
    print(
        "\nThis repo is the Python pipeline behind a published serial's game\n"
        "adaptation. It converts authored prose into engine-ready script and\n"
        "validates the result. Below: the prose->Ren'Py converter, run live.\n"
    )

    if not PROSE_ACT1.is_dir():
        print(f"ERROR: expected released prose at {PROSE_ACT1}")
        return 1

    convert_prose = _load("convert_prose")
    prose_files = sorted(PROSE_ACT1.glob("*.md"))
    print(f"Released Act 1 prose files found: {len(prose_files)}")
    print(f"Speakers mapped in converter:     {len(convert_prose.SPEAKER_MAP)}")
    print()

    converter = convert_prose.ProseConverter()
    total_in = 0
    total_out = 0
    for path in prose_files:
        raw = path.read_text(encoding="utf-8")
        rpy = converter.convert_file(str(path))
        total_in += len(raw.splitlines())
        total_out += len(rpy.splitlines())
        print(
            f"  {path.name:<48} "
            f"{len(raw.splitlines()):>4} md lines -> "
            f"{len(rpy.splitlines()):>4} rpy lines"
        )

    print()
    print("-" * 70)
    print(f"  TOTAL: {total_in} prose lines -> {total_out} generated Ren'Py lines")
    print("-" * 70)

    # Show a small slice of generated output for the first chapter.
    sample = converter_sample = convert_prose.ProseConverter().convert_file(
        str(prose_files[0])
    )
    print(f"\nSample generated Ren'Py (first 18 lines of {prose_files[0].name}):\n")
    for line in sample.splitlines()[:18]:
        print("  | " + line)

    print(
        "\nNext steps:\n"
        "  - Interactive UI:   streamlit run streamlit_app.py\n"
        "  - Validate output:  python tools/validate_renpy.py <game_dir>\n"
        "  - Release gate:     python tools/check_release.py\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
