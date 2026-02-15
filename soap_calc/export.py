"""Export a calculated recipe to Markdown."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from soap_calc.models import (
    Recipe,
    RecipeResult,
    Stage,
    WaterCalculationMode,
)


# Stage ordering for the instructions section
_STAGE_ORDER = [
    Stage.LYE_LIQUID,
    Stage.OIL_PHASE,
    Stage.LIGHT_TRACE,
    Stage.MEDIUM_TRACE,
    Stage.HEAVY_TRACE,
    Stage.POST_COOK,
    Stage.IN_MOLD,
]

_STAGE_INSTRUCTIONS = {
    Stage.LYE_LIQUID: (
        "**Prepare the lye solution.** Wearing safety gear (goggles, gloves), "
        "slowly add the lye to your liquid(s) — *never* the other way around. "
        "Stir until dissolved and set aside to cool."
    ),
    Stage.OIL_PHASE: (
        "**Prepare the oils.** Weigh and combine your oils. Melt any solid "
        "oils/butters gently, then allow the oil blend to cool to your target "
        "temperature (typically 100–110 °F / 38–43 °C)."
    ),
    Stage.LIGHT_TRACE: (
        "**Combine & reach light trace.** When both lye solution and oils are "
        "at temperature, pour the lye solution into the oils and blend with a "
        "stick blender until light trace. Add the following ingredients:"
    ),
    Stage.MEDIUM_TRACE: (
        "**Medium trace.** Continue blending until the batter thickens to "
        "medium trace. Add the following:"
    ),
    Stage.HEAVY_TRACE: (
        "**Heavy trace.** Blend until the batter is thick. Add:"
    ),
    Stage.POST_COOK: (
        "**Post-Cook / After Gel.** (For Hot Process) After the cook is complete "
        "and temperature drops below flashpoints, stir in:"
    ),
    Stage.IN_MOLD: (
        "**Pour into mold.** Transfer the batter to your prepared mold. "
        "Add any toppings or swirls, then:"
    ),
}


def _fmt_pv(pv) -> str:
    """Format a PropertyValue for the properties table."""
    icon = {"Below": "⬇️", "Within": "✅", "Above": "⬆️"}.get(pv.rating.value, "")
    return f"{pv.value:.0f} ({pv.low}–{pv.high}) {icon}"


def _draw_bar(value: float, max_value: float = 100.0, width: int = 15) -> str:
    """Draw a text-based progress bar."""
    if max_value <= 0:
        return ""
    
    # Cap value for display
    pct = max(0.0, min(value, max_value)) / max_value
    filled = int(round(pct * width))
    empty = width - filled
    
    # Using block chars: █ and ░
    return f"`{'█' * filled}{'░' * empty}`"

def render_markdown(recipe: Recipe, result: RecipeResult) -> str:
    """Render a recipe + result as a Markdown string."""
    lines: list[str] = []
    a = lines.append

    total_base_oil = result.total_oil_weight

    # --- Header -----------------------------------------------------------
    a(f"# 🧼 {recipe.name}\n")
    a(f"**Total base oil weight:** {total_base_oil:.0f} g  ")
    a(f"**Total batch weight:** {result.total_batch_weight:.0f} g  ")
    
    if recipe.superfat_oils:
        # Split Phase Mode
        a(f"**Superfat Phase (Post-Cook):** {recipe.superfat_pct:.1f} % of Total Oil  ")
        a(f"**Lye Discount on Base Phase:** 0 %  ")
    else:
        # Standard Mode
        a(f"**Lye Discount (Superfat):** {recipe.superfat_pct:.0f} %  ")
    
    if result.superfat_oils and not recipe.superfat_oils:
         # Fallback? No, if result has superfat_oils, recipe must have had them.
         pass
    
    a(f"**Lye type:** {recipe.lye_type.value}  ")

    # Water mode display
    if recipe.water_mode == WaterCalculationMode.WATER_LYE_RATIO:
        a(f"**Water:Lye Ratio:** {recipe.water_value:.1f}:1")
    elif recipe.water_mode == WaterCalculationMode.LYE_CONCENTRATION:
        a(f"**Lye Concentration:** {recipe.water_value:.1f} %")
    else:
        a(f"**Water as % of Oils:** {recipe.water_value:.1f} %")

    if recipe.liquid_discount_pct > 0:
        a(f"  **Liquid discount:** {recipe.liquid_discount_pct:.0f} %")
    a("")

    # --- Oils table -------------------------------------------------------
    a("## Base Oils\n")
    a("| Oil | % of Oils | Weight (g) |")
    a("|---|---:|---:|")
    for entry in recipe.oils:
        weight = total_base_oil * entry.percentage / 100.0
        a(f"| {entry.oil.name} | {entry.percentage:.1f} % | {weight:.1f} |")
    a(f"| **Total** | **100 %** | **{total_base_oil:.1f}** |")
    a("")
    
    # --- Superfat Oils ----------------------------------------------------
    if result.superfat_oils:
        a("## Superfat / Post-Cook Oils\n")
        a("| Oil | Weight (g) |")
        a("|---|---:|")
        for entry in result.superfat_oils:
            a(f"| {entry.name} | {entry.amount:.1f} |")
        a("")

    # --- Lye & Liquid -----------------------------------------------------
    a("## Lye & Liquid\n")
    lye = result.lye
    if lye.naoh_amount > 0:
        a(f"- **NaOH:** {lye.naoh_amount:.2f} g")
    if lye.koh_amount > 0:
        a(f"- **KOH:** {lye.koh_amount:.2f} g")
    a(f"- **Total liquid:** {result.total_liquid:.2f} g")
    if len(result.liquid_breakdown) > 1 or (
        result.liquid_breakdown and result.liquid_breakdown[0].name.lower() != "water"
    ):
        for lb in result.liquid_breakdown:
            note = f" — {lb.handling_notes}" if lb.handling_notes else ""
            a(f"  - {lb.name}: {lb.amount:.1f} g{note}")
    a("")

    # --- Additives --------------------------------------------------------
    if result.additives:
        a("## Additives\n")
        a("| Additive | Weight (g) | Stage |")
        a("|---|---:|---|")
        for ar in result.additives:
            a(f"| {ar.name} | {ar.amount:.1f} | {ar.stage.value} |")
        a("")

    # --- Fragrances -------------------------------------------------------
    if result.fragrances:
        a("## Fragrance\n")
        a("| Fragrance | Weight (g) | Stage |")
        a("|---|---:|---|")
        for fr in result.fragrances:
            a(f"| {fr.name} | {fr.amount:.1f} | {fr.stage.value} |")
        a("")

    # --- Soap Properties --------------------------------------------------
    a("## Predicted Soap Properties\n")
    a("> *Note: These properties are calculated for the base saponified oils only.*  \n")
    a("| Property | Value (Range) | Profile |")
    a("|---|---|---|")
    props = result.properties
    for pv in [
        props.hardness,
        props.cleansing,
        props.conditioning,
        props.bubbly_lather,
        props.creamy_lather,
        props.iodine,
        props.ins,
    ]:
        bar = _draw_bar(pv.value, 100.0, 10)
        # Iodine and INS have different scales, but 100 is a decent arbitrary max for simple visualization
        # except INS which goes to ~170.
        if pv.name == "INS":
             bar = _draw_bar(pv.value, 200.0, 10)
        
        a(f"| {pv.name} | {_fmt_pv(pv)} | {bar} |")
    a("")

    # --- Fatty Acid Profile -----------------------------------------------
    a("## Fatty Acid Profile\n")
    fa = result.fatty_acid_profile
    a("| Fatty Acid | % | Profile |")
    a("|---|---:|---|")
    for name, val in [
        ("Lauric", fa.lauric),
        ("Myristic", fa.myristic),
        ("Palmitic", fa.palmitic),
        ("Stearic", fa.stearic),
        ("Ricinoleic", fa.ricinoleic),
        ("Oleic", fa.oleic),
        ("Linoleic", fa.linoleic),
        ("Linolenic", fa.linolenic),
    ]:
        if val > 0:
            bar = _draw_bar(val, 50.0, 10) # 50% is a reasonable max for any single FA
            a(f"| {name} | {val:.1f} | {bar} |")
    a("")

    # --- Step-by-step instructions ----------------------------------------
    a("## Instructions\n")
    by_stage = result.ingredients_by_stage()

    step = 1
    for stage in _STAGE_ORDER:
        instruction = _STAGE_INSTRUCTIONS.get(stage, "")
        items = by_stage.get(stage, [])

        if not items and stage not in (Stage.LYE_LIQUID, Stage.OIL_PHASE):
            continue

        a(f"### Step {step}: {stage.value}\n")
        if instruction:
            a(f"{instruction}\n")

        if stage == Stage.OIL_PHASE:
            for entry in recipe.oils:
                weight = total_base_oil * entry.percentage / 100.0
                a(f"- {entry.oil.name}: {weight:.1f} g")
        else:
            for item in items:
                a(f"- {item}")
        a("")
        step += 1

    # Cure
    a(f"### Step {step}: Cure\n")
    a(
        "Insulate the mold for 24–48 hours, then unmold and cut into bars. "
        "Cure on a rack in a cool, dry place with good airflow for **4–6 weeks** "
        "before use.\n"
    )

    # --- Warnings ---------------------------------------------------------
    if result.warnings:
        a("## ⚠️ Warnings\n")
        for w in result.warnings:
            a(f"- {w}")
        a("")

    # --- Notes ------------------------------------------------------------
    if recipe.notes:
        a("## Notes\n")
        a(recipe.notes)
        a("")

    return "\n".join(lines)


def export_markdown(
    recipe: Recipe,
    result: RecipeResult,
    path: Union[str, Path],
) -> None:
    """Write the recipe card to a Markdown file."""
    md = render_markdown(recipe, result)
    Path(path).write_text(md, encoding="utf-8")
