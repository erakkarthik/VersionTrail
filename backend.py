import os
import sys
import time
import shutil
import logging
import ctypes
import threading
from datetime import datetime
from collections import defaultdict

from PyQt6.QtCore import QThread, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ──────────────────────────────────────────────────────────────
# LOGGING BRIDGE (Thread-Safe)
# ──────────────────────────────────────────────────────────────
class LogBridge:
    def __init__(self, ui_signal, file_logger=None):
        self.ui_signal = ui_signal
        self.file_logger = file_logger

    def __call__(self, msg: str):
        self.ui_signal.emit(msg)
        if self.file_logger:
            self.file_logger.info(msg)


# ──────────────────────────────────────────────────────────────
# WATCHDOG EVENT HANDLER
# ──────────────────────────────────────────────────────────────
class BackupHandler(FileSystemEventHandler):
    def __init__(self, watch_path, backup_dir, log_callback, stop_event, target_file=None, recursive=True):
        super().__init__()
        self.watch_path = os.path.abspath(watch_path)
        self.backup_dir = os.path.abspath(backup_dir)
        self.log = log_callback
        self.stop_event = stop_event
        self.target_file = os.path.abspath(target_file) if target_file else None
        self.recursive = recursive
        self.file_state = {}
        self.last_backup_time = defaultdict(float)
        self.debounce_secs = 1.5
        self.lock = threading.Lock()

    def _is_hidden_or_system(self, path: str) -> bool:
        if sys.platform == "win32":
            try:
                attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
                return attrs != -1 and (attrs & 0x6) != 0
            except Exception:
                return False
        return os.path.basename(path).startswith(".")

    def on_any_event(self, event):
        if self.stop_event.is_set() or event.is_directory:
            return
        filepath = os.path.abspath(event.src_path)
        if self.target_file and filepath != self.target_file:
            return
        if self._is_hidden_or_system(filepath):
            return
        try:
            stat = os.stat(filepath)
        except FileNotFoundError:
            return

        mtime, size = stat.st_mtime, stat.st_size
        with self.lock:
            prev_mtime, prev_size = self.file_state.get(filepath, (None, None))
            if mtime == prev_mtime and size == prev_size:
                return
            now = time.time()
            if now - self.last_backup_time[filepath] < self.debounce_secs:
                return
            self.file_state[filepath] = (mtime, size)
            self.last_backup_time[filepath] = now

        threading.Thread(target=self._perform_backup, args=(filepath,), daemon=True).start()

    def _perform_backup(self, filepath: str):
        try:
            name, ext = os.path.splitext(os.path.basename(filepath))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{name}_{timestamp}{ext}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            if os.path.exists(backup_path):
                counter = 2
                while True:
                    backup_name = f"{name}_{timestamp}_v{counter}{ext}"
                    backup_path = os.path.join(self.backup_dir, backup_name)
                    if not os.path.exists(backup_path):
                        break
                    counter += 1
            shutil.copy2(filepath, backup_path)
            self.log(f"[INFO] Backed up: {os.path.basename(filepath)} -> {backup_name}")
        except PermissionError:
            self.log(f"[WARN] Skipped: {os.path.basename(filepath)} - File in use/locked")
        except Exception as e:
            self.log(f"[ERROR] Failed backup {os.path.basename(filepath)}: {e}")


# ──────────────────────────────────────────────────────────────
# MONITOR WORKER THREAD
# ──────────────────────────────────────────────────────────────
class MonitorWorker(QThread):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)

    def __init__(self, source_path, backup_path, scope, file_logger=None):
        super().__init__()
        self.source_path = os.path.abspath(source_path)
        self.backup_path = os.path.abspath(backup_path)
        self.scope = scope  # 'file', 'folder', 'recursive'
        self.stop_event = threading.Event()
        self.observer = None
        self.file_logger = file_logger

    def run(self):
        os.makedirs(self.backup_path, exist_ok=True)
        watch_dir = os.path.dirname(self.source_path) if self.scope == 'file' else self.source_path
        target_file = self.source_path if self.scope == 'file' else None
        recursive = self.scope == 'recursive'

        log_cb = LogBridge(self.log_signal, self.file_logger)
        handler = BackupHandler(watch_dir, self.backup_path, log_cb, self.stop_event, target_file, recursive)

        self.observer = Observer()
        self.observer.schedule(handler, watch_dir, recursive=recursive)
        self.observer.start()

        self.status_signal.emit("Running")
        self.log_signal.emit("[INFO] Monitor started.")

        while not self.stop_event.is_set():
            self.stop_event.wait(0.2)

        self.observer.stop()
        self.observer.join()
        self.status_signal.emit("Stopped")
        self.log_signal.emit("[INFO] Monitor stopped.")

    def stop(self):
        self.stop_event.set()


# ──────────────────────────────────────────────────────────────
# LOGGING SETUP
# ──────────────────────────────────────────────────────────────
def setup_logging():
    logger = logging.getLogger("VersionTrail")
    logger.setLevel(logging.INFO)
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    formatter = logging.Formatter("%(message)s")
    log_path = os.path.join(os.getcwd(), "versiontrail.log")
    try:
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        pass
    return logger