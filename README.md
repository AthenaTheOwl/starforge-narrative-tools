# No. 14 - starforge-narrative-tools

A curated exhibit from Starforge, an in-progress narrative game project. This
repo extracts the public Act 1 slice plus the Python conversion and validation
tooling used to move long-form writing toward game-ready data.

The story itself is published as
[Starforge Canticles on Royal Road](https://www.royalroad.com/fiction/149065/starforge-canticles).
This repo shows the production system around the published portion of that
public serial.

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
```

## See also

Part of the Starforge cluster:

- [starforge-narrative-tools](https://github.com/AthenaTheOwl/starforge-narrative-tools) - public Act 1 corpus + conversion/validation tooling
- [starforge-renpy-demo](https://github.com/AthenaTheOwl/starforge-renpy-demo) - Act 1 Ren'Py narrative demo copy
- [starforge-rpg-prototype](https://github.com/AthenaTheOwl/starforge-rpg-prototype) - Act 1 Godot RPG prototype copy
