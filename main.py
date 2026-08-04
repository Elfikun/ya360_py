import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow
from gui.styles import MAIN_STYLE
from utils.logger import setup_logger

CONFIG_FILE = "data/config.json"

def ensure_config():
    """Creates a default config.json if it doesn't exist."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "tokens": [
                {
                    "name": "Default Token",
                    "value": "YOUR_YANDEX_OAUTH_TOKEN_HERE"
                }
            ]
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        return False # Indicated it was newly created
    return True

def load_tokens():
    """Loads all tokens from config.json."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            tokens_data = config.get("tokens", [])
            tokens = [t.get("value") for t in tokens_data if t.get("value") and t.get("value") != "YOUR_YANDEX_OAUTH_TOKEN_HERE"]
            return tokens
    except Exception as e:
        print(f"Error loading config: {e}")
    return []

def main():
    logger = setup_logger()
    logger.info("Starting Yandex 360 Directory Manager")

    app = QApplication(sys.argv)
    app.setStyleSheet(MAIN_STYLE)

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
