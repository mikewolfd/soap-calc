# Soap Calc

A powerful soap-making calculator and recipe manager, designed to provide comprehensive data analysis and clear instructions for cold and hot process soap making.

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
  "default_oil_weight": 800,
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

*   **`percent_base`**: When defining additives, specify what the percentage is based on.
    *   `"Oil Weight"` (Default)
    *   `"Liquid Weight"`
    *   `"Total Batch Weight"`
*   **`ignore_warnings`**: A list of warning codes to suppress during validation (e.g., if you intentionally want a very soft soap).

## Installation

This package requires Python 3.9 or higher.

To install the package in editable mode (recommended for development):

```bash
pip install -e .
```

To install as a regular package:

```bash
pip install .
```

## Usage

Once installed, the `soap-calc` command is available in your terminal.

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
