# CLI Usage Guide

The `soap-calc` command-line interface (CLI) is your primary tool for validating, calculating, and exporting recipes.

## Basic Commands

### `validate`

Checks your recipe file for errors without performing full calculations.

```bash
soap-calc validate recipe.json
```

**Common errors found:**
*   Oil percentages not summing to 100%.
*   Unknown oil names.
*   Missing required fields (e.g., `lye_type`).

### `calculate`

Computes the recipe and prints the results to the terminal.

```bash
soap-calc calculate recipe.json
```

**Options:**
*   `--oil-weight <grams>`: Override the `total_oil_weight` in the recipe file. Useful for resizing a batch on the fly.
    ```bash
    soap-calc calculate recipe.json --oil-weight 1000
    ```

### `export`

Generates a detailed Markdown report suitable for printing or sharing.

```bash
soap-calc export recipe.json -o instructions.md
```

**Options:**
*   `-o, --output <file>`: Specify the output filename. If omitted, prints to stdout.

### `scale`

Resizes a recipe file permanently and saves it as a new file.

```bash
soap-calc scale original.json 1200 -o scaled.json
```

This scales `original.json` to 1200g of total oils and saves it to `scaled.json`.

### `list-oils`

Searches the available oil database.

```bash
soap-calc list-oils "coconut"
```

Use this to find the exact naming spelling for your `oils` list.
