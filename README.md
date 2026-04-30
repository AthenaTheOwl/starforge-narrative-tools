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

- [starforge-renpy-demo](https://github.com/AthenaTheOwl/starforge-renpy-demo) - Act 1 Ren'Py narrative demo copy
- [starforge-rpg-prototype](https://github.com/AthenaTheOwl/starforge-rpg-prototype) - Act 1 Godot RPG prototype copy
