"""
Player Controls Configuration Page for Nexus Wheel Dashboard.
Hold-to-activate vs Toggle mode, WASD/Arrow navigation, scroll wheel, and deadzone.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QRadioButton, QButtonGroup, QFrame, QSlider
)
from PySide6.QtCore import Qt, Signal
from database.db import DatabaseManager

class PlayerControlsPage(QWidget):
    controls_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Player Controls & Navigation")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title)

        desc = QLabel("Configure GTA V style hold-to-activate or toggle mode, mouse aiming, WASD and arrow keys.")
        desc.setStyleSheet("color: #8B949E; margin-bottom: 8px;")
        layout.addWidget(desc)

        # 1. Activation Mode (Hold vs Toggle)
        c1 = QFrame()
        c1.setObjectName("card")
        l1 = QVBoxLayout(c1)
        l1.setSpacing(12)

        h1 = QLabel("Activation Mode")
        h1.setObjectName("card_header")
        l1.addWidget(h1)

        self.btn_group_mode = QButtonGroup(self)
        
        self.rb_toggle = QRadioButton("Toggle Mode (Press hotkey to open, click or press Enter to execute)")
        self.rb_hold = QRadioButton("Hold Mode – GTA V Classic (Hold hotkey to keep wheel open, release key to execute selection)")

        cur_mode = self._db.get_setting("activation_mode", "toggle")
        if cur_mode == "hold":
            self.rb_hold.setChecked(True)
        else:
            self.rb_toggle.setChecked(True)

        self.btn_group_mode.addButton(self.rb_toggle)
        self.btn_group_mode.addButton(self.rb_hold)

        self.rb_toggle.toggled.connect(self._on_mode_changed)
        self.rb_hold.toggled.connect(self._on_mode_changed)

        l1.addWidget(self.rb_toggle)
        l1.addWidget(self.rb_hold)
        layout.addWidget(c1)

        # 2. Navigation Inputs Card
        c2 = QFrame()
        c2.setObjectName("card")
        l2 = QVBoxLayout(c2)
        l2.setSpacing(12)

        h2 = QLabel("Input Methods")
        h2.setObjectName("card_header")
        l2.addWidget(h2)

        self.cb_mouse = QCheckBox("Select segments using mouse cursor movement / aiming")
        self.cb_mouse.setChecked(self._db.get_setting("mouse_navigation", True))
        self.cb_mouse.toggled.connect(lambda v: self._save("mouse_navigation", v))
        l2.addWidget(self.cb_mouse)

        self.cb_arrows = QCheckBox("Select segments using keyboard Arrow keys (Up, Down, Left, Right)")
        self.cb_arrows.setChecked(self._db.get_setting("keyboard_navigation", True))
        self.cb_arrows.toggled.connect(lambda v: self._save("keyboard_navigation", v))
        l2.addWidget(self.cb_arrows)

        self.cb_wasd = QCheckBox("Navigate using gaming WASD keys")
        self.cb_wasd.setChecked(self._db.get_setting("wasd_navigation", True))
        self.cb_wasd.toggled.connect(lambda v: self._save("wasd_navigation", v))
        l2.addWidget(self.cb_wasd)

        self.cb_scroll = QCheckBox("Use Mouse Wheel scroll to switch active categories")
        self.cb_scroll.setChecked(self._db.get_setting("scroll_wheel_categories", True))
        self.cb_scroll.toggled.connect(lambda v: self._save("scroll_wheel_categories", v))
        l2.addWidget(self.cb_scroll)

        self.cb_enter = QCheckBox("Press Enter / Return to confirm and execute selected action")
        self.cb_enter.setChecked(self._db.get_setting("confirm_with_enter", True))
        self.cb_enter.toggled.connect(lambda v: self._save("confirm_with_enter", v))
        l2.addWidget(self.cb_enter)

        self.cb_escape = QCheckBox("Press Escape to cancel and close wheel")
        self.cb_escape.setChecked(self._db.get_setting("cancel_with_escape", True))
        self.cb_escape.toggled.connect(lambda v: self._save("cancel_with_escape", v))
        l2.addWidget(self.cb_escape)

        layout.addWidget(c2)

        # 3. Dead Zone Tuning Card
        c3 = QFrame()
        c3.setObjectName("card")
        l3 = QVBoxLayout(c3)
        l3.setSpacing(12)

        h3 = QLabel("Dead Zone Sensitivity")
        h3.setObjectName("card_header")
        l3.addWidget(h3)

        desc_dz = QLabel("Defines the inner neutral circle. Minor mouse movements inside this zone will not select segments.")
        desc_dz.setObjectName("card_desc")
        l3.addWidget(desc_dz)

        cur_dz = int(self._db.get_setting("deadzone_radius", 45))
        self.lbl_dz = QLabel(f"Dead Zone Radius: {cur_dz} pixels")
        self.lbl_dz.setStyleSheet("font-weight: 700; color: #00F0FF;")

        self.slider_dz = QSlider(Qt.Orientation.Horizontal)
        self.slider_dz.setRange(20, 90)
        self.slider_dz.setValue(cur_dz)
        self.slider_dz.valueChanged.connect(self._on_dz_slider_changed)

        l3.addWidget(self.lbl_dz)
        l3.addWidget(self.slider_dz)
        layout.addWidget(c3)

        layout.addStretch()

    def _on_mode_changed(self):
        mode = "hold" if self.rb_hold.isChecked() else "toggle"
        self._db.set_setting("activation_mode", mode)
        self.controls_changed.emit()

    def _on_dz_slider_changed(self, val):
        self.lbl_dz.setText(f"Dead Zone Radius: {val} pixels")
        self._db.set_setting("deadzone_radius", val)
        self.controls_changed.emit()

    def _save(self, key, val):
        self._db.set_setting(key, val)
        self.controls_changed.emit()
