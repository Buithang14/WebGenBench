from pathlib import Path
from typing import List, Optional, Tuple
import yaml
from pydantic import BaseModel, Field, ConfigDict
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent

class TaskMeta(BaseModel):
    task_id: str
    name: str
    title_vi: str
    prompt_file: str
    reference_image: str
    expected_files: List[str]
    ui_requirements: List[str] = Field(default_factory=list)
    technical_requirements: List[str] = Field(default_factory=list)


class TaskData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    meta: TaskMeta
    prompt_text: str
    prompt_path: Path
    reference_image_path: Path
    image_dimensions: Optional[Tuple[int, int]] = None


def find_task_directory(task_id: str, tasks_dir: Optional[Path] = None) -> Path:
    """Tìm thư mục của task dựa vào task_id (ví dụ: 'T01' -> 'tasks/T01_login')."""
    tasks_root = tasks_dir or (BASE_DIR / "tasks")
    if not tasks_root.is_dir():
        raise FileNotFoundError(f"Thư mục tasks không tồn tại: {tasks_root}")

    # Tìm thư mục khớp với task_id (hoặc bắt đầu bằng {task_id}_)
    matched_dirs = [
        d for d in tasks_root.iterdir()
        if d.is_dir() and (d.name == task_id or d.name.startswith(f"{task_id}_"))
    ]

    if not matched_dirs:
        raise FileNotFoundError(f"Không tìm thấy thư mục nào cho Task ID '{task_id}' trong {tasks_root}")

    return matched_dirs[0]


def load_task(task_id: str, base_dir: Optional[Path] = None) -> TaskData:
    """Đọc, xác thực và nạp dữ liệu hoàn chỉnh cho một bài tập benchmark."""
    root = base_dir or BASE_DIR
    task_dir = find_task_directory(task_id, root / "tasks")
    meta_file = task_dir / "task_meta.yaml"

    if not meta_file.exists():
        raise FileNotFoundError(f"Không tìm thấy file task_meta.yaml tại: {meta_file}")

    with open(meta_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    meta = TaskMeta.model_validate(data)

    # 1. Xác thực và nạp nội dung prompt
    prompt_path = root / meta.prompt_file
    if not prompt_path.exists():
        # Fallback thử tìm trong thư mục task_dir nếu đường dẫn tương đối
        fallback_prompt = task_dir / Path(meta.prompt_file).name
        if fallback_prompt.exists():
            prompt_path = fallback_prompt
        else:
            raise FileNotFoundError(f"Không tìm thấy file prompt tại: {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read().strip()

    # 2. Xác thực file ảnh tham chiếu
    ref_image_path = root / meta.reference_image
    if not ref_image_path.exists():
        fallback_image = root / "designs" / Path(meta.reference_image).name
        if fallback_image.exists():
            ref_image_path = fallback_image
        else:
            raise FileNotFoundError(f"Không tìm thấy ảnh thiết kế mẫu tại: {ref_image_path}")

    dimensions = None
    try:
        with Image.open(ref_image_path) as img:
            dimensions = img.size  # (width, height)
    except Exception as e:
        raise ValueError(f"File ảnh tham chiếu không hợp lệ ({ref_image_path}): {e}")

    return TaskData(
        meta=meta,
        prompt_text=prompt_text,
        prompt_path=prompt_path,
        reference_image_path=ref_image_path,
        image_dimensions=dimensions,
    )


def list_available_tasks(tasks_dir: Optional[Path] = None) -> List[str]:
    """Liệt kê danh sách tất cả các task_id có sẵn trong thư mục tasks."""
    tasks_root = tasks_dir or (BASE_DIR / "tasks")
    if not tasks_root.is_dir():
        return []

    available = []
    for d in tasks_root.iterdir():
        if d.is_dir() and (d / "task_meta.yaml").exists():
            try:
                with open(d / "task_meta.yaml", "r", encoding="utf-8") as f:
                    meta_raw = yaml.safe_load(f)
                    if meta_raw and "task_id" in meta_raw:
                        available.append(meta_raw["task_id"])
            except Exception:
                continue
    return sorted(available)
