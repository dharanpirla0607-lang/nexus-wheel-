"""
Smart Photo Downloader and Screen Extractor for Nexus Wheel.
Captures photos under cursor, detects bounding contours via Computer Vision,
and exports into any image format (PNG, JPG, WEBP, BMP, ICO, TIFF, GIF, PDF).
"""

import os
import io
import time
import math
from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List
from PIL import Image, ImageGrab
import numpy as np
import cv2

try:
    import win32gui
    import win32ui
    import win32con
    import win32api
except ImportError:
    win32gui = None

class PhotoDownloader:
    SUPPORTED_FORMATS = ["PNG", "JPG", "WEBP", "BMP", "ICO", "TIFF", "GIF", "PDF"]

    FORMAT_DESCRIPTIONS = {
        "PNG": "Lossless PNG with transparency support",
        "JPG": "Standard JPEG photo (compressed)",
        "WEBP": "Modern WebP (high quality & compact)",
        "BMP": "Uncompressed Windows Bitmap",
        "ICO": "Windows Icon (multi-resolution 16-256px)",
        "TIFF": "High Dynamic Range / Print TIFF",
        "GIF": "Graphics Interchange Format",
        "PDF": "Portable Document Format (Single-page)"
    }

    @staticmethod
    def capture_full_screen() -> Image.Image:
        """Captures the entire virtual screen across all monitors."""
        try:
            # ImageGrab.grab(all_screens=True) grabs entire virtual screen
            img = ImageGrab.grab(all_screens=True)
            return img
        except Exception as e:
            print(f"[PhotoDownloader] Standard grab failed: {e}, falling back to primary")
            try:
                return ImageGrab.grab()
            except Exception as e2:
                print(f"[PhotoDownloader] Screen grab fatal: {e2}")
                # Create a blank fallback
                return Image.new("RGB", (1920, 1080), (30, 30, 30))

    @staticmethod
    def detect_photo_bounds(
        screen_img: Image.Image,
        cursor_x: int,
        cursor_y: int,
        search_radius: int = 700
    ) -> Tuple[int, int, int, int]:
        """
        Uses OpenCV edge and contour analysis to detect the bounding box of a photo
        under the given cursor coordinates. Returns (x, y, width, height).
        """
        img_w, img_h = screen_img.size

        # Clamp cursor to image bounds
        cx = max(0, min(img_w - 1, cursor_x))
        cy = max(0, min(img_h - 1, cursor_y))

        # Check Window rect under cursor if win32gui is available
        win_rect = None
        if win32gui:
            try:
                hwnd = win32gui.WindowFromPoint((cx, cy))
                if hwnd:
                    # Get root window or child control
                    wx1, wy1, wx2, wy2 = win32gui.GetWindowRect(hwnd)
                    if wx2 > wx1 and wy2 > wy1:
                        win_rect = (wx1, wy1, wx2 - wx1, wy2 - wy1)
            except Exception:
                pass

        # Define Region of Interest (ROI) around cursor
        rx1 = max(0, cx - search_radius)
        ry1 = max(0, cy - search_radius)
        rx2 = min(img_w, cx + search_radius)
        ry2 = min(img_h, cy + search_radius)

        roi_crop = screen_img.crop((rx1, ry1, rx2, ry2))
        np_roi = np.array(roi_crop)

        if len(np_roi.shape) == 3 and np_roi.shape[2] >= 3:
            bgr = cv2.cvtColor(np_roi, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        else:
            gray = np_roi

        roi_cx = cx - rx1
        roi_cy = cy - ry1

        # Multi-scale edge detection
        candidates = []

        # Pass 1: Canny with gentle morphological connection
        edges = cv2.Canny(gray, 30, 130)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(closed_edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if x <= roi_cx <= x + w and y <= roi_cy <= y + h:
                if w >= 60 and h >= 60:
                    candidates.append((x + rx1, y + ry1, w, h))

        # Pass 2: Adaptive thresholding for high-contrast photo borders / frames
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 15, 3
        )
        kernel_t = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed_thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_t)
        contours_t, _ = cv2.findContours(closed_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours_t:
            x, y, w, h = cv2.boundingRect(cnt)
            if x <= roi_cx <= x + w and y <= roi_cy <= y + h:
                if w >= 60 and h >= 60:
                    candidates.append((x + rx1, y + ry1, w, h))

        # Filter candidates: remove those that are practically the entire search region
        valid = []
        roi_w = rx2 - rx1
        roi_h = ry2 - ry1
        for (x, y, w, h) in candidates:
            # Check aspect ratio isn't a long thin line (like scrollbar or line)
            if w / max(1, h) > 10 or h / max(1, w) > 10:
                continue
            if w > roi_w * 0.98 and h > roi_h * 0.98:
                continue
            valid.append((x, y, w, h))

        if valid:
            # Find the best candidate:
            # Prefer rectangles with area between 10,000 px^2 (e.g. 100x100) and reasonable size
            valid.sort(key=lambda b: (b[2] * b[3]))
            # If the smallest is very small (< 120x120), see if there's a slightly larger containing photo
            chosen = valid[0]
            for b in valid:
                if b[2] >= 140 and b[3] >= 140:
                    chosen = b
                    break
            return chosen

        # Fallback 1: Window rect if reasonable
        if win_rect:
            wx, wy, ww, wh = win_rect
            if 100 <= ww <= 1920 and 100 <= wh <= 1200:
                return (max(0, wx), max(0, wy), min(img_w - wx, ww), min(img_h - wy, wh))

        # Fallback 2: Default 500x500 box centered on cursor
        def_w, def_h = 500, 500
        fx = max(0, min(img_w - def_w, cx - def_w // 2))
        fy = max(0, min(img_h - def_h, cy - def_h // 2))
        return (fx, fy, def_w, def_h)

    @staticmethod
    def crop_photo(screen_img: Image.Image, bounds: Tuple[int, int, int, int]) -> Image.Image:
        """Crops the image to specified bounding box (x, y, w, h)."""
        x, y, w, h = bounds
        img_w, img_h = screen_img.size
        x1 = max(0, min(img_w - 1, x))
        y1 = max(0, min(img_h - 1, y))
        x2 = max(x1 + 10, min(img_w, x + w))
        y2 = max(y1 + 10, min(img_h, y + h))
        return screen_img.crop((x1, y1, x2, y2))

    @staticmethod
    def get_clipboard_image() -> Optional[Image.Image]:
        """Checks if there is an image in clipboard."""
        try:
            cb_img = ImageGrab.grabclipboard()
            if isinstance(cb_img, Image.Image):
                return cb_img
        except Exception:
            pass
        return None

    @staticmethod
    def save_image(
        image: Image.Image,
        output_path: str,
        target_format: str = "PNG",
        quality: int = 95
    ) -> str:
        """
        Saves PIL Image to the target path in the requested format.
        Supported formats: PNG, JPG, WEBP, BMP, ICO, TIFF, GIF, PDF.
        """
        fmt = target_format.upper().strip()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        if fmt in ("JPG", "JPEG"):
            # JPEG doesn't support alpha channel; composite over white
            if image.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                bg.paste(image, mask=image.split()[-1] if len(image.split()) == 4 else None)
                save_img = bg
            else:
                save_img = image.convert("RGB")
            save_img.save(output_path, "JPEG", quality=quality, optimize=True)

        elif fmt == "PNG":
            if image.mode not in ("RGB", "RGBA"):
                save_img = image.convert("RGBA")
            else:
                save_img = image
            save_img.save(output_path, "PNG", optimize=True)

        elif fmt == "WEBP":
            save_img = image.convert("RGBA") if image.mode in ("RGBA", "P") else image.convert("RGB")
            save_img.save(output_path, "WEBP", quality=quality, method=6)

        elif fmt == "BMP":
            save_img = image.convert("RGB")
            save_img.save(output_path, "BMP")

        elif fmt == "ICO":
            # Windows icon format supports multiple resolutions
            sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
            rgba = image.convert("RGBA")
            rgba.save(output_path, "ICO", sizes=sizes)

        elif fmt == "TIFF":
            save_img = image.convert("RGBA") if image.mode == "RGBA" else image.convert("RGB")
            save_img.save(output_path, "TIFF", compression="tiff_deflate")

        elif fmt == "GIF":
            save_img = image.convert("P", palette=Image.ADAPTIVE, colors=256)
            save_img.save(output_path, "GIF")

        elif fmt == "PDF":
            save_img = image.convert("RGB")
            save_img.save(output_path, "PDF", resolution=150.0)

        else:
            # Fallback
            image.save(output_path)

        return output_path

    @staticmethod
    def get_default_download_dir() -> str:
        """Returns standard Windows Downloads folder."""
        try:
            import winreg
            sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                val, _ = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")
                if os.path.isdir(val):
                    return val
        except Exception:
            pass

        user_home = os.path.expanduser("~")
        down_dir = os.path.join(user_home, "Downloads")
        if os.path.isdir(down_dir):
            return down_dir
        pic_dir = os.path.join(user_home, "Pictures")
        if os.path.isdir(pic_dir):
            return pic_dir
        return user_home

    @classmethod
    def generate_default_filename(cls, ext: str) -> str:
        ext_clean = ext.lower().replace(".", "").strip()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"Photo_{ts}.{ext_clean}"
