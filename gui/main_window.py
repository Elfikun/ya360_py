import sys
import os
import datetime
import csv

# Ensure root directory is in sys.path when running main_window.py directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QTabBar,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QMessageBox, QHeaderView, QAbstractItemView, QDialog,
    QMenu, QFileDialog, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer

from api.manager import ApiManager
from gui.dialogs import CreateUserDialog, ResetPasswordDialog, LogViewerDialog, UserCreatedSuccessDialog
from utils.logger import get_logger
from utils.config import get_theme, set_theme

logger = get_logger()

class MainWindow(QMainWindow):
    def __init__(self, passwork_settings: dict):
        super().__init__()
        self.setWindowTitle("Yandex 360 Directory Manager")
        self.resize(1200, 800)

        self.api_manager = ApiManager()
        self.organizations = []
        self.all_users = []  # List of all fetched users
        self._pending_passwords = {}

        self.current_org_id = None
        self.current_tab_filter = "All"

        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(200)
        self.update_timer.timeout.connect(self._do_update_ui)

        self.current_theme = get_theme()
        self.passwork_settings = passwork_settings

        # Initialize UI elements
        self.setup_ui()
        self.setup_connections()

        # Disable main interaction elements until tokens are loaded
        self._set_main_interaction_enabled(False)

        self.fetch_tokens()

    def _set_main_interaction_enabled(self, enabled: bool):
        """Enables or disables main UI components, keeping the parent window and retry button active."""
        if hasattr(self, 'org_list'):
            self.org_list.setEnabled(enabled)
        if hasattr(self, 'table'):
            self.table.setEnabled(enabled)
        if hasattr(self, 'btn_create'):
            self.btn_create.setEnabled(enabled)
            self.btn_lock.setEnabled(enabled)
            self.btn_unlock.setEnabled(enabled)
            self.btn_reset_pass.setEnabled(enabled)
            self.btn_delete.setEnabled(enabled)

    def fetch_tokens(self):
        if hasattr(self, 'retry_btn'):
            self.retry_btn.hide()
        self.statusBar().showMessage("Подключение к Passwork и получение токенов...")
        url = self.passwork_settings.get("passwork_url")
        token = self.passwork_settings.get("passwork_api_token")
        tag = self.passwork_settings.get("passwork_search_tag")

        if not url or not token or token == "YOUR_PASSWORK_API_TOKEN_HERE":
            self.on_error("Ошибка конфигурации", "Не настроены параметры Passwork. Пожалуйста, проверьте config.json.")
            self.retry_btn.show()
        else:
            self.api_manager.fetch_tokens_from_passwork_async(url, token, tag)

    def retry_fetch_tokens(self):
        from utils.config import load_passwork_settings
        self.passwork_settings = load_passwork_settings()
        self.fetch_tokens()

    @pyqtSlot(list)
    def on_tokens_fetched(self, tokens):
        self._set_main_interaction_enabled(True)
        if hasattr(self, 'retry_btn'):
            self.retry_btn.hide()
        self.statusBar().showMessage("Токены успешно получены. Загрузка организаций...")
        self.api_manager.fetch_orgs()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # ---------------- SIDEBAR ----------------
        sidebar_layout = QVBoxLayout()

        # Orgs List
        self.org_list = QListWidget()
        self.org_list.setFixedWidth(250)
        self.org_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.org_list.customContextMenuRequested.connect(self.show_org_context_menu)
        sidebar_layout.addWidget(QLabel("<b>Организации</b>"))
        sidebar_layout.addWidget(self.org_list)

        # Stats
        self.stats_label = QLabel("Total: 0\nActive: 0\nDisabled: 0")
        sidebar_layout.addWidget(self.stats_label)

        main_layout.addLayout(sidebar_layout)

        # ---------------- MAIN AREA ----------------
        right_layout = QVBoxLayout()

        # Search and Filters
        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск (Имя, Email, Никнейм)...")
        self.search_input.textChanged.connect(self.filter_table)
        top_bar.addWidget(self.search_input)

        top_bar.addWidget(QLabel("<b>Сортировка:</b>"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("По умолчанию", -1)
        self.sort_combo.addItem("По ФИО (А-Я)", (0, Qt.SortOrder.AscendingOrder))
        self.sort_combo.addItem("По ФИО (Я-А)", (0, Qt.SortOrder.DescendingOrder))
        self.sort_combo.addItem("По дате создания (новые → старые)", (4, Qt.SortOrder.DescendingOrder))
        self.sort_combo.addItem("По дате создания (старые → новые)", (4, Qt.SortOrder.AscendingOrder))
        self.sort_combo.addItem("По дате блокировки (новые → старые)", (5, Qt.SortOrder.DescendingOrder))
        self.sort_combo.addItem("По дате блокировки (старые → новые)", (5, Qt.SortOrder.AscendingOrder))
        self.sort_combo.currentIndexChanged.connect(self.on_sort_combo_changed)
        top_bar.addWidget(self.sort_combo)

        # Log button (Audit log icon)
        logs_btn = QPushButton("📜")
        logs_btn.setObjectName("iconButton")
        logs_btn.setToolTip("Журнал действий")
        logs_btn.setFixedSize(36, 36)
        logs_btn.clicked.connect(self.show_logs)
        top_bar.addWidget(logs_btn)

        # Theme toggle button
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("iconButton")
        self.theme_btn.setFixedSize(36, 36)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.update_theme_button_ui()
        top_bar.addWidget(self.theme_btn)

        right_layout.addLayout(top_bar)

        # Tabs for filtering
        self.tabs = QTabBar()
        self.tabs.addTab("Все")
        self.tabs.addTab("Активные")
        self.tabs.addTab("Заблокированные")
        self.tabs.currentChanged.connect(self.on_tab_changed)
        right_layout.addWidget(self.tabs)

        # Data Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ФИО", "Никнейм", "Email", "Статус", "Создан", "Дата блокировки"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        right_layout.addWidget(self.table)

        # Retry button for Passwork
        self.retry_btn = QPushButton("Повторить подключение к Passwork")
        self.retry_btn.clicked.connect(self.retry_fetch_tokens)
        self.retry_btn.hide()
        self.retry_btn.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold; padding: 10px;")
        right_layout.addWidget(self.retry_btn)

        # Action Buttons
        action_layout = QHBoxLayout()

        self.btn_create = QPushButton("+ Создать")
        self.btn_create.clicked.connect(self.create_user)

        self.btn_lock = QPushButton("🔒 Заблокировать")
        self.btn_lock.clicked.connect(self.lock_user)

        self.btn_unlock = QPushButton("🔓 Разблокировать")
        self.btn_unlock.clicked.connect(self.unlock_user)

        self.btn_reset_pass = QPushButton("🔑 Сброс пароля")
        self.btn_reset_pass.clicked.connect(self.reset_password)

        self.btn_delete = QPushButton("🗑️ Удалить")
        self.btn_delete.clicked.connect(self.delete_user)

        action_layout.addWidget(self.btn_create)
        action_layout.addWidget(self.btn_lock)
        action_layout.addWidget(self.btn_unlock)
        action_layout.addWidget(self.btn_reset_pass)
        action_layout.addWidget(self.btn_delete)

        right_layout.addLayout(action_layout)

        main_layout.addLayout(right_layout)

    def setup_connections(self):
        self.api_manager.tokens_fetched.connect(self.on_tokens_fetched)
        self.api_manager.orgs_loaded.connect(self.on_orgs_loaded)
        self.api_manager.users_loaded.connect(self.on_users_loaded)
        self.api_manager.user_created.connect(self.on_user_created)
        self.api_manager.user_updated.connect(self.on_user_updated)
        self.api_manager.user_deleted.connect(self.on_user_deleted)
        self.api_manager.error_occurred.connect(self.on_error)
        self.org_list.currentItemChanged.connect(self.on_org_selected)

    def toggle_theme(self):
        from gui.styles import get_theme_style
        from PyQt6.QtWidgets import QApplication

        self.current_theme = "dark" if self.current_theme == "light" else "light"
        set_theme(self.current_theme)

        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_theme_style(self.current_theme))

        self.update_theme_button_ui()

    def update_theme_button_ui(self):
        if hasattr(self, "theme_btn"):
            if self.current_theme == "dark":
                self.theme_btn.setText("☀️")
                self.theme_btn.setToolTip("Переключить на светлую тему")
            else:
                self.theme_btn.setText("🌙")
                self.theme_btn.setToolTip("Переключить на темную тему")

    # --- Slots / Callbacks ---

    @pyqtSlot(list)
    def on_orgs_loaded(self, orgs):
        self.organizations = orgs
        self.org_list.clear()

        # Add "All Organizations" item
        all_item = QListWidgetItem("Все организации")
        all_item.setData(Qt.ItemDataRole.UserRole, "ALL")
        self.org_list.addItem(all_item)

        for org in orgs:
            item = QListWidgetItem(org.get("name", f"Org {org.get('id')}"))
            item.setData(Qt.ItemDataRole.UserRole, org.get("id"))
            self.org_list.addItem(item)

        self.statusBar().showMessage(f"Loaded {len(orgs)} organizations", 5000)
        self.org_list.setCurrentRow(0) # Select "All" by default

    @pyqtSlot(str, list)
    def on_users_loaded(self, org_id, users):
        # We might receive users for a specific org while viewing all, or just that org
        # For simplicity, we just keep a main all_users list and re-render.
        # Clear existing users for this org_id
        self.all_users = [u for u in self.all_users if u.get('_org_id') != org_id]

        # Find org name
        org_name = next((o.get("name") for o in self.organizations if o.get("id") == org_id), org_id)

        # Append new users, skipping internal Yandex robot accounts
        skipped = 0
        for u in users:
            if self._is_robot_account(u):
                skipped += 1
                continue
            u['_org_id'] = org_id
            u['_org_name'] = org_name
            self.all_users.append(u)

        msg = f"Loaded users for org {org_name}"
        if skipped:
            msg += f" (skipped {skipped} robot accounts)"
        self.statusBar().showMessage(msg, 5000)
        self.update_timer.start()

    @staticmethod
    def _is_robot_account(user: dict) -> bool:
        """Returns True for internal Yandex service/robot accounts that should be hidden."""
        nickname = (user.get("nickname") or "").lower()
        email = (user.get("email") or "").lower()

        if "robot" in nickname:
            return True
        if nickname.startswith("yndx-"):
            return True
        if email.endswith("@yandex.ru"):
            return True
        return False


    def _do_update_ui(self):
        self.update_stats()
        self.filter_table()

    @pyqtSlot(dict)
    def on_user_created(self, user):
        nickname = user.get("nickname", "")
        email = user.get("email") or f"{nickname}@..."
        password = self._pending_passwords.pop(nickname, "")
        logger.info(f"User created: '{nickname}' ({email}) [ID: {user.get('id', '?')}]")
        self.statusBar().showMessage("Пользователь успешно создан!", 5000)

        success_dialog = UserCreatedSuccessDialog(email, password, self)
        success_dialog.exec()

        if self.current_org_id and self.current_org_id != "ALL":
            self.api_manager.fetch_users(self.current_org_id)
        else:
            for org in self.organizations:
                self.api_manager.fetch_users(org.get("id"))

    @pyqtSlot(dict)
    def on_user_updated(self, user):
        nickname = user.get("nickname") or user.get("email", "")
        logger.info(f"User updated: '{nickname}' [ID: {user.get('id', '?')}]")
        self.statusBar().showMessage("Данные пользователя обновлены", 5000)

        if isinstance(user, dict) and user.get("id"):
            updated_id = str(user.get("id"))
            for i, u in enumerate(self.all_users):
                if str(u.get("id")) == updated_id:
                    self.all_users[i].update(user)
                    break

        self.filter_table()
        self.update_stats()

    @pyqtSlot(str, str)
    def on_user_deleted(self, org_id, user_id):
        org_name = next((o.get("name") for o in self.organizations if str(o.get("id")) == str(org_id)), org_id)
        logger.info(f"User permanently deleted: [ID: {user_id}] from org '{org_name}'")
        self.statusBar().showMessage("Пользователь удален навсегда", 5000)
        self.all_users = [u for u in self.all_users if u.get('id') != user_id]
        self.filter_table()
        self.update_stats()

    @pyqtSlot(str, str)
    def on_error(self, title, message):
        QMessageBox.critical(self, title, message)
        self.statusBar().showMessage(f"Error: {title}")
        if title in ["Ошибка Passwork", "Токены не найдены", "Ошибка конфигурации"]:
            if hasattr(self, 'retry_btn'):
                self.retry_btn.show()

    # --- UI Interactions ---

    def on_org_selected(self, current, previous):
        if not current:
            return

        org_id = current.data(Qt.ItemDataRole.UserRole)
        self.current_org_id = org_id

        self.all_users.clear()
        self.table.setRowCount(0)

        if org_id == "ALL":
            for org in self.organizations:
                self.api_manager.fetch_users(org.get("id"))
        else:
            self.api_manager.fetch_users(org_id)

    def on_tab_changed(self, index):
        if index == 0:
            self.current_tab_filter = "All"
        elif index == 1:
            self.current_tab_filter = "Active"
        elif index == 2:
            self.current_tab_filter = "Disabled"
        self.filter_table()

    def is_user_enabled(self, user: dict) -> bool:
        if "isEnabled" in user:
            enabled = user["isEnabled"]
        elif "is_enabled" in user:
            enabled = user["is_enabled"]
        else:
            enabled = True

        if user.get("isDismissed") or user.get("is_dismissed"):
            return False
        return bool(enabled)

    def update_stats(self):
        total = len(self.all_users)
        active = sum(1 for u in self.all_users if self.is_user_enabled(u))
        disabled = total - active
        self.stats_label.setText(f"Всего: {total}\nАктивные: {active}\nЗаблокированные: {disabled}")

    def on_sort_combo_changed(self):
        data = self.sort_combo.currentData()
        if data is None or data == -1:
            return
        col, order = data
        self.table.sortItems(col, order)

    def filter_table(self):
        search_text = self.search_input.text().lower()

        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for user in self.all_users:
            # Tab filter
            is_enabled = self.is_user_enabled(user)
            if self.current_tab_filter == "Active" and not is_enabled:
                continue
            if self.current_tab_filter == "Disabled" and is_enabled:
                continue

            # Search filter
            name = f"{user.get('name', {}).get('last', '')} {user.get('name', {}).get('first', '')}".lower()
            email = user.get("email", "").lower()
            nickname = user.get("nickname", "").lower()

            if search_text and search_text not in name and search_text not in email and search_text not in nickname:
                continue

            # Add to table
            row = self.table.rowCount()
            self.table.insertRow(row)

            full_name = f"{user.get('name', {}).get('last', '')} {user.get('name', {}).get('first', '')} {user.get('name', {}).get('middle', '')}".strip()
            fio_item = QTableWidgetItem(full_name)

            user_id = str(user.get("id", ""))
            org_name = user.get("_org_name", "")
            fio_item.setToolTip(f"ID: {user_id}\nОрганизация: {org_name}")

            self.table.setItem(row, 0, fio_item)
            self.table.setItem(row, 1, QTableWidgetItem(user.get("nickname", "")))
            self.table.setItem(row, 2, QTableWidgetItem(user.get("email", "")))

            status = "Активен" if is_enabled else "Заблокирован"
            self.table.setItem(row, 3, QTableWidgetItem(status))

            created_at = (user.get("createdAt") or user.get("created_at") or user.get("created") or "")[:10]
            self.table.setItem(row, 4, QTableWidgetItem(created_at))

            if not is_enabled:
                blocked_raw = (
                    user.get("isEnabledUpdatedAt") or
                    user.get("is_enabled_updated_at") or
                    user.get("blocked_at") or
                    user.get("_blocked_at") or
                    user.get("updatedAt") or
                    user.get("updated_at") or
                    ""
                )
                blocked_at = blocked_raw[:10] if blocked_raw else "-"
            else:
                blocked_at = "-"

            self.table.setItem(row, 5, QTableWidgetItem(blocked_at))

            # Store full user data in column 0 item
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, user)

        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)

        if hasattr(self, "sort_combo"):
            sort_data = self.sort_combo.currentData()
            if sort_data and sort_data != -1:
                col, order = sort_data
                self.table.sortItems(col, order)

    def get_selected_user(self):
        users = self.get_selected_users()
        return users[0] if users else None

    def get_selected_users(self):
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите одного или нескольких пользователей.")
            return []

        users = []
        for row in sorted(selected_rows):
            item = self.table.item(row, 0)
            if item:
                user = item.data(Qt.ItemDataRole.UserRole)
                if user:
                    users.append(user)
        return users

    def create_user(self):
        if not self.organizations:
            QMessageBox.warning(self, "Внимание", "Нет доступных организаций.")
            return

        dialog = CreateUserDialog(self.organizations, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            org_id, data = dialog.get_data()
            nickname = data.get("nickname", "")
            password = data.get("password", "")
            if nickname:
                self._pending_passwords[nickname] = password
            org_name = next((o.get("name") for o in self.organizations if str(o.get("id")) == str(org_id)), org_id)
            logger.info(f"Creating user '{nickname}' in org '{org_name}'")
            self.api_manager.create_user(org_id, data)

    def lock_user(self):
        users = self.get_selected_users()
        if not users:
            return

        count = len(users)
        msg = f"Вы действительно хотите заблокировать {count} выбранных пользователей?" if count > 1 else f"Вы действительно хотите заблокировать пользователя '{users[0].get('nickname')}'?"
        if QMessageBox.question(self, "Подтверждение блокировки", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        now_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        for user in users:
            org_id = user.get("_org_id")
            user_id = user.get("id")
            nickname = user.get("nickname") or user.get("email", "")
            org_name = user.get("_org_name", org_id)
            user["_blocked_at"] = now_date
            user["isEnabledUpdatedAt"] = now_date
            logger.info(f"Blocking user '{nickname}' in org '{org_name}' [ID: {user_id}]")
            self.api_manager.block_user(org_id, user_id)

    def unlock_user(self):
        users = self.get_selected_users()
        if not users:
            return

        count = len(users)
        msg = f"Вы действительно хотите разблокировать {count} выбранных пользователей?" if count > 1 else f"Вы действительно хотите разблокировать пользователя '{users[0].get('nickname')}'?"
        if QMessageBox.question(self, "Подтверждение разблокировки", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        for user in users:
            org_id = user.get("_org_id")
            user_id = user.get("id")
            nickname = user.get("nickname") or user.get("email", "")
            org_name = user.get("_org_name", org_id)
            logger.info(f"Unblocking user '{nickname}' in org '{org_name}' [ID: {user_id}]")
            self.api_manager.update_user(org_id, user_id, {"isEnabled": True})

    def reset_password(self):
        user = self.get_selected_user()
        if user:
            dialog = ResetPasswordDialog(user.get("nickname"), self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_password, force_change = dialog.get_data()
                org_id = user.get("_org_id")
                user_id = user.get("id")

                nickname = user.get("nickname") or user.get("email", "")
                org_name = user.get("_org_name", org_id)
                logger.info(f"Resetting password for '{nickname}' in org '{org_name}' [ID: {user_id}]")
                self.api_manager.update_user(org_id, user_id, {
                    "password": new_password,
                    "passwordChangeRequired": force_change
                })
                QMessageBox.information(self, "Успех", "Запрос на смену пароля отправлен.")

    def delete_user(self):
        users = self.get_selected_users()
        if not users:
            return

        count = len(users)
        if count > 1:
            msg = f"ВНИМАНИЕ!\nВы действительно хотите НАВСЕГДА удалить {count} выбранных пользователей?"
        else:
            nickname = users[0].get("nickname") or users[0].get("email") or users[0].get("id")
            msg = f"ВНИМАНИЕ!\nВы действительно хотите НАВСЕГДА удалить пользователя '{nickname}'?"

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for user in users:
                org_id = user.get("_org_id")
                user_id = user.get("id")
                nickname = user.get("nickname") or user.get("email", "")
                org_name = user.get("_org_name", org_id)
                logger.info(f"Permanently deleting user '{nickname}' from org '{org_name}' [ID: {user_id}]")
                self.api_manager.delete_user_permanently(org_id, user_id)

    def show_logs(self):
        dialog = LogViewerDialog(self)
        dialog.exec()

    def show_org_context_menu(self, pos):
        item = self.org_list.itemAt(pos)
        if not item:
            return

        org_id = item.data(Qt.ItemDataRole.UserRole)
        org_name = item.text()

        menu = QMenu(self)
        export_active_action = menu.addAction("📄 Выгрузить АКТИВНЫХ пользователей в CSV")
        export_blocked_action = menu.addAction("📄 Выгрузить ЗАБЛОКИРОВАННЫХ пользователей в CSV")
        menu.addSeparator()
        export_all_action = menu.addAction("📄 Выгрузить ВСЕХ пользователей в CSV")

        action = menu.exec(self.org_list.mapToGlobal(pos))
        if action == export_active_action:
            self.export_users_to_csv(org_id, org_name, "active")
        elif action == export_blocked_action:
            self.export_users_to_csv(org_id, org_name, "blocked")
        elif action == export_all_action:
            self.export_users_to_csv(org_id, org_name, "all")

    def export_users_to_csv(self, org_id: str, org_name: str, status_filter: str):
        target_users = []
        for user in self.all_users:
            if org_id != "ALL" and str(user.get("_org_id")) != str(org_id):
                continue

            is_enabled = self.is_user_enabled(user)
            if status_filter == "active" and not is_enabled:
                continue
            if status_filter == "blocked" and is_enabled:
                continue

            target_users.append(user)

        filter_label = "активных" if status_filter == "active" else ("заблокированных" if status_filter == "blocked" else "всех")
        if not target_users:
            QMessageBox.information(
                self,
                "Информация",
                f"Нет {filter_label} пользователей для выгрузки в организации '{org_name}'."
            )
            return

        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        file_filter_tag = "active" if status_filter == "active" else ("blocked" if status_filter == "blocked" else "all")
        clean_org_name = "".join(c for c in org_name if c.isalnum() or c in (" ", "_", "-")).strip()
        default_filename = f"users_{clean_org_name}_{file_filter_tag}_{today_str}.csv"

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить список пользователей в CSV",
            default_filename,
            "CSV Files (*.csv);;All Files (*)"
        )

        if not filepath:
            return

        try:
            with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "ID", "Организация", "ФИО", "Никнейм", "Email", "Статус", "Дата создания", "Дата блокировки"
                ])
                for user in target_users:
                    is_enabled = self.is_user_enabled(user)
                    full_name = f"{user.get('name', {}).get('last', '')} {user.get('name', {}).get('first', '')} {user.get('name', {}).get('middle', '')}".strip()
                    status_text = "Активен" if is_enabled else "Заблокирован"
                    created_at = (user.get("createdAt") or user.get("created_at") or user.get("created") or "")[:10]

                    if not is_enabled:
                        blocked_raw = (
                            user.get("isEnabledUpdatedAt") or
                            user.get("is_enabled_updated_at") or
                            user.get("blocked_at") or
                            user.get("_blocked_at") or
                            user.get("updatedAt") or
                            user.get("updated_at") or
                            ""
                        )
                        blocked_at = blocked_raw[:10] if blocked_raw else "-"
                    else:
                        blocked_at = "-"

                    writer.writerow([
                        str(user.get("id", "")),
                        user.get("_org_name", ""),
                        full_name,
                        user.get("nickname", ""),
                        user.get("email", ""),
                        status_text,
                        created_at,
                        blocked_at
                    ])

            QMessageBox.information(
                self,
                "Успех",
                f"Успешно выгружено {len(target_users)} пользователей в файл:\n{filepath}"
            )
            logger.info(f"Exported {len(target_users)} users ({status_filter}) to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить CSV файл:\n{e}")
