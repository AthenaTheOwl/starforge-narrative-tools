# Verification scope — October 18, 2026

The current public Act 1 source was checked without changing prose or
regenerating any published adaptation. `python tools/check_release.py`
passed: 10 Python tests, public-scope validation and tool compilation.

This establishes the source/converter boundary. It does not establish that
a generated game runs in Ren'Py, Godot, Twine or ChoiceScript. Each sibling
owns its engine proof. The [cluster table](portfolio-cluster.md) records
those separately.

For an AI Product Team pilot, give a change reviewer the source diff and
converter output, and a verifier the actual gate output. Preserve the
existing gate as the acceptance check. A role's final summary is not a
replacement for it. Start with one converter maintenance task; cap review
at one reviewer and one repair, and record any useful defect found.

Keep published prose under author control. Research notes can propose a
tooling experiment; they do not authorize changes to scenes, voice or canon.
