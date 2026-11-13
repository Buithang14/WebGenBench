import json
from pathlib import Path
from typing import Optional, Any, List

from metrics.base_metric import BaseMetric, MetricResult


class RuntimeCleanlinessMetric(BaseMetric):
    """Đánh giá độ sạch runtime: không có lỗi JS uncaught, console.error hay 404 tài nguyên."""

    def __init__(self):
        super().__init__(name="runtime_cleanliness")

    def evaluate(self, run_dir: Path, task_meta: Optional[Any] = None) -> MetricResult:
        report_file = run_dir / "render_report.json"
        issues: List[str] = []

        if not report_file.exists():
            return MetricResult(
                metric_name=self.name,
                score=50.0,
                raw_value={"warning": "Missing render_report.json"},
                issues=["Chưa có file render_report.json để đánh giá lỗi runtime."],
            )

        try:
            data = json.loads(report_file.read_text(encoding="utf-8"))
            runtime_errors = data.get("runtime_errors", {})
        except Exception as e:
            return MetricResult(
                metric_name=self.name,
                score=0.0,
                raw_value={"error": str(e)},
                issues=[f"Lỗi đọc render_report.json: {e}"],
            )

        score = 100.0
        page_errors = runtime_errors.get("page_errors", [])
        console_errors = runtime_errors.get("console_errors", [])
        failed_requests = runtime_errors.get("failed_requests", [])
        console_warnings = runtime_errors.get("console_warnings", [])

        # 1. Trừ điểm Uncaught PageError: -30đ mỗi lỗi
        for err in page_errors:
            score -= 30.0
            issues.append(f"Lỗi ngoại lệ JavaScript (Uncaught PageError): {err[:120]}")

        # 2. Trừ điểm Console Error: -15đ mỗi lỗi
        for err in console_errors:
            score -= 15.0
            issues.append(f"Lỗi Console Error: {err[:120]}")

        # 3. Trừ điểm Request Failed (404, CORS...): -15đ mỗi lỗi
        for req in failed_requests:
            score -= 15.0
            url = req.get("url", "")
            fail = req.get("failure", "")
            issues.append(f"Lỗi tải tài nguyên thất bại ({fail}): {url}")

        # 4. Trừ điểm Cảnh báo Console Warn: -5đ mỗi cảnh báo
        for warn in console_warnings:
            score -= 5.0
            issues.append(f"Cảnh báo Console Warning: {warn[:100]}")

        score = min(max(round(score, 2), 0.0), 100.0)
        return MetricResult(
            metric_name=self.name,
            score=score,
            raw_value={
                "page_errors_count": len(page_errors),
                "console_errors_count": len(console_errors),
                "failed_requests_count": len(failed_requests),
                "console_warnings_count": len(console_warnings),
            },
            issues=issues,
        )

