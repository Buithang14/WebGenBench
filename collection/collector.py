import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List

from config.logger import logger


class ArtifactCollector:
    """Bộ thu thập và lưu trữ toàn vẹn project kết quả sinh ra bởi IDE AI Agent."""

    def __init__(self, base_output_dir: Optional[Path] = None):
        self.base_output_dir = Path(base_output_dir) if base_output_dir else Path("outputs")

    @staticmethod
    def calculate_file_sha256(file_path: Path) -> str:
        """Tính mã băm SHA-256 của một tệp tin."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def calculate_project_sha256(project_dir: Path) -> str:
        """Tính mã băm SHA-256 tổng thể của toàn bộ project kết quả."""
        hasher = hashlib.sha256()
        all_files = sorted([p for p in project_dir.rglob("*") if p.is_file()])
        for p in all_files:
            rel_path = p.relative_to(project_dir).as_posix()
            hasher.update(rel_path.encode("utf-8"))
            with open(p, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def count_lines_of_code(file_path: Path) -> int:
        """Đếm số dòng của một tệp văn bản mã nguồn."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    def collect_run_artifacts(
        self,
        run_id: str,
        workspace_dir: Path,
        metadata: Dict[str, Any],
    ) -> Path:
        """Thu thập toàn bộ sản phẩm của lần chạy từ workspace_dir sang outputs/{run_id}/.
        
        Quy tắc bất biến:
        - Giữ nguyên trạng 100% mã nguồn AI sinh ra, không chỉnh sửa nội dung.
        - Bỏ qua tệp quản lý nội bộ .gitkeep.
        - Tạo thư mục outputs/{run_id}/project/ chứa code kết quả.
        - Lưu tệp siêu dữ liệu outputs/{run_id}/run_metadata.json.
        """
        workspace_dir = Path(workspace_dir).resolve()
        run_dir = (self.base_output_dir / run_id).resolve()
        project_dest_dir = run_dir / "project"

        # Đảm bảo thư mục đích sạch
        if project_dest_dir.exists():
            shutil.rmtree(project_dest_dir)
        project_dest_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Đang thu thập kết quả từ '{workspace_dir}' vào '{project_dest_dir}'...")

        # 1. Sao chép nguyên trạng các tệp/thư mục (trừ .gitkeep)
        copied_files: List[str] = []
        if workspace_dir.exists():
            for item in workspace_dir.iterdir():
                if item.name == ".gitkeep":
                    continue
                dest = project_dest_dir / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                    copied_files.append(item.name)
                elif item.is_dir():
                    shutil.copytree(item, dest)
                    for sub in dest.rglob("*"):
                        if sub.is_file():
                            copied_files.append(sub.relative_to(project_dest_dir).as_posix())

        copied_files.sort()

        # 2. Xác định file entry HTML
        entry_html: Optional[str] = None
        if (project_dest_dir / "index.html").exists():
            entry_html = "index.html"
        else:
            for f_name in copied_files:
                if f_name.lower().endswith(".html"):
                    entry_html = f_name
                    break

        # 3. Tính tổng số dòng code (LOC)
        total_loc = 0
        code_extensions = {".html", ".htm", ".css", ".js", ".ts", ".json"}
        for f_name in copied_files:
            p = project_dest_dir / f_name
            if p.suffix.lower() in code_extensions:
                total_loc += self.count_lines_of_code(p)

        # 4. Tính mã băm toàn vẹn SHA-256
        sha256_hash = self.calculate_project_sha256(project_dest_dir) if copied_files else ""

        # 5. Tổng hợp run_metadata.json
        run_meta = {
            "run_id": run_id,
            "ide": metadata.get("ide", "unknown"),
            "agent": metadata.get("agent", "unknown"),
            "model": metadata.get("model", "unknown"),
            "task_id": metadata.get("task_id", "unknown"),
            "condition": metadata.get("condition", "text_only"),
            "start_time": metadata.get("start_time"),
            "duration_seconds": metadata.get("duration_seconds", 0.0),
            "status": metadata.get("status", "UNKNOWN"),
            "files": copied_files,
            "entry_html": entry_html,
            "total_loc": total_loc,
            "sha256_hash": sha256_hash,
            "error_message": metadata.get("error_message"),
        }

        # Bổ sung các thông số mở rộng khác trong metadata nếu có
        for k, v in metadata.items():
            if k not in run_meta:
                run_meta[k] = v

        metadata_file = run_dir / "run_metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(run_meta, f, indent=2, ensure_ascii=False)

        logger.success(
            f"Đã thu thập thành công {len(copied_files)} tệp vào: {project_dest_dir} "
            f"(Entry: {entry_html}, LOC: {total_loc}, SHA256: {sha256_hash[:10]}...)"
        )
        return run_dir

