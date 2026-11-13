import time
import threading
from pathlib import Path
from unittest.mock import MagicMock

from automation.base_adapter import BaseIDEAdapter
from automation.completion_detector import CompletionDetector, CodeFileEventHandler


def test_code_file_event_handler_filtering(tmp_path: Path):
    handler = CodeFileEventHandler()
    assert handler._is_valid_code_file(str(tmp_path / "index.html")) is True
    assert handler._is_valid_code_file(str(tmp_path / "style.css")) is True
    assert handler._is_valid_code_file(str(tmp_path / ".gitkeep")) is False
    assert handler._is_valid_code_file(str(tmp_path / ".env")) is False
    assert handler._is_valid_code_file(str(tmp_path / ".cursorrules")) is False


def test_completion_detector_success(tmp_path: Path):
    detector = CompletionDetector()
    mock_adapter = MagicMock(spec=BaseIDEAdapter)
    mock_adapter.is_agent_busy.return_value = False

    def create_file_delayed():
        time.sleep(0.3)
        (tmp_path / "index.html").write_text("<h1>Test</h1>", encoding="utf-8")
        (tmp_path / "style.css").write_text("body {}", encoding="utf-8")

    t = threading.Thread(target=create_file_delayed)
    t.start()

    res = detector.wait_for_completion(
        adapter=mock_adapter,
        workspace_dir=tmp_path,
        timeout_seconds=5,
        quiet_period_seconds=1,
        poll_interval=0.2,
    )
    t.join()

    assert res["status"] == "SUCCESS"
    assert "index.html" in res["files_detected"]
    assert "style.css" in res["files_detected"]
    assert res["duration_seconds"] > 0
    assert res["error_message"] is None


def test_completion_detector_timeout(tmp_path: Path):
    detector = CompletionDetector()
    mock_adapter = MagicMock(spec=BaseIDEAdapter)
    mock_adapter.is_agent_busy.return_value = False
    mock_adapter.capture_window_screenshot.return_value = True

    # No files created in tmp_path
    res = detector.wait_for_completion(
        adapter=mock_adapter,
        workspace_dir=tmp_path,
        timeout_seconds=2,
        quiet_period_seconds=1,
        poll_interval=0.2,
    )

    assert res["status"] == "TIMEOUT"
    assert res["files_detected"] == []
    assert "Timeout" in res["error_message"]
    mock_adapter.capture_window_screenshot.assert_called_once()

