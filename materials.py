import csv
import os
import sys
from utils import log_error # Use your global logger instead of pure prints

# --- NEW: PyInstaller Path Fix ---
if getattr(sys, 'frozen', False):
    # If running as a built .exe, look in the folder where the .exe is actually sitting
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # If running normally in VS Code/PyCharm, look in the script's folder
    BASE_DIR = os.path.dirname(__file__)

MATERIALS_CSV = os.path.join(BASE_DIR, "materials.csv")

def load_materials():
    """Load materials from CSV file into a dictionary."""
    materials = {}
    try:
        with open(MATERIALS_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            expected_headers = {'code', 'name', 'price'}
            
            if not expected_headers.issubset(reader.fieldnames or []):
                raise ValueError(f"CSV headers must include: {expected_headers}")
            
            for row in reader:
                raw_code = row["code"].strip()
                name = row["name"].strip()
                
                # Normalize code
                if raw_code.isdigit():
                    code = str(int(raw_code))
                else:
                    code = raw_code.upper()
                
                # Validate and parse price
                try:
                    price = float(row["price"].strip())
                except (ValueError, KeyError):
                    print(f"[WARN] Skipping material with invalid price: {row}")
                    continue
                
                # Skip empty codes or names
                if not code or not name:
                    print(f"[WARN] Skipping material with empty code or name: {row}")
                    continue
                
                # Warn about duplicates but don't skip
                if code in materials:
                    print(f"[WARN] Duplicate code in materials.csv: {code}")
                
                materials[code] = {"name": name, "price": price}
                
    except FileNotFoundError:
        log_error("Materials Load", f"'materials.csv' not found at {MATERIALS_CSV}")
    except Exception as e:
        log_error("Materials Load", f"Failed to load materials: {e}")
    
    return materials

def reload_materials():
    """Call this function to refresh prices while the app is running."""
    global materials_dict
    materials_dict = load_materials()
    print(f"[INFO] Materials reloaded successfully. Total items: {len(materials_dict)}")

# Load materials for the first time at module import
reload_materials()

def get_material_by_code(code):
    """Get material details by code."""
    if not code:
        return None
    
    # Normalize the input code exactly like we do on load
    key = str(code).strip()
    if key.isdigit():
        key = str(int(key))
    else:
        key = key.upper()
    
    return materials_dict.get(key)