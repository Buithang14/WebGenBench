import abc
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MetricResult(BaseModel):
    """Cấu trúc dữ liệu chuẩn cho kết quả chấm điểm của một nhóm tiêu chí."""
    metric_name: str
    score: float = Field(ge=0.0, le=100.0, description="Điểm chuẩn hóa từ 0.0 đến 100.0")
    raw_value: Dict[str, Any] = Field(default_factory=dict, description="Số liệu đo đạc gốc chi tiết")
    issues: List[str] = Field(default_factory=list, description="Danh sách các lỗi hoặc cảnh báo phát hiện được")


class BaseMetric(abc.ABC):
    """Lớp cơ sở trừu tượng cho tất cả các module đánh giá (Evaluation Metrics).
    
    Quy tắc kiến trúc:
    - Độc lập hoàn toàn với việc điều khiển IDE.
    - Nhận đầu vào là thư mục kết quả outputs/{run_id}/ và siêu dữ liệu task.
    - Trả về MetricResult với điểm chuẩn hóa trong khoảng [0.0, 100.0].
    """

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def evaluate(self, run_dir: Path, task_meta: Optional[Any] = None) -> MetricResult:
        """Thực hiện đánh giá định lượng và trả về kết quả MetricResult."""
        pass

