# soap-calc API & Recipe Format Reference

## Python API

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

## Writing Recipe Files

Recipe files are JSON or YAML. **Always generate recipes from the schema and examples — never from memory.**

### Step 1: Read the schema

Read `schemas/recipe.schema.json` to get the current field definitions, enum values, required fields, and defaults. The schema is the single source of truth for recipe structure.

Pay attention to:
- **Enum values** — `LyeType`, `WaterCalculationMode`, `Stage`, `PercentBase`, `FragranceType` all have exact allowed values defined in `$defs`. Use only those values.
- **Required vs optional fields** — the schema defines which fields are required per object type (e.g., `OilEntry` requires both `oil` and `percentage`).
- **Defaults** — many fields have defaults (e.g., `superfat_pct` defaults to 5.0, `water_mode` defaults to "Water:Lye Ratio"). Omit fields where the default is acceptable to keep recipes minimal.

### Step 2: Reference a working example

Read `examples/beginner_3oil.json` to see correct structure and formatting conventions. Use this as a structural template — match its indentation, key ordering, and nesting style.

### Step 3: Generate the recipe

Write the recipe JSON/YAML conforming to the schema. Follow these rules:

- **Oil names must match the database exactly.** Always verify with `soap-calc list-oils` before writing. A wrong name = wrong SAP value = unsafe lye calculation.
- **Oil percentages must sum to ~100%.** The schema enforces 0–100 per entry, but total balance is your responsibility.
- **Only include fields that differ from defaults.** A minimal recipe is easier to read and less likely to contain errors.
- **`percent_base` on additives** controls what the percentage is relative to — check the schema's `PercentBase` enum for allowed values.
- **`ignore_warnings`** is an array of warning code strings — only include if the user explicitly wants to suppress specific warnings.

### Step 4: Validate

After writing, always run `soap-calc validate {file}` to catch issues the schema alone can't enforce (property range warnings, fatty acid balance, etc.).
