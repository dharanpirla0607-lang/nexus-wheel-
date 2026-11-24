"""
GTA V Inspired Radial Wheel Menu Widget for Nexus Wheel.
High performance, 60 FPS custom QPainter widget with glassmorphism,
monochrome black & white aesthetics, smooth segment transitions,
center HUD display, and seamlessly integrated outer sub-options.
"""

import math
import os
from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPainterPath,
    QRadialGradient, QLinearGradient, QPixmap, QCursor
)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QTimer, QPropertyAnimation, QEasingCurve, Property
from utils.icon_provider import IconProvider
from windows.audio_controller import AudioController
from database.db import DatabaseManager


# Sub-options dictionary for actions so each option expands into related sub-actions when hovered
SUB_OPTIONS_MAP: Dict[str, List[Dict[str, Any]]] = {
    "volume_up": [
        {"label": "+20%", "action_type": "custom_hotkey", "target": "volume_up", "icon": "vol_up", "hotkey_hint": "Boost"},
        {"label": "Max Vol", "action_type": "custom_hotkey", "target": "volume_up", "icon": "vol_up", "hotkey_hint": "100%"},
        {"label": "Sound Settings", "action_type": "app", "target": "ms-settings:sound", "icon": "settings", "hotkey_hint": "Settings"}
    ],
    "volume_down": [
        {"label": "-20%", "action_type": "custom_hotkey", "target": "volume_down", "icon": "vol_down", "hotkey_hint": "Lower"},
        {"label": "Quiet 10%", "action_type": "custom_hotkey", "target": "volume_down", "icon": "vol_down", "hotkey_hint": "Low"},
        {"label": "Sound Settings", "action_type": "app", "target": "ms-settings:sound", "icon": "settings", "hotkey_hint": "Settings"}
    ],
    "mute_toggle": [
        {"label": "Mute All", "action_type": "system", "target": "mute_toggle", "icon": "mute", "hotkey_hint": "Mute"},
        {"label": "Vol 50%", "action_type": "system", "target": "volume_up", "icon": "vol_up", "hotkey_hint": "Mid"},
        {"label": "Sound Mixer", "action_type": "app", "target": "ms-settings:sound", "icon": "audio", "hotkey_hint": "Mixer"}
    ],
    "play_pause": [
        {"label": "Play/Pause", "action_type": "media", "target": "play_pause", "icon": "play", "hotkey_hint": "Space"},
        {"label": "Next Track", "action_type": "media", "target": "next_track", "icon": "next", "hotkey_hint": "Next"},
        {"label": "Prev Track", "action_type": "media", "target": "prev_track", "icon": "prev", "hotkey_hint": "Prev"}
    ],
    "next_track": [
        {"label": "Fast Fwd", "action_type": "media", "target": "next_track", "icon": "next", "hotkey_hint": "+10s"},
        {"label": "Next Track", "action_type": "media", "target": "next_track", "icon": "next", "hotkey_hint": "Next"},
        {"label": "Stop", "action_type": "media", "target": "stop", "icon": "close", "hotkey_hint": "Stop"}
    ],
    "prev_track": [
        {"label": "Rewind", "action_type": "media", "target": "prev_track", "icon": "prev", "hotkey_hint": "-10s"},
        {"label": "Prev Track", "action_type": "media", "target": "prev_track", "icon": "prev", "hotkey_hint": "Prev"},
        {"label": "Replay", "action_type": "media", "target": "prev_track", "icon": "repeat", "hotkey_hint": "Replay"}
    ],
    "screenshot": [
        {"label": "Full Screen", "action_type": "productivity", "target": "screenshot", "icon": "screenshot", "hotkey_hint": "Full"},
        {"label": "Snipping Tool", "action_type": "app", "target": "snippingtool.exe", "icon": "snip", "hotkey_hint": "Snip"},
        {"label": "Clipboard Grab", "action_type": "productivity", "target": "clipboard_history", "icon": "clipboard", "hotkey_hint": "Win+V"}
    ],
    "download_photo": [
        {"label": "Save PNG", "action_type": "productivity", "target": "download_photo_png", "icon": "photo", "hotkey_hint": "Lossless"},
        {"label": "Save JPG", "action_type": "productivity", "target": "download_photo_jpg", "icon": "photo", "hotkey_hint": "Photo"},
        {"label": "Save WEBP", "action_type": "productivity", "target": "download_photo_webp", "icon": "photo", "hotkey_hint": "WebP"},
        {"label": "All Formats...", "action_type": "productivity", "target": "download_photo", "icon": "download", "hotkey_hint": "Custom"}
    ],
    "copy": [
        {"label": "Copy", "action_type": "productivity", "target": "copy", "icon": "copy", "hotkey_hint": "Ctrl+C"},
        {"label": "Cut", "action_type": "productivity", "target": "cut", "icon": "snip", "hotkey_hint": "Ctrl+X"},
        {"label": "Clipboard History", "action_type": "productivity", "target": "clipboard_history", "icon": "clipboard", "hotkey_hint": "Win+V"}
    ],
    "paste": [
        {"label": "Paste", "action_type": "productivity", "target": "paste", "icon": "paste", "hotkey_hint": "Ctrl+V"},
        {"label": "Undo", "action_type": "productivity", "target": "undo", "icon": "undo", "hotkey_hint": "Ctrl+Z"},
        {"label": "Redo", "action_type": "productivity", "target": "redo", "icon": "redo", "hotkey_hint": "Ctrl+Y"}
    ],
    "lock_pc": [
        {"label": "Lock PC", "action_type": "system", "target": "lock_pc", "icon": "lock", "hotkey_hint": "Win+L"},
        {"label": "Sleep", "action_type": "system", "target": "sleep_pc", "icon": "sleep", "hotkey_hint": "Sleep", "is_destructive": 1},
        {"label": "Sign Out", "action_type": "system", "target": "lock_pc", "icon": "user", "hotkey_hint": "Logout"}
    ],
    "shutdown_pc": [
        {"label": "Shutdown", "action_type": "system", "target": "shutdown_pc", "icon": "shutdown", "hotkey_hint": "Off", "is_destructive": 1},
        {"label": "Restart", "action_type": "system", "target": "restart_pc", "icon": "restart", "hotkey_hint": "Reboot", "is_destructive": 1},
        {"label": "Sleep", "action_type": "system", "target": "sleep_pc", "icon": "sleep", "hotkey_hint": "Sleep", "is_destructive": 1}
    ],
    "restart_pc": [
        {"label": "Restart", "action_type": "system", "target": "restart_pc", "icon": "restart", "hotkey_hint": "Reboot", "is_destructive": 1},
        {"label": "Shutdown", "action_type": "system", "target": "shutdown_pc", "icon": "shutdown", "hotkey_hint": "Off", "is_destructive": 1},
        {"label": "Lock PC", "action_type": "system", "target": "lock_pc", "icon": "lock", "hotkey_hint": "Lock"}
    ],
    "minimize": [
        {"label": "Minimize", "action_type": "window", "target": "minimize", "icon": "minimize", "hotkey_hint": "Min"},
        {"label": "Show Desktop", "action_type": "window", "target": "desktop", "icon": "desktop", "hotkey_hint": "Win+D"},
        {"label": "Snap Left", "action_type": "window", "target": "snap_left", "icon": "snap_left", "hotkey_hint": "Win+←"}
    ],
    "maximize": [
        {"label": "Maximize", "action_type": "window", "target": "maximize", "icon": "maximize", "hotkey_hint": "Max"},
        {"label": "Always on Top", "action_type": "window", "target": "toggle_top", "icon": "pin", "hotkey_hint": "Pin"},
        {"label": "Snap Right", "action_type": "window", "target": "snap_right", "icon": "snap_right", "hotkey_hint": "Win+→"}
    ],
    "close": [
        {"label": "Close Window", "action_type": "window", "target": "close", "icon": "close", "hotkey_hint": "Alt+F4", "is_destructive": 1},
        {"label": "Minimize", "action_type": "window", "target": "minimize", "icon": "minimize", "hotkey_hint": "Min"},
        {"label": "Task Manager", "action_type": "app", "target": "taskmgr.exe", "icon": "task", "hotkey_hint": "TaskMgr"}
    ],
    "chrome.exe": [
        {"label": "Open Chrome", "action_type": "app", "target": "chrome.exe", "icon": "chrome", "hotkey_hint": "Browser"},
        {"label": "New Tab", "action_type": "custom_hotkey", "target": "ctrl+t", "icon": "chrome", "hotkey_hint": "Ctrl+T"},
        {"label": "Incognito", "action_type": "app", "target": "chrome.exe", "arguments": "--incognito", "icon": "chrome", "hotkey_hint": "Private"}
    ],
    "explorer.exe": [
        {"label": "Explorer", "action_type": "app", "target": "explorer.exe", "icon": "explorer", "hotkey_hint": "Win+E"},
        {"label": "Downloads", "action_type": "custom_folder", "target": os.path.expanduser("~/Downloads"), "icon": "download", "hotkey_hint": "Folder"},
        {"label": "Pictures", "action_type": "custom_folder", "target": os.path.expanduser("~/Pictures"), "icon": "photo", "hotkey_hint": "Folder"}
    ],
    "wt.exe": [
        {"label": "Terminal", "action_type": "app", "target": "wt.exe", "icon": "terminal", "hotkey_hint": "Open"},
        {"label": "PowerShell", "action_type": "custom_cmd", "target": "powershell.exe", "icon": "terminal", "hotkey_hint": "PS"},
        {"label": "Command Prompt", "action_type": "custom_cmd", "target": "cmd.exe", "icon": "terminal", "hotkey_hint": "CMD"}
    ],
    "taskmgr.exe": [
        {"label": "Task Manager", "action_type": "app", "target": "taskmgr.exe", "icon": "task", "hotkey_hint": "Open"},
        {"label": "Resource Monitor", "action_type": "custom_cmd", "target": "resmon.exe", "icon": "task", "hotkey_hint": "ResMon"},
        {"label": "Device Manager", "action_type": "custom_cmd", "target": "devmgmt.msc", "icon": "settings", "hotkey_hint": "DevMgmt"}
    ],
    "code": [
        {"label": "VS Code", "action_type": "app", "target": "code", "icon": "code", "hotkey_hint": "Code"},
        {"label": "Open Folder", "action_type": "app", "target": "code", "arguments": ".", "icon": "folder", "hotkey_hint": "Workspace"},
        {"label": "Terminal", "action_type": "app", "target": "wt.exe", "icon": "terminal", "hotkey_hint": "WT"}
    ]
}


class RadialWheelWidget(QWidget):
    action_triggered = Signal(dict)
    selection_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._db = DatabaseManager()
        self._audio = AudioController()

        # Wheel data
        self.wheel_data: Dict[str, Any] = {}
        self.categories: List[Dict[str, Any]] = []
        self.active_category_index: int = 0
        self.shortcuts: List[Dict[str, Any]] = []

        # Segment counts: 4, 6, 8, 10, 12
        self.segments_count: int = 8
        self.selected_index: int = -1
        self.last_hovered_index: int = -1

        # Geometry & Dynamic Sizing — compact & neat
        self.base_wheel_radius: float = 185.0
        self.base_inner_radius: float = 80.0
        self.base_center_radius: float = 68.0
        self.base_deadzone_radius: float = 30.0
        self.base_sub_outer_radius: float = 245.0
        self.base_widget_size: int = 540

        self.scale_factor: float = 1.0
        self.wheel_radius: float = 185.0
        self.inner_radius: float = 80.0
        self.center_radius: float = 68.0
        self.deadzone_radius: float = 30.0
        self.sub_outer_radius: float = 245.0

        # Sub-options state
        self.hovered_sub_index: int = -1
        self._sub_weights: List[float] = [0.0] * 16

        # Animation states (for 60 FPS interpolation)
        self._anim_progress: float = 1.0
        self._scale_val: float = 1.0
        self._rot_val: float = 0.0
        self._pulse_val: float = 0.0

        # Segment hover interpolation (0.0 to 1.0 per segment)
        self._hover_weights: List[float] = [0.0] * 16

        # Quick download / screenshot context — set by overlay before showing
        self._screen_img = None
        self._cursor_pos = None

        # Cached wallpaper pixmap to avoid reloading every frame
        self._wallpaper_pixmap: Optional[QPixmap] = None
        self._wallpaper_path: str = ""

        # Timer for smooth 60 FPS glow & hover animations
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(16)  # ~60 FPS
        self._anim_timer.timeout.connect(self._on_animation_step)

        # Pulse direction for center ring breathing
        self._pulse_direction = 1

    # ------------------------------------------------------------------ #
    # Qt Properties for QPropertyAnimation
    # ------------------------------------------------------------------ #
    def get_anim_progress(self) -> float:
        return self._anim_progress

    def set_anim_progress(self, val: float):
        self._anim_progress = val
        self.update()

    anim_progress = Property(float, get_anim_progress, set_anim_progress)

    # ------------------------------------------------------------------ #
    # Scale / Size
    # ------------------------------------------------------------------ #
    def apply_scale(self, scale: float):
        """Applies dynamic scale to make the radial wheel smaller or larger."""
        scale = max(0.45, min(1.35, scale))
        self.scale_factor = scale
        self.wheel_radius = self.base_wheel_radius * scale
        self.inner_radius = self.base_inner_radius * scale
        self.center_radius = self.base_center_radius * scale
        self.sub_outer_radius = self.base_sub_outer_radius * scale
        dz = float(self._db.get_setting("deadzone_radius", 30))
        self.deadzone_radius = dz * scale
        w_size = int(self.base_widget_size * scale)
        self.setFixedSize(w_size, w_size)
        self.update()

    # ------------------------------------------------------------------ #
    # Load / Category management
    # ------------------------------------------------------------------ #
    def load_wheel(self, wheel_id: str):
        """Loads a wheel by ID and populates its active category shortcuts."""
        current_scale = float(self._db.get_setting("wheel_scale", 1.0))
        self.apply_scale(current_scale)

        w = self._db.get_wheel(wheel_id)
        if not w:
            w = self._db.get_default_wheel()
        self.wheel_data = w
        self.segments_count = int(w.get("segments_count", 8))
        self.categories = self._db.get_categories(w["id"])
        self.active_category_index = 0
        self.selected_index = -1
        self.last_hovered_index = -1
        self.hovered_sub_index = -1
        self._hover_weights = [0.0] * self.segments_count
        self._sub_weights = [0.0] * 8
        self._load_current_category_shortcuts()
        self.update()

    def _load_current_category_shortcuts(self):
        if not self.categories:
            self.shortcuts = []
            return
        cat_id = self.categories[self.active_category_index]["id"]
        raw_sc = self._db.get_shortcuts(self.wheel_data["id"], cat_id)

        sc_map = {s["segment_index"]: s for s in raw_sc}
        self.shortcuts = []
        for i in range(self.segments_count):
            if i in sc_map:
                self.shortcuts.append(sc_map[i])
            else:
                self.shortcuts.append({
                    "id": f"empty_{i}",
                    "wheel_id": self.wheel_data.get("id", "wheel_main"),
                    "category_id": cat_id,
                    "segment_index": i,
                    "label": f"Slot {i+1}",
                    "action_type": "none",
                    "target": "",
                    "arguments": "",
                    "icon": "empty",
                    "hotkey_hint": "",
                    "is_destructive": 0
                })

    def next_category(self):
        if len(self.categories) > 1:
            self.active_category_index = (self.active_category_index + 1) % len(self.categories)
            self._load_current_category_shortcuts()
            self._audio.play_select()
            self.hovered_sub_index = -1
            self.update()

    def prev_category(self):
        if len(self.categories) > 1:
            self.active_category_index = (self.active_category_index - 1) % len(self.categories)
            self._load_current_category_shortcuts()
            self._audio.play_select()
            self.hovered_sub_index = -1
            self.update()

    # ------------------------------------------------------------------ #
    # Sub-options resolver
    # ------------------------------------------------------------------ #
    def get_sub_options(self, segment_index: int) -> List[Dict[str, Any]]:
        """Returns related sub-actions for the given segment index."""
        if segment_index < 0 or segment_index >= len(self.shortcuts):
            return []
        sc = self.shortcuts[segment_index]
        target = sc.get("target", "").lower().strip()
        label = sc.get("label", "").lower().strip()
        act_type = sc.get("action_type", "")

        # 1. Exact match in sub-options map
        if target in SUB_OPTIONS_MAP:
            return SUB_OPTIONS_MAP[target]

        # 2. Key phrase matching
        for key, opts in SUB_OPTIONS_MAP.items():
            if key in target or key in label:
                return opts

        # 3. Dynamic generic fallback based on action_type
        if act_type == "app":
            return [
                {"label": f"Launch", "action_type": "app", "target": sc.get("target", ""), "icon": sc.get("icon", "app"), "hotkey_hint": "Open"},
                {"label": "Run as Admin", "action_type": "custom_cmd", "target": f'powershell Start-Process "{sc.get("target", "")}" -Verb runAs', "icon": "shield", "hotkey_hint": "Admin"},
                {"label": "Open Location", "action_type": "custom_cmd", "target": f'explorer /select,"{sc.get("target", "")}"', "icon": "folder", "hotkey_hint": "Dir"}
            ]
        elif act_type == "productivity":
            return [
                {"label": sc.get("label", "Execute"), "action_type": act_type, "target": sc.get("target", ""), "icon": sc.get("icon", "star"), "hotkey_hint": "Run"},
                {"label": "Clipboard History", "action_type": "productivity", "target": "clipboard_history", "icon": "clipboard", "hotkey_hint": "Win+V"},
                {"label": "Quick Snip", "action_type": "productivity", "target": "screenshot", "icon": "snip", "hotkey_hint": "Snip"}
            ]
        elif act_type == "window":
            return [
                {"label": sc.get("label", "Window"), "action_type": act_type, "target": sc.get("target", ""), "icon": sc.get("icon", "switch"), "hotkey_hint": "Run"},
                {"label": "Always on Top", "action_type": "window", "target": "toggle_top", "icon": "pin", "hotkey_hint": "Pin"},
                {"label": "Show Desktop", "action_type": "window", "target": "desktop", "icon": "desktop", "hotkey_hint": "Win+D"}
            ]
        elif act_type == "system":
            return [
                {"label": sc.get("label", "System"), "action_type": act_type, "target": sc.get("target", ""), "icon": sc.get("icon", "settings"), "hotkey_hint": "Run"},
                {"label": "Settings", "action_type": "app", "target": "ms-settings:", "icon": "settings", "hotkey_hint": "Win+I"},
                {"label": "Lock PC", "action_type": "system", "target": "lock_pc", "icon": "lock", "hotkey_hint": "Win+L"}
            ]
        return []

    # ------------------------------------------------------------------ #
    # Animations
    # ------------------------------------------------------------------ #
    def start_open_animation(self, preset_name: str = "GTA V Classic"):
        settings = self._db.get_all_settings()
        if not settings.get("animations_enabled", True):
            self._anim_progress = 1.0
            self._scale_val = 1.0
            self._rot_val = 0.0
            self._anim_timer.start()
            self.update()
            return

        from animations.presets import ANIMATION_PRESETS
        preset = ANIMATION_PRESETS.get(preset_name, ANIMATION_PRESETS.get("GTA V Classic", {}))
        dur = preset.get("open_duration", 220)
        self.start_scale = preset.get("start_scale", 0.82) if preset.get("scale_animation", True) else 1.0
        self.start_rot = preset.get("start_rotation", -15.0) if preset.get("rotation_animation", True) else 0.0

        self._anim = QPropertyAnimation(self, b"anim_progress")
        self._anim.setDuration(dur)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)

        easing = preset.get("easing_type", "OutCubic")
        if easing == "OutBack":
            self._anim.setEasingCurve(QEasingCurve.Type.OutBack)
        elif easing == "OutQuad":
            self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        elif easing == "OutElastic":
            self._anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        else:
            self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim.start()
        self._anim_timer.start()
        self._audio.play_open()

    def start_close_animation(self, on_finish_callback=None):
        settings = self._db.get_all_settings()
        self._audio.play_close()

        if not settings.get("animations_enabled", True):
            if on_finish_callback:
                on_finish_callback()
            return

        preset_name = settings.get("animation_preset", "GTA V Classic")
        from animations.presets import ANIMATION_PRESETS
        preset = ANIMATION_PRESETS.get(preset_name, ANIMATION_PRESETS.get("GTA V Classic", {}))
        dur = preset.get("close_duration", 160)

        self._close_anim = QPropertyAnimation(self, b"anim_progress")
        self._close_anim.setDuration(dur)
        self._close_anim.setStartValue(self._anim_progress)
        self._close_anim.setEndValue(0.0)
        self._close_anim.setEasingCurve(QEasingCurve.Type.InQuad)

        if on_finish_callback:
            self._close_anim.finished.connect(on_finish_callback)

        self._close_anim.start()

    def _on_animation_step(self):
        """Smoothly lerps hover transitions for both main segments and outer sub-options."""
        self._pulse_val += 0.025 * self._pulse_direction
        if self._pulse_val > 1.0:
            self._pulse_val = 1.0
            self._pulse_direction = -1
        elif self._pulse_val < 0.0:
            self._pulse_val = 0.0
            self._pulse_direction = 1

        changed = False
        target_speed = 0.16

        # Lerp main segment hover weights
        for i in range(len(self._hover_weights)):
            target = 1.0 if i == self.selected_index else 0.0
            diff = target - self._hover_weights[i]
            if abs(diff) > 0.005:
                self._hover_weights[i] += diff * target_speed
                changed = True
            else:
                self._hover_weights[i] = target

        # Lerp sub-options hover weights
        for j in range(len(self._sub_weights)):
            target = 1.0 if j == self.hovered_sub_index else 0.0
            diff = target - self._sub_weights[j]
            if abs(diff) > 0.005:
                self._sub_weights[j] += diff * 0.20
                changed = True
            else:
                self._sub_weights[j] = target

        if changed or self._anim_progress < 1.0:
            self.update()

    # ------------------------------------------------------------------ #
    # Mouse / Hit testing
    # ------------------------------------------------------------------ #
    def _calculate_hit_target(self, pos: QPointF) -> tuple[int, int]:
        """
        Calculates main segment index and sub-option index smoothly without jitter.
        Returns (seg_idx, sub_idx).
        """
        cx = self.width() / 2.0
        cy = self.height() / 2.0
        dx = pos.x() - cx
        dy = pos.y() - cy
        dist = math.hypot(dx, dy)

        deadzone = self.deadzone_radius
        if dist < deadzone:
            return -1, -1

        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        norm_deg = (angle_deg + 90.0) % 360.0

        step_deg = 360.0 / self.segments_count
        shifted_deg = (norm_deg + (step_deg / 2.0)) % 360.0
        natural_seg_idx = int(shifted_deg // step_deg)

        # 1. If currently hovering an expanded segment, check if cursor is in its outer sub-options arc
        if self.selected_index >= 0:
            sub_opts = self.get_sub_options(self.selected_index)
            if sub_opts:
                r_sub_in = self.wheel_radius + 4
                r_sub_out = self.sub_outer_radius + 15
                if r_sub_in <= dist <= r_sub_out:
                    m_angle = -90.0 + (self.selected_index * step_deg)
                    k = len(sub_opts)
                    arc_span = max(step_deg * 1.4, k * 18.0)

                    # Compute difference from mid angle (-180 to +180)
                    angle_diff = (angle_deg - m_angle + 180.0) % 360.0 - 180.0
                    half_span = arc_span / 2.0
                    if -half_span <= angle_diff <= half_span:
                        sub_step = arc_span / k
                        idx_in_arc = int((angle_diff + half_span) // sub_step)
                        idx_in_arc = max(0, min(k - 1, idx_in_arc))
                        return self.selected_index, idx_in_arc

        # 2. Cursor is in main wheel body
        if dist <= self.wheel_radius + (25 * self.scale_factor):
            return natural_seg_idx, -1

        return -1, -1

    def mouseMoveEvent(self, event):
        if not self._db.get_setting("mouse_navigation", True):
            return
        seg_idx, sub_idx = self._calculate_hit_target(event.position())

        # Update sub-option hover
        if sub_idx != self.hovered_sub_index:
            self.hovered_sub_index = sub_idx
            if sub_idx >= 0:
                self._audio.play_select()
            self.update()

        # Update main segment hover
        if seg_idx != self.selected_index:
            self.set_selected_index(seg_idx)

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicked a sub-option
            if self.selected_index >= 0 and self.hovered_sub_index >= 0:
                sub_opts = self.get_sub_options(self.selected_index)
                if 0 <= self.hovered_sub_index < len(sub_opts):
                    chosen_sub = sub_opts[self.hovered_sub_index]
                    self._audio.play_execute()
                    self.action_triggered.emit(chosen_sub)
                    return

            # Clicked main segment
            if self.selected_index >= 0 and self.selected_index < len(self.shortcuts):
                sc = self.shortcuts[self.selected_index]
                if sc.get("action_type") != "none":
                    self.execute_selection()
            elif self.selected_index == -1:
                self.next_category()
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            step = 0.05 if delta > 0 else -0.05
            new_scale = round(max(0.45, min(1.30, self.scale_factor + step)), 2)
            self.apply_scale(new_scale)
            self._db.set_setting("wheel_scale", new_scale)

            p = self.parent()
            if p:
                p_geo = p.geometry()
                cursor_pos = QCursor.pos() - p_geo.topLeft()
                pos_mode = self._db.get_setting("position_mode", "cursor")
                ww = self.width()
                wh = self.height()
                if pos_mode == "cursor":
                    target_x = max(20, min(p_geo.width() - ww - 20, cursor_pos.x() - ww // 2))
                    target_y = max(20, min(p_geo.height() - wh - 20, cursor_pos.y() - wh // 2))
                else:
                    target_x = (p_geo.width() - ww) // 2
                    target_y = (p_geo.height() - wh) // 2
                self.move(target_x, target_y)

            event.accept()
            return

        if self._db.get_setting("scroll_wheel_categories", True):
            delta = event.angleDelta().y()
            if delta > 0:
                self.prev_category()
            elif delta < 0:
                self.next_category()
            event.accept()
        else:
            super().wheelEvent(event)

    # ------------------------------------------------------------------ #
    # Selection helpers
    # ------------------------------------------------------------------ #
    def set_selected_index(self, idx: int):
        if idx != self.selected_index:
            self.selected_index = idx
            self.hovered_sub_index = -1
            if idx >= 0:
                self._audio.play_select()
                self.selection_changed.emit(idx)
            self.update()

    def select_next(self):
        new_idx = 0 if self.selected_index < 0 else (self.selected_index + 1) % self.segments_count
        self.set_selected_index(new_idx)

    def select_prev(self):
        new_idx = self.segments_count - 1 if self.selected_index <= 0 else (self.selected_index - 1) % self.segments_count
        self.set_selected_index(new_idx)

    def select_direction(self, direction: str):
        d = direction.upper()
        n = self.segments_count
        angle_map = {"UP": 0.0, "RIGHT": 90.0, "DOWN": 180.0, "LEFT": 270.0}
        target_angle = angle_map.get(d, 0.0)
        step_deg = 360.0 / n
        idx = int(round(target_angle / step_deg)) % n
        self.set_selected_index(idx)

    def execute_selection(self):
        if self.hovered_sub_index >= 0 and self.selected_index >= 0:
            sub_opts = self.get_sub_options(self.selected_index)
            if 0 <= self.hovered_sub_index < len(sub_opts):
                self._audio.play_execute()
                self.action_triggered.emit(sub_opts[self.hovered_sub_index])
                return

        if self.selected_index >= 0 and self.selected_index < len(self.shortcuts):
            sc = self.shortcuts[self.selected_index]
            if sc.get("action_type") != "none":
                self._audio.play_execute()
                self.action_triggered.emit(sc)

    # ------------------------------------------------------------------ #
    # Wallpaper helpers
    # ------------------------------------------------------------------ #
    def _get_wallpaper_pixmap(self, path: str) -> Optional[QPixmap]:
        if path != self._wallpaper_path:
            self._wallpaper_path = path
            self._wallpaper_pixmap = None
            if path and os.path.isfile(path):
                pix = QPixmap(path)
                if not pix.isNull():
                    self._wallpaper_pixmap = pix
        return self._wallpaper_pixmap

    # ------------------------------------------------------------------ #
    # PAINTING — PURE BLACK & WHITE / MONOCHROME
    # ------------------------------------------------------------------ #
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        cx = self.width() / 2.0
        cy = self.height() / 2.0

        settings = self._db.get_all_settings()

        # Pure Black & White Palette
        c_white = QColor(255, 255, 255)
        c_dark_plate = QColor(10, 10, 12)
        c_seg_bg = QColor(18, 18, 22)
        c_active_glow = QColor(255, 255, 255)

        overall_opacity = float(settings.get("overall_opacity", 0.95))
        bg_opacity = float(settings.get("bg_opacity", 0.75))
        seg_opacity = float(settings.get("segment_opacity", 0.90))

        # Animated scale & rotation
        scale_val = 1.0
        rot_val = 0.0
        if self._anim_progress < 1.0:
            scale_val = getattr(self, "start_scale", 0.85) + (1.0 - getattr(self, "start_scale", 0.85)) * self._anim_progress
            rot_val = getattr(self, "start_rot", -15.0) * (1.0 - self._anim_progress)

        painter.save()
        painter.translate(cx, cy)
        painter.scale(scale_val, scale_val)
        painter.rotate(rot_val)
        painter.setOpacity(self._anim_progress * overall_opacity)

        # ── 1. Outer Ambient Glow & Frosted Backdrop Plate ──
        bg_grad = QRadialGradient(0, 0, self.wheel_radius + 30)
        bg_grad.setColorAt(0.0, QColor(14, 14, 16, int(bg_opacity * 200)))
        bg_grad.setColorAt(0.7, QColor(8, 8, 10, int(bg_opacity * 210)))
        bg_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(bg_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(0, 0), self.wheel_radius + 20, self.wheel_radius + 20)

        # ── 2. Optional Wallpaper clipped to wheel donut ──
        wallpaper_path = settings.get("wheel_wallpaper", "")
        if wallpaper_path:
            wp_pix = self._get_wallpaper_pixmap(wallpaper_path)
            if wp_pix is not None:
                donut_clip = QPainterPath()
                donut_clip.addEllipse(QPointF(0, 0), self.wheel_radius, self.wheel_radius)
                inner_hole = QPainterPath()
                inner_hole.addEllipse(QPointF(0, 0), self.inner_radius, self.inner_radius)
                donut_clip = donut_clip.subtracted(inner_hole)

                painter.save()
                painter.setClipPath(donut_clip)
                diam = int(self.wheel_radius * 2)
                scaled_pix = wp_pix.scaled(diam, diam,
                                           Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                           Qt.TransformationMode.SmoothTransformation)
                draw_x = int(-scaled_pix.width() / 2)
                draw_y = int(-scaled_pix.height() / 2)

                painter.setOpacity(0.35 * self._anim_progress * overall_opacity)
                painter.drawPixmap(draw_x, draw_y, scaled_pix)
                painter.restore()
                painter.setOpacity(self._anim_progress * overall_opacity)

        # ── 3. Outer Ring Bevel (Sleek White Border) ──
        outer_rim_pen = QPen(QColor(255, 255, 255, 25), 1.5)
        painter.setPen(outer_rim_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(0, 0), self.wheel_radius, self.wheel_radius)

        # ── 4. Draw Radial Segments ──
        n = self.segments_count
        step_deg = 360.0 / n
        gap_deg = 3.0

        for i in range(n):
            hw = self._hover_weights[i] if i < len(self._hover_weights) else 0.0

            mid_angle = -90.0 + (i * step_deg)
            start_ang = mid_angle - (step_deg / 2.0) + (gap_deg / 2.0)
            sweep_ang = step_deg - gap_deg

            # Outer radius expands smoothly
            r_out = self.wheel_radius + (20.0 * hw)
            r_in = self.inner_radius

            path = QPainterPath()
            rect_out = QRectF(-r_out, -r_out, r_out * 2, r_out * 2)
            rect_in = QRectF(-r_in, -r_in, r_in * 2, r_in * 2)

            path.arcMoveTo(rect_out, -start_ang)
            path.arcTo(rect_out, -start_ang, -sweep_ang)
            path.arcTo(rect_in, -(start_ang + sweep_ang), sweep_ang)
            path.closeSubpath()

            # Segment fill: Monochrome Gradient
            if hw > 0.01:
                # Active segment: High-contrast white glow / frosted crystal
                seg_grad = QRadialGradient(0, 0, r_out)
                seg_grad.setColorAt(0.3, QColor(35, 35, 42, int(seg_opacity * 230)))
                seg_grad.setColorAt(0.85, QColor(255, 255, 255, int(hw * 75)))
                seg_grad.setColorAt(1.0, QColor(255, 255, 255, int(hw * 210)))
                painter.setBrush(QBrush(seg_grad))

                # Crisp white border
                border_pen = QPen(QColor(255, 255, 255, int(180 + 75 * hw)), 1.5 + (1.0 * hw))
                painter.setPen(border_pen)
            else:
                # Inactive: deep dark translucent slate
                inactive_c = QColor(16, 16, 20, int(seg_opacity * 200))
                painter.setBrush(QBrush(inactive_c))
                painter.setPen(QPen(QColor(255, 255, 255, 24), 0.8))

            painter.drawPath(path)

            # Draw Segment Content: Icon + Label
            if i < len(self.shortcuts):
                sc = self.shortcuts[i]
                label_text = sc.get("label", f"Action {i+1}")
                icon_name = sc.get("icon", "app")

                # Shift outward smoothly on hover
                r_mid_base = (r_in + self.wheel_radius) / 2.0
                r_mid = r_mid_base + (8.0 * hw)

                mid_rad = math.radians(mid_angle)
                icon_x = math.cos(mid_rad) * r_mid
                icon_y = math.sin(mid_rad) * r_mid

                sf = self.scale_factor
                icon_size = max(14, int((26 + (10 * hw)) * sf))
                icon_col = "#FFFFFF"
                pix = IconProvider.get_pixmap(icon_name, icon_col, icon_size)
                painter.drawPixmap(
                    int(icon_x - icon_size / 2.0),
                    int(icon_y - icon_size / 2.0 - (5 * sf)),
                    pix
                )

                f_size = max(6, int((7.2 + (1.2 * hw)) * sf))
                font = QFont(
                    settings.get("font_family", "Segoe UI"),
                    f_size,
                    QFont.Weight.Bold if hw > 0.3 else QFont.Weight.DemiBold
                )
                painter.setFont(font)
                painter.setPen(QColor(255, 255, 255, int(255 if hw > 0.3 else 170)))

                # Ensure text rect fits neatly inside the segment without overlapping outer arcs
                tw = 85 * sf
                th = 20 * sf
                text_rect = QRectF(
                    icon_x - tw / 2.0,
                    icon_y + (icon_size / 2.0) - (6 * sf),
                    tw, th
                )
                painter.drawText(
                    text_rect,
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                    label_text
                )

        # ── 5. DRAW EXPANDED SUB-OPTIONS ARC FOR HOVERED ITEM ──
        if self.selected_index >= 0 and self.selected_index < len(self.shortcuts):
            hw_sel = self._hover_weights[self.selected_index] if self.selected_index < len(self._hover_weights) else 0.0
            if hw_sel > 0.05:
                self._paint_sub_options(painter, self.selected_index, hw_sel, settings)

        # ── 6. Center Ring & HUD Display ──
        self._paint_center_display(painter, settings)

        painter.restore()

    def _paint_sub_options(
        self,
        painter: QPainter,
        segment_index: int,
        hover_weight: float,
        settings: Dict[str, Any]
    ):
        """Draws outer sub-options arc with clean separation and zero overlap."""
        sub_opts = self.get_sub_options(segment_index)
        if not sub_opts:
            return

        k = len(sub_opts)
        step_deg = 360.0 / self.segments_count
        mid_angle = -90.0 + (segment_index * step_deg)

        # Clean angular span tailored to the segment count
        arc_span = max(step_deg * 1.35, k * 18.0)
        sub_step = arc_span / k
        gap_sub = 2.4

        # Clear gap between main wheel and outer arc
        r_in = (self.wheel_radius + 24.0) + (4.0 * (1.0 - hover_weight))
        r_out_base = self.sub_outer_radius
        sf = self.scale_factor

        for j in range(k):
            item = sub_opts[j]
            lbl = item.get("label", f"Sub {j+1}")
            ic_name = item.get("icon", "star")

            sub_hw = self._sub_weights[j] if j < len(self._sub_weights) else 0.0
            r_out = r_out_base + (8.0 * sub_hw)

            item_mid_angle = (mid_angle - (arc_span / 2.0)) + (j * sub_step) + (sub_step / 2.0)
            item_start_ang = item_mid_angle - (sub_step / 2.0) + (gap_sub / 2.0)
            item_sweep_ang = sub_step - gap_sub

            # Sub-segment path
            path = QPainterPath()
            rect_out = QRectF(-r_out, -r_out, r_out * 2, r_out * 2)
            rect_in = QRectF(-r_in, -r_in, r_in * 2, r_in * 2)

            path.arcMoveTo(rect_out, -item_start_ang)
            path.arcTo(rect_out, -item_start_ang, -item_sweep_ang)
            path.arcTo(rect_in, -(item_start_ang + item_sweep_ang), item_sweep_ang)
            path.closeSubpath()

            # Styling for sub-segment — Monochrome Black & White
            alpha_mult = hover_weight
            if j == self.hovered_sub_index or sub_hw > 0.01:
                # Active sub-option: bright frosted white glow
                sub_grad = QRadialGradient(0, 0, r_out)
                sub_grad.setColorAt(0.2, QColor(40, 40, 48, int(245 * alpha_mult)))
                sub_grad.setColorAt(0.85, QColor(255, 255, 255, int(180 * alpha_mult)))
                painter.setBrush(QBrush(sub_grad))

                glow_pen = QPen(QColor(255, 255, 255, int(255 * alpha_mult)), 1.8 + (1.0 * sub_hw))
                painter.setPen(glow_pen)
            else:
                # Inactive sub-option: clean dark glass pill
                bg_sub = QColor(14, 14, 18, int(215 * alpha_mult))
                painter.setBrush(QBrush(bg_sub))
                painter.setPen(QPen(QColor(255, 255, 255, int(50 * alpha_mult)), 1.0))

            painter.drawPath(path)

            # Sub-item Content: Icon & small clean label
            r_sub_mid = (r_in + r_out) / 2.0
            mid_rad = math.radians(item_mid_angle)
            sx = math.cos(mid_rad) * r_sub_mid
            sy = math.sin(mid_rad) * r_sub_mid

            sz = max(12, int((18 + (4 * sub_hw)) * sf))
            col_icon = "#FFFFFF"
            pix = IconProvider.get_pixmap(ic_name, col_icon, sz)
            painter.drawPixmap(int(sx - sz / 2.0), int(sy - sz / 2.0 - (4 * sf)), pix)

            f_sub_sz = max(5, int((6.8 + (0.6 * sub_hw)) * sf))
            f_opt = QFont(settings.get("font_family", "Segoe UI"), f_sub_sz, QFont.Weight.Bold)
            painter.setFont(f_opt)
            painter.setPen(QColor(255, 255, 255, int(250 * alpha_mult)))

            txt_rect = QRectF(sx - 40 * sf, sy + (sz / 2.0) - (3 * sf), 80 * sf, 15 * sf)
            painter.drawText(txt_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, lbl)

    def _paint_center_display(
        self,
        painter: QPainter,
        settings: Dict[str, Any]
    ):
        r_c = self.center_radius
        sf = self.scale_factor

        # Center plate — frosted monochrome dark glass
        center_grad = QRadialGradient(0, 0, r_c)
        center_grad.setColorAt(0.0, QColor(10, 10, 14, 245))
        center_grad.setColorAt(0.82, QColor(18, 18, 24, 250))
        center_grad.setColorAt(1.0, QColor(28, 28, 36, 255))

        painter.setBrush(QBrush(center_grad))
        pulse_alpha = int(120 + (100 * self._pulse_val))
        pulse_pen = QPen(QColor(255, 255, 255, pulse_alpha), 1.8)
        painter.setPen(pulse_pen)
        painter.drawEllipse(QPointF(0, 0), r_c, r_c)

        # Subtle monochrome decorative ticks
        painter.setPen(QPen(QColor(255, 255, 255, 35), 0.8))
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            x1 = math.cos(rad) * (r_c - (8 * sf))
            y1 = math.sin(rad) * (r_c - (8 * sf))
            x2 = math.cos(rad) * (r_c - (3 * sf))
            y2 = math.sin(rad) * (r_c - (3 * sf))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Check if hovering a sub-option
        if self.selected_index >= 0 and self.hovered_sub_index >= 0:
            sub_opts = self.get_sub_options(self.selected_index)
            if 0 <= self.hovered_sub_index < len(sub_opts):
                sub_item = sub_opts[self.hovered_sub_index]
                label = sub_item.get("label", "Sub Action")
                hint = sub_item.get("hotkey_hint", "EXECUTE")
                ic_name = sub_item.get("icon", "star")

                c_icon_sz = max(18, int(32 * sf))
                pix = IconProvider.get_pixmap(ic_name, "#FFFFFF", c_icon_sz)
                painter.drawPixmap(-c_icon_sz // 2, -int(44 * sf), pix)

                f_title = QFont(settings.get("font_family", "Segoe UI"), max(6, int(8.2 * sf)), QFont.Weight.ExtraBold)
                painter.setFont(f_title)
                painter.setPen(QColor(255, 255, 255, 255))
                painter.drawText(QRectF(-r_c + 8 * sf, -6 * sf, (r_c - 8 * sf) * 2, 20 * sf), Qt.AlignmentFlag.AlignCenter, label.upper())

                f_sub = QFont(settings.get("font_family", "Segoe UI"), max(5, int(6 * sf)), QFont.Weight.Bold)
                painter.setFont(f_sub)
                painter.setPen(QColor(200, 200, 200))
                painter.drawText(QRectF(-r_c + 8 * sf, 15 * sf, (r_c - 8 * sf) * 2, 15 * sf), Qt.AlignmentFlag.AlignCenter, "⚡ SUB-OPTION")

                f_hint = QFont(settings.get("font_family", "Segoe UI"), max(5, int(6 * sf)), QFont.Weight.DemiBold)
                painter.setFont(f_hint)
                painter.setPen(QColor(160, 160, 160))
                painter.drawText(QRectF(-r_c + 8 * sf, 30 * sf, (r_c - 8 * sf) * 2, 15 * sf), Qt.AlignmentFlag.AlignCenter, hint)
                return

        # Main selection
        if self.selected_index >= 0 and self.selected_index < len(self.shortcuts):
            sc = self.shortcuts[self.selected_index]
            label = sc.get("label", "Unknown Action")
            action_type = sc.get("action_type", "").upper()
            hotkey_hint = sc.get("hotkey_hint", "")
            icon_name = sc.get("icon", "app")
            is_destructive = sc.get("is_destructive", 0)

            c_icon_sz = max(18, int(34 * sf))
            icon_col = "#FF5555" if is_destructive else "#FFFFFF"
            pix = IconProvider.get_pixmap(icon_name, icon_col, c_icon_sz)
            painter.drawPixmap(-c_icon_sz // 2, -int(46 * sf), pix)

            f_title = QFont(
                settings.get("font_family", "Segoe UI"),
                max(6, int(8.8 * sf)),
                QFont.Weight.ExtraBold
            )
            painter.setFont(f_title)
            painter.setPen(QColor(255, 255, 255, 255))
            painter.drawText(
                QRectF(-r_c + 8 * sf, -6 * sf, (r_c - 8 * sf) * 2, 20 * sf),
                Qt.AlignmentFlag.AlignCenter,
                label.upper()
            )

            f_sub = QFont(
                settings.get("font_family", "Segoe UI"),
                max(5, int(6 * sf)),
                QFont.Weight.Bold
            )
            painter.setFont(f_sub)
            painter.setPen(QColor(210, 210, 210) if not is_destructive else QColor("#FF5555"))
            tag_text = f"[{action_type}]" if not is_destructive else "⚠ CONFIRM REQUIRED"
            painter.drawText(
                QRectF(-r_c + 8 * sf, 15 * sf, (r_c - 8 * sf) * 2, 15 * sf),
                Qt.AlignmentFlag.AlignCenter,
                tag_text
            )

            # Hotkey / expansion hint
            f_hint = QFont(
                settings.get("font_family", "Segoe UI"),
                max(5, int(6 * sf)),
                QFont.Weight.DemiBold
            )
            painter.setFont(f_hint)
            painter.setPen(QColor(160, 160, 160))
            sub_count = len(self.get_sub_options(self.selected_index))
            hint_str = hotkey_hint if hotkey_hint else (f"▾ {sub_count} SUB-OPTIONS" if sub_count else "CLICK TO RUN")
            painter.drawText(
                QRectF(-r_c + 8 * sf, 30 * sf, (r_c - 8 * sf) * 2, 15 * sf),
                Qt.AlignmentFlag.AlignCenter,
                hint_str
            )

        else:
            # Idle / Deadzone display
            cat_name = self.categories[self.active_category_index]["name"] if self.categories else "NEXUS WHEEL"
            wheel_name = self.wheel_data.get("name", "MAIN WHEEL").upper()

            logo_sz = max(16, int(30 * sf))
            pix = IconProvider.get_pixmap("wheel", "#FFFFFF", logo_sz)
            painter.drawPixmap(-logo_sz // 2, -int(40 * sf), pix)

            f_title = QFont(
                settings.get("font_family", "Segoe UI"),
                max(6, int(8.8 * sf)),
                QFont.Weight.ExtraBold
            )
            painter.setFont(f_title)
            painter.setPen(QColor(255, 255, 255, 255))
            painter.drawText(
                QRectF(-r_c + 8 * sf, -8 * sf, (r_c - 8 * sf) * 2, 20 * sf),
                Qt.AlignmentFlag.AlignCenter,
                cat_name.upper()
            )

            f_sub = QFont(
                settings.get("font_family", "Segoe UI"),
                max(5, int(6 * sf)),
                QFont.Weight.Bold
            )
            painter.setFont(f_sub)
            painter.setPen(QColor(200, 200, 200))
            painter.drawText(
                QRectF(-r_c + 8 * sf, 12 * sf, (r_c - 8 * sf) * 2, 15 * sf),
                Qt.AlignmentFlag.AlignCenter,
                wheel_name
            )

            f_hint = QFont(
                settings.get("font_family", "Segoe UI"),
                max(5, int(6 * sf)),
                QFont.Weight.Normal
            )
            painter.setFont(f_hint)
            painter.setPen(QColor(150, 150, 150))
            hint_txt = "SCROLL: CAT • CTRL+SCROLL: RESIZE"
            painter.drawText(
                QRectF(-r_c + 8 * sf, 27 * sf, (r_c - 8 * sf) * 2, 15 * sf),
                Qt.AlignmentFlag.AlignCenter,
                hint_txt
            )
