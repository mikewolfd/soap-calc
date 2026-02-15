---
name: Inventory Management
description: Process user oil and additive inventory lists, cross-reference against the soap-calc databases, and save a validated inventory.md for use by other skills.
---

# Inventory Management Skill

## Purpose
When a user tells you what oils, butters, fats, and/or additives they have on hand, parse their input, validate each item against the project databases, and save a structured `inventory.md` file at the project root.

Other skills (like Soap Formulation) can optionally read this file to constrain recommendations — but **only when the user explicitly asks**.

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

### 2. Save `inventory.md`

Write (or update) the file at **`/Users/mikewolfd/Work/soap-calc/inventory.md`**.

Use this exact format:

```markdown
# Soap Making Inventory

> Last updated: YYYY-MM-DD

## Oils

| Oil | SAP (NaOH) | SAP (KOH) | Iodine | INS |
|-----|------------|------------|--------|-----|
| Olive Oil | 0.134 | 0.188 | 85.0 | 103.0 |
| Coconut Oil, 76 deg | 0.183 | 0.257 | 10.0 | 258.0 |

## Additives

| Additive | Category | Usage | Stage | Purpose |
|----------|----------|-------|-------|---------|
| Sodium Lactate | hardener | 1 tsp/lb oils | lye | Adds hardness; speeds unmolding |

## Unverified Items

- Custom Oil X *(not in database — add to `~/.soap_calc/oils.json` for lye calculations)*
```

**Rules:**
- Oil names **must use the exact database name** (canonical spelling) so other skills can match them.
- The "Usage" column for additives should be formatted as `<min>–<max> <unit>/<per>` (e.g., `1–3 tsp/lb oils`). If min equals max, show just one value.
- If there are no items in a section, include the header but write "*(none)*" instead of the table.
- If there are no unverified items, omit the "Unverified Items" section entirely.

### 3. Handle Updates

When the user asks to **add** items:
- Read the existing `inventory.md`, add the new validated items, and rewrite the file.

When the user asks to **remove** items:
- Read the existing `inventory.md`, remove the specified items, and rewrite the file.

When the user asks to **show** their inventory:
- Read and display the contents of `inventory.md`.

When the user asks to **clear** their inventory:
- Delete or overwrite `inventory.md` with empty sections.

### 4. Confirm With the User

After saving, briefly summarize what was added:
- Number of oils matched
- Number of additives matched
- Any items that were ambiguous or unverified
- Remind the user that other skills will only use this inventory when explicitly asked (e.g., "formulate a recipe from my inventory")

## Important Notes

- **This skill only manages the inventory file.** It does not formulate recipes or run calculations.
- **Inventory is opt-in for other skills.** The `inventory.md` file exists as a reference. Other skills must be explicitly told to use it (e.g., "use my inventory", "make a recipe with what I have").
- **Oil names are safety-critical.** Always resolve to exact database names. A wrong oil name means wrong SAP values, which means potentially unsafe lye amounts.
