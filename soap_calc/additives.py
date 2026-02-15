"""Additive database loading and searching functions."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from soap_calc.models import AdditiveInfo, AdditiveUsage, Stage

logger = logging.getLogger(__name__)

# Cache loaded additives
_ADDITIVES_CACHE: Optional[Dict[str, AdditiveInfo]] = None


def _parse_stage(stage_str: str) -> str:
    """Normalize stage string from JSON."""
    s = stage_str.lower().strip()
    if s == "lye":
        return Stage.LYE_LIQUID.value
    elif s == "trace":
        return Stage.LIGHT_TRACE.value
    elif s == "pre_cook":
        return Stage.OIL_PHASE.value
    elif s == "post_cook":
        return Stage.POST_COOK.value
    return s


def _load_additives() -> Dict[str, AdditiveInfo]:
    """Load additives from the package data and user config directory."""
    global _ADDITIVES_CACHE
    if _ADDITIVES_CACHE is not None:
        return _ADDITIVES_CACHE

    additives: Dict[str, AdditiveInfo] = {}

    # 1. Load built-in additives
    base_dir = Path(__file__).parent.parent
    data_path = base_dir / "data" / "additives.json"
    
    if data_path.exists():
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    try:
                        entry = _parse_additive_entry(item)
                        additives[entry.name.lower()] = entry
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Skipping invalid additive entry: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {data_path}: {e}")
    else:
        logger.warning(f"Additive database not found at {data_path}")

    # 2. Load user-defined additives
    user_path = Path.home() / ".soap_calc" / "additives.json"
    if user_path.exists():
        try:
            with open(user_path, "r", encoding="utf-8") as f:
                user_data = json.load(f)
                for item in user_data:
                    try:
                        entry = _parse_additive_entry(item)
                        additives[entry.name.lower()] = entry
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Skipping invalid user additive: {e}")
        except Exception as e:
            logger.warning(f"Failed to load user additives from {user_path}: {e}")

    _ADDITIVES_CACHE = additives
    return additives


def _parse_additive_entry(data: dict) -> AdditiveInfo:
    """Parse a dictionary into an AdditiveInfo object."""
    usage_data = data.get("usage", {})
    usage = AdditiveUsage(
        min=float(usage_data.get("min", 0.0)),
        max=float(usage_data.get("max", 0.0)),
        unit=usage_data.get("unit", ""),
        per=usage_data.get("per", "")
    )
    
    return AdditiveInfo(
        name=data["name"],
        category=data.get("category", "additive"),
        usage=usage,
        stage=_parse_stage(data.get("stage", "")),
        purpose=data.get("purpose", ""),
        lye_adjustment=float(data.get("lye_adjustment", 0.0)),
        notes=data.get("notes", ""),
    )


def get_additive(name: str) -> Optional[AdditiveInfo]:
    """Retrieve an additive by name (case-insensitive)."""
    additives = _load_additives()
    return additives.get(name.lower())


def list_additives() -> List[AdditiveInfo]:
    """List all available additives sorted by name."""
    additives = _load_additives()
    return sorted(additives.values(), key=lambda a: a.name.lower())


def search_additives(query: str) -> List[AdditiveInfo]:
    """Search for additives with names matching the query (case-insensitive)."""
    additives = _load_additives()
    q = query.lower()
    matches = [a for name, a in additives.items() if q in name]
    return sorted(matches, key=lambda a: a.name.lower())
