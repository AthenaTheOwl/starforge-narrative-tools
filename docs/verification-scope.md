# Verification scope — October 18, 2026

The current public Act 1 source was checked without changing prose or
regenerating any published adaptation. `python tools/check_release.py`
passed: 10 Python tests, public-scope validation and tool compilation.

This shows the public tree passes the Act 1-only path and token checks,
every tool compiles, and the prose-to-Ren'Py converter runs over every
released prose file without error (a smoke run through `tools/demo.py`;
only its exit code and header line are checked, not the generated script).
The dialogue and combat converters and `validate_renpy.py` are compiled but
not run here. None of this establishes that a generated game runs in Ren'Py,
Godot, Twine or ChoiceScript. Each sibling owns its engine proof. The
[cluster table](portfolio-cluster.md) records those separately.

October 19 (review branch): the gate now runs 12 Python tests. The two new
ones in `tests/test_convert_prose.py` assert the converter's exact colour and
italic tag output and scan the converted script of all 65 released chapters
for doubled (escaped) tags, so the converter's output is now asserted for
tag validity. Rendering in Ren'Py is still not exercised here.

Keep published prose under author control. Tooling work does not authorize
changes to scenes, voice or canon.
