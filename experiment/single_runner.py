import time
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from config.logger import logger
from config.loader import load_settings
from experiment.task_loader import load_task
from automation.cursor.cursor_adapter import CursorAdapter
from automation.completion_detector import CompletionDetector
from collection.collector import ArtifactCollector


BASE_DIR = Path(__file__).resolve().parent.parent


def execute_single_run(
    ide_name: str,
    task_id: str,
    condition: str = "text_only",
    run_id: Optional[str] = None,
    timeout_seconds: int = 180,
    quiet_period_seconds: int = 10,
) -> Dict[str, Any]:
    """Thực hiện một Vertical Slice hoàn chỉnh:
    1. Nạp đề bài Task từ thư mục tasks/
    2. Chuẩn bị workspace/current_run sạch
    3. Mở IDE qua Adapter, focus và kích hoạt ô nhập
    4. Nạp prompt văn bản (kèm ảnh tham chiếu nếu condition == 'text_image')
    5. CompletionDetector chờ AI sinh xong toàn bộ file
    6. Kích hoạt accept_changes_if_any và đóng IDE an toàn
    7. ArtifactCollector thu thập toàn bộ sản phẩm vào outputs/{run_id}/
    """
    ide_name = ide_name.lower()
    start_time_iso = datetime.datetime.now().isoformat()
    start_ts = time.time()

    if not run_id:
        run_id = f"{ide_name}_{task_id}_{condition}_{int(start_ts)}"

    logger.info(f"========== BẮT ĐẦU VERTICAL SLICE RUN: [{run_id}] ==========")
    logger.info(f"IDE: {ide_name.upper()} | Task: {task_id} | Condition: {condition}")

    # 1. Nạp thông tin Task
    task_data = load_task(task_id)
    prompt_text = task_data.prompt_text
    image_path: Optional[Path] = None

    if condition == "text_image":
        ref_img = BASE_DIR / task_data.meta.reference_image
        if ref_img.exists():
            image_path = ref_img
            logger.info(f"Đã nạp ảnh thiết kế tham chiếu: {image_path}")
        else:
            logger.warning(f"Không tìm thấy ảnh tham chiếu tại: {ref_img}")

    # 2. Khởi tạo IDE Adapter
    if ide_name == "cursor":
        adapter = CursorAdapter()
    else:
        raise NotImplementedError(f"IDE '{ide_name}' chưa được hỗ trợ trong phiên bản hiện tại.")

    workspace_dir = (BASE_DIR / "workspace" / "current_run").resolve()
    adapter.prepare_workspace(workspace_dir)

    # Biến lưu kết quả hoàn thành
    completion_result: Dict[str, Any] = {
        "status": "FAILED",
        "duration_seconds": 0.0,
        "files_detected": [],
        "error_message": None,
    }

    try:
        # 3. Mở IDE và kết nối
        logger.info(f"Đang khởi chạy {ide_name.upper()}...")
        if not adapter.launch_ide(workspace_dir):
            raise RuntimeError(f"Khởi chạy {ide_name.upper()} thất bại!")

        if not adapter.connect_window(timeout=25):
            raise RuntimeError(f"Không thể kết nối tới cửa sổ {ide_name.upper()}!")

        adapter.focus_and_maximize()
        time.sleep(1.0)

        # 4. Gửi prompt
        logger.info("Đang nạp prompt vào AI Agent...")
        if not adapter.submit_prompt(prompt_text=prompt_text, image_path=image_path):
            raise RuntimeError("Gửi prompt tới Agent thất bại!")

        # 5. Bộ phát hiện hoàn thành (Completion Detector)
        logger.info("Kích hoạt Completion Detector...")
        detector = CompletionDetector()
        completion_result = detector.wait_for_completion(
            adapter=adapter,
            workspace_dir=workspace_dir,
            timeout_seconds=timeout_seconds,
            quiet_period_seconds=quiet_period_seconds,
        )

        # 6. Chấp nhận lưu thay đổi
        adapter.accept_changes_if_any()

    except Exception as e:
        logger.error(f"Lỗi trong quá trình thực thi: {e}")
        completion_result["status"] = "ERROR"
        completion_result["error_message"] = str(e)
    finally:
        # Đóng IDE an toàn
        adapter.close_ide()

    # 7. Thu thập artifacts
    collector = ArtifactCollector()
    total_duration = round(time.time() - start_ts, 2)
    meta = {
        "run_id": run_id,
        "ide": ide_name,
        "agent": f"{ide_name}_agent",
        "model": "auto",
        "task_id": task_id,
        "condition": condition,
        "start_time": start_time_iso,
        "duration_seconds": completion_result.get("duration_seconds", total_duration),
        "status": completion_result.get("status", "UNKNOWN"),
        "error_message": completion_result.get("error_message"),
        "prompt": prompt_text,
    }

    run_dir = collector.collect_run_artifacts(
        run_id=run_id,
        workspace_dir=workspace_dir,
        metadata=meta,
    )

    # 8. Tự động đồng bộ vào CSDL SQLite
    try:
        from storage.db_manager import DBManager
        db_manager = DBManager()
        db_manager.init_db()
        db_manager.sync_run_from_disk(run_id=run_id)
        logger.info(f"Đã tự động đồng bộ lượt chạy [{run_id}] vào CSDL SQLite.")
    except Exception as e:
        logger.warning(f"Không thể tự động đồng bộ [{run_id}] vào SQLite: {e}")

    logger.info(f"========== KẾT THÚC RUN: [{run_id}] - TRẠNG THÁI: {meta['status']} ==========")
    return meta

