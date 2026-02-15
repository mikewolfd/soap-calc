"""Fragrance calculator with EO safety data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from soap_calc.models import Fragrance, FragranceType


# ---------------------------------------------------------------------------
# EO safety database (IFRA max % for leave-on / rinse-off products)
# Values are approximate maximums for rinse-off products (like soap).
# ---------------------------------------------------------------------------

# name -> max safe usage rate as % of total product weight
_EO_MAX_RATES: Dict[str, float] = {
    "cedarwood": 5.0,
    "chamomile": 4.0,
    "cinnamon bark": 0.5,
    "cinnamon leaf": 1.0,
    "citronella": 3.0,
    "clary sage": 5.0,
    "clove bud": 0.5,
    "eucalyptus": 5.0,
    "frankincense": 5.0,
    "geranium": 3.0,
    "ginger": 3.0,
    "grapefruit": 4.0,
    "lavender": 5.0,
    "lemon": 3.0,
    "lemongrass": 2.0,
    "lime": 2.0,
    "orange": 5.0,
    "oregano": 0.5,
    "patchouli": 5.0,
    "peppermint": 3.0,
    "rosemary": 4.0,
    "rosewood": 5.0,
    "spearmint": 3.0,
    "tea tree": 3.0,
    "thyme": 1.0,
    "vetiver": 5.0,
    "wintergreen": 1.0,
    "ylang ylang": 3.0,
}


def get_eo_max_rate(name: str) -> Optional[float]:
    """Return the max safe usage rate (%) for an essential oil, or None."""
    return _EO_MAX_RATES.get(name.lower())


def list_eo_rates() -> Dict[str, float]:
    """Return the full EO safety rate dictionary."""
    return dict(sorted(_EO_MAX_RATES.items()))


# ---------------------------------------------------------------------------
# Fragrance calculation
# ---------------------------------------------------------------------------

# Default rates: % of oil weight
_DEFAULT_FO_RATE = 5.0   # fragrance oil: 5% of oil weight
_DEFAULT_EO_RATE = 3.0   # essential oil: 3% of oil weight (if no specific max)


@dataclass
class FragranceResult:
    """Computed fragrance amount with optional safety warning."""

    name: str
    fragrance_type: FragranceType
    amount: float           # grams
    rate_used: float        # percentage applied
    max_safe_pct: Optional[float] = None
    warning: Optional[str] = None


def calculate_fragrance(
    fragrance: Fragrance,
    total_oil_weight: float,
) -> FragranceResult:
    """Calculate the weight for a fragrance entry.

    If the fragrance already has an ``amount`` set, it is used directly.
    Otherwise, if ``percentage`` is set, it is applied to *total_oil_weight*.
    Otherwise, default rates are used (5 % for FO, 3 % for EO).
    """
    max_safe = fragrance.max_safe_pct
    if max_safe is None and fragrance.fragrance_type == FragranceType.ESSENTIAL_OIL:
        max_safe = get_eo_max_rate(fragrance.name)

    # Determine rate
    if fragrance.amount is not None:
        amount = fragrance.amount
        rate = (amount / total_oil_weight * 100.0) if total_oil_weight > 0 else 0.0
    elif fragrance.percentage is not None:
        rate = fragrance.percentage
        amount = total_oil_weight * rate / 100.0
    else:
        if fragrance.fragrance_type == FragranceType.ESSENTIAL_OIL:
            rate = min(_DEFAULT_EO_RATE, max_safe) if max_safe else _DEFAULT_EO_RATE
        else:
            rate = _DEFAULT_FO_RATE
        amount = total_oil_weight * rate / 100.0

    # Safety check
    warning = None
    if max_safe is not None and rate > max_safe:
        warning = (
            f"{fragrance.name}: usage rate {rate:.1f}% exceeds max safe rate "
            f"of {max_safe:.1f}% for rinse-off products."
        )

    return FragranceResult(
        name=fragrance.name,
        fragrance_type=fragrance.fragrance_type,
        amount=round(amount, 2),
        rate_used=round(rate, 2),
        max_safe_pct=max_safe,
        warning=warning,
    )
