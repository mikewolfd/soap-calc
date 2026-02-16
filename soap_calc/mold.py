"""Mold size calculator — derive batch weight from mold dimensions."""

from __future__ import annotations

from soap_calc.models import MoldSpec, OIL_DENSITY_G_PER_CM3
from soap_calc.units import inches_to_cm


def mold_from_inches(
    length: float,
    width: float,
    height: float,
    fill_factor: float = 0.95,
) -> MoldSpec:
    """Create a :class:`MoldSpec` from inch measurements.

    Args:
        length (float): Length in inches.
        width (float): Width in inches.
        height (float): Height in inches.
        fill_factor (float, optional): Percentage of mold volume to fill (0.0-1.0). Defaults to 0.95.

    Returns:
        MoldSpec: The resulting mold specification with dimensions converted to cm.
    """
    return MoldSpec(
        length=inches_to_cm(length),
        width=inches_to_cm(width),
        height=inches_to_cm(height),
        fill_factor=fill_factor,
    )


def batch_weight_for_mold(mold: MoldSpec) -> float:
    """Return the target **total batch weight** (grams) for a given mold.

    Estimated from oil weight (approx 65% of batch).

    Args:
        mold (MoldSpec): The mold estimation parameters.

    Returns:
        float: Estimated total batch weight in grams.
    """
    return round(mold.estimated_batch_weight, 1)


def oil_weight_for_mold(mold: MoldSpec) -> float:
    """Estimate target **oil weight** from mold size.

    Uses defined oil density (approx 0.692 g/cm³).

    Args:
        mold (MoldSpec): The mold estimation parameters.

    Returns:
        float: Estimated oil weight in grams.
    """
    return round(mold.volume * mold.fill_factor * OIL_DENSITY_G_PER_CM3, 1)
