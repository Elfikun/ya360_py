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

    window = MainWindow(passwork_settings)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
