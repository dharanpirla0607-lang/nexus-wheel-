"""
Startup, System Tray, and Gaming Mode Page for Nexus Wheel Dashboard.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QFrame, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from database.db import DatabaseManager
from windows.win32_integration import WindowsIntegration

class StartupBackgroundPage(QWidget):
    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Startup & Gaming Mode")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title)

        desc = QLabel("Configure Windows autorun, system tray persistence, and fullscreen game detection.")
        desc.setStyleSheet("color: #8B949E; margin-bottom: 4px;")
        layout.addWidget(desc)

        # 1. Startup & Tray Card
        c1 = QFrame()
        c1.setObjectName("card")
        l1 = QVBoxLayout(c1)
        l1.setSpacing(12)

        h1 = QLabel("Background Execution & Startup")
        h1.setObjectName("card_header")
        l1.addWidget(h1)

        self.cb_startup = QCheckBox("Launch on Windows startup (Run in background silently)")
        self.cb_startup.setChecked(WindowsIntegration.is_startup_enabled())
        self.cb_startup.toggled.connect(self._toggle_startup)
        l1.addWidget(self.cb_startup)

        self.cb_tray = QCheckBox("Keep Nexus Wheel running in system tray when dashboard is closed")
        self.cb_tray.setChecked(self._db.get_setting("minimize_to_tray", True))
        self.cb_tray.toggled.connect(lambda v: self._save("minimize_to_tray", v))
        l1.addWidget(self.cb_tray)

        layout.addWidget(c1)

        # 2. Gaming Mode Card
        c2 = QFrame()
        c2.setObjectName("card")
        l2 = QVBoxLayout(c2)
        l2.setSpacing(12)

        h2 = QLabel("Gaming Mode & Anti-Interference")
        h2.setObjectName("card_header")
        l2.addWidget(h2)

        desc_gm = QLabel("Automatically detects fullscreen games and prevents accidental desktop shortcut execution.")
        desc_gm.setObjectName("card_desc")
        l2.addWidget(desc_gm)

        self.cb_gm_enabled = QCheckBox("Enable Gaming Mode")
        self.cb_gm_enabled.setChecked(self._db.get_setting("gaming_mode_enabled", True))
        self.cb_gm_enabled.toggled.connect(lambda v: self._save("gaming_mode_enabled", v))
        l2.addWidget(self.cb_gm_enabled)

        self.cb_disable_gaming = QCheckBox("Disable wheel completely when a recognized game is running")
        self.cb_disable_gaming.setChecked(self._db.get_setting("disable_when_gaming", False))
        self.cb_disable_gaming.toggled.connect(lambda v: self._save("disable_when_gaming", v))
        l2.addWidget(self.cb_disable_gaming)

        self.cb_allow_fs = QCheckBox("Allow wheel overlay over fullscreen games (Exclusive overlay mode)")
        self.cb_allow_fs.setChecked(self._db.get_setting("allow_over_fullscreen", True))
        self.cb_allow_fs.toggled.connect(lambda v: self._save("allow_over_fullscreen", v))
        l2.addWidget(self.cb_allow_fs)

        # Games Table
        h_table = QLabel("Recognized Games & Profiles:")
        h_table.setStyleSheet("font-weight: 600; color: #FFFFFF; margin-top: 6px;")
        l2.addWidget(h_table)

        self.table_games = QTableWidget()
        self.table_games.setColumnCount(3)
        self.table_games.setHorizontalHeaderLabels(["Game / Application", "Process (.EXE)", "Suppressed"])
        self.table_games.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_games.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_games.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_games.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_games.setFixedHeight(160)
        l2.addWidget(self.table_games)

        # Add Game Row
        row_add = QHBoxLayout()
        self.edit_proc = QLineEdit()
        self.edit_proc.setPlaceholderText("Process (e.g. game.exe)")
        self.edit_disp = QLineEdit()
        self.edit_disp.setPlaceholderText("Game Display Name")

        btn_add_game = QPushButton("+ Add Game")
        btn_add_game.setObjectName("primary_btn")
        btn_add_game.clicked.connect(self._add_game)

        btn_del_game = QPushButton("Remove")
        btn_del_game.setObjectName("danger_btn")
        btn_del_game.clicked.connect(self._delete_game)

        row_add.addWidget(self.edit_proc, 1)
        row_add.addWidget(self.edit_disp, 1)
        row_add.addWidget(btn_add_game)
        row_add.addWidget(btn_del_game)
        l2.addLayout(row_add)

        layout.addWidget(c2)
        layout.addStretch()

        self._refresh_games_table()

    def _toggle_startup(self, enabled: bool):
        WindowsIntegration.set_startup(enabled, "NexusWheel")
        self._save("start_with_windows", enabled)

    def _refresh_games_table(self):
        games = self._db.get_games()
        self.table_games.setRowCount(len(games))
        for i, g in enumerate(games):
            item_name = QTableWidgetItem(g["display_name"])
            item_proc = QTableWidgetItem(g["process_name"])
            
            cb_block = QCheckBox()
            cb_block.setChecked(bool(g["blocked"]))
            cb_block.toggled.connect(lambda v, gid=g["id"]: self._db.toggle_game_blocked(gid, v))
            
            self.table_games.setItem(i, 0, item_name)
            self.table_games.setItem(i, 1, item_proc)
            self.table_games.setCellWidget(i, 2, cb_block)

    def _add_game(self):
        proc = self.edit_proc.text().strip().lower()
        disp = self.edit_disp.text().strip()
        if not proc or not disp:
            QMessageBox.warning(self, "Invalid Input", "Please enter both process name and game name.")
            return
        if not proc.endswith(".exe"):
            proc += ".exe"
        self._db.add_game(proc, disp, True)
        self.edit_proc.clear()
        self.edit_disp.clear()
        self._refresh_games_table()

    def _delete_game(self):
        row = self.table_games.currentRow()
        if row < 0:
            return
        games = self._db.get_games()
        if row < len(games):
            self._db.delete_game(games[row]["id"])
            self._refresh_games_table()

    def _save(self, key, val):
        self._db.set_setting(key, val)
        self.settings_changed.emit()
