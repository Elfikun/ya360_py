LIGHT_STYLE = """
QMainWindow {
    background-color: #f4f5f7;
    color: #1f2937;
}

QWidget {
    font-size: 13px;
    color: #1f2937;
}

/* Sidebar */
QListWidget {
    background-color: #ffffff;
    color: #1f2937;
    border: none;
    border-right: 1px solid #e0e0e0;
    padding: 5px;
    font-size: 14px;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    color: #1f2937;
}
QListWidget::item:hover {
    background-color: #f0f4f8;
}
QListWidget::item:selected {
    background-color: #e5f0fa;
    color: #005bff;
    font-weight: bold;
}

/* Header & Search */
QLineEdit {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #ffffff;
    color: #1f2937;
    selection-background-color: #005bff;
    selection-color: #ffffff;
}
QLineEdit:focus {
    border-color: #005bff;
}

QComboBox {
    padding: 6px 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #ffffff;
    color: #1f2937;
}
QComboBox:hover {
    border-color: #005bff;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #ccc;
    selection-background-color: #e5f0fa;
    selection-color: #005bff;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #e0e0e0;
    background: #ffffff;
}
QTabBar::tab {
    background: #f4f5f7;
    color: #555555;
    border: 1px solid #e0e0e0;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background: #ffffff;
    color: #005bff;
    border-bottom-color: #ffffff;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background: #e9ecef;
}

/* Table */
QTableWidget {
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #e0e0e0;
    gridline-color: #f0f0f0;
    selection-background-color: #e5f0fa;
    selection-color: #005bff;
}
QTableWidget::item {
    padding: 4px;
}
QHeaderView::section {
    background-color: #fafafa;
    color: #333333;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #e0e0e0;
    border-right: 1px solid #e0e0e0;
    font-weight: bold;
}

/* Buttons */
QPushButton {
    background-color: #005bff;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #004ecc;
}
QPushButton:pressed {
    background-color: #003a99;
}
QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}

/* Icon Buttons (logs, theme toggle) */
QPushButton#iconButton {
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 16px;
    padding: 0px;
}
QPushButton#iconButton:hover {
    background-color: #e5f0fa;
    border-color: #005bff;
}
QPushButton#iconButton:pressed {
    background-color: #cce0f5;
}

/* Dialogs & Widgets */
QDialog {
    background-color: #ffffff;
    color: #1f2937;
}

QLabel {
    color: #1f2937;
}

QTextEdit {
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #ccc;
    border-radius: 4px;
}

QMenu {
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #ccc;
}
QMenu::item:selected {
    background-color: #e5f0fa;
    color: #005bff;
}

QStatusBar {
    background-color: #f4f5f7;
    color: #555555;
}

QToolTip {
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #ccc;
    padding: 4px;
}
"""

DARK_STYLE = """
QMainWindow {
    background-color: #1e1f22;
    color: #e0e0e0;
}

QWidget {
    font-size: 13px;
    color: #e0e0e0;
}

/* Sidebar */
QListWidget {
    background-color: #2b2d30;
    color: #e0e0e0;
    border: none;
    border-right: 1px solid #3c3f41;
    padding: 5px;
    font-size: 14px;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    color: #cfd2d7;
}
QListWidget::item:hover {
    background-color: #35373a;
    color: #ffffff;
}
QListWidget::item:selected {
    background-color: #2d4365;
    color: #4c8dff;
    font-weight: bold;
}

/* Header & Search */
QLineEdit {
    padding: 8px;
    border: 1px solid #4e5157;
    border-radius: 4px;
    background-color: #1e1f22;
    color: #f0f0f0;
    selection-background-color: #3574f0;
    selection-color: #ffffff;
}
QLineEdit:focus {
    border-color: #3574f0;
}

QComboBox {
    padding: 6px 10px;
    border: 1px solid #4e5157;
    border-radius: 4px;
    background-color: #2b2d30;
    color: #f0f0f0;
}
QComboBox:hover {
    border-color: #3574f0;
}
QComboBox QAbstractItemView {
    background-color: #2b2d30;
    color: #f0f0f0;
    border: 1px solid #4e5157;
    selection-background-color: #2d4365;
    selection-color: #4c8dff;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #3c3f41;
    background: #2b2d30;
}
QTabBar::tab {
    background: #1e1f22;
    color: #9da0a6;
    border: 1px solid #3c3f41;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background: #2b2d30;
    color: #4c8dff;
    border-bottom-color: #2b2d30;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background: #25272a;
    color: #e0e0e0;
}

/* Table */
QTableWidget {
    background-color: #2b2d30;
    color: #e0e0e0;
    border: 1px solid #3c3f41;
    gridline-color: #3c3f41;
    selection-background-color: #2d4365;
    selection-color: #ffffff;
}
QTableWidget::item {
    padding: 4px;
}
QHeaderView::section {
    background-color: #222427;
    color: #b0b4ba;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #3c3f41;
    border-right: 1px solid #3c3f41;
    font-weight: bold;
}

/* Buttons */
QPushButton {
    background-color: #3574f0;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #4582ff;
}
QPushButton:pressed {
    background-color: #285ec4;
}
QPushButton:disabled {
    background-color: #3c3f41;
    color: #777777;
}

/* Icon Buttons (logs, theme toggle) */
QPushButton#iconButton {
    background-color: #2b2d30;
    color: #e0e0e0;
    border: 1px solid #4e5157;
    border-radius: 4px;
    font-size: 16px;
    padding: 0px;
}
QPushButton#iconButton:hover {
    background-color: #35373a;
    border-color: #3574f0;
}
QPushButton#iconButton:pressed {
    background-color: #222427;
}

/* Dialogs & Widgets */
QDialog {
    background-color: #2b2d30;
    color: #e0e0e0;
}

QLabel {
    color: #e0e0e0;
}

QTextEdit {
    background-color: #1e1f22;
    color: #f0f0f0;
    border: 1px solid #4e5157;
    border-radius: 4px;
}

QMenu {
    background-color: #2b2d30;
    color: #e0e0e0;
    border: 1px solid #4e5157;
}
QMenu::item:selected {
    background-color: #2d4365;
    color: #4c8dff;
}

QStatusBar {
    background-color: #1e1f22;
    color: #9da0a6;
}

QToolTip {
    background-color: #2b2d30;
    color: #f0f0f0;
    border: 1px solid #4e5157;
    padding: 4px;
}

QScrollBar:vertical {
    border: none;
    background: #1e1f22;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #4e5157;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #6f737a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #1e1f22;
    height: 10px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #4e5157;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #6f737a;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""

MAIN_STYLE = LIGHT_STYLE

def get_theme_style(theme_name: str) -> str:
    """Returns the QSS stylesheet string for the requested theme name ('light' or 'dark')."""
    if theme_name == "dark":
        return DARK_STYLE
    return LIGHT_STYLE

