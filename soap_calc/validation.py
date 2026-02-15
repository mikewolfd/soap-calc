"""Recipe validation — checks a recipe and returns warnings."""

from __future__ import annotations

from typing import List

from soap_calc.models import (
    FragranceType,
    LyeType,
    Recipe,
    WaterCalculationMode,
)
from soap_calc.fragrance import get_eo_max_rate
from soap_calc.additives import get_additive


def validate(recipe: Recipe) -> List[str]:
    """Return a list of warning strings for the given recipe.

    An empty list means no issues were detected.
    """
    warnings: List[str] = []

    # --- Basic sanity checks -----------------------------------------------
    if not recipe.oils:
        warnings.append("Recipe has no oils.")
        return warnings

    total_pct = sum(e.percentage for e in recipe.oils)
    if abs(total_pct - 100.0) > 0.5:
        warnings.append(
            f"Oil percentages sum to {total_pct:.1f}% (should be 100%)."
        )

    for entry in recipe.oils:
        if entry.percentage < 0:
            warnings.append(f"{entry.oil.name}: oil percentage cannot be negative.")

    # --- Superfat ----------------------------------------------------------
    if recipe.superfat_pct < 0:
        warnings.append("Superfat percentage is negative — this would use more lye than needed to saponify all oils.")
    elif recipe.superfat_pct >= 100:
        warnings.append(
            f"Superfat of {recipe.superfat_pct:.0f}% would leave no oil for saponification. "
            "Reduce superfat_pct to less than 100%."
        )
    elif recipe.superfat_pct > 20:
        warnings.append(
            f"Superfat of {recipe.superfat_pct:.0f}% is unusually high. "
            "Most recipes use 3–8 %. Very high superfat can create a soft, oily bar."
        )
    elif recipe.superfat_pct == 0:
        warnings.append("Superfat is 0 % — the bar will have no excess fat for skin conditioning and may be harsh.")

    # --- Water / Liquid calc -----------------------------------------------
    mode = recipe.water_mode
    val = recipe.water_value

    if mode == WaterCalculationMode.WATER_LYE_RATIO:
        if val < 1.0:
            warnings.append(f"Water:Lye ratio of {val:.2f} is dangerously low (unsafe).")
        elif val > 3.5:
            warnings.append(f"Water:Lye ratio of {val:.2f} is very high (long cure time).")

    elif mode == WaterCalculationMode.LYE_CONCENTRATION:
        if val < 25.0:
            warnings.append(f"Lye concentration of {val:.1f}% is very low (too much water).")
        elif val > 50.0:
            warnings.append(f"Lye concentration of {val:.1f}% is dangerously high (unsafe).")
    
    elif mode == WaterCalculationMode.WATER_PERCENT_OF_OILS:
        if val < 20.0:
             warnings.append(f"Water as % of oils ({val:.1f}%) is very low (steep discount).")
        elif val > 40.0:
             warnings.append(f"Water as % of oils ({val:.1f}%) is high (long cure time).")

    # --- Liquid discount ---------------------------------------------------
    if recipe.liquid_discount_pct < 0:
        warnings.append("Liquid discount percentage should not be negative.")
    elif recipe.liquid_discount_pct > 30:
        warnings.append(
            f"Liquid discount of {recipe.liquid_discount_pct:.0f}% is very aggressive. "
            "This can cause the batter to seize or be difficult to work with."
        )

    # --- Dual-lye ratio ----------------------------------------------------
    if recipe.lye_type == LyeType.DUAL:
        if not (0 < recipe.naoh_ratio < 100):
            warnings.append(
                f"Dual-lye NaOH ratio is {recipe.naoh_ratio:.0f}%. "
                "It should be between 0 and 100 (exclusive). "
                "Use LyeType.NAOH or LyeType.KOH for single-lye recipes."
            )

    # --- Oil-specific checks -----------------------------------------------
    for entry in recipe.oils:
        fa = entry.oil.fatty_acids
        name = entry.oil.name

        # High-cleansing oils (coconut, babassu, palm kernel) can be drying
        if fa.cleansing > 40 and entry.percentage > 30:
            warnings.append(
                f"{name} is {entry.percentage:.0f}% of oils (high cleansing). "
                f"Above 30 % it can be drying — consider raising superfat to 8–20 %."
            )

    # --- Blend-level checks ------------------------------------------------
    from soap_calc.properties import blend_fatty_acids, calculate_iodine

    blended = blend_fatty_acids(recipe.oils)
    iodine = calculate_iodine(recipe.oils)

    if blended.hard < 10:
        warnings.append(
            "Very low hard-fat content — the bar will be extremely soft. "
            "Consider adding palm, coconut, tallow, or a butter."
        )

    if iodine > 70:
        warnings.append(
            f"Iodine value is {iodine:.0f} (recommended ≤ 70). "
            "High iodine increases risk of DOS (dreaded orange spots) and reduces longevity."
        )

    # --- Fragrance checks --------------------------------------------------
    for frag in recipe.fragrances:
        if frag.fragrance_type == FragranceType.ESSENTIAL_OIL:
            max_rate = frag.max_safe_pct or get_eo_max_rate(frag.name)
            if max_rate is not None and frag.percentage is not None:
                if frag.percentage > max_rate:
                    warnings.append(
                        f"{frag.name}: requested {frag.percentage:.1f}% exceeds IFRA max "
                        f"of {max_rate:.1f}% for rinse-off products."
                    )

    # --- Superfat Oils checks ----------------------------------------------
    if recipe.superfat_oils:
        total_sf_oil_pct = sum(sf.percentage for sf in recipe.superfat_oils)
        if abs(total_sf_oil_pct - 100.0) > 0.5:
             warnings.append(
                f"Superfat oil percentages sum to {total_sf_oil_pct:.1f}% (should be 100% of the Superfat Phase)."
            )

    # --- Strict Safety Checks ----------------------------------------------
    if recipe.naoh_purity <= 0:
        warnings.append("NaOH purity must be greater than 0%.")
    
    if recipe.lye_type == LyeType.KOH and recipe.koh_purity <= 0:
        warnings.append("KOH purity must be greater than 0%.")

    # --- Additive checks ---------------------------------------------------
    for add in recipe.additives:
        # Stearic Acid Safety Check
        if "stearic acid" in add.name.lower():
             warnings.append(
                 f"'{add.name}' is listed as an additive. Stearic Acid should be entered as an Oil "
                 "so its SAP value is calculated correctly. Using it as an additive treats it as inert."
             )

        info = get_additive(add.name)
        if not info:
            continue

        # Check percentage usage if applicable
        # We only check if the user specified a percentage relative to oil weight,
        # and the DB defines usage in "pct" of "oil_weight".
        if (
            add.percentage is not None
            and info.usage.unit == "pct"
            and info.usage.per == "oil_weight"
        ):
            # Verify the percentage base matches (default is OIL_WEIGHT)
            # Assuming Additive.percent_base is OIL_WEIGHT for now as it's the default
            if add.percentage > info.usage.max > 0:
                warnings.append(
                    f"{add.name}: {add.percentage:.1f}% exceeds max recommended {info.usage.max:.1f}%."
                )

        # Check stage recommendation
        # info.stage is the string value of the recommended stage
        if info.stage and add.stage.value != info.stage:
            warnings.append(
                f"{add.name}: Recommended stage is '{info.stage}' (current: '{add.stage.value}')."
            )

    # --- Liquid allocation -------------------------------------------------
    total_liquid_pct = sum(liq.percentage for liq in recipe.liquids)
    if recipe.liquids and abs(total_liquid_pct - 100.0) > 0.1:
        warnings.append(
            f"Custom liquid percentages sum to {total_liquid_pct:.1f}% (should be 100%)."
        )

    return warnings
