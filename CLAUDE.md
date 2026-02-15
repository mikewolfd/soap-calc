# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`soap-calc` is a Python library and CLI for soap-making formulation and saponification calculations. It supports NaOH (bar soap), KOH (liquid soap), and dual-lye (hybrid) recipes with comprehensive property prediction, validation, and recipe export.

## Development Commands

### Installation
```bash
# Install in editable mode for development
pip install -e .

# Install test dependencies
pip install pytest
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_calculator.py

# Run specific test function
pytest tests/test_calculator.py::test_naoh_calculation

# Run with verbose output
pytest -v

# Run with output capture disabled (see print statements)
pytest -s
```

### CLI Usage
```bash
# Calculate a recipe (displays results in terminal)
soap-calc calculate examples/beginner_3oil.json

# Override default oil weight
soap-calc calculate recipe.yaml --oil-weight 1200

# Validate recipe for warnings
soap-calc validate recipe.yaml

# Export to Markdown
soap-calc export recipe.yaml -o report.md

# Scale recipe to target oil weight
soap-calc scale recipe.yaml 1000 -o scaled.yaml

# Search oil database
soap-calc list-oils "coconut"
```

## High-Level Architecture

### Core Data Flow

```
Recipe (JSON/YAML)
  ↓ recipe_io.load_recipe()
Recipe (models.Recipe)
  ↓ calculator.calculate()
  ├─→ oils.py: Load oil database, resolve SAP values
  ├─→ properties.py: Blend fatty acids, predict soap properties
  ├─→ fragrance.py: Calculate fragrance amounts with safety limits
  ├─→ validation.py: Check recipe for warnings
  ↓
RecipeResult (models.RecipeResult)
  ↓ export.render_markdown() / export.export_markdown()
Markdown Report
```

### Module Relationships

**Data Layer** (`models.py`)
- Defines all domain types: `Recipe`, `Oil`, `FattyAcidProfile`, `RecipeResult`, `SoapProperties`
- Enums: `LyeType`, `WaterCalculationMode`, `Stage`, `PercentBase`
- Dataclasses use composition: recipes contain oils, oils contain fatty acid profiles

**Database Layer** (`oils.py`, `additives.py`)
- Loads JSON databases from `data/oils.json` and `data/additives.json`
- Supports user extensions via `~/.soap_calc/oils.json`
- Provides search/lookup functions with fuzzy matching
- All oils must have SAP values for NaOH and KOH

**Calculation Engine** (`calculator.py`)
- Central `calculate(recipe, oil_weight=None)` function
- Handles three calculation paths:
  1. **Standard superfat**: Applies lye discount to all oils
  2. **Superfat oils**: Splits oils into base (saponified) and superfat phase (post-cook addition)
  3. **Dual lye**: Calculates NaOH and KOH amounts based on user-specified ratio
- Water calculation supports three modes: Water:Lye Ratio, Lye Concentration %, Water as % of Oils
- Returns `RecipeResult` with all calculated weights

**Property Prediction** (`properties.py`)
- `blend_fatty_acids()`: Combines fatty acid profiles from multiple oils weighted by percentage
- `predict_properties()`: Estimates hardness, cleansing, conditioning, lather (bubbly/creamy), longevity, iodine value, INS value
- Properties are derived from fatty acid profile composition (e.g., cleansing = lauric + myristic)

**I/O Layer** (`recipe_io.py`)
- Supports both JSON and YAML formats (auto-detected by extension)
- `load_recipe()`: Deserializes file → `Recipe` object
- `save_recipe()`: Serializes `Recipe` → file
- `scale_recipe()`: Proportionally resizes recipe to target oil weight

**Export Layer** (`export.py`)
- `render_markdown()`: Generates detailed recipe sheet with:
  - Ingredient tables grouped by stage (Lye Liquid, Oil Phase, Trace, Post Cook, In Mold)
  - Property analysis with visual bars
  - Step-by-step instructions
  - Warnings and validation results

**Validation** (`validation.py`)
- Checks for missing lye/water definitions
- Validates property ranges (e.g., warns if cleansing > 25% or hardness < 30%)
- Fragrance safety limit checks
- Returns list of warning strings (empty = no issues)

**CLI Interface** (`cli.py`)
- Subcommands: `calculate`, `export`, `validate`, `list-oils`, `scale`
- Uses `argparse` for argument parsing
- Entry point: `soap_calc.cli:main` (defined in `pyproject.toml`)

**Utilities** (`units.py`, `mold.py`, `fragrance.py`)
- `units.py`: Weight, volume, temperature, dimension conversions
- `mold.py`: Batch sizing based on mold dimensions (L×W×H) and fill factor
- `fragrance.py`: Fragrance calculation with IFRA essential oil safety database

## Critical Domain Knowledge

### Saponification Chemistry
- **Saponification** = alkaline hydrolysis of fats (triglyceride + base → soap + glycerol)
- **SAP value** = grams of alkali needed to saponify 1g of fat
  - Each oil has a unique SAP value for NaOH and KOH
  - SAP values are in `data/oils.json` and must be accurate (safety-critical)
- **Superfat** = intentional lye discount (5-8% typical), leaves free conditioning oils in soap

### Lye Types
- **NaOH (sodium hydroxide)**: Hard bar soap (tight crystalline structure)
- **KOH (potassium hydroxide)**: Soft paste or liquid soap (loose hydrated structure)
- **Dual lye**: Hybrid recipes (e.g., shaving soap) with custom NaOH:KOH ratio

### Fatty Acid Profiles Drive Soap Properties
- **Lauric + Myristic** (C12, C14): Big bubbles, cleansing, drying (coconut, palm kernel)
- **Palmitic + Stearic** (C16, C18): Hardness, creamy lather, longevity (palm, tallow, cocoa butter)
- **Oleic** (C18:1): Conditioning, gentle, slow hardening (olive, avocado)
- **Linoleic/Linolenic** (C18:2, C18:3): Conditioning but prone to rancidity (keep < 15%)
- **Ricinoleic** (C18:1 OH): Lather booster, foam stabilizer (castor oil, cap at 5-10%)

### Superfat Oil Split Logic
- **Standard superfat**: Lye discount applied uniformly to all oils (CP soap)
- **Superfat oils**: Separate oil list added post-cook (HP soap)
  - Calculator splits total oil weight: `base_oils = (100% - superfat_pct) × total`, `superfat_oils = superfat_pct × total`
  - Base oils are fully saponified, superfat oils bypass lye (guaranteed to remain as free oil)

### Water Calculation Modes
1. **Water:Lye Ratio**: `water_weight = lye_weight × ratio` (e.g., 2:1 is common)
2. **Lye Concentration**: `lye_weight / (lye_weight + water_weight) × 100 = concentration%`
3. **Water as % of Oils**: `water_weight = total_oil_weight × percentage / 100`

## Soap Formulation Agent Skill

**This repository includes a built-in Claude Code skill for soap formulation guidance.**

Location: `.agent/skills/soap-formulation/`

The skill provides:
- Expert formulation advice using the expert reference file (`soap-formulation-expert-reference.md`)
- Recipe generation workflow (consult reference → search oils → write recipe → validate → calculate → export)
- Troubleshooting guidance for soap making problems
- Safety callouts (lye handling, pH testing)

**When to use the skill:**
- User asks to formulate a new recipe
- User asks "why is my soap [problem]?" (soft, not lathering, DOS, etc.)
- User wants oil substitution advice
- User requests recipe review

**Key skill instructions:**
- Always use `soap-calc` package for lye calculations (never manual calculation — safety issue)
- Consult `soap-formulation-expert-reference.md` for fatty acid balance targets and formulation archetypes
- Use `soap-calc list-oils` to verify oil names match database before writing recipes
- Include safety notes in all formulation output

## Inventory Management Skill

Location: `.agent/skills/inventory/`

The skill processes user-provided oil and additive lists, cross-references against `data/oils.json` and `data/additives.json`, and saves a validated `inventory.md` at the project root.

**When to use the skill:**
- User tells you what oils/additives they have on hand
- User asks to add/remove/show/clear their inventory

**Key behavior:**
- Resolves user input to exact database names (safety-critical for SAP values)
- Asks for clarification on ambiguous matches (e.g., "coconut oil" → which variant?)
- Flags items not found in either database as unverified
- Other skills only use `inventory.md` when the user **explicitly** asks (e.g., "use my inventory")


## JSON Schemas

Schemas are in `schemas/` directory:
- `recipe.schema.json`: Recipe input format
- `recipe_result.schema.json`: Calculation output format
- `oils.schema.json`: Oil database format
- `additives.schema.json`: Additive database format

Validation script: `validate_schemas.py` (checks JSON files against schemas using `jsonschema` library)

## Recipe File Format

Recipes are JSON or YAML. Required fields:
- `name`: Recipe name
- `lye_type`: "NaOH", "KOH", or "Dual" (for dual, also specify `naoh_pct` and `koh_pct`)
- `superfat_pct`: Superfat percentage (5.0 typical)
- `water_mode`: "Water:Lye Ratio", "Lye Concentration", or "Water as % of Oils"
- `water_value`: Numeric value for the chosen water mode
- `total_oil_weight` OR `base_oil_weight`: Oil weight in grams (only one needed; `base_oil_weight` adds superfat on top)
- `oils`: List of `{"oil": "Oil Name", "percentage": X}` (must sum to ~100%)

Optional fields:
- `superfat_oils`: Separate oil list for post-cook superfat (HP soap)
- `liquids`: List of liquid phase ingredients (water, milk, etc.)
- `additives`: Additives with `name`, `percentage`, `percent_base`, `stage`
- `fragrances`: Fragrances with `name`, `type`, `percentage`, `max_safe_pct`, `stage`
- `notes`: Free text notes
- `ignore_warnings`: List of warning codes to suppress (e.g., `["ins_low", "iodine_high"]`)

See `examples/beginner_3oil.json` for a complete example.

## Important Constraints

**Never manually calculate lye amounts.** Always use the `calculate()` function or CLI. Incorrect lye calculations = caustic soap (safety hazard). SAP values vary by oil source and must come from the verified database.

**Oil names must match database exactly.** Use fuzzy search in `oils.py` or `soap-calc list-oils` to find correct names. Case-insensitive matching is supported but spelling must be close.

**Fatty acids should sum to ~100%.** The database is curated for accuracy, but user-added oils should have fatty acid profiles that sum to 100% ± 5%.

**Percentages are relative to specified base.** Additives can be percentage of:
- Oil Weight (default)
- Liquid Weight
- Total Batch Weight

The `percent_base` field controls this. The calculator resolves the actual weight based on calculated batch totals.

## Testing Strategy

Tests are in `tests/` directory:

- `test_calculator.py`: Core calculation engine (lye, water, superfat, dual-lye, property prediction)
- `test_modules.py`: Oil database, recipe I/O, scaling, validation, fragrance, mold, export, end-to-end
- `test_cli.py`: CLI command parsing and execution
- `test_units.py`: Unit conversion utilities

Tests use pytest fixtures for sample recipes and expected results. Many tests verify calculations against known good values (e.g., SoapCalc reference).
