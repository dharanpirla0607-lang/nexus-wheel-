"""
About & Reference Page for Nexus Wheel Dashboard.
Application details, complete player controls cheat sheet, and system diagnostics.
"""

import sys
import platform
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt, __version__ as PYSIDE_VER
from utils.icon_provider import IconProvider

class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header with Logo
        row_header = QHBoxLayout()
        logo_lbl = QLabel()
        logo_pix = IconProvider.get_pixmap("wheel", "#00F0FF", 64)
        logo_lbl.setPixmap(logo_pix)
        row_header.addWidget(logo_lbl)

        col_head = QVBoxLayout()
        title = QLabel("NEXUS WHEEL")
        title.setStyleSheet("font-size: 26px; font-weight: 900; color: #FFFFFF; letter-spacing: 2px;")
        sub = QLabel("GTA V Inspired Universal Radial Control Wheel for Windows 11 • Version 1.0.0")
        sub.setStyleSheet("color: #00F0FF; font-weight: 700; font-size: 12px;")
        col_head.addWidget(title)
        col_head.addWidget(sub)
        row_header.addLayout(col_head, 1)

        layout.addLayout(row_header)

        # 1. Player Controls Reference Card
        c1 = QFrame()
        c1.setObjectName("card")
        l1 = QVBoxLayout(c1)
        l1.setSpacing(10)

        h1 = QLabel("Controls & Keybindings Reference")
        h1.setObjectName("card_header")
        l1.addWidget(h1)

        controls = [
            ("Mouse Movement", "Move cursor outward into desired segment direction to aim/select"),
            ("Mouse Left Click", "Instantly trigger and execute the hovered shortcut action"),
            ("Mouse Wheel Scroll", "Quickly cycle through categories or wheels"),
            ("Hold Activation Key", "Keep wheel open while key is held down; release to execute (GTA V style)"),
            ("Toggle Activation Key", "Press key once to open wheel, click or press Enter to execute"),
            ("W / A / S / D", "Navigate segment selections using gaming movement keys"),
            ("Arrow Keys (↑ ↓ ← →)", "Navigate between radial segments in 4-way / 8-way directions"),
            ("Enter / Return", "Confirm and execute the currently highlighted action"),
            ("Escape", "Dismiss and cancel the radial menu without executing"),
            ("Alt + X", "Default global hotkey for Main Wheel"),
            ("Ctrl + G", "Default global hotkey for Gaming Wheel"),
            ("Alt + Z", "Default global hotkey for Productivity Wheel"),
            ("Alt + M", "Default global hotkey for Media Wheel"),
            ("Alt + D", "Default global hotkey for Developer Wheel")
        ]

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Input / Action", "Description"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setRowCount(len(controls))
        table.setFixedHeight(220)

        for i, (inp, d) in enumerate(controls):
            item_inp = QTableWidgetItem(inp)
            item_inp.setForeground(Qt.GlobalColor.cyan)
            item_d = QTableWidgetItem(d)
            table.setItem(i, 0, item_inp)
            table.setItem(i, 1, item_d)

        l1.addWidget(table)
        layout.addWidget(c1)

        # 2. System Diagnostics Card
        c2 = QFrame()
        c2.setObjectName("card")
        l2 = QVBoxLayout(c2)
        l2.setSpacing(8)

        h2 = QLabel("System Architecture & Environment")
        h2.setObjectName("card_header")
        l2.addWidget(h2)

        screens = QGuiApplication.screens()
        screen_info = ", ".join([f"{s.name()} ({s.size().width()}x{s.size().height()} @ {s.devicePixelRatio():.1f}x DPI)" for s in screens])

        diag = [
            f"• Operating System: Windows 11 ({platform.system()} {platform.release()} Build {platform.version()})",
            f"• Python Environment: {platform.python_implementation()} {sys.version.split()[0]} ({platform.architecture()[0]})",
            f"• GUI Framework: PySide6 v{PYSIDE_VER} (Native Win32 DirectX/GDI+ Composition)",
            f"• Displays Detected: {len(screens)} Screen(s) — {screen_info}",
            "• Windows API: pywin32 & ctypes integration active (Global hooks, Sound, DWM composition)"
        ]

        for line in diag:
            lbl = QLabel(line)
            lbl.setStyleSheet("color: #8B949E; font-size: 12px;")
            l2.addWidget(lbl)

        layout.addWidget(c2)
        layout.addStretch()
