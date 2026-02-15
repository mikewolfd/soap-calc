"""Unit conversion utilities."""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Weight
# ---------------------------------------------------------------------------

_G_PER_OZ = 28.3495
_G_PER_LB = 453.592
_G_PER_KG = 1000.0


def grams_to_ounces(g: float) -> float:
    return g / _G_PER_OZ


def ounces_to_grams(oz: float) -> float:
    return oz * _G_PER_OZ


def grams_to_pounds(g: float) -> float:
    return g / _G_PER_LB


def pounds_to_grams(lb: float) -> float:
    return lb * _G_PER_LB


def grams_to_kilograms(g: float) -> float:
    return g / _G_PER_KG


def kilograms_to_grams(kg: float) -> float:
    return kg * _G_PER_KG


# ---------------------------------------------------------------------------
# Volume
# ---------------------------------------------------------------------------

_ML_PER_FLOZ = 29.5735
_ML_PER_CUP = 236.588


def ml_to_floz(ml: float) -> float:
    return ml / _ML_PER_FLOZ


def floz_to_ml(floz: float) -> float:
    return floz * _ML_PER_FLOZ


def ml_to_cups(ml: float) -> float:
    return ml / _ML_PER_CUP


def cups_to_ml(cups: float) -> float:
    return cups * _ML_PER_CUP


# ---------------------------------------------------------------------------
# Temperature
# ---------------------------------------------------------------------------


def celsius_to_fahrenheit(c: float) -> float:
    return c * 9.0 / 5.0 + 32.0


def fahrenheit_to_celsius(f: float) -> float:
    return (f - 32.0) * 5.0 / 9.0


# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------

_CM_PER_INCH = 2.54


def cm_to_inches(cm: float) -> float:
    return cm / _CM_PER_INCH


def inches_to_cm(inches: float) -> float:
    return inches * _CM_PER_INCH
