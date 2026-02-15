---
name: Inventory Management
description: Process user oil and additive inventory lists, cross-reference against the soap-calc databases, and save a validated inventory.md for use by other skills.
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

## Trigger
Activate this skill when the user says something like:
- "I have olive oil, coconut oil, shea butter, and sodium lactate"
- "Here's what's in my soap supplies…"
- "Add castor oil to my inventory"
- "Remove palm oil from my inventory"
- "Show / update / clear my inventory"

## Workflow

### 1. Cross-Reference Each Item

For every item the user mentions:

1. **Check oils first** — use `soap-calc list-oils "<name>"` or the Python API `search_oils(query)` to fuzzy-match against `data/oils.json`.
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
1. Read the template file at `/Users/mikewolfd/Work/soap-calc/examples/inventory.template.md`
2. Copy the entire contents (including frontmatter)
3. Replace the placeholder sections with actual data:
   - Update `last_updated` in both frontmatter and body to current date (YYYY-MM-DD)
   - Replace `*(none)*` in Oils section with populated table (or keep `*(none)*` if empty)
   - Replace `*(none)*` in Additives section with populated table (or keep `*(none)*` if empty)
   - Add Unverified Items section only if there are unverified items (omit entirely if none)

**Data formatting rules:**
- Oil names **must use the exact database name** (canonical spelling) so other skills can match them
- For additives, "Usage" column format: `<min>–<max> <unit>/<per>` (e.g., `1–3 tsp/lb oils`). If min equals max, show just one value
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

## Important Notes

- **This skill only manages the inventory file.** It does not formulate recipes or run calculations.
- **Inventory is opt-in for other skills.** The `inventory.md` file exists as a reference. Other skills must be explicitly told to use it (e.g., "use my inventory", "make a recipe with what I have").
- **Oil names are safety-critical.** Always resolve to exact database names. A wrong oil name means wrong SAP values, which means potentially unsafe lye amounts.
