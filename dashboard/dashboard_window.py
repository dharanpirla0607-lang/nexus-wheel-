"""
Main Settings Dashboard Window for Nexus Wheel.
Fluent sidebar navigation hosting all 11 configuration sections.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QFrame, QButtonGroup, QScrollArea
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal

from utils.icon_provider import IconProvider
from database.db import DatabaseManager
from dashboard.styles import get_dashboard_stylesheet

# Import pages
from dashboard.pages.page_general import GeneralPage
from dashboard.pages.page_wheel import WheelCustomizationPage
from dashboard.pages.page_shortcuts import ShortcutManagerPage
from dashboard.pages.page_controls import PlayerControlsPage
from dashboard.pages.page_transparency import TransparencyPage
from dashboard.pages.page_animations import AnimationsPage
from dashboard.pages.page_appearance import AppearancePage
from dashboard.pages.page_audio import AudioFeedbackPage
from dashboard.pages.page_startup import StartupBackgroundPage
from dashboard.pages.page_backup import BackupRestorePage
from dashboard.pages.page_about import AboutPage

class DashboardWindow(QMainWindow):
    test_wheel_requested = Signal()
    config_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NEXUS WHEEL – Command Dashboard")
        self.resize(1080, 720)
        self.setMinimumSize(940, 640)

        self._db = DatabaseManager()
        self._apply_theme_style()
        self._init_ui()

    def _apply_theme_style(self):
        accent_hex = self._db.get_setting("accent_color", "#00F0FF")
        self.setStyleSheet(get_dashboard_stylesheet(accent_hex))

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ------------------ SIDEBAR ------------------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        l_side = QVBoxLayout(sidebar)
        l_side.setContentsMargins(14, 18, 14, 18)
        l_side.setSpacing(6)

        # Logo & App Title
        brand_row = QHBoxLayout()
        logo_lbl = QLabel()
        accent = self._db.get_setting("accent_color", "#00F0FF")
        logo_lbl.setPixmap(IconProvider.get_pixmap("wheel", accent, 32))
        brand_row.addWidget(logo_lbl)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        title_lbl = QLabel("NEXUS WHEEL")
        title_lbl.setObjectName("sidebar_title")
        sub_lbl = QLabel("SYSTEM CONTROL")
        sub_lbl.setObjectName("sidebar_sub")
        brand_text.addWidget(title_lbl)
        brand_text.addWidget(sub_lbl)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()
        l_side.addLayout(brand_row)

        l_side.addSpacing(14)

        # Navigation Buttons
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_items = [
            ("General", "general", 0),
            ("Wheel Customization", "wheel", 1),
            ("Shortcut Manager", "shortcut", 2),
            ("Player Controls", "keyboard", 3),
            ("Transparency", "glass", 4),
            ("Animations", "anim", 5),
            ("Appearance", "star", 6),
            ("Audio Feedback", "audio", 7),
            ("Startup & Gaming", "game", 8),
            ("Backup & Restore", "backup", 9),
            ("About & Reference", "about", 10),
        ]

        self.nav_buttons = []
        for text, icon_name, idx in nav_items:
            btn = QPushButton(f"  {text}")
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.setIcon(IconProvider.get_icon(icon_name, "#00F0FF", 20))
            if idx == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda ch, i=idx: self.switch_page(i))
            self.nav_group.addButton(btn, idx)
            self.nav_buttons.append(btn)
            l_side.addWidget(btn)

        l_side.addStretch()

        # Quick Test Button in Sidebar footer
        btn_quick_test = QPushButton("⚡ Activate Wheel Now")
        btn_quick_test.setObjectName("primary_btn")
        btn_quick_test.clicked.connect(lambda: self.test_wheel_requested.emit())
        l_side.addWidget(btn_quick_test)

        main_layout.addWidget(sidebar)

        # ------------------ CONTENT AREA ------------------
        content_frame = QFrame()
        l_content = QVBoxLayout(content_frame)
        l_content.setContentsMargins(0, 0, 0, 0)
        l_content.setSpacing(0)

        # Stacked pages
        self.stack = QStackedWidget()

        # Instantiate pages
        self.p_general = GeneralPage()
        self.p_wheel = WheelCustomizationPage()
        self.p_shortcuts = ShortcutManagerPage()
        self.p_controls = PlayerControlsPage()
        self.p_transparency = TransparencyPage()
        self.p_animations = AnimationsPage()
        self.p_appearance = AppearancePage()
        self.p_audio = AudioFeedbackPage()
        self.p_startup = StartupBackgroundPage()
        self.p_backup = BackupRestorePage()
        self.p_about = AboutPage()

        # Hook signals
        self.p_general.settings_changed.connect(self._on_settings_updated)
        self.p_wheel.wheel_updated.connect(self._on_wheel_updated)
        self.p_shortcuts.shortcuts_updated.connect(self._on_shortcuts_updated)
        self.p_controls.controls_changed.connect(self._on_settings_updated)
        self.p_transparency.transparency_changed.connect(self._on_settings_updated)
        self.p_animations.animations_changed.connect(self._on_settings_updated)
        self.p_animations.test_animation_requested.connect(lambda: self.test_wheel_requested.emit())
        self.p_appearance.theme_changed.connect(self._on_theme_changed)
        self.p_audio.audio_changed.connect(self._on_settings_updated)
        self.p_startup.settings_changed.connect(self._on_settings_updated)
        self.p_backup.configuration_restored.connect(self._on_configuration_restored)

        pages = [
            self.p_general, self.p_wheel, self.p_shortcuts, self.p_controls,
            self.p_transparency, self.p_animations, self.p_appearance, self.p_audio,
            self.p_startup, self.p_backup, self.p_about
        ]

        for p in pages:
            # Wrap each page in smooth scroll area
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(p)
            self.stack.addWidget(scroll)

        l_content.addWidget(self.stack)
        main_layout.addWidget(content_frame, 1)

    def switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        if index < len(self.nav_buttons):
            self.nav_buttons[index].setChecked(True)

    def _on_theme_changed(self, accent_hex: str):
        self._apply_theme_style()
        self.config_changed.emit()

    def _on_settings_updated(self):
        self.config_changed.emit()

    def _on_wheel_updated(self):
        self.p_shortcuts._populate_wheels()
        self.p_shortcuts._populate_categories()
        self.p_shortcuts._refresh_shortcuts_table()
        self.config_changed.emit()

    def _on_shortcuts_updated(self):
        self.config_changed.emit()

    def _on_configuration_restored(self):
        self._apply_theme_style()
        self.p_wheel._populate_wheel_selector()
        self.p_wheel._load_current_wheel_values()
        self.p_shortcuts._populate_wheels()
        self.p_shortcuts._populate_categories()
        self.p_shortcuts._refresh_shortcuts_table()
        self.config_changed.emit()

    def closeEvent(self, event):
        """Minimize to system tray if setting enabled, otherwise exit."""
        if self._db.get_setting("minimize_to_tray", True):
            event.ignore()
            self.hide()
        else:
            event.accept()
