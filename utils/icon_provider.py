"""
Vector Icon Provider for Nexus Wheel.
Renders crisp, high-DPI vector icons dynamically using QPainterPath.
Provides icons for all 50+ actions, categories, and dashboard tabs.
"""

from PySide6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QColor, QPen, QBrush
from PySide6.QtCore import Qt, QRectF, QPointF
import math

class IconProvider:
    _cache = {}

    @classmethod
    def get_icon(cls, name: str, color_hex: str = "#00F0FF", size: int = 48) -> QIcon:
        key = f"{name}_{color_hex}_{size}"
        if key in cls._cache:
            return cls._cache[key]
        pixmap = cls.get_pixmap(name, color_hex, size)
        icon = QIcon(pixmap)
        cls._cache[key] = icon
        return icon

    @classmethod
    def get_pixmap(cls, name: str, color_hex: str = "#00F0FF", size: int = 48) -> QPixmap:
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        c = QColor(color_hex)
        pen = QPen(c, max(2.0, size / 16.0))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        s = float(size)
        pad = s * 0.18
        w = s - 2 * pad
        h = s - 2 * pad
        rect = QRectF(pad, pad, w, h)
        cx = s / 2.0
        cy = s / 2.0

        n = name.lower().replace("-", "_").replace(" ", "_")

        # Draw according to icon name
        if "chrome" in n:
            painter.drawEllipse(QPointF(cx, cy), w * 0.45, w * 0.45)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(QPointF(cx, cy), w * 0.18, w * 0.18)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawLine(QPointF(cx, cy - w * 0.45), QPointF(cx + w * 0.35, cy - w * 0.1))
            painter.drawLine(QPointF(cx + w * 0.38, cy + w * 0.22), QPointF(cx - w * 0.1, cy + w * 0.44))
            painter.drawLine(QPointF(cx - w * 0.38, cy - w * 0.22), QPointF(cx - w * 0.25, cy - w * 0.38))

        elif "edge" in n:
            path = QPainterPath()
            path.arcMoveTo(rect, 45)
            path.arcTo(rect, 45, 270)
            path.cubicTo(QPointF(cx + w * 0.2, cy + w * 0.1), QPointF(cx - w * 0.1, cy - w * 0.2), QPointF(cx, cy))
            painter.drawPath(path)

        elif "code" in n or "vscode" in n or "developer" in n:
            # < / >
            p = QPainterPath()
            p.moveTo(cx - w * 0.2, cy - h * 0.35)
            p.lineTo(cx - w * 0.45, cy)
            p.lineTo(cx - w * 0.2, cy + h * 0.35)
            p.moveTo(cx + w * 0.2, cy - h * 0.35)
            p.lineTo(cx + w * 0.45, cy)
            p.lineTo(cx + w * 0.2, cy + h * 0.35)
            p.moveTo(cx + w * 0.1, cy - h * 0.4)
            p.lineTo(cx - w * 0.1, cy + h * 0.4)
            painter.drawPath(p)

        elif "explorer" in n or "folder" in n:
            p = QPainterPath()
            p.moveTo(pad, pad + h * 0.2)
            p.lineTo(pad + w * 0.35, pad + h * 0.2)
            p.lineTo(pad + w * 0.45, pad + h * 0.35)
            p.lineTo(pad + w, pad + h * 0.35)
            p.lineTo(pad + w, pad + h)
            p.lineTo(pad, pad + h)
            p.closeSubpath()
            painter.drawPath(p)

        elif "setting" in n or "gear" in n:
            # Gear
            painter.drawEllipse(QPointF(cx, cy), w * 0.2, w * 0.2)
            teeth = 8
            for i in range(teeth):
                angle = (i * 360 / teeth) * (math.pi / 180.0)
                x1 = cx + math.cos(angle) * (w * 0.3)
                y1 = cy + math.sin(angle) * (w * 0.3)
                x2 = cx + math.cos(angle) * (w * 0.45)
                y2 = cy + math.sin(angle) * (w * 0.45)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        elif "calc" in n:
            painter.drawRoundedRect(rect, 4, 4)
            painter.drawLine(QPointF(pad + w * 0.2, pad + h * 0.3), QPointF(pad + w * 0.8, pad + h * 0.3))
            painter.drawPoint(QPointF(cx - w * 0.2, cy + h * 0.1))
            painter.drawPoint(QPointF(cx, cy + h * 0.1))
            painter.drawPoint(QPointF(cx + w * 0.2, cy + h * 0.1))
            painter.drawPoint(QPointF(cx - w * 0.2, cy + h * 0.3))
            painter.drawPoint(QPointF(cx, cy + h * 0.3))
            painter.drawPoint(QPointF(cx + w * 0.2, cy + h * 0.3))

        elif "note" in n or "text" in n:
            painter.drawRoundedRect(rect, 3, 3)
            painter.drawLine(QPointF(pad + w * 0.25, pad + h * 0.3), QPointF(pad + w * 0.75, pad + h * 0.3))
            painter.drawLine(QPointF(pad + w * 0.25, pad + h * 0.5), QPointF(pad + w * 0.75, pad + h * 0.5))
            painter.drawLine(QPointF(pad + w * 0.25, pad + h * 0.7), QPointF(pad + w * 0.55, pad + h * 0.7))

        elif "task" in n or "monitor" in n:
            painter.drawRoundedRect(rect, 3, 3)
            p = QPainterPath()
            p.moveTo(pad + w * 0.15, cy)
            p.lineTo(pad + w * 0.35, cy)
            p.lineTo(pad + w * 0.45, cy - h * 0.3)
            p.lineTo(pad + w * 0.55, cy + h * 0.3)
            p.lineTo(pad + w * 0.65, cy)
            p.lineTo(pad + w * 0.85, cy)
            painter.drawPath(p)

        elif "vol_up" in n or "volume_up" in n:
            p = QPainterPath()
            p.moveTo(pad, cy - h * 0.15)
            p.lineTo(pad + w * 0.25, cy - h * 0.15)
            p.lineTo(pad + w * 0.45, cy - h * 0.4)
            p.lineTo(pad + w * 0.45, cy + h * 0.4)
            p.lineTo(pad + w * 0.25, cy + h * 0.15)
            p.lineTo(pad, cy + h * 0.15)
            p.closeSubpath()
            painter.drawPath(p)
            painter.drawArc(QRectF(cx - w * 0.1, cy - h * 0.3, w * 0.5, h * 0.6), -45 * 16, 90 * 16)
            painter.drawArc(QRectF(cx + w * 0.1, cy - h * 0.45, w * 0.5, h * 0.9), -45 * 16, 90 * 16)

        elif "vol_down" in n or "volume_down" in n:
            p = QPainterPath()
            p.moveTo(pad, cy - h * 0.15)
            p.lineTo(pad + w * 0.25, cy - h * 0.15)
            p.lineTo(pad + w * 0.45, cy - h * 0.4)
            p.lineTo(pad + w * 0.45, cy + h * 0.4)
            p.lineTo(pad + w * 0.25, cy + h * 0.15)
            p.lineTo(pad, cy + h * 0.15)
            p.closeSubpath()
            painter.drawPath(p)
            painter.drawArc(QRectF(cx - w * 0.1, cy - h * 0.3, w * 0.5, h * 0.6), -45 * 16, 90 * 16)

        elif "mute" in n:
            p = QPainterPath()
            p.moveTo(pad, cy - h * 0.15)
            p.lineTo(pad + w * 0.25, cy - h * 0.15)
            p.lineTo(pad + w * 0.45, cy - h * 0.4)
            p.lineTo(pad + w * 0.45, cy + h * 0.4)
            p.lineTo(pad + w * 0.25, cy + h * 0.15)
            p.lineTo(pad, cy + h * 0.15)
            p.closeSubpath()
            painter.drawPath(p)
            painter.drawLine(QPointF(cx + w * 0.2, cy - h * 0.25), QPointF(cx + w * 0.45, cy + h * 0.25))
            painter.drawLine(QPointF(cx + w * 0.45, cy - h * 0.25), QPointF(cx + w * 0.2, cy + h * 0.25))

        elif "bright" in n:
            painter.drawEllipse(QPointF(cx, cy), w * 0.22, w * 0.22)
            for i in range(8):
                rad = (i * 45) * math.pi / 180.0
                painter.drawLine(QPointF(cx + math.cos(rad) * w * 0.32, cy + math.sin(rad) * w * 0.32),
                                 QPointF(cx + math.cos(rad) * w * 0.45, cy + math.sin(rad) * w * 0.45))

        elif "wifi" in n:
            painter.drawArc(QRectF(cx - w * 0.45, cy - h * 0.45, w * 0.9, h * 0.9), 45 * 16, 90 * 16)
            painter.drawArc(QRectF(cx - w * 0.3, cy - h * 0.3, w * 0.6, h * 0.6), 45 * 16, 90 * 16)
            painter.drawArc(QRectF(cx - w * 0.15, cy - h * 0.15, w * 0.3, h * 0.3), 45 * 16, 90 * 16)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(QPointF(cx, cy + h * 0.25), 2.5, 2.5)

        elif "bluetooth" in n:
            p = QPainterPath()
            p.moveTo(cx - w * 0.2, cy - h * 0.2)
            p.lineTo(cx + w * 0.25, cy + h * 0.25)
            p.lineTo(cx, cy + h * 0.45)
            p.lineTo(cx, cy - h * 0.45)
            p.lineTo(cx + w * 0.25, cy - h * 0.25)
            p.lineTo(cx - w * 0.2, cy + h * 0.2)
            painter.drawPath(p)

        elif "display" in n:
            painter.drawRoundedRect(QRectF(pad, pad, w, h * 0.65), 3, 3)
            painter.drawLine(QPointF(cx, pad + h * 0.65), QPointF(cx, pad + h * 0.85))
            painter.drawLine(QPointF(cx - w * 0.25, pad + h * 0.85), QPointF(cx + w * 0.25, pad + h * 0.85))

        elif "lock" in n:
            painter.drawRoundedRect(QRectF(pad + w * 0.15, cy - h * 0.1, w * 0.7, h * 0.55), 3, 3)
            p = QPainterPath()
            p.arcMoveTo(QRectF(cx - w * 0.22, cy - h * 0.45, w * 0.44, h * 0.5), 0)
            p.arcTo(QRectF(cx - w * 0.22, cy - h * 0.45, w * 0.44, h * 0.5), 0, 180)
            painter.drawPath(p)

        elif "sleep" in n:
            # Moon
            p = QPainterPath()
            p.moveTo(cx + w * 0.1, pad)
            p.arcTo(rect, 90, 180)
            p.arcTo(QRectF(pad + w * 0.2, pad, w * 0.7, h), 270, -140)
            painter.drawPath(p)

        elif "power" in n or "shutdown" in n:
            painter.drawArc(QRectF(pad + w * 0.1, pad + h * 0.1, w * 0.8, h * 0.8), -60 * 16, 300 * 16)
            painter.drawLine(QPointF(cx, pad + h * 0.05), QPointF(cx, cy))

        elif "restart" in n:
            painter.drawArc(rect, 45 * 16, 270 * 16)
            # Arrow head
            p = QPainterPath()
            p.moveTo(cx + w * 0.35, cy - h * 0.25)
            p.lineTo(cx + w * 0.5, cy - h * 0.05)
            p.lineTo(cx + w * 0.2, cy - h * 0.05)
            p.closeSubpath()
            painter.setBrush(QBrush(c))
            painter.drawPath(p)

        elif "play" in n or "pause" in n or "playback" in n:
            p = QPainterPath()
            p.moveTo(pad + w * 0.25, pad + h * 0.15)
            p.lineTo(pad + w * 0.8, cy)
            p.lineTo(pad + w * 0.25, pad + h * 0.85)
            p.closeSubpath()
            painter.setBrush(QBrush(c))
            painter.drawPath(p)

        elif "next" in n:
            p = QPainterPath()
            p.moveTo(pad + w * 0.15, pad + h * 0.2)
            p.lineTo(cx, cy)
            p.lineTo(pad + w * 0.15, pad + h * 0.8)
            p.closeSubpath()
            p.moveTo(cx, pad + h * 0.2)
            p.lineTo(pad + w * 0.75, cy)
            p.lineTo(cx, pad + h * 0.8)
            p.closeSubpath()
            painter.setBrush(QBrush(c))
            painter.drawPath(p)
            painter.drawLine(QPointF(pad + w * 0.8, pad + h * 0.2), QPointF(pad + w * 0.8, pad + h * 0.8))

        elif "prev" in n:
            p = QPainterPath()
            p.moveTo(pad + w * 0.85, pad + h * 0.2)
            p.lineTo(cx, cy)
            p.lineTo(pad + w * 0.85, pad + h * 0.8)
            p.closeSubpath()
            p.moveTo(cx, pad + h * 0.2)
            p.lineTo(pad + w * 0.25, cy)
            p.lineTo(cx, pad + h * 0.8)
            p.closeSubpath()
            painter.setBrush(QBrush(c))
            painter.drawPath(p)
            painter.drawLine(QPointF(pad + w * 0.2, pad + h * 0.2), QPointF(pad + w * 0.2, pad + h * 0.8))

        elif "spotify" in n or "music" in n:
            painter.drawEllipse(rect)
            painter.drawArc(QRectF(cx - w * 0.35, cy - h * 0.25, w * 0.7, h * 0.3), 30 * 16, 120 * 16)
            painter.drawArc(QRectF(cx - w * 0.28, cy - h * 0.1, w * 0.56, h * 0.26), 30 * 16, 120 * 16)
            painter.drawArc(QRectF(cx - w * 0.2, cy + h * 0.05, w * 0.4, h * 0.22), 30 * 16, 120 * 16)

        elif "minimize" in n:
            painter.drawRoundedRect(rect, 4, 4)
            painter.drawLine(QPointF(pad + w * 0.25, cy + h * 0.25), QPointF(pad + w * 0.75, cy + h * 0.25))

        elif "maximize" in n or "restore" in n:
            painter.drawRoundedRect(rect, 4, 4)
            painter.drawRect(QRectF(pad + w * 0.25, pad + h * 0.25, w * 0.5, h * 0.5))

        elif "close" in n:
            painter.drawRoundedRect(rect, 4, 4)
            painter.drawLine(QPointF(pad + w * 0.3, pad + h * 0.3), QPointF(pad + w * 0.7, pad + h * 0.7))
            painter.drawLine(QPointF(pad + w * 0.7, pad + h * 0.3), QPointF(pad + w * 0.3, pad + h * 0.7))

        elif "snap_left" in n:
            painter.drawRoundedRect(rect, 4, 4)
            painter.setBrush(QBrush(c))
            painter.drawRect(QRectF(pad + w * 0.08, pad + h * 0.1, w * 0.4, h * 0.8))

        elif "snap_right" in n:
            painter.drawRoundedRect(rect, 4, 4)
            painter.setBrush(QBrush(c))
            painter.drawRect(QRectF(cx + w * 0.02, pad + h * 0.1, w * 0.4, h * 0.8))

        elif "desktop" in n:
            painter.drawRoundedRect(QRectF(pad, pad, w, h * 0.7), 2, 2)
            painter.drawLine(QPointF(cx - w * 0.2, pad + h * 0.9), QPointF(cx + w * 0.2, pad + h * 0.9))
            painter.drawLine(QPointF(cx, pad + h * 0.7), QPointF(cx, pad + h * 0.9))

        elif "pin" in n or "top" in n:
            p = QPainterPath()
            p.moveTo(cx - w * 0.15, pad + h * 0.1)
            p.lineTo(cx + w * 0.15, pad + h * 0.1)
            p.lineTo(cx + w * 0.25, pad + h * 0.45)
            p.lineTo(cx + w * 0.05, pad + h * 0.45)
            p.lineTo(cx + w * 0.05, pad + h * 0.85)
            p.lineTo(cx - w * 0.05, pad + h * 0.85)
            p.lineTo(cx - w * 0.05, pad + h * 0.45)
            p.lineTo(cx - w * 0.25, pad + h * 0.45)
            p.closeSubpath()
            painter.drawPath(p)

        elif "copy" in n:
            painter.drawRoundedRect(QRectF(pad, pad + h * 0.2, w * 0.65, h * 0.75), 2, 2)
            painter.drawRoundedRect(QRectF(pad + w * 0.3, pad, w * 0.65, h * 0.75), 2, 2)

        elif "paste" in n:
            painter.drawRoundedRect(QRectF(pad + w * 0.1, pad + h * 0.15, w * 0.8, h * 0.8), 3, 3)
            painter.drawRoundedRect(QRectF(cx - w * 0.2, pad, w * 0.4, h * 0.2), 2, 2)

        elif "cut" in n:
            painter.drawLine(QPointF(pad + w * 0.2, pad + h * 0.2), QPointF(pad + w * 0.8, pad + h * 0.8))
            painter.drawLine(QPointF(pad + w * 0.8, pad + h * 0.2), QPointF(pad + w * 0.2, pad + h * 0.8))
            painter.drawEllipse(QPointF(pad + w * 0.3, pad + h * 0.75), w * 0.12, w * 0.12)
            painter.drawEllipse(QPointF(pad + w * 0.7, pad + h * 0.75), w * 0.12, w * 0.12)

        elif "undo" in n:
            p = QPainterPath()
            p.arcMoveTo(QRectF(pad + w * 0.1, pad + h * 0.2, w * 0.8, h * 0.8), 0)
            p.arcTo(QRectF(pad + w * 0.1, pad + h * 0.2, w * 0.8, h * 0.8), 0, 180)
            painter.drawPath(p)
            painter.drawLine(QPointF(pad + w * 0.1, cy), QPointF(pad, cy - h * 0.15))
            painter.drawLine(QPointF(pad + w * 0.1, cy), QPointF(pad + w * 0.2, cy - h * 0.15))

        elif "redo" in n:
            p = QPainterPath()
            p.arcMoveTo(QRectF(pad + w * 0.1, pad + h * 0.2, w * 0.8, h * 0.8), 180)
            p.arcTo(QRectF(pad + w * 0.1, pad + h * 0.2, w * 0.8, h * 0.8), 180, -180)
            painter.drawPath(p)
            painter.drawLine(QPointF(pad + w * 0.9, cy), QPointF(pad + w * 0.8, cy - h * 0.15))
            painter.drawLine(QPointF(pad + w * 0.9, cy), QPointF(pad + w, cy - h * 0.15))

        elif "screenshot" in n or "snip" in n:
            painter.drawRoundedRect(rect, 4, 4)
            painter.drawEllipse(QPointF(cx, cy), w * 0.2, w * 0.2)
            painter.drawPoint(QPointF(pad + w * 0.8, pad + h * 0.25))

        elif "clipboard" in n:
            painter.drawRoundedRect(QRectF(pad + w * 0.15, pad + h * 0.15, w * 0.7, h * 0.8), 3, 3)
            painter.drawRoundedRect(QRectF(cx - w * 0.2, pad + h * 0.05, w * 0.4, h * 0.18), 2, 2)
            painter.drawLine(QPointF(pad + w * 0.3, cy), QPointF(pad + w * 0.7, cy))
            painter.drawLine(QPointF(pad + w * 0.3, cy + h * 0.2), QPointF(pad + w * 0.7, cy + h * 0.2))

        elif "download" in n:
            painter.drawLine(QPointF(cx, pad + h * 0.15), QPointF(cx, pad + h * 0.65))
            painter.drawLine(QPointF(cx - w * 0.25, pad + h * 0.45), QPointF(cx, pad + h * 0.65))
            painter.drawLine(QPointF(cx + w * 0.25, pad + h * 0.45), QPointF(cx, pad + h * 0.65))
            painter.drawLine(QPointF(pad + w * 0.15, pad + h * 0.85), QPointF(pad + w * 0.85, pad + h * 0.85))

        elif "photo" in n or "camera" in n or "image" in n:
            # Camera body
            painter.drawRoundedRect(QRectF(pad, cy - h * 0.3, w, h * 0.65), 5, 5)
            # Lens
            painter.drawEllipse(QPointF(cx, cy + h * 0.05), w * 0.22, w * 0.22)
            # Flash / shutter bump
            painter.drawRoundedRect(QRectF(cx - w * 0.18, cy - h * 0.42, w * 0.36, h * 0.14), 2, 2)
            # Flash dot
            painter.drawEllipse(QPointF(pad + w * 0.8, cy - h * 0.15), 2, 2)

        elif "python" in n:
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "PY")

        elif "terminal" in n or "command" in n:
            painter.drawRoundedRect(rect, 3, 3)
            p = QPainterPath()
            p.moveTo(pad + w * 0.2, cy - h * 0.2)
            p.lineTo(pad + w * 0.4, cy)
            p.lineTo(pad + w * 0.2, cy + h * 0.2)
            painter.drawPath(p)
            painter.drawLine(QPointF(pad + w * 0.45, cy + h * 0.2), QPointF(pad + w * 0.75, cy + h * 0.2))

        elif "web" in n or "globe" in n or "link" in n:
            painter.drawEllipse(rect)
            painter.drawLine(QPointF(pad, cy), QPointF(pad + w, cy))
            painter.drawArc(rect, 0, 360 * 16)
            painter.drawEllipse(QPointF(cx, cy), w * 0.25, h * 0.5)

        elif "game" in n or "gaming" in n:
            # Gamepad
            painter.drawRoundedRect(QRectF(pad, cy - h * 0.3, w, h * 0.6), 8, 8)
            # Dpad
            painter.drawLine(QPointF(pad + w * 0.25, cy - h * 0.15), QPointF(pad + w * 0.25, cy + h * 0.15))
            painter.drawLine(QPointF(pad + w * 0.15, cy), QPointF(pad + w * 0.35, cy))
            # Buttons
            painter.drawPoint(QPointF(pad + w * 0.75, cy - h * 0.1))
            painter.drawPoint(QPointF(pad + w * 0.85, cy))
            painter.drawPoint(QPointF(pad + w * 0.75, cy + h * 0.1))
            painter.drawPoint(QPointF(pad + w * 0.65, cy))

        elif "wheel" in n or "radial" in n:
            painter.drawEllipse(rect)
            painter.drawEllipse(QPointF(cx, cy), w * 0.2, w * 0.2)
            for i in range(4):
                rad = (i * 90) * math.pi / 180.0
                painter.drawLine(QPointF(cx + math.cos(rad) * w * 0.2, cy + math.sin(rad) * w * 0.2),
                                 QPointF(cx + math.cos(rad) * w * 0.5, cy + math.sin(rad) * w * 0.5))

        elif "switch" in n or "window" in n:
            painter.drawRoundedRect(QRectF(pad, pad + h * 0.1, w * 0.6, h * 0.6), 3, 3)
            painter.drawRoundedRect(QRectF(pad + w * 0.3, pad + h * 0.3, w * 0.6, h * 0.6), 3, 3)

        elif "anim" in n or "speed" in n:
            painter.drawArc(rect, 45 * 16, 270 * 16)
            painter.drawLine(QPointF(cx, cy), QPointF(cx + w * 0.25, cy - h * 0.25))

        elif "glass" in n or "transparency" in n or "eye" in n:
            p = QPainterPath()
            p.moveTo(pad, cy)
            p.cubicTo(QPointF(cx - w * 0.2, cy - h * 0.35), QPointF(cx + w * 0.2, cy - h * 0.35), QPointF(pad + w, cy))
            p.cubicTo(QPointF(cx + w * 0.2, cy + h * 0.35), QPointF(cx - w * 0.2, cy + h * 0.35), QPointF(pad, cy))
            painter.drawPath(p)
            painter.drawEllipse(QPointF(cx, cy), w * 0.16, w * 0.16)

        elif "audio" in n or "sound" in n:
            painter.drawArc(QRectF(cx - w * 0.2, cy - h * 0.3, w * 0.4, h * 0.6), -45 * 16, 90 * 16)
            painter.drawArc(QRectF(cx, cy - h * 0.45, w * 0.45, h * 0.9), -45 * 16, 90 * 16)
            p = QPainterPath()
            p.moveTo(pad, cy - h * 0.15)
            p.lineTo(pad + w * 0.2, cy - h * 0.15)
            p.lineTo(pad + w * 0.35, cy - h * 0.35)
            p.lineTo(pad + w * 0.35, cy + h * 0.35)
            p.lineTo(pad + w * 0.2, cy + h * 0.15)
            p.lineTo(pad, cy + h * 0.15)
            p.closeSubpath()
            painter.drawPath(p)

        elif "backup" in n or "restore" in n or "database" in n or "cloud" in n:
            painter.drawRoundedRect(QRectF(pad, pad + h * 0.1, w, h * 0.22), 2, 2)
            painter.drawRoundedRect(QRectF(pad, pad + h * 0.39, w, h * 0.22), 2, 2)
            painter.drawRoundedRect(QRectF(pad, pad + h * 0.68, w, h * 0.22), 2, 2)
            painter.drawPoint(QPointF(pad + w * 0.85, pad + h * 0.21))
            painter.drawPoint(QPointF(pad + w * 0.85, pad + h * 0.5))
            painter.drawPoint(QPointF(pad + w * 0.85, pad + h * 0.79))

        elif "about" in n or "info" in n:
            painter.drawEllipse(rect)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "i")

        elif "general" in n or "home" in n:
            p = QPainterPath()
            p.moveTo(cx, pad)
            p.lineTo(pad + w, cy)
            p.lineTo(pad + w * 0.8, cy)
            p.lineTo(pad + w * 0.8, pad + h)
            p.lineTo(pad + w * 0.2, pad + h)
            p.lineTo(pad + w * 0.2, cy)
            p.lineTo(pad, cy)
            p.closeSubpath()
            painter.drawPath(p)

        elif "keyboard" in n or "shortcut" in n or "control" in n:
            painter.drawRoundedRect(rect, 4, 4)
            painter.drawLine(QPointF(pad + w * 0.2, pad + h * 0.35), QPointF(pad + w * 0.8, pad + h * 0.35))
            painter.drawLine(QPointF(pad + w * 0.2, pad + h * 0.6), QPointF(pad + w * 0.8, pad + h * 0.6))

        else:
            # Default Star / Hexagon Icon
            points = []
            for i in range(6):
                ang = i * (math.pi / 3.0)
                points.append(QPointF(cx + math.cos(ang) * w * 0.45, cy + math.sin(ang) * w * 0.45))
            p = QPainterPath()
            p.moveTo(points[0])
            for pt in points[1:]:
                p.lineTo(pt)
            p.closeSubpath()
            painter.drawPath(p)
            painter.drawPoint(QPointF(cx, cy))

        painter.end()
        return pix
