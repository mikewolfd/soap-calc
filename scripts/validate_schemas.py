
import json
import jsonschema
from jsonschema import validate, ValidationError
from pathlib import Path

def validate_file(data_file_path, schema_file_path):
    print(f"Validating {data_file_path} against {schema_file_path}...")
    try:
        data_path = Path(data_file_path)
        schema_path = Path(schema_file_path)
        
        if not data_path.exists():
            print(f"Schema Error: Data file not found: {data_file_path}")
            return
            
        if not schema_path.exists():
            print(f"Schema Error: Schema file not found: {schema_file_path}")
            return

        with open(data_path, 'r') as f:
            data = json.load(f)
            
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        validate(instance=data, schema=schema)
        print("✅ Validation Successful!")
    except ValidationError as e:
        print(f"❌ Validation Failed: {e.message}")
        print(f"Path: {e.path}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print("-" * 30)

if __name__ == "__main__":
    # Assume script is in scripts/ directory, so project root is parent
    base_dir = Path(__file__).parent.parent
    
    # 1. Validate Oils Database
    validate_file(base_dir / "data/oils.json", base_dir / "schemas/oils.schema.json")
    
    # 2. Validate Additives Database
    validate_file(base_dir / "data/additives.json", base_dir / "schemas/additives.schema.json")
    
    # 3. Validate Example Recipe
    validate_file(base_dir / "examples/beginner_3oil.json", base_dir / "schemas/recipe.schema.json")
