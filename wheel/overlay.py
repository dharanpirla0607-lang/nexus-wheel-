"""
Full-Screen Transparent Overlay for Nexus Wheel.
Hosts the Radial Wheel with background dimming, multi-monitor support,
screen boundary clamping, and confirmation dialogs for destructive actions.
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import QWidget, QMessageBox, QApplication
from PySide6.QtGui import QPainter, QColor, QCursor, QKeyEvent, QGuiApplication
from PySide6.QtCore import Qt, QPoint, Signal, QRect
from wheel.radial_menu import RadialWheelWidget
from shortcuts.executor import ActionExecutor
from database.db import DatabaseManager
from windows.win32_integration import WindowsIntegration
import win32gui

class NexusOverlay(QWidget):
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self.previous_active_hwnd: Optional[int] = None
        self.is_open: bool = False
        self.last_screen_grab = None
        self.wheel_open_pos = QPoint()

        # Transparent, frameless, always-on-top tool window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Child radial wheel widget
        self.wheel_widget = RadialWheelWidget(self)
        self.wheel_widget.setFixedSize(640, 640)
        self.wheel_widget.action_triggered.connect(self._on_action_triggered)

    def show_wheel(self, wheel_id: Optional[str] = None):
        """Activates and displays the overlay."""
        # Capture current cursor position and pristine screen BEFORE displaying overlay
        self.wheel_open_pos = QCursor.pos()
        try:
            from utils.photo_downloader import PhotoDownloader
            self.last_screen_grab = PhotoDownloader.capture_full_screen()
        except Exception as e:
            print(f"[NexusOverlay] Screen capture error: {e}")
            self.last_screen_grab = None

        # Capture the window currently in focus before we steal focus
        self.previous_active_hwnd = WindowsIntegration.get_foreground_window()

        # Check gaming mode blacklist
        if self._db.get_setting("gaming_mode_enabled", True):
            if self._db.get_setting("disable_when_gaming", False):
                if WindowsIntegration.is_foreground_fullscreen():
                    print("Gaming mode: Wheel activation suppressed over fullscreen game.")
                    return

        # Load wheel configuration
        if not wheel_id:
            def_w = self._db.get_default_wheel()
            wheel_id = def_w["id"]
            
        self.wheel_widget.load_wheel(wheel_id)

        # Pass screen grab and cursor position into the wheel widget for
        # context-aware actions (e.g. quick download, AI features).
        self.wheel_widget._screen_img = self.last_screen_grab
        self.wheel_widget._cursor_pos = self.wheel_open_pos

        # Size and position overlay across current screen
        screen = QGuiApplication.screenAt(QCursor.pos())
        if not screen:
            screen = QGuiApplication.primaryScreen()
        screen_geo = screen.geometry()
        self.setGeometry(screen_geo)

        # Calculate wheel widget position
        pos_mode = self._db.get_setting("position_mode", "cursor")
        ww = self.wheel_widget.width()
        wh = self.wheel_widget.height()

        if pos_mode == "cursor":
            cursor_pos = QCursor.pos() - screen_geo.topLeft()
            target_x = cursor_pos.x() - ww // 2
            target_y = cursor_pos.y() - wh // 2
            # Clamp inside screen boundaries
            target_x = max(20, min(screen_geo.width() - ww - 20, target_x))
            target_y = max(20, min(screen_geo.height() - wh - 20, target_y))
        else: # Screen center
            target_x = (screen_geo.width() - ww) // 2
            target_y = (screen_geo.height() - wh) // 2

        self.wheel_widget.move(target_x, target_y)

        self.is_open = True
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()
        self.wheel_widget.setFocus()

        # Trigger opening animation
        preset = self._db.get_setting("animation_preset", "GTA V Classic")
        self.wheel_widget.start_open_animation(preset)

    def hide_wheel(self):
        """Closes the overlay with animation."""
        if not self.is_open:
            return
        self.is_open = False
        self.wheel_widget.start_close_animation(on_finish_callback=self._do_close)

    def _do_close(self):
        self.hide()
        self.closed.emit()
        # Restore focus to previous window if possible
        if self.previous_active_hwnd and win32gui.IsWindow(self.previous_active_hwnd):
            try:
                win32gui.SetForegroundWindow(self.previous_active_hwnd)
            except Exception:
                pass

    def _on_action_triggered(self, shortcut: Dict[str, Any]):
        # Check if destructive action requires confirmation
        if shortcut.get("is_destructive", 0):
            label = shortcut.get("label", "Action")
            reply = QMessageBox.question(
                self,
                "Confirm Destructive Action",
                f"Are you sure you want to execute:\n'{label}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Hide wheel and execute action
        self.hide_wheel()
        context = {
            "screen_img": self.last_screen_grab,
            "cursor_pos": self.wheel_open_pos
        }
        ActionExecutor.execute(shortcut, self.previous_active_hwnd, context=context)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        # Escape cancels
        if key == Qt.Key.Key_Escape:
            self.hide_wheel()
            event.accept()
            return

        # Enter confirms
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            if self._db.get_setting("confirm_with_enter", True):
                self.wheel_widget.execute_selection()
                event.accept()
                return

        # WASD & Arrow Key Navigation
        if self._db.get_setting("keyboard_navigation", True):
            if key in (Qt.Key.Key_Up, Qt.Key.Key_W):
                self.wheel_widget.select_direction("UP")
                event.accept()
                return
            elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
                self.wheel_widget.select_direction("DOWN")
                event.accept()
                return
            elif key in (Qt.Key.Key_Left, Qt.Key.Key_A):
                self.wheel_widget.select_direction("LEFT")
                event.accept()
                return
            elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
                self.wheel_widget.select_direction("RIGHT")
                event.accept()
                return
            elif key == Qt.Key.Key_Tab:
                # Tab cycles category
                self.wheel_widget.next_category()
                event.accept()
                return

        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        # Click outside the wheel widget closes the menu
        wheel_rect = self.wheel_widget.geometry()
        if not wheel_rect.contains(event.pos()):
            self.hide_wheel()
            event.accept()
        else:
            super().mousePressEvent(event)

    def paintEvent(self, event):
        """Draws transparent background or subtle dimming if enabled."""
        painter = QPainter(self)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.eraseRect(self.rect())

        dim_opacity = float(self._db.get_setting("dimming_opacity", 0.0))
        if dim_opacity > 0.01:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            alpha = int(dim_opacity * 255)
            painter.fillRect(self.rect(), QColor(0, 0, 0, alpha))
        painter.end()
