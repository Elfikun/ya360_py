from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from typing import Dict, Any, List
from api.client import Yandex360Client
from utils.logger import get_logger

logger = get_logger()

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            self.signals.error.emit((e, traceback_str))
            logger.error(f"Worker error: {e}\n{traceback_str}")
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class ApiManager(QObject):
    # Signals to update GUI
    orgs_loaded = pyqtSignal(list)
    users_loaded = pyqtSignal(str, list)  # org_id, users_list
    user_created = pyqtSignal(dict)
    user_updated = pyqtSignal(dict)
    user_deleted = pyqtSignal(str, str) # org_id, user_id
    error_occurred = pyqtSignal(str, str) # title, error_message

    def __init__(self, tokens: List[str]):
        super().__init__()
        self.tokens = tokens
        self.clients = {token: Yandex360Client(token) for token in tokens}
        self.org_to_token_map = {} # Maps org_id to the token used to access it
        self.thread_pool = QThreadPool()
        logger.info(f"ApiManager initialized with {len(tokens)} tokens and max thread count: {self.thread_pool.maxThreadCount()}")

    def set_tokens(self, tokens: List[str]):
        self.tokens = tokens
        self.clients = {token: Yandex360Client(token) for token in tokens}

    def _get_client_for_org(self, org_id: str) -> Yandex360Client:
        token = self.org_to_token_map.get(str(org_id))
        if token and token in self.clients:
            return self.clients[token]
        # Fallback to first client if not mapped (shouldn't happen ideally)
        if self.clients:
            return next(iter(self.clients.values()))
        raise ValueError(f"No client configured for org_id {org_id}")

    def fetch_orgs(self):
        # We need a custom worker to fetch orgs across all tokens
        def _fetch_all_orgs():
            all_orgs = []
            for token, client in self.clients.items():
                try:
                    orgs = client.get_orgs()
                    for org in orgs:
                        org_id_str = str(org.get("id"))
                        self.org_to_token_map[org_id_str] = token
                        # Optionally annotate the org dict with token hint if needed,
                        # but keeping it in manager map is cleaner.
                        all_orgs.append(org)
                except Exception as e:
                    logger.error(f"Failed to fetch orgs for a token: {e}")
                    # Allow partial loading but log error
            return all_orgs

        worker = Worker(_fetch_all_orgs)
        worker.signals.result.connect(self.orgs_loaded.emit)
        worker.signals.error.connect(lambda err: self.error_occurred.emit("Failed to fetch organizations", str(err[0])))
        self.thread_pool.start(worker)

    def fetch_users(self, org_id: str):
        client = self._get_client_for_org(org_id)
        worker = Worker(client.get_users, org_id)
        worker.signals.result.connect(lambda users: self.users_loaded.emit(org_id, users))
        worker.signals.error.connect(lambda err: self.error_occurred.emit("Failed to fetch users", str(err[0])))
        self.thread_pool.start(worker)

    def create_user(self, org_id: str, user_data: Dict[str, Any]):
        client = self._get_client_for_org(org_id)
        worker = Worker(client.create_user, org_id, user_data)
        worker.signals.result.connect(self.user_created.emit)
        worker.signals.error.connect(lambda err: self.error_occurred.emit("Failed to create user", str(err[0])))
        self.thread_pool.start(worker)

    def update_user(self, org_id: str, user_id: str, user_data: Dict[str, Any]):
        client = self._get_client_for_org(org_id)
        worker = Worker(client.update_user, org_id, user_id, user_data)
        worker.signals.result.connect(self.user_updated.emit)
        worker.signals.error.connect(lambda err: self.error_occurred.emit("Failed to update user", str(err[0])))
        self.thread_pool.start(worker)

    def block_user(self, org_id: str, user_id: str):
        self.update_user(org_id, user_id, {"is_enabled": False})

    def reset_password(self, org_id: str, user_id: str, new_password: str):
        self.update_user(org_id, user_id, {
            "password": new_password,
            "is_password_change_required": True
        })

    def delete_user_permanently(self, org_id: str, user_id: str):
        client = self._get_client_for_org(org_id)
        worker = Worker(client.delete_user, org_id, user_id)
        worker.signals.result.connect(lambda _: self.user_deleted.emit(org_id, user_id))
        worker.signals.error.connect(lambda err: self.error_occurred.emit("Failed to delete user", str(err[0])))
        self.thread_pool.start(worker)
