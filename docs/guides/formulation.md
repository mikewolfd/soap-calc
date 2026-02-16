# Formulation Techniques

This guide covers advanced formulation strategies using `soap-calc`.

## Dual-Lye Recipes

Dual-lye recipes use both Sodium Hydroxide (NaOH) and Potassium Hydroxide (KOH). This is common for:
*   **Cream Soaps**: Often 60% KOH / 40% NaOH.
*   **Shaving Soaps**: Often high in Stearic Acid with a mix of lyes for lather stability and solubility.

**To create a dual-lye recipe:**

1.  Set `lye_type` to `"Hybrid"`.
2.  Add `ratio_naoh` (0.0 to 1.0). The remainder will be KOH.

```json
{
  "lye_type": "Hybrid",
  "ratio_naoh": 0.40,
  ...
}
```
*   `ratio_naoh: 0.40` means 40% of the lye is NaOH and 60% is KOH.

## Understanding Superfat

There are two ways to add extra moisturizing oils to your soap.

### 1. Traditional Lye Discount (`superfat_pct`)

The most common method. The calculator simply reduces the amount of lye used by the specified percentage.

```json
"superfat_pct": 5.0
```

*   **Pros**: Easy, safe margin for error.
*   **Cons**: You don't control *which* oils are unsaponified; the lye reacts with whatever it finds first.

### 2. Superfat Oils / Post-Cook Oils

In Hot Process (HP) soap making, you can add specific oils *after* the saponification cook is complete. These oils remain 100% intact as moisturizers.

To use this feature:
1.  Set `base_oil_weight` instead of `total_oil_weight`. This fixes the weight of the oils being cooked.
2.  Define "Superfat Oils" in your recipe (future feature implementation dependent, currently handled by manually adding oils to notes or specific "post-cook" stages if supported by your process workflow).

> **Note:** In the current version of `soap-calc`, `superfat_pct` applies a lye discount across the board. True "post-add" handling varies by process (CP vs HP) and is mechanically a process step rather than a different math calculation, as the total unsaponified fat is the same.

## Scaling to Molds

If you have a specific mold, you can calculate exactly how much oil you need to fill it.

**Formula:**
$$ \text{Total Oil Weight} = \text{Volume (cm}^3) \times 0.40 \text{ (approx factor)} $$

*   Wait, `soap-calc` uses a density of **0.692 g/cm³** for oils.

To calculate volume:
$$ \text{Volume} = \text{Length} \times \text{Width} \times \text{Height} $$

Example: A mold is 10cm x 5cm x 7cm.
$$ \text{Volume} = 350 \text{ cm}^3 $$
$$ \text{Oils Needed} = 350 \times 0.692 \approx 242 \text{ grams} $$

You can use `soap-calc scale` to resize your favorite recipe to this new weight.
