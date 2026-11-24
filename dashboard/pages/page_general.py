"""
General Settings Page for Nexus Wheel Dashboard.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QFrame, QComboBox, QMessageBox, QLineEdit, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from database.db import DatabaseManager
from windows.win32_integration import WindowsIntegration

class GeneralPage(QWidget):
    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("General Settings")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title)

        desc = QLabel("Configure core application behavior, startup preferences, and global shortcuts.")
        desc.setStyleSheet("color: #8B949E; margin-bottom: 8px;")
        layout.addWidget(desc)

        # 1. Startup & System Tray Card
        c1 = QFrame()
        c1.setObjectName("card")
        l1 = QVBoxLayout(c1)
        l1.setSpacing(12)

        h1 = QLabel("System Integration")
        h1.setObjectName("card_header")
        l1.addWidget(h1)

        self.cb_startup = QCheckBox("Start Nexus Wheel automatically with Windows")
        self.cb_startup.setChecked(WindowsIntegration.is_startup_enabled())
        self.cb_startup.toggled.connect(self._toggle_startup)
        l1.addWidget(self.cb_startup)

        self.cb_tray = QCheckBox("Minimize application to system tray on close")
        self.cb_tray.setChecked(self._db.get_setting("minimize_to_tray", True))
        self.cb_tray.toggled.connect(lambda v: self._save_setting("minimize_to_tray", v))
        l1.addWidget(self.cb_tray)

        self.cb_hotkeys = QCheckBox("Enable global activation hotkeys")
        self.cb_hotkeys.setChecked(self._db.get_setting("global_hotkeys_enabled", True))
        self.cb_hotkeys.toggled.connect(lambda v: self._save_setting("global_hotkeys_enabled", v))
        l1.addWidget(self.cb_hotkeys)

        self.cb_notif = QCheckBox("Show system notifications for actions and profile changes")
        self.cb_notif.setChecked(self._db.get_setting("show_notifications", True))
        self.cb_notif.toggled.connect(lambda v: self._save_setting("show_notifications", v))
        l1.addWidget(self.cb_notif)

        layout.addWidget(c1)

        # 2. Wheel Position & Default Card
        c2 = QFrame()
        c2.setObjectName("card")
        l2 = QVBoxLayout(c2)
        l2.setSpacing(12)

        h2 = QLabel("Default Radial Wheel & Behavior")
        h2.setObjectName("card_header")
        l2.addWidget(h2)

        row_def = QHBoxLayout()
        lbl_def = QLabel("Default Active Wheel:")
        lbl_def.setStyleSheet("color: #E6EDF3; font-weight: 600;")
        self.combo_default_wheel = QComboBox()
        self._populate_wheels()
        self.combo_default_wheel.currentIndexChanged.connect(self._on_default_wheel_changed)
        row_def.addWidget(lbl_def)
        row_def.addWidget(self.combo_default_wheel)
        row_def.addStretch()
        l2.addLayout(row_def)

        self.cb_remember_pos = QCheckBox("Remember last wheel position on screen")
        self.cb_remember_pos.setChecked(self._db.get_setting("remember_last_position", False))
        self.cb_remember_pos.toggled.connect(lambda v: self._save_setting("remember_last_position", v))
        l2.addWidget(self.cb_remember_pos)

        layout.addWidget(c2)

        # 3. Photo Downloader Preferences Card
        c_photo = QFrame()
        c_photo.setObjectName("card")
        l_photo = QVBoxLayout(c_photo)
        l_photo.setSpacing(12)

        h_photo = QLabel("Photo Downloader Preferences")
        h_photo.setObjectName("card_header")
        l_photo.addWidget(h_photo)

        desc_p = QLabel("Configure the default format and folder used when downloading photos by opening the wheel on them.")
        desc_p.setStyleSheet("color: #8B949E; font-size: 11px;")
        l_photo.addWidget(desc_p)

        row_p_fmt = QHBoxLayout()
        lbl_p_fmt = QLabel("Default Image Format:")
        lbl_p_fmt.setStyleSheet("color: #E6EDF3; font-weight: 600;")
        self.combo_photo_fmt = QComboBox()
        for f in ["PNG", "JPG", "WEBP", "BMP", "ICO", "TIFF", "GIF", "PDF"]:
            self.combo_photo_fmt.addItem(f, f)
        cur_p_fmt = self._db.get_setting("photo_download_format", "PNG")
        idx_pf = self.combo_photo_fmt.findData(cur_p_fmt)
        if idx_pf >= 0:
            self.combo_photo_fmt.setCurrentIndex(idx_pf)
        self.combo_photo_fmt.currentIndexChanged.connect(lambda: self._save_setting("photo_download_format", self.combo_photo_fmt.currentData()))
        row_p_fmt.addWidget(lbl_p_fmt)
        row_p_fmt.addWidget(self.combo_photo_fmt)
        row_p_fmt.addStretch()
        l_photo.addLayout(row_p_fmt)

        row_p_dir = QHBoxLayout()
        lbl_p_dir = QLabel("Default Save Folder:")
        lbl_p_dir.setStyleSheet("color: #E6EDF3; font-weight: 600;")
        from utils.photo_downloader import PhotoDownloader
        cur_p_dir = self._db.get_setting("photo_download_dir", "") or PhotoDownloader.get_default_download_dir()
        self.edit_photo_dir = QLineEdit(cur_p_dir)
        self.edit_photo_dir.textChanged.connect(lambda text: self._save_setting("photo_download_dir", text))
        btn_browse_p = QPushButton("Browse")
        btn_browse_p.setObjectName("secondary_btn")
        btn_browse_p.clicked.connect(self._browse_photo_folder)
        row_p_dir.addWidget(lbl_p_dir)
        row_p_dir.addWidget(self.edit_photo_dir, 1)
        row_p_dir.addWidget(btn_browse_p)
        l_photo.addLayout(row_p_dir)

        layout.addWidget(c_photo)

        # 4. Reset Defaults Card
        c3 = QFrame()
        c3.setObjectName("card")
        l3 = QVBoxLayout(c3)
        l3.setSpacing(12)

        h3 = QLabel("Factory Reset")
        h3.setObjectName("card_header")
        l3.addWidget(h3)

        desc3 = QLabel("Reset all Nexus Wheel preferences and keybindings to their original defaults.")
        desc3.setObjectName("card_desc")
        l3.addWidget(desc3)

        btn_reset = QPushButton("Restore Default Settings")
        btn_reset.setObjectName("danger_btn")
        btn_reset.setFixedWidth(200)
        btn_reset.clicked.connect(self._reset_defaults)
        l3.addWidget(btn_reset)

        layout.addWidget(c3)
        layout.addStretch()

    def _populate_wheels(self):
        self.combo_default_wheel.clear()
        wheels = self._db.get_wheels()
        for idx, w in enumerate(wheels):
            self.combo_default_wheel.addItem(w["name"], w["id"])
            if w.get("is_default", 0) == 1:
                self.combo_default_wheel.setCurrentIndex(idx)

    def _on_default_wheel_changed(self):
        wid = self.combo_default_wheel.currentData()
        if wid:
            wheels = self._db.get_wheels()
            for w in wheels:
                w["is_default"] = 1 if w["id"] == wid else 0
                self._db.save_wheel(w)
            self.settings_changed.emit()

    def _toggle_startup(self, enabled: bool):
        WindowsIntegration.set_startup(enabled, "NexusWheel")
        self._db.set_setting("start_with_windows", enabled)
        self.settings_changed.emit()

    def _save_setting(self, key: str, val):
        self._db.set_setting(key, val)
        self.settings_changed.emit()

    def _browse_photo_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder", self.edit_photo_dir.text())
        if folder:
            self.edit_photo_dir.setText(folder)
            self._save_setting("photo_download_dir", folder)

    def _reset_defaults(self):
        reply = QMessageBox.question(
            self,
            "Reset Defaults",
            "Are you sure you want to restore default settings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._db.reset_settings_to_default()
            self._init_ui()
            self.settings_changed.emit()
