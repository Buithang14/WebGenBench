"""experiment/batch_runner.py
Module quản lý ma trận thí nghiệm hàng loạt (Batch Experiment Runner)
Hỗ trợ sinh hàng đợi 144 lượt chạy, kiểm tra tiến độ, Resume và Retry theo Plan.docx.
"""

from typing import List, Dict, Any, Optional
from config.loader import load_tools
from experiment.task_loader import list_available_tasks
from storage.db_manager import DBManager
from storage.models import Run


class BatchRunner:
    """Quản lý ma trận kế hoạch thí nghiệm và hàng đợi thực thi."""

    def __init__(self, repetitions: int = 3, db_manager: Optional[DBManager] = None):
        self.repetitions = repetitions
        self.db = db_manager or DBManager()

    def generate_full_matrix(
        self,
        ides: Optional[List[str]] = None,
        tasks: Optional[List[str]] = None,
        conditions: Optional[List[str]] = None,
        repetitions: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Sinh toàn bộ ma trận thí nghiệm dự kiến: IDEs × Tasks × Conditions × Repetitions."""
        tools_cfg = load_tools()
        target_ides = ides or list(tools_cfg.tools.keys())
        target_tasks = tasks or list_available_tasks()
        target_conditions = conditions or ["text_only", "text_image"]
        n_reps = repetitions or self.repetitions

        matrix: List[Dict[str, Any]] = []
        for ide in target_ides:
            for task_id in target_tasks:
                for cond in target_conditions:
                    for rep in range(1, n_reps + 1):
                        run_id = f"{ide}_{task_id}_{cond}_rep{rep}"
                        matrix.append({
                            "run_id": run_id,
                            "ide_name": ide,
                            "task_id": task_id,
                            "prompt_condition": cond,
                            "repetition": rep,
                        })
        return matrix

    def get_matrix_progress(self, matrix: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Đối chiếu ma trận với CSDL SQLite để thống kê số run đã hoàn thành, lỗi và chưa chạy."""
        if matrix is None:
            matrix = self.generate_full_matrix()

        with self.db.get_session() as session:
            existing_runs = session.query(Run).all()
            run_map = {r.id: r for r in existing_runs}

        completed: List[Dict[str, Any]] = []
        failed: List[Dict[str, Any]] = []
        pending: List[Dict[str, Any]] = []

        for item in matrix:
            r_id = item["run_id"]
            db_run = run_map.get(r_id)
            if db_run:
                item_with_status = {**item, "status": db_run.status, "duration": db_run.duration_seconds}
                if db_run.status == "SUCCESS":
                    completed.append(item_with_status)
                else:
                    failed.append(item_with_status)
            else:
                pending.append({**item, "status": "PENDING", "duration": 0.0})

        total = len(matrix)
        pct_done = round(len(completed) / total * 100, 1) if total > 0 else 0.0

        return {
            "total_planned": total,
            "completed_count": len(completed),
            "failed_count": len(failed),
            "pending_count": len(pending),
            "progress_percent": pct_done,
            "completed": completed,
            "failed": failed,
            "pending": pending,
        }

