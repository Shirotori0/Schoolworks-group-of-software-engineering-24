import json
import os
from ..prompt import prompt

BASE_DIR = "ai/data/prompts"

def load(session_id: str):
    path = os.path.join(BASE_DIR, f"{session_id}.json")

    if not os.path.exists(path):
        return None
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def save(session_id: str, data):
    path = os.path.join(BASE_DIR, f"{session_id}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

