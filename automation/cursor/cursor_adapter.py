import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional, List, Any
import pywinauto
import pyautogui
import win32gui
import win32con
import win32api

from automation.base_adapter import BaseIDEAdapter, ensure_interactive_desktop
from automation.clipboard_helper import copy_text_to_clipboard, copy_image_to_clipboard
from config.logger import logger
from config.loader import SettingsConfig


class CursorAdapter(BaseIDEAdapter):
    """IDE Adapter chuyên trách điều khiển phần mềm Cursor bằng GUI Automation."""

    def __init__(self, settings: Optional[SettingsConfig] = None):
        super().__init__(ide_name="cursor", settings=settings)

    def resolve_executable_path(self) -> Path:
        r"""Dò tìm đường dẫn file thực thi Cursor.exe chính trên Windows.
        
        Thứ tự ưu tiên:
        1. settings.yaml (có giải nén biến môi trường %LOCALAPPDATA%, %APPDATA%, ...)
        2. E:\kì 2 năm 4\NCKH\Cursor\cursor\Cursor.exe
        3. Shortcut trong Start Menu (.lnk) và Desktop (.lnk)
        4. %LOCALAPPDATA%\Programs\cursor\Cursor.exe
        5. %PROGRAMFILES%\Cursor\Cursor.exe
        6. Lệnh trong PATH (shutil.which('cursor'))
        """
        candidate_paths: List[Path] = []

        # 1. Từ file cấu hình settings.yaml
        if self.settings and self.settings.executables.cursor:
            raw_path = self.settings.executables.cursor
            expanded = os.path.expandvars(raw_path)
            candidate_paths.append(Path(expanded))

        # 2. Vị trí cài đặt chính thức của Cursor Editor trên máy
        candidate_paths.append(Path(r"E:\kì 2 năm 4\NCKH\Cursor\cursor\Cursor.exe"))

        # 3. Thử đọc từ Shortcut Desktop và Start Menu
        shortcut_dirs = [
            Path(os.environ.get("USERPROFILE", "")) / "Desktop",
            Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            Path(os.environ.get("ProgramData", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        ]
        for s_dir in shortcut_dirs:
            if s_dir.is_dir():
                for lnk in s_dir.rglob("*cursor*.lnk"):
                    try:
                        import win32com.client
                        shell = win32com.client.Dispatch("WScript.Shell")
                        shortcut = shell.CreateShortcut(str(lnk))
                        if shortcut.TargetPath and shortcut.TargetPath.lower().endswith("cursor.exe"):
                            candidate_paths.append(Path(shortcut.TargetPath))
                    except Exception:
                        pass

        # 4. Vị trí Local AppData thông dụng của Windows
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            candidate_paths.append(Path(local_app_data) / "Programs" / "cursor" / "Cursor.exe")

        # 5. Vị trí Program Files
        prog_files = os.environ.get("ProgramFiles", "")
        if prog_files:
            candidate_paths.append(Path(prog_files) / "Cursor" / "Cursor.exe")

        prog_files_x86 = os.environ.get("ProgramFiles(x86)", "")
        if prog_files_x86:
            candidate_paths.append(Path(prog_files_x86) / "Cursor" / "Cursor.exe")

        # 6. Tìm trong biến môi trường PATH
        which_path = shutil.which("cursor")
        if which_path:
            candidate_paths.append(Path(which_path))

        # Duyệt kiểm tra đường dẫn thực tế tồn tại
        for path in candidate_paths:
            try:
                if path and path.is_file():
                    self.executable_path = path.resolve()
                    logger.info(f"Đã tìm thấy Cursor tại: {self.executable_path}")
                    return self.executable_path
            except Exception:
                continue

        # Nếu không tìm thấy
        searched_locations = "\n - " + "\n - ".join(str(p) for p in candidate_paths)
        raise FileNotFoundError(
            f"Không tìm thấy file thực thi 'Cursor.exe' trên máy tính Windows. Đã tìm tại:{searched_locations}"
        )

    def launch_ide(self, workspace_dir: Path) -> bool:
        """Khởi chạy Cursor mở trực tiếp thư mục workspace_dir."""
        ensure_interactive_desktop()
        exe = self.resolve_executable_path()
        resolved_workspace = Path(workspace_dir).resolve()
        cmd = [
            str(exe),
            "--classic",
            "--new-window",
            "--force-renderer-accessibility",
            str(resolved_workspace),
        ]

        # Chuẩn bị môi trường sạch: Loại bỏ ELECTRON_RUN_AS_NODE để Electron chạy ở chế độ GUI app đầy đủ
        clean_env = os.environ.copy()
        clean_env.pop("ELECTRON_RUN_AS_NODE", None)
        clean_env.pop("VSCODE_DEV", None)

        # Định tuyến hiển thị lên Desktop tương tác của người dùng
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.lpDesktop = r"WinSta0\Default"

        cwd = str(exe.parent)
        logger.info(f"Đang khởi chạy Cursor: {' '.join(cmd)}")
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=cwd,
                env=clean_env,
                startupinfo=startupinfo,
            )
            self.workspace_dir = resolved_workspace
            logger.info(f"Đã kích hoạt tiến trình Cursor (PID: {self.process.pid})")
            return True
        except Exception as e:
            logger.error(f"Khởi chạy Cursor thất bại: {e}")
            return False

    def connect_window(self, timeout: int = 25) -> bool:
        """Tìm và kết nối tới cửa sổ Code Editor chính của Cursor chứa workspace_dir."""
        ensure_interactive_desktop()
        logger.info(f"Đang dò tìm cửa sổ Cursor Editor (timeout={timeout}s)...")
        start_time = time.time()
        folder_name = self.workspace_dir.name if self.workspace_dir else "current_run"

        best_window = None

        while time.time() - start_time < timeout:
            ensure_interactive_desktop()

            # 1. Quét qua pywinauto Desktop (UIA)
            try:
                desktop = pywinauto.Desktop(backend="uia")
                for win in desktop.windows():
                    try:
                        title = win.window_text() or ""
                        if win.is_visible():
                            rect = win.rectangle()
                            # Cửa sổ Editor chính luôn có kích thước lớn (> 600x400)
                            if rect.width() > 600 and rect.height() > 400:
                                # Ưu tiên tuyệt đối: Cửa sổ có chứa tên thư mục workspace 'current_run'
                                if folder_name.lower() in title.lower():
                                    self.window = win
                                    logger.info(f"Đã kết nối thành công tới cửa sổ Editor chính: '{title}' (Handle: {win.handle})")
                                    return True
                                # Ưu tiên dự phòng: Cửa sổ có tiêu đề Cursor
                                elif "cursor" in title.lower():
                                    best_window = win
                    except Exception:
                        continue
            except Exception as e:
                logger.debug(f"Đang tìm kiếm cửa sổ qua Desktop UIA... ({e})")

            # 2. Fallback qua win32gui EnumWindows
            try:
                import win32gui
                hwnds: List[int] = []
                win32gui.EnumWindows(lambda h, extra: (hwnds.append(h), True)[1], None)
                for h in hwnds:
                    try:
                        if win32gui.IsWindowVisible(h):
                            t = win32gui.GetWindowText(h)
                            c = win32gui.GetClassName(h)
                            if "chrome_widgetwin" in c.lower():
                                rect = win32gui.GetWindowRect(h)
                                if (rect[2] - rect[0]) > 600 and (rect[3] - rect[1]) > 400:
                                    if folder_name.lower() in t.lower():
                                        app = pywinauto.Application(backend="uia").connect(handle=h)
                                        self.window = app.window(handle=h)
                                        logger.info(f"Đã kết nối thành công tới cửa sổ Editor qua HWND {h}: '{t}'")
                                        return True
                                    elif "cursor" in t.lower() and best_window is None:
                                        app = pywinauto.Application(backend="uia").connect(handle=h)
                                        best_window = app.window(handle=h)
                    except Exception:
                        continue
            except Exception:
                pass

            time.sleep(1.0)

        # Nếu hết timeout mà tìm thấy cửa sổ Cursor (dù tiêu đề chưa kịp cập nhật current_run)
        if best_window is not None:
            self.window = best_window
            logger.info(f"Đã kết nối tới cửa sổ Cursor: '{best_window.window_text()}' (Handle: {best_window.handle})")
            return True

        logger.error(f"Hết thời gian {timeout}s: Không tìm thấy cửa sổ Cursor.")
        return False

    def focus_and_maximize(self) -> bool:
        """Khôi phục, đưa cửa sổ lên tiền cảnh (foreground), phóng to và chụp ảnh xác nhận."""
        ensure_interactive_desktop()
        if self.window is None:
            logger.error("Chưa kết nối tới cửa sổ Cursor nào để focus!")
            return False

        try:
            # 1. Khôi phục nếu bị minimized
            try:
                self.window.restore()
            except Exception:
                pass

            # 2. Đưa lên tiền cảnh và set focus
            try:
                self.window.set_focus()
            except Exception:
                pass
            time.sleep(0.5)

            # 3. Phóng to cửa sổ
            try:
                self.window.maximize()
            except Exception as e:
                logger.warning(f"Không thể maximize qua UIA ({e}), giữ kích thước hiện tại.")

            # Chờ thêm 1.5 giây để giao diện Electron hoàn tất vẽ các thanh công cụ/editor
            time.sleep(1.5)

            # 4. Chụp ảnh màn hình xác nhận
            log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
            screenshot_path = log_dir / "cursor_launched.png"
            self.capture_window_screenshot(screenshot_path)

            logger.info("Đã focus, phóng to cửa sổ Cursor và chụp ảnh xác nhận thành công.")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi focus/maximize cửa sổ Cursor: {e}")
            return False

    def _get_target_render_hwnd(self) -> int:
        """Tìm child window Chrome_RenderWidgetHostHWND nhận input của Cursor."""
        h = self.window.handle
        children: List[int] = []
        try:
            win32gui.EnumChildWindows(h, lambda hwnd, extra: (children.append(hwnd), True)[1], None)
            for c in children:
                if "renderwidget" in win32gui.GetClassName(c).lower():
                    return c
        except Exception:
            pass
        return h

    def open_agent_panel(self) -> bool:
        """Kích hoạt và đưa con trỏ chuột/focus trực tiếp vào ô nhập prompt của Cursor Agent."""
        ensure_interactive_desktop()
        if self.window is None:
            logger.error("Chưa kết nối tới cửa sổ Cursor để mở Agent panel!")
            return False

        logger.info("Đang định vị và kích hoạt ô nhập prompt của Cursor Agent...")
        try:
            self.window.set_focus()
            time.sleep(0.5)

            h = self.window.handle
            target_hwnd = self._get_target_render_hwnd()
            title = self.window.window_text() or ""
            rect = win32gui.GetWindowRect(h)
            w = max(rect[2] - rect[0], 1)
            h_len = max(rect[3] - rect[1], 1)

            # Phân biệt 2 chế độ: Agent Canvas (Cursor Agents) hoặc Classic VS Code Editor
            if "agent" in title.lower() and "current_run" not in title.lower():
                rel_x = int(w * 0.38)
                rel_y = int(h_len * 0.52)
            else:
                # Classic Editor mode:
                # Nhấp nút '+' (New Agent) ở header panel chat để luôn mở phiên chat sạch mới
                plus_x = int(w * 0.956)
                plus_y = 70
                lParam_plus = (plus_y << 16) | (plus_x & 0xFFFF)
                win32gui.PostMessage(target_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam_plus)
                time.sleep(0.05)
                win32gui.PostMessage(target_hwnd, win32con.WM_LBUTTONUP, 0, lParam_plus)
                time.sleep(0.5)

                rel_x = int(w * 0.87)
                rel_y = int(h_len * 0.18)

            # 1. Click vào ô nhập liệu qua PostMessage
            lParam = (rel_y << 16) | (rel_x & 0xFFFF)
            win32gui.PostMessage(target_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
            time.sleep(0.05)
            win32gui.PostMessage(target_hwnd, win32con.WM_LBUTTONUP, 0, lParam)
            time.sleep(0.3)

            # 2. Dự phòng: Gửi phím tắt mở Agent panel (Ctrl+Shift+L / Ctrl+L)
            try:
                self.window.type_keys("^+l")
            except Exception:
                pass

            logger.info("Đã focus thành công vào ô nhập prompt của Cursor Agent.")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi mở Agent panel: {e}")
            return False

    def submit_prompt(self, prompt_text: str, image_path: Optional[Path] = None) -> bool:
        """Dán văn bản prompt (kèm ảnh thiết kế nếu có) vào ô nhập của Cursor Agent và nhấn gửi."""
        ensure_interactive_desktop()
        if self.window is None:
            logger.error("Chưa kết nối tới cửa sổ Cursor để submit prompt!")
            return False

        log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
        h = self.window.handle
        target_hwnd = self._get_target_render_hwnd()
        title = self.window.window_text() or ""
        rect = win32gui.GetWindowRect(h)
        w = max(rect[2] - rect[0], 1)
        h_len = max(rect[3] - rect[1], 1)

        # 1. Đảm bảo ô nhập đã được focus
        if not self.open_agent_panel():
            logger.error("Không thể focus vào ô nhập prompt.")
            return False

        time.sleep(0.5)

        # 2. Xóa sạch nội dung cũ trong ô nhập (Ctrl+A -> Backspace x 30)
        try:
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('A'), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_BACK, 0, 0, 0)
            win32api.keybd_event(win32con.VK_BACK, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception:
            pass

        for _ in range(30):
            win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, win32con.VK_BACK, 0)
            win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, win32con.VK_BACK, 0)
        time.sleep(0.2)

        # 3. Nếu có ảnh đính kèm: Nạp ảnh vào clipboard và gửi lệnh dán (Ctrl+V)
        if image_path is not None and image_path.exists():
            logger.info(f"Đang đính kèm ảnh thiết kế: {image_path.name}...")
            if copy_image_to_clipboard(image_path):
                time.sleep(0.3)
                try:
                    scan_ctrl = win32api.MapVirtualKey(win32con.VK_CONTROL, 0)
                    scan_v = win32api.MapVirtualKey(0x56, 0)
                    win32api.keybd_event(win32con.VK_CONTROL, scan_ctrl, 0, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(0x56, scan_v, 0, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(0x56, scan_v, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(win32con.VK_CONTROL, scan_ctrl, win32con.KEYEVENTF_KEYUP, 0)
                except Exception:
                    try:
                        self.window.type_keys("^v")
                    except Exception:
                        pass
                
                # Chờ 1.5 giây để Cursor hiển thị thumbnail ảnh đính kèm
                logger.info("Chờ 1.5s để Cursor nạp thumbnail ảnh đính kèm...")
                time.sleep(1.5)
            else:
                logger.warning(f"Không thể sao chép ảnh {image_path} vào clipboard.")

        # 4. Nạp nội dung prompt văn bản vào clipboard và nhập vào ô
        logger.info(f"Đang nạp prompt văn bản ({len(prompt_text)} ký tự) vào ô nhập...")
        copy_text_to_clipboard(prompt_text)
        time.sleep(0.2)

        # Gửi ký tự Unicode trực tiếp qua WM_CHAR để đảm bảo độ tin cậy tuyệt đối 100% không mất chữ
        for ch in prompt_text:
            win32gui.PostMessage(target_hwnd, win32con.WM_CHAR, ord(ch), 0)
            time.sleep(0.005)

        # Chờ 1.5 giây để giao diện cập nhật nội dung văn bản
        time.sleep(1.5)

        # 5. Chụp ảnh màn hình trước khi gửi: logs/cursor_before_send.png
        before_file = log_dir / "cursor_before_send.png"
        self.capture_window_screenshot(before_file)
        logger.info(f"Đã chụp ảnh trước khi gửi lưu tại: {before_file}")

        # 6. Gửi lệnh: Click nút Submit (mũi tên lên) và gửi phím Enter
        logger.info("Đang gửi lệnh (Submit / Enter) cho Cursor Agent...")
        if "agent" in title.lower() and "current_run" not in title.lower():
            # Chế độ Canvas trung tâm
            submit_coords = [(int(w * 0.54), int(h_len * 0.56))]
        else:
            # Chế độ Classic Editor: Thử cả vị trí nút submit ở khung trên và khung dưới (nếu đã có lịch sử chat)
            submit_coords = [
                (int(w * 0.972), int(h_len * 0.887)),
                (int(w * 0.972), int(h_len * 0.920)),
                (int(w * 0.970), int(h_len * 0.250)),
            ]

        for s_x, s_y in submit_coords:
            lParam_s = (s_y << 16) | (s_x & 0xFFFF)
            win32gui.PostMessage(target_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam_s)
            time.sleep(0.05)
            win32gui.PostMessage(target_hwnd, win32con.WM_LBUTTONUP, 0, lParam_s)
            time.sleep(0.1)

        win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
        try:
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception:
            pass

        # 7. Chờ 3.0 giây để Cursor Agent chuyển sang trạng thái xử lý/sinh code
        logger.info("Chờ 3.0s để Cursor Agent bắt đầu sinh code...")
        time.sleep(3.0)

        # 8. Chụp ảnh màn hình sau khi gửi: logs/cursor_prompt_submitted.png
        after_file = log_dir / "cursor_prompt_submitted.png"
        self.capture_window_screenshot(after_file)
        logger.info(f"Đã chụp ảnh sau khi gửi lệnh lưu tại: {after_file}")

        logger.success("Đã hoàn tất submit prompt thành công cho Cursor Agent!")
        return True

    def is_agent_busy(self) -> bool:
        """Kiểm tra xem Cursor Agent còn đang bận xử lý/sinh code hay không."""
        ensure_interactive_desktop()
        if self.window is None:
            return False

        try:
            import tempfile
            from PIL import Image, ImageChops, ImageStat
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f1, \
                 tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f2:
                p1, p2 = Path(f1.name), Path(f2.name)

            self.capture_window_screenshot(p1)
            time.sleep(1.2)
            self.capture_window_screenshot(p2)

            im1 = Image.open(p1).convert("RGB")
            im2 = Image.open(p2).convert("RGB")

            p1.unlink(missing_ok=True)
            p2.unlink(missing_ok=True)

            w, h = im1.size
            crop_box = (int(w * 0.70), 0, w, h)
            chat1 = im1.crop(crop_box)
            chat2 = im2.crop(crop_box)

            diff = ImageChops.difference(chat1, chat2)
            stat = ImageStat.Stat(diff)
            rms = sum(stat.rms) / max(len(stat.rms), 1)

            is_busy = rms > 0.8
            logger.debug(f"Cursor is_agent_busy: visual RMS diff = {rms:.3f} -> busy = {is_busy}")
            return is_busy
        except Exception as e:
            logger.warning(f"Lỗi khi kiểm tra Cursor is_agent_busy: {e}")
            return False

    def accept_changes_if_any(self) -> bool:
        """Kích hoạt lưu toàn bộ file (Ctrl+S / Ctrl+K, S) và chấp nhận thay đổi nếu có."""
        ensure_interactive_desktop()
        if self.window is None:
            return False

        logger.info("Đang kiểm tra và chấp nhận (accept/save) các thay đổi file trong Cursor...")
        try:
            # 1. Gửi phím tắt Save All (Ctrl+S)
            try:
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(ord('S'), 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(ord('S'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            except Exception:
                pass

            time.sleep(0.3)
            # 2. Thử gửi phím tắt Accept All của Cursor (Ctrl+Enter)
            try:
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            except Exception:
                pass

            time.sleep(0.5)
            logger.info("Đã gửi tín hiệu lưu/accept file thành công.")
            return True
        except Exception as e:
            logger.warning(f"Lỗi khi accept_changes: {e}")
            return False

    def dump_ui_tree(self, output_file: Path, max_depth: int = 4, max_elements: int = 250) -> bool:
        """Dò cây UI Automation của Cursor và ghi ra file text với mã hóa UTF-8."""
        ensure_interactive_desktop()
        if self.window is None:
            logger.error("Chưa kết nối tới cửa sổ Cursor để dump cây UI!")
            return False

        output_file.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Bắt đầu dò cây giao diện UI của Cursor (max_depth={max_depth})...")

        lines: List[str] = []
        lines.append(f"UI AUTOMATION TREE DUMP - CURSOR")
        try:
            lines.append(f"Window Title: {self.window.window_text()}")
            lines.append(f"Handle: {self.window.handle}")
        except Exception:
            pass
        lines.append("=" * 80)
        lines.append(f"{'Depth':<6} | {'ControlType':<20} | {'AutomationId':<25} | {'Name'}")
        lines.append("-" * 80)

        count = [0]

        def _traverse(element, depth: int):
            if depth > max_depth or count[0] >= max_elements:
                return

            try:
                c_type = element.element_info.control_type or "Unknown"
                name = (element.element_info.name or "").strip().replace("\n", " ")
                auto_id = element.element_info.automation_id or ""
                indent = "  " * depth

                line = f"{depth:<6} | {indent + c_type:<20} | {auto_id[:24]:<25} | {name[:40]}"
                lines.append(line)
                count[0] += 1

                for child in element.children():
                    _traverse(child, depth + 1)
            except Exception:
                pass

        try:
            _traverse(self.window, 0)
            lines.append("=" * 80)
            lines.append(f"Tổng số phần tử đã dò: {count[0]}")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            logger.info(f"Đã xuất cây UI ({count[0]} phần tử) vào: {output_file}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi dump cây UI: {e}")
            return False

    def close_ide(self, timeout: float = 5.0) -> bool:
        """Đóng an toàn cửa sổ Cursor vừa mở."""
        ensure_interactive_desktop()
        logger.info("Đang đóng cửa sổ Cursor an toàn...")
        closed = False

        if self.window is not None:
            try:
                self.window.close()
                closed = True
                time.sleep(1.0)
            except Exception as e:
                logger.warning(f"Không thể close() qua window handle ({e}), thử đóng qua process...")

        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait(timeout=timeout)
                closed = True
                logger.info("Tiến trình Cursor đã kết thúc.")
            except Exception:
                try:
                    self.process.kill()
                    closed = True
                except Exception:
                    pass

        self.window = None
        self.process = None
        return closed
