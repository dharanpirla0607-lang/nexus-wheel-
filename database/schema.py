"""
Database Schema & Initialization for Nexus Wheel.
SQLite persistent storage for wheels, categories, shortcuts, and application settings.
"""

import sqlite3
import os
import json
from typing import Dict, Any, List, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nexus_wheel.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS wheels (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    hotkey TEXT NOT NULL,
    segments_count INTEGER DEFAULT 8,
    is_default INTEGER DEFAULT 0,
    order_index INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    wheel_id TEXT NOT NULL,
    name TEXT NOT NULL,
    icon TEXT NOT NULL,
    order_index INTEGER DEFAULT 0,
    FOREIGN KEY(wheel_id) REFERENCES wheels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS shortcuts (
    id TEXT PRIMARY KEY,
    wheel_id TEXT NOT NULL,
    category_id TEXT NOT NULL,
    segment_index INTEGER NOT NULL,
    label TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target TEXT NOT NULL,
    arguments TEXT DEFAULT '',
    icon TEXT NOT NULL,
    hotkey_hint TEXT DEFAULT '',
    is_destructive INTEGER DEFAULT 0,
    FOREIGN KEY(wheel_id) REFERENCES wheels(id) ON DELETE CASCADE,
    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS games_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    blocked INTEGER DEFAULT 1
);
"""

DEFAULT_SETTINGS = {
    # General
    "activation_mode": "toggle", # "hold" or "toggle"
    "activation_hotkey": "Alt+X",
    "position_mode": "cursor",   # "cursor" or "center"
    "wheel_scale": 1.0,          # Dynamic scale (e.g. 0.6=Mini, 0.75=Small, 1.0=Default)
    "photo_download_format": "PNG", # Default download format (PNG, JPG, WEBP, BMP, ICO, TIFF, GIF, PDF)
    "photo_download_dir": "",    # Empty defaults to user Downloads folder
    "photo_auto_open_folder": False,
    "remember_last_position": False,
    "start_with_windows": False,
    "minimize_to_tray": True,
    "global_hotkeys_enabled": True,
    "show_notifications": True,
    
    # Player Controls
    "deadzone_radius": 45,       # inner radius where mouse movement is ignored
    "mouse_navigation": True,
    "keyboard_navigation": True,
    "wasd_navigation": True,
    "scroll_wheel_categories": True,
    "confirm_with_enter": True,
    "cancel_with_escape": True,
    
    # Transparency
    "overall_opacity": 0.95,
    "bg_opacity": 0.85,
    "segment_opacity": 0.90,
    "icon_opacity": 1.0,
    "highlight_opacity": 0.95,
    "blur_intensity": 20,
    "dimming_opacity": 0.0,
    "glass_transparency": 0.85,

    # Animations
    "animations_enabled": True,
    "animation_preset": "GTA V Classic",
    "open_duration": 220,
    "close_duration": 160,
    "segment_transition_speed": 160,
    "hover_animation_speed": 120,
    "scale_animation": True,
    "rotation_animation": True,
    "glow_intensity": 0.85,
    "blur_transition": True,
    "selection_animation": True,

    # Appearance
    "theme": "Cyberpunk Neon",
    "accent_color": "#00F0FF",
    "secondary_color": "#FF007F",
    "bg_color": "#0E1117",
    "text_color": "#FFFFFF",
    "font_family": "Segoe UI Variable Display",

    # Audio
    "audio_enabled": True,
    "audio_volume": 0.80,
    "sound_open": True,
    "sound_close": True,
    "sound_select": True,
    "sound_execute": True,
    "sound_error": True,

    # Gaming Mode
    "gaming_mode_enabled": True,
    "game_detection_mode": "fullscreen", # "fullscreen" or "list"
    "allow_over_fullscreen": True,
    "disable_when_gaming": False
}

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executescript(SCHEMA_SQL)
        
        # Initialize default settings if not exists
        for key, val in DEFAULT_SETTINGS.items():
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, json.dumps(val)))
                
        # Check if default wheels exist
        cursor.execute("SELECT COUNT(*) as cnt FROM wheels")
        if cursor.fetchone()["cnt"] == 0:
            seed_default_data(conn)
            
        # Seed default games
        default_games = [
            ("gta5.exe", "Grand Theft Auto V"),
            ("Valorant.exe", "VALORANT"),
            ("cs2.exe", "Counter-Strike 2"),
            ("Cyberpunk2077.exe", "Cyberpunk 2077"),
            ("Overwatch.exe", "Overwatch 2"),
            ("steam.exe", "Steam Game Client")
        ]
        for proc, disp in default_games:
            cursor.execute("INSERT OR IGNORE INTO games_list (process_name, display_name, blocked) VALUES (?, ?, 1)", (proc, disp))

        # Check if Download Photo shortcut exists in shortcuts
        cursor.execute("SELECT COUNT(*) as cnt FROM shortcuts WHERE target = 'download_photo'")
        if cursor.fetchone()["cnt"] == 0:
            cursor.execute("""
                UPDATE shortcuts 
                SET label = 'Download Photo', action_type = 'productivity', target = 'download_photo', icon = 'photo', hotkey_hint = 'Any Format'
                WHERE (id = 's_prd_4' OR (category_id = 'cat_prod' AND segment_index = 3))
            """)
            
        conn.commit()

def seed_default_data(conn: sqlite3.Connection):
    cursor = conn.cursor()
    
    # 1. Main Wheel (8 segments)
    cursor.execute("""
        INSERT INTO wheels (id, name, hotkey, segments_count, is_default, order_index)
        VALUES ('wheel_main', 'Main Wheel', 'Alt+X', 8, 1, 0)
    """)
    
    # Categories for Main Wheel
    categories = [
        ("cat_apps", "wheel_main", "Applications", "apps", 0),
        ("cat_sys", "wheel_main", "System Controls", "settings", 1),
        ("cat_media", "wheel_main", "Media Controls", "music", 2),
        ("cat_win", "wheel_main", "Window Management", "switch", 3),
        ("cat_prod", "wheel_main", "Productivity", "clipboard", 4)
    ]
    for cid, wid, name, icon, ord_idx in categories:
        cursor.execute("INSERT INTO categories VALUES (?, ?, ?, ?, ?)", (cid, wid, name, icon, ord_idx))
        
    # Shortcuts for cat_apps (8 segments)
    app_shortcuts = [
        ("s_app_1", "wheel_main", "cat_apps", 0, "File Explorer", "app", "explorer.exe", "", "explorer", "Win+E", 0),
        ("s_app_2", "wheel_main", "cat_apps", 1, "Google Chrome", "app", "chrome.exe", "", "chrome", "", 0),
        ("s_app_3", "wheel_main", "cat_apps", 2, "VS Code", "app", "code", "", "code", "", 0),
        ("s_app_4", "wheel_main", "cat_apps", 3, "Settings", "app", "ms-settings:", "", "settings", "Win+I", 0),
        ("s_app_5", "wheel_main", "cat_apps", 4, "Task Manager", "app", "taskmgr.exe", "", "task", "Ctrl+Shift+Esc", 0),
        ("s_app_6", "wheel_main", "cat_apps", 5, "Terminal", "app", "wt.exe", "", "terminal", "", 0),
        ("s_app_7", "wheel_main", "cat_apps", 6, "Calculator", "app", "calc.exe", "", "calc", "", 0),
        ("s_app_8", "wheel_main", "cat_apps", 7, "Notepad", "app", "notepad.exe", "", "note", "", 0),
    ]
    for s in app_shortcuts:
        cursor.execute("INSERT INTO shortcuts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", s)
        
    # Shortcuts for cat_sys (8 segments)
    sys_shortcuts = [
        ("s_sys_1", "wheel_main", "cat_sys", 0, "Volume Up", "system", "volume_up", "", "vol_up", "Vol+", 0),
        ("s_sys_2", "wheel_main", "cat_sys", 1, "Volume Down", "system", "volume_down", "", "vol_down", "Vol-", 0),
        ("s_sys_3", "wheel_main", "cat_sys", 2, "Mute / Unmute", "system", "mute_toggle", "", "mute", "Mute", 0),
        ("s_sys_4", "wheel_main", "cat_sys", 3, "Lock PC", "system", "lock_pc", "", "lock", "Win+L", 0),
        ("s_sys_5", "wheel_main", "cat_sys", 4, "Sleep", "system", "sleep_pc", "", "sleep", "", 1),
        ("s_sys_6", "wheel_main", "cat_sys", 5, "Shutdown", "system", "shutdown_pc", "", "shutdown", "", 1),
        ("s_sys_7", "wheel_main", "cat_sys", 6, "Restart", "system", "restart_pc", "", "restart", "", 1),
        ("s_sys_8", "wheel_main", "cat_sys", 7, "Display Settings", "system", "ms-settings:display", "", "display", "", 0),
    ]
    for s in sys_shortcuts:
        cursor.execute("INSERT INTO shortcuts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", s)

    # Shortcuts for cat_media (6/8 segments)
    media_shortcuts = [
        ("s_med_1", "wheel_main", "cat_media", 0, "Play / Pause", "media", "play_pause", "", "play", "Media", 0),
        ("s_med_2", "wheel_main", "cat_media", 1, "Next Track", "media", "next_track", "", "next", "Next", 0),
        ("s_med_3", "wheel_main", "cat_media", 2, "Prev Track", "media", "prev_track", "", "prev", "Prev", 0),
        ("s_med_4", "wheel_main", "cat_media", 3, "Spotify", "custom_web", "https://open.spotify.com", "", "spotify", "", 0),
        ("s_med_5", "wheel_main", "cat_media", 4, "YouTube Music", "custom_web", "https://music.youtube.com", "", "music", "", 0),
        ("s_med_6", "wheel_main", "cat_media", 5, "Toggle Mute", "media", "mute_toggle", "", "mute", "", 0),
        ("s_med_7", "wheel_main", "cat_media", 6, "Volume +", "system", "volume_up", "", "vol_up", "", 0),
        ("s_med_8", "wheel_main", "cat_media", 7, "Volume -", "system", "volume_down", "", "vol_down", "", 0),
    ]
    for s in media_shortcuts:
        cursor.execute("INSERT INTO shortcuts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", s)

    # Shortcuts for cat_win (8 segments)
    win_shortcuts = [
        ("s_win_1", "wheel_main", "cat_win", 0, "Minimize Active", "window", "minimize", "", "minimize", "", 0),
        ("s_win_2", "wheel_main", "cat_win", 1, "Maximize / Restore", "window", "maximize", "", "maximize", "", 0),
        ("s_win_3", "wheel_main", "cat_win", 2, "Close Active", "window", "close", "", "close", "Alt+F4", 1),
        ("s_win_4", "wheel_main", "cat_win", 3, "Snap Left", "window", "snap_left", "", "snap_left", "Win+Left", 0),
        ("s_win_5", "wheel_main", "cat_win", 4, "Snap Right", "window", "snap_right", "", "snap_right", "Win+Right", 0),
        ("s_win_6", "wheel_main", "cat_win", 5, "Show Desktop", "window", "desktop", "", "desktop", "Win+D", 0),
        ("s_win_7", "wheel_main", "cat_win", 6, "Always on Top", "window", "toggle_top", "", "pin", "", 0),
        ("s_win_8", "wheel_main", "cat_win", 7, "Switch App", "window", "switch_app", "", "switch", "Alt+Tab", 0),
    ]
    for s in win_shortcuts:
        cursor.execute("INSERT INTO shortcuts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", s)

    # Shortcuts for cat_prod (8 segments)
    prod_shortcuts = [
        ("s_prd_1", "wheel_main", "cat_prod", 0, "Screenshot", "productivity", "screenshot", "", "screenshot", "Win+Shift+S", 0),
        ("s_prd_2", "wheel_main", "cat_prod", 1, "Snipping Tool", "app", "snippingtool.exe", "", "snip", "", 0),
        ("s_prd_3", "wheel_main", "cat_prod", 2, "Clipboard History", "productivity", "clipboard_history", "", "clipboard", "Win+V", 0),
        ("s_prd_4", "wheel_main", "cat_prod", 3, "Download Photo", "productivity", "download_photo", "", "photo", "Any Format", 0),
        ("s_prd_5", "wheel_main", "cat_prod", 4, "Copy", "productivity", "copy", "", "copy", "Ctrl+C", 0),
        ("s_prd_6", "wheel_main", "cat_prod", 5, "Paste", "productivity", "paste", "", "paste", "Ctrl+V", 0),
        ("s_prd_7", "wheel_main", "cat_prod", 6, "Undo", "productivity", "undo", "", "undo", "Ctrl+Z", 0),
        ("s_prd_8", "wheel_main", "cat_prod", 7, "Redo", "productivity", "redo", "", "redo", "Ctrl+Y", 0),
    ]
    for s in prod_shortcuts:
        cursor.execute("INSERT INTO shortcuts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", s)

    # 2. Gaming Wheel (6 segments)
    cursor.execute("""
        INSERT INTO wheels (id, name, hotkey, segments_count, is_default, order_index)
        VALUES ('wheel_gaming', 'Gaming Wheel', 'Ctrl+G', 6, 0, 1)
    """)
    cursor.execute("INSERT INTO categories VALUES ('cat_game_main', 'wheel_gaming', 'Gaming Suite', 'game', 0)")
    game_shortcuts = [
        ("s_gm_1", "wheel_gaming", "cat_game_main", 0, "Steam", "app", "steam://open/main", "", "game", "", 0),
        ("s_gm_2", "wheel_gaming", "cat_game_main", 1, "Discord", "app", "discord.exe", "", "web", "", 0),
        ("s_gm_3", "wheel_gaming", "cat_game_main", 2, "Mute Mic / Audio", "system", "mute_toggle", "", "mute", "", 0),
        ("s_gm_4", "wheel_gaming", "cat_game_main", 3, "Instant Screenshot", "productivity", "screenshot", "", "screenshot", "", 0),
        ("s_gm_5", "wheel_gaming", "cat_game_main", 4, "Task Manager", "app", "taskmgr.exe", "", "task", "", 0),
        ("s_gm_6", "wheel_gaming", "cat_game_main", 5, "Volume Boost", "system", "volume_up", "", "vol_up", "", 0),
    ]
    for s in game_shortcuts:
        cursor.execute("INSERT INTO shortcuts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", s)

    # 3. Productivity Wheel (8 segments)
    cursor.execute("""
        INSERT INTO wheels (id, name, hotkey, segments_count, is_default, order_index)
        VALUES ('wheel_prod', 'Productivity Wheel', 'Alt+Z', 8, 0, 2)
    """)
    cursor.execute("INSERT INTO categories VALUES ('cat_prod_main', 'wheel_prod', 'Productivity Center', 'clipboard', 0)")
    for i, s in enumerate(prod_shortcuts):
        cursor.execute("INSERT INTO shortcuts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (f"s_pw_{i}", "wheel_prod", "cat_prod_main", s[3], s[4], s[5], s[6], s[7], s[8], s[9], s[10]))

    # 4. Media Wheel (6 segments)
    cursor.execute("""
        INSERT INTO wheels (id, name, hotkey, segments_count, is_default, order_index)
        VALUES ('wheel_media', 'Media Wheel', 'Alt+M', 6, 0, 3)
    """)
    cursor.execute("INSERT INTO categories VALUES ('cat_media_main', 'wheel_media', 'Media Center', 'music', 0)")
    for i in range(6):
        s = media_shortcuts[i]
        cursor.execute("INSERT INTO shortcuts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (f"s_mw_{i}", "wheel_media", "cat_media_main", i, s[4], s[5], s[6], s[7], s[8], s[9], s[10]))

    # 5. Developer Wheel (8 segments)
    cursor.execute("""
        INSERT INTO wheels (id, name, hotkey, segments_count, is_default, order_index)
        VALUES ('wheel_dev', 'Developer Wheel', 'Alt+D', 8, 0, 4)
    """)
    cursor.execute("INSERT INTO categories VALUES ('cat_dev_main', 'wheel_dev', 'Developer Tools', 'code', 0)")
    dev_shortcuts = [
        ("s_dev_1", "wheel_dev", "cat_dev_main", 0, "VS Code", "app", "code", "", "code", "", 0),
        ("s_dev_2", "wheel_dev", "cat_dev_main", 1, "Windows Terminal", "app", "wt.exe", "", "terminal", "", 0),
        ("s_dev_3", "wheel_dev", "cat_dev_main", 2, "Git Bash / PowerShell", "custom_cmd", "powershell.exe", "", "terminal", "", 0),
        ("s_dev_4", "wheel_dev", "cat_dev_main", 3, "GitHub", "custom_web", "https://github.com", "", "web", "", 0),
        ("s_dev_5", "wheel_dev", "cat_dev_main", 4, "Run Python REPL", "custom_cmd", "python", "", "python", "", 0),
        ("s_dev_6", "wheel_dev", "cat_dev_main", 5, "Localhost 3000", "custom_web", "http://localhost:3000", "", "web", "", 0),
        ("s_dev_7", "wheel_dev", "cat_dev_main", 6, "Task Manager", "app", "taskmgr.exe", "", "task", "", 0),
        ("s_dev_8", "wheel_dev", "cat_dev_main", 7, "DevRelay / Docs", "custom_web", "https://dev.to", "", "web", "", 0),
    ]
    for s in dev_shortcuts:
        cursor.execute("INSERT INTO shortcuts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", s)
