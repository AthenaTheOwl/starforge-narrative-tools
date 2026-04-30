# Open Source Godot Game References

## Primary References for Implementation Patterns

### 1. Haldric-Next (Turn-Based Tactics)
**URL:** https://github.com/Byteron/haldric-next
**Relevant for:**
- Hex grid implementation
- Turn-based combat flow
- Unit movement and positioning
- Tactical combat UI
- Map/terrain system

**Key files to reference:**
- Hex coordinate systems
- Combat resolution
- Unit actions and abilities
- UI for tactical combat

### 2. Dialogic (Dialogue System)
**URL:** https://github.com/dialogic-godot/dialogic
**Relevant for:**
- Dialogue tree structure
- Branching conversations
- Character portraits
- Dialogue variables/flags
- Timeline system

**Use for:** Dialogue manager implementation, conversation flow

### 3. Rakugo (Visual Novel Framework)
**URL:** https://github.com/rakugoteam/Rakugo
**Relevant for:**
- Narrative-focused game structure
- Save/load for story state
- Character system
- Story progression tracking

**Use for:** Story state management, character progression

### 4. Godot JRPG Template
**URL:** https://github.com/Crystal-Bit/godot-game-template
**Relevant for:**
- Menu systems (party, inventory, equipment)
- Turn-based RPG combat
- Scene transitions
- Save system
- UI organization

### 5. Godot Action RPG Tutorial
**URL:** https://github.com/uheartbeast/Heart-Platformer
**Relevant for:**
- Stats system
- Health/resource bars
- Damage numbers
- Visual feedback
- UI polish

---

## Additional Useful Projects

### Story/Narrative Focus
- **Inkle's Ink** (Godot plugin) - Narrative scripting
- **Godot Visual Novel Engine** - Story-driven mechanics

### Combat Systems
- **Godot Tactical RPG** - Grid-based combat
- **Crystal Bit JRPG** - Party-based combat

### UI/UX
- **Godot UI Examples** - Professional UI patterns
- **Kenney's UI Assets** - Free UI sprites

---

## Implementation Strategy

### When Using References:
1. **Study the pattern, don't copy-paste** - Understand the architecture
2. **Adapt to Starforge's needs** - We have unique mechanics (Heat, Lattice, etc.)
3. **Cite in comments** - Add `# Based on: [project]` in code
4. **Maintain our style** - Keep the gothic-noir, dark sci-fi aesthetic

### Priority Order:
1. **Plot/Story** - Dialogue extraction from prose (PRIMARY FOCUS)
2. **Narrative systems** - Dialogue manager, quest tracking
3. **Combat** - Reference Haldric for tactical hex combat
4. **UI** - Reference JRPG template for party/inventory screens
5. **Polish** - Visual feedback, animations

---

## Plot Development Focus

### What "Plot Focus" Means:
- Story content is the MAIN product
- Combat and systems serve the narrative
- Dialogue quality > mechanical complexity
- Character moments > optimization
- Player choices affect story more than stats

### Plot Implementation Priority:

**Phase 3A: Story Content (TOP PRIORITY)**
1. Extract ALL Act 1 dialogues from `~/starforge/prose/act1/`
2. Character recruitment scenes (Elia ✅, need: Elisira, Vesper, Jalen, Nyx, Rho)
3. Key story moments:
   - First mentor contact
   - Bee's first manifestation
   - Crew bonding scenes (meals, watches)
   - Revelations about the Lattice
   - Each character's personal arc setup

4. Dialogue branches based on:
   - Player dialogue choices
   - Character relationships
   - Previous story flags
   - Skill checks (Avyanna's persuasion, Jalen's tech knowledge, etc.)

**Phase 3B: Narrative Systems**
1. Character relationship tracker
2. Story flag system (decisions persist)
3. Dialogue history/journal
4. Quest log with story context
5. Character codex (learn about crew over time)

**Phase 3C: Plot-Driven Mechanics**
1. Combat encounters tied to story beats
2. Environmental storytelling in locations
3. Items with lore descriptions
4. Abilities that reflect character personality
5. Music/ambiance matching story tone

---

## Dialogue Extraction Guide

### Source Material:
- **Location:** `~/starforge/prose/act1/`
- **Format:** Novel-style prose with dialogue and narration

### Extraction Process:
1. **Read the prose chapter**
2. **Identify dialogue exchanges** - Who's speaking, what choices player has
3. **Convert to JSON format** (see existing `data/dialogue/*.json`)
4. **Preserve tone** - Keep the gothic-noir voice, dry humor, sharp subtext
5. **Add branching** - Where player can choose responses
6. **Flag important moments** - Set story flags for consequences

### JSON Dialogue Format:
```json
{
  "id": "act1_scene_name",
  "nodes": {
    "start": {
      "speaker": "Avyanna",
      "text": "Dialogue text here...",
      "choices": [
        {
          "text": "[Persuasion] Try to reason with them",
          "next": "persuasion_path",
          "skill_check": {"skill": "persuasion", "dc": 12},
          "set_flag": "tried_persuasion"
        },
        {
          "text": "Remain silent",
          "next": "silent_path"
        }
      ]
    }
  }
}
```

### Dialogue Priorities (from prose):
1. **Chapter 1-2:** Elia rescue (done), site aftermath, crew meal
2. **Chapter 3-4:** Vesper recruitment, first combat analysis
3. **Chapter 5-6:** Jalen joins, tech explanations
4. **Chapter 7-8:** Nyx encounter, tension/trust building
5. **Chapter 9-10:** Rho integration, mentor reveal setup

---

## GitHub References to Clone

Agents can reference these directly:

```bash
# Clone reference projects to ~/starforge/references/
mkdir -p ~/starforge/references
cd ~/starforge/references

git clone https://github.com/Byteron/haldric-next.git
git clone https://github.com/dialogic-godot/dialogic.git
git clone https://github.com/Crystal-Bit/godot-game-template.git

# These are read-only references for implementation patterns
```

---

## Next Mayor Instructions

Tell the Mayor:

"Read ~/starforge/REFERENCES.md. Primary focus is PLOT/STORY content extraction from prose.

Create beads for:
1. **Dialogue Extraction (P0)** - Extract ALL remaining Act 1 dialogues from ~/starforge/prose/act1/ chapters, convert to JSON format
2. **Character Recruitment (P0)** - Create recruitment scenes for Elisira, Vesper, Jalen, Nyx, Rho
3. **Story Moments (P0)** - Implement key narrative beats: mentor contact, Bee manifestation, crew bonding
4. **Narrative Systems (P1)** - Relationship tracker, story flags, dialogue journal
5. **Combat Integration (P2)** - Reference haldric-next for hex combat patterns

Use open-source Godot references for implementation patterns but maintain Starforge's unique mechanics and gothic-noir tone."
