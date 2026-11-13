import math
from pathlib import Path
from typing import Dict, List
import yaml
from pydantic import BaseModel, Field, field_validator

CONFIG_DIR = Path(__file__).resolve().parent

class TimingConfig(BaseModel):
    timeout_seconds: int = Field(gt=0)
    quiet_period_seconds: int = Field(gt=0)
    cooldown_seconds: int = Field(ge=0)

class ExecutablesConfig(BaseModel):
    cursor: str
    windsurf: str
    vscode: str

class SettingsConfig(BaseModel):
    executables: ExecutablesConfig
    timing: TimingConfig
    viewports: List[int]

    @field_validator("viewports")
    @classmethod
    def validate_viewports(cls, v: List[int]) -> List[int]:
        if not v or any(vp <= 0 for vp in v):
            raise ValueError("Viewports must be a non-empty list of positive integers.")
        return v

class ScoringWeights(BaseModel):
    html_validity: float = Field(ge=0.0, le=1.0)
    accessibility: float = Field(ge=0.0, le=1.0)
    responsive: float = Field(ge=0.0, le=1.0)
    design_similarity: float = Field(ge=0.0, le=1.0)
    code_quality: float = Field(ge=0.0, le=1.0)
    runtime_cleanliness: float = Field(ge=0.0, le=1.0)

    @field_validator("runtime_cleanliness")
    @classmethod
    def validate_total_weight(cls, v: float, info) -> float:
        # Trong pydantic v2, info.data chứa các field trước đó
        data = info.data
        if "html_validity" in data and "accessibility" in data and "responsive" in data and "design_similarity" in data and "code_quality" in data:
            total = (
                data["html_validity"]
                + data["accessibility"]
                + data["responsive"]
                + data["design_similarity"]
                + data["code_quality"]
                + v
            )
            if not math.isclose(total, 1.0, rel_tol=1e-6, abs_tol=1e-6):
                raise ValueError(f"Tổng trọng số các tiêu chí phải bằng 1.0 (Hiện tại: {total:.6f})")
        return v

class ScoringConfig(BaseModel):
    weights: ScoringWeights

class ToolItemConfig(BaseModel):
    name: str
    agent_name: str
    fixed_model: str
    shortcut: str
    description: str

class ToolsConfig(BaseModel):
    tools: Dict[str, ToolItemConfig]

class AppConfig(BaseModel):
    settings: SettingsConfig
    scoring: ScoringConfig
    tools: ToolsConfig


def _read_yaml_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file cấu hình: {path}")
    with open(path, "r", encoding="utf-8") as f:
        content = yaml.safe_load(f)
        return content or {}


def load_settings(config_dir: Path = CONFIG_DIR) -> SettingsConfig:
    data = _read_yaml_file(config_dir / "settings.yaml")
    return SettingsConfig.model_validate(data)


def load_scoring(config_dir: Path = CONFIG_DIR) -> ScoringConfig:
    data = _read_yaml_file(config_dir / "scoring.yaml")
    return ScoringConfig.model_validate(data)


def load_tools(config_dir: Path = CONFIG_DIR) -> ToolsConfig:
    data = _read_yaml_file(config_dir / "tools.yaml")
    return ToolsConfig.model_validate(data)


def load_all_configs(config_dir: Path = CONFIG_DIR) -> AppConfig:
    """Nạp và xác thực toàn bộ file cấu hình của hệ thống WebGenBench."""
    settings = load_settings(config_dir)
    scoring = load_scoring(config_dir)
    tools = load_tools(config_dir)
    return AppConfig(settings=settings, scoring=scoring, tools=tools)

