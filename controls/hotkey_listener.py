"""
Global Hotkey & Player Controls Listener for Nexus Wheel.
Listens for global key-down and key-up events across Windows,
supporting both 'Hold-to-Activate' and 'Toggle' modes for multiple radial wheels.
"""

import threading
from typing import Dict, Any, List, Optional
from PySide6.QtCore import QObject, Signal
from database.db import DatabaseManager
from pynput import keyboard

class GlobalHotkeyManager(QObject):
    wheel_toggle_requested = Signal(str)      # wheel_id
    wheel_hold_start = Signal(str)            # wheel_id
    wheel_hold_end = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self._listener: Optional[keyboard.Listener] = None
        self._running = False
        
        # Modifier states
        self._ctrl_down = False
        self._alt_down = False
        self._shift_down = False
        self._win_down = False

        # Active hold state
        self._currently_held_wheel: Optional[str] = None
        self._held_trigger_key: Optional[str] = None

        # Registered hotkey map: parsed combo string -> wheel_id
        # e.g., "alt+x" -> "wheel_main"
        self._hotkey_map: Dict[str, str] = {}
        self.reload_hotkeys()

    def reload_hotkeys(self):
        """Reads all wheels from DB and sets up hotkey mapping."""
        self._hotkey_map.clear()
        wheels = self._db.get_wheels()
        for w in wheels:
            hk = w.get("hotkey", "").strip().lower()
            if hk:
                norm_hk = self._normalize_combo(hk)
                self._hotkey_map[norm_hk] = w["id"]

    def _normalize_combo(self, combo_str: str) -> str:
        parts = [p.strip().lower() for p in combo_str.split("+") if p.strip()]
        mods = []
        keys = []
        for p in parts:
            if p in ("ctrl", "control"):
                mods.append("ctrl")
            elif p in ("alt", "menu"):
                mods.append("alt")
            elif p in ("shift",):
                mods.append("shift")
            elif p in ("win", "cmd", "windows"):
                mods.append("win")
            else:
                keys.append(p)
        mods = sorted(list(set(mods)))
        keys = sorted(keys)
        return "+".join(mods + keys)

    def start(self):
        if self._running:
            return
        self._running = True
        self._listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        self._running = False
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def _key_to_str(self, key) -> str:
        if isinstance(key, keyboard.Key):
            k_name = key.name.lower()
            if "ctrl" in k_name:
                return "ctrl"
            if "alt" in k_name:
                return "alt"
            if "shift" in k_name:
                return "shift"
            if "cmd" in k_name or "win" in k_name:
                return "win"
            return k_name
        elif hasattr(key, "char") and key.char:
            return key.char.lower()
        return str(key).lower().replace("'", "")

    def _on_key_press(self, key):
        if not self._db.get_setting("global_hotkeys_enabled", True):
            return

        k_str = self._key_to_str(key)

        # Update modifier states
        if k_str == "ctrl":
            self._ctrl_down = True
        elif k_str == "alt":
            self._alt_down = True
        elif k_str == "shift":
            self._shift_down = True
        elif k_str == "win":
            self._win_down = True

        # Build current combo
        active_mods = []
        if self._ctrl_down: active_mods.append("ctrl")
        if self._alt_down: active_mods.append("alt")
        if self._shift_down: active_mods.append("shift")
        if self._win_down: active_mods.append("win")

        if k_str not in ("ctrl", "alt", "shift", "win"):
            combo = "+".join(sorted(active_mods) + [k_str])
            
            # Check match in hotkey map
            if combo in self._hotkey_map:
                wheel_id = self._hotkey_map[combo]
                mode = self._db.get_setting("activation_mode", "toggle")

                if mode == "hold":
                    if not self._currently_held_wheel:
                        self._currently_held_wheel = wheel_id
                        self._held_trigger_key = k_str
                        self.wheel_hold_start.emit(wheel_id)
                else: # Toggle mode
                    self.wheel_toggle_requested.emit(wheel_id)

    def _on_key_release(self, key):
        k_str = self._key_to_str(key)

        if k_str == "ctrl":
            self._ctrl_down = False
        elif k_str == "alt":
            self._alt_down = False
        elif k_str == "shift":
            self._shift_down = False
        elif k_str == "win":
            self._win_down = False

        # In hold mode: releasing either the trigger key or activation modifier releases the wheel
        if self._currently_held_wheel:
            mode = self._db.get_setting("activation_mode", "toggle")
            if mode == "hold":
                if k_str == self._held_trigger_key or k_str in ("alt", "ctrl", "shift"):
                    self._currently_held_wheel = None
                    self._held_trigger_key = None
                    self.wheel_hold_end.emit()
