from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_convert_prose():
    spec = importlib.util.spec_from_file_location("convert_prose", ROOT / "tools" / "convert_prose.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["convert_prose"] = module
    spec.loader.exec_module(module)
    return module


def test_styled_lines_emit_single_brace_color_tags() -> None:
    converter = load_convert_prose().ProseConverter()

    # "{{" is an escaped literal brace in Ren'Py, so a doubled tag would be
    # shown as text instead of coloring the line.
    assert converter.format_bee_protocol("ping *ok*", indent="") == (
        'narrator "{color=#f1c40f}ping {i}ok{/i}{/color}"'
    )
    assert converter.format_ai_citizen_log("<WAFFLE.BAT//> ready", indent="") == (
        'narrator "{color=#43d4a8}<WAFFLE.BAT//> ready{/color}"'
    )
    assert converter.format_blockquote(["> **FORM**", "> *Note:* filed"], indent="") == (
        'narrator "{color=#808090}{b}FORM{/b}\\n{i}Note:{/i} filed{/color}"'
    )


def test_released_prose_has_no_escaped_text_tags() -> None:
    convert_prose = load_convert_prose()
    converter = convert_prose.ProseConverter()

    offenders = []
    for path in sorted((ROOT / "prose" / "act1").glob("*.md")):
        if path.name.endswith("_combined.md"):
            continue
        for line in converter.convert_file(str(path)).splitlines():
            if any(bad in line for bad in ("{{color=", "{{/color}}", "{{i}", "{i}}", "{/i}}")):
                offenders.append(f"{path.name}: {line.strip()[:80]}")

    assert offenders == []
