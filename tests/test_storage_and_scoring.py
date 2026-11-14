"""tests/test_storage_and_scoring.py
Kiểm thử toàn diện cho Milestone 8 (Storage Module / SQLite)
và Milestone 9 (Dynamic Scoring Module / CLI recalculate).
"""

import json
import shutil
from pathlib import Path
import pytest
from sqlalchemy import inspect

from storage.models import Base
from storage.db_manager import DBManager
from scoring.calculator import ScoreCalculator


def test_db_initialization(tmp_path: Path):
    """Kiểm tra khởi tạo CSDL SQLite và sự tồn tại của đầy đủ 7 bảng."""
    test_db = tmp_path / "test_init.db"
    db_mgr = DBManager(db_path=test_db)
    db_mgr.init_db()

    assert test_db.exists(), "File database SQLite phải được tạo ra."

    inspector = inspect(db_mgr.engine)
    table_names = inspector.get_table_names()

    expected_tables = {
        "experiments",
        "tasks",
        "runs",
        "generated_projects",
        "screenshots",
        "automatic_metrics",
        "scores",
        "human_ratings",
    }
    assert expected_tables.issubset(set(table_names)), f"Thiếu bảng trong CSDL: {expected_tables - set(table_names)}"


def test_sync_and_full_trace_run_001(tmp_path: Path):
    """Kiểm tra đồng bộ dữ liệu thật của run_001 từ đĩa vào SQLite và truy vết hồ sơ từ A-Z."""
    test_db = tmp_path / "test_trace.db"
    db_mgr = DBManager(db_path=test_db)
    db_mgr.init_db()

    # Đồng bộ run_001 sẵn có trên đĩa
    sync_res = db_mgr.sync_run_from_disk(run_id="run_001")
    assert sync_res["status"] == "SYNCED"

    # Truy vết ngược toàn bộ dữ liệu
    trace = db_mgr.get_run_full_trace(run_id="run_001")
    assert trace is not None

    # 1. Kiểm tra Run
    run_info = trace["run"]
    assert run_info["id"] == "run_001"
    assert run_info["ide_name"] == "cursor"
    assert run_info["task_id"] == "T01"
    assert run_info["prompt_condition"] == "text_only"
    assert run_info["status"] == "SUCCESS"
    assert run_info["blind_code"] is not None

    # 2. Kiểm tra Project
    proj = trace["project"]
    assert proj["file_count"] == 3
    assert proj["total_lines_of_code"] == 566
    assert "index.html" in proj["files"]

    # 3. Kiểm tra Screenshots
    screenshots = trace["screenshots"]
    assert len(screenshots) == 3
    viewports = {sc["viewport_width"] for sc in screenshots}
    assert viewports == {375, 768, 1440}

    # 4. Kiểm tra Automatic Metrics
    metrics = trace["automatic_metrics"]
    assert len(metrics) == 6
    assert "html_validity" in metrics
    assert "accessibility" in metrics
    assert "responsive" in metrics
    assert "design_similarity" in metrics
    assert "code_quality" in metrics
    assert "runtime_cleanliness" in metrics

    # 5. Kiểm tra Score
    score = trace["score"]
    assert score["weighted_total_score"] == pytest.approx(91.94, abs=0.1)


def test_dynamic_recalculation_with_custom_weights(tmp_path: Path):
    """Kiểm thử tính năng tính lại điểm động khi cấu hình trọng số thay đổi

    mà KHÔNG cần chạy lại IDE hay Playwright.
    """
    test_db = tmp_path / "test_recalc.db"
    test_outputs = tmp_path / "outputs"
    test_outputs.mkdir(parents=True)

    # Copy dữ liệu run_001 sang thư mục tạm để kiểm thử ghi file metrics_report.json
    real_run_dir = Path("outputs") / "run_001"
    if real_run_dir.exists():
        shutil.copytree(real_run_dir, test_outputs / "run_001")

    db_mgr = DBManager(db_path=test_db)
    db_mgr.init_db()
    db_mgr.sync_run_from_disk(run_id="run_001", base_outputs_dir=test_outputs)

    # Ban đầu với trọng số mặc định (html_validity: 0.15, design_similarity: 0.25):
    trace_before = db_mgr.get_run_full_trace("run_001")
    assert trace_before["score"]["weighted_total_score"] == pytest.approx(91.94, abs=0.1)

    # Tạo file scoring.yaml mới với trọng số thay đổi:
    # Chuyển 0.05 từ html_validity sang design_similarity
    custom_scoring_file = tmp_path / "custom_scoring.yaml"
    custom_weights_content = """weights:
  html_validity: 0.10
  accessibility: 0.20
  responsive: 0.20
  design_similarity: 0.30
  code_quality: 0.10
  runtime_cleanliness: 0.10
"""
    custom_scoring_file.write_text(custom_weights_content, encoding="utf-8")

    calculator = ScoreCalculator(config_path=custom_scoring_file)
    new_weights = calculator.load_weights()
    assert new_weights["html_validity"] == 0.10
    assert new_weights["design_similarity"] == 0.30

    # Tính toán kỳ vọng toán học:
    # HTML Validity: 100 * 0.10 = 10.00
    # Accessibility: 87.0 * 0.20 = 17.40
    # Responsive: 95.0 * 0.20 = 19.00
    # Design Similarity: 88.15 * 0.30 = 26.445
    # Code Quality: 85.0 * 0.10 = 8.50
    # Runtime Cleanliness: 100.0 * 0.10 = 10.00
    # Tổng kỳ vọng: 10 + 17.40 + 19.00 + 26.445 + 8.50 + 10.00 = 91.345 -> 91.35
    expected_score = round(10.00 + 17.40 + 19.00 + 26.445 + 8.50 + 10.00, 2)

    # Chạy recalculate_all_scores
    updated_runs = calculator.recalculate_all_scores(db_manager=db_mgr, base_outputs_dir=test_outputs)
    assert updated_runs == 1

    # Kiểm tra điểm số trong CSDL SQLite
    trace_after = db_mgr.get_run_full_trace("run_001")
    updated_score = trace_after["score"]["weighted_total_score"]
    assert updated_score == pytest.approx(expected_score, abs=0.05)
    assert trace_after["score"]["weights_snapshot"]["design_similarity"] == 0.30

    # Kiểm tra file metrics_report.json cũng được cập nhật đồng bộ
    updated_report = json.loads((test_outputs / "run_001" / "metrics_report.json").read_text(encoding="utf-8"))
    assert updated_report["total_score"] == pytest.approx(expected_score, abs=0.05)
    assert updated_report["weights"]["design_similarity"] == 0.30


def test_list_all_runs(tmp_path: Path):
    """Kiểm tra hàm list_all_runs trả về danh sách tóm tắt."""
    test_db = tmp_path / "test_list.db"
    db_mgr = DBManager(db_path=test_db)
    db_mgr.init_db()
    db_mgr.sync_run_from_disk(run_id="run_001")

    all_runs = db_mgr.list_all_runs()
    assert len(all_runs) >= 1
    run_entry = all_runs[0]
    assert run_entry["run_id"] == "run_001"
    assert run_entry["ide_name"] == "cursor"
    assert run_entry["task_id"] == "T01"
    assert run_entry["weighted_total_score"] is not None


def test_task_sync_and_crud(tmp_path: Path):
    """Kiểm tra đồng bộ bài tập từ thư mục tasks/ vào SQLite và lưu bài tập mới."""
    test_db = tmp_path / "test_tasks.db"
    db_mgr = DBManager(db_path=test_db)
    db_mgr.init_db(auto_sync_tasks=True)

    # 1. Kiểm tra auto sync tasks
    tasks = db_mgr.list_all_tasks()
    assert len(tasks) >= 1
    task_ids = [t["task_id"] for t in tasks]
    assert "T01" in task_ids

    # 2. Kiểm tra get_task
    t01 = db_mgr.get_task("T01")
    assert t01 is not None
    assert t01["name"] == "Login Form"
    assert len(t01["ui_requirements"]) > 0
    assert len(t01["technical_requirements"]) > 0

    # 3. Kiểm tra save_task
    save_res = db_mgr.save_task(
        task_id="T99",
        name="Test Task",
        title_vi="Bài tập kiểm thử",
        prompt_text="Tạo giao diện kiểm thử...",
        ui_requirements=["UI 1", "UI 2"],
        technical_requirements=["Tech 1"],
        sync_to_disk=False,
    )
    assert save_res["status"] == "SAVED"
    t99 = db_mgr.get_task("T99")
    assert t99 is not None
    assert t99["title_vi"] == "Bài tập kiểm thử"

