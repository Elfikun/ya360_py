import json
import os
from typing import Dict, Any

CACHE_FILE = "data/deleted_cache.json"

def ensure_cache_file():
    """Ensures that the cache directory and file exist."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)

def load_cache() -> Dict[str, Any]:
    """Loads the deleted cache from the JSON file."""
    ensure_cache_file()
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_cache(data: Dict[str, Any]):
    """Saves the given data to the deleted cache JSON file."""
    ensure_cache_file()
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_to_cache(user_id: str, user_data: Dict[str, Any]):
    """Adds a user to the deleted cache."""
    cache = load_cache()
    cache[user_id] = user_data
    save_cache(cache)

def remove_from_cache(user_id: str):
    """Removes a user from the deleted cache."""
    cache = load_cache()
    if user_id in cache:
        del cache[user_id]
        save_cache(cache)
