# Soap Calc

[![PyPI](https://img.shields.io/pypi/v/soap-calc.svg)](https://pypi.org/project/soap-calc/)
[![Documentation](https://img.shields.io/badge/docs-latest-blue)](https://mikewolfd.github.io/soap-calc/)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-orange)](https://docs.anthropic.com/en/docs/claude-code)

> [!CAUTION]
> **Handle Lye with Care.** Sodium Hydroxide (NaOH) and Potassium Hydroxide (KOH) are caustic chemicals that cause severe burns. Always wear safety goggles and gloves. Verify all calculations before use.

**The first Python-based soap formulation library.** Define recipes in JSON, calculate lye and water amounts, predict soap properties, and export printable instructions—all from the command line or through AI agents like Claude Code.

Traditional web calculators lock your formulas in HTML forms. Soap Calc treats recipes as code: version them with git, iterate programmatically, and collaborate with AI to brainstorm oils, debug formulations, and scale batches. Ask "Create a moisturizing bar soap for dry skin" or "Why is this recipe too soft?" and get structured, chemically sound answers.

Every calculation is transparent and reproducible. No proprietary formulas, no hidden assumptions—just saponification chemistry you can audit and extend.

## Claude Code Plugin

> **Skip the CLI — formulate soap through conversation.** This repository doubles as a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin. Ask *"Create a moisturizing bar with shea butter"* or *"Why is my soap too soft?"* and get validated, calculated recipes with full chemistry explanations.

```bash
pip install soap-calc
claude plugin install https://github.com/mikewolfd/soap-calc
```

The plugin adds two skills to your Claude Code sessions:

#### 🧪 Soap Formulation

Expert formulation guidance combined with the calculation engine. Design, troubleshoot, and refine recipes through conversation.

- Generate recipes from plain English (*"conditioning shampoo bar"*, *"gentle baby soap"*)
- Troubleshoot problems (*"why is my soap soft?"*, *"how do I fix DOS?"*)
- Get oil substitution advice based on fatty acid profiles and SAP values
- Validate against formulation best practices before calculation
- Safety guidance for lye handling and pH testing

The skill consults a built-in expert reference for fatty acid balance targets and formulation archetypes, verifies oil names against the database, writes recipe files, validates, calculates, and exports — all while explaining the chemistry.

#### 📦 Inventory Management

Track your oils, butters, and additives. The skill cross-references items against the verified database and saves them for use in formulation.

- Resolves ambiguous names (e.g., "coconut oil" → prompts for specific variant)
- Flags unverified items not in the database
- Saves inventory to `~/.soap_calc/inventory.md` (global) or `./inventory.md` (project-specific)

**Try:** *"I have olive oil, coconut oil, shea butter, and sodium lactate"* then later *"Create a recipe using my inventory"*

> **Note:** Inventory is only used when you explicitly ask. Otherwise, formulations draw from the full oil database.

## Background

Inspired by [Soapmaking Friend](https://www.soapmakingfriend.com/), this project reimagines soap calculation as a Python library. Built collaboratively with AI tools including antigravity by Google, Gemini 3 Pro, and Claude Opus 4.6.

## Features

### Core Calculation
*   **Multi-Lye Support**
    *   **Sodium Hydroxide (NaOH)**: For hard bar soaps.
    *   **Potassium Hydroxide (KOH)**: For liquid soaps.
    *   **Dual Lye (Hybrid)**: Create hybrid recipes (e.g., shaving soap, cream soap) with any ratio of NaOH:KOH.
*   **Flexible Water Calculation Modes**
    *   **Water:Lye Ratio**: Specify water relative to the lye amount (e.g., 2:1).
    *   **Lye Concentration**: Calculate water needed to reach a specific lye concentration %.
    *   **Water as % of Oils**: Traditional method (discouraged but supported).
*   **Superfatting**
    *   Apply lye discount directly (standard superfat).
    *   Define "Superfat Oils" added post-cook or after the gel phase (Hot Process).

### Recipe Management
*   **Ingredient Management**:
    *   **Oils**: Define base oils with percentage of total oil weight.
    *   **Liquids**: Define liquid phase ingredients (water, milks, juices, etc.) with handling notes.
    *   **Additives**: Track additives (sugar, sodium lactate, colorants, exfoliants) with usage rates (amount or percentage) and addition stage.
    *   **Fragrances**: Manage Essential Oils and Fragrance Oils with usage amounts and safety limits.
*   **Phased Tracking**: Assign ingredients to specific stages:
    *   Lye Liquid
    *   Oil Phase
    *   Trace (Light/Medium/Heavy)
    *   Post Cook / After Gel
    *   In Mold
*   **Mold-Based Sizing**: Calculate total batch size based on mold dimensions (Length x Width x Height) and desired fill factor, assuming ~0.692 g/cm³ oil density.
*   **Recipe Scaling**: Automatically resize recipes to a target total oil weight while preserving ingredient ratios.

### Analysis & Validation
*   **Property Estimation**: Estimate theoretical soap qualities based on fatty acid profiles:
    *   Hardness, Cleansing, Conditioning
    *   Bubbly Lather, Creamy Lather
    *   Longevity
    *   Iodine Value
    *   INS Value
*   **Validation System**: Checks recipes for:
    *   Missing lye/water definitions.
    *   Properties falling outside recommended ranges.
    *   Fragrance safety limits (where applicable).

### Database & Extensibility
*   **Built-in Oil Library**: Includes common oils (Olive, Coconut, Palm, Shea Butter, Castor, etc.) with their SAP values and fatty acid profiles.
*   **User Extensions**: Extend the database with your own oils via `~/.soap_calc/oils.json`.
*   **Search**: CLI tools to list and search available oils.

### Output & Formats
*   **Input Formats**: Define recipes using human-readable **JSON** or **YAML**.
*   **Markdown Export**: Generate detailed, printable recipe sheets including:
    *   Calculated measurements (Lye, Water, Oils).
    *   Step-by-step ingredient checklists grouped by stage.
    *   Property analysis and warnings.

## Recipe Format Example

Create recipes in JSON or YAML. Here is a feature-rich example:

```json
{
  "name": "Lavender Dream",
  "lye_type": "NaOH",
  "superfat_pct": 5.0,
  "water_mode": "Water:Lye Ratio",
  "water_value": 2.0,
  "total_oil_weight": 800,
  "oils": [
    { "oil": "Olive Oil", "percentage": 40 },
    { "oil": "Coconut Oil, 76 deg", "percentage": 30 },
    { "oil": "Palm Oil", "percentage": 30 }
  ],
  "additives": [
    {
      "name": "Sodium Lactate",
      "percentage": 1.0,
      "percent_base": "Oil Weight",
      "stage": "Lye Liquid"
    }
  ],
  "fragrances": [
    { 
      "name": "Lavender EO", 
      "percentage": 3.0, 
      "max_safe_pct": 5.0 
    }
  ],
  "ignore_warnings": ["ins_low", "iodine_high"]
}
```

### Advanced Fields

*   **`total_oil_weight`** vs **`base_oil_weight`**: Two ways to specify batch size (only set one):
    *   `"total_oil_weight"`: Total weight of all oils in grams (base + superfat combined). Use for cold process or when you think in terms of total batch oils.
    *   `"base_oil_weight"`: Weight of just the base oils in grams. Superfat oils are calculated *on top* of this amount (`base × superfat_pct / 100`). Ideal for hot process recipes where you want a specific base oil weight.
    *   If neither is set, defaults to 800 g. A `mold` specification or CLI `--oil-weight` override takes priority over both.

    **Example:** `"base_oil_weight": 1000` with `"superfat_pct": 10` → 1000 g base oils + 100 g superfat oils = 1100 g total.

*   **`percent_base`**: When defining additives, specify what the percentage is based on.
    *   `"Oil Weight"` (Default)
    *   `"Liquid Weight"`
    *   `"Total Batch Weight"`
*   **`ignore_warnings`**: A list of warning codes to suppress during validation (e.g., if you intentionally want a very soft soap).

## Installation

This package requires Python 3.9 or higher.

Install from [PyPI](https://pypi.org/project/soap-calc/):

```bash
pip install soap-calc
```

Or install in editable mode for development:

```bash
git clone https://github.com/mikewolfd/soap-calc.git
cd soap-calc
pip install -e .
```

## CLI Usage

The `soap-calc` CLI is available after installation.

### Validate a Recipe
Check a recipe file for potential issues:
```bash
soap-calc validate my_recipe.yaml
```

### Calculate & View
Calculate a recipe and display the results in the terminal. You can optionally override the total oil weight using `--oil-weight` (or `-w` implies via arg parsing if alias existed, but use full flag for clarity):

```bash
soap-calc calculate my_recipe.yaml
# Override to 1200g oil weight
soap-calc calculate my_recipe.yaml --oil-weight 1200
```

### Export to Markdown
Generate a detailed report:
```bash
soap-calc export my_recipe.yaml -o report.md
```

### Scale a Recipe
Resize a recipe to use 1000g of oils:
```bash
soap-calc scale my_recipe.yaml 1000 -o scaled_recipe.yaml
```

### List Available Oils
```bash
soap-calc list-oils "coconut"
```

## Extending the Database

You can add your own oils by creating a file at `~/.soap_calc/oils.json`.

**Schema:**

```json
[
  {
    "name": "My Custom Oil",
    "sap_naoh": 0.135,
    "sap_koh": 0.190,
    "iodine": 55,
    "ins": 145,
    "fatty_acids": {
      "lauric": 0.0,
      "myristic": 0.0,
      "palmitic": 10.0,
      "stearic": 5.0,
      "ricinoleic": 0.0,
      "oleic": 40.0,
      "linoleic": 40.0,
      "linolenic": 0.0
    },
    "notes": "Sourced from Local Supplier X"
  }
]
```

*   **SAP Values**: Must be provided.
*   **Fatty Acids**: Should sum to approximately 100.0. Used for property calculation.

## Development

### Running Tests
To run the test suite, ensure you have `pytest` installed:

```bash
pip install pytest
pytest
```

### Project Structure
- `soap_calc/`: Main package source code.
- `tests/`: Unit and integration tests.
- `data/`: Built-in oil database.
- `examples/`: Example recipe files.

## Disclaimer

**Use at your own risk.** This software is provided "as is" without warranty of any kind. Soap making involves the use of caustic chemicals (sodium hydroxide and potassium hydroxide) which can cause severe burns and injury if mishandled.

- Always wear appropriate safety gear (goggles, gloves, long sleeves).
- Always verify lye calculations with a second source (e.g., [SoapCalc.net](http://soapcalc.net) or [Soapee](https://soapee.com)).
- The authors and contributors of this software are not liable for any injuries, damages, or ruined batches resulting from the use of this calculator.
- Professional advice is recommended for commercial production.
