"""Superfat character analysis for post-cook oil blends."""

from __future__ import annotations

from typing import List, Optional

from soap_calc.models import OilEntry, SkinFeel
from soap_calc.properties import blend_fatty_acids


def _detect_wax_fraction(oils: List[OilEntry]) -> float:
    """Return the fraction (0-1) of the blend that is non-triglyceride wax.

    Waxes (lanolin, beeswax) have near-zero standard fatty acid values in
    our database but positive SAP values.  This heuristic relies on the
    curated oil database — oils with incomplete FA data could be
    misclassified; add an ``is_wax`` field to Oil if this becomes a problem.

    Args:
        oils: List of oil entries in the blend.

    Returns:
        The fraction of the blend that is wax (0.0 to 1.0).
    """
    total_pct = sum(o.percentage for o in oils)
    if total_pct <= 0:
        return 0.0
    wax_pct = sum(
        o.percentage for o in oils
        if sum(o.oil.fatty_acids.model_dump().values()) < 1.0
        and o.oil.sap_naoh > 0
    )
    return wax_pct / total_pct


def _classify_3(score: float, low_thresh: float, high_thresh: float) -> str:
    """Classify a score into Low / Moderate / High.

    Args:
        score: The numeric score to classify.
        low_thresh: The minimum threshold for "Moderate" classification.
        high_thresh: The minimum threshold for "High" classification.

    Returns:
        Classification string: "Low", "Moderate", or "High".
    """
    if score >= high_thresh:
        return "High"
    elif score >= low_thresh:
        return "Moderate"
    return "Low"


def analyze_skin_feel(
    oils: List[OilEntry],
    base_oils: Optional[List[OilEntry]] = None,
    superfat_pct: float = 5.0,
) -> SkinFeel:
    """Profile the superfat character of a post-cook oil blend.

    Reports four independent dimensions rather than a single classification:
      - **Film Persistence**: waxy saturates (palmitic+stearic) + wax boost.
        Solid-at-body-temp fats resist solubilization by soap micelles.
      - **Emollient Slip**: oleic + ricinoleic (monounsaturated).
        Liquid emollients that provide slip and after-feel.
      - **Lather Impact**: fluidity-weighted antifoam score, scaled by
        superfat % and adjusted for base soap interaction.
      - **DOS Risk**: polyunsaturated FA (linoleic+linolenic) fraction.
        PUFA in the free oil phase oxidizes rapidly.

    Args:
        oils (List[OilEntry]): The oils comprising the superfat phase.
        base_oils (Optional[List[OilEntry]]): The base soap oils (used for coupling calculations).
            Defaults to None.
        superfat_pct (float): The total percentage of superfat. Defaults to 5.0.

    Returns:
        SkinFeel: A detailed analysis of the estimated skin feel.
    """
    fa = blend_fatty_acids(oils)

    # --- Fatty acid groups ---------------------------------------------------
    waxy_sat = fa.palmitic + fa.stearic
    brittle_sat = fa.lauric + fa.myristic
    mono = fa.oleic + fa.ricinoleic
    poly = fa.linoleic + fa.linolenic
    total_fa = waxy_sat + brittle_sat + mono + poly

    wax_fraction = _detect_wax_fraction(oils)
    wax_boost = wax_fraction * 50.0

    # --- Base Coupling -------------------------------------------------------
    # High-cleansing (lauric/myristic) bases solubilize superfat aggressively,
    # reducing its effective contribution across all dimensions — not just foam.
    if base_oils:
        base_fa = blend_fatty_acids(base_oils)
        base_cleansing = (base_fa.lauric + base_fa.myristic) / 100.0
        retention = 1.0 - (base_cleansing * 0.3)
    else:
        retention = 1.0

    # --- Film Persistence ----------------------------------------------------
    # Palmitic+stearic are solid at body temp → physical barrier on skin.
    # The 1.2x multiplier reflects their outsized perceptual impact (they
    # resist solubilization more than their percentage suggests).
    # Wax boost adds occlusive contribution from non-triglyceride waxes.
    # Retention: high-cleansing bases strip superfat, reducing film.
    film_score = (waxy_sat * 1.2 + wax_boost) * retention
    film_persistence = _classify_3(film_score, 20.0, 40.0)

    # --- Emollient Slip ------------------------------------------------------
    # Oleic and ricinoleic are liquid at skin temp → slip, after-feel.
    # Retention: liquid emollients are especially vulnerable to wash-off
    # by aggressive micelles.
    emollient_score = mono * retention
    emollient_slip = _classify_3(emollient_score, 25.0, 45.0)

    # --- DOS Risk ------------------------------------------------------------
    # PUFA as fraction of total superfat FA.  Free (unsaponified) PUFA
    # oxidizes much faster than PUFA locked in soap crystals.
    if total_fa > 0:
        poly_frac = poly / total_fa * 100.0
    else:
        poly_frac = 0.0
    dos_risk = _classify_3(poly_frac, 20.0, 40.0)

    # --- Lather Impact -------------------------------------------------------
    # Free oils suppress foam (they are antifoams).  The impact depends on:
    #   1. Oil fluidity — more unsaturated = more fluid = stronger antifoam
    #   2. Ricinoleic acid — polar hydroxyl group, disproportionate suppression
    #   3. Superfat percentage — more free oil = more suppression
    #   4. Base coupling — lauric/myristic bases solubilize oils aggressively,
    #      partially removing the superfat (and its antifoam effect)
    antifoam = (
        poly * 1.5            # most fluid, strongest antifoam
        + fa.oleic * 1.0      # moderate fluidity
        + fa.ricinoleic * 1.3 # polar, disproportionate foam suppression
        + brittle_sat * 0.6   # melts near body temp, moderate
        + waxy_sat * 0.3      # solid, weakest antifoam (structuring lipids)
        + wax_boost * 0.2     # waxes: minimal foam suppression
    ) / 100.0  # normalize FA percentages to 0-1 scale

    # Scale by superfat %; 5% is the reference point (multiplier = 1.0)
    sf_scale = superfat_pct / 5.0

    lather_score = antifoam * sf_scale * retention

    if lather_score > 1.2:
        lather_impact = "Very High"
    elif lather_score > 0.8:
        lather_impact = "High"
    elif lather_score > 0.4:
        lather_impact = "Moderate"
    else:
        lather_impact = "Low"

    # --- Description ---------------------------------------------------------
    # Combine whichever dimensions score Moderate or above into a narrative.
    parts: list[str] = []
    if film_persistence != "Low":
        if film_persistence == "High":
            parts.append("solid-at-skin-temp fats resist wash-off, leaving a protective barrier")
        else:
            parts.append("moderate film persistence from waxy saturates")
    if emollient_slip != "Low":
        if emollient_slip == "High":
            parts.append("high emollient slip for a silky after-feel")
        else:
            parts.append("moderate emollient slip from liquid oils")
    if dos_risk != "Low":
        if dos_risk == "High":
            parts.append("high DOS risk — consider adding antioxidant (ROE/Vitamin E)")
        else:
            parts.append("moderate DOS risk from polyunsaturated oils")
    if lather_impact in ("High", "Very High"):
        parts.append(f"{lather_impact.lower()} lather suppression from free oils")

    if parts:
        description = "; ".join(parts).capitalize() + "."
    else:
        description = "Low-signal superfat blend with no dominant character."

    return SkinFeel(
        film_persistence=film_persistence,
        emollient_slip=emollient_slip,
        lather_impact=lather_impact,
        dos_risk=dos_risk,
        description=description,
    )
