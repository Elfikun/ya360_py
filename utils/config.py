import os
import sys
import json


def _get_base_dir() -> str:
    """Returns the base directory for data files.

    When running as a PyInstaller --onefile bundle, sys.executable points to
    the .exe itself, so we use its parent directory.  When running as a plain
    Python script we fall back to the project root (two levels up from this
    file).
    """
    if getattr(sys, 'frozen', False):
        # Packaged: place data/ next to the .exe
        return os.path.dirname(sys.executable)
    # Development: project root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = _get_base_dir()
CONFIG_FILE = os.path.join(BASE_DIR, "data", "config.json")


def ensure_config():
    """Creates a default config.json if it doesn't exist."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "theme": "light",
            "passwork_url": "https://your-passwork-domain.com",
            "passwork_api_token": "YOUR_PASSWORK_API_TOKEN_HERE",
            "passwork_search_tag": "yandex-360-token"
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        return False # Indicated it was newly created
    return True

def load_config() -> dict:
    """Loads configuration dictionary from config.json."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return {}

def save_config(config_data: dict):
    """Saves configuration dictionary to config.json."""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")

def load_passwork_settings():
    """Loads Passwork connection settings from config.json."""
    config = load_config()
    return {
        "passwork_url": config.get("passwork_url"),
        "passwork_api_token": config.get("passwork_api_token"),
        "passwork_search_tag": config.get("passwork_search_tag", "yandex-360-token")
    }

def get_theme() -> str:
    """Gets current saved theme name ('light' or 'dark')."""
    config = load_config()
    return config.get("theme", "light")

def set_theme(theme_name: str):
    """Saves chosen theme to config.json."""
    config = load_config()
    config["theme"] = theme_name
    save_config(config)
