import abc
import os
import shutil
import time
import ctypes
from pathlib import Path
from typing import Optional, Any
from PIL import Image

from config.logger import logger
from config.loader import load_settings, SettingsConfig


def ensure_interactive_desktop():
    """Đảm bảo thread hiện tại được gắn với desktop tương tác 'default' trên Windows."""
    try:
        import win32con
        user32 = ctypes.windll.user32
        h_desk = user32.OpenDesktopW("default", 0, False, win32con.GENERIC_ALL)
        if h_desk:
            user32.SetThreadDesktop(h_desk)
    except Exception as e:
        logger.debug(f"Không thể chuyển thread desktop: {e}")


class BaseIDEAdapter(abc.ABC):
    """Lớp cơ sở trừu tượng cho tất cả các IDE Adapter (Cursor, Windsurf, VS Code).
    
    Quy tắc kiến trúc:
    - Mọi tương tác với IDE đều thông qua GUI Automation / Process management.
    - Tuyệt đối không gọi trực tiếp API của LLM bên dưới.
    - Đảm bảo độc lập hoàn toàn với module chấm điểm (metrics/scoring).
    """

    def __init__(self, ide_name: str, settings: Optional[SettingsConfig] = None):
        self.ide_name = ide_name.lower()
        self.settings = settings or load_settings()
        self.executable_path: Optional[Path] = None
        self.process: Optional[Any] = None
        self.window: Optional[Any] = None
        self.workspace_dir: Optional[Path] = None

    @abc.abstractmethod
    def resolve_executable_path(self) -> Path:
        """Dò tìm đường dẫn thực thi của IDE trên hệ điều hành Windows."""
        pass

    def prepare_workspace(self, workspace_dir: Path) -> Path:
        """Tạo mới hoặc làm sạch thư mục làm việc tạm trước khi mở IDE.
        
        Nếu thư mục đã tồn tại, xóa toàn bộ nội dung bên trong (trừ .gitkeep) để đảm bảo môi trường sạch.
        """
        workspace_dir.mkdir(parents=True, exist_ok=True)
        for item in workspace_dir.iterdir():
            if item.name == ".gitkeep":
                continue
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                logger.warning(f"Không thể xóa tệp tạm {item}: {e}")
        
        self.workspace_dir = workspace_dir.resolve()
        logger.info(f"Đã chuẩn bị workspace sạch tại: {self.workspace_dir}")
        return self.workspace_dir

    @abc.abstractmethod
    def launch_ide(self, workspace_dir: Path) -> bool:
        """Khởi chạy IDE mở trực tiếp thư mục workspace_dir."""
        pass

    @abc.abstractmethod
    def connect_window(self, timeout: int = 20) -> bool:
        """Tìm và kết nối tới cửa sổ IDE trên Windows."""
        pass

    @abc.abstractmethod
    def focus_and_maximize(self) -> bool:
        """Đưa cửa sổ IDE lên tiền cảnh (foreground) và phóng to toàn màn hình."""
        pass

    @abc.abstractmethod
    def dump_ui_tree(self, output_file: Path) -> bool:
        """Xuất cấu trúc các phần tử giao diện (UI Automation tree) của cửa sổ IDE ra file."""
        pass

    def capture_window_screenshot(self, output_file: Path) -> bool:
        """Chụp ảnh màn hình cửa sổ hiện tại hoặc toàn màn hình để phục vụ ghi log/debug."""
        ensure_interactive_desktop()
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 1. Thử dùng Windows API PrintWindow qua handle cửa sổ
        if self.window is not None:
            try:
                import win32gui
                import win32ui
                hwnd = self.window.handle
                rect = win32gui.GetWindowRect(hwnd)
                w = max(rect[2] - rect[0], 1)
                h = max(rect[3] - rect[1], 1)

                hwndDC = win32gui.GetWindowDC(hwnd)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
                saveDC.SelectObject(saveBitMap)

                # PW_RENDERFULLCONTENT = 2
                res = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
                if not res:
                    res = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                im = Image.frombuffer("RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), bmpstr, "raw", "BGRX", 0, 1)

                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)

                im.save(str(output_file))
                logger.info(f"Đã chụp ảnh cửa sổ qua PrintWindow lưu tại: {output_file}")
                return True
            except Exception as e:
                logger.debug(f"PrintWindow không thành công ({e}), chuyển sang phương thức dự phòng...")

        # 2. Phương thức dự phòng: ImageGrab
        try:
            from PIL import ImageGrab
            if self.window is not None:
                rect = self.window.rectangle()
                bbox = (rect.left, rect.top, rect.right, rect.bottom)
                screenshot = ImageGrab.grab(bbox=bbox)
            else:
                screenshot = ImageGrab.grab()
            screenshot.save(str(output_file))
            logger.info(f"Đã chụp ảnh màn hình lưu tại: {output_file}")
            return True
        except Exception as ex:
            logger.warning(f"Chụp ảnh màn hình qua ImageGrab thất bại: {ex}")
            # 3. Tạo một ảnh trắng có thông tin log nếu hệ thống không có display DC
            placeholder = Image.new("RGB", (1280, 720), color="#1E1E1E")
            placeholder.save(str(output_file))
            logger.info(f"Đã lưu ảnh thông tin trạng thái tại: {output_file}")
            return True

    @abc.abstractmethod
    def open_agent_panel(self) -> bool:
        """Mở hoặc kích hoạt (focus) trực tiếp vào ô nhập prompt của AI Agent."""
        pass

    @abc.abstractmethod
    def submit_prompt(self, prompt_text: str, image_path: Optional[Path] = None) -> bool:
        """Thực hiện nạp prompt văn bản (kèm ảnh thiết kế nếu có) vào ô nhập của Agent và nhấn gửi."""
        pass

    @abc.abstractmethod
    def is_agent_busy(self) -> bool:
        """Kiểm tra xem AI Agent trong IDE còn đang xử lý / sinh code hay không."""
        pass

    @abc.abstractmethod
    def accept_changes_if_any(self) -> bool:
        """Nếu IDE cần chấp nhận/lưu thay đổi file trên giao diện, tự động kích hoạt."""
        pass

    @abc.abstractmethod
    def close_ide(self) -> bool:
        """Đóng cửa sổ IDE an toàn."""
        pass
