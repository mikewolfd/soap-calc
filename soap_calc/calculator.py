"""Core saponification calculator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from soap_calc.fragrance import calculate_fragrance
from soap_calc.models import (
    AdditiveResult,
    LiquidBreakdown,
    LyeResult,
    LyeType,
    Oil,
    OilEntry,
    PercentBase,
    Recipe,
    RecipeResult,
    Stage,
    WaterCalculationMode,
)
from soap_calc.properties import blend_fatty_acids, predict_properties
from soap_calc.validation import validate


# ---------------------------------------------------------------------------
# Resolved oil entry (internal)
# ---------------------------------------------------------------------------


@dataclass
class _ResolvedOil:
    """An oil entry with its absolute weight computed from percentage."""

    oil: Oil
    percentage: float
    weight: float  # grams


def _resolve_entries(entries: List[OilEntry], total_weight: float) -> List[_ResolvedOil]:
    """Convert percentage-based oil entries to absolute weights."""
    # Normalize percentages if they don't sum to 100?
    # For now assume they are roughly 100 or relative to the total_weight phase.
    # Validation handles the sum check. Here we just apply the % logic.
    # If the user provides 50% + 50% = 100%, then sum of weights = total_weight.
    return [
        _ResolvedOil(
            oil=e.oil,
            percentage=e.percentage,
            weight=round(total_weight * e.percentage / 100.0, 2),
        )
        for e in entries
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def calculate(
    recipe: Recipe,
    *,
    oil_weight: Optional[float] = None,
    run_validation: bool = True,
) -> RecipeResult:
    """Run the full saponification calculation on a :class:`Recipe`."""
    
    # 1. Total Batch Oil Weight
    # This is the sum of Base Oils + Superfat Oils (if any)
    total_batch_oil_weight = recipe.resolve_oil_weight(oil_weight)

    # 2. Determine Split (Base vs Superfat Phase)
    has_superfat_oils = len(recipe.superfat_oils) > 0
    
    # Check if base_oil_weight drives the sizing (no override, no mold)
    _core_mode = (
        oil_weight is None
        and recipe.mold is None
        and recipe.base_oil_weight is not None
        and has_superfat_oils
    )
    
    if has_superfat_oils:
        if _core_mode:
            # Core-mode: base = core directly, superfat added on top
            weight_base_phase = float(recipe.base_oil_weight)  # type: ignore[arg-type]
            weight_superfat_phase = round(
                weight_base_phase * recipe.superfat_pct / 100.0, 2
            )
            total_batch_oil_weight = weight_base_phase + weight_superfat_phase
        else:
            # Total-mode: split total by superfat_pct
            sf_ratio = recipe.superfat_pct / 100.0
            if sf_ratio >= 1.0:
                sf_ratio = 0.99
            weight_superfat_phase = round(total_batch_oil_weight * sf_ratio, 2)
            weight_base_phase = total_batch_oil_weight - weight_superfat_phase
        
        # Base is fully saponified (0% discount)
        base_lye_discount = 0.0
        effective_superfat = recipe.superfat_pct
    else:
        # Standard Logic
        weight_base_phase = total_batch_oil_weight
        weight_superfat_phase = 0.0
        
        # Applying discount to base
        base_lye_discount = recipe.superfat_pct
        effective_superfat = recipe.superfat_pct

    # 3. Resolve Base Oils
    resolved_base = _resolve_entries(recipe.oils, weight_base_phase)

    # 4. Calculate Lye (on Base Phase)
    lye_discount_factor = 1.0 - (base_lye_discount / 100.0)

    purity_naoh = recipe.naoh_purity / 100.0
    purity_koh = recipe.koh_purity / 100.0
    
    # Avoid division by zero
    if purity_naoh <= 0: purity_naoh = 1.0
    if purity_koh <= 0: purity_koh = 0.90

    if recipe.lye_type == LyeType.NAOH:
        naoh_pure = sum(r.weight * r.oil.sap_naoh for r in resolved_base)
        naoh_pure = naoh_pure * lye_discount_factor
        naoh = round(naoh_pure / purity_naoh, 2)
        koh = 0.0
    elif recipe.lye_type == LyeType.KOH:
        koh_pure = sum(r.weight * r.oil.sap_koh for r in resolved_base)
        koh_pure = koh_pure * lye_discount_factor
        koh = round(koh_pure / purity_koh, 2)
        naoh = 0.0
    else:  # DUAL
        naoh_frac = recipe.naoh_ratio / 100.0
        koh_frac = 1.0 - naoh_frac
        
        naoh_pure = sum(r.weight * r.oil.sap_naoh for r in resolved_base)
        koh_pure = sum(r.weight * r.oil.sap_koh for r in resolved_base)
        
        naoh_pure = naoh_pure * naoh_frac * lye_discount_factor
        koh_pure = koh_pure * koh_frac * lye_discount_factor
        
        naoh = round(naoh_pure / purity_naoh, 2)
        koh = round(koh_pure / purity_koh, 2)

    total_lye = naoh + koh
    lye = LyeResult(naoh_amount=naoh, koh_amount=koh)

    # 5. Calculate Liquid (on Base Phase or Lye)
    mode = recipe.water_mode
    val = recipe.water_value
    
    if mode == WaterCalculationMode.WATER_LYE_RATIO:
        base_liquid = total_lye * val
    elif mode == WaterCalculationMode.LYE_CONCENTRATION:
        if val > 0 and val < 100:
            base_liquid = (total_lye / (val / 100.0)) - total_lye
        else:
            base_liquid = total_lye * 2.0
    else:  # WATER_PERCENT_OF_OILS
        # Use Base Phase weight logic
        base_liquid = weight_base_phase * (val / 100.0)

    # Apply liquid discount
    if recipe.liquid_discount_pct > 0:
        base_liquid *= (1.0 - recipe.liquid_discount_pct / 100.0)
    
    total_liquid = round(base_liquid, 2)

    # Liquid Breakdown
    liquid_breakdown: List[LiquidBreakdown] = []
    total_liq_pct = sum(l.percentage for l in recipe.liquids)
    if total_liq_pct > 0:
         for liq in recipe.liquids:
            amount = round(total_liquid * liq.percentage / total_liq_pct, 2)
            liquid_breakdown.append(LiquidBreakdown(liq.name, amount, liq.handling_notes))
    else:
        liquid_breakdown.append(LiquidBreakdown("Water", total_liquid))


    # 6. Process Additives
    # Note: Percentages usually relative to "Oils". In reformulation, this likely means TOTAL Batch Oils?
    # If I say "add 3% fragrance", I usually mean 3% of the total soaping oils.
    # So we use `total_batch_oil_weight`.
    
    additive_results: List[AdditiveResult] = []
    additive_weight = 0.0
    
    for add in recipe.additives:
        amt = 0.0
        if add.amount is not None:
            amt = add.amount
        elif add.percentage is not None:
            base_mass = 0.0
            if add.percent_base == PercentBase.OIL_WEIGHT:
                base_mass = total_batch_oil_weight
            elif add.percent_base == PercentBase.LIQUID_WEIGHT:
                base_mass = total_liquid
            else: # TOTAL_BATCH (Approx)
                base_mass = total_batch_oil_weight + total_lye + total_liquid
            
            amt = base_mass * add.percentage / 100.0
        
        amt = round(amt, 2)
        additive_weight += amt
        additive_results.append(
            AdditiveResult(name=add.name, amount=amt, stage=add.stage, notes=add.notes)
        )

    # 7. Process Superfat Oils
    superfat_results: List[AdditiveResult] = []
    
    if has_superfat_oils and weight_superfat_phase > 0:
        resolved_sf = _resolve_entries(recipe.superfat_oils, weight_superfat_phase)
        for r in resolved_sf:
            superfat_results.append(
                AdditiveResult(
                    name=r.oil.name,
                    amount=r.weight,
                    stage=Stage.POST_COOK,
                    notes="Superfat Phase"
                )
            )

    # 8. Fragrances
    fragrance_results: List[AdditiveResult] = []
    fragrance_warnings: List[str] = []
    fragrance_weight = 0.0
    
    for frag in recipe.fragrances:
        # Calculate relative to TOTAL oils
        f_res = calculate_fragrance(frag, total_batch_oil_weight)
        fragrance_weight += f_res.amount
        fragrance_results.append(
             AdditiveResult(
                 name=f_res.name,
                 amount=f_res.amount,
                 stage=frag.stage,
                 notes=frag.notes
             )
        )
        if f_res.warning:
            fragrance_warnings.append(f_res.warning)

    # 9. Properties
    # Properties should be based on the BASE PHASE (Saponified).
    # Superfat oils don't contribute to the crystalline soap structure properties (hardness/lather).
    # They act as conditioners.
    # So we pass `resolved_base` (converted back to simple OilEntries for the predictor)
    # The predictor expects a list of OilEntries with percentages.
    # Since `resolved_base` has absolute weights, we can reconstruct the percentages equivalent
    # relative to the BASE PHASE.
    
    # Actually, `recipe.oils` ALREADY contains the percentages relative to the Base Phase!
    # (Since we resolve `weight_base_phase` using them).
    # So we can just use `recipe.oils` for property prediction.
    
    properties = predict_properties(recipe.oils)
    fa_profile = blend_fatty_acids(recipe.oils)

    # 10. Total Weight & Result
    total_batch_weight = round(
        weight_base_phase + 
        weight_superfat_phase + 
        lye.total_weight + 
        total_liquid + 
        additive_weight + 
        fragrance_weight, 
        2
    )
    
    warnings = fragrance_warnings[:]
    if run_validation:
        warnings.extend(validate(recipe))
        
    filtered_warnings = []
    if recipe.ignore_warnings:
        for w in warnings:
            if not any(token.lower() in w.lower() for token in recipe.ignore_warnings):
                filtered_warnings.append(w)
    else:
        filtered_warnings = warnings

    return RecipeResult(
        lye=lye,
        total_liquid=total_liquid,
        liquid_breakdown=liquid_breakdown,
        total_oil_weight=weight_base_phase, # Saponified weight
        total_batch_weight=total_batch_weight,
        fatty_acid_profile=fa_profile,
        properties=properties,
        additives=additive_results,
        fragrances=fragrance_results,
        superfat_oils=superfat_results,
        effective_superfat_pct=effective_superfat,
        warnings=filtered_warnings
    )
