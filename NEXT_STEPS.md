# Starforge Canticles RPG - Next Steps & Testing

## Current Status ✅

**Phase 2 Complete** - 5 major systems implemented:
- ✅ Combat System (damage, status effects, enemy AI)
- ✅ Dialogue System (branching, portraits, skill checks)
- ✅ Stats & Powers (abilities, loadouts)
- ✅ Party Management (equipment, inventory)
- ✅ Act 1 Content (location graph, dialogue from prose)

**Location:** `~/starforge/starforge-rpg/`

---

## Immediate Next Steps

### 1. Commit Current Work
```bash
cd ~/starforge/starforge-rpg
git add -A
git commit -m "Phase 2: Combat, dialogue, stats, party, and Act 1 content

- Combat: Full damage calculator with defense matrix
- Combat: Status effects system (control, DoT, buffs)
- Combat: Enemy AI with squad tactics
- Dialogue: 5 Act 1 conversations from prose
- Dialogue: Portrait display and branching engine
- Stats: Ability system with 6-slot loadouts
- Party: Equipment panel and inventory management
- Act 1: Location graph with 4+ locations
- Act 1: Quest JSON for lumen thief arc

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### 2. Set Up Testing Infrastructure

**Create test framework for Godot:**
- Install GUT (Godot Unit Test) addon
- Set up test directory structure: `tests/unit/`, `tests/integration/`
- Create test runner scene
- Add CI/CD config for automated testing

**Priority test files to create:**
1. `tests/unit/test_damage_calculator.gd` - Combat math verification
2. `tests/unit/test_status_effects.gd` - Status effect lifecycle
3. `tests/unit/test_dialogue_manager.gd` - Dialogue tree traversal
4. `tests/integration/test_combat_flow.gd` - Full combat encounter
5. `tests/integration/test_party_management.gd` - Equipment and loadouts

### 3. Integration & Polish

**Combat Integration:**
- Connect damage calculator to battle UI
- Implement turn order display
- Add status effect visual indicators
- Hook enemy AI to battle controller
- Test with real enemy encounters

**Dialogue Integration:**
- Connect dialogue trees to exploration controller
- Implement portrait rendering
- Add dialogue history/log
- Test skill check branching
- Verify dialogue flags persist

**Party UI Integration:**
- Wire party screen to PartyManager autoload
- Connect equipment panels to character data
- Implement drag-drop for ability slots
- Test relic weapon inlay system

**Act 1 Flow:**
- Connect location graph to exploration scene
- Ensure quest JSON loads correctly
- Test location transitions
- Verify dialogue triggers at story points

### 4. Visual Polish & UI Theme

**Dark Sci-Fi Theme Implementation:**
- Create theme resource at `resources/themes/main_theme.tres`
- Colors: Background #0a0a14, Text #c0c0d0, Accent #4060a0, Danger #a04040
- Apply to all UI scenes (title, exploration, battle, dialogue, party)
- Add hover effects and button states
- Style HP/shield bars with color gradients

**Combat UI Enhancements:**
- Character portraits in battle
- Turn order indicator
- Status effect icons
- Damage numbers animation
- Target selection highlight

**Exploration UI:**
- Location name overlay
- Quest objectives tracker
- Party status summary (HP, Heat)

---

## Phase 3: Content & Features

### PRIMARY FOCUS: PLOT/STORY CONTENT ⭐

**See ~/starforge/REFERENCES.md for open-source Godot game references**

### Content Creation (TOP PRIORITY)
1. **Remaining Act 1 Dialogues** - Extract from `~/starforge/prose/act1/`:
   - Character recruitment scenes (Elisira, Vesper, Jalen, Nyx, Rho)
   - First mentor contact
   - Bee's manifestation moment
   - Key story revelations
   - Crew bonding scenes (meals, watches, personal moments)
   - **Reference:** Dialogic, Rakugo for dialogue patterns

2. **Enemy Encounters** - Create encounter JSON for:
   - Corporate (troopers, commanders, drones)
   - Raiders (scrappers, veterans, demo)
   - Cult (acolytes, binders, hierophant)
   - Husks (shards, shells, echoes)

3. **Abilities & Equipment** - Data files for:
   - All character abilities (per `~/starforge/spec/`)
   - Starting equipment sets
   - Act 1 findable items
   - Relic weapon progression

### New Features
1. **Save/Load System**
   - Serialize party state, quest progress, dialogue flags
   - Implement save slots UI
   - Auto-save on major events

2. **Combat Enhancements**
   - Tactical positioning (hex grid)
   - Environmental effects
   - Cover system
   - Multi-target abilities

3. **Progression Systems**
   - Experience and leveling
   - Ability unlock tree
   - Relic weapon inlays (story-gated)

4. **Audio**
   - Background music system
   - Combat sound effects
   - Dialogue voice lines (optional)

---

## Testing Checklist

### Unit Tests
- [ ] Damage calculation formulas
- [ ] Heat penalty curve
- [ ] Defense matrix interactions
- [ ] Status effect durations
- [ ] Armor degradation
- [ ] Shield regeneration
- [ ] Dialogue branching logic
- [ ] Skill check thresholds
- [ ] Equipment stat bonuses
- [ ] Ability heat costs

### Integration Tests
- [ ] Full combat encounter (player vs 3 enemies)
- [ ] Status effects persist across turns
- [ ] Enemy AI makes valid moves
- [ ] Dialogue choices affect flags
- [ ] Party screen updates on equipment change
- [ ] Location transitions work
- [ ] Quest triggers fire correctly

### Gameplay Tests
- [ ] Play through Act 1 opening (Site K9 → West Corridor)
- [ ] Test all 5 recruited characters in combat
- [ ] Verify dialogue skill checks work
- [ ] Equip items and see stat changes
- [ ] Trigger all 5 new dialogue scenes
- [ ] Defeat each enemy type

---

## Technical Debt & Refactoring

### Code Quality
- Add type hints to all functions
- Document complex algorithms (especially damage calc)
- Refactor large functions (>50 lines)
- Remove debug print statements
- Add error handling for missing data files

### Performance
- Profile combat calculations
- Optimize dialogue tree lookups
- Cache frequently accessed data
- Reduce scene reload times

### Architecture
- Standardize event bus patterns
- Consolidate data loading (use ResourceLoader)
- Create data schemas for JSON validation
- Add logging system for debugging

---

## Documentation Needed

1. **Dev Docs:**
   - Combat system overview (how damage flows)
   - Dialogue format specification
   - Enemy AI behavior tags
   - Data file schemas (JSON structure)

2. **Player Docs:**
   - Character abilities reference
   - Combat mechanics guide
   - Status effects glossary
   - Story/lore primer

---

## GitHub Setup

```bash
cd ~/starforge/starforge-rpg
gh repo create starforge-canticles-rpg --private --source=. --remote=origin --push

# Or manually:
git remote add origin https://github.com/AthenaTheOwl/starforge-canticles-rpg.git
git push -u origin master
```

---

## Gastown Agent Tasks

**Assign these as new beads:**

1. **Testing Setup** - Install GUT, create test structure, write 5 priority unit tests
2. **Combat Integration** - Wire damage calculator and AI to battle UI, add visual feedback
3. **Dialogue Integration** - Connect dialogue trees to exploration, implement portraits
4. **UI Theme** - Create dark sci-fi theme resource and apply to all scenes
5. **Act 1 Polish** - Extract remaining dialogues from prose, create enemy encounters
6. **Save System** - Implement save/load with serialization and UI

**Lower priority:**
7. Audio system
8. Tactical hex combat
9. Progression/leveling
10. Performance optimization

---

## Success Criteria for Phase 3

- ✅ All tests pass
- ✅ Can play Act 1 from start to first quest completion
- ✅ All 5 party members recruited and usable
- ✅ Combat feels complete (animations, feedback, AI works)
- ✅ Dialogue flows naturally with proper portraits
- ✅ UI is cohesive with dark sci-fi aesthetic
- ✅ Can save/load game state
- ✅ Code is documented and tested

---

**Next command for Mayor:**

"Read ~/starforge/NEXT_STEPS.md and create beads for the Phase 3 tasks. Start with Testing Setup, Combat Integration, and Dialogue Integration as priority 1."
