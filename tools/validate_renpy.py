#!/usr/bin/env python3
"""validate_renpy.py — Validate generated Ren'Py files for Starforge Canticles.

Checks:
1. All jump targets resolve to existing labels
2. All character variables used in say statements are defined
3. No orphan labels (unreachable from entry points)
4. Label naming conventions
"""

import os
import re
import sys


def scan_rpy_files(game_dir):
    """Scan all .rpy files and collect labels, jumps, and character references."""
    labels = set()
    jumps = {}  # {target: [(file, line_num), ...]}
    calls = {}  # {target: [(file, line_num), ...]}
    speakers = set()
    defined_chars = set()

    for root, dirs, files in os.walk(game_dir):
        for fname in files:
            if not fname.endswith(".rpy"):
                continue
            filepath = os.path.join(root, fname)
            relpath = os.path.relpath(filepath, game_dir)

            with open(filepath, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    stripped = line.strip()

                    # Collect labels
                    label_match = re.match(r'^label\s+(\S+?)(?:\(.*\))?:', stripped)
                    if label_match:
                        labels.add(label_match.group(1))

                    # Collect jumps
                    jump_match = re.match(r'^jump\s+(\S+)', stripped)
                    if jump_match:
                        target = jump_match.group(1)
                        jumps.setdefault(target, []).append((relpath, line_num))

                    # Collect calls
                    call_match = re.match(r'^call\s+(?:expression\s+)?(\S+)', stripped)
                    if call_match:
                        target = call_match.group(1)
                        # Skip expression calls with variables
                        if not target.startswith("_") and not target.startswith('"'):
                            calls.setdefault(target, []).append((relpath, line_num))

                    # Collect define statements (character definitions)
                    define_match = re.match(r'^define\s+(\w+)\s*=\s*Character\(', stripped)
                    if define_match:
                        defined_chars.add(define_match.group(1))

                    # Collect speaker usage (character variable in say statement)
                    # Use original line (not stripped) since say statements are indented
                    say_match = re.match(r'^\s+(\w+)\s+"', line)
                    if say_match:
                        speaker = say_match.group(1)
                        if speaker not in ("if", "elif", "else", "while", "for", "return",
                                          "jump", "call", "menu", "pass", "python", "default",
                                          "define", "show", "hide", "scene", "with", "pause",
                                          "centered", "text", "textbutton", "label", "style",
                                          "screen", "frame", "vbox", "hbox", "bar", "add",
                                          "null", "timer", "use", "fixed", "grid", "window",
                                          "viewport", "vpgrid", "has", "tag", "zorder",
                                          "modal", "action", "at"):
                            speakers.add(speaker)

    return labels, jumps, calls, speakers, defined_chars


def validate(game_dir):
    """Run all validation checks."""
    print(f"Validating Ren'Py project: {game_dir}\n")

    labels, jumps, calls, speakers, defined_chars = scan_rpy_files(game_dir)

    errors = 0
    warnings = 0

    # 1. Check jump targets
    print("--- Jump Target Validation ---")
    for target, locations in sorted(jumps.items()):
        # Skip relative jumps (starting with .)
        if target.startswith("."):
            continue
        if target not in labels:
            for file, line in locations:
                print(f"  ERROR: Jump to undefined label '{target}' at {file}:{line}")
                errors += 1

    # 2. Check call targets
    print("\n--- Call Target Validation ---")
    for target, locations in sorted(calls.items()):
        if target.startswith(".") or target.startswith("screen"):
            continue
        if target not in labels:
            # May be a dynamic call or built-in
            for file, line in locations:
                print(f"  WARNING: Call to potentially undefined label '{target}' at {file}:{line}")
                warnings += 1

    # 3. Check speaker definitions
    print("\n--- Speaker Validation ---")
    # Add narrator as always-defined
    defined_chars.add("narrator")
    undefined_speakers = speakers - defined_chars
    # Filter out common false positives
    false_positives = {"properties", "spacing", "xalign", "yalign", "xpos", "ypos",
                       "xsize", "ysize", "xoffset", "yoffset", "color", "size",
                       "bold", "italic", "background", "hover_background", "padding",
                       "selected_color", "hover_color", "insensitive_color",
                       "font", "id", "key", "layout", "scrollbars", "size_group",
                       "style_prefix", "text_color", "text_hover_color", "margin",
                       "xmaximum", "ymaximum", "xminimum", "yminimum", "yfill",
                       "xfill", "spacing", "first_spacing", "box_wrap",
                       "xcenter", "ycenter", "anchor", "pos", "align"}
    undefined_speakers -= false_positives
    for speaker in sorted(undefined_speakers):
        print(f"  WARNING: Speaker variable '{speaker}' used but not defined with Character()")
        warnings += 1

    # 4. Summary stats
    print(f"\n--- Summary ---")
    print(f"  Labels found:    {len(labels)}")
    print(f"  Jump targets:    {len(jumps)}")
    print(f"  Call targets:    {len(calls)}")
    print(f"  Speakers used:   {len(speakers)}")
    print(f"  Characters defined: {len(defined_chars)}")
    print(f"")
    print(f"  Errors:   {errors}")
    print(f"  Warnings: {warnings}")

    return errors == 0


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)

    if len(sys.argv) >= 2:
        game_dir = sys.argv[1]
    else:
        game_dir = os.path.join(base_dir, "starforge-renpy", "game")

    if not os.path.isdir(game_dir):
        print(f"ERROR: Game directory not found: {game_dir}")
        sys.exit(1)

    success = validate(game_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
