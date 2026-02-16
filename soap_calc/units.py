"""Unit conversion utilities."""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Weight
# ---------------------------------------------------------------------------

_G_PER_OZ = 28.3495
_G_PER_LB = 453.592
_G_PER_KG = 1000.0


def grams_to_ounces(g: float) -> float:
    """Convert grams to ounces.

    Args:
        g: Weight in grams.

    Returns:
        Weight in ounces.
    """
    return g / _G_PER_OZ


def ounces_to_grams(oz: float) -> float:
    """Convert ounces to grams.

    Args:
        oz: Weight in ounces.

    Returns:
        Weight in grams.
    """
    return oz * _G_PER_OZ


def grams_to_pounds(g: float) -> float:
    """Convert grams to pounds.

    Args:
        g: Weight in grams.

    Returns:
        Weight in pounds.
    """
    return g / _G_PER_LB


def pounds_to_grams(lb: float) -> float:
    """Convert pounds to grams.

    Args:
        lb: Weight in pounds.

    Returns:
        Weight in grams.
    """
    return lb * _G_PER_LB


def grams_to_kilograms(g: float) -> float:
    """Convert grams to kilograms.

    Args:
        g: Weight in grams.

    Returns:
        Weight in kilograms.
    """
    return g / _G_PER_KG


def kilograms_to_grams(kg: float) -> float:
    """Convert kilograms to grams.

    Args:
        kg: Weight in kilograms.

    Returns:
        Weight in grams.
    """
    return kg * _G_PER_KG


# ---------------------------------------------------------------------------
# Volume
# ---------------------------------------------------------------------------

_ML_PER_FLOZ = 29.5735
_ML_PER_CUP = 236.588


def ml_to_floz(ml: float) -> float:
    """Convert milliliters to fluid ounces.

    Args:
        ml: Volume in milliliters.

    Returns:
        Volume in fluid ounces.
    """
    return ml / _ML_PER_FLOZ


def floz_to_ml(floz: float) -> float:
    """Convert fluid ounces to milliliters.

    Args:
        floz: Volume in fluid ounces.

    Returns:
        Volume in milliliters.
    """
    return floz * _ML_PER_FLOZ


def ml_to_cups(ml: float) -> float:
    """Convert milliliters to cups.

    Args:
        ml: Volume in milliliters.

    Returns:
        Volume in cups.
    """
    return ml / _ML_PER_CUP


def cups_to_ml(cups: float) -> float:
    """Convert cups to milliliters.

    Args:
        cups: Volume in cups.

    Returns:
        Volume in milliliters.
    """
    return cups * _ML_PER_CUP


# ---------------------------------------------------------------------------
# Temperature
# ---------------------------------------------------------------------------


def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit.

    Args:
        c: Temperature in Celsius.

    Returns:
        Temperature in Fahrenheit.
    """
    return c * 9.0 / 5.0 + 32.0


def fahrenheit_to_celsius(f: float) -> float:
    """Convert Fahrenheit to Celsius.

    Args:
        f: Temperature in Fahrenheit.

    Returns:
        Temperature in Celsius.
    """
    return (f - 32.0) * 5.0 / 9.0


# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------

_CM_PER_INCH = 2.54


def cm_to_inches(cm: float) -> float:
    """Convert centimeters to inches.

    Args:
        cm: Length in centimeters.

    Returns:
        Length in inches.
    """
    return cm / _CM_PER_INCH


def inches_to_cm(inches: float) -> float:
    """Convert inches to centimeters.

    Args:
        inches: Length in inches.

    Returns:
        Length in centimeters.
    """
    return inches * _CM_PER_INCH
