import pytest
from pydantic import ValidationError
from config.loader import (
    load_settings,
    load_scoring,
    load_tools,
    load_all_configs,
    ScoringWeights,
)

def test_load_all_configs():
    config = load_all_configs()
    assert config.settings.timing.timeout_seconds == 180
    assert config.settings.viewports == [375, 768, 1440]
    assert "cursor" in config.tools.tools
    assert "windsurf" in config.tools.tools
    assert "vscode" in config.tools.tools
    
    total = sum([
        config.scoring.weights.html_validity,
        config.scoring.weights.accessibility,
        config.scoring.weights.responsive,
        config.scoring.weights.design_similarity,
        config.scoring.weights.code_quality,
        config.scoring.weights.runtime_cleanliness,
    ])
    assert abs(total - 1.0) < 1e-6

def test_invalid_scoring_weights():
    with pytest.raises(ValidationError):
        ScoringWeights(
            html_validity=0.2,
            accessibility=0.2,
            responsive=0.2,
            design_similarity=0.2,
            code_quality=0.2,
            runtime_cleanliness=0.2,  # Tổng = 1.2 != 1.0 -> phải raise ValidationError
        )

