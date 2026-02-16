# Soap Calc

[![PyPI](https://img.shields.io/pypi/v/soap-calc.svg)](https://pypi.org/project/soap-calc/)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-orange)](https://docs.anthropic.com/en/docs/claude-code)

**The first Python-based soap formulation library.**

Define recipes in JSON, calculate lye and water amounts, predict soap properties, and export printable instructions—all from the command line or through AI agents like Claude Code.

<div class="grid cards" markdown>

-   :material-school: **Tutorials**
    ---
    New to Soap Calc? Start here to build your first recipe.

    [:arrow_right: Your First Recipe](tutorial/index.md)

-   :material-compass: **How-to Guides**
    ---
    Practical step-by-step guides for specific tasks.

    *   [:arrow_right: Formulation Techniques](guides/formulation.md)
    *   [:arrow_right: CLI Usage](guides/cli.md)
    *   [:arrow_right: Inventory Management](guides/inventory.md)

-   :material-book-open-page-variant: **Explanation**
    ---
    Understand the chemistry and math behind the calculator.

    *   [:arrow_right: The Math of Saponification](explanation/chemistry.md)
    *   [:arrow_right: Soap Properties](explanation/properties.md)

-   :material-code-json: **Reference**
    ---
    Technical API reference for the Python package.

    *   [:arrow_right: API Reference](reference/core.md)

-   :material-robot: **Skills**
    ---
    Supercharge your workflow with AI agents.

    *   [:arrow_right: Overview](skills/index.md)
    *   [:arrow_right: Inventory Management](skills/inventory.md)
    *   [:arrow_right: Formulation Assistant](skills/formulation.md)

</div>

## Key Features

*   **Multi-Lye Support:** NaOH (Bar), KOH (Liquid), and Dual-Lye (Hybrid).
*   **Transparent Math:** No hidden formulas. Every calculation is open source.
*   **Ingredient Database:** Customizable JSON-based oil library.
*   **Property Analysis:** Predict hardness, cleansing, conditioning, and more based on fatty acid profiles.
*   **Markdown Export:** Generate beautiful, printable recipe sheets.

## Installation

```bash
pip install soap-calc
```

## Quick Example

```python
from soap_calc import SoapCalculator

# Load your recipe
calculator = SoapCalculator("my_recipe.json")
# Calculate
result = calculator.calculate()
# Print results
print(result)
```
