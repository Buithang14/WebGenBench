import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from automation.base_adapter import BaseIDEAdapter
from config.logger import logger


class CodeFileEventHandler(FileSystemEventHandler):
    """Lắng nghe các sự kiện tạo mới và chỉnh sửa tệp mã nguồn trong thư mục workspace."""

    def __init__(self):
        super().__init__()
        self.first_file_time: Optional[float] = None
        self.last_modified_time: float = time.time()
        self.detected_files: set[str] = set()

    def _is_valid_code_file(self, file_path_str: str) -> bool:
        path = Path(file_path_str)
        name = path.name
        if name.startswith(".") or name == ".gitkeep":
            return False
        return True

    def on_created(self, event: FileSystemEvent):
        if event.is_directory or not self._is_valid_code_file(event.src_path):
            return
        now = time.time()
        if self.first_file_time is None:
            self.first_file_time = now
        self.last_modified_time = now
        self.detected_files.add(Path(event.src_path).name)
        logger.info(f"[Watchdog] Phát hiện tệp mới: {Path(event.src_path).name}")

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory or not self._is_valid_code_file(event.src_path):
            return
        now = time.time()
        if self.first_file_time is None:
            self.first_file_time = now
        self.last_modified_time = now
        self.detected_files.add(Path(event.src_path).name)
        logger.debug(f"[Watchdog] Tệp thay đổi: {Path(event.src_path).name}")

    def on_moved(self, event: FileSystemEvent):
        if not event.is_directory and hasattr(event, "dest_path") and self._is_valid_code_file(event.dest_path):
            now = time.time()
            if self.first_file_time is None:
                self.first_file_time = now
            self.last_modified_time = now
            self.detected_files.add(Path(event.dest_path).name)
            logger.info(f"[Watchdog] Tệp đổi tên/di chuyển: {Path(event.dest_path).name}")


class CompletionDetector:
    """Bộ phát hiện AI hoàn thành sinh code dựa trên biến động hệ thống tệp và trạng thái IDE."""

    def __init__(self):
        pass

    @staticmethod
    def get_valid_files(workspace_dir: Path) -> List[Path]:
        """Lấy danh sách các tệp code hợp lệ (khác dotfiles và .gitkeep) trong thư mục."""
        if not workspace_dir.exists():
            return []
        files = []
        for p in workspace_dir.iterdir():
            if p.is_file() and not p.name.startswith(".") and p.name != ".gitkeep":
                files.append(p)
        return sorted(files, key=lambda x: x.name)

    def wait_for_completion(
        self,
        adapter: BaseIDEAdapter,
        workspace_dir: Path,
        timeout_seconds: int = 180,
        quiet_period_seconds: int = 10,
        poll_interval: float = 1.0,
    ) -> Dict[str, Any]:
        """Lắng nghe và chờ đến khi AI hoàn tất sinh mã nguồn trong workspace.
        
        Điều kiện hoàn thành:
        1. Có ít nhất 1 tệp code hợp lệ xuất hiện trong workspace_dir.
        2. Đã trôi qua quiet_period_seconds kể từ lần thay đổi tệp cuối cùng.
        3. adapter.is_agent_busy() trả về False (Agent đã ngừng sinh/suy luận).
        """
        workspace_dir = Path(workspace_dir).resolve()
        workspace_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Bắt đầu theo dõi hoàn thành sinh code tại: {workspace_dir} "
            f"(timeout={timeout_seconds}s, quiet_period={quiet_period_seconds}s)..."
        )

        start_time = time.time()
        handler = CodeFileEventHandler()
        observer = Observer()
        observer.schedule(handler, str(workspace_dir), recursive=False)
        observer.start()

        # Kiểm tra trước xem có sẵn tệp nào từ trước không
        initial_files = self.get_valid_files(workspace_dir)
        if initial_files:
            handler.first_file_time = time.time()
            handler.last_modified_time = time.time()
            for f in initial_files:
                handler.detected_files.add(f.name)

        try:
            while time.time() - start_time < timeout_seconds:
                time.sleep(poll_interval)
                now = time.time()
                elapsed = now - start_time

                current_files = self.get_valid_files(workspace_dir)
                has_files = len(current_files) > 0

                if has_files and handler.first_file_time is None:
                    handler.first_file_time = now
                    handler.last_modified_time = now

                time_since_last_change = now - handler.last_modified_time

                # Kiểm tra điều kiện (a) và (b)
                if has_files and time_since_last_change >= quiet_period_seconds:
                    logger.info(
                        f"Hệ thống tệp tĩnh lặng {time_since_last_change:.1f}s >= {quiet_period_seconds}s. "
                        f"Đang kiểm tra trạng thái IDE Agent..."
                    )
                    
                    # Kiểm tra điều kiện (c): Agent không còn bận
                    if not adapter.is_agent_busy():
                        total_duration = round(now - start_time, 2)
                        detected_names = [f.name for f in current_files]
                        logger.success(
                            f"Xác nhận AI đã hoàn thành nhiệm vụ! "
                            f"Thời gian: {total_duration}s. Số tệp: {len(detected_names)}: {detected_names}"
                        )
                        return {
                            "status": "SUCCESS",
                            "duration_seconds": total_duration,
                            "files_detected": detected_names,
                            "error_message": None,
                            "first_file_time": handler.first_file_time,
                            "last_modified_time": handler.last_modified_time,
                        }
                    else:
                        logger.info("Cursor Agent vẫn đang hiển thị trạng thái bận, tiếp tục chờ...")

            # Quá thời gian timeout
            total_duration = round(time.time() - start_time, 2)
            log_dir = Path(__file__).resolve().parent.parent / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            timeout_screenshot = log_dir / f"timeout_{int(time.time())}.png"
            adapter.capture_window_screenshot(timeout_screenshot)
            logger.error(f"Hết thời gian chờ {timeout_seconds}s! Đã chụp ảnh lỗi tại: {timeout_screenshot}")

            current_files = self.get_valid_files(workspace_dir)
            return {
                "status": "TIMEOUT",
                "duration_seconds": total_duration,
                "files_detected": [f.name for f in current_files],
                "error_message": f"Timeout {timeout_seconds}s exceeded waiting for AI completion.",
                "first_file_time": handler.first_file_time,
                "last_modified_time": handler.last_modified_time,
            }

        finally:
            observer.stop()
            observer.join(timeout=2.0)

