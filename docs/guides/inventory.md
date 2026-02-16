# Inventory & Custom Oils

`soap-calc` comes with a large database of standard oils, but you may want to add your own or manage what you have in stock.

## Adding Custom Oils

You can extend the default database by creating a `~/.soap_calc/oils.json` file on your machine.

### File Format

The file should contain a JSON list of oil objects.

```json
[
  {
    "name": "My Special Exotic Butter",
    "sap_naoh": 0.128,
    "sap_koh": 0.180,
    "iodine": 60,
    "ins": 115,
    "fatty_acids": {
       "lauric": 0.0,
       "myristic": 0.0,
       "palmitic": 5.0,
       "stearic": 5.0,
       "ricinoleic": 0.0,
       "oleic": 50.0,
       "linoleic": 35.0,
       "linolenic": 0.0
    },
    "notes": "Sourced from local farm"
  }
]
```

### Critical Fields
*   **`name`**: Must be unique.
*   **`sap_naoh`** or **`sap_koh`**: The Saponification Value. If you only have one, `soap-calc` can estimate the other (KOH is approx NaOH * 1.403), but providing both is best.
*   **`fatty_acids`**: A dictionary summing to ~100. This is required for property calculation (Hardness, Cleansing, etc.).

Once added, `soap-calc` will automatically load this file and you can use "My Special Exotic Butter" in any recipe.
