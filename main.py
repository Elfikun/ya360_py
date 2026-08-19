import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow
from gui.styles import get_theme_style
from utils.logger import setup_logger
from utils.config import ensure_config, load_tokens, get_theme, CONFIG_FILE

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
