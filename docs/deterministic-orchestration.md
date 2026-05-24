# Deterministic Orchestration

This repo is the source and tooling proof for the public Starforge slice. Its
orchestration should be deterministic Python validation, not game-engine or
browser automation.

## Native Tooling

- `python -m pytest` runs corpus, cleanup, and tooling tests.
- `python tools/validate_public_scope.py` enforces the public Act 1 boundary.
- `python -m compileall tools` verifies the conversion and validation scripts
  still compile.
- `python tools/check_release.py` runs the repo-local release gate in order.
- `python tools/check_release.py --clean --fail-on-generated` is accepted for
  cluster-wide strict runs; the flags are no-ops here because there are no
  engine-generated runtime artifacts in this source/tooling repo.

## Proof Gates

1. Public Act 1 prose and specs are present.
2. No unreleased source paths or generated runtime artifacts are present.
3. Conversion and validation tools compile.
4. The public-scope validator passes.
5. README claims stay limited to source, tooling, conversion, and validation.

## CI Ring

The GitHub Actions workflow runs `tools/check_release.py`. This is enough for
this repo because it does not own a playable engine runtime. Engine-specific
proof belongs in the Ren'Py, Godot, Twine, or ChoiceScript repos.

## Release Rule

Do not promote a downstream game repo from this repo's green tests alone. This
repo proves source hygiene and conversion/tooling readiness; each engine repo
must run its own native gate.
