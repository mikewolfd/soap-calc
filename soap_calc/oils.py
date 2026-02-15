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


from pydantic import ValidationError

# ... (imports)

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
                        oil = Oil.model_validate(item)
                        oils[oil.name.lower()] = oil
                    except (KeyError, ValueError, ValidationError) as e:
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
                        oil = Oil.model_validate(item)
                        oils[oil.name.lower()] = oil  # Overrides built-ins if name matches
                    except (KeyError, ValueError, ValidationError) as e:
                        logger.warning(f"Skipping invalid user oil: {e}")
        except Exception as e:
            logger.warning(f"Failed to load user oils from {user_path}: {e}")

    _OILS_CACHE = oils
    return oils


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

