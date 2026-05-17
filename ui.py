import os
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QButtonGroup, QFileDialog,
    QPlainTextEdit, QSystemTrayIcon, QMenu, QMessageBox, QStyle,
    QFrame, QComboBox, QLabel, QAbstractButton,
    QDialog, QListWidget, QListWidgetItem, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont, QShortcut, QKeySequence, QPainter, QColor, QPen

from backend import MonitorWorker, setup_logging
from translations import TRANSLATIONS, RTL_LANGUAGES, SCRIPT_FONTS


APP_VERSION = "1.0.0"
APP_NAME    = "VersionTrail"

# ── Config path (AppData) ──────────────────────────────────────────────────────
_APPDATA    = os.environ.get("APPDATA", os.path.expanduser("~"))
_CONFIG_DIR = os.path.join(_APPDATA, APP_NAME)
CONFIG_PATH = os.path.join(_CONFIG_DIR, "config.json")

SUPPORTED_LANGUAGES = list(TRANSLATIONS.keys())   # ["English", "Tamil", "Chinese", "Arabic"]


def load_language() -> str:
    """Read saved language from config.json; fall back to English."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        lang = data.get("language", "English")
        return lang if lang in TRANSLATIONS else "English"
    except Exception:
        return "English"


def save_language(language: str) -> None:
    """Persist language selection to config.json in AppData."""
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"language": language}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ── Palette ────────────────────────────────────────────────────────────────────
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


# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM MODE BUTTON  (card-style radio alternative)
# ──────────────────────────────────────────────────────────────────────────────
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


# ──────────────────────────────────────────────────────────────────────────────
# STATUS DOT
# ──────────────────────────────────────────────────────────────────────────────
class StatusDot(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self.set_color(C_DOT_IDLE)

    def set_color(self, color: str):
        self.setStyleSheet(f"border-radius: 5px; background: {color};")


# ──────────────────────────────────────────────────────────────────────────────
# LANGUAGE PICKER DIALOG
# ──────────────────────────────────────────────────────────────────────────────
class LanguageDialog(QDialog):
    """Small dialog with a search box + list for choosing a language."""

    def __init__(self, current_language: str, parent=None):
        super().__init__(parent)
        t = TRANSLATIONS.get(current_language, TRANSLATIONS["English"])

        self.setWindowTitle(t["dlg_language_title"])
        self.setFixedSize(320, 420)
        self.selected_language = current_language

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Search box
        self.search = QLineEdit()
        self.search.setPlaceholderText(t["dlg_language_search"])
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background: {C_BG_SECONDARY};
                border: 1px solid {C_BORDER_SOFT};
                border-radius: 6px;
                padding: 0 10px;
                min-height: 32px;
                font-size: 13px;
                color: {C_TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border: 1px solid {C_TEAL};
            }}
        """)
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)

        # Language list
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background: {C_BG_PRIMARY};
                border: 1px solid {C_BORDER_SOFT};
                border-radius: 8px;
                font-size: 13px;
                color: {C_TEXT_PRIMARY};
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background: {C_TEAL_BG};
                color: {C_TEAL_DARK};
            }}
            QListWidget::item:hover:!selected {{
                background: {C_BG_SECONDARY};
            }}
        """)
        self._populate(SUPPORTED_LANGUAGES, current_language)
        self.list_widget.itemDoubleClicked.connect(self._accept)
        layout.addWidget(self.list_widget)

        # OK / Cancel
        buttons = QDialogButtonBox()
        self.ok_btn     = buttons.addButton(t["dlg_ok"],     QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_btn = buttons.addButton(t["dlg_cancel"], QDialogButtonBox.ButtonRole.RejectRole)
        self.ok_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_TEAL};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 20px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{ background: {C_TEAL_DARK}; }}
        """)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_BG_PRIMARY};
                border: 1px solid {C_BORDER_MED};
                border-radius: 6px;
                padding: 6px 20px;
                font-size: 13px;
                color: {C_TEXT_PRIMARY};
            }}
            QPushButton:hover {{ background: {C_BG_SECONDARY}; }}
        """)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate(self, languages: list, current: str):
        self.list_widget.clear()
        for lang in languages:
            item = QListWidgetItem(lang)
            self.list_widget.addItem(item)
            if lang == current:
                self.list_widget.setCurrentItem(item)

    def _filter(self, text: str):
        query = text.strip().lower()
        filtered = [l for l in SUPPORTED_LANGUAGES if query in l.lower()]
        current = self.selected_language
        self._populate(filtered, current)

    def _accept(self):
        item = self.list_widget.currentItem()
        if item:
            self.selected_language = item.text()
        self.accept()


# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLESHEET
# ──────────────────────────────────────────────────────────────────────────────
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

/* ── Secondary action: Stop ── */
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


# ──────────────────────────────────────────────────────────────────────────────
# MAIN WINDOW
# ──────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(580, 560)
        self.setMinimumSize(520, 480)
        self.worker          = None
        self.all_logs        = []
        self.log_filter      = "All Events"
        self._backup_count   = 0
        self._src_touched    = False
        self._bak_touched    = False
        self.logger          = setup_logging()
        self.current_language = load_language()   # load BEFORE UI is built

        self.setStyleSheet(GLOBAL_QSS)
        self._apply_direction(self.current_language)   # set RTL/LTR before widgets render
        self.setup_ui()
        self.setup_menu()
        self.setup_tray()
        self.setup_shortcuts()
        self.update_status("Idle")
        self.apply_language(self.current_language)     # apply translated strings

    # ── Direction helper ───────────────────────────────────────────────────────
    def _apply_direction(self, language: str):
        """Set app-wide layout direction only. Font is handled per-widget in apply_language."""
        app = QApplication.instance()
        if language in RTL_LANGUAGES:
            app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    # ── Language application ───────────────────────────────────────────────────
    def apply_language(self, language: str):
        """Update every translatable string in the UI."""
        t   = TRANSLATIONS.get(language, TRANSLATIONS["English"])
        rtl = language in RTL_LANGUAGES
        align_flag = Qt.AlignmentFlag.AlignRight if rtl else Qt.AlignmentFlag.AlignLeft

        # Store FIRST so any method called below (e.g. update_status) can use self._t
        self._t = t

        # ── Script font: applied only to UI text widgets, NOT log pane ──
        # This avoids OpenType warnings from Consolas/Segoe UI being asked to render
        # non-Latin scripts. Log pane always keeps FONT_MONO.
        ui_font_name = SCRIPT_FONTS.get(language, FONT_UI)
        ui_font      = QFont(ui_font_name, 10)
        ui_font_sm   = QFont(ui_font_name, 9)
        ui_font_xs   = QFont(ui_font_name, 8)
        for widget in [
            self.mode_lbl, self.src_lbl, self.dst_lbl,
            self.src_edit, self.bak_edit,
            self.src_btn, self.bak_btn,
            self.start_btn, self.stop_btn,
            self.status_label, self.filter_label, self.filter_combo,
            self.src_error, self.bak_error,
        ]:
            widget.setFont(ui_font)
        for btn in [self.btn_file, self.btn_folder, self.btn_recursive]:
            btn.setFont(ui_font_sm)
        for pill_lbl in [
            self.stat_files._label,   self.stat_files._value_label,
            self.stat_folders._label, self.stat_folders._value_label,
            self.stat_backups._label, self.stat_backups._value_label,
        ]:
            pill_lbl.setFont(ui_font_xs)

        # ── Menu bar labels ──
        self.menu_file.setTitle(t["menu_file"])
        self.menu_language.setTitle(t["menu_language"])
        self.menu_help.setTitle(t["menu_help"])
        self.action_exit.setText(t["menu_exit"])
        self.action_choose_language.setText(t["menu_choose_language"])
        self.action_quick_start.setText(t["menu_quick_start"])
        self.action_about.setText(t["menu_about"])
        # Force menubar to repaint — PyQt6 doesn't always refresh on setTitle alone
        self.menuBar().update()

        # ── Mode buttons ──
        self.btn_file.setText(t["btn_single_file"])
        self.btn_folder.setText(t["btn_folder"])
        self.btn_recursive.setText(t["btn_folder_recursive"])
        # Force custom-painted buttons to redraw
        for btn in [self.btn_file, self.btn_folder, self.btn_recursive]:
            btn.update()

        # ── Section labels ──
        self.mode_lbl.setText(t["section_monitor"])
        self.src_lbl.setText(t["section_source"])
        self.dst_lbl.setText(t["section_destination"])

        # ── Path inputs & browse buttons ──
        self.src_edit.setPlaceholderText(t["placeholder_source"])
        self.src_edit.setAlignment(align_flag)
        self.bak_edit.setPlaceholderText(t["placeholder_destination"])
        self.bak_edit.setAlignment(align_flag)
        self.src_btn.setText(t["btn_browse"])
        self.bak_btn.setText(t["btn_browse"])

        # ── Action buttons ──
        self.start_btn.setText(t["btn_start"])
        self.stop_btn.setText(t["btn_stop"])

        # ── Filter combo ──
        self.filter_label.setText(t["filter_label"])
        self.filter_combo.blockSignals(True)
        self.filter_combo.clear()
        self.filter_combo.addItems([t["filter_all"], t["filter_changes"], t["filter_errors"]])
        self.filter_combo.blockSignals(False)

        # ── Stat pills ──
        self.stat_files._label.setText(t["stat_files"])
        self.stat_folders._label.setText(t["stat_folders"])
        self.stat_backups._label.setText(t["stat_backups"])

        # ── Log pane: direction only, font stays FONT_MONO ──
        log_dir = Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight
        self.log_text.setLayoutDirection(log_dir)
        self.log_text.setPlaceholderText(t["log_placeholder"])

        # ── Status bar ──
        self.update_status(self._current_status_state)

        # ── Tray menu ──
        self.tray_show_action.setText(t["tray_show"])
        self.tray_exit_action.setText(t["tray_exit"])

    # ── UI ─────────────────────────────────────────────────────────────────────
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 10, 14, 14)
        root.setSpacing(8)

        # ── Config card ──────────────────────────────────────────────────────
        config_card = QFrame()
        config_card.setObjectName("configCard")
        cc = QVBoxLayout(config_card)
        cc.setContentsMargins(14, 10, 14, 10)
        cc.setSpacing(4)

        # Mode selector
        self.mode_lbl = QLabel("MONITOR")
        self.mode_lbl.setObjectName("sectionLabel")
        cc.addWidget(self.mode_lbl)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(6)
        self.btn_file      = ModeButton("Single File")
        self.btn_folder    = ModeButton("Folder")
        self.btn_recursive = ModeButton("Folder + Sub Folder")

        self.scope_group = QButtonGroup(self)
        self.scope_group.setExclusive(True)
        for btn in [self.btn_file, self.btn_folder, self.btn_recursive]:
            self.scope_group.addButton(btn)
            mode_row.addWidget(btn)
            btn.clicked.connect(self._on_mode_selected)
        cc.addLayout(mode_row)

        # Source
        self.src_lbl = QLabel("SOURCE (File/Folder)")
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
        self.dst_lbl = QLabel("BACKUP DESTINATION FOLDER")
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

        # Action buttons
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

        # ── Status + stats bar ────────────────────────────────────────────────
        status_bar = QFrame()
        status_bar.setObjectName("statusBar")
        sb_layout = QVBoxLayout(status_bar)
        sb_layout.setContentsMargins(12, 8, 14, 8)
        sb_layout.setSpacing(6)

        # Row 1: dot + status text + filter
        sb_row = QHBoxLayout()
        sb_row.setSpacing(8)

        self.status_dot   = StatusDot()
        self.status_label = QLabel("Idle")
        self.status_label.setFont(QFont(FONT_UI, 9))
        self.status_label.setStyleSheet(f"color: {C_TEXT_MUTED}; background: transparent; border: none;")
        sb_row.addWidget(self.status_dot)
        sb_row.addWidget(self.status_label)
        sb_row.addStretch()

        self.filter_label = QLabel("Filter:")
        self.filter_label.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 12px; background: transparent; border: none;")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Events", "Changes Only", "Errors Only"])
        self.filter_combo.currentTextChanged.connect(self.apply_log_filter)
        sb_row.addWidget(self.filter_label)
        sb_row.addWidget(self.filter_combo)
        sb_layout.addLayout(sb_row)

        # Row 2: stats pills
        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)

        self.stat_files   = self._make_stat_pill("📄 Files monitored", "0")
        self.stat_folders = self._make_stat_pill("📁 Folders", "0")
        self.stat_backups = self._make_stat_pill("💾 Backups made", "0")

        for pill in [self.stat_files, self.stat_folders, self.stat_backups]:
            stats_row.addWidget(pill)
        stats_row.addStretch()
        sb_layout.addLayout(stats_row)

        root.addWidget(status_bar)

        # ── Log card ──────────────────────────────────────────────────────────
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

        # Track current status state for re-translation
        self._current_status_state = "Idle"

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
        row  = QHBoxLayout(pill)
        row.setContentsMargins(8, 3, 10, 3)
        row.setSpacing(6)
        lbl = QLabel(label)
        lbl.setObjectName("statPillLabel")
        val = QLabel(value)
        val.setObjectName("statPillValue")
        row.addWidget(lbl)
        row.addWidget(val)
        pill._label       = lbl    # exposed for apply_language
        pill._value_label = val
        return pill

    def _update_stats(self):
        """Recount monitored files/folders from the source path."""
        src   = self.src_edit.text().strip()
        scope = self._scope()
        files, folders, backups = 0, 0, self._backup_count

        if src and os.path.exists(src) and self.worker and self.worker.isRunning():
            if scope == "file":
                files   = 1
                folders = 0
            elif scope == "folder":
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
                        files   += len(fls)
                        folders += len(dirs)
                except Exception:
                    pass

        self.stat_files._value_label.setText(str(files))
        self.stat_folders._value_label.setText(str(folders))
        self.stat_backups._value_label.setText(str(backups))

    # ── Menu bar ───────────────────────────────────────────────────────────────
    def setup_menu(self):
        menubar = self.menuBar()

        # File
        self.menu_file    = menubar.addMenu("File")
        self.action_exit  = QAction("Exit Completely", self)
        self.action_exit.setShortcut("Ctrl+Q")
        self.action_exit.triggered.connect(self.force_exit)
        self.menu_file.addAction(self.action_exit)

        # Language  ← NEW: inserted between File and Help
        self.menu_language           = menubar.addMenu("Language")
        self.action_choose_language  = QAction("Choose Language…", self)
        self.action_choose_language.triggered.connect(self.show_language_dialog)
        self.menu_language.addAction(self.action_choose_language)

        # Help
        self.menu_help         = menubar.addMenu("Help")
        self.action_quick_start = QAction("Quick Start Guide", self)
        self.action_quick_start.triggered.connect(self.show_quick_start)
        self.menu_help.addAction(self.action_quick_start)
        self.action_about = QAction("About", self)
        self.action_about.triggered.connect(self.show_about)
        self.menu_help.addAction(self.action_about)

    # ── Language dialog ────────────────────────────────────────────────────────
    def show_language_dialog(self):
        dlg = LanguageDialog(self.current_language, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            chosen = dlg.selected_language
            if chosen and chosen != self.current_language:
                self.current_language = chosen
                save_language(chosen)
                self._apply_direction(chosen)
                self.apply_language(chosen)
                t = self._t
                QMessageBox.information(
                    self,
                    t["menu_language"],
                    t["msg_language_changed"].format(lang=chosen)
                )

    # ── System tray ────────────────────────────────────────────────────────────
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray_icon.setToolTip(f"{APP_NAME} - Idle")
        self.tray_icon.show()

        tray_menu = QMenu()
        self.tray_show_action = QAction("Show Window", self)
        self.tray_show_action.triggered.connect(self.show_normal)
        tray_menu.addAction(self.tray_show_action)
        tray_menu.addSeparator()
        self.tray_exit_action = QAction("Exit Completely", self)
        self.tray_exit_action.triggered.connect(self.force_exit)
        tray_menu.addAction(self.tray_exit_action)

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

    # ── Shortcuts ──────────────────────────────────────────────────────────────
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Alt+S"), self, self.start_monitor)
        QShortcut(QKeySequence("Alt+O"), self, self.stop_monitor)

    # ── Status ─────────────────────────────────────────────────────────────────
    def update_status(self, state: str):
        self._current_status_state = state
        t = getattr(self, "_t", TRANSLATIONS["English"])

        dot_colors = {"Idle": C_DOT_IDLE, "Running": C_DOT_RUN, "Error": C_DOT_ERR}
        self.status_dot.set_color(dot_colors.get(state, C_DOT_IDLE))

        text_map = {
            "Idle":    t["status_idle"],
            "Running": t["status_running"],
            "Stopped": t["status_stopped"],
        }
        self.status_label.setText(text_map.get(state, state))
        self.tray_icon.setToolTip(f"{APP_NAME} - {state}")

    # ── Validation ─────────────────────────────────────────────────────────────
    def _scope(self) -> str:
        if self.btn_file.isChecked():      return "file"
        if self.btn_recursive.isChecked(): return "recursive"
        if self.btn_folder.isChecked():    return "folder"
        return ""

    def validate_inputs(self):
        t     = getattr(self, "_t", TRANSLATIONS["English"])
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
                self.src_error.setText(t["error_select_source"])
            valid = False
        elif not os.path.exists(src):
            self.src_error.setText(t["error_source_not_exist"])
            valid = False
        elif scope not in ("file", "") and not os.path.isdir(src):
            self.src_error.setText(t["error_source_must_folder"])
            valid = False
        elif scope == "file" and not os.path.isfile(src):
            self.src_error.setText(t["error_source_must_file"])
            valid = False

        if not bak:
            if self._bak_touched:
                self.bak_error.setText(t["error_select_destination"])
            valid = False
        elif not os.path.isdir(bak):
            self.bak_error.setText(t["error_dest_not_folder"])
            valid = False
        elif src and os.path.abspath(src) == os.path.abspath(bak):
            self.bak_error.setText(t["error_same_path"])
            valid = False
        elif scope == "recursive" and src and os.path.abspath(bak).startswith(os.path.abspath(src) + os.sep):
            self.bak_error.setText(t["error_dest_inside_source"])
            valid = False

        self.start_btn.setEnabled(valid)

    # ── File dialogs ───────────────────────────────────────────────────────────
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

    # ── Monitor control ────────────────────────────────────────────────────────
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

    # ── Logging ────────────────────────────────────────────────────────────────
    def append_log(self, msg: str):
        self.all_logs.append(msg)
        if "[INFO] Backed up:" in msg:
            self._backup_count += 1
        self._update_stats()
        self.apply_log_filter()

    def apply_log_filter(self):
        t = getattr(self, "_t", TRANSLATIONS["English"])
        self.log_filter = self.filter_combo.currentText()
        self.log_text.clear()
        for log in self.all_logs:
            if self.log_filter == t["filter_all"]:
                self.log_text.appendPlainText(log)
            elif self.log_filter == t["filter_changes"] and "[INFO] Backed up:" in log:
                self.log_text.appendPlainText(log)
            elif self.log_filter == t["filter_errors"] and ("[WARN]" in log or "[ERROR]" in log):
                self.log_text.appendPlainText(log)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    # ── Dialogs ────────────────────────────────────────────────────────────────
    def show_quick_start(self):
        t = getattr(self, "_t", TRANSLATIONS["English"])
        QMessageBox.information(self, t["quick_start_title"], t["quick_start_text"])

    def show_about(self):
        t = getattr(self, "_t", TRANSLATIONS["English"])
        text = (
            f"<b>{APP_NAME}</b><br>"
            f"Version: {APP_VERSION}<br>"
            f"License: MIT License<br><br>"
            f"{t['about_description']}"
            f"<br><br>"
            f"-------------------------------------------<br>"
            f"Coder: ERAKKARTHIK<br>"
            f"-------------------------------------------<br>"
            f"Tester: ERAKKARTHIK, D11DMB"
        )
        QMessageBox.about(self, t["about_title"], text)

    # ── Window close → tray ────────────────────────────────────────────────────
    def closeEvent(self, event):
        t = getattr(self, "_t", TRANSLATIONS["English"])
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            t["tray_minimized_title"],
            t["tray_minimized_body"],
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )