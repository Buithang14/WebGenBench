import json
from pathlib import Path
from typing import Dict, Any, Optional

from config.logger import logger
from config.loader import load_scoring
from experiment.task_loader import load_task
from rendering.browser_renderer import BrowserRenderer
from metrics.html_validity import HTMLValidityMetric
from metrics.accessibility import AccessibilityMetric
from metrics.responsive import ResponsiveMetric
from metrics.design_similarity import DesignSimilarityMetric
from metrics.code_quality import CodeQualityMetric
from metrics.runtime_cleanliness import RuntimeCleanlinessMetric
from scoring.calculator import ScoreCalculator
from storage.db_manager import DBManager


class Evaluator:
    """Bộ điều phối toàn diện 6 module chấm điểm tự động cho một lần chạy benchmark."""

    def __init__(self, base_outputs_dir: Optional[Path] = None):
        self.base_outputs_dir = Path(base_outputs_dir) if base_outputs_dir else Path("outputs")
        self.scoring_config = load_scoring()
        self.metrics = [
            HTMLValidityMetric(),
            AccessibilityMetric(),
            ResponsiveMetric(),
            DesignSimilarityMetric(),
            CodeQualityMetric(),
            RuntimeCleanlinessMetric(),
        ]

    def evaluate_run(self, run_id: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Thực hiện đánh giá toàn diện 6 tiêu chí cho Run chỉ định."""
        run_dir = (self.base_outputs_dir / run_id).resolve()
        if not run_dir.exists():
            raise FileNotFoundError(f"Thư mục lần chạy không tồn tại: {run_dir}")

        # 1. Đọc task_id từ run_metadata.json nếu chưa có
        meta_file = run_dir / "run_metadata.json"
        task_meta = None
        if not task_id and meta_file.exists():
            try:
                run_meta = json.loads(meta_file.read_text(encoding="utf-8"))
                task_id = run_meta.get("task_id", "T01")
            except Exception:
                task_id = "T01"

        if task_id:
            try:
                task_data = load_task(task_id)
                task_meta = task_data.meta
            except Exception as e:
                logger.warning(f"Không thể nạp task {task_id}: {e}")

        # 2. Đảm bảo đã có ảnh render và render_report.json
        render_report_file = run_dir / "render_report.json"
        if not render_report_file.exists():
            logger.info(f"Chưa có render_report.json cho {run_id}, tiến hành kết xuất Playwright...")
            renderer = BrowserRenderer(base_outputs_dir=self.base_outputs_dir)
            renderer.render_run(run_id)

        # 3. Chạy lần lượt 6 metrics
        calculator = ScoreCalculator()
        weights = calculator.load_weights()

        metric_results: Dict[str, Any] = {}
        metric_raw_scores: Dict[str, float] = {}

        for metric in self.metrics:
            m_res = metric.evaluate(run_dir=run_dir, task_meta=task_meta)
            metric_raw_scores[metric.name] = m_res.score
            w = weights.get(metric.name, 0.0)
            contribution = round((m_res.score * w), 2)

            metric_results[metric.name] = {
                "score": m_res.score,
                "weight": w,
                "weighted_contribution": contribution,
                "raw_value": m_res.raw_value,
                "issues": m_res.issues,
            }
            logger.info(f"Metric [{metric.name:<19}]: {m_res.score:>5.1f}/100 (Trọng số: {w:.2f}) -> {contribution:>5.2f}đ")

        calc_result = calculator.calculate_weighted_score(metric_raw_scores, custom_weights=weights)
        total_weighted_score = calc_result["weighted_total_score"]

        evaluation_report = {
            "run_id": run_id,
            "task_id": task_id,
            "total_score": total_weighted_score,
            "weights": weights,
            "metrics": metric_results,
        }

        # Lưu báo cáo vào outputs/{run_id}/metrics_report.json
        output_report_file = run_dir / "metrics_report.json"
        with open(output_report_file, "w", encoding="utf-8") as f:
            json.dump(evaluation_report, f, indent=2, ensure_ascii=False)

        logger.success(f"Đã lưu kết quả chấm điểm tổng thể tại: {output_report_file}")

        # Tự động đồng bộ kết quả vào SQLite
        try:
            db_manager = DBManager()
            db_manager.init_db()
            db_manager.sync_run_from_disk(run_id=run_id, base_outputs_dir=self.base_outputs_dir)
            logger.info(f"Đã tự động đồng bộ kết quả chấm điểm [{run_id}] vào SQLite.")
        except Exception as e:
            logger.warning(f"Không thể đồng bộ điểm số vào SQLite: {e}")

        return evaluation_report


def evaluate_run(run_id: str, task_id: Optional[str] = None) -> Dict[str, Any]:
    """Hàm tiện ích đánh giá một lần chạy."""
    evaluator = Evaluator()
    return evaluator.evaluate_run(run_id=run_id, task_id=task_id)

