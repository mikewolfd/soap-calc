---
name: inventory
description: >
  Manage the user's soap-making supply inventory (oils, butters, fats, additives). Cross-references
  items against the soap-calc oil and additive JSON databases and saves a validated inventory.md
  file. Use when the user: (1) lists oils or additives they have on hand, (2) asks to add or remove
  items from their inventory, (3) asks to show, update, or clear their inventory, or (4) says things
  like "here's what I have" or "add castor oil to my inventory." Do NOT use for recipe formulation
  or lye calculations — use the soap-formulation skill for those.
compatibility: Requires soap-calc Python package (pip install -e .)
metadata:
  version: 1.0.0
---

# Inventory Management Skill

## Purpose
When a user tells you what oils, butters, fats, and/or additives they have on hand, parse their input, validate each item against the project databases, and save a structured `inventory.md` file.

Other skills (like Soap Formulation) can optionally read this file to constrain recommendations — but **only when the user explicitly asks**.

## Inventory File Locations

The skill uses a **hybrid approach** with priority:

1. **`./inventory.md`** (current directory) — project-specific inventory
2. **`~/.soap_calc/inventory.md`** (user home) — global user inventory

**Reading:** Checks current directory first, then falls back to user default.

**Writing:** When creating a new inventory or if the user asks to "save" without specifying, ask which location to use:
- **Current directory** — for project-specific supplies (e.g., "vacation cabin soap", "gift batch ingredients")
- **User default** — for your main inventory that follows you across all projects

**Updating/Removing:** Modify whichever file currently exists. If both exist, modify the current directory one (higher priority).

## Workflow

### 1. Cross-Reference Each Item

For every item the user mentions:

1. **Check oils first** — use `soap-calc list-oils "{name}"` or the Python API `search_oils(query)` to fuzzy-match against `data/oils.json`.
2. **Check additives second** — read `data/additives.json` and match by name (case-insensitive substring).
3. **Classify the result**:
   - ✅ **Exact or unambiguous match** → add to inventory with the canonical database name.
   - ⚠️ **Ambiguous match** (e.g., "coconut oil" matches 4 variants) → ask the user which specific variant(s) they have. List the options.
   - ❌ **No match in either database** → flag as unverified. Ask the user whether to include it anyway or skip it. If included, note that it cannot be used in lye calculations until added to `~/.soap_calc/oils.json`.

### 2. Determine Save Location

**For new inventories (no existing file found):**
- Ask the user: "Save inventory to current directory (`./inventory.md`) or user default (`~/.soap_calc/inventory.md`)?"
- Most users will want user default for their main inventory

**For updates (inventory already exists):**
- Save to whichever location currently has the file
- If both exist, update the current directory one (higher priority)

### 3. Save `inventory.md`

**Always start from the template:**
1. Read the template file at `skills/inventory/assets/inventory.template.md`
2. Copy the entire contents (including frontmatter)
3. Replace the placeholder sections with actual data:
   - Update `last_updated` in both frontmatter and body to current date (YYYY-MM-DD)
   - Replace `*(none)*` in Oils section with populated table (or keep `*(none)*` if empty)
   - Replace `*(none)*` in Additives section with populated table (or keep `*(none)*` if empty)
   - Add Unverified Items section only if there are unverified items (omit entirely if none)

**Data formatting rules:**
- Oil names **must use the exact database name** (canonical spelling) so other skills can match them
- For additives, "Usage" column format: `{min}–{max} {unit}/{per}` (e.g., `1–3 tsp/lb oils`). If min equals max, show just one value
- If a section has no items, write `*(none)*` instead of the table
- Only include "Unverified Items" section if there are items to list

### 4. Handle Updates

When the user asks to **add** items:
- Find existing inventory (check `./inventory.md` first, then `~/.soap_calc/inventory.md`)
- If no inventory exists, ask where to create it (see "Determine Save Location" above)
- Add the new validated items and save

When the user asks to **remove** items:
- Find existing inventory (same priority)
- Remove the specified items and save
- If inventory becomes empty, ask if they want to delete the file

When the user asks to **show** their inventory:
- Find existing inventory (same priority)
- Display the contents
- If no inventory found, say "No inventory found. Would you like to create one?"

When the user asks to **clear** their inventory:
- Find existing inventory (same priority)
- Delete the file or overwrite with empty sections
- Confirm which file was cleared

### 5. Confirm With the User

After saving, briefly summarize:
- Number of oils matched
- Number of additives matched
- Any items that were ambiguous or unverified
- **Location where the inventory was saved** (important for user awareness)
- Remind the user that other skills will only use this inventory when explicitly asked (e.g., "formulate a recipe from my inventory")

## Examples

### Example 1: "I have olive oil, coconut oil, shea butter, and sodium lactate"

1. Run `soap-calc list-oils "olive"` → exact match: "Olive Oil". Add to oils table.
2. Run `soap-calc list-oils "coconut"` → multiple matches: "Coconut Oil (76°)", "Coconut Oil (92°)", "Coconut Oil, Fractionated". Ask the user which variant(s).
3. Run `soap-calc list-oils "shea"` → exact match: "Shea Butter". Add to oils table.
4. Check `data/additives.json` for "sodium lactate" → match found with usage `1–3 tsp/lb oils`, stage "Lye Liquid". Add to additives table.
5. No existing inventory found → ask save location.
6. Read `assets/inventory.template.md`, populate tables with matched items, write to chosen location.
7. Confirm: "Saved 3 oils, 1 additive. 1 oil needs clarification (coconut — which variant?)."

### Example 2: "Add castor oil to my inventory"

1. Find existing inventory: check `./inventory.md` first, then `~/.soap_calc/inventory.md`.
2. Run `soap-calc list-oils "castor"` → exact match: "Castor Oil".
3. Read existing inventory, append "Castor Oil" row to the oils table with SAP/iodine/INS values from the database.
4. Save to the same file location.
5. Confirm: "Added Castor Oil to your inventory at ./inventory.md."

### Example 3: "Here's what I have: argan oil, beeswax, vitamin E, dragon fruit extract"

1. Run `soap-calc list-oils "argan"` → match: "Argan Oil". Add to oils.
2. Run `soap-calc list-oils "beeswax"` → match: "Beeswax". Add to oils.
3. Check `data/additives.json` for "vitamin E" → match found. Add to additives.
4. Check both databases for "dragon fruit extract" → no match. Flag as unverified. Ask: "Dragon fruit extract is not in the oil or additive database. Include it as unverified (it won't be usable for lye calculations), or skip it?"
5. Save inventory with matched items plus any user-confirmed unverified items.

## Error Handling

- **`soap-calc` not installed**: Tell the user to run `pip install -e .` from the project root. Do not attempt to read `data/oils.json` directly as a fallback — the CLI provides fuzzy matching that raw JSON lookups don't.
- **Database files missing** (`data/oils.json`, `data/additives.json`): Likely means the user is outside the project directory or the package isn't installed. Ask the user to confirm they're in the soap-calc project root.
- **Write permission denied**: Suggest saving to the other location (e.g., if `~/.soap_calc/` fails, try `./inventory.md`, or vice versa).
- **All items unverified**: Warn the user that an inventory with only unverified items cannot be used for safe lye calculations. Suggest checking oil names with `soap-calc list-oils`.

## Important Notes

- **This skill only manages the inventory file.** It does not formulate recipes or run calculations.
- **Inventory is opt-in for other skills.** The `inventory.md` file exists as a reference. Other skills must be explicitly told to use it (e.g., "use my inventory", "make a recipe with what I have").
- **Oil names are safety-critical.** Always resolve to exact database names. A wrong oil name means wrong SAP values, which means potentially unsafe lye amounts.
