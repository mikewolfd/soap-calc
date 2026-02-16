"""Recipe serialization (JSON / YAML) and scaling."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from soap_calc.models import (
    Additive,
    Fragrance,
    FragranceType,
    Liquid,
    LyeType,
    MoldSpec,
    Oil,
    OilEntry,
    PercentBase,
    Recipe,
    Stage,
    WaterCalculationMode,
    FattyAcidProfile,
)
from soap_calc.oils import get_oil


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def _oil_entry_to_dict(entry: OilEntry) -> Dict[str, Any]:
    """Convert an OilEntry to a dictionary for serialization.

    Args:
        entry: The oil entry to serialize.

    Returns:
        Dictionary with 'oil' name and 'percentage' fields.
    """
    return {"oil": entry.oil.name, "percentage": entry.percentage}


def _liquid_to_dict(liq: Liquid) -> Dict[str, Any]:
    """Convert a Liquid to a dictionary for serialization.

    Args:
        liq: The liquid to serialize.

    Returns:
        Dictionary with liquid name, percentage, and optional handling notes.
    """
    d: Dict[str, Any] = {"name": liq.name, "percentage": liq.percentage}
    if liq.handling_notes:
        d["handling_notes"] = liq.handling_notes
    return d


def _additive_to_dict(add: Additive) -> Dict[str, Any]:
    """Convert an Additive to a dictionary for serialization.

    Args:
        add: The additive to serialize.

    Returns:
        Dictionary with additive name, amount/percentage, percent base, stage, and optional notes.
    """
    d: Dict[str, Any] = {"name": add.name}
    if add.amount is not None:
        d["amount"] = add.amount
    if add.percentage is not None:
        d["percentage"] = add.percentage
    d["percent_base"] = add.percent_base.value
    d["stage"] = add.stage.value
    if add.notes:
        d["notes"] = add.notes
    return d


def _fragrance_to_dict(frag: Fragrance) -> Dict[str, Any]:
    """Convert a Fragrance to a dictionary for serialization.

    Args:
        frag: The fragrance to serialize.

    Returns:
        Dictionary with fragrance name, type, amount/percentage, safety limit, stage, and optional notes.
    """
    d: Dict[str, Any] = {
        "name": frag.name,
        "type": frag.fragrance_type.value,
    }
    if frag.amount is not None:
        d["amount"] = frag.amount
    if frag.percentage is not None:
        d["percentage"] = frag.percentage
    if frag.max_safe_pct is not None:
        d["max_safe_pct"] = frag.max_safe_pct
    d["stage"] = frag.stage.value
    if frag.notes:
        d["notes"] = frag.notes
    return d


def _mold_to_dict(mold: MoldSpec) -> Dict[str, Any]:
    """Convert a MoldSpec to a dictionary for serialization.

    Args:
        mold: The mold specification to serialize.

    Returns:
        Dictionary with mold dimensions (length_cm, width_cm, height_cm) and optional fill_factor.
    """
    d: Dict[str, Any] = {
        "length_cm": mold.length,
        "width_cm": mold.width,
        "height_cm": mold.height,
    }
    if mold.fill_factor != 0.95:
        d["fill_factor"] = mold.fill_factor
    return d


def recipe_to_dict(recipe: Recipe) -> Dict[str, Any]:
    """Convert a :class:`Recipe` to a plain dictionary.

    Args:
        recipe: The recipe object to serialize.

    Returns:
        A dictionary representation suitable for JSON/YAML serialization.
    """
    d: Dict[str, Any] = {
        "name": recipe.name,
        "lye_type": recipe.lye_type.value,
        "naoh_ratio": recipe.naoh_ratio,
        "naoh_purity": recipe.naoh_purity,
        "koh_purity": recipe.koh_purity,
        "superfat_pct": recipe.superfat_pct,
        "water_mode": recipe.water_mode.value,
        "water_value": recipe.water_value,
        "liquid_discount_pct": recipe.liquid_discount_pct,
        "oils": [_oil_entry_to_dict(e) for e in recipe.oils],
        "liquids": [_liquid_to_dict(liq) for liq in recipe.liquids],
        "additives": [_additive_to_dict(a) for a in recipe.additives],
        "fragrances": [_fragrance_to_dict(frag) for frag in recipe.fragrances],
    }
    if recipe.total_oil_weight is not None:
        d["total_oil_weight"] = recipe.total_oil_weight
    if recipe.base_oil_weight is not None:
        d["base_oil_weight"] = recipe.base_oil_weight
    # If neither was explicitly set, emit total_oil_weight for explicitness
    if recipe.total_oil_weight is None and recipe.base_oil_weight is None:
        d["total_oil_weight"] = recipe.resolve_oil_weight()
    if recipe.superfat_oils:
        d["superfat_oils"] = [_oil_entry_to_dict(e) for e in recipe.superfat_oils]
    if recipe.mold is not None:
        d["mold"] = _mold_to_dict(recipe.mold)
    if recipe.ignore_warnings:
        d["ignore_warnings"] = recipe.ignore_warnings
    if recipe.description:
        d["description"] = recipe.description
    if recipe.notes:
        d["notes"] = recipe.notes
    return d


def _parse_oil_entry(data: Dict[str, Any]) -> OilEntry:
    """Parse a dictionary into an OilEntry object.

    Args:
        data: Dictionary containing 'oil' name and 'percentage' fields.

    Returns:
        An OilEntry object with the oil from the database or a minimal Oil if not found.
    """
    oil_name = data["oil"]
    oil = get_oil(oil_name)
    if oil is None:
        # Create a minimal Oil if not in the database
        oil = Oil(
            name=oil_name,
            sap_naoh=data.get("sap_naoh", 0.135),
            sap_koh=data.get("sap_koh", 0.19),
            fatty_acids=FattyAcidProfile(),
        )
    return OilEntry(oil=oil, percentage=data["percentage"])


def _parse_liquid(data: Dict[str, Any]) -> Liquid:
    """Parse a dictionary into a Liquid object.

    Args:
        data: Dictionary containing liquid 'name', optional 'percentage', and 'handling_notes'.

    Returns:
        A Liquid object.
    """
    return Liquid(
        name=data["name"],
        percentage=data.get("percentage", 100.0),
        handling_notes=data.get("handling_notes", ""),
    )


def _parse_additive(data: Dict[str, Any]) -> Additive:
    """Parse a dictionary into an Additive object.

    Args:
        data: Dictionary containing additive fields (name, amount, percentage, percent_base, stage, notes).

    Returns:
        An Additive object.
    """
    return Additive(
        name=data["name"],
        amount=data.get("amount"),
        percentage=data.get("percentage"),
        percent_base=PercentBase(data.get("percent_base", PercentBase.OIL_WEIGHT.value)),
        stage=Stage(data.get("stage", Stage.LIGHT_TRACE.value)),
        notes=data.get("notes", ""),
    )


def _parse_fragrance(data: Dict[str, Any]) -> Fragrance:
    """Parse a dictionary into a Fragrance object.

    Args:
        data: Dictionary containing fragrance fields (name, type, amount, percentage, max_safe_pct, stage, notes).

    Returns:
        A Fragrance object.
    """
    return Fragrance(
        name=data["name"],
        fragrance_type=FragranceType(data.get("type", FragranceType.FRAGRANCE_OIL.value)),
        amount=data.get("amount"),
        percentage=data.get("percentage"),
        max_safe_pct=data.get("max_safe_pct"),
        stage=Stage(data.get("stage", Stage.LIGHT_TRACE.value)),
        notes=data.get("notes", ""),
    )


def _parse_mold(data: Dict[str, Any]) -> MoldSpec:
    """Parse a dictionary into a MoldSpec object.

    Args:
        data: Dictionary containing mold dimensions (length_cm, width_cm, height_cm) and optional fill_factor.

    Returns:
        A MoldSpec object.
    """
    return MoldSpec(
        length=data["length_cm"],
        width=data["width_cm"],
        height=data["height_cm"],
        fill_factor=data.get("fill_factor", 0.95),
    )


def dict_to_recipe(data: Dict[str, Any]) -> Recipe:
    """Build a :class:`Recipe` from a plain dictionary.

    Args:
        data: The dictionary data (e.g., loaded from JSON).

    Returns:
        The reconstructed Recipe object.
    """
    mold_data = data.get("mold")
    
    wc_mode_str = data.get("water_mode", WaterCalculationMode.WATER_LYE_RATIO.value)
    val = float(data.get("water_value", 2.0))
    mode = WaterCalculationMode(wc_mode_str)

    return Recipe(
        name=data.get("name", "Untitled Recipe"),
        description=data.get("description", ""),
        lye_type=LyeType(data.get("lye_type", LyeType.NAOH.value)),
        naoh_ratio=data.get("naoh_ratio", 100.0),
        naoh_purity=data.get("naoh_purity", 100.0),
        koh_purity=data.get("koh_purity", 90.0),
        superfat_pct=data.get("superfat_pct", 5.0),
        water_mode=mode,
        water_value=val,
        liquid_discount_pct=data.get("liquid_discount_pct", 0.0),
        oils=[_parse_oil_entry(o) for o in data.get("oils", [])],
        liquids=[_parse_liquid(l) for l in data.get("liquids", [{"name": "Water"}])],
        additives=[_parse_additive(a) for a in data.get("additives", [])],
        fragrances=[_parse_fragrance(f) for f in data.get("fragrances", [])],
        superfat_oils=[_parse_oil_entry(o) for o in data.get("superfat_oils", [])],
        total_oil_weight=data.get("total_oil_weight"),
        base_oil_weight=data.get("base_oil_weight"),
        mold=_parse_mold(mold_data) if mold_data else None,
        ignore_warnings=data.get("ignore_warnings", []),
        notes=data.get("notes", ""),
    )


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------


def save_recipe(
    recipe: Recipe,
    path: Union[str, Path],
    fmt: Optional[str] = None,
) -> None:
    """Serialize a recipe to a JSON or YAML file.

    Args:
        recipe: The recipe to save.
        path: Destination file path.
        fmt: Format ('json' or 'yaml'). If None, inferred from extension.
    """
    path = Path(path)
    if fmt is None:
        ext = path.suffix.lower()
        if ext in (".yml", ".yaml"):
            fmt = "yaml"
        else:
            fmt = "json"

    data = recipe_to_dict(recipe)
    with open(path, "w", encoding="utf-8") as fh:
        if fmt == "yaml":
            yaml.dump(data, fh, default_flow_style=False, sort_keys=False)
        else:
            json.dump(data, fh, indent=2, ensure_ascii=False)


def load_recipe(path: Union[str, Path]) -> Recipe:
    """Load a recipe from a JSON or YAML file.

    Args:
        path: Path to the recipe file.

    Returns:
        The loaded recipe object.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If JSON parsing fails.
        yaml.YAMLError: If YAML parsing fails.
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as fh:
        ext = path.suffix.lower()
        if ext in (".yml", ".yaml"):
            data = yaml.safe_load(fh)
        else:
            data = json.load(fh)
    return dict_to_recipe(data)


# ---------------------------------------------------------------------------
# Scaling
# ---------------------------------------------------------------------------


def scale_recipe(recipe: Recipe, target_oil_weight: float) -> Recipe:
    """Return a new recipe scaled to *target_oil_weight* (total oils).

    Because oils are stored as percentages the ratios stay the same —
    only the batch size changes.  Additive *amounts* (absolute grams)
    are scaled proportionally; percentage-based additives scale
    automatically.

    Args:
        recipe: The original recipe to scale.
        target_oil_weight: The new target total oil weight in grams.

    Returns:
        A new Recipe object with scaled amounts.
    """
    current = recipe.resolve_oil_weight()
    factor = target_oil_weight / current if current > 0 else 1.0
    new = copy.deepcopy(recipe)

    # Set total explicitly and clear core / mold so they don't conflict
    new.total_oil_weight = target_oil_weight
    new.base_oil_weight = None
    new.mold = None  # Clear mold so it doesn't override the scaled weight

    for add in new.additives:
        if add.amount is not None:
            add.amount = round(add.amount * factor, 2)
    for frag in new.fragrances:
        if frag.amount is not None:
            frag.amount = round(frag.amount * factor, 2)
    return new
