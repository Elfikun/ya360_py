from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication

from utils.helpers import generate_nickname, generate_password
from utils.storage import load_cache, remove_from_cache
from utils.logger import LOG_FILE
import datetime

class CreateUserDialog(QDialog):
    def __init__(self, organizations, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать пользователя")
        self.setMinimumWidth(400)
        self.organizations = organizations
        self.user_data = None

        layout = QVBoxLayout(self)

        # First Name
        layout.addWidget(QLabel("Имя:"))
        self.first_name_input = QLineEdit()
        self.first_name_input.textChanged.connect(self.update_nickname)
        layout.addWidget(self.first_name_input)

        # Last Name
        layout.addWidget(QLabel("Фамилия:"))
        self.last_name_input = QLineEdit()
        self.last_name_input.textChanged.connect(self.update_nickname)
        layout.addWidget(self.last_name_input)

        # Middle Name
        layout.addWidget(QLabel("Отчество (опционально):"))
        self.middle_name_input = QLineEdit()
        self.middle_name_input.textChanged.connect(self.update_nickname)
        layout.addWidget(self.middle_name_input)

        # Organization
        layout.addWidget(QLabel("Организация:"))
        self.org_combo = QComboBox()
        for org in self.organizations:
            self.org_combo.addItem(org.get("name", "Unknown"), org.get("id"))
        layout.addWidget(self.org_combo)

        # Nickname
        layout.addWidget(QLabel("Никнейм:"))
        self.nickname_input = QLineEdit()
        layout.addWidget(self.nickname_input)

        # Password
        layout.addWidget(QLabel("Пароль:"))
        pass_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setText(generate_password())
        pass_layout.addWidget(self.password_input)

        regen_btn = QPushButton("🔄")
        regen_btn.setFixedWidth(40)
        regen_btn.clicked.connect(lambda: self.password_input.setText(generate_password()))
        pass_layout.addWidget(regen_btn)

        copy_btn = QPushButton("📋")
        copy_btn.setFixedWidth(40)
        copy_btn.clicked.connect(self.copy_password)
        pass_layout.addWidget(copy_btn)
        layout.addLayout(pass_layout)

        # Require password change
        self.require_pass_change = QCheckBox("Требовать смену пароля при первом входе")
        self.require_pass_change.setChecked(True)
        layout.addWidget(self.require_pass_change)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Создать")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def update_nickname(self):
        first = self.first_name_input.text().strip()
        last = self.last_name_input.text().strip()
        middle = self.middle_name_input.text().strip()

        if last:
            nick = generate_nickname(last, first, middle)
            self.nickname_input.setText(nick)

    def copy_password(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.password_input.text())

    def accept(self):
        if not self.first_name_input.text().strip() or not self.last_name_input.text().strip():
            QMessageBox.warning(self, "Ошибка валидации", "Поля 'Имя' и 'Фамилия' обязательны для заполнения.")
            return
        super().accept()

    def get_data(self):
        org_id = self.org_combo.currentData()
        # Yandex 360 API structure for user creation
        return org_id, {
            "name": {
                "first": self.first_name_input.text().strip(),
                "last": self.last_name_input.text().strip(),
                "middle": self.middle_name_input.text().strip()
            },
            "nickname": self.nickname_input.text().strip(),
            "password": self.password_input.text(),
            "is_password_change_required": self.require_pass_change.isChecked()
        }


class ResetPasswordDialog(QDialog):
    def __init__(self, nickname, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сброс пароля")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Новый пароль для пользователя <b>{nickname}</b>:"))

        pass_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setText(generate_password())
        self.password_input.setReadOnly(True)
        pass_layout.addWidget(self.password_input)

        copy_btn = QPushButton("📋 Копировать")
        copy_btn.clicked.connect(self.copy_password)
        pass_layout.addWidget(copy_btn)
        layout.addLayout(pass_layout)

        self.require_pass_change = QCheckBox("Требовать смену пароля при первом входе")
        self.require_pass_change.setChecked(True)
        layout.addWidget(self.require_pass_change)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Применить")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def copy_password(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.password_input.text())

    def get_data(self):
        return self.password_input.text(), self.require_pass_change.isChecked()


class AutoCleanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авто-очистка удаленных пользователей (> 30 дней)")
        self.resize(600, 400)

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Никнейм", "Организация", "Дата удаления"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

        self.users_to_delete = []
        self.load_candidates()

        if not self.users_to_delete:
            self.layout.addWidget(QLabel("Нет пользователей, удаленных более 30 дней назад."))
        else:
            self.layout.addWidget(QLabel(f"Найдено пользователей для окончательного удаления: {len(self.users_to_delete)}"))

        btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton("Удалить навсегда")
        self.delete_btn.setStyleSheet("background-color: #d9534f; color: white;")
        self.delete_btn.setEnabled(len(self.users_to_delete) > 0)
        self.delete_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(cancel_btn)
        self.layout.addLayout(btn_layout)

    def load_candidates(self):
        cache = load_cache()
        now = datetime.datetime.now(datetime.timezone.utc)

        self.table.setRowCount(0)

        for user_id, data in cache.items():
            deleted_at_str = data.get("deleted_at")
            if deleted_at_str:
                try:
                    deleted_at = datetime.datetime.fromisoformat(deleted_at_str.replace('Z', '+00:00'))
                    days_diff = (now - deleted_at).days
                    if days_diff > 30:
                        self.users_to_delete.append({
                            "user_id": user_id,
                            "org_id": data.get("org_id"),
                            "nickname": data.get("nickname")
                        })

                        row = self.table.rowCount()
                        self.table.insertRow(row)
                        self.table.setItem(row, 0, QTableWidgetItem(user_id))
                        self.table.setItem(row, 1, QTableWidgetItem(data.get("nickname", "")))
                        self.table.setItem(row, 2, QTableWidgetItem(data.get("org_name", "")))
                        self.table.setItem(row, 3, QTableWidgetItem(deleted_at_str[:10]))

                except ValueError:
                    pass

    def get_candidates(self):
        return self.users_to_delete


class LogViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Журнал действий")
        self.resize(700, 500)

        layout = QVBoxLayout(self)

        import os
        from PyQt6.QtWidgets import QTextEdit

        # Search layout
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по логам...")
        self.search_input.textChanged.connect(self.filter_logs)
        search_layout.addWidget(QLabel("🔍"))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.all_log_lines = []

        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                self.all_log_lines = f.readlines()
                self.log_text.setText("".join(self.all_log_lines))
        else:
            self.log_text.setText("Лог файл пуст или не существует.")

        # Scroll to bottom
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def filter_logs(self):
        search_term = self.search_input.text().lower()
        if not search_term:
            self.log_text.setText("".join(self.all_log_lines))
        else:
            filtered = [line for line in self.all_log_lines if search_term in line.lower()]
            self.log_text.setText("".join(filtered))

        # Scroll to bottom again after filtering
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
