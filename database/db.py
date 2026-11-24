"""
Database Operations and Manager for Nexus Wheel.
"""

import sqlite3
import json
import os
from typing import Dict, Any, List, Optional
from database.schema import get_connection, init_database, DEFAULT_SETTINGS

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            init_database()
        return cls._instance

    # Settings
    def get_setting(self, key: str, default: Any = None) -> Any:
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row["value"])
        except Exception as e:
            print(f"Error reading setting {key}: {e}")
        return default if default is not None else DEFAULT_SETTINGS.get(key)

    def set_setting(self, key: str, value: Any):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                val_json = json.dumps(value)
                cursor.execute("""
                    INSERT INTO settings (key, value) VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """, (key, val_json))
                conn.commit()
        except Exception as e:
            print(f"Error saving setting {key}: {e}")

    def get_all_settings(self) -> Dict[str, Any]:
        result = dict(DEFAULT_SETTINGS)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings")
                for row in cursor.fetchall():
                    try:
                        result[row["key"]] = json.loads(row["value"])
                    except Exception:
                        result[row["key"]] = row["value"]
        except Exception as e:
            print(f"Error fetching all settings: {e}")
        return result

    def reset_settings_to_default(self):
        for k, v in DEFAULT_SETTINGS.items():
            self.set_setting(k, v)

    # Wheels
    def get_wheels(self) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM wheels ORDER BY order_index ASC")
            return [dict(r) for r in cursor.fetchall()]

    def get_wheel(self, wheel_id: str) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM wheels WHERE id = ?", (wheel_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_default_wheel(self) -> Dict[str, Any]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM wheels WHERE is_default = 1")
            row = cursor.fetchone()
            if not row:
                cursor.execute("SELECT * FROM wheels ORDER BY order_index ASC LIMIT 1")
                row = cursor.fetchone()
            return dict(row)

    def save_wheel(self, wheel_data: Dict[str, Any]):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO wheels (id, name, hotkey, segments_count, is_default, order_index)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    hotkey = excluded.hotkey,
                    segments_count = excluded.segments_count,
                    is_default = excluded.is_default,
                    order_index = excluded.order_index
            """, (
                wheel_data["id"],
                wheel_data["name"],
                wheel_data["hotkey"],
                wheel_data.get("segments_count", 8),
                wheel_data.get("is_default", 0),
                wheel_data.get("order_index", 0)
            ))
            conn.commit()

    def delete_wheel(self, wheel_id: str):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shortcuts WHERE wheel_id = ?", (wheel_id,))
            cursor.execute("DELETE FROM categories WHERE wheel_id = ?", (wheel_id,))
            cursor.execute("DELETE FROM wheels WHERE id = ?", (wheel_id,))
            conn.commit()

    # Categories
    def get_categories(self, wheel_id: str) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE wheel_id = ? ORDER BY order_index ASC", (wheel_id,))
            return [dict(r) for r in cursor.fetchall()]

    def save_category(self, cat_data: Dict[str, Any]):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO categories (id, wheel_id, name, icon, order_index)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    icon = excluded.icon,
                    order_index = excluded.order_index
            """, (
                cat_data["id"],
                cat_data["wheel_id"],
                cat_data["name"],
                cat_data.get("icon", "apps"),
                cat_data.get("order_index", 0)
            ))
            conn.commit()

    def delete_category(self, category_id: str):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shortcuts WHERE category_id = ?", (category_id,))
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()

    # Shortcuts
    def get_shortcuts(self, wheel_id: str, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cursor = conn.cursor()
            if category_id:
                cursor.execute("""
                    SELECT * FROM shortcuts 
                    WHERE wheel_id = ? AND category_id = ? 
                    ORDER BY segment_index ASC
                """, (wheel_id, category_id))
            else:
                cursor.execute("""
                    SELECT * FROM shortcuts 
                    WHERE wheel_id = ? 
                    ORDER BY category_id, segment_index ASC
                """, (wheel_id,))
            return [dict(r) for r in cursor.fetchall()]

    def save_shortcut(self, sc_data: Dict[str, Any]):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO shortcuts (
                    id, wheel_id, category_id, segment_index, label, 
                    action_type, target, arguments, icon, hotkey_hint, is_destructive
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    segment_index = excluded.segment_index,
                    label = excluded.label,
                    action_type = excluded.action_type,
                    target = excluded.target,
                    arguments = excluded.arguments,
                    icon = excluded.icon,
                    hotkey_hint = excluded.hotkey_hint,
                    is_destructive = excluded.is_destructive
            """, (
                sc_data["id"],
                sc_data["wheel_id"],
                sc_data["category_id"],
                sc_data.get("segment_index", 0),
                sc_data["label"],
                sc_data["action_type"],
                sc_data["target"],
                sc_data.get("arguments", ""),
                sc_data.get("icon", "app"),
                sc_data.get("hotkey_hint", ""),
                sc_data.get("is_destructive", 0)
            ))
            conn.commit()

    def delete_shortcut(self, shortcut_id: str):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shortcuts WHERE id = ?", (shortcut_id,))
            conn.commit()

    def reorder_shortcuts(self, ordered_shortcut_ids: List[str]):
        with get_connection() as conn:
            cursor = conn.cursor()
            for idx, sid in enumerate(ordered_shortcut_ids):
                cursor.execute("UPDATE shortcuts SET segment_index = ? WHERE id = ?", (idx, sid))
            conn.commit()

    # Games
    def get_games(self) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM games_list ORDER BY display_name ASC")
            return [dict(r) for r in cursor.fetchall()]

    def add_game(self, process_name: str, display_name: str, blocked: bool = True):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO games_list (process_name, display_name, blocked)
                VALUES (?, ?, ?)
            """, (process_name.strip().lower(), display_name.strip(), 1 if blocked else 0))
            conn.commit()

    def delete_game(self, game_id: int):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM games_list WHERE id = ?", (game_id,))
            conn.commit()

    def toggle_game_blocked(self, game_id: int, blocked: bool):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE games_list SET blocked = ? WHERE id = ?", (1 if blocked else 0, game_id))
            conn.commit()

    # Backup & Restore
    def export_backup_json(self) -> str:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings")
            settings = {r["key"]: json.loads(r["value"]) for r in cursor.fetchall()}
            cursor.execute("SELECT * FROM wheels")
            wheels = [dict(r) for r in cursor.fetchall()]
            cursor.execute("SELECT * FROM categories")
            categories = [dict(r) for r in cursor.fetchall()]
            cursor.execute("SELECT * FROM shortcuts")
            shortcuts = [dict(r) for r in cursor.fetchall()]
            cursor.execute("SELECT * FROM games_list")
            games = [dict(r) for r in cursor.fetchall()]

            data = {
                "version": "1.0.0",
                "settings": settings,
                "wheels": wheels,
                "categories": categories,
                "shortcuts": shortcuts,
                "games": games
            }
            return json.dumps(data, indent=2)

    def import_backup_json(self, json_str: str) -> bool:
        try:
            data = json.loads(json_str)
            with get_connection() as conn:
                cursor = conn.cursor()
                # Clear existing
                cursor.execute("DELETE FROM shortcuts")
                cursor.execute("DELETE FROM categories")
                cursor.execute("DELETE FROM wheels")
                cursor.execute("DELETE FROM games_list")
                
                # Restore settings
                for k, v in data.get("settings", {}).items():
                    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, json.dumps(v)))

                # Restore wheels
                for w in data.get("wheels", []):
                    cursor.execute("INSERT INTO wheels VALUES (?, ?, ?, ?, ?, ?)", (
                        w["id"], w["name"], w["hotkey"], w["segments_count"], w["is_default"], w["order_index"]
                    ))

                # Restore categories
                for c in data.get("categories", []):
                    cursor.execute("INSERT INTO categories VALUES (?, ?, ?, ?, ?)", (
                        c["id"], c["wheel_id"], c["name"], c["icon"], c["order_index"]
                    ))

                # Restore shortcuts
                for s in data.get("shortcuts", []):
                    cursor.execute("INSERT INTO shortcuts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                        s["id"], s["wheel_id"], s["category_id"], s["segment_index"],
                        s["label"], s["action_type"], s["target"], s.get("arguments", ""),
                        s["icon"], s.get("hotkey_hint", ""), s.get("is_destructive", 0)
                    ))

                # Restore games
                for g in data.get("games", []):
                    cursor.execute("INSERT OR REPLACE INTO games_list (process_name, display_name, blocked) VALUES (?, ?, ?)", (
                        g["process_name"], g["display_name"], g.get("blocked", 1)
                    ))

                conn.commit()
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
