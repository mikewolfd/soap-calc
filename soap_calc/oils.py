"""Oil database loading and searching functions."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from soap_calc.models import FattyAcidProfile, Oil

logger = logging.getLogger(__name__)

# Cache loaded oils
_OILS_CACHE: Optional[Dict[str, Oil]] = None


def _load_oils() -> Dict[str, Oil]:
    """Load oils from the package data and user config directory."""
    global _OILS_CACHE
    if _OILS_CACHE is not None:
        return _OILS_CACHE

    oils: Dict[str, Oil] = {}

    # 1. Load built-in oils
    # Try to find data/oils.json relative to this file
    base_dir = Path(__file__).parent.parent
    data_path = base_dir / "data" / "oils.json"
    
    if data_path.exists():
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    try:
                        oil = _parse_oil(item)
                        oils[oil.name.lower()] = oil
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Skipping invalid oil entry in data: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {data_path}: {e}")
    else:
        logger.warning(f"Oil database not found at {data_path}")

    # 2. Load user-defined oils
    user_path = Path.home() / ".soap_calc" / "oils.json"
    if user_path.exists():
        try:
            with open(user_path, "r", encoding="utf-8") as f:
                user_data = json.load(f)
                for item in user_data:
                    try:
                        oil = _parse_oil(item)
                        oils[oil.name.lower()] = oil  # Overrides built-ins if name matches
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Skipping invalid user oil: {e}")
        except Exception as e:
            logger.warning(f"Failed to load user oils from {user_path}: {e}")

    _OILS_CACHE = oils
    return oils


def _parse_oil(data: dict) -> Oil:
    """Parse a dictionary into an Oil object."""
    fa = data.get("fatty_acids", {})
    
    # Construct FattyAcidProfile, defaulting missing acids to 0.0
    profile = FattyAcidProfile(
        lauric=float(fa.get("lauric", 0.0)),
        myristic=float(fa.get("myristic", 0.0)),
        palmitic=float(fa.get("palmitic", 0.0)),
        stearic=float(fa.get("stearic", 0.0)),
        ricinoleic=float(fa.get("ricinoleic", 0.0)),
        oleic=float(fa.get("oleic", 0.0)),
        linoleic=float(fa.get("linoleic", 0.0)),
        linolenic=float(fa.get("linolenic", 0.0)),
    )
    
    return Oil(
        name=data["name"],
        sap_naoh=float(data.get("sap_naoh", 0.0)),
        sap_koh=float(data.get("sap_koh", 0.0)),
        fatty_acids=profile,
        iodine=float(data.get("iodine", 0.0)),
        ins=float(data.get("ins", 0.0)),
        notes=data.get("notes", ""),
    )


def get_oil(name: str) -> Optional[Oil]:
    """Retrieve an oil by name (case-insensitive)."""
    oils = _load_oils()
    return oils.get(name.lower())


def list_oils() -> List[Oil]:
    """List all available oils sorted by name."""
    oils = _load_oils()
    return sorted(oils.values(), key=lambda o: o.name.lower())


def search_oils(query: str) -> List[Oil]:
    """Search for oils with names matching the query (case-insensitive)."""
    oils = _load_oils()
    q = query.lower()
    matches = [o for name, o in oils.items() if q in name]
    return sorted(matches, key=lambda o: o.name.lower())

# Common oils exported for convenience
def _require_oil(name: str) -> Oil:
    oil = get_oil(name)
    if not oil:
        # Fallback for testing/initialization if DB is missing items
        return Oil(name=name, sap_naoh=0.0, sap_koh=0.0, fatty_acids=FattyAcidProfile())
    return oil

OLIVE_OIL = _require_oil("Olive Oil")
COCONUT_OIL_76 = _require_oil("Coconut Oil, 76 deg")
SHEA_BUTTER = _require_oil("Shea Butter")
CASTOR_OIL = _require_oil("Castor Oil")
PALM_OIL = _require_oil("Palm Oil")
