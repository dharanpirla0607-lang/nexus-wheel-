"""
NEXUS WHEEL – GTA V Inspired Universal Control Wheel for Windows 11.
Main Application Entry Point.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QIcon

# Ensure local directories in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import DatabaseManager
from utils.sound_generator import generate_all_sounds
from utils.icon_provider import IconProvider
from wheel.overlay import NexusOverlay
from dashboard.dashboard_window import DashboardWindow
from windows.system_tray import SystemTrayManager
from controls.hotkey_listener import GlobalHotkeyManager

class NexusWheelApp:
    def __init__(self):
        # 1. Initialize persistent database and assets
        self.db = DatabaseManager()
        generate_all_sounds()

        # 2. Setup Windows Overlay
        self.overlay = NexusOverlay()

        # 3. Setup Settings Dashboard Window
        self.dashboard = DashboardWindow()

        # 4. Setup System Tray
        self.tray = SystemTrayManager()

        # 5. Setup Global Hotkey Manager
        self.hotkeys = GlobalHotkeyManager()

        # Connect inter-module signals
        self._connect_signals()

        # Start hotkey listener
        self.hotkeys.start()

    def _connect_signals(self):
        # Global Hotkeys -> Overlay
        self.hotkeys.wheel_toggle_requested.connect(self._on_hotkey_toggle)
        self.hotkeys.wheel_hold_start.connect(self._on_hotkey_hold_start)
        self.hotkeys.wheel_hold_end.connect(self._on_hotkey_hold_end)

        # Tray -> Actions
        self.tray.open_dashboard_requested.connect(self._show_dashboard)
        self.tray.toggle_wheel_requested.connect(lambda: self.overlay.show_wheel())
        self.tray.wheel_selected.connect(lambda wid: self.overlay.show_wheel(wid))
        self.tray.exit_requested.connect(self.exit_app)

        # Dashboard -> Actions
        self.dashboard.test_wheel_requested.connect(lambda: self.overlay.show_wheel())
        self.dashboard.config_changed.connect(self._on_config_changed)

    def _on_hotkey_toggle(self, wheel_id: str):
        if self.overlay.is_open:
            self.overlay.hide_wheel()
        else:
            self.overlay.show_wheel(wheel_id)

    def _on_hotkey_hold_start(self, wheel_id: str):
        if not self.overlay.is_open:
            self.overlay.show_wheel(wheel_id)

    def _on_hotkey_hold_end(self):
        if self.overlay.is_open:
            # Releasing key triggers the currently hovered selection and closes wheel (GTA V style)
            self.overlay.wheel_widget.execute_selection()
            self.overlay.hide_wheel()

    def _on_config_changed(self):
        self.hotkeys.reload_hotkeys()
        self.tray.update_icon()

    def _show_dashboard(self):
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()

    def run(self, start_minimized: bool = False):
        if not start_minimized and not self.db.get_setting("start_with_windows", False):
            self._show_dashboard()
        else:
            self.tray.show_message("Nexus Wheel Active", "Press Alt+X to open the radial wheel.")

    def exit_app(self):
        self.hotkeys.stop()
        if self.overlay.is_open:
            self.overlay.close()
        self.dashboard.close()
        QApplication.quit()

def main():
    # Enable High DPI & Per-Monitor DPI awareness
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    accent = "#00F0FF"
    app.setWindowIcon(IconProvider.get_icon("wheel", accent, 64))

    start_minimized = "--minimized" in sys.argv

    nexus_app = NexusWheelApp()
    nexus_app.run(start_minimized)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
