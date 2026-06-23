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

tab_convert, tab_about = st.tabs(["Convert prose → Ren'Py", "What this is"])

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
