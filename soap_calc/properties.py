"""Soap property prediction from fatty-acid profiles."""

from __future__ import annotations

from typing import List

from soap_calc.models import (
    FattyAcidProfile,
    OilEntry,
    PropertyRating,
    PropertyValue,
    SoapProperties,
    PROPERTY_RANGES,
)


def blend_fatty_acids(oil_entries: List[OilEntry]) -> FattyAcidProfile:
    """Compute a weighted-average fatty-acid profile for a blend of oils.

    Each fatty-acid percentage is weighted by the oil's share (percentage)
    of total oils.

    Args:
        oil_entries (List[OilEntry]): List of oil entries in the recipe.

    Returns:
        FattyAcidProfile: The aggregated fatty acid profile for the blend.
    """
    total_pct = sum(e.percentage for e in oil_entries)
    if total_pct <= 0:
        return FattyAcidProfile()

    lauric = sum(e.oil.fatty_acids.lauric * e.percentage for e in oil_entries) / total_pct
    myristic = sum(e.oil.fatty_acids.myristic * e.percentage for e in oil_entries) / total_pct
    palmitic = sum(e.oil.fatty_acids.palmitic * e.percentage for e in oil_entries) / total_pct
    stearic = sum(e.oil.fatty_acids.stearic * e.percentage for e in oil_entries) / total_pct
    ricinoleic = sum(e.oil.fatty_acids.ricinoleic * e.percentage for e in oil_entries) / total_pct
    oleic = sum(e.oil.fatty_acids.oleic * e.percentage for e in oil_entries) / total_pct
    linoleic = sum(e.oil.fatty_acids.linoleic * e.percentage for e in oil_entries) / total_pct
    linolenic = sum(e.oil.fatty_acids.linolenic * e.percentage for e in oil_entries) / total_pct

    return FattyAcidProfile(
        lauric=round(lauric, 2),
        myristic=round(myristic, 2),
        palmitic=round(palmitic, 2),
        stearic=round(stearic, 2),
        ricinoleic=round(ricinoleic, 2),
        oleic=round(oleic, 2),
        linoleic=round(linoleic, 2),
        linolenic=round(linolenic, 2),
    )


def calculate_iodine(oil_entries: List[OilEntry]) -> float:
    """Weighted-average iodine value of an oil blend.

    Args:
        oil_entries (List[OilEntry]): List of oil entries in the recipe.

    Returns:
        float: The effective iodine value.
    """
    total_pct = sum(e.percentage for e in oil_entries)
    if total_pct <= 0:
        return 0.0
    return round(
        sum(e.oil.iodine * e.percentage for e in oil_entries) / total_pct, 2
    )


def calculate_ins(oil_entries: List[OilEntry]) -> float:
    """Weighted-average INS value of an oil blend.

    Args:
        oil_entries (List[OilEntry]): List of oil entries in the recipe.

    Returns:
        float: The effective INS value.
    """
    total_pct = sum(e.percentage for e in oil_entries)
    if total_pct <= 0:
        return 0.0
    return round(
        sum(e.oil.ins * e.percentage for e in oil_entries) / total_pct, 2
    )


def _rate(val: float, low: float, high: float) -> PropertyRating:
    """Rate a property value against acceptable range boundaries.

    Args:
        val: The property value to rate.
        low: The lower bound of the acceptable range.
        high: The upper bound of the acceptable range.

    Returns:
        PropertyRating: BELOW if val < low, ABOVE if val > high, WITHIN otherwise.
    """
    if val < low:
        return PropertyRating.BELOW
    if val > high:
        return PropertyRating.ABOVE
    return PropertyRating.WITHIN


def _pv(name: str, val: float, low: float, high: float) -> PropertyValue:
    """Create a PropertyValue with rating computed from range boundaries.

    Args:
        name: The property name.
        val: The property value.
        low: The lower bound of the acceptable range.
        high: The upper bound of the acceptable range.

    Returns:
        PropertyValue: A complete property value with computed rating.
    """
    return PropertyValue(
        name=name,
        value=val,
        low=low,
        high=high,
        rating=_rate(val, low, high),
    )


def predict_properties(oil_entries: List[OilEntry]) -> SoapProperties:
    """Predict soap properties from a list of oil entries.

    Generates a full report of hardness, cleansing, conditioning, etc.,
    based on the fatty acid profile of the blend.

    Args:
        oil_entries (List[OilEntry]): List of oil entries in the recipe.

    Returns:
        SoapProperties: The predicted properties.
    """
    fa = blend_fatty_acids(oil_entries)
    iodine = calculate_iodine(oil_entries)
    ins = calculate_ins(oil_entries)

    return SoapProperties(
        hardness=_pv("Hardness", round(fa.hard, 1), *PROPERTY_RANGES["hardness"]),
        cleansing=_pv("Cleansing", round(fa.cleansing, 1), *PROPERTY_RANGES["cleansing"]),
        conditioning=_pv("Conditioning", round(fa.conditioning, 1), *PROPERTY_RANGES["conditioning"]),
        bubbly_lather=_pv("Bubbly Lather", round(fa.bubbly, 1), *PROPERTY_RANGES["bubbly_lather"]),
        creamy_lather=_pv("Creamy Lather", round(fa.creamy, 1), *PROPERTY_RANGES["creamy_lather"]),
        longevity=_pv("Longevity", round(fa.longevity, 1), *PROPERTY_RANGES["longevity"]),
        iodine=_pv("Iodine", iodine, *PROPERTY_RANGES["iodine"]),
        ins=_pv("INS", ins, *PROPERTY_RANGES["ins"]),
    )
