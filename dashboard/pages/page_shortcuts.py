"""
Visual Shortcut Manager Page for Nexus Wheel Dashboard.
Add, Edit, Delete, and Reorder shortcuts across categories and radial wheels.
"""

import uuid
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QLineEdit, QFileDialog, QCheckBox, QMessageBox
)
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt, Signal
from database.db import DatabaseManager
from utils.icon_provider import IconProvider

class ShortcutEditDialog(QDialog):
    def __init__(self, shortcut_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Radial Shortcut")
        self.setFixedSize(520, 560)
        self.setStyleSheet("""
            QDialog { background-color: #0E121A; color: #FFFFFF; }
            QLabel { color: #E6EDF3; font-weight: 600; font-size: 12px; }
            QLineEdit, QComboBox { background-color: #161B22; border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 6px; color: #FFFFFF; padding: 7px; }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #00F0FF; }
        """)
        self.shortcut = dict(shortcut_data)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"Configure Slot {self.shortcut.get('segment_index', 0) + 1}")
        title.setStyleSheet("font-size: 16px; font-weight: 800; color: #00F0FF;")
        layout.addWidget(title)

        # 1. Label
        layout.addWidget(QLabel("Shortcut Label:"))
        self.edit_label = QLineEdit(self.shortcut.get("label", ""))
        layout.addWidget(self.edit_label)

        # 2. Action Type
        layout.addWidget(QLabel("Action Type:"))
        self.combo_type = QComboBox()
        self.combo_type.addItem("Application / Program", "app")
        self.combo_type.addItem("System Control", "system")
        self.combo_type.addItem("Media Control", "media")
        self.combo_type.addItem("Window Management", "window")
        self.combo_type.addItem("Productivity Tool", "productivity")
        self.combo_type.addItem("Custom Executable (.EXE)", "custom_exe")
        self.combo_type.addItem("Custom Web URL", "custom_web")
        self.combo_type.addItem("Command / Terminal Script", "custom_cmd")
        self.combo_type.addItem("Python Script (.py)", "custom_py")
        self.combo_type.addItem("Keyboard Shortcut Combo", "custom_hotkey")
        self.combo_type.addItem("Custom File / Folder", "custom_file")

        cur_type = self.shortcut.get("action_type", "app")
        idx = self.combo_type.findData(cur_type)
        if idx >= 0:
            self.combo_type.setCurrentIndex(idx)
        self.combo_type.currentIndexChanged.connect(self._on_type_changed)
        layout.addWidget(self.combo_type)

        # 3. Target
        layout.addWidget(QLabel("Target / Command / Action Name:"))
        row_target = QHBoxLayout()
        self.edit_target = QLineEdit(self.shortcut.get("target", ""))
        self.edit_target.setPlaceholderText("e.g. download_photo, screenshot, copy, paste, chrome.exe")
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.setStyleSheet("background: #21262D; color: #FFFFFF; padding: 6px 12px; border-radius: 6px;")
        self.btn_browse.clicked.connect(self._browse_target)
        row_target.addWidget(self.edit_target, 1)
        row_target.addWidget(self.btn_browse)
        layout.addLayout(row_target)

        # 4. Arguments (optional)
        layout.addWidget(QLabel("Command Line Arguments (Optional):"))
        self.edit_args = QLineEdit(self.shortcut.get("arguments", ""))
        layout.addWidget(self.edit_args)

        # 5. Icon Name
        layout.addWidget(QLabel("Vector Icon:"))
        self.combo_icon = QComboBox()
        icon_options = [
            ("chrome", "Chrome Browser"), ("edge", "Edge Browser"), ("code", "VS Code / IDE"),
            ("explorer", "File Explorer"), ("settings", "Settings Gear"), ("task", "Task Manager"),
            ("terminal", "Terminal / CMD"), ("calc", "Calculator"), ("note", "Notepad"),
            ("vol_up", "Volume Up"), ("vol_down", "Volume Down"), ("mute", "Mute Audio"),
            ("bright", "Brightness"), ("wifi", "Wi-Fi"), ("bluetooth", "Bluetooth"),
            ("display", "Display"), ("lock", "Lock Screen"), ("sleep", "Sleep"),
            ("shutdown", "Shutdown Power"), ("restart", "Restart"), ("play", "Media Play/Pause"),
            ("next", "Next Track"), ("prev", "Prev Track"), ("spotify", "Spotify"),
            ("music", "YouTube Music"), ("minimize", "Minimize Window"), ("maximize", "Maximize Window"),
            ("close", "Close Window"), ("snap_left", "Snap Left"), ("snap_right", "Snap Right"),
            ("desktop", "Show Desktop"), ("pin", "Always on Top"), ("switch", "Switch App"),
            ("copy", "Copy"), ("paste", "Paste"), ("cut", "Cut"), ("undo", "Undo"),
            ("redo", "Redo"), ("screenshot", "Screenshot"), ("snip", "Snipping Tool"),
            ("clipboard", "Clipboard History"), ("download", "Downloads Folder"),
            ("photo", "Photo / Camera Grabber"),
            ("python", "Python Script"), ("game", "Gamepad / Steam"), ("web", "Web / Globe")
        ]
        for ic_key, ic_name in icon_options:
            self.combo_icon.addItem(IconProvider.get_icon(ic_key, "#00F0FF", 24), ic_name, ic_key)

        cur_icon = self.shortcut.get("icon", "app")
        idx_ic = self.combo_icon.findData(cur_icon)
        if idx_ic >= 0:
            self.combo_icon.setCurrentIndex(idx_ic)
        layout.addWidget(self.combo_icon)

        # 6. Hotkey Hint
        layout.addWidget(QLabel("Display Hotkey Hint (e.g. Win+E, Alt+F4):"))
        self.edit_hint = QLineEdit(self.shortcut.get("hotkey_hint", ""))
        layout.addWidget(self.edit_hint)

        # 7. Destructive Confirmation Checkbox
        self.cb_destructive = QCheckBox("Require Confirmation Prompt (Destructive Action)")
        self.cb_destructive.setChecked(bool(self.shortcut.get("is_destructive", 0)))
        layout.addWidget(self.cb_destructive)

        layout.addStretch()

        # Dialog Buttons
        row_btn = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("background: #21262D; color: #FFFFFF; padding: 8px 16px; border-radius: 6px;")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Save Shortcut")
        btn_save.setStyleSheet("background: #00F0FF; color: #000000; font-weight: 700; padding: 8px 20px; border-radius: 6px;")
        btn_save.clicked.connect(self._save_and_accept)

        row_btn.addStretch()
        row_btn.addWidget(btn_cancel)
        row_btn.addWidget(btn_save)
        layout.addLayout(row_btn)

    def _on_type_changed(self):
        t = self.combo_type.currentData()
        self.btn_browse.setEnabled(t in ("app", "custom_exe", "custom_py", "custom_file"))

    def _browse_target(self):
        t = self.combo_type.currentData()
        if t == "custom_py":
            path, _ = QFileDialog.getOpenFileName(self, "Select Python Script", "", "Python Files (*.py)")
        elif t in ("app", "custom_exe"):
            path, _ = QFileDialog.getOpenFileName(self, "Select Executable", "", "Executables (*.exe *.bat *.cmd);;All Files (*.*)")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Select Target File", "", "All Files (*.*)")
        if path:
            self.edit_target.setText(path)
            if not self.edit_label.text():
                import os
                base = os.path.splitext(os.path.basename(path))[0]
                self.edit_label.setText(base.replace("-", " ").replace("_", " ").title())

    def _save_and_accept(self):
        self.shortcut["label"] = self.edit_label.text().strip() or "Unnamed"
        self.shortcut["action_type"] = self.combo_type.currentData()
        self.shortcut["target"] = self.edit_target.text().strip()
        self.shortcut["arguments"] = self.edit_args.text().strip()
        self.shortcut["icon"] = self.combo_icon.currentData()
        self.shortcut["hotkey_hint"] = self.edit_hint.text().strip()
        self.shortcut["is_destructive"] = 1 if self.cb_destructive.isChecked() else 0
        self.accept()


class ShortcutManagerPage(QWidget):
    shortcuts_updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self.current_wheel_id = "wheel_main"
        self.current_cat_id = "cat_apps"
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Shortcut Manager")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title)

        desc = QLabel("Assign, customize, and reorder shortcuts across categories and radial segments.")
        desc.setStyleSheet("color: #8B949E; margin-bottom: 4px;")
        layout.addWidget(desc)

        # Filter bar: Wheel & Category
        c_filter = QFrame()
        c_filter.setObjectName("card")
        l_filter = QHBoxLayout(c_filter)
        l_filter.setContentsMargins(12, 10, 12, 10)

        lbl_w = QLabel("Wheel:")
        lbl_w.setStyleSheet("font-weight: 700; color: #00F0FF;")
        self.combo_wheel = QComboBox()
        self._populate_wheels()
        self.combo_wheel.currentIndexChanged.connect(self._on_wheel_changed)

        lbl_cat = QLabel("Category:")
        lbl_cat.setStyleSheet("font-weight: 700; color: #00F0FF; margin-left: 12px;")
        self.combo_cat = QComboBox()
        self._populate_categories()
        self.combo_cat.currentIndexChanged.connect(self._on_cat_changed)

        btn_add_cat = QPushButton("+ Category")
        btn_add_cat.setObjectName("secondary_btn")
        btn_add_cat.clicked.connect(self._add_category)

        btn_del_cat = QPushButton("Delete Category")
        btn_del_cat.setObjectName("danger_btn")
        btn_del_cat.clicked.connect(self._delete_category)

        l_filter.addWidget(lbl_w)
        l_filter.addWidget(self.combo_wheel, 1)
        l_filter.addWidget(lbl_cat)
        l_filter.addWidget(self.combo_cat, 1)
        l_filter.addWidget(btn_add_cat)
        l_filter.addWidget(btn_del_cat)
        layout.addWidget(c_filter)

        # Shortcuts Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Slot", "Icon", "Label", "Action Type", "Target", "Hotkey"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._edit_selected_shortcut)
        layout.addWidget(self.table)

        # Action bar buttons
        row_actions = QHBoxLayout()
        btn_edit = QPushButton("Edit Shortcut")
        btn_edit.setObjectName("primary_btn")
        btn_edit.clicked.connect(self._edit_selected_shortcut)

        btn_up = QPushButton("▲ Move Up")
        btn_up.setObjectName("secondary_btn")
        btn_up.clicked.connect(self._move_shortcut_up)

        btn_down = QPushButton("▼ Move Down")
        btn_down.setObjectName("secondary_btn")
        btn_down.clicked.connect(self._move_shortcut_down)

        btn_clear = QPushButton("Clear Slot")
        btn_clear.setObjectName("danger_btn")
        btn_clear.clicked.connect(self._clear_selected_shortcut)

        row_actions.addWidget(btn_edit)
        row_actions.addWidget(btn_up)
        row_actions.addWidget(btn_down)
        row_actions.addWidget(btn_clear)
        row_actions.addStretch()
        layout.addLayout(row_actions)

        self._refresh_shortcuts_table()

    def _populate_wheels(self):
        self.combo_wheel.blockSignals(True)
        self.combo_wheel.clear()
        wheels = self._db.get_wheels()
        for idx, w in enumerate(wheels):
            self.combo_wheel.addItem(w["name"], w["id"])
            if w["id"] == self.current_wheel_id:
                self.combo_wheel.setCurrentIndex(idx)
        self.combo_wheel.blockSignals(False)

    def _populate_categories(self):
        self.combo_cat.blockSignals(True)
        self.combo_cat.clear()
        cats = self._db.get_categories(self.current_wheel_id)
        cur_idx = 0
        for idx, c in enumerate(cats):
            self.combo_cat.addItem(c["name"], c["id"])
            if c["id"] == self.current_cat_id:
                cur_idx = idx
        if cats:
            self.combo_cat.setCurrentIndex(cur_idx)
            self.current_cat_id = cats[cur_idx]["id"]
        else:
            self.current_cat_id = ""
        self.combo_cat.blockSignals(False)

    def _on_wheel_changed(self):
        wid = self.combo_wheel.currentData()
        if wid:
            self.current_wheel_id = wid
            self._populate_categories()
            self._refresh_shortcuts_table()

    def _on_cat_changed(self):
        cid = self.combo_cat.currentData()
        if cid:
            self.current_cat_id = cid
            self._refresh_shortcuts_table()

    def _refresh_shortcuts_table(self):
        self.table.setRowCount(0)
        if not self.current_cat_id:
            return

        w = self._db.get_wheel(self.current_wheel_id)
        seg_count = int(w.get("segments_count", 8)) if w else 8
        shortcuts = self._db.get_shortcuts(self.current_wheel_id, self.current_cat_id)
        sc_map = {s["segment_index"]: s for s in shortcuts}

        self.table.setRowCount(seg_count)
        for i in range(seg_count):
            sc = sc_map.get(i)
            # Slot item
            item_slot = QTableWidgetItem(f"Slot {i + 1}")
            item_slot.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, item_slot)

            if sc and sc.get("action_type") != "none":
                # Icon item
                icon = IconProvider.get_icon(sc.get("icon", "app"), "#00F0FF", 24)
                item_icon = QTableWidgetItem(icon, "")
                item_icon.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 1, item_icon)

                # Label
                label_text = sc.get("label", "")
                if sc.get("is_destructive", 0):
                    label_text += " ⚠️"
                item_label = QTableWidgetItem(label_text)
                self.table.setItem(i, 2, item_label)

                # Action Type
                item_type = QTableWidgetItem(sc.get("action_type", "").upper())
                self.table.setItem(i, 3, item_type)

                # Target
                item_target = QTableWidgetItem(sc.get("target", ""))
                self.table.setItem(i, 4, item_target)

                # Hotkey
                item_hk = QTableWidgetItem(sc.get("hotkey_hint", ""))
                item_hk.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 5, item_hk)
            else:
                # Empty slot
                empty_item = QTableWidgetItem("[ Empty Slot ]")
                empty_item.setForeground(QColor(100, 110, 125))
                self.table.setItem(i, 2, empty_item)
                for col in [1, 3, 4, 5]:
                    self.table.setItem(i, col, QTableWidgetItem(""))

        self.table.resizeRowsToContents()

    def _get_selected_row_data(self) -> Optional[Dict[str, Any]]:
        row = self.table.currentRow()
        if row < 0:
            return None
        shortcuts = self._db.get_shortcuts(self.current_wheel_id, self.current_cat_id)
        for s in shortcuts:
            if s["segment_index"] == row:
                return s
        # Create empty placeholder data for this slot
        return {
            "id": f"sc_{uuid.uuid4().hex[:8]}",
            "wheel_id": self.current_wheel_id,
            "category_id": self.current_cat_id,
            "segment_index": row,
            "label": f"Action {row + 1}",
            "action_type": "app",
            "target": "",
            "arguments": "",
            "icon": "app",
            "hotkey_hint": "",
            "is_destructive": 0
        }

    def _edit_selected_shortcut(self):
        sc_data = self._get_selected_row_data()
        if not sc_data:
            QMessageBox.information(self, "Select Slot", "Please select a segment slot to edit.")
            return

        dlg = ShortcutEditDialog(sc_data, self)
        if dlg.exec():
            self._db.save_shortcut(dlg.shortcut)
            self._refresh_shortcuts_table()
            self.shortcuts_updated.emit()

    def _clear_selected_shortcut(self):
        row = self.table.currentRow()
        if row < 0:
            return
        shortcuts = self._db.get_shortcuts(self.current_wheel_id, self.current_cat_id)
        for s in shortcuts:
            if s["segment_index"] == row:
                self._db.delete_shortcut(s["id"])
                break
        self._refresh_shortcuts_table()
        self.shortcuts_updated.emit()

    def _move_shortcut_up(self):
        row = self.table.currentRow()
        if row <= 0:
            return
        self._swap_slots(row, row - 1)
        self.table.selectRow(row - 1)

    def _move_shortcut_down(self):
        row = self.table.currentRow()
        if row < 0 or row >= self.table.rowCount() - 1:
            return
        self._swap_slots(row, row + 1)
        self.table.selectRow(row + 1)

    def _swap_slots(self, idx1: int, idx2: int):
        shortcuts = self._db.get_shortcuts(self.current_wheel_id, self.current_cat_id)
        sc1 = next((s for s in shortcuts if s["segment_index"] == idx1), None)
        sc2 = next((s for s in shortcuts if s["segment_index"] == idx2), None)

        if sc1:
            sc1["segment_index"] = idx2
            self._db.save_shortcut(sc1)
        if sc2:
            sc2["segment_index"] = idx1
            self._db.save_shortcut(sc2)

        self._refresh_shortcuts_table()
        self.shortcuts_updated.emit()

    def _add_category(self):
        cat_id = f"cat_{uuid.uuid4().hex[:6]}"
        cats = self._db.get_categories(self.current_wheel_id)
        new_cat = {
            "id": cat_id,
            "wheel_id": self.current_wheel_id,
            "name": f"New Category {len(cats) + 1}",
            "icon": "apps",
            "order_index": len(cats)
        }
        self._db.save_category(new_cat)
        self.current_cat_id = cat_id
        self._populate_categories()
        self._refresh_shortcuts_table()
        self.shortcuts_updated.emit()

    def _delete_category(self):
        cats = self._db.get_categories(self.current_wheel_id)
        if len(cats) <= 1:
            QMessageBox.warning(self, "Warning", "You must keep at least one category.")
            return
        reply = QMessageBox.question(
            self,
            "Confirm Delete Category",
            f"Are you sure you want to delete the category '{self.combo_cat.currentText()}' and all its shortcuts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._db.delete_category(self.current_cat_id)
            self._populate_categories()
            self._refresh_shortcuts_table()
            self.shortcuts_updated.emit()
