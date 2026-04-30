#!/usr/bin/env python3
"""convert_prose.py — Transform Starforge Canticles prose markdown files into Ren'Py .rpy files.

Usage:
    python convert_prose.py <input_dir> <output_dir> [--act N]
    python convert_prose.py                          # defaults: ../prose -> ../starforge-renpy/game/prose_scenes
    python convert_prose.py --act 1                  # only convert act1
    python convert_prose.py --act 1                  # public repo only includes Act 1

Each .md prose file produces one .rpy file with:
- A top-level label matching the scene ID (derived from filename)
- Scene breaks (---) become visual pauses with transitions
- Dialogue lines (Character: text) become character say statements
- Narration in [brackets] becomes narrator italic text
- Internal monologue in (parentheses) becomes narrator text
- BEE/SHARD protocol messages get special formatting
- WAFFLE.BAT logs get monospace amber styling
- Blockquote documents/logs become styled narrator text
- Coda sections (## Coda) become separate labels
"""

import os
import re
import sys
from pathlib import Path


# ──────────────────────────────────────────────────────────────────────
# Speaker mapping: prose name -> Ren'Py character variable
# ──────────────────────────────────────────────────────────────────────
SPEAKER_MAP = {
    # Main crew
    "Avyanna": "avyanna",
    "Elia": "elia",
    "Elisira": "elisira",
    "Vesper": "vesper",
    "Nyx": "nyx",
    "Rho": "rho",
    "Jalen": "jalen",
    # AI citizens
    "Waffle.bat": "waffle",
    "Waffle": "waffle",
    "WAFFLE.BAT": "waffle",
    "Bubbles": "bubbles",
    "Cinnamon": "cinnamon",
    "Souffle": "souffle",
    "Soufflé": "souffle",
    "Grove": "grove",
    # Entity
    "Bee": "bee",
    "BEE": "bee",
    # Recurring NPCs
    "Rowan": "rowan",
    "Senna": "senna",
    "Orin": "orin",
    "Maren": "maren",
    "Aleena": "aleena",
    "Halcyon": "halcyon",
    "Keris": "keris",
    "Via": "via",
    "Kenna": "kenna",
    # Generic / incidental
    "Lead Pirate": "lead_pirate",
    "Pirate": "pirate",
    "Guard": "guard",
    "Clerk": "clerk",
    "Dockhand": "dockhand",
    "Worker": "worker",
    "Corporate Officer": "corp_officer",
    "Security Sergeant": "security_sergeant",
    "QC-7": "qc_7",
    "ALL": "all_crew",
    "???": "unknown",
    "SYSTEM": "narrator",
    "Narration": "narrator",
}

# Characters that need Character() definitions added (not in current characters.rpy)
NEW_CHARACTERS = {}  # populated during conversion


def sanitize_label(name):
    """Convert a filename/string to a valid Ren'Py label."""
    name = name.lower()
    name = re.sub(r'[^a-z0-9_]', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    return name


def get_scene_id(filepath):
    """Derive scene ID from filepath: act1/09a_medical_autonomy.md -> act1_09a_medical_autonomy"""
    path = Path(filepath)
    act = path.parent.name  # public repo contains "act1"
    stem = path.stem  # "09a_medical_autonomy"
    return sanitize_label(f"{act}_{stem}")


def escape_renpy(text):
    """Escape characters that are special in Ren'Py strings."""
    # Escape existing curly braces that aren't Ren'Py tags
    # But preserve {i}, {b}, {color=...}, {/i}, {/b}, {/color}, {size=...}, {/size}
    # First, handle percent signs and backslashes
    text = text.replace('\\', '\\\\')
    # Escape double quotes inside strings
    text = text.replace('"', '\\"')
    # Square brackets need escaping in Ren'Py (they're interpolation)
    # But we use them for narration detection first, so escape after parsing
    return text


def escape_renpy_text(text):
    """Escape text for use inside Ren'Py say statements."""
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    # Square brackets in Ren'Py are variable interpolation - escape literal ones
    text = text.replace('[', '[[')
    return text


def convert_bbcode(text):
    """Convert markdown/BBCode formatting to Ren'Py text tags."""
    # Bold: **text** or __text__ -> {b}text{/b}
    text = re.sub(r'\*\*(.+?)\*\*', r'{b}\1{/b}', text)
    text = re.sub(r'__(.+?)__', r'{b}\1{/b}', text)
    # Italic: *text* or _text_ -> {i}text{/i}
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'{i}\1{/i}', text)
    # BBCode pass-through
    text = text.replace('[i]', '{i}').replace('[/i]', '{/i}')
    text = text.replace('[b]', '{b}').replace('[/b]', '{/b}')
    # Color tags
    text = re.sub(r'\[color=([^\]]+)\]', r'{color=\1}', text)
    text = text.replace('[/color]', '{/color}')
    return text


def parse_stage_direction(text):
    """Extract stage direction from dialogue: [into comm, quiet] -> (direction, remaining_text)"""
    match = re.match(r'^\[([^\]]+)\]\s*(.*)$', text)
    if match:
        return match.group(1), match.group(2)
    return None, text


def is_dialogue_line(line):
    """Check if a line is dialogue: Character: [optional direction] text"""
    # Match "Name:" or "Name.ext:" at start of line
    match = re.match(r'^([A-Z][a-zA-Z.\'\- ]+?):\s+(.+)$', line)
    if match:
        speaker = match.group(1)
        # Filter out false positives (markdown headers, scene metadata)
        if speaker in ('Location', 'Present', 'Teaching', 'Subject', 'Status',
                       'Note', 'Addendum', 'Reminder', 'Entry', 'Date',
                       'Classification', 'Outcome', 'Casualties', 'Vessel',
                       'File', 'WARNING', 'NOTICE', 'ALERT', 'ERROR',
                       'HULL INTEGRITY ALERT', 'Type', 'Priority', 'Source',
                       'Destination', 'Duration', 'Result', 'Ref', 'CC',
                       'From', 'To', 'Re', 'CAUTION', 'OVERRIDE',
                       'FLOOR', 'FLOORS NOT THRONES', 'Title', 'TOTAL',
                       'PAY', 'PENALTY', 'QUOTA', 'Dessert',
                       'A lesson', 'Following the chaos girl',
                       'The outside world insists', 'Staying in the corridor',
                       'Timestamp', 'Instance', 'Processing note',
                       'Observation', 'Assessment', 'Action',
                       'Flag purpose', 'Flag type', 'Severity',
                       'Recommendation', 'Clarification', 'Override'):
            return None
        return speaker, match.group(2)
    return None


def is_narration_bracket(line):
    """Check if line is bracketed narration: [The ship creaks...]"""
    return line.startswith('[') and line.endswith(']') and not line.startswith('[SCENE')


def is_internal_monologue(line):
    """Check if line is parenthesized internal thought: (She isn't ready.)"""
    return line.startswith('(') and line.endswith(')')


def is_bee_protocol(line):
    """Check for BEE/SHARD protocol: {BEE:: msg} or {SHARD:: msg}"""
    return bool(re.match(r'^\{(BEE|SHARD|LATTICE)::', line))


def is_ai_citizen_log(line):
    """Check for AI citizen log: <WAFFLE.BAT// ...>, <BUBBLES// ...>, <CINNAMON.EXE// ...>, etc."""
    return bool(re.match(r'^<(WAFFLE|BUBBLES|CINNAMON|SOUFFLE|GROVE|LUMEN|VIA)[.\w]*\s*//', line))


def is_scene_break(line):
    """Check for scene break: ---"""
    return line.strip() == '---'


def is_chapter_header(line):
    """Check for chapter header: # Chapter X: Title"""
    return line.startswith('# ')


def is_coda_header(line):
    """Check for coda section: ## Coda - Character: Title"""
    return line.startswith('## Coda')


def is_blockquote(line):
    """Check for blockquote: > text"""
    return line.startswith('> ')


def is_scene_metadata(line):
    """Check for scene metadata block: > **[SCENE - ...]**"""
    return line.startswith('> **[SCENE') or line.startswith('> *Location') or \
           line.startswith('> *Present') or line.startswith('> *Teaching')


class ProseConverter:
    def __init__(self):
        self.unknown_speakers = set()
        self.scene_count = 0
        self.line_count = 0
        self.all_scene_ids = []

    def resolve_speaker(self, name):
        """Map speaker name to Ren'Py character variable."""
        if name in SPEAKER_MAP:
            return SPEAKER_MAP[name]
        # Try case-insensitive match
        for key, val in SPEAKER_MAP.items():
            if key.lower() == name.lower():
                return val
        # Generate a variable name for unknown speakers
        var_name = sanitize_label(name)
        # Avoid Ren'Py reserved keywords
        RENPY_KEYWORDS = {
            'if', 'elif', 'else', 'while', 'for', 'pass', 'return',
            'jump', 'call', 'scene', 'show', 'hide', 'with', 'play',
            'stop', 'voice', 'define', 'default', 'init', 'python',
            'screen', 'style', 'transform', 'image', 'menu', 'label',
            'pause', 'queue', 'window', 'nvl', 'and', 'or', 'not',
            'in', 'is', 'as', 'from', 'import', 'class', 'del',
            'try', 'except', 'finally', 'raise', 'yield', 'assert',
            'lambda', 'global', 'nonlocal', 'break', 'continue',
            'true', 'false', 'none',
        }
        if var_name in RENPY_KEYWORDS:
            var_name = var_name + "_char"
        if var_name not in NEW_CHARACTERS:
            NEW_CHARACTERS[var_name] = name
            self.unknown_speakers.add(name)
        return var_name

    def format_dialogue(self, speaker_var, direction, text, indent="    "):
        """Format a dialogue line as Ren'Py say statement."""
        text = convert_bbcode(text)
        text = escape_renpy_text(text)

        if direction:
            direction_escaped = escape_renpy_text(direction)
            if speaker_var == "narrator":
                return f'{indent}narrator "{{i}}[[{direction_escaped}]] {text}{{/i}}"'
            return f'{indent}{speaker_var} "{{i}}[[{direction_escaped}]]{{/i}} {text}"'
        else:
            if speaker_var == "narrator":
                return f'{indent}narrator "{{i}}{text}{{/i}}"'
            return f'{indent}{speaker_var} "{text}"'

    def format_narration(self, text, indent="    "):
        """Format narration (bracketed text) as italic narrator."""
        # Strip outer brackets
        if text.startswith('[') and text.endswith(']'):
            text = text[1:-1]
        text = convert_bbcode(text)
        text = escape_renpy_text(text)
        return f'{indent}narrator "{{i}}{text}{{/i}}"'

    def format_monologue(self, text, indent="    "):
        """Format internal monologue (parenthesized) as narrator."""
        # Strip outer parens
        if text.startswith('(') and text.endswith(')'):
            text = text[1:-1]
        text = convert_bbcode(text)
        text = escape_renpy_text(text)
        return f'{indent}narrator "{text}"'

    def format_bee_protocol(self, text, indent="    "):
        """Format BEE/SHARD protocol as styled text."""
        text = convert_bbcode(text)
        text = escape_renpy_text(text)
        # Show as amber styled text (protocol messages)
        return f'{indent}narrator "{{{{color=#f1c40f}}}}{text}{{{{/color}}}}"'

    def format_ai_citizen_log(self, text, indent="    "):
        """Format AI citizen log (<WAFFLE.BAT//>, <BUBBLES//>, etc.) as styled text."""
        text = convert_bbcode(text)
        text = escape_renpy_text(text)
        # Show as green styled text (AI citizen logs)
        return f'{indent}narrator "{{{{color=#43d4a8}}}}{text}{{{{/color}}}}"'

    def format_blockquote(self, lines, indent="    "):
        """Format a blockquote block as styled narrator text."""
        # Strip > prefix and join
        clean_lines = []
        for line in lines:
            stripped = line.lstrip('> ').strip()
            if stripped:
                stripped = convert_bbcode(stripped)
                stripped = escape_renpy_text(stripped)
                clean_lines.append(stripped)
        if not clean_lines:
            return ""
        text = "\\n".join(clean_lines)
        return f'{indent}narrator "{{{{color=#808090}}}}{text}{{{{/color}}}}"'

    def convert_file(self, filepath):
        """Convert a single prose .md file to .rpy content."""
        scene_id = get_scene_id(filepath)
        self.all_scene_ids.append(scene_id)

        with open(filepath, 'r', encoding='utf-8') as f:
            raw_lines = f.readlines()

        lines = [l.rstrip('\n').lstrip('\ufeff') for l in raw_lines]

        output = []
        output.append(f"## Generated from {Path(filepath).name} by convert_prose.py")
        output.append(f"## Do not edit manually — re-run converter after prose changes")
        output.append("")

        # Check if there are coda sections
        coda_indices = [i for i, l in enumerate(lines) if is_coda_header(l)]

        # Main scene label
        output.append(f"label {scene_id}:")

        # Convert main content (up to first coda, or all if no codas)
        end_idx = coda_indices[0] if coda_indices else len(lines)
        main_output = self._convert_block(lines[:end_idx], indent="    ")
        output.extend(main_output)

        # If there are codas, jump to them in sequence then return
        if coda_indices:
            for ci, coda_idx in enumerate(coda_indices):
                coda_end = coda_indices[ci + 1] if ci + 1 < len(coda_indices) else len(lines)
                coda_header = lines[coda_idx]
                coda_label = f"{scene_id}_coda_{ci}"

                # Parse coda name from header
                coda_match = re.match(r'## Coda\s*[-–—]\s*(.+)', coda_header)
                coda_title = coda_match.group(1).strip() if coda_match else f"Coda {ci}"

                output.append("")
                output.append(f"    # Coda: {coda_title}")
                output.append(f"    call {coda_label}")

            output.append("    return")
            output.append("")

            # Now emit each coda as its own label
            for ci, coda_idx in enumerate(coda_indices):
                coda_end = coda_indices[ci + 1] if ci + 1 < len(coda_indices) else len(lines)
                coda_header = lines[coda_idx]
                coda_label = f"{scene_id}_coda_{ci}"

                coda_match = re.match(r'## Coda\s*[-–—]\s*(.+)', coda_header)
                coda_title = coda_match.group(1).strip() if coda_match else f"Coda {ci}"

                output.append(f"label {coda_label}:")
                output.append(f'    narrator "{{i}}— {escape_renpy_text(coda_title)} —{{/i}}"')
                output.append("    pause 0.5")
                coda_output = self._convert_block(lines[coda_idx + 1:coda_end], indent="    ")
                output.extend(coda_output)
                output.append("    return")
                output.append("")
        else:
            output.append("    return")
            output.append("")

        self.scene_count += 1
        return '\n'.join(output)

    def _convert_block(self, lines, indent="    "):
        """Convert a block of prose lines to Ren'Py statements."""
        output = []
        i = 0
        scene_break_count = 0
        in_blockquote = False
        blockquote_lines = []
        skip_metadata = False

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Skip chapter headers (the label handles this)
            if is_chapter_header(line):
                i += 1
                continue

            # Scene metadata blocks — skip (already captured in scene_id)
            if is_scene_metadata(line):
                # Skip the whole metadata block
                while i < len(lines) and lines[i].strip().startswith('>'):
                    i += 1
                continue

            # Flush blockquote if we leave it
            if in_blockquote and not is_blockquote(line):
                bq = self.format_blockquote(blockquote_lines, indent)
                if bq:
                    output.append(bq)
                blockquote_lines = []
                in_blockquote = False

            # Blockquote accumulation
            if is_blockquote(line):
                if not in_blockquote:
                    in_blockquote = True
                    blockquote_lines = []
                blockquote_lines.append(line)
                i += 1
                continue

            # Scene break
            if is_scene_break(line):
                scene_break_count += 1
                if scene_break_count == 1:
                    # First scene break after header is just the opening
                    output.append(f"{indent}pause 0.3")
                else:
                    output.append("")
                    output.append(f"{indent}scene black with dissolve")
                    output.append(f"{indent}pause 0.5")
                    output.append(f"{indent}scene bg ship_interior with dissolve")
                i += 1
                continue

            # BEE/SHARD protocol
            if is_bee_protocol(line):
                output.append(self.format_bee_protocol(line, indent))
                self.line_count += 1
                i += 1
                continue

            # AI citizen log (<WAFFLE.BAT//>, <BUBBLES//>, <CINNAMON.EXE//>, etc.)
            if is_ai_citizen_log(line):
                output.append(self.format_ai_citizen_log(line, indent))
                self.line_count += 1
                i += 1
                continue

            # Dialogue
            dialogue = is_dialogue_line(line)
            if dialogue:
                speaker_name, text = dialogue
                speaker_var = self.resolve_speaker(speaker_name)
                direction, remaining = parse_stage_direction(text)
                output.append(self.format_dialogue(speaker_var, direction, remaining, indent))
                self.line_count += 1
                i += 1
                continue

            # Bracketed narration
            if is_narration_bracket(line):
                output.append(self.format_narration(line, indent))
                self.line_count += 1
                i += 1
                continue

            # Internal monologue
            if is_internal_monologue(line):
                output.append(self.format_monologue(line, indent))
                self.line_count += 1
                i += 1
                continue

            # Anything else — treat as narration
            if line and not line.startswith('#'):
                text = convert_bbcode(line)
                text = escape_renpy_text(text)
                output.append(f'{indent}narrator "{{i}}{text}{{/i}}"')
                self.line_count += 1

            i += 1

        # Flush any remaining blockquote
        if in_blockquote and blockquote_lines:
            bq = self.format_blockquote(blockquote_lines, indent)
            if bq:
                output.append(bq)

        return output


def generate_manifest(scene_ids, output_dir):
    """Generate a manifest file listing all scene IDs for chapter_flow integration."""
    manifest_path = os.path.join(output_dir, '_manifest.txt')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write("# Prose scene manifest — generated by convert_prose.py\n")
        f.write("# One scene ID per line, in file order\n")
        f.write(f"# Total: {len(scene_ids)} scenes\n\n")
        for sid in sorted(scene_ids):
            f.write(f"{sid}\n")
    return manifest_path


def generate_new_characters(output_path, new_chars):
    """Generate a supplemental characters file for speakers found in prose."""
    if not new_chars:
        return
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("## prose_characters.rpy — Additional character definitions from prose files\n")
        f.write("## Generated by convert_prose.py — re-run converter to update\n\n")
        for var_name in sorted(new_chars.keys()):
            display_name = new_chars[var_name]
            f.write(f'define {var_name} = Character("{display_name}", '
                    f'color="#888888", what_prefix="\\"", what_suffix="\\"")\n')


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)

    default_input = os.path.join(base_dir, "prose")
    default_output = os.path.join(base_dir, "starforge-renpy", "game", "prose_scenes")

    # Parse args
    input_dir = default_input
    output_dir = default_output
    target_acts = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--act':
            target_acts = []
            i += 1
            while i < len(args) and not args[i].startswith('-'):
                target_acts.append(int(args[i]))
                i += 1
        elif args[i] == '--output' or args[i] == '-o':
            i += 1
            output_dir = args[i]
            i += 1
        elif not args[i].startswith('-'):
            if input_dir == default_input:
                input_dir = args[i]
            else:
                output_dir = args[i]
            i += 1
        else:
            i += 1

    if not os.path.isdir(input_dir):
        print(f"ERROR: Input directory not found: {input_dir}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Find act directories
    act_dirs = []
    for entry in sorted(os.listdir(input_dir)):
        act_path = os.path.join(input_dir, entry)
        if os.path.isdir(act_path) and entry.startswith('act'):
            act_num_match = re.match(r'act(\d+)', entry)
            if act_num_match:
                act_num = int(act_num_match.group(1))
                if target_acts is None or act_num in target_acts:
                    act_dirs.append((act_num, entry, act_path))

    if not act_dirs:
        print(f"No act directories found in {input_dir}")
        sys.exit(1)

    converter = ProseConverter()
    total_files = 0
    skipped = 0

    for act_num, act_name, act_path in act_dirs:
        # Create output subdirectory per act
        act_output = os.path.join(output_dir, act_name)
        os.makedirs(act_output, exist_ok=True)

        # Find all .md files (skip combined files)
        md_files = sorted([
            f for f in os.listdir(act_path)
            if f.endswith('.md') and not f.endswith('_combined.md')
        ])

        print(f"\n{'='*60}")
        print(f"Act {act_num}: {len(md_files)} prose files")
        print(f"{'='*60}")

        for md_file in md_files:
            md_path = os.path.join(act_path, md_file)
            scene_id = get_scene_id(md_path)

            # Convert
            try:
                rpy_content = converter.convert_file(md_path)
            except Exception as e:
                print(f"  ERROR: {md_file}: {e}")
                skipped += 1
                continue

            # Write .rpy file
            rpy_path = os.path.join(act_output, scene_id + '.rpy')
            with open(rpy_path, 'w', encoding='utf-8') as f:
                f.write(rpy_content)

            total_files += 1
            print(f"  OK {md_file} -> {scene_id}.rpy")

    # Generate manifest
    manifest_path = generate_manifest(converter.all_scene_ids, output_dir)

    # Generate supplemental characters
    chars_path = os.path.join(os.path.dirname(output_dir), 'prose_characters.rpy')
    generate_new_characters(chars_path, NEW_CHARACTERS)

    print(f"\n{'='*60}")
    print(f"CONVERSION COMPLETE")
    print(f"{'='*60}")
    print(f"  Files converted: {total_files}")
    print(f"  Files skipped:   {skipped}")
    print(f"  Scenes:          {converter.scene_count}")
    print(f"  Lines:           {converter.line_count}")
    print(f"  Manifest:        {manifest_path}")
    if converter.unknown_speakers:
        print(f"\n  New speakers found ({len(converter.unknown_speakers)}):")
        for s in sorted(converter.unknown_speakers):
            print(f"    - {s}")
        print(f"  Characters file:  {chars_path}")


if __name__ == '__main__':
    main()
