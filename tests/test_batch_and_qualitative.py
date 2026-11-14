"""tests/test_batch_and_qualitative.py
Kiểm thử cho BatchRunner và phân hệ Qualitative Evaluation (BlindMapper & Agreement).
"""

from pathlib import Path
from storage.db_manager import DBManager
from experiment.batch_runner import BatchRunner
from qualitative.blind_mapper import BlindMapper
from qualitative.agreement import (
    calculate_descriptive_stats,
    calculate_sample_consensus,
    compute_inter_rater_agreement,
)
from storage.models import HumanRating


def test_batch_runner_matrix_generation(tmp_path: Path):
    db_mgr = DBManager(db_path=tmp_path / "test_batch.db")
    db_mgr.init_db()

    runner = BatchRunner(repetitions=2, db_manager=db_mgr)
    matrix = runner.generate_full_matrix(
        ides=["cursor"],
        tasks=["T01"],
        conditions=["text_only", "text_image"],
        repetitions=2
    )

    # 1 IDE x 1 Task x 2 Conditions x 2 Repetitions = 4 runs
    assert len(matrix) == 4
    assert matrix[0]["run_id"] == "cursor_T01_text_only_rep1"
    assert matrix[1]["run_id"] == "cursor_T01_text_only_rep2"

    progress = runner.get_matrix_progress(matrix)
    assert progress["total_planned"] == 4
    assert progress["completed_count"] == 0
    assert progress["pending_count"] == 4


def test_blind_mapper_assignment(tmp_path: Path):
    db_mgr = DBManager(db_path=tmp_path / "test_blind.db")
    db_mgr.init_db()

    mapper = BlindMapper(db_manager=db_mgr)
    count = mapper.ensure_blind_codes_assigned()
    assert count == 0  # Chưa có run nào

    samples = mapper.get_blind_sample_list()
    assert isinstance(samples, list)


def test_agreement_calculations(tmp_path: Path):
    # Test descriptive stats
    stats = calculate_descriptive_stats([4.0, 5.0, 3.0, 4.0])
    assert stats["mean"] == 4.0
    assert stats["min"] == 3.0
    assert stats["max"] == 5.0
    assert stats["count"] == 4

    # Test sample consensus
    ratings = [
        {"layout_score": 4, "aesthetics_score": 5, "readability_score": 4, "completeness_score": 5, "average_rating": 4.5},
        {"layout_score": 4, "aesthetics_score": 4, "readability_score": 4, "completeness_score": 4, "average_rating": 4.0},
    ]
    consensus = calculate_sample_consensus(ratings)
    assert consensus["rater_count"] == 2
    assert consensus["overall_avg"] == 4.25
    assert consensus["layout_stats"]["mean"] == 4.0

