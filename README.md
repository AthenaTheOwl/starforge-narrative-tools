# No. 14 - starforge-narrative-tools

[Starforge Canticles](https://www.royalroad.com/fiction/149065/starforge-canticles)
is a serialized speculative-fiction novel I'm publishing chapter-by-chapter on
Royal Road. This repo is the Python toolkit behind it: prose-to-game schemas,
conversion pipeline, and validation gates that keep the in-progress game
adaptation in sync with what's already public.

Active development happens in a private workshop. This public copy is cleaned
for portfolio review: only released Act 1 material is included, later acts
are excluded, runtime junk is excluded, and tests are added so the repo can be
iterated on safely.

## What this proves

- Large passion projects need the same guardrails as product work.
- Narrative adaptation can be treated as a pipeline: prose, specs, conversion,
  validation, and regression checks.
- The useful artifact is not only the story. It is the operating system around
  a published serial and its in-progress game adaptation.
- AI-assisted creative work still needs release boundaries, validation, and
  clean public/private separation.

## Live demo

This repo is a Python toolkit, not a playable engine build, so its honest
deployable surface is a **tool demo** that runs the real converter on the real
released prose.

- No-argument capability tour (read-only, writes nothing):

  ```powershell
  python tools\demo.py
  ```

  Converts all 66 released Act 1 prose files in memory and prints a prose-line ->
  generated-Ren'Py-line summary plus a sample of generated script.

- Interactive Streamlit app (deploy target: Streamlit Community Cloud, entry
  point `streamlit_app.py`):

  ```powershell
  pip install -r requirements.txt
  streamlit run streamlit_app.py
  ```

  Pick a released Act 1 chapter and watch authored markdown prose convert to
  engine-ready Ren'Py live, side by side, with the speaker map and a download
  button. The toolkit has zero runtime dependencies; only this demo UI needs
  streamlit (`requirements.txt`).

The playable game builds live in the sibling repos (ChoiceScript static web
build, Twine single-HTML, plus the Ren'Py and Godot prototypes). This repo owns
the conversion/validation pipeline.

## What is included

- `prose/act1/` - released Act 1 prose slice copied from the active workshop
- `spec/` - Act 1-safe public specs and adaptation notes
- `tools/` - Python conversion and validation utilities
- `tests/` - repo-level hygiene and tooling checks
- `docs/` - portfolio framing and cleanup policy

## What is intentionally excluded

- Game engine runtime files
- unreleased later-act prose/spec content
- Ren'Py compiled files and saves
- Godot editor state
- SDK folders
- private task-daemon state

## Validate

```powershell
python -m pytest
python -m compileall tools
python tools\check_release.py
```

`tools/check_release.py` is the deterministic orchestration entry point for
this repo. It intentionally uses Python validation only because this repo owns
source hygiene and conversion tooling, not a playable engine runtime. For
cluster-wide strict runs it also accepts `--clean --fail-on-generated`; those
flags are no-ops here because this repo has no engine-generated runtime
artifacts to keep or clean. See
`docs/deterministic-orchestration.md` for the proof gates.

## See also

Part of the Starforge cluster:

- [starforge-renpy-demo](https://github.com/AthenaTheOwl/starforge-renpy-demo) - Act 1 Ren'Py narrative demo copy
- [starforge-rpg-prototype](https://github.com/AthenaTheOwl/starforge-rpg-prototype) - Act 1 Godot RPG prototype copy
- [starforge-twine-demo](https://github.com/AthenaTheOwl/starforge-twine-demo) - single-HTML Twine/SugarCube demo
- [starforge-choicescript-demo](https://github.com/AthenaTheOwl/starforge-choicescript-demo) - stat-forward ChoiceScript demo
