import io
import time
from pathlib import Path
from typing import Optional
from PIL import Image
import win32clipboard
import win32con

from automation.base_adapter import ensure_interactive_desktop
from config.logger import logger


def copy_text_to_clipboard(text: str, retries: int = 5, delay: float = 0.05) -> bool:
    """Sao chép chuỗi văn bản UTF-8 (hỗ trợ đầy đủ tiếng Việt) vào Windows Clipboard."""
    ensure_interactive_desktop()
    for attempt in range(retries):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            # CF_UNICODETEXT hỗ trợ chuỗi Unicode đầy đủ (UTF-16/UTF-8 tiếng Việt)
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
            win32clipboard.CloseClipboard()
            logger.debug(f"Đã sao chép văn bản vào clipboard ({len(text)} ký tự).")
            return True
        except Exception as e:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
            time.sleep(delay)

    logger.error("Không thể mở hoặc ghi vào Windows Clipboard sau nhiều lần thử.")
    return False


def get_text_from_clipboard(retries: int = 5, delay: float = 0.05) -> Optional[str]:
    """Đọc chuỗi văn bản từ Windows Clipboard (dùng để kiểm thử hoặc kiểm tra)."""
    ensure_interactive_desktop()
    for _ in range(retries):
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                return data
            win32clipboard.CloseClipboard()
            return None
        except Exception:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
            time.sleep(delay)
    return None


def copy_image_to_clipboard(image_path: Path, retries: int = 5, delay: float = 0.05) -> bool:
    """Đọc file ảnh và nạp dữ liệu định dạng CF_DIB (Device Independent Bitmap) vào Windows Clipboard.
    
    Cơ chế chuẩn trên Windows:
    - Mở ảnh bằng Pillow, chuyển sang hệ màu RGB.
    - Lưu vào bộ nhớ dạng BMP (bỏ qua 14 bytes header BITMAPFILEHEADER).
    - Đẩy phần còn lại (BITMAPINFOHEADER + pixel bits) vào Clipboard qua CF_DIB.
    """
    ensure_interactive_desktop()
    if not image_path.exists():
        logger.error(f"File ảnh không tồn tại để nạp vào clipboard: {image_path}")
        return False

    try:
        with Image.open(image_path) as img:
            output = io.BytesIO()
            # Chuyển đổi sang RGB nếu đang ở RGBA/P
            rgb_image = img.convert("RGB")
            rgb_image.save(output, "BMP")
            # Bỏ qua 14 byte đầu của header BITMAPFILEHEADER để tạo CF_DIB chuẩn
            dib_data = output.getvalue()[14:]
            output.close()
    except Exception as e:
        logger.error(f"Lỗi khi xử lý file ảnh {image_path}: {e}")
        return False

    for attempt in range(retries):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_DIB, dib_data)
            win32clipboard.CloseClipboard()
            logger.info(f"Đã sao chép ảnh {image_path.name} ({len(dib_data)} bytes) vào clipboard.")
            return True
        except Exception as e:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
            time.sleep(delay)

    logger.error("Không thể ghi dữ liệu ảnh CF_DIB vào Windows Clipboard.")
    return False


def is_image_in_clipboard(retries: int = 5, delay: float = 0.05) -> bool:
    """Kiểm tra xem Windows Clipboard hiện tại có đang chứa dữ liệu hình ảnh (CF_DIB) hay không."""
    ensure_interactive_desktop()
    for _ in range(retries):
        try:
            win32clipboard.OpenClipboard()
            has_image = bool(win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB))
            win32clipboard.CloseClipboard()
            return has_image
        except Exception:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
            time.sleep(delay)
    return False
