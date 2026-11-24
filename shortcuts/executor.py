"""
Action Executor for Nexus Wheel.
Executes all built-in and custom shortcut actions safely with exception handling.
"""

import os
import subprocess
import webbrowser
import threading
from typing import Dict, Any, Callable, Optional
from windows.win32_integration import WindowsIntegration, send_key_combo
import win32con

KEY_MAP = {
    "ctrl": 0x11,
    "control": 0x11,
    "lctrl": 0xA2,
    "rctrl": 0xA3,
    "alt": 0x12,
    "menu": 0x12,
    "lalt": 0xA4,
    "ralt": 0xA5,
    "shift": 0x10,
    "lshift": 0xA0,
    "rshift": 0xA1,
    "win": 0x5B,
    "windows": 0x5B,
    "tab": 0x09,
    "enter": 0x0D,
    "esc": 0x1B,
    "escape": 0x1B,
    "space": 0x20,
    "backspace": 0x08,
    "delete": 0x2E,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B
}

def parse_hotkey_string(hotkey_str: str):
    """Converts a hotkey string like 'Ctrl+Shift+S' into a list of VK codes."""
    parts = [p.strip().lower() for p in hotkey_str.split("+") if p.strip()]
    vk_list = []
    for p in parts:
        if p in KEY_MAP:
            vk_list.append(KEY_MAP[p])
        elif len(p) == 1:
            vk_list.append(ord(p.upper()))
    return vk_list

class ActionExecutor:
    @staticmethod
    def execute(shortcut: Dict[str, Any], previous_active_hwnd: Optional[int] = None, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Executes a shortcut action.
        previous_active_hwnd is the HWND of the window that had focus before the wheel opened.
        context is an optional dict providing extra activation parameters (e.g. screen_img, cursor_pos).
        """
        action_type = shortcut.get("action_type", "")
        target = shortcut.get("target", "")
        arguments = shortcut.get("arguments", "")

        try:
            # 1. Applications
            if action_type == "app":
                if target.startswith("ms-settings:"):
                    WindowsIntegration.open_uri(target)
                elif target.endswith(".exe") or "/" in target or "\\" in target:
                    if arguments:
                        subprocess.Popen([target, arguments], shell=True)
                    else:
                        os.startfile(target)
                else:
                    # Generic command or protocol
                    if arguments:
                        subprocess.Popen(f"{target} {arguments}", shell=True)
                    else:
                        subprocess.Popen(target, shell=True)
                return True

            # 2. System Controls
            elif action_type == "system":
                t = target.lower()
                if t == "volume_up":
                    WindowsIntegration.volume_up()
                elif t == "volume_down":
                    WindowsIntegration.volume_down()
                elif t == "mute_toggle":
                    WindowsIntegration.volume_mute()
                elif t == "brightness_up":
                    WindowsIntegration.adjust_brightness(10)
                elif t == "brightness_down":
                    WindowsIntegration.adjust_brightness(-10)
                elif t == "lock_pc":
                    WindowsIntegration.lock_workstation()
                elif t == "sleep_pc":
                    WindowsIntegration.sleep_pc()
                elif t == "shutdown_pc":
                    WindowsIntegration.shutdown_pc()
                elif t == "restart_pc":
                    WindowsIntegration.restart_pc()
                elif t.startswith("ms-settings:"):
                    WindowsIntegration.open_uri(t)
                return True

            # 3. Media Controls
            elif action_type == "media":
                t = target.lower()
                if t == "play_pause":
                    WindowsIntegration.media_play_pause()
                elif t == "next_track":
                    WindowsIntegration.media_next()
                elif t == "prev_track":
                    WindowsIntegration.media_prev()
                elif t == "mute_toggle":
                    WindowsIntegration.volume_mute()
                elif t == "stop":
                    WindowsIntegration.media_stop()
                return True

            # 4. Window Management (Targets the previously active window)
            elif action_type == "window":
                t = target.lower()
                if t == "minimize":
                    WindowsIntegration.minimize_active_window(previous_active_hwnd)
                elif t == "maximize":
                    WindowsIntegration.maximize_or_restore_active_window(previous_active_hwnd)
                elif t == "close":
                    WindowsIntegration.close_active_window(previous_active_hwnd)
                elif t == "snap_left":
                    WindowsIntegration.snap_left()
                elif t == "snap_right":
                    WindowsIntegration.snap_right()
                elif t == "desktop":
                    WindowsIntegration.show_desktop()
                elif t == "toggle_top":
                    WindowsIntegration.toggle_always_on_top(previous_active_hwnd)
                elif t == "switch_app":
                    WindowsIntegration.switch_app()
                return True

            # 5. Productivity
            elif action_type in ("productivity", "photo"):
                t = target.lower()
                if t in ("download_photo", "photo_download", "download_image", "photo_grabber"):
                    from utils.photo_downloader import PhotoDownloader
                    from windows.photo_downloader_dialog import NexusPhotoDownloaderDialog
                    from PySide6.QtGui import QCursor
                    from PySide6.QtCore import QPoint

                    screen_img = context.get("screen_img") if context else None
                    cursor_pos = context.get("cursor_pos") if context else None
                    if not screen_img:
                        screen_img = PhotoDownloader.capture_full_screen()
                    if not cursor_pos:
                        cursor_pos = QCursor.pos()

                    dlg = NexusPhotoDownloaderDialog(screen_img, cursor_pos)
                    dlg.exec()
                    return True

                elif t.startswith("download_photo_") or t.startswith("photo_download_"):
                    fmt = t.split("_")[-1].upper()
                    from utils.photo_downloader import PhotoDownloader
                    from windows.audio_controller import AudioController
                    from database.db import DatabaseManager
                    from PySide6.QtGui import QCursor
                    from PySide6.QtWidgets import QMessageBox

                    screen_img = context.get("screen_img") if context else None
                    cursor_pos = context.get("cursor_pos") if context else None
                    if not screen_img:
                        screen_img = PhotoDownloader.capture_full_screen()
                    if not cursor_pos:
                        cursor_pos = QCursor.pos()

                    bounds = PhotoDownloader.detect_photo_bounds(screen_img, cursor_pos.x(), cursor_pos.y())
                    cropped = PhotoDownloader.crop_photo(screen_img, bounds)

                    db = DatabaseManager()
                    folder = db.get_setting("photo_download_dir", "") or PhotoDownloader.get_default_download_dir()
                    filename = PhotoDownloader.generate_default_filename(fmt)
                    out_path = os.path.join(folder, filename)

                    PhotoDownloader.save_image(cropped, out_path, fmt)
                    AudioController().play_execute()

                    # Show non-blocking notification or confirmation
                    try:
                        subprocess.Popen(f'explorer /select,"{os.path.abspath(out_path)}"')
                    except Exception:
                        pass
                    return True

                elif t == "copy":
                    WindowsIntegration.clipboard_copy()
                elif t == "paste":
                    WindowsIntegration.clipboard_paste()
                elif t == "cut":
                    WindowsIntegration.clipboard_cut()
                elif t == "undo":
                    WindowsIntegration.undo()
                elif t == "redo":
                    WindowsIntegration.redo()
                elif t == "screenshot":
                    WindowsIntegration.trigger_screenshot()
                elif t == "clipboard_history":
                    WindowsIntegration.open_clipboard_history()
                return True

            # 6. Custom Actions
            elif action_type == "custom_exe":
                if arguments:
                    subprocess.Popen([target, arguments], shell=True)
                else:
                    os.startfile(target)
                return True

            elif action_type == "custom_web":
                url = target if target.startswith("http") else f"https://{target}"
                webbrowser.open(url)
                return True

            elif action_type == "custom_cmd":
                subprocess.Popen(target, shell=True)
                return True

            elif action_type == "custom_py":
                if os.path.exists(target):
                    subprocess.Popen(["python", target], shell=True)
                return True

            elif action_type == "custom_hotkey":
                vks = parse_hotkey_string(target)
                if vks:
                    send_key_combo(*vks)
                return True

            elif action_type == "custom_file" or action_type == "custom_folder":
                os.startfile(target)
                return True

        except Exception as e:
            print(f"Failed to execute action {shortcut}: {e}")
            return False

        return False
