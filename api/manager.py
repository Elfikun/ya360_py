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
        self.setAutoDelete(False)

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
        self.active_workers = set()
        logger.info(f"ApiManager initialized with {len(tokens)} tokens and max thread count: {self.thread_pool.maxThreadCount()}")

    def _start_worker(self, worker: Worker):
        self.active_workers.add(worker)
        worker.signals.finished.connect(lambda: self.active_workers.discard(worker))
        self.thread_pool.start(worker)

    def _get_client_for_org(self, org_id: str) -> Yandex360Client:
        token = self.org_to_token_map.get(str(org_id))
        if token and token in self.clients:
            return self.clients[token]
        raise ValueError(
            f"No client mapped for org_id '{org_id}'. "
            f"Ensure organizations are loaded before performing actions."
        )

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
                        all_orgs.append(org)
                except Exception as e:
                    logger.error(f"Failed to fetch orgs for a token: {e}")
            return all_orgs

        worker = Worker(_fetch_all_orgs)
        worker.signals.result.connect(self.orgs_loaded.emit)
        worker.signals.error.connect(lambda err: self.error_occurred.emit("Failed to fetch organizations", str(err[0])))
        self._start_worker(worker)

    def fetch_users(self, org_id: Any):
        client = self._get_client_for_org(org_id)
        worker = Worker(client.get_users, str(org_id))
        worker.signals.result.connect(lambda users: self.users_loaded.emit(str(org_id), users))
        worker.signals.error.connect(lambda err: self.error_occurred.emit("Failed to fetch users", str(err[0])))
        self._start_worker(worker)

    def create_user(self, org_id: Any, user_data: Dict[str, Any]):
        client = self._get_client_for_org(org_id)
        worker = Worker(client.create_user, str(org_id), user_data)
        worker.signals.result.connect(self.user_created.emit)
        worker.signals.error.connect(lambda err: self.error_occurred.emit("Failed to create user", str(err[0])))
        self._start_worker(worker)

    def update_user(self, org_id: Any, user_id: Any, user_data: Dict[str, Any]):
        client = self._get_client_for_org(org_id)
        worker = Worker(client.update_user, str(org_id), str(user_id), user_data)
        worker.signals.result.connect(self.user_updated.emit)
        worker.signals.error.connect(lambda err: self.error_occurred.emit("Failed to update user", str(err[0])))
        self._start_worker(worker)

    def block_user(self, org_id: Any, user_id: Any):
        self.update_user(org_id, user_id, {"isEnabled": False})

    def delete_user_permanently(self, org_id: Any, user_id: Any):
        client = self._get_client_for_org(org_id)
        worker = Worker(client.delete_user, str(org_id), str(user_id))
        worker.signals.result.connect(lambda _: self.user_deleted.emit(str(org_id), str(user_id)))
        worker.signals.error.connect(lambda err: self.error_occurred.emit("Failed to delete user", str(err[0])))
        self._start_worker(worker)
