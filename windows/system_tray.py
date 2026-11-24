"""
Windows System Tray Controller for Nexus Wheel.
"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import QObject, Signal
from utils.icon_provider import IconProvider
from database.db import DatabaseManager

class SystemTrayManager(QObject):
    toggle_wheel_requested = Signal()
    open_dashboard_requested = Signal()
    exit_requested = Signal()
    wheel_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self.tray_icon = QSystemTrayIcon(parent)
        self._init_tray()

    def _init_tray(self):
        accent = self._db.get_setting("accent_color", "#00F0FF")
        icon = IconProvider.get_icon("wheel", accent, 32)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("NEXUS WHEEL – GTA V Control Center")

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background-color: #0E121A; color: #FFFFFF; border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 6px; padding: 4px; }
            QMenu::item { padding: 6px 20px; border-radius: 4px; }
            QMenu::item:selected { background-color: #00F0FF; color: #000000; font-weight: bold; }
        """)

        # Action: Activate Wheel
        act_toggle = QAction("⚡ Activate Wheel", menu)
        act_toggle.triggered.connect(lambda: self.toggle_wheel_requested.emit())
        menu.addAction(act_toggle)

        # Action: Open Dashboard
        act_dash = QAction("⚙️ Open Settings Dashboard", menu)
        act_dash.triggered.connect(lambda: self.open_dashboard_requested.emit())
        menu.addAction(act_dash)

        menu.addSeparator()

        # Submenu: Switch Wheel
        sub_wheels = menu.addMenu("Radial Wheels")
        wheels = self._db.get_wheels()
        for w in wheels:
            act_w = QAction(f"{w['name']} ({w['hotkey']})", sub_wheels)
            act_w.triggered.connect(lambda ch, wid=w["id"]: self.wheel_selected.emit(wid))
            sub_wheels.addAction(act_w)

        menu.addSeparator()

        # Action: Exit
        act_exit = QAction("Exit Nexus Wheel", menu)
        act_exit.triggered.connect(lambda: self.exit_requested.emit())
        menu.addAction(act_exit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def update_icon(self):
        accent = self._db.get_setting("accent_color", "#00F0FF")
        self.tray_icon.setIcon(IconProvider.get_icon("wheel", accent, 32))

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.open_dashboard_requested.emit()

    def show_message(self, title: str, message: str):
        if self._db.get_setting("show_notifications", True):
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 2500)
