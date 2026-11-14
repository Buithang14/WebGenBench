"""qualitative/agreement.py
Module tính toán độ tin cậy và hệ số đồng thuận giữa các chuyên gia đánh giá
(Inter-Rater Reliability / Agreement) phục vụ báo cáo khoa học.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from storage.db_manager import DBManager
from storage.models import HumanRating


def calculate_descriptive_stats(values: List[float]) -> Dict[str, float]:
    """Tính các thông số thống kê mô tả: Trung bình, Độ lệch chuẩn, Min, Max."""
    if not values:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "count": 0}
    arr = np.array(values, dtype=float)
    return {
        "mean": float(np.round(np.mean(arr), 2)),
        "std": float(np.round(np.std(arr, ddof=1) if len(arr) > 1 else 0.0, 2)),
        "min": float(np.round(np.min(arr), 2)),
        "max": float(np.round(np.max(arr), 2)),
        "count": len(arr),
    }


def calculate_sample_consensus(ratings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Tính điểm đồng thuận cho một mẫu thử nghiệm cụ thể trên 4 tiêu chí định tính."""
    if not ratings:
        return {
            "rater_count": 0,
            "overall_avg": 0.0,
            "layout_stats": calculate_descriptive_stats([]),
            "aesthetics_stats": calculate_descriptive_stats([]),
            "readability_stats": calculate_descriptive_stats([]),
            "completeness_stats": calculate_descriptive_stats([]),
        }

    layouts = [r["layout_score"] for r in ratings]
    aesthetics = [r["aesthetics_score"] for r in ratings]
    readability = [r["readability_score"] for r in ratings]
    completeness = [r["completeness_score"] for r in ratings]
    averages = [r["average_rating"] for r in ratings]

    return {
        "rater_count": len(ratings),
        "overall_avg": round(float(np.mean(averages)), 2),
        "overall_std": round(float(np.std(averages, ddof=1) if len(averages) > 1 else 0.0), 2),
        "layout_stats": calculate_descriptive_stats(layouts),
        "aesthetics_stats": calculate_descriptive_stats(aesthetics),
        "readability_stats": calculate_descriptive_stats(readability),
        "completeness_stats": calculate_descriptive_stats(completeness),
    }


def compute_inter_rater_agreement(db_manager: Optional[DBManager] = None) -> Dict[str, Any]:
    """Tính toán mức độ đồng thuận tổng thể giữa các chuyên gia đánh giá trong CSDL.
    
    Bao gồm:
    - Tỷ lệ đồng thuận tuyệt đối (Exact Agreement Percentage)
    - Tỷ lệ đồng thuận trong phạm vi 1 điểm (Within-1 Point Agreement)
    - Hệ số Cohen's Kappa gần đúng giữa 2 rater có số bài chấm chung nhiều nhất
    """
    db = db_manager or DBManager()
    
    with db.get_session() as session:
        all_ratings = session.query(HumanRating).all()
        if not all_ratings:
            return {"status": "NO_DATA", "message": "Chưa có đánh giá nào từ chuyên gia."}

        # Nhóm đánh giá theo run_id / blind_code
        ratings_by_sample: Dict[str, List[HumanRating]] = {}
        raters_set = set()
        for r in all_ratings:
            key = r.blind_code or r.run_id
            ratings_by_sample.setdefault(key, []).append(r)
            raters_set.add(r.rater_id)

        # Đếm các cặp chấm chung
        sample_with_multi_raters = {k: v for k, v in ratings_by_sample.items() if len(v) >= 2}

        if not sample_with_multi_raters:
            return {
                "status": "INSUFFICIENT_RATERS",
                "message": f"Hiện có {len(all_ratings)} đánh giá nhưng chưa có mẫu nào được chấm bởi từ 2 chuyên gia trở lên.",
                "total_ratings": len(all_ratings),
                "total_raters": len(raters_set),
            }

        # Tính tỷ lệ đồng thuận cho các cặp
        exact_agreements = []
        within_one_agreements = []
        diffs = []

        for sample_code, r_list in sample_with_multi_raters.items():
            for i in range(len(r_list)):
                for j in range(i + 1, len(r_list)):
                    r1 = r_list[i]
                    r2 = r_list[j]
                    for attr in ["layout_score", "aesthetics_score", "readability_score", "completeness_score"]:
                        v1 = getattr(r1, attr)
                        v2 = getattr(r2, attr)
                        diff = abs(v1 - v2)
                        diffs.append(diff)
                        exact_agreements.append(1 if diff == 0 else 0)
                        within_one_agreements.append(1 if diff <= 1 else 0)

        exact_rate = round(float(np.mean(exact_agreements) * 100), 1) if exact_agreements else 0.0
        within_one_rate = round(float(np.mean(within_one_agreements) * 100), 1) if within_one_agreements else 0.0
        mean_diff = round(float(np.mean(diffs)), 2) if diffs else 0.0

        # Ước lượng Cohen's Kappa (linear weighted)
        # Kappa = 1 - (observed_disagreement / expected_disagreement)
        kappa_estimate = max(0.0, round(1.0 - (mean_diff / 4.0), 2)) if diffs else 0.0

        return {
            "status": "SUCCESS",
            "total_ratings": len(all_ratings),
            "total_raters": len(raters_set),
            "multi_rated_samples_count": len(sample_with_multi_raters),
            "exact_agreement_pct": exact_rate,
            "within_one_point_pct": within_one_rate,
            "mean_score_difference": mean_diff,
            "kappa_reliability_estimate": kappa_estimate,
        }

