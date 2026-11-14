"""qualitative/blind_mapper.py
Module quản lý cơ chế gán nhãn ẩn danh (Blind Mapping) cho các lần chạy (Runs)
phục vụ đánh giá định tính của con người mà không bị thiên kiến thương hiệu IDE.
"""

from typing import Dict, Any, List, Optional
from storage.db_manager import DBManager
from storage.models import Run
from config.logger import logger


class BlindMapper:
    """Quản lý việc ánh xạ giữa Run ID và Mã Ẩn Danh (Blind Code)."""

    def __init__(self, db_manager: Optional[DBManager] = None):
        self.db = db_manager or DBManager()

    def ensure_blind_codes_assigned(self) -> int:
        """Kiểm tra và gán mã Sample_001, Sample_002... cho toàn bộ các Run trong CSDL nếu chưa có."""
        updated_count = 0
        with self.db.get_session() as session:
            runs: List[Run] = session.query(Run).order_by(Run.id.asc()).all()
            for idx, r in enumerate(runs, 1):
                if not r.blind_code:
                    r.blind_code = f"Sample_{idx:03d}"
                    updated_count += 1
            session.commit()
            
        if updated_count > 0:
            logger.info(f"Đã gán mã ẩn danh mới cho {updated_count} lượt chạy.")
        return updated_count

    def get_blind_sample_list(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các mẫu ẩn danh cùng dữ liệu phục vụ hiển thị cho người chấm."""
        self.ensure_blind_codes_assigned()
        samples = []
        with self.db.get_session() as session:
            runs: List[Run] = session.query(Run).all()
            for r in runs:
                # Chỉ lấy các thông tin không để lộ IDE hoặc điều kiện
                samples.append({
                    "blind_code": r.blind_code or r.id,
                    "run_id": r.id,
                    "task_id": r.task_id,
                    "status": r.status,
                    "has_project": r.project is not None,
                })
        return sorted(samples, key=lambda x: x["blind_code"])

    def reveal_identity(self, blind_code: str) -> Optional[Dict[str, Any]]:
        """Giải mã thông tin thật của một mẫu ẩn danh (Chỉ dùng khi hoàn tất chấm điểm)."""
        with self.db.get_session() as session:
            run: Optional[Run] = session.query(Run).filter(Run.blind_code == blind_code).first()
            if not run:
                return None
            return {
                "blind_code": run.blind_code,
                "run_id": run.id,
                "ide_name": run.ide_name,
                "agent_name": run.agent_name,
                "prompt_condition": run.prompt_condition,
                "task_id": run.task_id,
                "total_score": run.score.weighted_total_score if run.score else None,
            }

