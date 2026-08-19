from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QMessageBox
)
from PyQt6.QtGui import QGuiApplication
import re

from utils.helpers import generate_nickname, generate_password
from utils.logger import LOG_FILE

class CreateUserDialog(QDialog):
    def __init__(self, organizations, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать пользователя")
        self.setMinimumWidth(400)
        self.organizations = organizations
        self.user_data = None

        layout = QVBoxLayout(self)

        # Last Name
        layout.addWidget(QLabel("Фамилия *:"))
        self.last_name_input = QLineEdit()
        self.last_name_input.textChanged.connect(self.update_nickname)
        layout.addWidget(self.last_name_input)

        # First Name
        layout.addWidget(QLabel("Имя *:"))
        self.first_name_input = QLineEdit()
        self.first_name_input.textChanged.connect(self.update_nickname)
        layout.addWidget(self.first_name_input)

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
        last = self.last_name_input.text().strip()
        first = self.first_name_input.text().strip()
        nickname = self.nickname_input.text().strip()
        password = self.password_input.text()

        if not last or not first:
            QMessageBox.warning(self, "Ошибка валидации", "Поля 'Фамилия' и 'Имя' обязательны для заполнения.")
            return

        # Nickname: only lowercase latin letters, digits, dots, underscores, hyphens
        if nickname and not re.fullmatch(r'[a-z0-9._\-]+', nickname):
            QMessageBox.warning(
                self,
                "Ошибка валидации",
                "Никнейм может содержать только строчные латинские буквы, цифры и символы: . _ -"
            )
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Ошибка валидации", "Пароль должен быть не менее 6 символов.")
            return

        super().accept()

    def get_data(self):
        org_id = self.org_combo.currentData()
        name_dict = {
            "first": self.first_name_input.text().strip(),
            "last": self.last_name_input.text().strip()
        }
        middle = self.middle_name_input.text().strip()
        if middle:
            name_dict["middle"] = middle

        return org_id, {
            "name": name_dict,
            "nickname": self.nickname_input.text().strip(),
            "password": self.password_input.text(),
            "departmentId": 1,
            "passwordChangeRequired": True
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
        return self.password_input.text(), True





class LogViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Журнал действий")
        self.resize(700, 500)

        layout = QVBoxLayout(self)

        import os
        import html
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
            self.log_text.setHtml(self._format_lines(self.all_log_lines))
        else:
            self.log_text.setText("Лог файл пуст или не существует.")

        # Scroll to bottom
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _format_lines(self, lines):
        """Converts log lines to HTML, highlighting user nicknames in bold."""
        import html
        html_lines = []
        # Match patterns like: 'nickname', e.g. 'katatp'
        nickname_re = re.compile(r"'([^']+)'")
        for line in lines:
            escaped = html.escape(line.rstrip())
            # Bold everything between single quotes (user nicknames / org names)
            formatted = nickname_re.sub(r"'<b>\1</b>'", escaped)
            html_lines.append(formatted)
        return "<pre style='font-family: monospace; white-space: pre-wrap;'>" + "<br>".join(html_lines) + "</pre>"

    def filter_logs(self):
        search_term = self.search_input.text().lower()
        if not search_term:
            self.log_text.setHtml(self._format_lines(self.all_log_lines))
        else:
            filtered = [line for line in self.all_log_lines if search_term in line.lower()]
            self.log_text.setHtml(self._format_lines(filtered))

        # Scroll to bottom again after filtering
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())


class UserCreatedSuccessDialog(QDialog):
    def __init__(self, email: str, password: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Пользователь успешно создан")
        self.setMinimumWidth(480)
        self.email = email
        self.password = password

        layout = QVBoxLayout(self)

        info_label = QLabel("Учетная запись успешно создана в Яндекс 360")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Email / Login section
        layout.addWidget(QLabel("Логин (email с доменом):"))
        email_layout = QHBoxLayout()
        self.email_input = QLineEdit(self.email)
        self.email_input.setReadOnly(True)
        email_layout.addWidget(self.email_input)

        copy_email_btn = QPushButton("📋 Логин")
        copy_email_btn.clicked.connect(self.copy_email)
        email_layout.addWidget(copy_email_btn)
        layout.addLayout(email_layout)

        # Password section
        layout.addWidget(QLabel("Пароль:"))
        pass_layout = QHBoxLayout()
        self.password_input = QLineEdit(self.password)
        self.password_input.setReadOnly(True)
        pass_layout.addWidget(self.password_input)

        copy_pass_btn = QPushButton("📋 Пароль")
        copy_pass_btn.clicked.connect(self.copy_password)
        pass_layout.addWidget(copy_pass_btn)
        layout.addLayout(pass_layout)

        layout.addSpacing(15)

        # Action Buttons
        btn_layout = QHBoxLayout()
        copy_all_btn = QPushButton("📋 Скопировать всё (Логин + Пароль)")
        copy_all_btn.setStyleSheet("font-weight: bold; padding: 6px 12px;")
        copy_all_btn.clicked.connect(self.copy_all)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(copy_all_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def copy_email(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.email)
        QMessageBox.information(self, "Успешно", "Логин скопирован в буфер обмена!")

    def copy_password(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.password)
        QMessageBox.information(self, "Успешно", "Пароль скопирован в буфер обмена!")

    def copy_all(self):
        clipboard = QGuiApplication.clipboard()
        text_to_copy = f"Логин: {self.email}\nПароль: {self.password}"
        clipboard.setText(text_to_copy)
        QMessageBox.information(self, "Успешно", "Логин и пароль скопированы в буфер обмена!")
