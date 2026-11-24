"""
Sleek Windows 11 Cyberpunk/Glassmorphic Photo Downloader & Converter Dialog.
Enables downloading any photo captured under cursor in any image format
(PNG, JPG, WEBP, BMP, ICO, TIFF, GIF, PDF).
"""

import os
import subprocess
from typing import Optional, Tuple
from PIL import Image
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QComboBox, QSlider, QLineEdit,
    QFileDialog, QMessageBox, QScrollArea, QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QBrush, QFont, QCursor
from PySide6.QtCore import Qt, QRect, QPoint, QSize, Signal

from utils.photo_downloader import PhotoDownloader
from utils.icon_provider import IconProvider
from windows.audio_controller import AudioController
from database.db import DatabaseManager

class InteractiveCropWidget(QWidget):
    crop_changed = Signal(QRect)

    def __init__(self, full_image: Image.Image, initial_rect: QRect, parent=None):
        super().__init__(parent)
        self.full_image = full_image
        self.crop_rect = initial_rect
        self.is_dragging = False
        self.drag_start = QPoint()
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMinimumSize(480, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Cache converted full QPixmap
        self._pixmap = self._pil_to_pixmap(full_image)

    def _pil_to_pixmap(self, img: Image.Image) -> QPixmap:
        if img.mode != "RGBA":
            img_rgba = img.convert("RGBA")
        else:
            img_rgba = img
        data = img_rgba.tobytes("raw", "RGBA")
        qim = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qim)

    def set_crop_rect(self, rect: QRect):
        self.crop_rect = rect
        self.update()
        self.crop_changed.emit(self.crop_rect)

    def _get_display_geometry(self) -> Tuple[float, float, float, float, float]:
        """Calculates scale and offset for aspect ratio fitting."""
        pw = self._pixmap.width()
        ph = self._pixmap.height()
        ww = self.width()
        wh = self.height()

        scale = min(ww / max(1, pw), wh / max(1, ph))
        disp_w = pw * scale
        disp_h = ph * scale
        ox = (ww - disp_w) / 2.0
        oy = (wh - disp_h) / 2.0
        return scale, ox, oy, disp_w, disp_h

    def _screen_to_img_coords(self, pt: QPoint) -> QPoint:
        scale, ox, oy, _, _ = self._get_display_geometry()
        ix = int((pt.x() - ox) / max(0.0001, scale))
        iy = int((pt.y() - oy) / max(0.0001, scale))
        ix = max(0, min(self.full_image.width, ix))
        iy = max(0, min(self.full_image.height, iy))
        return QPoint(ix, iy)

    def _img_to_screen_rect(self, r: QRect) -> QRect:
        scale, ox, oy, _, _ = self._get_display_geometry()
        sx = int(ox + r.x() * scale)
        sy = int(oy + r.y() * scale)
        sw = int(r.width() * scale)
        sh = int(r.height() * scale)
        return QRect(sx, sy, sw, sh)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start = self._screen_to_img_coords(event.pos())
            self.crop_rect = QRect(self.drag_start, QSize(1, 1))
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            cur = self._screen_to_img_coords(event.pos())
            x1 = min(self.drag_start.x(), cur.x())
            y1 = min(self.drag_start.y(), cur.y())
            w = max(10, abs(cur.x() - self.drag_start.x()))
            h = max(10, abs(cur.y() - self.drag_start.y()))
            self.crop_rect = QRect(x1, y1, w, h)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.is_dragging = False
            if self.crop_rect.width() < 20 or self.crop_rect.height() < 20:
                # Minimum crop size
                self.crop_rect.setWidth(max(40, self.crop_rect.width()))
                self.crop_rect.setHeight(max(40, self.crop_rect.height()))
            self.crop_changed.emit(self.crop_rect)
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # Background
        painter.fillRect(self.rect(), QColor(10, 14, 20))

        scale, ox, oy, disp_w, disp_h = self._get_display_geometry()
        target_rect = QRect(int(ox), int(oy), int(disp_w), int(disp_h))
        painter.drawPixmap(target_rect, self._pixmap)

        # Semi-transparent dark mask over unselected areas
        mask_color = QColor(0, 0, 0, 140)
        s_rect = self._img_to_screen_rect(self.crop_rect)

        # Draw 4 mask regions around selection
        painter.fillRect(QRect(target_rect.left(), target_rect.top(), target_rect.width(), max(0, s_rect.top() - target_rect.top())), mask_color)
        painter.fillRect(QRect(target_rect.left(), s_rect.bottom(), target_rect.width(), max(0, target_rect.bottom() - s_rect.bottom())), mask_color)
        painter.fillRect(QRect(target_rect.left(), s_rect.top(), max(0, s_rect.left() - target_rect.left()), s_rect.height()), mask_color)
        painter.fillRect(QRect(s_rect.right(), s_rect.top(), max(0, target_rect.right() - s_rect.right()), s_rect.height()), mask_color)

        # Neon highlight border around crop
        pen = QPen(QColor("#00F0FF"), 2.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(s_rect)

        # Corner drag handles
        h_pen = QPen(QColor("#FFFFFF"), 2.0)
        h_brush = QBrush(QColor("#00F0FF"))
        painter.setPen(h_pen)
        painter.setBrush(h_brush)
        hs = 6
        corners = [
            s_rect.topLeft(), s_rect.topRight(),
            s_rect.bottomLeft(), s_rect.bottomRight()
        ]
        for c in corners:
            painter.drawRect(QRect(c.x() - hs // 2, c.y() - hs // 2, hs, hs))


class NexusPhotoDownloaderDialog(QDialog):
    def __init__(
        self,
        screen_img: Image.Image,
        cursor_pos: QPoint,
        initial_format: Optional[str] = None,
        parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle("NEXUS PHOTO DOWNLOADER – Universal Image Grabber")
        self.resize(920, 640)
        self.setMinimumSize(820, 560)
        
        self._db = DatabaseManager()
        self._audio = AudioController()

        self.full_screen_img = screen_img
        self.cursor_pos = cursor_pos

        # Detect auto photo bounding box
        self.detected_bounds = PhotoDownloader.detect_photo_bounds(
            screen_img, cursor_pos.x(), cursor_pos.y()
        )
        self.current_crop_rect = QRect(*self.detected_bounds)

        # Format state
        db_fmt = self._db.get_setting("photo_download_format", "PNG")
        self.selected_format = initial_format or db_fmt or "PNG"
        self.quality = 95
        self.scale_pct = 100

        self._init_styles()
        self._init_ui()
        self._update_format_buttons()
        self._update_crop_info()

    def _init_styles(self):
        accent = self._db.get_setting("accent_color", "#00F0FF")
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #0E121A;
                color: #FFFFFF;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
            #card {{
                background-color: #141A24;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                padding: 12px;
            }}
            #card_header {{
                font-size: 13px;
                font-weight: 700;
                color: {accent};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QLabel {{
                color: #C9D1D9;
                font-size: 12px;
            }}
            QLineEdit, QComboBox {{
                background-color: #1B2230;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 6px;
                color: #FFFFFF;
                padding: 7px 10px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {accent};
            }}
            QSlider::groove:horizontal {{
                height: 6px;
                background: #1B2230;
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: {accent};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: #FFFFFF;
                width: 14px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 7px;
            }}
            QPushButton#primary_btn {{
                background-color: {accent};
                color: #000000;
                font-weight: 700;
                font-size: 13px;
                border: none;
                border-radius: 6px;
                padding: 9px 18px;
            }}
            QPushButton#primary_btn:hover {{
                background-color: #33F5FF;
            }}
            QPushButton#secondary_btn {{
                background-color: #212836;
                color: #FFFFFF;
                font-weight: 600;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 6px;
                padding: 8px 14px;
            }}
            QPushButton#secondary_btn:hover {{
                background-color: #2D3748;
                border: 1px solid {accent};
            }}
            QPushButton#fmt_btn {{
                background-color: #1B2230;
                color: #A0AEC0;
                font-weight: 700;
                font-size: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
            }}
            QPushButton#fmt_btn:hover {{
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            QPushButton#fmt_btn_active {{
                background-color: rgba(0, 240, 255, 0.18);
                color: {accent};
                font-weight: 800;
                font-size: 12px;
                border: 2px solid {accent};
                border-radius: 6px;
                padding: 8px 12px;
            }}
        """)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(18, 16, 18, 16)

        # Header Bar
        hdr = QHBoxLayout()
        logo_icon = QLabel()
        accent = self._db.get_setting("accent_color", "#00F0FF")
        logo_icon.setPixmap(IconProvider.get_pixmap("download", accent, 28))
        hdr.addWidget(logo_icon)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        t_lbl = QLabel("PHOTO DOWNLOADER & CONVERTER")
        t_lbl.setStyleSheet(f"font-size: 16px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.5px;")
        sub_lbl = QLabel("Auto-detected photo under cursor. Select target format and save instantly.")
        sub_lbl.setStyleSheet("font-size: 11px; color: #8B949E;")
        title_box.addWidget(t_lbl)
        title_box.addWidget(sub_lbl)
        hdr.addLayout(title_box)
        hdr.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setStyleSheet("background: transparent; color: #8B949E; font-size: 14px; font-weight: bold; border: none;")
        btn_close.clicked.connect(self.reject)
        hdr.addWidget(btn_close)
        main_layout.addLayout(hdr)

        # Content Split: Left (Interactive Image Preview) & Right (Formats & Options)
        body = QHBoxLayout()
        body.setSpacing(16)

        # LEFT: Interactive Crop Preview Widget
        left_box = QVBoxLayout()
        left_box.setSpacing(8)

        # Region Mode Bar
        mode_bar = QHBoxLayout()
        mode_bar.setSpacing(8)
        self.btn_mode_auto = QPushButton("✨ Auto Photo")
        self.btn_mode_auto.setObjectName("secondary_btn")
        self.btn_mode_auto.clicked.connect(self._select_auto_bounds)

        self.btn_mode_crop = QPushButton("🔲 Custom Crop")
        self.btn_mode_crop.setObjectName("secondary_btn")
        self.btn_mode_crop.setToolTip("Click and drag on the image to select custom area")

        self.btn_mode_window = QPushButton("🖼️ Window Area")
        self.btn_mode_window.setObjectName("secondary_btn")
        self.btn_mode_window.clicked.connect(self._select_window_bounds)

        self.btn_mode_clip = QPushButton("📋 From Clipboard")
        self.btn_mode_clip.setObjectName("secondary_btn")
        self.btn_mode_clip.clicked.connect(self._select_clipboard)
        # Check if clipboard has image
        if not PhotoDownloader.get_clipboard_image():
            self.btn_mode_clip.setEnabled(False)

        mode_bar.addWidget(self.btn_mode_auto)
        mode_bar.addWidget(self.btn_mode_crop)
        mode_bar.addWidget(self.btn_mode_window)
        mode_bar.addWidget(self.btn_mode_clip)
        mode_bar.addStretch()
        left_box.addLayout(mode_bar)

        # The interactive preview
        self.crop_widget = InteractiveCropWidget(self.full_screen_img, self.current_crop_rect)
        self.crop_widget.crop_changed.connect(self._on_crop_changed)
        left_box.addWidget(self.crop_widget, 1)

        # Crop resolution status label
        self.lbl_crop_stats = QLabel("Resolution: 0 × 0 px")
        self.lbl_crop_stats.setStyleSheet("font-size: 11px; color: #8B949E;")
        left_box.addWidget(self.lbl_crop_stats)

        body.addLayout(left_box, 6)

        # RIGHT: Export & Format Control Panel
        right_panel = QFrame()
        right_panel.setObjectName("card")
        right_panel.setFixedWidth(340)
        r_layout = QVBoxLayout(right_panel)
        r_layout.setSpacing(12)

        # 1. Format Selection
        lbl_fmt_hdr = QLabel("1. SELECT TARGET FORMAT")
        lbl_fmt_hdr.setObjectName("card_header")
        r_layout.addWidget(lbl_fmt_hdr)

        grid_fmts = QVBoxLayout()
        grid_fmts.setSpacing(6)
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()

        self.fmt_buttons = {}
        formats_row1 = ["PNG", "JPG", "WEBP", "BMP"]
        formats_row2 = ["ICO", "TIFF", "GIF", "PDF"]

        for f in formats_row1:
            btn = QPushButton(f)
            btn.setObjectName("fmt_btn")
            btn.clicked.connect(lambda checked=False, fmt=f: self._on_format_selected(fmt))
            row1.addWidget(btn)
            self.fmt_buttons[f] = btn

        for f in formats_row2:
            btn = QPushButton(f)
            btn.setObjectName("fmt_btn")
            btn.clicked.connect(lambda checked=False, fmt=f: self._on_format_selected(fmt))
            row2.addWidget(btn)
            self.fmt_buttons[f] = btn

        grid_fmts.addLayout(row1)
        grid_fmts.addLayout(row2)
        r_layout.addLayout(grid_fmts)

        self.lbl_fmt_desc = QLabel("Lossless PNG with transparency support")
        self.lbl_fmt_desc.setStyleSheet("font-size: 11px; color: #8B949E; margin-bottom: 4px;")
        r_layout.addWidget(self.lbl_fmt_desc)

        # 2. Quality & Resize Options
        lbl_opt_hdr = QLabel("2. QUALITY & RESOLUTION")
        lbl_opt_hdr.setObjectName("card_header")
        r_layout.addWidget(lbl_opt_hdr)

        self.box_quality = QWidget()
        box_q_l = QVBoxLayout(self.box_quality)
        box_q_l.setContentsMargins(0, 0, 0, 0)
        box_q_l.setSpacing(4)
        self.lbl_quality = QLabel(f"Quality: {self.quality}%")
        self.slider_quality = QSlider(Qt.Orientation.Horizontal)
        self.slider_quality.setRange(20, 100)
        self.slider_quality.setValue(self.quality)
        self.slider_quality.valueChanged.connect(self._on_quality_changed)
        box_q_l.addWidget(self.lbl_quality)
        box_q_l.addWidget(self.slider_quality)
        r_layout.addWidget(self.box_quality)

        row_scale = QHBoxLayout()
        lbl_sc = QLabel("Scale / Resize:")
        self.combo_scale = QComboBox()
        self.combo_scale.addItem("100% (Original)", 100)
        self.combo_scale.addItem("75%", 75)
        self.combo_scale.addItem("50% (Half)", 50)
        self.combo_scale.addItem("150%", 150)
        self.combo_scale.addItem("200% (2x High-DPI)", 200)
        self.combo_scale.currentIndexChanged.connect(self._on_scale_changed)
        row_scale.addWidget(lbl_sc)
        row_scale.addWidget(self.combo_scale)
        r_layout.addLayout(row_scale)

        # 3. Filename & Save Location
        lbl_save_hdr = QLabel("3. SAVE DESTINATION")
        lbl_save_hdr.setObjectName("card_header")
        r_layout.addWidget(lbl_save_hdr)

        r_layout.addWidget(QLabel("Filename:"))
        self.edit_filename = QLineEdit()
        self.edit_filename.setText(PhotoDownloader.generate_default_filename(self.selected_format))
        r_layout.addWidget(self.edit_filename)

        r_layout.addWidget(QLabel("Folder:"))
        row_dir = QHBoxLayout()
        def_dir = self._db.get_setting("photo_download_dir", "") or PhotoDownloader.get_default_download_dir()
        self.edit_dir = QLineEdit(def_dir)
        btn_browse_dir = QPushButton("Browse")
        btn_browse_dir.setObjectName("secondary_btn")
        btn_browse_dir.clicked.connect(self._browse_save_dir)
        row_dir.addWidget(self.edit_dir, 1)
        row_dir.addWidget(btn_browse_dir)
        r_layout.addLayout(row_dir)

        r_layout.addStretch()

        # Action Buttons
        btn_dl = QPushButton("⚡ DOWNLOAD NOW")
        btn_dl.setObjectName("primary_btn")
        btn_dl.clicked.connect(self._download_now)
        r_layout.addWidget(btn_dl)

        row_extra = QHBoxLayout()
        btn_save_as = QPushButton("💾 Save As...")
        btn_save_as.setObjectName("secondary_btn")
        btn_save_as.clicked.connect(self._save_as)

        btn_copy = QPushButton("📋 Copy Image")
        btn_copy.setObjectName("secondary_btn")
        btn_copy.clicked.connect(self._copy_image_to_clipboard)

        row_extra.addWidget(btn_save_as)
        row_extra.addWidget(btn_copy)
        r_layout.addLayout(row_extra)

        body.addWidget(right_panel, 4)
        main_layout.addLayout(body)

    def _update_format_buttons(self):
        for fmt, btn in self.fmt_buttons.items():
            if fmt == self.selected_format:
                btn.setObjectName("fmt_btn_active")
            else:
                btn.setObjectName("fmt_btn")
            btn.setStyle(btn.style())

        self.lbl_fmt_desc.setText(PhotoDownloader.FORMAT_DESCRIPTIONS.get(self.selected_format, ""))
        # Quality slider is relevant for JPG and WEBP
        self.box_quality.setVisible(self.selected_format in ("JPG", "JPEG", "WEBP"))

        # Update filename extension
        cur_fn = self.edit_filename.text().strip()
        if cur_fn:
            base, _ = os.path.splitext(cur_fn)
            self.edit_filename.setText(f"{base}.{self.selected_format.lower()}")

    def _on_format_selected(self, fmt: str):
        self.selected_format = fmt
        self._db.set_setting("photo_download_format", fmt)
        self._update_format_buttons()
        self._audio.play_select()

    def _on_quality_changed(self, val: int):
        self.quality = val
        self.lbl_quality.setText(f"Quality: {val}%")

    def _on_scale_changed(self, index: int):
        self.scale_pct = self.combo_scale.currentData()
        self._update_crop_info()

    def _on_crop_changed(self, rect: QRect):
        self.current_crop_rect = rect
        self._update_crop_info()

    def _update_crop_info(self):
        w = self.current_crop_rect.width()
        h = self.current_crop_rect.height()
        scaled_w = int(w * self.scale_pct / 100.0)
        scaled_h = int(h * self.scale_pct / 100.0)
        scale_txt = f" (Scaled: {scaled_w} × {scaled_h} px)" if self.scale_pct != 100 else ""
        self.lbl_crop_stats.setText(f"Selected Region: {w} × {h} px{scale_txt}")

    def _select_auto_bounds(self):
        self.current_crop_rect = QRect(*self.detected_bounds)
        self.crop_widget.set_crop_rect(self.current_crop_rect)
        self._audio.play_select()

    def _select_window_bounds(self):
        # Full screen image dimensions
        self.current_crop_rect = QRect(0, 0, self.full_screen_img.width, self.full_screen_img.height)
        self.crop_widget.set_crop_rect(self.current_crop_rect)
        self._audio.play_select()

    def _select_clipboard(self):
        cb_img = PhotoDownloader.get_clipboard_image()
        if cb_img:
            self.full_screen_img = cb_img
            self.detected_bounds = (0, 0, cb_img.width, cb_img.height)
            self.current_crop_rect = QRect(0, 0, cb_img.width, cb_img.height)
            self.crop_widget = InteractiveCropWidget(cb_img, self.current_crop_rect)
            self.crop_widget.crop_changed.connect(self._on_crop_changed)
            self._audio.play_select()

    def _browse_save_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.edit_dir.text())
        if d:
            self.edit_dir.setText(d)
            self._db.set_setting("photo_download_dir", d)

    def _get_cropped_pil_image(self) -> Image.Image:
        bounds = (
            self.current_crop_rect.x(),
            self.current_crop_rect.y(),
            self.current_crop_rect.width(),
            self.current_crop_rect.height()
        )
        cropped = PhotoDownloader.crop_photo(self.full_screen_img, bounds)
        if self.scale_pct != 100:
            nw = max(10, int(cropped.width * self.scale_pct / 100.0))
            nh = max(10, int(cropped.height * self.scale_pct / 100.0))
            cropped = cropped.resize((nw, nh), Image.Resampling.LANCZOS)
        return cropped

    def _download_now(self):
        """1-click download directly to chosen folder."""
        folder = self.edit_dir.text().strip() or PhotoDownloader.get_default_download_dir()
        filename = self.edit_filename.text().strip() or PhotoDownloader.generate_default_filename(self.selected_format)
        out_path = os.path.join(folder, filename)

        try:
            cropped = self._get_cropped_pil_image()
            PhotoDownloader.save_image(cropped, out_path, self.selected_format, self.quality)
            self._audio.play_execute()

            # Confirm download
            reply = QMessageBox.information(
                self,
                "Download Successful",
                f"Photo saved successfully:\n{out_path}\n\nWould you like to open the folder?",
                QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
            if reply == QMessageBox.StandardButton.Open:
                subprocess.Popen(f'explorer /select,"{os.path.abspath(out_path)}"')

            self.accept()

        except Exception as e:
            self._audio.play_error()
            QMessageBox.critical(self, "Download Error", f"Failed to save photo:\n{e}")

    def _save_as(self):
        """Standard Windows Save As dialog with target format filter."""
        ext = self.selected_format.lower()
        filter_str = f"{self.selected_format} Files (*.{ext});;All Files (*.*)"
        folder = self.edit_dir.text().strip() or PhotoDownloader.get_default_download_dir()
        filename = self.edit_filename.text().strip()
        default_file = os.path.join(folder, filename)

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Photo As", default_file, filter_str)
        if file_path:
            try:
                cropped = self._get_cropped_pil_image()
                PhotoDownloader.save_image(cropped, file_path, self.selected_format, self.quality)
                self._audio.play_execute()
                self.accept()
            except Exception as e:
                self._audio.play_error()
                QMessageBox.critical(self, "Save Error", f"Failed to save image:\n{e}")

    def _copy_image_to_clipboard(self):
        """Copies the selected photo region directly to Windows clipboard."""
        try:
            import io
            import win32clipboard
            cropped = self._get_cropped_pil_image()
            output = io.BytesIO()
            cropped.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:] # Strip 14-byte BMP header for DIB format
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()

            self._audio.play_execute()
            QMessageBox.information(self, "Copied", "Photo copied to clipboard successfully!")
        except Exception as e:
            self._audio.play_error()
            QMessageBox.warning(self, "Copy Failed", f"Could not copy to clipboard: {e}")
