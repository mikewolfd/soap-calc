---
name: Soap Formulation
description: Generate soap recipes, formulation advice, troubleshooting guidance, and educational content about soap making (CP, HP, NaOH, KOH).
---

# Soap Formulation Skill

## Purpose
Generate soap recipes, formulation advice, troubleshooting guidance, and educational content about soap making. This skill covers cold process (CP), hot process (HP), bar soap (NaOH), and liquid soap (KOH) formulation.

## Before You Start
If the user's request involves **formulation, chemistry, fatty acid selection, additive choices, or troubleshooting soap behavior**, read `./soap-formulation-expert-reference.md` first. It contains condensed expert knowledge on fatty acid profiles, additive interactions, and formulation archetypes.

Skip the reference file for simple requests like "make me a soap label" or "write product descriptions for my soap line."

## The `soap-calc` Package

This project contains a full-featured soap calculator at `/Users/mikewolfd/Work/soap-calc`. **Use the package tools instead of doing manual calculations.** The package handles SAP values, lye calculations, property estimation, and validation — all from its built-in oil database.

### Key Project Paths
- **Oil database**: `data/oils.json` — built-in library of common oils with SAP values and fatty acid profiles
- **Additive database**: `data/additives.json` — common soap additives with usage rates and notes
- **Example recipes**: `examples/` — reference recipe files
- **JSON Schemas**: `schemas/` — validation schemas for recipes (`recipe.schema.json`), results (`recipe_result.schema.json`), oils (`oils.schema.json`), and additives (`additives.schema.json`)
- **User extensions**: Oils can be extended via `~/.soap_calc/oils.json`

### CLI Commands
The `soap-calc` command is available after installing the package (`pip install -e .`).

| Command | Usage | Purpose |
|---|---|---|
| `calculate` | `soap-calc calculate recipe.yaml` | Calculate lye, water, and measurements; display results |
| `export` | `soap-calc export recipe.yaml -o report.md` | Generate a detailed Markdown recipe sheet |
| `validate` | `soap-calc validate recipe.yaml` | Check recipe for warnings and issues |
| `list-oils` | `soap-calc list-oils "coconut"` | Search/list oils in the built-in database |
| `scale` | `soap-calc scale recipe.yaml 1000 -o scaled.yaml` | Resize recipe to a target oil weight |

- Use `--oil-weight <grams>` with `calculate` or `export` to override the recipe's default oil weight.
- Use `-o <path>` with `export` and `scale` to write output to a file.

### Python API
For programmatic use, the key modules are:

```python
from soap_calc.recipe_io import load_recipe, save_recipe, scale_recipe
from soap_calc.calculator import calculate
from soap_calc.export import export_markdown, render_markdown
from soap_calc.validation import validate
from soap_calc.oils import list_oils, search_oils
```

- `load_recipe(path)` → loads a JSON or YAML recipe file into a `Recipe` model
- `calculate(recipe, oil_weight=None)` → returns a `RecipeResult` with all lye, water, and oil measurements
- `render_markdown(recipe, result)` → returns a formatted Markdown string
- `export_markdown(recipe, result, path)` → writes the Markdown report to a file
- `validate(recipe)` → returns a list of warning strings (empty = no issues)
- `search_oils(query)` → returns matching `OilProfile` objects from the database
- `scale_recipe(recipe, target_oil_weight)` → returns a new `Recipe` scaled to the target

### Recipe File Format
Recipes are JSON or YAML. Key fields:

```json
{
  "name": "Recipe Name",
  "lye_type": "NaOH",              // "NaOH", "KOH", or "Dual"
  "superfat_pct": 5.0,
  "water_mode": "Water:Lye Ratio", // or "Lye Concentration", "% of Oil Weight"
  "water_value": 2.0,
  "default_oil_weight": 800,       // grams
  "oils": [
    { "oil": "Olive Oil", "percentage": 40 },
    { "oil": "Coconut Oil (76°)", "percentage": 30 }
  ],
  "liquids": [
    { "name": "Water", "percentage": 100 }
  ],
  "additives": [
    {
      "name": "Sodium Lactate",
      "percentage": 1.0,
      "percent_base": "Oil Weight",  // or "Liquid Weight", "Total Batch Weight"
      "stage": "Lye Liquid"          // or "Oil Phase", "Light Trace", "Medium Trace", "Heavy Trace", "Post Cook", "In Mold"
    }
  ],
  "fragrances": [
    {
      "name": "Lavender EO",
      "type": "Essential Oil",       // or "Fragrance Oil"
      "percentage": 3.0,
      "max_safe_pct": 5.0,
      "stage": "Light Trace"
    }
  ],
  "notes": "Optional recipe notes.",
  "ignore_warnings": ["ins_low", "iodine_high"]
}
```

- **Oil names must match the database exactly.** Use `soap-calc list-oils` to find correct names.
- **`percent_base`**: Controls what the additive percentage is relative to — `"Oil Weight"` (default), `"Liquid Weight"`, or `"Total Batch Weight"`.
- **`ignore_warnings`**: Suppress specific validation warnings by code.

### Workflow: Generating a Complete Recipe

When a user asks you to formulate a recipe, follow this workflow:

1. **Consult the reference file** for formulation guidance and archetype selection.
2. **Search the oil database** — run `soap-calc list-oils` or use `search_oils()` to confirm oil names and verify SAP values are available.
3. **Write the recipe file** as JSON or YAML using the format above. Save to the `examples/` directory or the user's requested location.
4. **Validate the recipe** — run `soap-calc validate <file>` to check for issues.
5. **Calculate the recipe** — run `soap-calc calculate <file>` to get exact lye, water, and oil amounts.
6. **Export if requested** — run `soap-calc export <file> -o report.md` to generate a printable recipe sheet.

**Never manually calculate lye amounts when the package is available.** The oil database has verified SAP values. Use `calculate()` or the CLI to get exact, safe lye figures.

## Recipe Output Format
When generating a soap recipe, always include:

1. **Oil blend** — list each oil with percentage of total oil weight
2. **Fatty acid profile summary** — approximate % lauric, myristic, palmitic, stearic, oleic, linoleic, ricinoleic
3. **Lye type and amount** — specify NaOH or KOH (or both), calculated at the stated superfat %
4. **Water amount** — as ratio to lye (e.g., 2:1 water:lye) or % of oil weight
5. **Superfat %** — and rationale for the chosen level
6. **Additives** — with usage rates (% of oil weight or tsp per lb of oils)
7. **Process notes** — CP or HP, expected trace speed, temperature guidance, cure time
8. **Expected soap properties** — hardness, lather type, cleansing level, conditioning, longevity

## Lye Calculation Rules
- **Use the `soap-calc` package for all lye calculations.** The built-in oil database has verified SAP values.
- If an oil is not in the database, say so and recommend the user add it to `~/.soap_calc/oils.json` or verify with an external calculator (SoapCalc, Soapee).
- Never present an unverified lye amount as safe. Incorrect lye = caustic or lye-heavy soap. This is a safety issue.
- Always state the superfat % used in the calculation.

## Safety Callouts
Always include safety notes when generating recipes or process instructions:
- Lye (NaOH/KOH) is caustic — gloves, goggles, ventilation required
- Always add lye TO water, never water to lye (exothermic boiling risk)
- Soap batter and fresh soap are alkaline and can irritate skin
- HP soap reaches 170–200°F — burn risk from hot batter
- Recommend pH testing or zap testing before first use of any new recipe

## Tone and Audience
- Default to practical, confident guidance — assume the user has basic soap making familiarity unless they indicate otherwise
- For beginners, add more process detail and explain "why" behind choices
- For experienced makers, focus on formulation rationale and tradeoffs
- Use the mental models from the reference file to build intuition, not just rote rules

## Common Request Patterns

**"Help me formulate a soap for [goal]"** → Read reference file. Start from the closest archetype recipe, then adjust fatty acid targets to match the goal. Write a recipe file, validate it, and calculate it with the package. Explain tradeoffs.

**"Why is my soap [problem]?"** → Read reference file. Map the symptom to likely causes (e.g., soft bar → too much oleic/not enough palmitic/stearic, or insufficient cure time; DOS → high polyunsaturates + no chelator/antioxidant). If the user provides a recipe file, run `soap-calc validate` and `soap-calc calculate` to get concrete data.

**"What oil can I substitute for [oil]?"** → Use `soap-calc list-oils` to look up fatty acid profiles. Match by fatty acid profile, not by oil name. Two oils with similar fatty acid breakdowns are interchangeable.

**"Review my recipe"** → Run `soap-calc validate` and `soap-calc calculate` on the recipe file. Check fatty acid balance against the targets in the reference file. Flag if cleansing is too high (>20% lauric+myristic without high superfat), if polyunsaturates are risky (>15% linoleic+linolenic without chelator), or if the bar will be too soft or too hard.

## Inventory-Aware Formulation

The project includes an **Inventory Management** skill (`.agent/skills/inventory/SKILL.md`) that saves a validated `inventory.md` file listing the user's available oils and additives.

**Only use the inventory when the user explicitly asks.** Look for phrases like:
- "use my inventory" / "from what I have"
- "make a recipe with my oils"
- "formulate using my supplies"

When inventory is requested:
1. Read `inventory.md` from the project root.
2. Constrain oil and additive selection to items listed in the inventory.
3. If the inventory doesn't contain enough variety for a good recipe (e.g., no hard oils, no lather booster), tell the user what's missing and suggest additions.
4. Follow the normal formulation workflow otherwise (consult reference file → validate → calculate → export).

**If the user does NOT mention their inventory, ignore `inventory.md` entirely and formulate from the full database as usual.**


## What This Skill Does NOT Cover
- Cosmetic regulatory compliance (FDA, EU cosmetics regulation)
- Melt-and-pour soap (different process entirely — no lye handling)
- Syndet bars (synthetic detergent bars — not true soap)
- Commercial-scale manufacturing processes

For these topics, answer from general knowledge or recommend the user consult specialized resources.
