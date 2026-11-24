"""
Transparency Controls Page for Nexus Wheel Dashboard.
Configures glassmorphism opacities, frosted blur, vignette dimming, and provides a live preview.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QFrame, QSplitter
)
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient, QLinearGradient
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from database.db import DatabaseManager
from utils.icon_provider import IconProvider

class TransparencyPreviewWidget(QWidget):
    """Real-time miniature rendering preview of the radial wheel with current opacity settings."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(260, 260)
        self.setStyleSheet("background: transparent;")
        self._db = DatabaseManager()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        cx = self.width() / 2.0
        cy = self.height() / 2.0

        # Background checkerboard or grid pattern to show transparency contrast
        painter.fillRect(self.rect(), QColor(14, 18, 26))
        # Draw tech grid
        painter.setPen(QPen(QColor(255, 255, 255, 12), 1.0))
        for x in range(0, self.width(), 20):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 20):
            painter.drawLine(0, y, self.width(), y)

        settings = self._db.get_all_settings()
        overall_op = float(settings.get("overall_opacity", 0.95))
        bg_op = float(settings.get("bg_opacity", 0.85))
        seg_op = float(settings.get("segment_opacity", 0.90))
        hl_op = float(settings.get("highlight_opacity", 0.95))
        accent_hex = settings.get("accent_color", "#00F0FF")
        accent = QColor(accent_hex)

        painter.save()
        painter.translate(cx, cy)
        painter.setOpacity(overall_op)

        # Ambient Glow Plate
        r = 110.0
        bg_grad = QRadialGradient(0, 0, r)
        bg_grad.setColorAt(0.0, QColor(14, 18, 26, int(bg_op * 240)))
        bg_grad.setColorAt(0.8, QColor(10, 13, 20, int(bg_op * 255)))
        bg_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(bg_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(0, 0), r, r)

        # 6 mini segments
        for i in range(6):
            start_ang = -90.0 + (i * 60.0) - 27.0
            sweep_ang = 54.0
            r_out = 100.0
            r_in = 52.0

            if i == 0: # Highlighted segment
                painter.setBrush(QBrush(QColor(accent.red(), accent.green(), accent.blue(), int(hl_op * 200))))
                painter.setPen(QPen(accent, 2.0))
            else:
                painter.setBrush(QBrush(QColor(22, 28, 40, int(seg_op * 220))))
                painter.setPen(QPen(QColor(255, 255, 255, 30), 1.0))

            from PySide6.QtGui import QPainterPath
            path = QPainterPath()
            path.arcMoveTo(QRectF(-r_out, -r_out, r_out * 2, r_out * 2), -start_ang)
            path.arcTo(QRectF(-r_out, -r_out, r_out * 2, r_out * 2), -start_ang, -sweep_ang)
            path.arcTo(QRectF(-r_in, -r_in, r_in * 2, r_in * 2), -(start_ang + sweep_ang), sweep_ang)
            path.closeSubpath()
            painter.drawPath(path)

        # Center mini HUD
        r_c = 46.0
        painter.setBrush(QBrush(QColor(10, 14, 22, 245)))
        painter.setPen(QPen(accent, 2.0))
        painter.drawEllipse(QPointF(0, 0), r_c, r_c)
        pix = IconProvider.get_pixmap("wheel", accent_hex, 24)
        painter.drawPixmap(-12, -12, pix)

        painter.restore()


class TransparencyPage(QWidget):
    transparency_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Transparency & Glassmorphism")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title)

        desc = QLabel("Fine-tune glass transparency, segment opacities, blur, and full-screen dimming with live preview.")
        desc.setStyleSheet("color: #8B949E; margin-bottom: 4px;")
        layout.addWidget(desc)

        # Splitter or Horizontal Layout: Sliders on left, Live Preview Card on right
        h_main = QHBoxLayout()
        h_main.setSpacing(20)

        # Left Column: Sliders
        col_sliders = QVBoxLayout()
        col_sliders.setSpacing(12)

        card_sliders = QFrame()
        card_sliders.setObjectName("card")
        l_s = QVBoxLayout(card_sliders)
        l_s.setSpacing(14)

        # 1. Overall Opacity
        self.slider_overall, self.lbl_overall = self._create_slider(
            l_s, "Overall Wheel Opacity", "overall_opacity", 0.1, 1.0, 0.95
        )

        # 2. Background Opacity
        self.slider_bg, self.lbl_bg = self._create_slider(
            l_s, "Background Glass Opacity", "bg_opacity", 0.1, 1.0, 0.85
        )

        # 3. Segment Opacity
        self.slider_seg, self.lbl_seg = self._create_slider(
            l_s, "Segment Opacity", "segment_opacity", 0.1, 1.0, 0.90
        )

        # 4. Icon Opacity
        self.slider_icon, self.lbl_icon = self._create_slider(
            l_s, "Icon Opacity", "icon_opacity", 0.1, 1.0, 1.0
        )

        # 5. Selection Highlight Opacity
        self.slider_hl, self.lbl_hl = self._create_slider(
            l_s, "Selection Highlight Opacity", "highlight_opacity", 0.1, 1.0, 0.95
        )

        # 6. Dimming Overlay Opacity
        self.slider_dim, self.lbl_dim = self._create_slider(
            l_s, "Screen Dimming Vignette Opacity", "dimming_opacity", 0.0, 1.0, 0.0
        )

        # 7. Blur Intensity
        self.slider_blur, self.lbl_blur = self._create_slider_int(
            l_s, "Background Blur Intensity (px)", "blur_intensity", 0, 50, 20
        )

        col_sliders.addWidget(card_sliders)
        h_main.addLayout(col_sliders, 3)

        # Right Column: Live Interactive Preview Card
        card_preview = QFrame()
        card_preview.setObjectName("card")
        card_preview.setFixedWidth(300)
        l_prev = QVBoxLayout(card_preview)
        l_prev.setAlignment(Qt.AlignmentFlag.AlignCenter)

        h_prev = QLabel("Live Glass Preview")
        h_prev.setObjectName("card_header")
        h_prev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l_prev.addWidget(h_prev)

        self.preview_widget = TransparencyPreviewWidget()
        l_prev.addWidget(self.preview_widget)

        lbl_prev_hint = QLabel("Adjusting sliders updates rendering immediately across desktop overlays.")
        lbl_prev_hint.setObjectName("card_desc")
        lbl_prev_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_prev_hint.setWordWrap(True)
        l_prev.addWidget(lbl_prev_hint)

        h_main.addWidget(card_preview, 2)
        layout.addLayout(h_main)
        layout.addStretch()

    def _create_slider(self, layout, label_text, key, min_val, max_val, default_val):
        cur_val = float(self._db.get_setting(key, default_val))
        row = QVBoxLayout()
        row.setSpacing(4)
        
        lbl = QLabel(f"{label_text}: {int(cur_val * 100)}%")
        lbl.setStyleSheet("font-weight: 600; color: #FFFFFF;")
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(int(min_val * 100), int(max_val * 100))
        slider.setValue(int(cur_val * 100))
        
        def on_change(v):
            f_val = v / 100.0
            lbl.setText(f"{label_text}: {v}%")
            self._db.set_setting(key, f_val)
            self.preview_widget.update()
            self.transparency_changed.emit()

        slider.valueChanged.connect(on_change)
        row.addWidget(lbl)
        row.addWidget(slider)
        layout.addLayout(row)
        return slider, lbl

    def _create_slider_int(self, layout, label_text, key, min_val, max_val, default_val):
        cur_val = int(self._db.get_setting(key, default_val))
        row = QVBoxLayout()
        row.setSpacing(4)
        
        lbl = QLabel(f"{label_text}: {cur_val}px")
        lbl.setStyleSheet("font-weight: 600; color: #FFFFFF;")
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(cur_val)
        
        def on_change(v):
            lbl.setText(f"{label_text}: {v}px")
            self._db.set_setting(key, v)
            self.preview_widget.update()
            self.transparency_changed.emit()

        slider.valueChanged.connect(on_change)
        row.addWidget(lbl)
        row.addWidget(slider)
        layout.addLayout(row)
        return slider, lbl
