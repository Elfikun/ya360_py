MAIN_STYLE = """
QMainWindow {
    background-color: #f4f5f7;
}

/* Sidebar */
QListWidget {
    background-color: #ffffff;
    border: none;
    border-right: 1px solid #e0e0e0;
    padding: 5px;
    font-size: 14px;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #e5f0fa;
    color: #005bff;
}

/* Header & Search */
QLineEdit {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #ffffff;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #e0e0e0;
    background: #ffffff;
}
QTabBar::tab {
    background: #f4f5f7;
    border: 1px solid #e0e0e0;
    padding: 8px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #ffffff;
    border-bottom-color: #ffffff;
    font-weight: bold;
}

/* Table */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    gridline-color: #f0f0f0;
}
QHeaderView::section {
    background-color: #fafafa;
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

/* Dialogs */
QDialog {
    background-color: #ffffff;
}
"""
