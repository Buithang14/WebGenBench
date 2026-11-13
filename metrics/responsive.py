import json
import re
from pathlib import Path
from typing import Optional, Any, List

from metrics.base_metric import BaseMetric, MetricResult


class ResponsiveMetric(BaseMetric):
    """Đánh giá độ thích ứng giao diện (Responsive Design) trên các kích thước màn hình."""

    def __init__(self):
        super().__init__(name="responsive")

    def evaluate(self, run_dir: Path, task_meta: Optional[Any] = None) -> MetricResult:
        project_dir = run_dir / "project"
        css_file = project_dir / "style.css"
        render_report_file = run_dir / "render_report.json"

        issues: List[str] = []
        score = 0.0

        # 1. Phân tích tĩnh file CSS (40đ)
        css_content = ""
        if css_file.exists():
            css_content = css_file.read_text(encoding="utf-8", errors="ignore")

        # a. Kiểm tra @media queries (+20đ)
        has_media_query = bool(re.search(r"@media\s*[^{]+{", css_content))
        if has_media_query:
            score += 20.0
        else:
            issues.append("File CSS không chứa câu truy vấn @media để điều chỉnh giao diện đa màn hình.")

        # b. Kiểm tra layout hiện đại Flexbox hoặc CSS Grid (+20đ)
        has_flex = bool(re.search(r"display\s*:\s*flex", css_content, re.IGNORECASE))
        has_grid = bool(re.search(r"display\s*:\s*grid", css_content, re.IGNORECASE))
        if has_flex or has_grid:
            score += 20.0
        else:
            issues.append("Không sử dụng bố cục linh hoạt Flexbox hoặc CSS Grid trong CSS.")

        # 2. Đo đạc thực tế từ render_report.json (30đ tràn ngang + 30đ độ chuẩn hình học layout)
        report_data = {}
        if render_report_file.exists():
            try:
                report_data = json.loads(render_report_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        dom_metrics = report_data.get("dom_metrics", {})
        
        # a. Kiểm tra tràn ngang (30đ)
        # Mobile 375px: +10đ
        m_375 = dom_metrics.get("375", {})
        if m_375:
            if not m_375.get("has_horizontal_overflow", False):
                score += 10.0
            else:
                diff = m_375.get("scrollWidth", 0) - m_375.get("clientWidth", 0)
                issues.append(f"Bị tràn thanh cuộn ngang ở màn hình di động 375px (+{diff}px).")
        else:
            score += 10.0

        # Tablet 768px: +10đ
        m_768 = dom_metrics.get("768", {})
        if m_768:
            if not m_768.get("has_horizontal_overflow", False):
                score += 10.0
            else:
                issues.append("Bị tràn thanh cuộn ngang ở màn hình tablet 768px.")
        else:
            score += 10.0

        # Desktop 1440px: +10đ
        m_1440 = dom_metrics.get("1440", {})
        if m_1440:
            if not m_1440.get("has_horizontal_overflow", False):
                score += 10.0
            else:
                issues.append("Bị tràn thanh cuộn ngang ở màn hình desktop 1440px.")
        else:
            score += 10.0

        # b. Kiểm tra toàn vẹn hình học layout (30đ cơ sở, trừ điểm theo mức độ nghiêm trọng)
        layout_points = 30.0
        reported_types = set()

        for vp_key, vp_val in dom_metrics.items():
            vp_issues = vp_val.get("layout_issues", [])
            for l_iss in vp_issues:
                t = l_iss.get("type")
                msg = l_iss.get("message")
                target = l_iss.get("target")

                if t == "MULTIPLE_VISIBLE_ICONS":
                    deduct = 20.0
                    key = f"{t}_{target}"
                    if key not in reported_types:
                        reported_types.add(key)
                        layout_points -= deduct
                        issues.append(f"[Lỗi hiển thị icon] {msg} tại {target}")

                elif t == "SIBLING_OVERLAP":
                    deduct = 15.0
                    key = f"{t}_{target}"
                    if key not in reported_types:
                        reported_types.add(key)
                        layout_points -= deduct
                        issues.append(f"[Lỗi đè phần tử] {msg} tại {target}")

                elif t == "BUTTON_VERTICAL_MISALIGNMENT":
                    deduct = 10.0
                    key = f"{t}_{target}"
                    if key not in reported_types:
                        reported_types.add(key)
                        layout_points -= deduct
                        issues.append(f"[Lỗi lệch tâm] {msg} tại {target}")

        score += max(0.0, layout_points)
        m_1440 = dom_metrics.get("1440", {})
        if m_1440:
            if not m_1440.get("has_horizontal_overflow", False):
                score += 15.0
            else:
                issues.append("Bị tràn thanh cuộn ngang ở màn hình desktop 1440px.")
        else:
            score += 15.0

        score = min(max(round(score, 2), 0.0), 100.0)
        return MetricResult(
            metric_name=self.name,
            score=score,
            raw_value={
                "has_media_query": has_media_query,
                "has_flex": has_flex,
                "has_grid": has_grid,
                "viewports_evaluated": list(dom_metrics.keys()),
            },
            issues=issues,
        )

