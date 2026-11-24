"""
Animation Settings Page for Nexus Wheel Dashboard.
Presets (GTA V Classic, Smooth Glass, Cyberpunk, Minimal, Ultra Fast) and custom speeds.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QComboBox, QSlider, QFrame, QPushButton
)
from PySide6.QtCore import Qt, Signal
from database.db import DatabaseManager
from animations.presets import ANIMATION_PRESETS

class AnimationsPage(QWidget):
    animations_changed = Signal()
    test_animation_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Animation Settings")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title)

        desc = QLabel("Customize 60 FPS transitions, opening scales, rotation angles, and neon glow speeds.")
        desc.setStyleSheet("color: #8B949E; margin-bottom: 4px;")
        layout.addWidget(desc)

        # 1. Presets Card
        c1 = QFrame()
        c1.setObjectName("card")
        l1 = QVBoxLayout(c1)
        l1.setSpacing(12)

        h1 = QLabel("Animation Presets")
        h1.setObjectName("card_header")
        l1.addWidget(h1)

        row_preset = QHBoxLayout()
        lbl_p = QLabel("Choose Preset:")
        lbl_p.setStyleSheet("font-weight: 600;")
        self.combo_preset = QComboBox()
        for p_name in ANIMATION_PRESETS.keys():
            self.combo_preset.addItem(p_name)
        
        cur_preset = self._db.get_setting("animation_preset", "GTA V Classic")
        idx = self.combo_preset.findText(cur_preset)
        if idx >= 0:
            self.combo_preset.setCurrentIndex(idx)
        self.combo_preset.currentTextChanged.connect(self._on_preset_selected)

        btn_test = QPushButton("⚡ Test Wheel Animation")
        btn_test.setObjectName("primary_btn")
        btn_test.clicked.connect(lambda: self.test_animation_requested.emit())

        row_preset.addWidget(lbl_p)
        row_preset.addWidget(self.combo_preset, 1)
        row_preset.addWidget(btn_test)
        l1.addLayout(row_preset)

        self.cb_enable_anim = QCheckBox("Enable Animations (Uncheck for instant response)")
        self.cb_enable_anim.setChecked(self._db.get_setting("animations_enabled", True))
        self.cb_enable_anim.toggled.connect(lambda v: self._save("animations_enabled", v))
        l1.addWidget(self.cb_enable_anim)

        layout.addWidget(c1)

        # 2. Timing & Speed Sliders Card
        c2 = QFrame()
        c2.setObjectName("card")
        l2 = QVBoxLayout(c2)
        l2.setSpacing(14)

        h2 = QLabel("Durations & Transition Speeds")
        h2.setObjectName("card_header")
        l2.addWidget(h2)

        # Open Duration
        self.slider_open, self.lbl_open = self._create_ms_slider(
            l2, "Opening Duration", "open_duration", 50, 600, 220
        )
        # Close Duration
        self.slider_close, self.lbl_close = self._create_ms_slider(
            l2, "Closing Duration", "close_duration", 50, 400, 160
        )
        # Segment Transition Speed
        self.slider_seg, self.lbl_seg = self._create_ms_slider(
            l2, "Segment Transition Speed", "segment_transition_speed", 40, 300, 160
        )
        # Hover Animation Speed
        self.slider_hover, self.lbl_hover = self._create_ms_slider(
            l2, "Hover Animation Speed", "hover_animation_speed", 30, 250, 120
        )

        layout.addWidget(c2)

        # 3. Dynamic Effects Toggles Card
        c3 = QFrame()
        c3.setObjectName("card")
        l3 = QVBoxLayout(c3)
        l3.setSpacing(12)

        h3 = QLabel("Visual Effect Elements")
        h3.setObjectName("card_header")
        l3.addWidget(h3)

        self.cb_scale = QCheckBox("Scale animation (Zooms in smoothly on appearance)")
        self.cb_scale.setChecked(self._db.get_setting("scale_animation", True))
        self.cb_scale.toggled.connect(lambda v: self._save("scale_animation", v))
        l3.addWidget(self.cb_scale)

        self.cb_rotation = QCheckBox("Rotation animation (Subtle spin into alignment)")
        self.cb_rotation.setChecked(self._db.get_setting("rotation_animation", True))
        self.cb_rotation.toggled.connect(lambda v: self._save("rotation_animation", v))
        l3.addWidget(self.cb_rotation)

        self.cb_blur_tr = QCheckBox("Blur transition effect")
        self.cb_blur_tr.setChecked(self._db.get_setting("blur_transition", True))
        self.cb_blur_tr.toggled.connect(lambda v: self._save("blur_transition", v))
        l3.addWidget(self.cb_blur_tr)

        self.cb_sel_anim = QCheckBox("Selection sweep animation indicator")
        self.cb_sel_anim.setChecked(self._db.get_setting("selection_animation", True))
        self.cb_sel_anim.toggled.connect(lambda v: self._save("selection_animation", v))
        l3.addWidget(self.cb_sel_anim)

        # Glow Intensity Slider
        glow_val = int(float(self._db.get_setting("glow_intensity", 0.85)) * 100)
        row_glow = QVBoxLayout()
        self.lbl_glow = QLabel(f"Neon Accent Glow Intensity: {glow_val}%")
        self.lbl_glow.setStyleSheet("font-weight: 600; color: #FFFFFF;")
        
        self.slider_glow = QSlider(Qt.Orientation.Horizontal)
        self.slider_glow.setRange(20, 100)
        self.slider_glow.setValue(glow_val)
        self.slider_glow.valueChanged.connect(self._on_glow_changed)
        
        row_glow.addWidget(self.lbl_glow)
        row_glow.addWidget(self.slider_glow)
        l3.addLayout(row_glow)

        layout.addWidget(c3)
        layout.addStretch()

    def _create_ms_slider(self, layout, title, key, min_ms, max_ms, default_ms):
        cur_val = int(self._db.get_setting(key, default_ms))
        row = QVBoxLayout()
        row.setSpacing(4)
        
        lbl = QLabel(f"{title}: {cur_val} ms")
        lbl.setStyleSheet("font-weight: 600; color: #FFFFFF;")
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_ms, max_ms)
        slider.setValue(cur_val)

        def on_change(v):
            lbl.setText(f"{title}: {v} ms")
            self._db.set_setting(key, v)
            self.animations_changed.emit()

        slider.valueChanged.connect(on_change)
        row.addWidget(lbl)
        row.addWidget(slider)
        layout.addLayout(row)
        return slider, lbl

    def _on_glow_changed(self, v):
        self.lbl_glow.setText(f"Neon Accent Glow Intensity: {v}%")
        self._db.set_setting("glow_intensity", v / 100.0)
        self.animations_changed.emit()

    def _on_preset_selected(self, preset_name):
        self._db.set_setting("animation_preset", preset_name)
        preset = ANIMATION_PRESETS.get(preset_name)
        if preset:
            self._db.set_setting("open_duration", preset["open_duration"])
            self._db.set_setting("close_duration", preset["close_duration"])
            self._db.set_setting("segment_transition_speed", preset["segment_transition_speed"])
            self._db.set_setting("hover_animation_speed", preset["hover_animation_speed"])
            self._db.set_setting("scale_animation", preset["scale_animation"])
            self._db.set_setting("rotation_animation", preset["rotation_animation"])
            self._db.set_setting("glow_intensity", preset["glow_intensity"])
            self._db.set_setting("blur_transition", preset["blur_transition"])
            self._db.set_setting("selection_animation", preset["selection_animation"])

            # Update UI elements
            self.slider_open.setValue(preset["open_duration"])
            self.slider_close.setValue(preset["close_duration"])
            self.slider_seg.setValue(preset["segment_transition_speed"])
            self.slider_hover.setValue(preset["hover_animation_speed"])
            self.cb_scale.setChecked(preset["scale_animation"])
            self.cb_rotation.setChecked(preset["rotation_animation"])
            self.cb_blur_tr.setChecked(preset["blur_transition"])
            self.cb_sel_anim.setChecked(preset["selection_animation"])
            self.slider_glow.setValue(int(preset["glow_intensity"] * 100))

        self.animations_changed.emit()

    def _save(self, key, val):
        self._db.set_setting(key, val)
        self.animations_changed.emit()
