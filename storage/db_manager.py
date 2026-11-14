"""storage/db_manager.py
Trình quản trị cơ sở dữ liệu SQLite (DBManager) cho WebGenBench.
Hỗ trợ đồng bộ kết quả thí nghiệm từ đĩa vào SQLite, truy vết dữ liệu từ A-Z
và quản lý các phiên làm việc (sessions) qua SQLAlchemy.
"""

import json
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config.logger import logger
from storage.models import (
    Base,
    Experiment,
    Task,
    Run,
    GeneratedProject,
    Screenshot,
    AutomaticMetric,
    Score,
    HumanRating,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "storage" / "webgenbench.db"


class DBManager:
    """Quản lý kết nối, đồng bộ và truy vấn CSDL SQLite của WebGenBench."""

    def __init__(self, db_path: Optional[Path | str] = None, echo: bool = False):
        if db_path is None:
            self.db_path = DEFAULT_DB_PATH
            self.db_url = f"sqlite:///{self.db_path.as_posix()}"
        elif str(db_path).startswith("sqlite://"):
            self.db_url = str(db_path)
            self.db_path = Path("in_memory")
        else:
            self.db_path = Path(db_path).resolve()
            self.db_url = f"sqlite:///{self.db_path.as_posix()}"

        # Đảm bảo thư mục cha tồn tại
        if self.db_path != Path("in_memory"):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(self.db_url, echo=echo, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db(self, auto_sync_tasks: bool = True) -> None:
        """Khởi tạo toàn bộ các bảng trong cơ sở dữ liệu nếu chưa có."""
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Đã khởi tạo/xác thực lược đồ CSDL tại: {self.db_url}")
        if auto_sync_tasks:
            try:
                self.sync_all_tasks_from_disk()
            except Exception as e:
                logger.warning(f"Không thể tự động đồng bộ bài tập vào SQLite: {e}")

    @contextmanager
    def get_session(self):
        """Context manager cung cấp session an toàn, tự động rollback khi lỗi và đóng session."""
        session: Session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def sync_task_from_disk(self, task_id: str, session: Optional[Session] = None) -> Dict[str, Any]:
        """Đọc định nghĩa Task từ thư mục tasks/ và đồng bộ (upsert) vào bảng tasks trong SQLite."""
        from experiment.task_loader import load_task

        task_data = load_task(task_id)
        meta = task_data.meta
        prompt_text = task_data.prompt_text

        def _do_sync(s: Session) -> Dict[str, Any]:
            task_obj = s.query(Task).filter(Task.task_id == meta.task_id).first()
            if not task_obj:
                task_obj = Task(
                    task_id=meta.task_id,
                    name=meta.name,
                    title_vi=meta.title_vi,
                    prompt_file=meta.prompt_file,
                    prompt_text=prompt_text,
                    reference_image=meta.reference_image,
                    expected_files_json=json.dumps(meta.expected_files, ensure_ascii=False),
                    ui_requirements_json=json.dumps(meta.ui_requirements, ensure_ascii=False),
                    technical_requirements_json=json.dumps(meta.technical_requirements, ensure_ascii=False),
                )
                s.add(task_obj)
            else:
                task_obj.name = meta.name
                task_obj.title_vi = meta.title_vi
                task_obj.prompt_file = meta.prompt_file
                task_obj.prompt_text = prompt_text
                task_obj.reference_image = meta.reference_image
                task_obj.expected_files_json = json.dumps(meta.expected_files, ensure_ascii=False)
                task_obj.ui_requirements_json = json.dumps(meta.ui_requirements, ensure_ascii=False)
                task_obj.technical_requirements_json = json.dumps(meta.technical_requirements, ensure_ascii=False)
            s.flush()
            return {"task_id": meta.task_id, "name": meta.name, "status": "SYNCED"}

        if session is not None:
            return _do_sync(session)
        else:
            with self.get_session() as s:
                return _do_sync(s)

    def sync_all_tasks_from_disk(self) -> int:
        """Đồng bộ toàn bộ các Task có sẵn trong thư mục tasks/ vào SQLite."""
        from experiment.task_loader import list_available_tasks

        available = list_available_tasks()
        count = 0
        with self.get_session() as session:
            for tid in available:
                try:
                    self.sync_task_from_disk(tid, session=session)
                    count += 1
                except Exception as e:
                    logger.warning(f"Lỗi khi sync bài tập '{tid}' vào SQLite: {e}")
        logger.info(f"Đã đồng bộ {count}/{len(available)} bài tập vào bảng tasks trong SQLite.")
        return count

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin chi tiết của bài tập từ SQLite."""
        with self.get_session() as session:
            t = session.query(Task).filter(Task.task_id == task_id).first()
            if not t:
                return None
            return {
                "task_id": t.task_id,
                "name": t.name,
                "title_vi": t.title_vi,
                "prompt_file": t.prompt_file,
                "prompt_text": t.prompt_text,
                "reference_image": t.reference_image,
                "expected_files": json.loads(t.expected_files_json or "[]"),
                "ui_requirements": json.loads(t.ui_requirements_json or "[]"),
                "technical_requirements": json.loads(t.technical_requirements_json or "[]"),
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "runs_count": len(t.runs) if t.runs else 0,
            }

    def list_all_tasks(self) -> List[Dict[str, Any]]:
        """Liệt kê toàn bộ danh sách bài tập từ SQLite."""
        with self.get_session() as session:
            tasks = session.query(Task).order_by(Task.task_id).all()
            results = []
            for t in tasks:
                results.append({
                    "task_id": t.task_id,
                    "name": t.name,
                    "title_vi": t.title_vi,
                    "prompt_file": t.prompt_file,
                    "prompt_text": t.prompt_text,
                    "reference_image": t.reference_image,
                    "expected_files": json.loads(t.expected_files_json or "[]"),
                    "ui_requirements": json.loads(t.ui_requirements_json or "[]"),
                    "technical_requirements": json.loads(t.technical_requirements_json or "[]"),
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "runs_count": len(t.runs) if t.runs else 0,
                })
            return results

    def save_task(
        self,
        task_id: str,
        name: str,
        title_vi: str,
        prompt_text: str,
        ui_requirements: List[str],
        technical_requirements: List[str],
        expected_files: Optional[List[str]] = None,
        reference_image: Optional[str] = None,
        sync_to_disk: bool = True,
    ) -> Dict[str, Any]:
        """Lưu hoặc cập nhật bài tập vào SQLite, đồng thời tùy chọn xuất ngược ra thư mục tasks/."""
        expected_files = expected_files or ["index.html", "style.css", "script.js"]
        reference_image = reference_image or f"designs/{task_id}_reference.png"
        prompt_file = f"tasks/{task_id}_{name.lower().replace(' ', '_')}/prompt.txt"

        with self.get_session() as session:
            task_obj = session.query(Task).filter(Task.task_id == task_id).first()
            if not task_obj:
                task_obj = Task(
                    task_id=task_id,
                    name=name,
                    title_vi=title_vi,
                    prompt_file=prompt_file,
                    prompt_text=prompt_text,
                    reference_image=reference_image,
                    expected_files_json=json.dumps(expected_files, ensure_ascii=False),
                    ui_requirements_json=json.dumps(ui_requirements, ensure_ascii=False),
                    technical_requirements_json=json.dumps(technical_requirements, ensure_ascii=False),
                )
                session.add(task_obj)
            else:
                task_obj.name = name
                task_obj.title_vi = title_vi
                task_obj.prompt_text = prompt_text
                task_obj.reference_image = reference_image
                task_obj.expected_files_json = json.dumps(expected_files, ensure_ascii=False)
                task_obj.ui_requirements_json = json.dumps(ui_requirements, ensure_ascii=False)
                task_obj.technical_requirements_json = json.dumps(technical_requirements, ensure_ascii=False)

        if sync_to_disk:
            import yaml
            safe_slug = name.lower().replace(" ", "_").replace("-", "_")
            task_dir = BASE_DIR / "tasks" / f"{task_id}_{safe_slug}"
            task_dir.mkdir(parents=True, exist_ok=True)

            p_file = task_dir / "prompt.txt"
            p_file.write_text(prompt_text.strip(), encoding="utf-8")

            meta_data = {
                "task_id": task_id,
                "name": name,
                "title_vi": title_vi,
                "prompt_file": f"tasks/{task_dir.name}/prompt.txt",
                "reference_image": reference_image,
                "expected_files": expected_files,
                "ui_requirements": ui_requirements,
                "technical_requirements": technical_requirements,
            }
            m_file = task_dir / "task_meta.yaml"
            with open(m_file, "w", encoding="utf-8") as f:
                yaml.dump(meta_data, f, allow_unicode=True, default_flow_style=False)

        logger.info(f"Đã lưu thành công bài tập '{task_id}' (DB + Disk Sync).")
        return {"task_id": task_id, "name": name, "status": "SAVED"}

    def sync_run_from_disk(
        self,
        run_id: str,
        experiment_id: Optional[int] = None,
        base_outputs_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Đọc toàn bộ kết quả của run_id từ outputs/{run_id}/ và đồng bộ (upsert) vào SQLite."""
        outputs_dir = Path(base_outputs_dir) if base_outputs_dir else (BASE_DIR / "outputs")
        run_dir = (outputs_dir / run_id).resolve()

        if not run_dir.exists():
            raise FileNotFoundError(f"Không tìm thấy thư mục của lượt chạy: {run_dir}")

        meta_file = run_dir / "run_metadata.json"
        if not meta_file.exists():
            raise FileNotFoundError(f"Không tìm thấy file run_metadata.json trong: {run_dir}")

        # Đọc dữ liệu từ 3 file JSON chính
        run_meta: Dict[str, Any] = json.loads(meta_file.read_text(encoding="utf-8"))

        render_report: Optional[Dict[str, Any]] = None
        render_file = run_dir / "render_report.json"
        if render_file.exists():
            try:
                render_report = json.loads(render_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Lỗi khi đọc render_report.json của {run_id}: {e}")

        metrics_report: Optional[Dict[str, Any]] = None
        metrics_file = run_dir / "metrics_report.json"
        if metrics_file.exists():
            try:
                metrics_report = json.loads(metrics_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Lỗi khi đọc metrics_report.json của {run_id}: {e}")

        with self.get_session() as session:
            # Đảm bảo bài test tương ứng đã có trong bảng tasks
            task_id = run_meta.get("task_id", "T01")
            task_obj = session.query(Task).filter(Task.task_id == task_id).first()
            if not task_obj:
                try:
                    self.sync_task_from_disk(task_id, session=session)
                except Exception as e:
                    logger.warning(f"Không thể tự động sync task '{task_id}': {e}")

            # 1. Đồng bộ bảng runs
            run_obj = session.query(Run).filter(Run.id == run_id).first()
            blind_code = run_meta.get("blind_code") or f"Sample_{run_id}"

            if not run_obj:
                run_obj = Run(
                    id=run_id,
                    experiment_id=experiment_id,
                    ide_name=run_meta.get("ide", "unknown"),
                    agent_name=run_meta.get("agent"),
                    model_name=run_meta.get("model", "auto"),
                    ide_version=run_meta.get("ide_version"),
                    task_id=run_meta.get("task_id", "T01"),
                    prompt_condition=run_meta.get("condition", "text_only"),
                    repetition_num=run_meta.get("repetition_num", 1),
                    prompt_used=run_meta.get("prompt", ""),
                    start_time=run_meta.get("start_time"),
                    duration_seconds=float(run_meta.get("duration_seconds", 0.0)),
                    status=run_meta.get("status", "UNKNOWN"),
                    error_message=run_meta.get("error_message"),
                    blind_code=blind_code,
                )
                session.add(run_obj)
            else:
                run_obj.ide_name = run_meta.get("ide", run_obj.ide_name)
                run_obj.agent_name = run_meta.get("agent", run_obj.agent_name)
                run_obj.model_name = run_meta.get("model", run_obj.model_name)
                run_obj.task_id = run_meta.get("task_id", run_obj.task_id)
                run_obj.prompt_condition = run_meta.get("condition", run_obj.prompt_condition)
                run_obj.prompt_used = run_meta.get("prompt", run_obj.prompt_used)
                run_obj.duration_seconds = float(run_meta.get("duration_seconds", run_obj.duration_seconds))
                run_obj.status = run_meta.get("status", run_obj.status)
                run_obj.error_message = run_meta.get("error_message", run_obj.error_message)
                if experiment_id is not None:
                    run_obj.experiment_id = experiment_id

            session.flush()

            # 2. Đồng bộ bảng generated_projects
            project_dir = run_dir / "project"
            files_list = run_meta.get("files", [])
            proj_obj = session.query(GeneratedProject).filter(GeneratedProject.run_id == run_id).first()
            if not proj_obj:
                proj_obj = GeneratedProject(
                    run_id=run_id,
                    folder_path=str(project_dir.as_posix()),
                    entry_html_file=run_meta.get("entry_html", "index.html"),
                    file_count=len(files_list),
                    total_lines_of_code=int(run_meta.get("total_loc", 0)),
                    sha256_hash=run_meta.get("sha256_hash", ""),
                    files_json=json.dumps(files_list, ensure_ascii=False),
                )
                session.add(proj_obj)
            else:
                proj_obj.folder_path = str(project_dir.as_posix())
                proj_obj.entry_html_file = run_meta.get("entry_html", "index.html")
                proj_obj.file_count = len(files_list)
                proj_obj.total_lines_of_code = int(run_meta.get("total_loc", 0))
                proj_obj.sha256_hash = run_meta.get("sha256_hash", "")
                proj_obj.files_json = json.dumps(files_list, ensure_ascii=False)

            # 3. Đồng bộ bảng screenshots
            if render_report and "screenshots" in render_report:
                session.query(Screenshot).filter(Screenshot.run_id == run_id).delete()
                dom_metrics = render_report.get("dom_metrics", {})
                for vp_str, img_path in render_report["screenshots"].items():
                    try:
                        vp_int = int(vp_str)
                    except ValueError:
                        vp_int = 0
                    vp_dom = dom_metrics.get(vp_str, {})
                    overflow = vp_dom.get("has_horizontal_overflow", False)
                    layout_audit_data = {
                        "layout_issues": vp_dom.get("layout_issues", []),
                        "contrast_issues": vp_dom.get("contrast_issues", []),
                        "main_card_bbox": vp_dom.get("main_card_bbox"),
                    }
                    screenshot_obj = Screenshot(
                        run_id=run_id,
                        viewport_width=vp_int,
                        image_path=str(img_path),
                        has_horizontal_overflow=overflow,
                        layout_audit_json=json.dumps(layout_audit_data, ensure_ascii=False),
                    )
                    session.add(screenshot_obj)

            # 4. Đồng bộ bảng automatic_metrics & scores
            if metrics_report and "metrics" in metrics_report:
                session.query(AutomaticMetric).filter(AutomaticMetric.run_id == run_id).delete()
                metrics_data = metrics_report["metrics"]

                for m_name, m_info in metrics_data.items():
                    raw_sc = float(m_info.get("score", 0.0))
                    raw_val = m_info.get("raw_value", {})
                    issues = m_info.get("issues", [])

                    auto_metric_obj = AutomaticMetric(
                        run_id=run_id,
                        metric_name=m_name,
                        raw_score=raw_sc,
                        raw_value_json=json.dumps(raw_val, ensure_ascii=False),
                        issues_json=json.dumps(issues, ensure_ascii=False),
                    )
                    session.add(auto_metric_obj)

                # Cập nhật bảng scores
                score_obj = session.query(Score).filter(Score.run_id == run_id).first()
                weights_dict = metrics_report.get("weights", {})
                total_sc = float(metrics_report.get("total_score", 0.0))

                if not score_obj:
                    score_obj = Score(
                        run_id=run_id,
                        html_validity_score=float(metrics_data.get("html_validity", {}).get("score", 0.0)),
                        accessibility_score=float(metrics_data.get("accessibility", {}).get("score", 0.0)),
                        responsive_score=float(metrics_data.get("responsive", {}).get("score", 0.0)),
                        design_similarity_score=float(metrics_data.get("design_similarity", {}).get("score", 0.0)),
                        code_quality_score=float(metrics_data.get("code_quality", {}).get("score", 0.0)),
                        runtime_cleanliness_score=float(metrics_data.get("runtime_cleanliness", {}).get("score", 0.0)),
                        weighted_total_score=total_sc,
                        weights_snapshot_json=json.dumps(weights_dict, ensure_ascii=False),
                        updated_at=datetime.datetime.now(),
                    )
                    session.add(score_obj)
                else:
                    score_obj.html_validity_score = float(metrics_data.get("html_validity", {}).get("score", 0.0))
                    score_obj.accessibility_score = float(metrics_data.get("accessibility", {}).get("score", 0.0))
                    score_obj.responsive_score = float(metrics_data.get("responsive", {}).get("score", 0.0))
                    score_obj.design_similarity_score = float(metrics_data.get("design_similarity", {}).get("score", 0.0))
                    score_obj.code_quality_score = float(metrics_data.get("code_quality", {}).get("score", 0.0))
                    score_obj.runtime_cleanliness_score = float(metrics_data.get("runtime_cleanliness", {}).get("score", 0.0))
                    score_obj.weighted_total_score = total_sc
                    score_obj.weights_snapshot_json = json.dumps(weights_dict, ensure_ascii=False)
                    score_obj.updated_at = datetime.datetime.now()

        logger.info(f"Đã đồng bộ thành công lượt chạy '{run_id}' vào SQLite.")
        return {"run_id": run_id, "status": "SYNCED"}

    def get_run_full_trace(self, run_id: str) -> Dict[str, Any]:
        """Truy vết toàn bộ hồ sơ dữ liệu từ A-Z của một Run từ SQLite."""
        with self.get_session() as session:
            run: Optional[Run] = session.query(Run).filter(Run.id == run_id).first()
            if not run:
                raise KeyError(f"Không tìm thấy lượt chạy '{run_id}' trong CSDL!")

            # 1. Thông tin Run
            run_dict = {
                "id": run.id,
                "experiment_id": run.experiment_id,
                "ide_name": run.ide_name,
                "agent_name": run.agent_name,
                "model_name": run.model_name,
                "ide_version": run.ide_version,
                "task_id": run.task_id,
                "prompt_condition": run.prompt_condition,
                "repetition_num": run.repetition_num,
                "prompt_used": run.prompt_used,
                "start_time": run.start_time,
                "duration_seconds": run.duration_seconds,
                "status": run.status,
                "error_message": run.error_message,
                "blind_code": run.blind_code,
            }

            # 2. Project
            proj_dict = {}
            if run.project:
                proj_dict = {
                    "folder_path": run.project.folder_path,
                    "entry_html_file": run.project.entry_html_file,
                    "file_count": run.project.file_count,
                    "total_lines_of_code": run.project.total_lines_of_code,
                    "sha256_hash": run.project.sha256_hash,
                    "files": json.loads(run.project.files_json) if run.project.files_json else [],
                }

            # 3. Screenshots
            screenshots_list = []
            for sc in run.screenshots:
                screenshots_list.append({
                    "viewport_width": sc.viewport_width,
                    "image_path": sc.image_path,
                    "has_horizontal_overflow": sc.has_horizontal_overflow,
                    "layout_audit": json.loads(sc.layout_audit_json) if sc.layout_audit_json else {},
                })

            # 4. Automatic Metrics
            metrics_dict = {}
            for am in run.automatic_metrics:
                metrics_dict[am.metric_name] = {
                    "raw_score": am.raw_score,
                    "raw_value": json.loads(am.raw_value_json) if am.raw_value_json else {},
                    "issues": json.loads(am.issues_json) if am.issues_json else [],
                }

            # 5. Score
            score_dict = {}
            if run.score:
                score_dict = {
                    "html_validity_score": run.score.html_validity_score,
                    "accessibility_score": run.score.accessibility_score,
                    "responsive_score": run.score.responsive_score,
                    "design_similarity_score": run.score.design_similarity_score,
                    "code_quality_score": run.score.code_quality_score,
                    "runtime_cleanliness_score": run.score.runtime_cleanliness_score,
                    "weighted_total_score": run.score.weighted_total_score,
                    "weights_snapshot": json.loads(run.score.weights_snapshot_json) if run.score.weights_snapshot_json else {},
                    "updated_at": run.score.updated_at.isoformat() if run.score.updated_at else None,
                }

            # 6. Human Ratings
            ratings_list = []
            for hr in run.human_ratings:
                ratings_list.append({
                    "rater_id": hr.rater_id,
                    "blind_code": hr.blind_code,
                    "layout_score": hr.layout_score,
                    "aesthetics_score": hr.aesthetics_score,
                    "readability_score": hr.readability_score,
                    "completeness_score": hr.completeness_score,
                    "average_rating": hr.average_rating,
                    "comment": hr.comment,
                    "rated_at": hr.rated_at.isoformat() if hr.rated_at else None,
                })

            # 7. Task Registry
            task_dict = {}
            if run.task:
                task_dict = {
                    "task_id": run.task.task_id,
                    "name": run.task.name,
                    "title_vi": run.task.title_vi,
                    "prompt_file": run.task.prompt_file,
                    "reference_image": run.task.reference_image,
                    "expected_files": json.loads(run.task.expected_files_json or "[]"),
                    "ui_requirements": json.loads(run.task.ui_requirements_json or "[]"),
                    "technical_requirements": json.loads(run.task.technical_requirements_json or "[]"),
                }

            return {
                "run": run_dict,
                "task": task_dict,
                "project": proj_dict,
                "screenshots": screenshots_list,
                "automatic_metrics": metrics_dict,
                "score": score_dict,
                "human_ratings": ratings_list,
            }

    def list_all_runs(self) -> List[Dict[str, Any]]:
        """Trả về danh sách tóm tắt toàn bộ các lần chạy cùng điểm số."""
        with self.get_session() as session:
            runs = session.query(Run).all()
            results = []
            for r in runs:
                results.append({
                    "run_id": r.id,
                    "ide_name": r.ide_name,
                    "task_id": r.task_id,
                    "prompt_condition": r.prompt_condition,
                    "status": r.status,
                    "duration_seconds": r.duration_seconds,
                    "total_loc": r.project.total_lines_of_code if r.project else 0,
                    "weighted_total_score": r.score.weighted_total_score if r.score else None,
                    "start_time": r.start_time,
                })
            return results
