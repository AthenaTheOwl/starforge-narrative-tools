#!/usr/bin/env python3
"""convert_combat.py — Generate skeleton narrative combat .rpy files from encounter + enemy JSON.

Usage:
    python convert_combat.py [encounter_dir] [enemy_dir] [output_dir]

Generates one .rpy file per encounter with:
- NarrativeCombat setup
- Menu choices derived from party abilities
- Enemy response rounds
- Victory/defeat branches
"""

import json
import os
import sys


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_combat_rpy(encounter_data, enemy_datas, encounter_id):
    """Generate a narrative combat .rpy file."""
    lines = []
    name = encounter_data.get("name", encounter_id)
    desc = encounter_data.get("description", "")
    rewards = encounter_data.get("rewards", {})
    xp = rewards.get("experience", 0)
    reward_flags = rewards.get("flags", [])

    # Collect enemy info
    all_enemies = []
    for wave in encounter_data.get("waves", []):
        for entry in wave.get("enemies", []):
            etype = entry.get("type", "")
            count = entry.get("count", 1)
            edata = enemy_datas.get(etype, {})
            ename = edata.get("name", etype)
            all_enemies.append({"type": etype, "count": count, "name": ename, "data": edata})

    enemy_summary = ", ".join(
        "{0}x {1}".format(e["count"], e["name"]) for e in all_enemies
    )

    lines.append(f"## combat_{encounter_id}.rpy — Narrative combat: {name}")
    lines.append(f"## Enemies: {enemy_summary}")
    lines.append(f"## Auto-generated skeleton — add flavor text")
    lines.append("")
    lines.append(f"label combat_{encounter_id}:")
    lines.append(f'    $ _nc = NarrativeCombat("{encounter_id}")')
    lines.append(f"    show screen combat_hud(_nc)")
    lines.append("")
    lines.append(f'    "{desc}" if "{desc}" else "Combat begins."')
    lines.append("")

    # Generate combat rounds
    max_rounds = 5  # skeleton generates up to 5 rounds
    for rnd in range(1, max_rounds + 1):
        lines.append(f"label .round_{rnd}:")
        lines.append(f"    $ _nc.advance_round()")
        lines.append("")

        # Player action menu
        lines.append("    menu:")
        lines.append('        "Choose your action:"')
        lines.append("")

        # Generate a few tactical options
        lines.append('        "Strike the nearest enemy [Attack vs DC 12]":')
        lines.append('            $ _enemies = _nc.get_living_enemy_keys()')
        lines.append('            if _enemies:')
        lines.append('                $ _target = _enemies[0]')
        lines.append('                $ _result = _nc.resolve_attack("avyanna", "strike", _target)')
        lines.append('                call screen dice_roll_screen')
        lines.append('                if _result["hit"]:')
        lines.append('                    "{i}The strike connects. [_result[\'damage\']] damage.{/i}"')
        lines.append('                else:')
        lines.append('                    "{i}The strike misses. The enemy sidesteps.{/i}"')
        lines.append("")

        lines.append('        "Hold position and assess [No roll — safe option]":')
        lines.append('            "{i}You hold back, watching for an opening.{/i}"')
        lines.append("")

        lines.append('        "Coordinate the crew [Tactics vs DC 14]":')
        lines.append('            $ _sc = skill_check("tactics", 14, "avyanna")')
        lines.append('            if _sc == "SUCCESS" or _sc == "CRITICAL_SUCCESS":')
        lines.append('                "{i}The crew moves as one. Coordinated fire drops an enemy.{/i}"')
        lines.append('                $ _enemies = _nc.get_living_enemy_keys()')
        lines.append('                if _enemies:')
        lines.append('                    $ _nc.enemy_hp[_enemies[0]] = max(0, _nc.enemy_hp[_enemies[0]] - 15)')
        lines.append('            else:')
        lines.append('                "{i}The coordination falters. The enemy exploits the gap.{/i}"')
        lines.append("")

        # Enemy response
        lines.append("    ## Enemy response")
        lines.append("    $ _threat = _nc.enemy_threatens()")
        lines.append('    if _threat["damage"] > 0:')
        lines.append('        "{i}[_threat[\'narrative\']] [_threat[\'damage\']] damage to [_threat[\'target_name\']].{/i}"')
        lines.append("")

        # Check combat end
        lines.append("    if _nc.is_combat_over():")
        lines.append("        jump .combat_end")
        lines.append("")

        # Next round or loop back
        if rnd < max_rounds:
            lines.append(f"    jump .round_{rnd + 1}")
        else:
            lines.append("    ## Extended combat — loop back")
            lines.append(f"    jump .round_{max_rounds}")
        lines.append("")

    # Victory / Defeat
    lines.append("label .combat_end:")
    lines.append("    hide screen combat_hud")
    lines.append("")
    lines.append("    if _nc.victory:")
    lines.append(f'        $ game_state.mark_encounter_cleared("{encounter_id}")')
    if xp:
        lines.append(f"        $ party_manager.award_xp({xp})")
    for flag in reward_flags:
        lines.append(f'        $ game_state.set_flag("{flag}")')
    lines.append('        "{i}Victory. The threat is neutralized.{/i}"')
    lines.append("        $ persistent.combat_victories = (persistent.combat_victories or 0) + 1")
    lines.append("    else:")
    lines.append("        ## Failure is interesting — not game over")
    lines.append(f'        $ game_state.set_flag("{encounter_id}_lost")')
    lines.append('        "{i}Everything goes dark. Someone drags you to cover.{/i}"')
    lines.append("        $ persistent.combat_defeats = (persistent.combat_defeats or 0) + 1")
    lines.append("")
    lines.append("    return")
    lines.append("")

    return "\n".join(lines)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)

    if len(sys.argv) >= 4:
        enc_dir = sys.argv[1]
        enemy_dir = sys.argv[2]
        output_dir = sys.argv[3]
    else:
        enc_dir = os.path.join(base_dir, "starforge-rpg", "data", "encounters")
        enemy_dir = os.path.join(base_dir, "starforge-rpg", "data", "enemies")
        output_dir = os.path.join(base_dir, "starforge-renpy", "game", "combat")

    if not os.path.isdir(enc_dir):
        print(f"ERROR: Encounter directory not found: {enc_dir}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Load all enemy definitions
    enemy_datas = {}
    if os.path.isdir(enemy_dir):
        for f in os.listdir(enemy_dir):
            if f.endswith(".json"):
                eid = f.replace(".json", "")
                enemy_datas[eid] = load_json(os.path.join(enemy_dir, f))

    # Convert encounters
    total = 0
    for filename in sorted(os.listdir(enc_dir)):
        if not filename.endswith(".json"):
            continue
        encounter_id = filename.replace(".json", "")
        enc_data = load_json(os.path.join(enc_dir, filename))

        rpy_content = generate_combat_rpy(enc_data, enemy_datas, encounter_id)
        output_path = os.path.join(output_dir, f"combat_{encounter_id}.rpy")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rpy_content)

        total += 1
        print(f"  {encounter_id}")

    print(f"\nGenerated {total} combat scene skeletons")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
