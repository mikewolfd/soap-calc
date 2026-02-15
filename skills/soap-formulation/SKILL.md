---
name: soap-formulation
description: >
  Expert soap recipe formulation, troubleshooting, and educational guidance for cold process (CP),
  hot process (HP), bar soap (NaOH), and liquid soap (KOH). Use when the user asks to: (1) formulate
  or generate a soap recipe, (2) troubleshoot soap problems ("why is my soap soft/crumbly/not
  lathering/getting DOS"), (3) substitute or compare oils, (4) review or improve an existing recipe,
  (5) get formulation advice on fatty acid balance, superfat levels, or additive choices, or
  (6) learn about soap making chemistry and techniques. Do NOT use for melt-and-pour soap, syndet
  bars, or cosmetic regulatory questions.
compatibility: Requires soap-calc Python package (pip install -e .)
metadata:
  version: 1.0.0
---

# Soap Formulation Skill

## Before You Start
If the user's request involves **formulation, chemistry, fatty acid selection, additive choices, or troubleshooting soap behavior**, read `references/soap-formulation-expert-reference.md` first. It contains condensed expert knowledge on fatty acid profiles, additive interactions, and formulation archetypes.

If the request specifically involves **superfat oil selection, HP post-cook additions, DOS/rancidity prevention, or oxidation stability**, also read `references/superfat-guide.md`. It covers superfat tradeoffs (stability vs. sensory vs. lather), base-superfat interactions, and stabilization strategies in depth.

Skip the reference files for simple requests like "make me a soap label" or "write product descriptions for my soap line."

## The `soap-calc` Package

This project contains a full-featured soap calculator. **Use the package tools instead of doing manual calculations.** The package handles SAP values, lye calculations, property estimation, and validation — all from its built-in oil database.

### Key Project Paths
- **Oil database**: `data/oils.json` — built-in library of common oils with SAP values and fatty acid profiles
- **Additive database**: `data/additives.json` — common soap additives with usage rates and notes
- **Example recipes**: `examples/` — reference recipe files
- **JSON Schemas**: `schemas/` — validation schemas for recipes (`recipe.schema.json`), oils (`oils.schema.json`), and additives (`additives.schema.json`)
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

- Use `--oil-weight {grams}` with `calculate` or `export` to override the recipe's default oil weight.
- Use `-o {path}` with `export` and `scale` to write output to a file.

For Python API usage and writing recipe files, consult `references/api-guide.md`. It includes a schema-driven workflow for generating valid recipe JSON/YAML from `schemas/recipe.schema.json`.

### Workflow: Generating a Complete Recipe

When a user asks you to formulate a recipe, follow this workflow:

1. **Consult the reference file** for formulation guidance and archetype selection.
2. **Search the oil database** — run `soap-calc list-oils` or use `search_oils()` to confirm oil names and verify SAP values are available.
3. **Write the recipe file** — follow the schema-driven workflow in `references/api-guide.md`. Save to the `examples/` directory or the user's requested location.
4. **Validate the recipe** — run `soap-calc validate {file}` to check for issues.
5. **Calculate the recipe** — run `soap-calc calculate {file}` to get exact lye, water, and oil amounts.
6. **Export if requested** — run `soap-calc export {file} -o report.md` to generate a printable recipe sheet.

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

**"Why is my soap [problem]?"** → Read reference file. Map the symptom to likely causes (e.g., soft bar → too much oleic/not enough palmitic/stearic, or insufficient cure time; DOS → high polyunsaturates + no chelator/antioxidant). For DOS/rancidity specifically, also read `references/superfat-guide.md` for oxidation system analysis. If the user provides a recipe file, run `soap-calc validate` and `soap-calc calculate` to get concrete data.

**"What should I use for superfat?" / "Which oil for post-cook HP?"** → Read `references/superfat-guide.md`. Match recommendation to the user's base oil profile (high-lauric, high-stearic, high-oleic, or high-PUFA) using the base-superfat strategy table. Recommend from Bucket 1 (high-impact, stable) by default. Flag stability concerns for PUFA-heavy picks.

**"What oil can I substitute for [oil]?"** → Use `soap-calc list-oils` to look up fatty acid profiles. Match by fatty acid profile, not by oil name. Two oils with similar fatty acid breakdowns are interchangeable.

**"Review my recipe"** → Run `soap-calc validate` and `soap-calc calculate` on the recipe file. Check fatty acid balance against the targets in the reference file. Flag if cleansing is too high (>20% lauric+myristic without high superfat), if polyunsaturates are risky (>15% linoleic+linolenic without chelator), or if the bar will be too soft or too hard.

## Examples

### Example 1: "Make me a gentle beginner bar soap"

1. Read `references/soap-formulation-expert-reference.md` — select the "gentle face/baby" archetype as starting point, adjust toward a more balanced everyday bar.
2. Run `soap-calc list-oils "olive"` and `soap-calc list-oils "coconut"` to confirm exact database names.
3. Write a recipe file using the schema-driven workflow in `references/api-guide.md` (read schema, reference example, generate, validate).
4. Run `soap-calc validate recipe.json` — fix any warnings.
5. Run `soap-calc calculate recipe.json` — present lye/water/oil weights.
6. Offer to export: `soap-calc export recipe.json -o report.md`.

### Example 2: "Why is my soap getting orange spots?"

1. Read `references/soap-formulation-expert-reference.md` — identify DOS (Dreaded Orange Spots) as rancidity from high polyunsaturates.
2. Read `references/superfat-guide.md` — analyze both layers of oxidation risk (superfat pool + soap matrix) and base-superfat combo stability.
3. If the user provides a recipe file, run `soap-calc calculate` and check linoleic + linolenic totals.
4. Recommend: reduce polyunsaturates below 15%, switch to a stable superfat (Bucket 1 or 2), add a chelator (sodium citrate at 0.5% of oils), add antioxidant (ROE or vitamin E at 0.5% of oils). Reference additive details in `data/additives.json`.

### Example 3: "What can I use instead of palm oil?"

1. Run `soap-calc list-oils "palm"` to get the fatty acid profile of Palm Oil.
2. Match by fatty acid composition (high palmitic/stearic/oleic): tallow, lard, kokum butter, or mango butter are common substitutes.
3. Run `soap-calc list-oils "tallow"` etc. to confirm database names and compare SAP values.
4. Explain the tradeoffs (e.g., tallow is closest but not vegan; kokum butter is harder but more expensive).

## Inventory-Aware Formulation

The project includes an **Inventory Management** skill (`skills/inventory/SKILL.md`) that saves a validated `inventory.md` file listing the user's available oils and additives.

**Only use the inventory when the user explicitly asks.** Look for phrases like:
- "use my inventory" / "from what I have"
- "make a recipe with my oils"
- "formulate using my supplies"

When inventory is requested:
1. **Find the inventory file** (priority order):
   - Check `./inventory.md` (current directory) first
   - Fall back to `~/.soap_calc/inventory.md` (user default)
   - If neither exists, tell the user they need to create an inventory first
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
