"""
Appearance & Themes Page for Nexus Wheel Dashboard.
Choose from presets (Cyberpunk Neon, GTA Classic Orange, Stealth Charcoal, Frost Blue, Crimson) or custom colors.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QColorDialog
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal
from database.db import DatabaseManager

THEMES = [
    {
        "name": "Cyberpunk Neon",
        "accent": "#00F0FF",
        "secondary": "#FF007F",
        "desc": "High-contrast cyan & magenta neon lighting"
    },
    {
        "name": "GTA Classic Orange",
        "accent": "#FF9900",
        "secondary": "#FFAA33",
        "desc": "Iconic Grand Theft Auto weapon wheel amber glow"
    },
    {
        "name": "Frost Blue",
        "accent": "#38BDF8",
        "secondary": "#818CF8",
        "desc": "Windows 11 Fluent icy translucent glow"
    },
    {
        "name": "Stealth Emerald",
        "accent": "#00E676",
        "secondary": "#10B981",
        "desc": "Military night-vision tactical green"
    },
    {
        "name": "Electric Purple",
        "accent": "#C084FC",
        "secondary": "#EC4899",
        "desc": "Deep futuristic synthwave aesthetic"
    },
    {
        "name": "Crimson Strike",
        "accent": "#F43F5E",
        "secondary": "#FB7185",
        "desc": "Aggressive red combat HUD styling"
    }
]

class AppearancePage(QWidget):
    theme_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Appearance & Themes")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title)

        desc = QLabel("Personalize the visual identity of your radial wheel with signature gaming colorways.")
        desc.setStyleSheet("color: #8B949E; margin-bottom: 8px;")
        layout.addWidget(desc)

        # 1. Preset Themes Grid
        c1 = QFrame()
        c1.setObjectName("card")
        l1 = QVBoxLayout(c1)
        l1.setSpacing(14)

        h1 = QLabel("Signature Colorways")
        h1.setObjectName("card_header")
        l1.addWidget(h1)

        cur_theme = self._db.get_setting("theme", "Cyberpunk Neon")

        for t in THEMES:
            row = QHBoxLayout()
            row.setSpacing(12)

            # Color dot preview
            dot = QLabel()
            dot.setFixedSize(22, 22)
            dot.setStyleSheet(f"background-color: {t['accent']}; border-radius: 11px; border: 2px solid #FFFFFF;")
            row.addWidget(dot)

            # Text info
            t_col = QVBoxLayout()
            t_col.setSpacing(2)
            lbl_name = QLabel(t["name"])
            lbl_name.setStyleSheet("font-weight: 700; font-size: 14px; color: #FFFFFF;")
            lbl_sub = QLabel(t["desc"])
            lbl_sub.setStyleSheet("color: #8B949E; font-size: 11px;")
            t_col.addWidget(lbl_name)
            t_col.addWidget(lbl_sub)
            row.addLayout(t_col, 1)

            btn_apply = QPushButton("Applied" if t["name"] == cur_theme else "Apply Theme")
            btn_apply.setObjectName("primary_btn" if t["name"] == cur_theme else "secondary_btn")
            btn_apply.setFixedWidth(110)
            
            # Connect callback
            btn_apply.clicked.connect(lambda ch, th=t: self._apply_theme(th))
            row.addWidget(btn_apply)

            l1.addLayout(row)

        layout.addWidget(c1)

        # 2. Custom Color Picker Card
        c2 = QFrame()
        c2.setObjectName("card")
        l2 = QVBoxLayout(c2)
        l2.setSpacing(12)

        h2 = QLabel("Custom Accent Color")
        h2.setObjectName("card_header")
        l2.addWidget(h2)

        row_cust = QHBoxLayout()
        self.btn_pick_accent = QPushButton("Pick Custom Accent Color")
        self.btn_pick_accent.setObjectName("secondary_btn")
        self.btn_pick_accent.clicked.connect(self._pick_custom_color)
        
        self.lbl_accent_hex = QLabel(f"Current: {self._db.get_setting('accent_color', '#00F0FF')}")
        self.lbl_accent_hex.setStyleSheet("font-weight: 700; color: #FFFFFF;")

        row_cust.addWidget(self.btn_pick_accent)
        row_cust.addWidget(self.lbl_accent_hex)
        row_cust.addStretch()
        l2.addLayout(row_cust)

        layout.addWidget(c2)
        layout.addStretch()

    def _apply_theme(self, theme_dict):
        self._db.set_setting("theme", theme_dict["name"])
        self._db.set_setting("accent_color", theme_dict["accent"])
        self._db.set_setting("secondary_color", theme_dict["secondary"])
        self.lbl_accent_hex.setText(f"Current: {theme_dict['accent']}")
        self.theme_changed.emit(theme_dict["accent"])
        self._init_ui()

    def _pick_custom_color(self):
        cur_hex = self._db.get_setting("accent_color", "#00F0FF")
        color = QColorDialog.getColor(QColor(cur_hex), self, "Select Accent Color")
        if color.isValid():
            hex_str = color.name()
            self._db.set_setting("theme", "Custom")
            self._db.set_setting("accent_color", hex_str)
            self.lbl_accent_hex.setText(f"Current: {hex_str}")
            self.theme_changed.emit(hex_str)
            self._init_ui()
