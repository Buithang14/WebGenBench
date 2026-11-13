"""scoring/calculator.py
Bộ tính điểm tổng hợp động (ScoreCalculator) cho WebGenBench.
Tự động nạp trọng số từ config/scoring.yaml, tính điểm đóng góp từng phần,
và hỗ trợ tính lại (recalculate) toàn bộ điểm số trong CSDL SQLite và file báo cáo khi trọng số thay đổi.
"""

import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import yaml
from config.logger import logger
from storage.db_manager import DBManager
from storage.models import Run, AutomaticMetric, Score

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SCORING_CONFIG = BASE_DIR / "config" / "scoring.yaml"


class ScoreCalculator:
    """Bộ tính điểm định lượng tổng hợp dựa trên trọng số cấu hình động."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = Path(config_path) if config_path else DEFAULT_SCORING_CONFIG

    def load_weights(self) -> Dict[str, float]:
        """Nạp trọng số mới nhất từ file cấu hình YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file cấu hình trọng số: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        weights = data.get("weights", {})
        total_w = sum(weights.values())
        if abs(total_w - 1.0) > 1e-4:
            logger.warning(f"Tổng trọng số không bằng 1.0 (Hiện tại: {total_w:.4f}). Vui lòng kiểm tra config/scoring.yaml!")

        return {k: float(v) for k, v in weights.items()}

    def calculate_weighted_score(
        self,
        metric_scores: Dict[str, float],
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Tính điểm đóng góp từng phần và điểm tổng hợp chuẩn hoá (0 - 100)."""
        weights = custom_weights if custom_weights is not None else self.load_weights()

        contributions: Dict[str, float] = {}
        total_score = 0.0

        for metric_name, w in weights.items():
            sc = float(metric_scores.get(metric_name, 0.0))
            cb = round(sc * w, 2)
            contributions[metric_name] = cb
            total_score += sc * w

        total_score = min(max(round(total_score, 2), 0.0), 100.0)

        return {
            "weights": weights,
            "contributions": contributions,
            "weighted_total_score": total_score,
        }

    def recalculate_all_scores(
        self,
        db_manager: DBManager,
        base_outputs_dir: Optional[Path] = None,
    ) -> int:
        """Đọc lại toàn bộ điểm thô 6 tiêu chí từ SQLite, áp dụng trọng số mới nhất,

        cập nhật bảng scores và file metrics_report.json tương ứng mà không cần chạy lại IDE.
        """
        weights = self.load_weights()
        outputs_dir = Path(base_outputs_dir) if base_outputs_dir else (BASE_DIR / "outputs")
        updated_count = 0

        with db_manager.get_session() as session:
            runs = session.query(Run).all()
            for r in runs:
                # Thu thập điểm gốc từ bảng automatic_metrics
                auto_metrics = session.query(AutomaticMetric).filter(AutomaticMetric.run_id == r.id).all()
                if not auto_metrics:
                    continue

                metric_scores = {am.metric_name: am.raw_score for am in auto_metrics}
                calc_result = self.calculate_weighted_score(metric_scores, custom_weights=weights)
                new_total = calc_result["weighted_total_score"]
                contributions = calc_result["contributions"]

                # Cập nhật hoặc tạo mới bản ghi Score trong DB
                score_obj = session.query(Score).filter(Score.run_id == r.id).first()
                if not score_obj:
                    score_obj = Score(
                        run_id=r.id,
                        html_validity_score=metric_scores.get("html_validity", 0.0),
                        accessibility_score=metric_scores.get("accessibility", 0.0),
                        responsive_score=metric_scores.get("responsive", 0.0),
                        design_similarity_score=metric_scores.get("design_similarity", 0.0),
                        code_quality_score=metric_scores.get("code_quality", 0.0),
                        runtime_cleanliness_score=metric_scores.get("runtime_cleanliness", 0.0),
                        weighted_total_score=new_total,
                        weights_snapshot_json=json.dumps(weights, ensure_ascii=False),
                        updated_at=datetime.datetime.now(),
                    )
                    session.add(score_obj)
                else:
                    score_obj.html_validity_score = metric_scores.get("html_validity", 0.0)
                    score_obj.accessibility_score = metric_scores.get("accessibility", 0.0)
                    score_obj.responsive_score = metric_scores.get("responsive", 0.0)
                    score_obj.design_similarity_score = metric_scores.get("design_similarity", 0.0)
                    score_obj.code_quality_score = metric_scores.get("code_quality", 0.0)
                    score_obj.runtime_cleanliness_score = metric_scores.get("runtime_cleanliness", 0.0)
                    score_obj.weighted_total_score = new_total
                    score_obj.weights_snapshot_json = json.dumps(weights, ensure_ascii=False)
                    score_obj.updated_at = datetime.datetime.now()

                # Đồng bộ cập nhật file metrics_report.json trên ổ đĩa nếu tồn tại
                report_file = outputs_dir / r.id / "metrics_report.json"
                if report_file.exists():
                    try:
                        report_data = json.loads(report_file.read_text(encoding="utf-8"))
                        report_data["total_score"] = new_total
                        report_data["weights"] = weights
                        for m_key, m_val in report_data.get("metrics", {}).items():
                            if m_key in weights:
                                m_val["weight"] = weights[m_key]
                                m_val["weighted_contribution"] = contributions.get(m_key, round(m_val.get("score", 0.0) * weights[m_key], 2))

                        with open(report_file, "w", encoding="utf-8") as f:
                            json.dump(report_data, f, indent=2, ensure_ascii=False)
                    except Exception as e:
                        logger.warning(f"Lỗi khi cập nhật file metrics_report.json cho {r.id}: {e}")

                updated_count += 1
                logger.info(f"Đã tính lại điểm cho [{r.id}]: Điểm mới = {new_total:.2f}/100.00")

        logger.success(f"Hoàn tất tính lại điểm cho {updated_count} lượt chạy với trọng số mới!")
        return updated_count
