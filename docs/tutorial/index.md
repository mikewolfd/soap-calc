# Your First Soap Recipe

This tutorial will guide you through creating your first soap recipe using **Soap Calc**. We will formulate a classic "Bastille" style bar using Olive Oil, Coconut Oil, and Shea Butter.

## Learning Objectives

In this tutorial, you will learn how to:

1.  Create a recipe file in JSON format.
2.  Define oils and their percentages.
3.  Add lye and water settings.
4.  Calculate the recipe to get exact measurements.
5.  Export a printable PDF-ready markdown file.

## Prerequisites

Ensure you have `soap-calc` installed:

```bash
pip install soap-calc
```

## Step 1: Create the Recipe File

Create a file named `my_first_soap.json` in your project folder.

We'll start by defining the metadata:

```json
{
  "name": "My First Soap",
  "notes": "A simple, conditioning bar for beginners.",
  "lye_type": "NaOH",
  "total_oil_weight": 500
}
```

*   **`lye_type`**: `NaOH` (Sodium Hydroxide) is used for bar soap.
*   **`total_oil_weight`**: We are making a small test batch of 500g of oils.

## Step 2: Add Water Settings

Water controls how fast your soap tracks and hardens.

```json
  "water_mode": "Water:Lye Ratio",
  "water_value": 2.0,
```

We chose a `2.0:1` water-to-lye ratio. This is a safe, standard ratio that isn't too wet (slow to cure) or too dry (accerlates trace).

## Step 3: Define Oils

We will use a blend of three common oils:

1.  **Olive Oil** (65%): For conditioning.
2.  **Coconut Oil** (25%): For bubbles and hardness.
3.  **Shea Butter** (10%): For luxury and moisturizing properties.

Add this `oils` list to your JSON:

```json
  "oils": [
    { "oil": "Olive Oil", "percentage": 65 },
    { "oil": "Coconut Oil, 76 deg", "percentage": 25 },
    { "oil": "Shea Butter", "percentage": 10 }
  ],
```

> **Note:** Oil names must match the internal database. You can search for oils using `soap-calc list-oils "Shea"`.

## Step 4: Superfat

Superfatting adds extra oil that isn't turned into soap, providing a safety buffer against lye and adding moisture to the skin.

```json
  "superfat_pct": 5.0
```

## Complete Recipe

Your final `my_first_soap.json` should look like this:

```json
{
  "name": "My First Soap",
  "notes": "A simple, conditioning bar for beginners.",
  "lye_type": "NaOH",
  "total_oil_weight": 500,
  "water_mode": "Water:Lye Ratio",
  "water_value": 2.0,
  "superfat_pct": 5.0,
  "oils": [
    { "oil": "Olive Oil", "percentage": 65 },
    { "oil": "Coconut Oil, 76 deg", "percentage": 25 },
    { "oil": "Shea Butter", "percentage": 10 }
  ]
}
```

## Step 5: Calculate and Export

Run the calculator to see your measurements:

```bash
soap-calc calculate my_first_soap.json
```

You should see output detailing the exact grams of Lye, Water, and each Oil needed.

To get a printable guide, export to Markdown:

```bash
soap-calc export my_first_soap.json -o recipe_instructions.md
```

Open `recipe_instructions.md` to see your step-by-step soap making guide!
