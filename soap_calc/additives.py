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


from pydantic import ValidationError

# ... (imports)

def _load_additives() -> Dict[str, AdditiveInfo]:
    """Load additives from the package data and user config directory.

    Loads additives from both the built-in data/additives.json and user-defined
    ~/.soap_calc/additives.json files. Results are cached globally.

    Returns:
        Dict[str, AdditiveInfo]: Dictionary mapping lowercase additive names to AdditiveInfo objects.
    """
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
                        entry = AdditiveInfo.model_validate(item)
                        additives[entry.name.lower()] = entry
                    except (KeyError, ValueError, ValidationError) as e:
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
                        entry = AdditiveInfo.model_validate(item)
                        additives[entry.name.lower()] = entry
                    except (KeyError, ValueError, ValidationError) as e:
                        logger.warning(f"Skipping invalid user additive: {e}")
        except Exception as e:
            logger.warning(f"Failed to load user additives from {user_path}: {e}")

    _ADDITIVES_CACHE = additives
    return additives


def get_additive(name: str) -> Optional[AdditiveInfo]:
    """Retrieve an additive by name (case-insensitive).

    Args:
        name: The name of the additive to find.

    Returns:
        The AdditiveInfo object if found, else None.
    """
    additives = _load_additives()
    return additives.get(name.lower())


def list_additives() -> List[AdditiveInfo]:
    """List all available additives sorted by name.

    Returns:
        A list of all loaded AdditiveInfo objects.
    """
    additives = _load_additives()
    return sorted(additives.values(), key=lambda a: a.name.lower())


def search_additives(query: str) -> List[AdditiveInfo]:
    """Search for additives with names matching the query (case-insensitive).

    Args:
        query: The substring to search for.

    Returns:
        A list of matching AdditiveInfo objects, sorted by name.
    """
    additives = _load_additives()
    q = query.lower()
    matches = [a for name, a in additives.items() if q in name]
    return sorted(matches, key=lambda a: a.name.lower())
