#!/usr/bin/env python3
"""convert_dialogue.py — Transform Starforge Canticles dialogue JSON files into Ren'Py .rpy files.

Usage:
    python convert_dialogue.py <input_dir> <output_dir>
    python convert_dialogue.py  # defaults: ../starforge-rpg/data/dialogue -> ../starforge-renpy/game/dialogue

Each JSON file produces one .rpy file with:
- A top-level label matching the dialogue ID
- One sub-label per node, prefixed with the dialogue ID
- Proper handling of choices, skill checks, flags, reputation, text variants, BEE protocol
"""

import json
import os
import re
import sys


# Speaker name -> Ren'Py character variable mapping
SPEAKER_MAP = {
    "SYSTEM": "narrator",
    "Narration": "narrator",
    "Avyanna": "avyanna",
    "Elia": "elia",
    "Elisira": "elisira",
    "Vesper": "vesper",
    "Nyx": "nyx",
    "Rho": "rho",
    "Jalen": "jalen",
    "Waffle.bat": "waffle",
    "Bubbles": "bubbles",
    "Cinnamon": "cinnamon",
    "Souffle": "souffle",
    "Soufflé": "souffle",
    "Grove": "grove",
    "Bee": "bee",
    "BEE": "bee",
    "Lead Pirate": "lead_pirate",
    "Pirate": "pirate",
    "Security Sergeant": "security_sergeant",
    "ALL": "all_crew",
    "???": "unknown",
    "QC-7": "qc_7",
}

# Known character IDs for reputation normalization.
# Keys not in this set are treated as faction/system reputation (set as flags).
KNOWN_CHARACTER_IDS = {
    "elia", "elisira", "vesper", "jalen", "nyx", "rho",
    "waffle", "bubbles", "cinnamon", "souffle", "grove", "bee",
}

# Maps display-name reputation keys to normalized character IDs
REPUTATION_KEY_MAP = {
    "Waffle.bat": "waffle",
    "Bubbles": "bubbles",
    "Cinnamon": "cinnamon",
    "Souffle": "souffle",
    "Soufflé": "souffle",
    "Elia": "elia",
    "Elisira": "elisira",
    "Vesper": "vesper",
    "Nyx": "nyx",
    "Rho": "rho",
    "Jalen": "jalen",
    "Bee": "bee",
    "BEE": "bee",
    "Grove": "grove",
    "QC-7": "qc_7",
}


def sanitize_label(name):
    """Convert a node ID to a valid Ren'Py label name."""
    s = name.replace("-", "_").replace(" ", "_").replace(".", "_")
    s = re.sub(r'[^a-zA-Z0-9_]', '', s)
    if s and s[0].isdigit():
        s = "_" + s
    return s


def convert_bbcode(text):
    """Convert Godot BBCode tags to Ren'Py text tags."""
    text = text.replace("[i]", "{i}")
    text = text.replace("[/i]", "{/i}")
    text = text.replace("[b]", "{b}")
    text = text.replace("[/b]", "{/b}")
    text = text.replace("[u]", "{u}")
    text = text.replace("[/u]", "{/u}")
    text = text.replace("[s]", "{s}")
    text = text.replace("[/s]", "{/s}")
    text = text.replace("[/color]", "{/color}")
    # Convert [color=X]...[/color] — must use regex to properly close the tag
    text = re.sub(r'\[color=([^\]]+)\]', r'{color=\1}', text)
    return text


def escape_renpy_text(text):
    """Escape special characters for Ren'Py string literals."""
    text = text.replace("\\n", "\n")
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    text = convert_bbcode(text)
    return text


def speaker_to_var(speaker):
    """Map a speaker name to its Ren'Py character variable."""
    if speaker in SPEAKER_MAP:
        return SPEAKER_MAP[speaker]
    for key, val in SPEAKER_MAP.items():
        if key.lower() == speaker.lower():
            return val
    var_name = speaker.lower().replace(" ", "_").replace(".", "_")
    var_name = re.sub(r'[^a-z0-9_]', '', var_name)
    return var_name


def normalize_reputation_key(raw_key):
    """Normalize a reputation key to a character ID, or return None if not a character."""
    # Check explicit mapping first
    if raw_key in REPUTATION_KEY_MAP:
        return REPUTATION_KEY_MAP[raw_key]
    # Check if already a known lowercase character ID
    lower_key = raw_key.lower()
    if lower_key in KNOWN_CHARACTER_IDS:
        return lower_key
    # Not a known character — this is a faction/system reputation key
    return None


def format_say(speaker, text, indent=4):
    """Format a Ren'Py say statement."""
    prefix = " " * indent
    escaped = escape_renpy_text(text)
    char_var = speaker_to_var(speaker)
    if char_var == "narrator":
        return f'{prefix}"{escaped}"'
    else:
        return f'{prefix}{char_var} "{escaped}"'


def format_jump(dialogue_id, target, indent=4):
    """Format a jump statement. 'end' returns from the dialogue."""
    prefix = " " * indent
    if target == "end":
        return f"{prefix}return"
    label = f"{dialogue_id}_{sanitize_label(target)}"
    return f"{prefix}jump {label}"


def emit_effects(node_or_choice, indent=4):
    """Emit set_flag and reputation Python calls for a node or choice."""
    lines = []
    prefix = " " * indent

    if "set_flag" in node_or_choice:
        flag_name = node_or_choice["set_flag"]
        flag_value = node_or_choice.get("flag_value", True)
        if isinstance(flag_value, bool):
            lines.append(f'{prefix}$ game_state.set_flag("{flag_name}")')
        else:
            lines.append(f'{prefix}$ game_state.set_flag("{flag_name}", {repr(flag_value)})')

    if "reputation" in node_or_choice:
        rep = node_or_choice["reputation"]
        for raw_key, amount in rep.items():
            char_id = normalize_reputation_key(raw_key)
            if char_id:
                # Known character — route through affinity system
                lines.append(f'{prefix}$ relationship_manager.process_reputation_affinity("{char_id}", {amount})')
            else:
                # Faction/system key — store as a flag with cumulative value
                safe_key = raw_key.lower().replace(" ", "_").replace(".", "_").replace("-", "_")
                lines.append(f'{prefix}$ game_state.set_flag("rep_{safe_key}", game_state.get_flag("rep_{safe_key}", 0) + {amount})')

    return lines


def emit_skill_check(check, dialogue_id, indent=4):
    """Emit skill check logic: roll + branching."""
    lines = []
    prefix = " " * indent

    stat = check.get("stat", check.get("skill", "attack"))
    dc = check.get("dc", check.get("threshold", 10))
    character = check.get("character", "avyanna")
    on_success = check.get("on_success", "end")
    on_failure = check.get("on_failure", "end")

    lines.append(f'{prefix}$ _sc_result = skill_check("{stat}", {dc}, "{character}")')
    lines.append(f'{prefix}if _sc_result == "SUCCESS" or _sc_result == "CRITICAL_SUCCESS":')
    lines.append(format_jump(dialogue_id, on_success, indent + 4))
    lines.append(f'{prefix}else:')
    lines.append(format_jump(dialogue_id, on_failure, indent + 4))

    return lines


def extract_flags_from_condition(cond):
    """Extract flag names from a condition dict.
    Handles both singular and plural forms:
      {"flag": "name"}         -> ["name"]
      {"flags": ["a", "b"]}   -> ["a", "b"]
      {}                       -> []  (empty = default/unconditional)
    """
    if not cond:
        return []
    # Singular: {"flag": "name"}
    if "flag" in cond:
        return [cond["flag"]]
    # Plural: {"flags": ["a", "b"]}
    if "flags" in cond:
        flags = cond["flags"]
        if isinstance(flags, list):
            return flags
        return [flags]
    return []


def emit_text_variants(node, speaker, indent=4):
    """Emit conditional text based on text_variants.

    Handles:
    - Dict format: {"flag_name": "alt text", "default": "normal text"}
    - Array format: [{"condition": {"flag": "x"}, "text": "..."}, ...]
      with condition.flag (singular), conditions.flags (plural array),
      and empty condition {} as default.
    """
    lines = []
    prefix = " " * indent
    variants = node["text_variants"]
    base_text = node.get("text", "")

    if isinstance(variants, dict):
        # Dict format: {flag_name: "alt text", "default": "normal text"}
        flags = [k for k in variants if k != "default"]
        default_text = variants.get("default", base_text)

        for i, flag in enumerate(flags):
            kw = "if" if i == 0 else "elif"
            lines.append(f'{prefix}{kw} game_state.has_flag("{flag}"):')
            lines.append(format_say(speaker, variants[flag], indent + 4))
        if default_text:
            if flags:
                lines.append(f"{prefix}else:")
                lines.append(format_say(speaker, default_text, indent + 4))
            else:
                lines.append(format_say(speaker, default_text, indent))

    elif isinstance(variants, list):
        # Array format: [{condition(s): {...}, text: "..."}, ...]
        conditional_variants = []
        default_text = base_text

        for variant in variants:
            cond = variant.get("conditions", variant.get("condition", {}))
            flags = extract_flags_from_condition(cond)
            vtext = variant.get("text", "")

            if not flags:
                # Empty condition = default text
                default_text = vtext
            else:
                conditional_variants.append((flags, vtext))

        # Emit if/elif chain for conditional variants
        emitted_any = False
        for i, (flags, vtext) in enumerate(conditional_variants):
            kw = "if" if i == 0 else "elif"
            if len(flags) == 1:
                lines.append(f'{prefix}{kw} game_state.has_flag("{flags[0]}"):')
            else:
                # Multiple flags — all must be set
                checks = " and ".join(f'game_state.has_flag("{f}")' for f in flags)
                lines.append(f'{prefix}{kw} {checks}:')
            lines.append(format_say(speaker, vtext, indent + 4))
            emitted_any = True

        # Emit default/else
        if default_text:
            if emitted_any:
                lines.append(f"{prefix}else:")
                lines.append(format_say(speaker, default_text, indent + 4))
            else:
                lines.append(format_say(speaker, default_text, indent))

    return lines


def emit_variants_branching(node, dialogue_id, indent=4):
    """Emit branching based on 'variants' field (branch-selection, not text replacement).

    Source format:
    "variants": [
        {"conditions": {"flag": "X"}, "next": "target_a"},
        {"conditions": {"flag": "Y"}, "next": "target_b"},
    ]
    "next": "fallback_target"
    """
    lines = []
    prefix = " " * indent
    variants = node["variants"]
    fallback = node.get("next", "end")

    for i, variant in enumerate(variants):
        cond = variant.get("conditions", {})
        flags = extract_flags_from_condition(cond)
        target = variant.get("next", fallback)

        if flags:
            kw = "if" if i == 0 else "elif"
            if len(flags) == 1:
                lines.append(f'{prefix}{kw} game_state.has_flag("{flags[0]}"):')
            else:
                checks = " and ".join(f'game_state.has_flag("{f}")' for f in flags)
                lines.append(f'{prefix}{kw} {checks}:')
            lines.append(format_jump(dialogue_id, target, indent + 4))

    # Fallback
    lines.append(f"{prefix}else:")
    lines.append(format_jump(dialogue_id, fallback, indent + 4))

    return lines


def convert_node(dialogue_id, node_id, node, all_nodes):
    """Convert a single dialogue node to Ren'Py lines."""
    lines = []
    label = f"{dialogue_id}_{sanitize_label(node_id)}"
    speaker = node.get("speaker", "SYSTEM")
    text = node.get("text", "")
    has_choices = "choices" in node and node["choices"]
    node_type = node.get("type", "")

    lines.append(f"label {label}:")

    # Node-level effects (set_flag, reputation) — emit before text
    effect_lines = emit_effects(node, indent=4)
    lines.extend(effect_lines)

    # Handle type="skill_check" nodes (have "check" field instead of "skill_check")
    if node_type == "skill_check" and "check" in node:
        check = node["check"]
        if text:
            lines.append(format_say(speaker, text))
        lines.extend(emit_skill_check(check, dialogue_id))
        lines.append("")
        return lines

    # Handle standalone skill_check field (no choices)
    if "skill_check" in node and not has_choices:
        check = node["skill_check"]
        if text:
            lines.append(format_say(speaker, text))
        lines.extend(emit_skill_check(check, dialogue_id))
        lines.append("")
        return lines

    # Text with variants (text replacement, not branch selection)
    if "text_variants" in node:
        lines.extend(emit_text_variants(node, speaker))
    elif text:
        lines.append(format_say(speaker, text))

    # Handle "variants" field (branch-selection: changes next target based on flags)
    if "variants" in node and isinstance(node["variants"], list):
        lines.extend(emit_variants_branching(node, dialogue_id))
        lines.append("")
        return lines

    # Choice node
    if has_choices:
        lines.append("    menu:")
        for choice in node["choices"]:
            choice_text = escape_renpy_text(choice.get("text", ""))
            lines.append(f'        "{choice_text}":')

            # Choice-level effects
            choice_effects = emit_effects(choice, indent=12)
            lines.extend(choice_effects)

            # Skill check on choice
            if "skill_check" in choice:
                check = choice["skill_check"]
                has_branches = check.get("on_success") or check.get("on_failure")
                if has_branches:
                    lines.extend(emit_skill_check(check, dialogue_id, indent=12))
                else:
                    stat = check.get("stat", check.get("skill", "attack"))
                    dc = check.get("dc", check.get("threshold", 10))
                    character = check.get("character", "avyanna")
                    lines.append(f'            $ _sc_result = skill_check("{stat}", {dc}, "{character}")')
                    target = choice.get("next", "end")
                    lines.append(format_jump(dialogue_id, target, indent=12))
            else:
                target = choice.get("next", "end")
                lines.append(format_jump(dialogue_id, target, indent=12))
    else:
        # Linear node — jump to next
        target = node.get("next", "end")
        lines.append(format_jump(dialogue_id, target))

    lines.append("")
    return lines


def convert_dialogue_file(json_path, output_path):
    """Convert a single dialogue JSON file to a .rpy file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dialogue_id = os.path.splitext(os.path.basename(json_path))[0]
    start_node = data.get("start_node", "start")
    nodes = data.get("nodes", {})

    all_lines = []
    all_lines.append(f"## {dialogue_id}.rpy — Auto-generated from {os.path.basename(json_path)}")
    all_lines.append(f"## {len(nodes)} dialogue nodes")
    all_lines.append("")

    # Top-level entry label
    all_lines.append(f"label {dialogue_id}:")
    all_lines.append(f"    $ game_state.mark_dialogue_played(\"{dialogue_id}\")")
    all_lines.append(f"    jump {dialogue_id}_{sanitize_label(start_node)}")
    all_lines.append("")

    # Convert each node
    for node_id, node in nodes.items():
        node_lines = convert_node(dialogue_id, node_id, node, nodes)
        all_lines.extend(node_lines)

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_lines))

    return dialogue_id, len(nodes)


def collect_speakers(input_dir):
    """Scan all dialogue files and collect unique speaker names."""
    speakers = set()
    for filename in os.listdir(input_dir):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(input_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for node in data.get("nodes", {}).values():
            speaker = node.get("speaker", "")
            if speaker:
                speakers.add(speaker)
    return speakers


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)

    if len(sys.argv) >= 3:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
    else:
        input_dir = os.path.join(base_dir, "starforge-rpg", "data", "dialogue")
        output_dir = os.path.join(base_dir, "starforge-renpy", "game", "dialogue")

    if not os.path.isdir(input_dir):
        print(f"ERROR: Input directory not found: {input_dir}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Collect and report speakers
    speakers = collect_speakers(input_dir)
    unmapped = speakers - set(SPEAKER_MAP.keys())
    if unmapped:
        print(f"WARNING: Unmapped speakers (will use auto-generated var names): {unmapped}")

    # Convert all files
    total_files = 0
    total_nodes = 0

    json_files = sorted(f for f in os.listdir(input_dir) if f.endswith(".json"))
    for filename in json_files:
        json_path = os.path.join(input_dir, filename)
        rpy_filename = filename.replace(".json", ".rpy")
        rpy_path = os.path.join(output_dir, rpy_filename)

        dialogue_id, node_count = convert_dialogue_file(json_path, rpy_path)
        total_files += 1
        total_nodes += node_count
        print(f"  {node_count:>4} nodes  {dialogue_id}")

    print(f"\nConverted {total_files} files ({total_nodes} total nodes)")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
