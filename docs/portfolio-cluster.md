# Starforge Portfolio Cluster

The public Starforge repos are separate by engine and proof claim. Green checks
in one repo do not promote another repo.

| Repo | Claim | Deterministic gate |
|---|---|---|
| `starforge-narrative-tools` | Public Act 1 source and conversion/validation tooling | `python tools/check_release.py` |
| `starforge-renpy-demo` | Act 1 visual-novel narrative demo | `python tools/check_release.py --clean --fail-on-generated --fail-on-renpy-lint-diagnostics --require-renpy --renpy <renpy>` |
| `starforge-rpg-prototype` | Godot RPG systems prototype | `python tools/check_release.py --clean --fail-on-generated --require-godot --godot <godot>` |
| `starforge-twine-demo` | Browser-playable full Act 1 Twine route | `python tools/check_release.py --clean --fail-on-generated` |
| `starforge-choicescript-demo` | Stat-forward full Act 1 ChoiceScript route | `python tools/check_release.py --clean --fail-on-generated` |

## Current Local Evidence

Recorded during the playtest/balance gate update on 2026-05-24:

- `starforge-narrative-tools`: 7 pytest checks passed, public-scope validation passed, tool compilation passed.
- `starforge-renpy-demo`: 7 pytest checks passed, static validator had 0 errors / 0 warnings, playtest path/dead-letter audit passed with 65 routed story scenes and 4 routed combat scenes, and Ren'Py 8.5.2 lint passed.
- `starforge-rpg-prototype`: 3 pytest checks passed, static Godot project validation passed, playtest path/dead-letter audit passed, and `scripts/validate_balance.py` passed with 5 queued warnings. Godot/GUT is wired but not run unless a Godot executable is configured.
- `starforge-twine-demo`: generated 21 main scenes and 44 optional scenes; Twee validation passed with 71 passages, story graph passed with 68 playable/reachable passages, public-scope validation passed, playtest path/dead-letter audit passed with 0 marker hits, Tweego produced `build/index.html`, and 4 Playwright smoke paths passed.
- `starforge-choicescript-demo`: generated 21 main scenes and 44 optional scenes; public-scope validation passed, playtest path/dead-letter audit passed with 143 choices and 65 stat mutations, ChoiceScript quicktest passed, and randomtest passed at 10,000 seeded iterations.

## Boundary Rule

Use the native tool for the codebase:

- Python for source/tooling hygiene.
- Ren'Py lint for Ren'Py.
- Godot/GUT for Godot.
- Tweego plus Playwright for Twine.
- ChoiceScript quicktest/randomtest for ChoiceScript.
- Engine-local `tools/playtest_audit.py` for deterministic path coverage,
  dead-letter queue, and gross balance surfaces before manual release-ready
  claims.
