#!/usr/bin/env python3
"""streamlit_app.py — Live demo of the Starforge narrative-tools conversion pipeline.

This app exercises the real toolkit (no mocks): it loads the released Act 1 prose
slice from ``prose/act1/`` and runs ``tools/convert_prose.ProseConverter`` to show
how authored markdown prose becomes engine-ready Ren'Py script.

Run locally:
    pip install streamlit
    streamlit run streamlit_app.py

Deploy: Streamlit Community Cloud, entry point ``streamlit_app.py``.
The toolkit itself has zero runtime dependencies; only this demo UI needs streamlit.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / "tools"
PROSE_ACT1 = ROOT / "prose" / "act1"


def _load_converter_module():
    """Import tools/convert_prose.py directly (tools/ is not a package)."""
    spec = importlib.util.spec_from_file_location(
        "convert_prose", TOOLS / "convert_prose.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["convert_prose"] = module
    spec.loader.exec_module(module)
    return module


def convert_prose_text(convert_prose, scene_filename: str, prose_text: str):
    """Run the REAL ProseConverter on arbitrary user-supplied prose.

    convert_file() reads from a path, so we write the text to a temp file whose
    name carries the act/scene id, then call the actual engine. No logic is
    reimplemented here — this is the same code path the released chapters use.
    Returns (rpy_text, converter) so the caller can read real telemetry
    (resolved speakers, unknown speakers, scene/line counts).
    """
    safe_name = scene_filename.strip() or "user_scene.md"
    if not safe_name.endswith(".md"):
        safe_name += ".md"
    with tempfile.TemporaryDirectory() as tmp:
        # parent dir name becomes the act segment of the scene id
        act_dir = Path(tmp) / "act1"
        act_dir.mkdir()
        path = act_dir / safe_name
        path.write_text(prose_text, encoding="utf-8")
        converter = convert_prose.ProseConverter()
        rpy = converter.convert_file(str(path))
    return rpy, converter


st.set_page_config(
    page_title="Starforge Narrative Tools",
    page_icon="📖",
    layout="wide",
)

st.title("Starforge Narrative Tools — prose-to-game pipeline")
st.caption(
    "Live demo of the real conversion toolkit behind "
    "[Starforge Canticles](https://www.royalroad.com/fiction/149065/starforge-canticles). "
    "Authored markdown prose in → engine-ready Ren'Py script out."
)

try:
    convert_prose = _load_converter_module()
except Exception as exc:  # pragma: no cover - surfaced in the UI
    st.error(f"Could not load the converter toolkit: {exc}")
    st.stop()

prose_files = sorted(PROSE_ACT1.glob("*.md")) if PROSE_ACT1.is_dir() else []

tab_convert, tab_play, tab_about = st.tabs(
    ["Convert prose → Ren'Py", "Write your own → convert live", "What this is"]
)

with tab_convert:
    if not prose_files:
        st.warning(
            f"No prose files found under {PROSE_ACT1}. "
            "This demo expects the released Act 1 slice in prose/act1/."
        )
    else:
        col_pick, col_stats = st.columns([3, 1])
        with col_pick:
            labels = [p.name for p in prose_files]
            choice = st.selectbox(
                "Pick a released Act 1 prose chapter", labels, index=0
            )
            selected = PROSE_ACT1 / choice

        raw = selected.read_text(encoding="utf-8")

        # Run the real converter on the selected file.
        converter = convert_prose.ProseConverter()
        try:
            rpy = converter.convert_file(str(selected))
            convert_error = None
        except Exception as exc:  # pragma: no cover - surfaced in the UI
            rpy = ""
            convert_error = exc

        with col_stats:
            st.metric("Prose lines", len(raw.splitlines()))
            st.metric("Generated .rpy lines", len(rpy.splitlines()))
            st.metric("Speakers mapped", len(convert_prose.SPEAKER_MAP))

        left, right = st.columns(2)
        with left:
            st.subheader("Input · authored prose (markdown)")
            st.code(raw, language="markdown")
        with right:
            st.subheader("Output · generated Ren'Py")
            if convert_error is not None:
                st.error(f"Conversion failed: {convert_error}")
            else:
                st.code(rpy, language="python")
                st.download_button(
                    "Download .rpy",
                    data=rpy,
                    file_name=selected.stem + ".rpy",
                    mime="text/plain",
                )

        st.divider()
        st.subheader("Speaker map (prose name → engine character variable)")
        st.dataframe(
            {
                "Prose name": list(convert_prose.SPEAKER_MAP.keys()),
                "Character var": list(convert_prose.SPEAKER_MAP.values()),
            },
            use_container_width=True,
            hide_index=True,
        )

with tab_play:
    st.subheader("Drive the real converter on your own prose")
    st.caption(
        "This is not a lookup. Whatever you type below is written to a scene "
        "file and run through the actual `ProseConverter.convert_file` engine — "
        "the same code path the released chapters use. Edit the prose and the "
        "generated Ren'Py + converter telemetry recompute live."
    )

    # Pre-fill with a small committed-style example so the user has a starting
    # point, then let them edit freely.
    default_example = (
        "# Chapter 0: First Watch\n"
        "\n"
        "> **[SCENE - Bridge, night cycle]**\n"
        "\n"
        "[The bridge is quiet except for the hum of the drive.]\n"
        "\n"
        "Avyanna: [quiet] You don't have to take the whole watch alone.\n"
        "\n"
        "Vesper: I know. I want to. Just this once.\n"
        "\n"
        "(She isn't ready to say why.)\n"
        "\n"
        "{BEE:: proximity nominal. no contacts.}\n"
        "\n"
        "<WAFFLE.BAT// brewing coffee. morale subsystem: optimal.>\n"
        "\n"
        "---\n"
        "\n"
        "Rho: Morning already?\n"
        "\n"
        "## Coda - Vesper: A name given\n"
        "\n"
        "[She writes her own name in the log for the first time.]\n"
    )

    col_name, _ = st.columns([2, 3])
    with col_name:
        scene_filename = st.text_input(
            "Scene file name (drives the generated label / scene id)",
            value="my_scene.md",
        )

    prose_input = st.text_area(
        "Authored prose (markdown) — edit me",
        value=default_example,
        height=320,
    )

    if not prose_input.strip():
        st.info("Type some prose above to run the converter.")
    else:
        try:
            user_rpy, user_converter = convert_prose_text(
                convert_prose, scene_filename, prose_input
            )
            user_error = None
        except Exception as exc:  # pragma: no cover - surfaced in the UI
            user_rpy, user_converter, user_error = "", None, exc

        if user_error is not None:
            st.error(f"Conversion failed: {user_error}")
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Prose lines", len(prose_input.splitlines()))
            m2.metric("Generated .rpy lines", len(user_rpy.splitlines()))
            m3.metric("Dialogue/narration lines", user_converter.line_count)
            m4.metric("Unknown speakers", len(user_converter.unknown_speakers))

            st.subheader("Output · generated Ren'Py")
            st.code(user_rpy, language="python")
            st.download_button(
                "Download .rpy",
                data=user_rpy,
                file_name=(scene_filename.strip() or "my_scene").replace(
                    ".md", ""
                )
                + ".rpy",
                mime="text/plain",
                key="user_download",
            )

            if user_converter.unknown_speakers:
                st.warning(
                    "Speakers not in the canonical map (the real converter "
                    "auto-generates character vars for these): "
                    + ", ".join(sorted(user_converter.unknown_speakers))
                )
            else:
                st.success(
                    "Every speaker resolved against the canonical speaker map."
                )

            with st.expander("How this is wired"):
                st.markdown(
                    "- Your text → temp `act1/<name>.md`\n"
                    "- `convert_prose.ProseConverter().convert_file(path)` "
                    "(the real engine) → Ren'Py\n"
                    "- Telemetry (`line_count`, `scene_count`, "
                    "`unknown_speakers`) read straight off the converter "
                    "instance — nothing is faked."
                )

with tab_about:
    st.markdown(
        """
This is a **Python toolkit**, not a game engine. It is the conversion and
validation layer that keeps an in-progress game adaptation in sync with the
already-published serial.

**What the toolkit does**

- `tools/convert_prose.py` — turns authored markdown prose into Ren'Py script
  (dialogue, narration, internal monologue, scene breaks, codas, special
  protocol/log formatting). This demo runs it live.
- `tools/convert_dialogue.py` — converts branching dialogue JSON into engine nodes.
- `tools/convert_combat.py` — converts combat encounter data.
- `tools/validate_renpy.py` — static validation of generated Ren'Py
  (jump/call targets, undefined speakers).
- `tools/validate_public_scope.py` / `tools/check_release.py` — release gates that
  enforce the public/private content boundary.

**Why a demo and not a deployable game**

The playable builds live in sibling repos (ChoiceScript web build, Twine
single-HTML, Ren'Py and Godot prototypes). This repo owns the *pipeline*, so the
honest deployable surface is a tool demo: show real prose going through the real
converter.
        """
    )
    st.info(
        "The toolkit has **zero runtime dependencies** (Python stdlib only). "
        "Only this Streamlit UI adds a dependency."
    )
