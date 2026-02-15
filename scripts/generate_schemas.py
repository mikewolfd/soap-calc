import json
import sys
from pathlib import Path
from typing import List, Type

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from pydantic import TypeAdapter
from soap_calc.models import AdditiveInfo, Oil, Recipe

def generate_schema(model: Type, output_path: Path, is_list: bool = False):
    """Generate and save JSON schema for a model."""
    if is_list:
        adapter = TypeAdapter(List[model])
        schema = adapter.json_schema()
    else:
        schema = model.model_json_schema()
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    print(f"Generated schema: {output_path}")

def main():
    base_dir = Path(__file__).parent.parent
    schemas_dir = base_dir / "schemas"
    schemas_dir.mkdir(exist_ok=True)

    # 1. oils.schema.json (List of Oils)
    generate_schema(Oil, schemas_dir / "oils.schema.json", is_list=True)

    # 2. additives.schema.json (List of AdditiveInfo)
    generate_schema(AdditiveInfo, schemas_dir / "additives.schema.json", is_list=True)

    # 3. recipe.schema.json (Single Recipe)
    generate_schema(Recipe, schemas_dir / "recipe.schema.json", is_list=False)

if __name__ == "__main__":
    main()
