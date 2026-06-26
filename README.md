# starforge-narrative-tools

The prologue opens on a form. GUILD CONCORD - FORM 7-DELTA: vessel boarded, casualties 0 (crew) / 4 (hostile, non-fatal), coffee machine status unchanged, the rest redacted. That paragraph is markdown in this repo. By the time the converter is done with it, it's a Ren'Py label with a speaker, color tags, and a pause — engine-ready, generated, do-not-edit-by-hand. This repo is the machine that does that, to all 66 chapters at once.

## What it does

[Starforge Canticles](https://www.royalroad.com/fiction/149065/starforge-canticles) is a serialized novel I publish chapter-by-chapter on Royal Road. The novel is also becoming a game, and a game wants the prose as script — speakers tagged, formatting translated, every chapter labeled — not as paragraphs. Doing that by hand once is fine. Doing it again every time a chapter changes is how a passion project quietly dies.

So the prose is the source and the script is generated. This repo holds the converter, the speaker map (39 of them), the validation gates, and the release boundary. The converter reads authored markdown and writes Ren'Py the engine can run. The gates check the result. And the release boundary is the load-bearing part: active writing happens in a private workshop, and this public copy ships only the material that's already published — released Act 1, nothing from later, no compiled engine junk, no half-written future. The repo can't leak the next chapter because the next chapter was never copied in.

## Try it

One command, no arguments, no setup. It converts every released chapter in memory and prints the tally — it writes nothing:

```powershell
python tools\demo.py
```

```
Released Act 1 prose files found: 66
Speakers mapped in converter:     39

  00_prologue_floors_not_thrones.md                 468 md lines ->  264 rpy lines
  01_cinder_hours.md                                455 md lines ->  263 rpy lines
  ...
  20_the_receipt.md                                1884 md lines -> 1198 rpy lines
  act1_combined.md                                 23866 md lines -> 14817 rpy lines

----------------------------------------------------------------------
  TOTAL: 47473 prose lines -> 29502 generated Ren'Py lines
----------------------------------------------------------------------

Sample generated Ren'Py (first 18 lines of 00_prologue_floors_not_thrones.md):

  | label act1_00_prologue_floors_not_thrones:
  |     narrator "{i}The hull screams before the alarms do.{/i}"
  |     elia "{i}[[into comm, not breaking stride]]{/i} Waffle. Report."
```

47,473 prose lines in, 29,502 generated script lines out. None of those output lines are checked in — they're produced fresh every run, which is the whole point of keeping the prose as the source.

## Live demo

Same converter, as a page you can poke. Pick a released Act 1 chapter and watch the authored markdown turn into Ren'Py live and side by side, with the speaker map and a download button. The toolkit has zero runtime dependencies; only this demo UI wants streamlit.

```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud: repo `AthenaTheOwl/starforge-narrative-tools`, branch `main`, main file `streamlit_app.py`.

<!-- live-url: (add the streamlit cloud url here once deployed) -->

## How it connects

This repo owns the conversion and validation. The playable builds live next door, each a different shape for the same Act 1 prose:

- [starforge-renpy-demo](https://github.com/AthenaTheOwl/starforge-renpy-demo) — the Act 1 Ren'Py narrative demo, the format this converter targets.
- [starforge-rpg-prototype](https://github.com/AthenaTheOwl/starforge-rpg-prototype) — the Act 1 Godot RPG prototype.
- [starforge-twine-demo](https://github.com/AthenaTheOwl/starforge-twine-demo) — the same chapters as a single-HTML Twine/SugarCube demo.
- [starforge-choicescript-demo](https://github.com/AthenaTheOwl/starforge-choicescript-demo) — a stat-forward ChoiceScript cut.

## Validate

```powershell
python -m pytest
python -m compileall tools
python tools\check_release.py
```

`tools/check_release.py` is the deterministic release gate. It's Python-only on purpose — this repo guards source hygiene and conversion, not a playable engine, so there are no generated runtime artifacts to clean. For cluster-wide strict runs it accepts `--clean --fail-on-generated`; those flags are no-ops here, since there's nothing engine-generated to fail on. The gates are written up in `docs/deterministic-orchestration.md`.

## Layout

```
prose/act1/   released Act 1 prose, copied from the private workshop
spec/         Act 1-safe specs and adaptation notes
tools/        the converter, validators, demo, and release gate
tests/        repo hygiene and tooling checks
docs/         framing and the cleanup policy
```

Excluded on purpose: engine runtime files, unreleased later-act prose, compiled Ren'Py and saves, Godot editor state, SDK folders, private task-daemon state.

## License

MIT. See [LICENSE](LICENSE).
