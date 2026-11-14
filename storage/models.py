"""storage/models.py
Khai báo lược đồ cơ sở dữ liệu (Database Schema) bằng SQLAlchemy ORM cho WebGenBench.
Hỗ trợ lưu trữ và truy vết quan hệ chặt chẽ từ Điểm số -> Metric -> Screenshot -> Project -> Run.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Experiment(Base):
    """Bảng lưu thông tin chiến dịch thí nghiệm (Experiment Batch)."""
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    config_snapshot_json = Column(Text, nullable=True)
    status = Column(String(30), default="RUNNING")
    created_at = Column(DateTime, default=datetime.now)

    # Quan hệ 1 - N với Runs
    runs = relationship("Run", back_populates="experiment", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Experiment(id={self.id}, name='{self.name}', status='{self.status}')>"


class Task(Base):
    """Bảng lưu thông tin các bài tập Benchmark (Task Registry)."""
    __tablename__ = "tasks"

    task_id = Column(String(50), primary_key=True)  # ví dụ: 'T01', 'T02'
    name = Column(String(100), nullable=False)
    title_vi = Column(String(255), nullable=True)
    prompt_file = Column(String(255), nullable=True)
    prompt_text = Column(Text, nullable=False)
    reference_image = Column(String(255), nullable=True)
    expected_files_json = Column(Text, nullable=True)  # JSON list
    ui_requirements_json = Column(Text, nullable=True)  # JSON list
    technical_requirements_json = Column(Text, nullable=True)  # JSON list
    created_at = Column(DateTime, default=datetime.now)

    # Quan hệ 1 - N với Runs
    runs = relationship("Run", back_populates="task")

    def __repr__(self) -> str:
        return f"<Task(id='{self.task_id}', name='{self.name}')>"


class Run(Base):
    """Bảng lưu trữ thông tin thực thi của một lần chạy (Run)."""
    __tablename__ = "runs"

    id = Column(String(100), primary_key=True)  # ví dụ: 'run_001'
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=True)
    ide_name = Column(String(50), nullable=False)
    agent_name = Column(String(50), nullable=True)
    model_name = Column(String(50), nullable=True)
    ide_version = Column(String(50), nullable=True)
    task_id = Column(String(50), ForeignKey("tasks.task_id"), nullable=False)
    prompt_condition = Column(String(30), nullable=False)  # 'text_only' / 'text_image'
    repetition_num = Column(Integer, default=1)
    prompt_used = Column(Text, nullable=False)
    start_time = Column(String(50), nullable=True)
    duration_seconds = Column(Float, default=0.0)
    status = Column(String(30), default="UNKNOWN")  # 'SUCCESS', 'FAILED', 'ERROR'
    error_message = Column(Text, nullable=True)
    blind_code = Column(String(50), nullable=True, index=True)  # ví dụ: 'Sample_001'

    # Quan hệ
    task = relationship("Task", back_populates="runs")
    experiment = relationship("Experiment", back_populates="runs")
    project = relationship("GeneratedProject", back_populates="run", uselist=False, cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="run", cascade="all, delete-orphan")
    automatic_metrics = relationship("AutomaticMetric", back_populates="run", cascade="all, delete-orphan")
    score = relationship("Score", back_populates="run", uselist=False, cascade="all, delete-orphan")
    human_ratings = relationship("HumanRating", back_populates="run", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Run(id='{self.id}', ide='{self.ide_name}', task='{self.task_id}', status='{self.status}')>"


class GeneratedProject(Base):
    """Bảng lưu thông tin mã nguồn và artifact sinh ra bởi IDE AI."""
    __tablename__ = "generated_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), ForeignKey("runs.id"), unique=True, nullable=False)
    folder_path = Column(String(255), nullable=False)
    entry_html_file = Column(String(100), default="index.html")
    file_count = Column(Integer, default=0)
    total_lines_of_code = Column(Integer, default=0)
    sha256_hash = Column(String(64), nullable=False)
    files_json = Column(Text, nullable=False)  # danh sách file dạng JSON

    run = relationship("Run", back_populates="project")

    def __repr__(self) -> str:
        return f"<GeneratedProject(run_id='{self.run_id}', loc={self.total_lines_of_code}, sha256='{self.sha256_hash[:8]}...')>"


class Screenshot(Base):
    """Bảng lưu thông tin chụp màn hình theo từng Viewport (375px, 768px, 1440px)."""
    __tablename__ = "screenshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), ForeignKey("runs.id"), nullable=False)
    viewport_width = Column(Integer, nullable=False)  # 375, 768, 1440
    image_path = Column(String(255), nullable=False)
    has_horizontal_overflow = Column(Boolean, default=False)
    layout_audit_json = Column(Text, nullable=True)  # chi tiết các lỗi DOM audit

    run = relationship("Run", back_populates="screenshots")

    def __repr__(self) -> str:
        return f"<Screenshot(run_id='{self.run_id}', viewport={self.viewport_width}px, overflow={self.has_horizontal_overflow})>"


class AutomaticMetric(Base):
    """Bảng lưu chi tiết kết quả của từng tiêu chí chấm điểm tự động."""
    __tablename__ = "automatic_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), ForeignKey("runs.id"), nullable=False)
    metric_name = Column(String(50), nullable=False)  # 1 trong 6 tiêu chí
    raw_score = Column(Float, nullable=False)  # 0.0 - 100.0
    raw_value_json = Column(Text, nullable=True)  # dữ liệu thô đo đạc
    issues_json = Column(Text, nullable=True)  # danh sách cảnh báo/lỗi

    run = relationship("Run", back_populates="automatic_metrics")

    def __repr__(self) -> str:
        return f"<AutomaticMetric(run_id='{self.run_id}', metric='{self.metric_name}', score={self.raw_score})>"


class Score(Base):
    """Bảng lưu điểm số tổng hợp cuối cùng và snapshot trọng số của Run."""
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), ForeignKey("runs.id"), unique=True, nullable=False)
    html_validity_score = Column(Float, default=0.0)
    accessibility_score = Column(Float, default=0.0)
    responsive_score = Column(Float, default=0.0)
    design_similarity_score = Column(Float, default=0.0)
    code_quality_score = Column(Float, default=0.0)
    runtime_cleanliness_score = Column(Float, default=0.0)
    weighted_total_score = Column(Float, default=0.0)
    weights_snapshot_json = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.now)

    run = relationship("Run", back_populates="score")

    def __repr__(self) -> str:
        return f"<Score(run_id='{self.run_id}', total={self.weighted_total_score})>"


class HumanRating(Base):
    """Bảng lưu đánh giá định tính của con người (Blind Human Evaluation - Milestone 11)."""
    __tablename__ = "human_ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), ForeignKey("runs.id"), nullable=False)
    blind_code = Column(String(50), nullable=True, index=True)
    rater_id = Column(String(50), nullable=False)
    layout_score = Column(Integer, nullable=False)  # 1 - 5
    aesthetics_score = Column(Integer, nullable=False)  # 1 - 5
    readability_score = Column(Integer, nullable=False)  # 1 - 5
    completeness_score = Column(Integer, nullable=False)  # 1 - 5
    average_rating = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    rated_at = Column(DateTime, default=datetime.now)

    run = relationship("Run", back_populates="human_ratings")

    def __repr__(self) -> str:
        return f"<HumanRating(run_id='{self.run_id}', rater='{self.rater_id}', avg={self.average_rating})>"
