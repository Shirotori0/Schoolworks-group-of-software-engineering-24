import os
import json

BASE_DIR = "ai/data/character_scripts"
def save_script(script_name: str, script):
    script_path = os.path.join(BASE_DIR, f"{script_name}.json")

    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=4)

def load_script(script_path: str):
    
    if not os.path.exists(script_path):
        return None
    
    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)
    return script