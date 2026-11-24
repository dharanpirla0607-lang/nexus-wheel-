"""
Modern Minimal Dark Theme QSS Stylesheet for Nexus Wheel Dashboard.
Clean, deep-black aesthetic with pill-style sidebar nav and subtle card borders.
"""


def get_dashboard_stylesheet(accent_hex: str = "#00F0FF") -> str:
    return f"""
    /* ── Global ───────────────────────────────────────────────────── */
    QWidget {{
        background-color: transparent;
        color: #E6EDF3;
        font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
        font-size: 14px;
        selection-background-color: {accent_hex};
        selection-color: #000000;
    }}

    QMainWindow, QDialog {{
        background-color: #0A0D12;
    }}

    /* ── Sidebar ──────────────────────────────────────────────────── */
    QFrame#sidebar {{
        background-color: #111520;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }}

    QLabel#sidebar_title {{
        color: #FFFFFF;
        font-size: 15px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }}

    QLabel#sidebar_sub {{
        color: {accent_hex};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
    }}

    /* Sidebar nav buttons — pill style */
    QPushButton#nav_btn {{
        background-color: transparent;
        color: #8B949E;
        text-align: left;
        padding: 10px 16px;
        border-radius: 14px;
        font-size: 13px;
        font-weight: 600;
        border: none;
        transition: background 0.15s ease;
    }}

    QPushButton#nav_btn:hover {{
        background-color: rgba(255, 255, 255, 0.07);
        color: #FFFFFF;
    }}

    QPushButton#nav_btn:checked {{
        background-color: rgba(0, 240, 255, 0.14);
        color: {accent_hex};
        font-weight: 700;
        border: none;
    }}

    /* ── Content / Scroll Area ────────────────────────────────────── */
    QScrollArea {{
        border: none;
        background: transparent;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0px;
        border-radius: 3px;
    }}

    QScrollBar::handle:vertical {{
        background: rgba(255, 255, 255, 0.15);
        min-height: 20px;
        border-radius: 3px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {accent_hex};
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 6px;
        margin: 0px;
        border-radius: 3px;
    }}

    QScrollBar::handle:horizontal {{
        background: rgba(255, 255, 255, 0.15);
        min-width: 20px;
        border-radius: 3px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {accent_hex};
    }}

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* ── Cards ────────────────────────────────────────────────────── */
    QFrame#card {{
        background-color: #161C28;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 16px;
    }}

    QFrame#card:hover {{
        border: 1px solid rgba(0, 240, 255, 0.20);
    }}

    QLabel#card_header {{
        color: #FFFFFF;
        font-size: 14px;
        font-weight: 700;
    }}

    QLabel#card_desc {{
        color: #8B949E;
        font-size: 12px;
    }}

    /* ── Form Inputs ──────────────────────────────────────────────── */
    QLineEdit, QComboBox, QSpinBox {{
        background-color: #0C1018;
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 9px;
        color: #FFFFFF;
        padding: 8px 12px;
        font-size: 13px;
    }}

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {accent_hex};
        background-color: #0F1420;
    }}

    QComboBox::drop-down {{
        border: none;
        width: 22px;
    }}

    QComboBox QAbstractItemView {{
        background-color: #0C1018;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 8px;
        color: #FFFFFF;
        selection-background-color: rgba(0, 240, 255, 0.20);
        selection-color: #FFFFFF;
        padding: 4px;
    }}

    /* ── Sliders ──────────────────────────────────────────────────── */
    QSlider::groove:horizontal {{
        height: 5px;
        background: #1A2030;
        border-radius: 3px;
    }}

    QSlider::sub-page:horizontal {{
        background: {accent_hex};
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        background: #FFFFFF;
        border: 2px solid {accent_hex};
        width: 15px;
        margin-top: -5px;
        margin-bottom: -5px;
        border-radius: 8px;
    }}

    QSlider::handle:horizontal:hover {{
        background: {accent_hex};
    }}

    /* ── Checkboxes ───────────────────────────────────────────────── */
    QCheckBox {{
        color: #E6EDF3;
        font-size: 13px;
        spacing: 10px;
    }}

    QCheckBox::indicator {{
        width: 17px;
        height: 17px;
        border-radius: 5px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        background-color: #0C1018;
    }}

    QCheckBox::indicator:hover {{
        border-color: {accent_hex};
    }}

    QCheckBox::indicator:checked {{
        background-color: {accent_hex};
        border-color: {accent_hex};
    }}

    /* ── Buttons ──────────────────────────────────────────────────── */
    QPushButton#primary_btn {{
        background-color: {accent_hex};
        color: #000000;
        font-weight: 700;
        font-size: 13px;
        padding: 10px 20px;
        border-radius: 10px;
        border: none;
    }}

    QPushButton#primary_btn:hover {{
        background-color: #33F5FF;
    }}

    QPushButton#primary_btn:pressed {{
        background-color: #00B4D8;
    }}

    QPushButton#secondary_btn {{
        background-color: rgba(255, 255, 255, 0.05);
        color: #CCDDEE;
        font-weight: 600;
        font-size: 13px;
        padding: 9px 16px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.10);
    }}

    QPushButton#secondary_btn:hover {{
        background-color: rgba(255, 255, 255, 0.11);
        border: 1px solid rgba(255, 255, 255, 0.22);
        color: #FFFFFF;
    }}

    QPushButton#danger_btn {{
        background-color: rgba(255, 68, 68, 0.12);
        color: #FF5555;
        font-weight: 600;
        font-size: 13px;
        padding: 9px 16px;
        border-radius: 10px;
        border: 1px solid rgba(255, 68, 68, 0.26);
    }}

    QPushButton#danger_btn:hover {{
        background-color: rgba(255, 68, 68, 0.26);
        border-color: #FF5555;
    }}

    /* ── Tab Widget ───────────────────────────────────────────────── */
    QTabWidget::pane {{
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        background-color: #161C28;
    }}

    QTabBar::tab {{
        background-color: transparent;
        color: #8B949E;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        margin-right: 4px;
    }}

    QTabBar::tab:selected {{
        background-color: rgba(0, 240, 255, 0.14);
        color: {accent_hex};
    }}

    QTabBar::tab:hover:!selected {{
        background-color: rgba(255, 255, 255, 0.07);
        color: #FFFFFF;
    }}

    /* ── Tables & Lists ───────────────────────────────────────────── */
    QTableWidget, QListWidget {{
        background-color: #0C1018;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        gridline-color: rgba(255, 255, 255, 0.04);
        color: #FFFFFF;
        alternate-background-color: #0F1520;
    }}

    QHeaderView::section {{
        background-color: #131A26;
        color: #8B949E;
        font-weight: 600;
        font-size: 12px;
        padding: 7px;
        border: none;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }}

    QTableWidget::item:selected, QListWidget::item:selected {{
        background-color: rgba(0, 240, 255, 0.14);
        color: #FFFFFF;
    }}

    QTableWidget::item:hover, QListWidget::item:hover {{
        background-color: rgba(255, 255, 255, 0.05);
    }}

    /* ── Tooltip ──────────────────────────────────────────────────── */
    QToolTip {{
        background-color: #161C28;
        color: #E6EDF3;
        border: 1px solid rgba(0, 240, 255, 0.30);
        border-radius: 7px;
        padding: 5px 9px;
        font-size: 12px;
    }}
    """
