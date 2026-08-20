import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow
from gui.styles import get_theme_style
from utils.logger import setup_logger
from utils.config import ensure_config, load_passwork_settings, get_theme, CONFIG_FILE
from utils.passwork_integration import fetch_yandex_tokens_from_passwork

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
            f"Файл конфигурации создан по пути: {CONFIG_FILE}\nПожалуйста, укажите настройки подключения к Passwork в этом файле и перезапустите приложение."
        )
        return

    passwork_settings = load_passwork_settings()
    url = passwork_settings.get("passwork_url")
    token = passwork_settings.get("passwork_api_token")
    tag = passwork_settings.get("passwork_search_tag")

    if not url or not token or token == "YOUR_PASSWORK_API_TOKEN_HERE":
        QMessageBox.warning(
            None,
            "Ошибка конфигурации",
            f"Пожалуйста, укажите корректные данные для подключения к Passwork (URL и API Token) в файле:\n{CONFIG_FILE}"
        )
        return

    tokens = fetch_yandex_tokens_from_passwork(url, token, tag)

    if not tokens:
        QMessageBox.warning(
            None,
            "Токены не найдены",
            f"Не удалось получить токены Yandex 360 из Passwork.\nУбедитесь, что в Passwork существуют записи с тегом '{tag}' и у вас есть к ним доступ."
        )
        return

    window = MainWindow(tokens)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
