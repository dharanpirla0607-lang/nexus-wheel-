"""
Windows 11 API Integration for Nexus Wheel.
Provides native Win32 controls for audio, media, display, windows management,
registry startup, and fullscreen gaming detection.
"""

import os
import sys
import subprocess
import webbrowser
import ctypes
from ctypes import wintypes
import win32api
import win32con
import win32gui
import win32process
import win32security
import winreg

# Key event virtual keys
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_LWIN = 0x5B
VK_LSHIFT = 0xA0
VK_LCONTROL = 0xA2
VK_LMENU = 0xA4

def send_key_combo(*vk_keys):
    """Sends a keyboard shortcut by pressing all keys and releasing them."""
    for vk in vk_keys:
        win32api.keybd_event(vk, 0, 0, 0)
    for vk in reversed(vk_keys):
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)

def send_key(vk):
    win32api.keybd_event(vk, 0, 0, 0)
    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)

class WindowsIntegration:
    @staticmethod
    def volume_up():
        send_key(VK_VOLUME_UP)

    @staticmethod
    def volume_down():
        send_key(VK_VOLUME_DOWN)

    @staticmethod
    def volume_mute():
        send_key(VK_VOLUME_MUTE)

    @staticmethod
    def media_play_pause():
        send_key(VK_MEDIA_PLAY_PAUSE)

    @staticmethod
    def media_next():
        send_key(VK_MEDIA_NEXT_TRACK)

    @staticmethod
    def media_prev():
        send_key(VK_MEDIA_PREV_TRACK)

    @staticmethod
    def media_stop():
        send_key(VK_MEDIA_STOP)

    @staticmethod
    def adjust_brightness(delta: int = 10):
        try:
            # PowerShell WmiMonitorBrightnessMethods
            cmd = f"""
            $b = (Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightness).CurrentBrightness + ({delta});
            if ($b -gt 100) {{ $b = 100 }} elseif ($b -lt 10) {{ $b = 10 }};
            (Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, $b)
            """
            subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", cmd],
                             creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            print(f"Brightness adjustment error: {e}")

    @staticmethod
    def lock_workstation():
        ctypes.windll.user32.LockWorkStation()

    @staticmethod
    def sleep_pc():
        try:
            # SetSuspendState(bHibernate=0, bForce=1, bWakeupEventsDisabled=0)
            ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
        except Exception as e:
            print(f"Sleep failed: {e}")

    @staticmethod
    def shutdown_pc():
        os.system("shutdown /s /t 0")

    @staticmethod
    def restart_pc():
        os.system("shutdown /r /t 0")

    @staticmethod
    def open_uri(uri: str):
        try:
            os.startfile(uri)
        except Exception:
            webbrowser.open(uri)

    # Window Management
    @staticmethod
    def get_foreground_window():
        return win32gui.GetForegroundWindow()

    @staticmethod
    def get_window_title(hwnd):
        return win32gui.GetWindowText(hwnd)

    @staticmethod
    def get_window_process_name(hwnd):
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            import psutil
            proc = psutil.Process(pid)
            return proc.name()
        except Exception:
            return ""

    @staticmethod
    def minimize_active_window(hwnd=None):
        if hwnd is None:
            hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

    @staticmethod
    def maximize_or_restore_active_window(hwnd=None):
        if hwnd is None:
            hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] == win32con.SW_SHOWMAXIMIZED:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

    @staticmethod
    def close_active_window(hwnd=None):
        if hwnd is None:
            hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    @staticmethod
    def toggle_always_on_top(hwnd=None):
        if hwnd is None:
            hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            is_topmost = bool(ex_style & win32con.WS_EX_TOPMOST)
            flag = win32con.HWND_NOTOPMOST if is_topmost else win32con.HWND_TOPMOST
            win32gui.SetWindowPos(hwnd, flag, 0, 0, 0, 0,
                                 win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            return not is_topmost
        return False

    @staticmethod
    def snap_left():
        send_key_combo(VK_LWIN, win32con.VK_LEFT)

    @staticmethod
    def snap_right():
        send_key_combo(VK_LWIN, win32con.VK_RIGHT)

    @staticmethod
    def show_desktop():
        send_key_combo(VK_LWIN, ord('D'))

    @staticmethod
    def switch_app():
        send_key_combo(VK_LMENU, win32con.VK_TAB)

    # Productivity
    @staticmethod
    def clipboard_copy():
        send_key_combo(VK_LCONTROL, ord('C'))

    @staticmethod
    def clipboard_paste():
        send_key_combo(VK_LCONTROL, ord('V'))

    @staticmethod
    def clipboard_cut():
        send_key_combo(VK_LCONTROL, ord('X'))

    @staticmethod
    def undo():
        send_key_combo(VK_LCONTROL, ord('Z'))

    @staticmethod
    def redo():
        send_key_combo(VK_LCONTROL, ord('Y'))

    @staticmethod
    def trigger_screenshot():
        send_key_combo(VK_LWIN, VK_LSHIFT, ord('S'))

    @staticmethod
    def open_clipboard_history():
        send_key_combo(VK_LWIN, ord('V'))

    # Startup Integration
    @staticmethod
    def set_startup(enable: bool, app_name: str = "NexusWheel"):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                if getattr(sys, 'frozen', False):
                    exe_path = f'"{sys.executable}"'
                else:
                    main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
                    exe_path = f'"{sys.executable}" "{main_py}"'
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Startup registry error: {e}")
            return False

    @staticmethod
    def is_startup_enabled(app_name: str = "NexusWheel") -> bool:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    # Fullscreen / Gaming detection
    @staticmethod
    def is_foreground_fullscreen() -> bool:
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return False
            # Check window rect against monitor
            rect = win32gui.GetWindowRect(hwnd)
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]
            
            screen_w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            
            # Check if desktop or shell
            cls_name = win32gui.GetClassName(hwnd)
            if cls_name in ["Progman", "WorkerW", "Shell_TrayWnd", "NexusWheelOverlay"]:
                return False

            if w >= screen_w and h >= screen_h:
                return True
        except Exception:
            pass
        return False
