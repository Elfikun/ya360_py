import sys
import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QTabWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QMessageBox, QHeaderView, QAbstractItemView, QDialog
)
from PyQt6.QtCore import Qt, pyqtSlot

from api.manager import ApiManager
from gui.dialogs import CreateUserDialog, ResetPasswordDialog, AutoCleanDialog, LogViewerDialog
from utils.logger import get_logger
from utils.storage import add_to_cache, remove_from_cache

logger = get_logger()

class MainWindow(QMainWindow):
    def __init__(self, tokens: list):
        super().__init__()
        self.setWindowTitle("Yandex 360 Directory Manager")
        self.resize(1200, 800)

        self.api_manager = ApiManager(tokens)
        self.organizations = []
        self.all_users = []  # List of all fetched users

        self.current_org_id = None
        self.current_tab_filter = "All"

        self.setup_ui()
        self.setup_connections()

        # Start initial data fetch
        self.statusBar().showMessage("Fetching organizations...")
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
        sidebar_layout.addWidget(QLabel("<b>Организации</b>"))
        sidebar_layout.addWidget(self.org_list)

        # Stats
        self.stats_label = QLabel("Total: 0\nActive: 0\nDisabled: 0")
        sidebar_layout.addWidget(self.stats_label)

        # Bottom sidebar buttons
        logs_btn = QPushButton("📜 Журнал")
        logs_btn.clicked.connect(self.show_logs)
        sidebar_layout.addWidget(logs_btn)

        main_layout.addLayout(sidebar_layout)

        # ---------------- MAIN AREA ----------------
        right_layout = QVBoxLayout()

        # Search and Filters
        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск (Имя, Email, Никнейм)...")
        self.search_input.textChanged.connect(self.filter_table)
        top_bar.addWidget(self.search_input)

        right_layout.addLayout(top_bar)

        # Tabs for filtering
        self.tabs = QTabWidget()
        self.tabs.addTab(QWidget(), "Все")
        self.tabs.addTab(QWidget(), "Активные")
        self.tabs.addTab(QWidget(), "Заблокированные")
        self.tabs.currentChanged.connect(self.on_tab_changed)
        right_layout.addWidget(self.tabs)

        # Data Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Организация", "ФИО", "Никнейм", "Email", "Статус", "Создан"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.table)

        # Action Buttons
        action_layout = QHBoxLayout()

        self.btn_create = QPushButton("+ Создать")
        self.btn_create.clicked.connect(self.create_user)

        self.btn_toggle_lock = QPushButton("🔒 Блок / Разблок")
        self.btn_toggle_lock.clicked.connect(self.toggle_lock)

        self.btn_reset_pass = QPushButton("🔑 Сброс пароля")
        self.btn_reset_pass.clicked.connect(self.reset_password)

        self.btn_delete = QPushButton("🗑️ Удалить (Soft)")
        self.btn_delete.clicked.connect(self.soft_delete_user)

        self.btn_auto_clean = QPushButton("🧹 Авто-Очистка (>30 дн)")
        self.btn_auto_clean.clicked.connect(self.auto_clean)

        action_layout.addWidget(self.btn_create)
        action_layout.addWidget(self.btn_toggle_lock)
        action_layout.addWidget(self.btn_reset_pass)
        action_layout.addWidget(self.btn_delete)
        action_layout.addWidget(self.btn_auto_clean)

        right_layout.addLayout(action_layout)

        main_layout.addLayout(right_layout)

    def setup_connections(self):
        self.api_manager.orgs_loaded.connect(self.on_orgs_loaded)
        self.api_manager.users_loaded.connect(self.on_users_loaded)
        self.api_manager.user_created.connect(self.on_user_created)
        self.api_manager.user_updated.connect(self.on_user_updated)
        self.api_manager.user_deleted.connect(self.on_user_deleted)
        self.api_manager.error_occurred.connect(self.on_error)
        self.org_list.currentItemChanged.connect(self.on_org_selected)

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

        # Append new users and add custom metadata
        for u in users:
            u['_org_id'] = org_id
            u['_org_name'] = org_name
            self.all_users.append(u)

        self.statusBar().showMessage(f"Loaded users for org {org_name}", 5000)
        self.update_stats()
        self.filter_table()

    @pyqtSlot(dict)
    def on_user_created(self, user):
        logger.info(f"User created: {user.get('nickname')}")
        self.statusBar().showMessage("Пользователь успешно создан!", 5000)
        QMessageBox.information(self, "Успех", f"Пользователь {user.get('nickname')} успешно создан.")
        # Reload users for that org
        # Assuming the API returns the org id in some way, or we just refresh the current view
        if self.current_org_id and self.current_org_id != "ALL":
            self.api_manager.fetch_users(self.current_org_id)
        else:
            # Refresh all (lazy approach, could be optimized)
            for org in self.organizations:
                self.api_manager.fetch_users(org.get("id"))

    @pyqtSlot(dict)
    def on_user_updated(self, user):
        logger.info(f"User updated: {user.get('id')}")
        self.statusBar().showMessage("Данные пользователя обновлены", 5000)
        # We need to refresh the current user list to reflect changes
        if self.current_org_id and self.current_org_id != "ALL":
            self.api_manager.fetch_users(self.current_org_id)
        else:
            # Update the user locally if possible, or refetch
            for i, u in enumerate(self.all_users):
                if u.get('id') == user.get('id'):
                    self.all_users[i].update(user)
                    break
            self.filter_table()
            self.update_stats()

    @pyqtSlot(str, str)
    def on_user_deleted(self, org_id, user_id):
        logger.info(f"User permanently deleted: {user_id}")
        self.statusBar().showMessage("Пользователь удален навсегда", 5000)
        remove_from_cache(user_id)
        self.all_users = [u for u in self.all_users if u.get('id') != user_id]
        self.filter_table()
        self.update_stats()

    @pyqtSlot(str, str)
    def on_error(self, title, message):
        QMessageBox.critical(self, title, message)
        self.statusBar().showMessage(f"Error: {title}")

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

    def update_stats(self):
        total = len(self.all_users)
        active = sum(1 for u in self.all_users if u.get("is_enabled", False))
        disabled = total - active
        self.stats_label.setText(f"Всего: {total}\nАктивные: {active}\nЗаблокированные: {disabled}")

    def filter_table(self):
        search_text = self.search_input.text().lower()

        self.table.setRowCount(0)

        for user in self.all_users:
            # Tab filter
            is_enabled = user.get("is_enabled", False)
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

            self.table.setItem(row, 0, QTableWidgetItem(str(user.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(user.get("_org_name", "")))

            full_name = f"{user.get('name', {}).get('last', '')} {user.get('name', {}).get('first', '')} {user.get('name', {}).get('middle', '')}".strip()
            self.table.setItem(row, 2, QTableWidgetItem(full_name))

            self.table.setItem(row, 3, QTableWidgetItem(user.get("nickname", "")))
            self.table.setItem(row, 4, QTableWidgetItem(user.get("email", "")))

            status = "Активен" if is_enabled else "Заблокирован"
            self.table.setItem(row, 5, QTableWidgetItem(status))

            created_at = user.get("created_at", "")[:10]
            self.table.setItem(row, 6, QTableWidgetItem(created_at))

            # Store full user data in the row
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, user)

    def get_selected_user(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите пользователя.")
            return None
        # Get data from the first column of the selected row
        row = selected_items[0].row()
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def create_user(self):
        if not self.organizations:
            QMessageBox.warning(self, "Внимание", "Нет доступных организаций.")
            return

        dialog = CreateUserDialog(self.organizations, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            org_id, data = dialog.get_data()
            logger.info(f"Creating user {data.get('nickname')} in org {org_id}")
            self.api_manager.create_user(org_id, data)

    def toggle_lock(self):
        user = self.get_selected_user()
        if user:
            org_id = user.get("_org_id")
            user_id = user.get("id")
            new_status = not user.get("is_enabled", False)

            logger.info(f"Toggling lock for {user_id} to {new_status}")
            self.api_manager.update_user(org_id, user_id, {"is_enabled": new_status})

    def reset_password(self):
        user = self.get_selected_user()
        if user:
            dialog = ResetPasswordDialog(user.get("nickname"), self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_password, force_change = dialog.get_data()
                org_id = user.get("_org_id")
                user_id = user.get("id")

                logger.info(f"Resetting password for {user_id}")
                self.api_manager.update_user(org_id, user_id, {
                    "password": new_password,
                    "is_password_change_required": force_change
                })
                QMessageBox.information(self, "Успех", "Запрос на смену пароля отправлен.")

    def soft_delete_user(self):
        user = self.get_selected_user()
        if user:
            reply = QMessageBox.question(self, 'Подтверждение',
                                         f"Вы уверены, что хотите заблокировать и перенести в корзину пользователя {user.get('nickname')}?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                org_id = user.get("_org_id")
                user_id = user.get("id")

                # Block user via API
                self.api_manager.block_user(org_id, user_id)

                # Add to local cache for 30-day tracking
                now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
                cache_data = {
                    "nickname": user.get("nickname"),
                    "email": user.get("email"),
                    "org_id": org_id,
                    "org_name": user.get("_org_name"),
                    "deleted_at": now_str,
                    "deleted_by": "Admin (App)"
                }
                add_to_cache(user_id, cache_data)
                logger.info(f"User {user_id} soft-deleted and added to cache.")
                self.statusBar().showMessage("Пользователь заблокирован и добавлен в корзину.")

    def auto_clean(self):
        dialog = AutoCleanDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            candidates = dialog.get_candidates()
            for cand in candidates:
                logger.info(f"Permanently deleting {cand['user_id']}")
                self.api_manager.delete_user_permanently(cand["org_id"], cand["user_id"])
            QMessageBox.information(self, "Успех", f"Запущено удаление {len(candidates)} пользователей.")

    def show_logs(self):
        dialog = LogViewerDialog(self)
        dialog.exec()
