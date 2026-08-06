import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow
from gui.styles import get_theme_style
from utils.logger import setup_logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "data", "config.json")


def ensure_config():
    """Creates a default config.json if it doesn't exist."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "theme": "light",
            "tokens": [
                {
                    "name": "Default Token",
                    "value": "YOUR_YANDEX_OAUTH_TOKEN_HERE"
                }
            ]
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

def load_tokens():
    """Loads all tokens from config.json."""
    config = load_config()
    tokens_data = config.get("tokens", [])
    tokens = [t.get("value") for t in tokens_data if t.get("value") and t.get("value") != "YOUR_YANDEX_OAUTH_TOKEN_HERE"]
    return tokens

def get_theme() -> str:
    """Gets current saved theme name ('light' or 'dark')."""
    config = load_config()
    return config.get("theme", "light")

def set_theme(theme_name: str):
    """Saves chosen theme to config.json."""
    config = load_config()
    config["theme"] = theme_name
    save_config(config)

def main():
    logger = setup_logger()
    logger.info("Starting Yandex 360 Directory Manager")

    app = QApplication(sys.argv)
    theme = get_theme()
    app.setStyleSheet(get_theme_style(theme))

    config_exists = ensure_config()

    if not config_exists:
        QMessageBox.information(
            None,
            "Первый запуск",
            f"Файл конфигурации создан по пути: {CONFIG_FILE}\nПожалуйста, добавьте ваши OAuth токены Yandex 360 в этот файл и перезапустите приложение."
        )
        return

    tokens = load_tokens()
    if not tokens:
        QMessageBox.warning(
            None,
            "Токены не найдены",
            f"Пожалуйста, добавьте хотя бы один действительный OAuth токен в файл:\n{CONFIG_FILE}"
        )
        return

    window = MainWindow(tokens)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

