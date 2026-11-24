"""
Wheel Customization Page for Nexus Wheel Dashboard.
Supports configuring segment counts (4, 6, 8, 10, 12), hotkeys, position mode, and deadzone.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QComboBox, QSlider, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from database.db import DatabaseManager

class WheelCustomizationPage(QWidget):
    wheel_updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self.current_wheel_id = "wheel_main"
        self._init_ui()

    def _init_ui(self):
        # Clear layout if rebuilding
        while self.layout() and self.layout().count():
            item = self.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        layout = self.layout() or QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Wheel Customization")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title)

        desc = QLabel("Configure segment counts (4 to 12), activation hotkeys, positioning, and deadzone radius.")
        desc.setStyleSheet("color: #8B949E; margin-bottom: 8px;")
        layout.addWidget(desc)

        # 1. Wheel Selector & Management
        c1 = QFrame()
        c1.setObjectName("card")
        l1 = QVBoxLayout(c1)
        l1.setSpacing(12)

        h1 = QLabel("Select Radial Wheel Profile")
        h1.setObjectName("card_header")
        l1.addWidget(h1)

        row_sel = QHBoxLayout()
        lbl_w = QLabel("Active Wheel:")
        lbl_w.setStyleSheet("font-weight: 600;")
        self.combo_wheel = QComboBox()
        self._populate_wheel_selector()
        self.combo_wheel.currentIndexChanged.connect(self._on_wheel_selected)
        
        btn_new_wheel = QPushButton("+ Create New Wheel")
        btn_new_wheel.setObjectName("secondary_btn")
        btn_new_wheel.clicked.connect(self._create_new_wheel)

        btn_del_wheel = QPushButton("Delete Wheel")
        btn_del_wheel.setObjectName("danger_btn")
        btn_del_wheel.clicked.connect(self._delete_current_wheel)

        row_sel.addWidget(lbl_w)
        row_sel.addWidget(self.combo_wheel, 1)
        row_sel.addWidget(btn_new_wheel)
        row_sel.addWidget(btn_del_wheel)
        l1.addLayout(row_sel)

        layout.addWidget(c1)

        # 2. Wheel Properties Card
        c2 = QFrame()
        c2.setObjectName("card")
        l2 = QVBoxLayout(c2)
        l2.setSpacing(14)

        h2 = QLabel("Wheel Configuration")
        h2.setObjectName("card_header")
        l2.addWidget(h2)

        # Wheel Name
        row_name = QHBoxLayout()
        lbl_name = QLabel("Wheel Name:")
        lbl_name.setFixedWidth(130)
        self.edit_name = QLineEdit()
        row_name.addWidget(lbl_name)
        row_name.addWidget(self.edit_name)
        l2.addLayout(row_name)

        # Activation Hotkey
        row_hk = QHBoxLayout()
        lbl_hk = QLabel("Activation Hotkey:")
        lbl_hk.setFixedWidth(130)
        self.edit_hotkey = QLineEdit()
        self.edit_hotkey.setPlaceholderText("e.g. Alt+X, Ctrl+G, Alt+Z")
        row_hk.addWidget(lbl_hk)
        row_hk.addWidget(self.edit_hotkey)
        l2.addLayout(row_hk)

        # Segments Count (4, 6, 8, 10, 12)
        row_seg = QHBoxLayout()
        lbl_seg = QLabel("Segments Count:")
        lbl_seg.setFixedWidth(130)
        self.combo_segments = QComboBox()
        for count in [4, 6, 8, 10, 12]:
            self.combo_segments.addItem(f"{count} Segments", count)
        row_seg.addWidget(lbl_seg)
        row_seg.addWidget(self.combo_segments)
        row_seg.addStretch()
        l2.addLayout(row_seg)

        # Position Mode
        row_pos = QHBoxLayout()
        lbl_pos = QLabel("Positioning:")
        lbl_pos.setFixedWidth(130)
        self.combo_pos = QComboBox()
        self.combo_pos.addItem("Mouse Cursor", "cursor")
        self.combo_pos.addItem("Screen Center", "center")
        cur_pos_mode = self._db.get_setting("position_mode", "cursor")
        idx_pos = 0 if cur_pos_mode == "cursor" else 1
        self.combo_pos.setCurrentIndex(idx_pos)
        self.combo_pos.currentIndexChanged.connect(lambda: self._db.set_setting("position_mode", self.combo_pos.currentData()))
        row_pos.addWidget(lbl_pos)
        row_pos.addWidget(self.combo_pos)
        row_pos.addStretch()
        l2.addLayout(row_pos)

        # Deadzone Radius Slider
        row_dz = QVBoxLayout()
        self.lbl_dz_val = QLabel(f"Dead Zone Radius: {self._db.get_setting('deadzone_radius', 45)} px")
        self.lbl_dz_val.setStyleSheet("font-weight: 600; color: #FFFFFF;")
        
        self.slider_dz = QSlider(Qt.Orientation.Horizontal)
        self.slider_dz.setRange(20, 90)
        self.slider_dz.setValue(int(self._db.get_setting("deadzone_radius", 45)))
        self.slider_dz.valueChanged.connect(self._on_deadzone_changed)

        row_dz.addWidget(self.lbl_dz_val)
        row_dz.addWidget(self.slider_dz)
        l2.addLayout(row_dz)

        # Save Button
        btn_save = QPushButton("Save Wheel Settings")
        btn_save.setObjectName("primary_btn")
        btn_save.setFixedWidth(180)
        btn_save.clicked.connect(self._save_wheel_config)
        l2.addWidget(btn_save)

        layout.addWidget(c2)

        # 3. Wheel Sizing & Scale Card (Make Wheel Smaller / Larger)
        c3 = QFrame()
        c3.setObjectName("card")
        l3 = QVBoxLayout(c3)
        l3.setSpacing(14)

        h3 = QLabel("Wheel Size & Scale (Make Wheel Smaller / Larger)")
        h3.setObjectName("card_header")
        l3.addWidget(h3)

        desc_size = QLabel("Make the radial wheel smaller or larger to fit your screen resolution and visual preference.")
        desc_size.setStyleSheet("color: #8B949E; font-size: 11px;")
        l3.addWidget(desc_size)

        # Quick Size Presets
        row_presets = QHBoxLayout()
        row_presets.setSpacing(8)
        lbl_pre = QLabel("Size Presets:")
        lbl_pre.setFixedWidth(110)
        lbl_pre.setStyleSheet("font-weight: 600;")
        row_presets.addWidget(lbl_pre)

        presets = [
            ("Mini (60%)", 60),
            ("Small (75%)", 75),
            ("Medium (85%)", 85),
            ("Default (100%)", 100),
            ("Large (115%)", 115)
        ]
        self.preset_buttons = {}
        for p_label, p_val in presets:
            btn = QPushButton(p_label)
            btn.setObjectName("secondary_btn")
            btn.clicked.connect(lambda checked=False, val=p_val: self._set_scale_value(val))
            row_presets.addWidget(btn)
            self.preset_buttons[p_val] = btn
        row_presets.addStretch()
        l3.addLayout(row_presets)

        # Fine-Tuning Scale Slider
        row_scale = QVBoxLayout()
        row_scale.setSpacing(4)
        cur_scale_pct = int(float(self._db.get_setting("wheel_scale", 1.0)) * 100)
        self.lbl_scale_val = QLabel(self._format_scale_text(cur_scale_pct))
        self.lbl_scale_val.setStyleSheet("font-weight: 600; color: #FFFFFF;")

        self.slider_scale = QSlider(Qt.Orientation.Horizontal)
        self.slider_scale.setRange(50, 125)
        self.slider_scale.setValue(cur_scale_pct)
        self.slider_scale.valueChanged.connect(self._on_scale_slider_changed)

        row_scale.addWidget(self.lbl_scale_val)
        row_scale.addWidget(self.slider_scale)
        l3.addLayout(row_scale)

        # Pro-Tip hint
        tip_lbl = QLabel("💡 Pro Tip: While the radial wheel is open on screen, hold Ctrl + Mouse Wheel up/down to dynamically resize it on the fly!")
        tip_lbl.setStyleSheet("color: #00F0FF; font-size: 11px; font-weight: 600; padding: 4px 0px;")
        l3.addWidget(tip_lbl)

        layout.addWidget(c3)
        layout.addStretch()

        # 4. Wheel Wallpaper / Background Texture Card
        c4 = QFrame()
        c4.setObjectName("card")
        l4 = QVBoxLayout(c4)
        l4.setSpacing(12)

        h4 = QLabel("Wheel Wallpaper / Background")
        h4.setObjectName("card_header")
        l4.addWidget(h4)

        desc_wp = QLabel("Set a custom image as the wheel's background texture. Supports PNG, JPG, WEBP, BMP.")
        desc_wp.setStyleSheet("color: #8B949E; font-size: 11px;")
        l4.addWidget(desc_wp)

        # Path row
        row_wp = QHBoxLayout()
        self.edit_wallpaper = QLineEdit()
        self.edit_wallpaper.setPlaceholderText("No wallpaper set — click Browse to choose an image...")
        cur_wp = self._db.get_setting("wheel_wallpaper", "")
        self.edit_wallpaper.setText(cur_wp)

        btn_browse_wp = QPushButton("Browse Image")
        btn_browse_wp.setObjectName("secondary_btn")
        btn_browse_wp.clicked.connect(self._browse_wallpaper)

        btn_clear_wp = QPushButton("Clear Wallpaper")
        btn_clear_wp.setObjectName("danger_btn")
        btn_clear_wp.clicked.connect(self._clear_wallpaper)

        row_wp.addWidget(self.edit_wallpaper, 1)
        row_wp.addWidget(btn_browse_wp)
        row_wp.addWidget(btn_clear_wp)
        l4.addLayout(row_wp)

        btn_save_wp = QPushButton("Save Wallpaper Setting")
        btn_save_wp.setObjectName("primary_btn")
        btn_save_wp.setFixedWidth(200)
        btn_save_wp.clicked.connect(self._save_wallpaper)
        l4.addWidget(btn_save_wp)

        layout.addWidget(c4)
        layout.addStretch()

        self._load_current_wheel_values()

    def _populate_wheel_selector(self):
        self.combo_wheel.blockSignals(True)
        self.combo_wheel.clear()
        wheels = self._db.get_wheels()
        cur_idx = 0
        for i, w in enumerate(wheels):
            self.combo_wheel.addItem(w["name"], w["id"])
            if w["id"] == self.current_wheel_id:
                cur_idx = i
        self.combo_wheel.setCurrentIndex(cur_idx)
        self.combo_wheel.blockSignals(False)

    def _on_wheel_selected(self, index):
        wid = self.combo_wheel.currentData()
        if wid:
            self.current_wheel_id = wid
            self._load_current_wheel_values()

    def _load_current_wheel_values(self):
        w = self._db.get_wheel(self.current_wheel_id)
        if not w:
            return
        self.edit_name.setText(w["name"])
        self.edit_hotkey.setText(w["hotkey"])
        seg_count = int(w.get("segments_count", 8))
        idx = self.combo_segments.findData(seg_count)
        if idx >= 0:
            self.combo_segments.setCurrentIndex(idx)

    def _format_scale_text(self, pct: int) -> str:
        px = int(640 * (pct / 100.0))
        rad = int(270 * (pct / 100.0))
        label_desc = "Standard"
        if pct <= 65:
            label_desc = "Mini (Ultra Compact)"
        elif pct <= 80:
            label_desc = "Small (Compact HUD)"
        elif pct <= 90:
            label_desc = "Medium"
        elif pct >= 110:
            label_desc = "Large"
        return f"Wheel Size: {pct}% – {label_desc} ({px} × {px} px • Radius: {rad} px)"

    def _set_scale_value(self, pct: int):
        self.slider_scale.setValue(pct)

    def _on_scale_slider_changed(self, pct: int):
        self.lbl_scale_val.setText(self._format_scale_text(pct))
        scale_float = round(pct / 100.0, 2)
        self._db.set_setting("wheel_scale", scale_float)
        self.wheel_updated.emit()

    def _on_deadzone_changed(self, val):
        self.lbl_dz_val.setText(f"Dead Zone Radius: {val} px")
        self._db.set_setting("deadzone_radius", val)

    def _save_wheel_config(self):
        w = self._db.get_wheel(self.current_wheel_id)
        if not w:
            return
        w["name"] = self.edit_name.text().strip() or "Unnamed Wheel"
        w["hotkey"] = self.edit_hotkey.text().strip() or "Alt+X"
        w["segments_count"] = self.combo_segments.currentData()
        self._db.save_wheel(w)
        self._populate_wheel_selector()
        self.wheel_updated.emit()
        QMessageBox.information(self, "Success", "Radial Wheel configuration saved successfully.")

    def _create_new_wheel(self):
        import uuid
        new_id = f"wheel_{uuid.uuid4().hex[:6]}"
        new_wheel = {
            "id": new_id,
            "name": f"Custom Wheel {self.combo_wheel.count() + 1}",
            "hotkey": "Alt+W",
            "segments_count": 8,
            "is_default": 0,
            "order_index": self.combo_wheel.count()
        }
        self._db.save_wheel(new_wheel)
        # Add default category
        self._db.save_category({
            "id": f"cat_{new_id}",
            "wheel_id": new_id,
            "name": "General",
            "icon": "apps",
            "order_index": 0
        })
        self.current_wheel_id = new_id
        self._populate_wheel_selector()
        self._load_current_wheel_values()
        self.wheel_updated.emit()

    def _delete_current_wheel(self):
        if self.combo_wheel.count() <= 1:
            QMessageBox.warning(self, "Warning", "You must keep at least one radial wheel.")
            return
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.edit_name.text()}' and all its shortcuts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._db.delete_wheel(self.current_wheel_id)
            wheels = self._db.get_wheels()
            self.current_wheel_id = wheels[0]["id"]
            self._populate_wheel_selector()
            self._load_current_wheel_values()
            self.wheel_updated.emit()

    # ------------------------------------------------------------------ #
    # Wallpaper helpers
    # ------------------------------------------------------------------ #
    def _browse_wallpaper(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Wheel Wallpaper Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.webp *.bmp);;All Files (*)"
        )
        if path:
            self.edit_wallpaper.setText(path)

    def _clear_wallpaper(self):
        self.edit_wallpaper.clear()
        self._db.set_setting("wheel_wallpaper", "")
        self.wheel_updated.emit()

    def _save_wallpaper(self):
        path = self.edit_wallpaper.text().strip()
        self._db.set_setting("wheel_wallpaper", path)
        self.wheel_updated.emit()
        QMessageBox.information(self, "Saved", "Wheel wallpaper setting saved successfully.")
