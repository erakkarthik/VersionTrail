import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QButtonGroup, QFileDialog,
    QPlainTextEdit, QSystemTrayIcon, QMenu, QMessageBox, QStyle,
    QFrame, QComboBox, QLabel, QAbstractButton
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont, QShortcut, QKeySequence, QPainter, QColor, QPen

from backend import MonitorWorker, setup_logging


APP_VERSION = "1.0.0"
APP_NAME = "VersionTrail"

# ── Palette ────────────────────────────────────────────────────
C_TEAL        = "#1D9E75"
C_TEAL_DARK   = "#0F6E56"
C_TEAL_BG     = "#E1F5EE"
C_TEAL_BORDER = "#5DCAA5"

C_RED_BG      = "#FCEBEB"
C_RED_TEXT    = "#A32D2D"
C_RED_BORDER  = "#F09595"

C_BG_PRIMARY   = "#FFFFFF"
C_BG_SECONDARY = "#F5F5F3"
C_BORDER_SOFT  = "#E0DED8"
C_BORDER_MED   = "#C8C6C0"
C_TEXT_PRIMARY = "#1A1A18"
C_TEXT_MUTED   = "#6B6A65"
C_TEXT_HINT    = "#9E9C97"
C_DOT_IDLE     = "#888780"
C_DOT_RUN      = C_TEAL
C_DOT_ERR      = "#E24B4A"

FONT_UI   = "Segoe UI"
FONT_MONO = "Consolas"


# ──────────────────────────────────────────────────────────────
# CUSTOM MODE BUTTON  (card-style radio alternative)
# ──────────────────────────────────────────────────────────────
class ModeButton(QAbstractButton):
    """Checkable card button used for scope selection."""

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setText(label)
        self.setCheckable(True)
        self.setFixedHeight(38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont(FONT_UI, 9))

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)

        if self.isChecked():
            p.setBrush(QColor(C_TEAL_BG))
            p.setPen(QPen(QColor(C_TEAL), 2))
        elif self.underMouse():
            p.setBrush(QColor(C_BG_SECONDARY))
            p.setPen(QPen(QColor(C_BORDER_MED), 1))
        else:
            p.setBrush(QColor(C_BG_PRIMARY))
            p.setPen(QPen(QColor(C_BORDER_SOFT), 1))

        p.drawRoundedRect(rect, 6, 6)

        text_color = QColor(C_TEAL_DARK) if self.isChecked() else QColor(C_TEXT_MUTED)
        p.setPen(text_color)
        p.setFont(self.font())
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, self.text())
        p.end()

    def sizeHint(self):
        return QSize(120, 38)


# ──────────────────────────────────────────────────────────────
# STATUS DOT
# ──────────────────────────────────────────────────────────────
class StatusDot(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self.set_color(C_DOT_IDLE)

    def set_color(self, color: str):
        self.setStyleSheet(f"border-radius: 5px; background: {color};")


# ──────────────────────────────────────────────────────────────
# GLOBAL STYLESHEET
# ──────────────────────────────────────────────────────────────
GLOBAL_QSS = f"""
QMainWindow, QWidget {{
    background: {C_BG_PRIMARY};
    color: {C_TEXT_PRIMARY};
    font-family: "{FONT_UI}";
    font-size: 13px;
}}

/* ── Menu bar ── */
QMenuBar {{
    background: {C_BG_PRIMARY};
    color: {C_TEXT_PRIMARY};
    border-bottom: 1px solid {C_BORDER_SOFT};
    padding: 2px 4px;
    font-size: 13px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 4px 10px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background: {C_BG_SECONDARY};
}}
QMenu {{
    background: {C_BG_PRIMARY};
    border: 1px solid {C_BORDER_SOFT};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 20px 6px 12px;
    border-radius: 4px;
    color: {C_TEXT_PRIMARY};
}}
QMenu::item:selected {{
    background: {C_BG_SECONDARY};
}}
QMenu::separator {{
    height: 1px;
    background: {C_BORDER_SOFT};
    margin: 4px 8px;
}}

/* ── Cards / Frames ── */
QFrame#configCard, QFrame#logCard {{
    background: {C_BG_PRIMARY};
    border: 1px solid {C_BORDER_SOFT};
    border-radius: 12px;
}}

/* ── Section labels (UPPERCASE small caps) ── */
QLabel#sectionLabel {{
    color: {C_TEXT_MUTED};
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
}}

/* ── Path inputs ── */
QLineEdit#pathEdit {{
    background: {C_BG_SECONDARY};
    border: 1px solid {C_BORDER_SOFT};
    border-radius: 6px;
    padding: 0 10px;
    color: {C_TEXT_MUTED};
    font-size: 12px;
    min-height: 34px;
    max-height: 34px;
}}
QLineEdit#pathEdit:focus {{
    border: 1px solid {C_TEAL};
    color: {C_TEXT_PRIMARY};
}}

/* ── Browse buttons ── */
QPushButton#browseBtn {{
    background: {C_BG_PRIMARY};
    border: 1px solid {C_BORDER_MED};
    border-radius: 6px;
    padding: 0 14px;
    color: {C_TEXT_PRIMARY};
    font-size: 12px;
    min-height: 34px;
    max-height: 34px;
}}
QPushButton#browseBtn:hover {{
    background: {C_BG_SECONDARY};
    border-color: {C_TEXT_HINT};
}}

/* ── Primary action: Start ── */
QPushButton#startBtn {{
    background: {C_TEAL};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0 20px;
    font-weight: 600;
    font-size: 13px;
    min-height: 34px;
    max-height: 34px;
}}
QPushButton#startBtn:hover {{ background: {C_TEAL_DARK}; }}
QPushButton#startBtn:disabled {{
    background: {C_BORDER_SOFT};
    color: {C_TEXT_HINT};
    border: none;
}}

/* ── Secondary action: Stop — red when active, grey when disabled ── */
QPushButton#stopBtn {{
    background: {C_RED_BG};
    color: {C_RED_TEXT};
    border: 1px solid {C_RED_BORDER};
    border-radius: 6px;
    padding: 0 20px;
    font-size: 13px;
    font-weight: 600;
    min-height: 34px;
    max-height: 34px;
}}
QPushButton#stopBtn:hover {{
    background: #F7C1C1;
    color: {C_RED_TEXT};
    border-color: {C_DOT_ERR};
}}
QPushButton#stopBtn:disabled {{
    background: {C_BG_SECONDARY};
    color: {C_TEXT_HINT};
    border: 1px solid {C_BORDER_SOFT};
    font-weight: normal;
}}

/* ── Stat pills ── */
QFrame#statPill {{
    background: {C_BG_PRIMARY};
    border: 1px solid {C_BORDER_SOFT};
    border-radius: 6px;
}}
QLabel#statPillLabel {{
    color: {C_TEXT_MUTED};
    font-size: 11px;
    background: transparent;
    border: none;
}}
QLabel#statPillValue {{
    color: {C_TEXT_PRIMARY};
    font-size: 11px;
    font-weight: 600;
    background: transparent;
    border: none;
}}

/* ── Status bar pill ── */
QFrame#statusBar {{
    background: {C_BG_SECONDARY};
    border: 1px solid {C_BORDER_SOFT};
    border-radius: 8px;
}}
QFrame#statusBar QLabel {{
    background: transparent;
    border: none;
}}

/* ── Filter combo ── */
QComboBox {{
    background: transparent;
    border: 1px solid {C_BORDER_MED};
    border-radius: 6px;
    padding: 0 10px;
    min-height: 26px;
    max-height: 26px;
    font-size: 12px;
    color: {C_TEXT_PRIMARY};
}}
QComboBox:hover {{
    background: {C_BG_PRIMARY};
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {C_BG_PRIMARY};
    border: 1px solid {C_BORDER_SOFT};
    border-radius: 6px;
    selection-background-color: {C_BG_SECONDARY};
    color: {C_TEXT_PRIMARY};
}}

/* ── Log pane ── */
QPlainTextEdit#logPane {{
    background: {C_BG_SECONDARY};
    border: 1px solid {C_BORDER_SOFT};
    border-radius: 8px;
    padding: 8px;
    font-family: "{FONT_MONO}";
    font-size: 11px;
    color: {C_TEXT_MUTED};
}}

/* ── Inline error labels ── */
QLabel#errorLabel {{
    color: {C_DOT_ERR};
    font-size: 11px;
}}
"""


# ──────────────────────────────────────────────────────────────
# MAIN WINDOW
# ──────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(580, 560)
        self.setMinimumSize(520, 480)
        self.worker = None
        self.all_logs = []
        self.log_filter = "All Events"
        self._backup_count = 0
        self._src_touched = False
        self._bak_touched = False
        self.logger = setup_logging()

        self.setStyleSheet(GLOBAL_QSS)
        self.setup_ui()
        self.setup_menu()
        self.setup_tray()
        self.setup_shortcuts()
        self.update_status("Idle")

    # ── UI ────────────────────────────────────────────────────
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 10, 14, 14)
        root.setSpacing(8)

        # ── Config card ──────────────────────────────────────
        config_card = QFrame()
        config_card.setObjectName("configCard")
        cc = QVBoxLayout(config_card)
        cc.setContentsMargins(14, 10, 14, 10)
        cc.setSpacing(4)

        # Mode selector
        mode_lbl = QLabel("MONITOR MODE")
        mode_lbl.setObjectName("sectionLabel")
        cc.addWidget(mode_lbl)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(6)
        self.btn_file      = ModeButton("Single File")
        self.btn_folder    = ModeButton("Folder (Shallow)")
        self.btn_recursive = ModeButton("Folder (Recursive)")

        self.scope_group = QButtonGroup(self)
        self.scope_group.setExclusive(True)
        for btn in [self.btn_file, self.btn_folder, self.btn_recursive]:
            self.scope_group.addButton(btn)
            mode_row.addWidget(btn)
            btn.clicked.connect(self._on_mode_selected)
        cc.addLayout(mode_row)

        # Source
        self.src_lbl = QLabel("SOURCE")
        self.src_lbl.setObjectName("sectionLabel")
        self.src_lbl.setContentsMargins(0, 4, 0, 0)
        cc.addWidget(self.src_lbl)

        src_row = QHBoxLayout()
        src_row.setSpacing(6)
        self.src_edit = QLineEdit()
        self.src_edit.setObjectName("pathEdit")
        self.src_edit.setReadOnly(True)
        self.src_edit.setPlaceholderText("No source selected")
        self.src_btn = QPushButton("Browse…")
        self.src_btn.setObjectName("browseBtn")
        self.src_btn.setFixedWidth(90)
        self.src_btn.clicked.connect(self.browse_source)
        src_row.addWidget(self.src_edit)
        src_row.addWidget(self.src_btn)
        self.src_row_widget = QWidget()
        self.src_row_widget.setLayout(src_row)
        cc.addWidget(self.src_row_widget)

        self.src_error = QLabel("")
        self.src_error.setObjectName("errorLabel")
        self.src_error.setFixedHeight(14)
        cc.addWidget(self.src_error)

        # Destination
        self.dst_lbl = QLabel("DESTINATION")
        self.dst_lbl.setObjectName("sectionLabel")
        self.dst_lbl.setContentsMargins(0, 2, 0, 0)
        cc.addWidget(self.dst_lbl)

        bak_row = QHBoxLayout()
        bak_row.setSpacing(6)
        self.bak_edit = QLineEdit()
        self.bak_edit.setObjectName("pathEdit")
        self.bak_edit.setReadOnly(True)
        self.bak_edit.setPlaceholderText("No destination selected")
        self.bak_btn = QPushButton("Browse…")
        self.bak_btn.setObjectName("browseBtn")
        self.bak_btn.setFixedWidth(90)
        self.bak_btn.clicked.connect(self.browse_backup)
        bak_row.addWidget(self.bak_edit)
        bak_row.addWidget(self.bak_btn)
        self.bak_row_widget = QWidget()
        self.bak_row_widget.setLayout(bak_row)
        cc.addWidget(self.bak_row_widget)

        self.bak_error = QLabel("")
        self.bak_error.setObjectName("errorLabel")
        self.bak_error.setFixedHeight(14)
        cc.addWidget(self.bak_error)

        # Action buttons (no separator — tighter)
        act_row = QHBoxLayout()
        act_row.setContentsMargins(0, 4, 0, 0)
        act_row.addStretch()
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setFixedWidth(110)
        self.stop_btn.clicked.connect(self.stop_monitor)
        self.stop_btn.setEnabled(False)

        self.start_btn = QPushButton("▶  Start Monitor")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setFixedWidth(155)
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_monitor)

        act_row.addWidget(self.stop_btn)
        act_row.addSpacing(8)
        act_row.addWidget(self.start_btn)
        self.act_row_widget = QWidget()
        self.act_row_widget.setLayout(act_row)
        cc.addWidget(self.act_row_widget)

        root.addWidget(config_card)

        # ── Status + stats bar ────────────────────────────────
        status_bar = QFrame()
        status_bar.setObjectName("statusBar")
        sb_layout = QVBoxLayout(status_bar)
        sb_layout.setContentsMargins(12, 8, 14, 8)
        sb_layout.setSpacing(6)

        # Row 1: dot + status text + filter
        sb_row = QHBoxLayout()
        sb_row.setSpacing(8)

        self.status_dot = StatusDot()
        self.status_label = QLabel("Idle")
        self.status_label.setFont(QFont(FONT_UI, 9))
        self.status_label.setStyleSheet(f"color: {C_TEXT_MUTED}; background: transparent; border: none;")
        sb_row.addWidget(self.status_dot)
        sb_row.addWidget(self.status_label)
        sb_row.addStretch()

        filter_lbl = QLabel("Filter:")
        filter_lbl.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 12px; background: transparent; border: none;")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Events", "Changes Only", "Errors Only"])
        self.filter_combo.currentTextChanged.connect(self.apply_log_filter)
        sb_row.addWidget(filter_lbl)
        sb_row.addWidget(self.filter_combo)
        sb_layout.addLayout(sb_row)

        # Row 2: stats pills
        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)

        self.stat_files = self._make_stat_pill("📄 Files monitored", "0")
        self.stat_folders = self._make_stat_pill("📁 Folders", "0")
        self.stat_backups = self._make_stat_pill("💾 Backups made", "0")

        for pill in [self.stat_files, self.stat_folders, self.stat_backups]:
            stats_row.addWidget(pill)
        stats_row.addStretch()
        sb_layout.addLayout(stats_row)

        root.addWidget(status_bar)

        # ── Log card ─────────────────────────────────────────
        log_card = QFrame()
        log_card.setObjectName("logCard")
        lc = QVBoxLayout(log_card)
        lc.setContentsMargins(12, 10, 12, 12)
        lc.setSpacing(8)

        self.log_text = QPlainTextEdit()
        self.log_text.setObjectName("logPane")
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont(FONT_MONO, 10))
        self.log_text.setPlaceholderText("Monitoring logs will appear here…")
        lc.addWidget(self.log_text)

        root.addWidget(log_card, stretch=1)

        # Validation connections
        self.src_edit.textChanged.connect(self.validate_inputs)
        self.bak_edit.textChanged.connect(self.validate_inputs)

        # Hide source/dest until a mode is chosen
        self._set_paths_visible(False)

    def _set_paths_visible(self, visible: bool):
        for w in [self.src_lbl, self.src_row_widget, self.src_error,
                  self.dst_lbl, self.bak_row_widget, self.bak_error,
                  self.act_row_widget]:
            w.setVisible(visible)

    def _on_mode_selected(self):
        self._set_paths_visible(True)
        self.validate_inputs()

    def _make_stat_pill(self, label: str, value: str) -> QFrame:
        """Small label+value pill for the stats row."""
        pill = QFrame()
        pill.setObjectName("statPill")
        row = QHBoxLayout(pill)
        row.setContentsMargins(8, 3, 10, 3)
        row.setSpacing(6)
        lbl = QLabel(label)
        lbl.setObjectName("statPillLabel")
        val = QLabel(value)
        val.setObjectName("statPillValue")
        row.addWidget(lbl)
        row.addWidget(val)
        pill._value_label = val
        return pill

    def _update_stats(self):
        """Recount monitored files/folders from the source path."""
        src = self.src_edit.text().strip()
        scope = self._scope()
        files, folders, backups = 0, 0, self._backup_count

        if src and os.path.exists(src) and self.worker and self.worker.isRunning():
            if scope == "file":
                files = 1
                folders = 0
            elif scope == "folder":
                # shallow: only immediate files are watched, no subfolders
                try:
                    for e in os.scandir(src):
                        if e.is_file():
                            files += 1
                except Exception:
                    pass
                folders = 0
            elif scope == "recursive":
                try:
                    for _, dirs, fls in os.walk(src):
                        files += len(fls)
                        folders += len(dirs)
                except Exception:
                    pass

        self.stat_files._value_label.setText(str(files))
        self.stat_folders._value_label.setText(str(folders))
        self.stat_backups._value_label.setText(str(backups))

    # ── Menu bar ──────────────────────────────────────────────
    def setup_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit Completely", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.force_exit)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Help")
        quick_start = QAction("Quick Start Guide", self)
        quick_start.triggered.connect(self.show_quick_start)
        help_menu.addAction(quick_start)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    # ── System tray ───────────────────────────────────────────
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray_icon.setToolTip(f"{APP_NAME} - Idle")
        self.tray_icon.show()

        tray_menu = QMenu()
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show_normal)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        exit_tray = QAction("Exit Completely", self)
        exit_tray.triggered.connect(self.force_exit)
        tray_menu.addAction(exit_tray)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_normal()

    def show_normal(self):
        self.show()
        self.setWindowState(Qt.WindowState.WindowActive)

    def force_exit(self):
        self.hide()
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        self.tray_icon.hide()
        QApplication.quit()

    # ── Shortcuts ─────────────────────────────────────────────
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Alt+S"), self, self.start_monitor)
        QShortcut(QKeySequence("Alt+O"), self, self.stop_monitor)

    # ── Status ────────────────────────────────────────────────
    def update_status(self, state: str):
        dot_colors = {"Idle": C_DOT_IDLE, "Running": C_DOT_RUN, "Error": C_DOT_ERR}
        self.status_dot.set_color(dot_colors.get(state, C_DOT_IDLE))
        self.status_label.setText(
            {"Idle": "Idle — waiting to start", "Running": "Running", "Stopped": "Idle — monitor stopped"}.get(state, state)
        )
        self.tray_icon.setToolTip(f"{APP_NAME} - {state}")

    # ── Validation ────────────────────────────────────────────
    def _scope(self) -> str:
        if self.btn_file.isChecked():
            return "file"
        if self.btn_recursive.isChecked():
            return "recursive"
        if self.btn_folder.isChecked():
            return "folder"
        return ""  # nothing selected yet

    def validate_inputs(self):
        src   = self.src_edit.text().strip()
        bak   = self.bak_edit.text().strip()
        scope = self._scope()

        self.src_error.setText("")
        self.bak_error.setText("")
        valid = True

        if not scope:
            valid = False

        if not src:
            if self._src_touched:
                self.src_error.setText("Please select a source.")
            valid = False
        elif not os.path.exists(src):
            self.src_error.setText("Source path does not exist.")
            valid = False
        elif scope not in ("file", "") and not os.path.isdir(src):
            self.src_error.setText("Source must be a folder for this mode.")
            valid = False
        elif scope == "file" and not os.path.isfile(src):
            self.src_error.setText("Source must be a file.")
            valid = False

        if not bak:
            if self._bak_touched:
                self.bak_error.setText("Please select a destination.")
            valid = False
        elif not os.path.isdir(bak):
            self.bak_error.setText("Destination must be an existing folder.")
            valid = False
        elif src and os.path.abspath(src) == os.path.abspath(bak):
            self.bak_error.setText("Source and destination cannot be the same.")
            valid = False
        elif scope == "recursive" and src and os.path.abspath(bak).startswith(os.path.abspath(src) + os.sep):
            self.bak_error.setText("Destination cannot be inside source (infinite loop risk).")
            valid = False

        self.start_btn.setEnabled(valid)

    # ── File dialogs ──────────────────────────────────────────
    def browse_source(self):
        if self.btn_file.isChecked():
            path, _ = QFileDialog.getOpenFileName(self, "Select File")
        else:
            path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self._src_touched = True
            self.src_edit.setText(path)

    def browse_backup(self):
        path = QFileDialog.getExistingDirectory(self, "Select Backup Folder")
        if path:
            self._bak_touched = True
            self.bak_edit.setText(path)

    # ── Monitor control ───────────────────────────────────────
    def start_monitor(self):
        src = self.src_edit.text().strip()
        bak = self.bak_edit.text().strip()
        if not src or not bak:
            return

        scope = self._scope()
        self.worker = MonitorWorker(src, bak, scope, self.logger)
        self.worker.log_signal.connect(self.append_log)
        self.worker.status_signal.connect(self.update_status)
        self.worker.start()

        self.logger.info(f"[INFO] Monitor started: {src} -> {bak} ({scope})")
        self._backup_count = 0
        self._update_stats()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_monitor(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.logger.info("[INFO] Monitor manually stopped.")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._backup_count = 0
        self._update_stats()
        self.update_status("Idle")

    # ── Logging ───────────────────────────────────────────────
    def append_log(self, msg: str):
        self.all_logs.append(msg)
        if "[INFO] Backed up:" in msg:
            self._backup_count += 1
        self._update_stats()
        self.apply_log_filter()

    def apply_log_filter(self):
        self.log_filter = self.filter_combo.currentText()
        self.log_text.clear()
        for log in self.all_logs:
            if self.log_filter == "All Events":
                self.log_text.appendPlainText(log)
            elif self.log_filter == "Changes Only" and "[INFO] Backed up:" in log:
                self.log_text.appendPlainText(log)
            elif self.log_filter == "Errors Only" and ("[WARN]" in log or "[ERROR]" in log):
                self.log_text.appendPlainText(log)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    # ── Dialogs ───────────────────────────────────────────────
    def show_quick_start(self):
        text = (
            f"<b>Quick Start Guide</b><br><br>"
            f"1. <b>Select Source:</b> Choose a file or folder to monitor.<br>"
            f"2. <b>Select Destination:</b> Choose where backups will be saved.<br>"
            f"3. <b>Choose Mode:</b><br>"
            f"&nbsp;&nbsp;• Single File: Tracks one file.<br>"
            f"&nbsp;&nbsp;• Folder (Shallow): Tracks immediate contents only.<br>"
            f"&nbsp;&nbsp;• Folder (Recursive): Tracks folder + all subfolders.<br>"
            f"4. <b>Start Monitor:</b> Begins real-time backup on save.<br><br>"
            f"<i>Logs show every change. Use the filter dropdown to focus on errors or backups.</i>"
        )
        QMessageBox.information(self, "Quick Start", text)

    def show_about(self):
        text = (
            f"<b>{APP_NAME}</b><br>"
            f"Version: {APP_VERSION}<br>"
            f"License: MIT License<br><br>"
            f"Real-time file backup utility with change detection,<br>"
            f"debounced saves, and system tray support."
        )
        QMessageBox.about(self, "About", text)

    # ── Window close → tray ───────────────────────────────────
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Running",
            "App minimized to system tray.",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )