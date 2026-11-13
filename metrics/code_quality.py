import re
from pathlib import Path
from typing import Optional, Any, List
from bs4 import BeautifulSoup

from metrics.base_metric import BaseMetric, MetricResult


class CodeQualityMetric(BaseMetric):
    """Đánh giá chất lượng mã nguồn tĩnh: tính tách bạch 3 tầng, quy chuẩn CSS/JS."""

    def __init__(self):
        super().__init__(name="code_quality")

    def evaluate(self, run_dir: Path, task_meta: Optional[Any] = None) -> MetricResult:
        project_dir = run_dir / "project"
        issues: List[str] = []
        score = 0.0

        html_file = project_dir / "index.html"
        css_file = project_dir / "style.css"
        js_file = project_dir / "script.js"

        # 1. Kiểm tra sự tách bạch của 3 tệp chuẩn (+25đ)
        has_html = html_file.exists()
        has_css = css_file.exists()
        has_js = js_file.exists()

        if has_html and has_css and has_js:
            score += 25.0
        else:
            missing = []
            if not has_html: missing.append("index.html")
            if not has_css: missing.append("style.css")
            if not has_js: missing.append("script.js")
            issues.append(f"Chưa tách biệt đầy đủ 3 tầng mã nguồn, thiếu: {missing}")

        # 2. Phân tích mã HTML
        html_content = html_file.read_text(encoding="utf-8", errors="ignore") if has_html else ""
        soup = BeautifulSoup(html_content, "html.parser")

        # a. Kiểm tra inline style (+15đ)
        inline_style_elements = soup.find_all(style=True)
        if len(inline_style_elements) == 0:
            score += 15.0
        elif len(inline_style_elements) <= 2:
            score += 7.5
            issues.append(f"Còn tồn tại {len(inline_style_elements)} phần tử sử dụng inline style.")
        else:
            issues.append(f"Lạm dụng inline style trên {len(inline_style_elements)} phần tử HTML.")

        # b. Kiểm tra inline event handlers (onclick, onsubmit, ...) (+15đ)
        inline_events = []
        for tag in soup.find_all(True):
            for attr in tag.attrs:
                if attr.lower().startswith("on"):
                    inline_events.append(f"{tag.name}[{attr}]")

        if len(inline_events) == 0:
            score += 15.0
        else:
            issues.append(f"Sử dụng inline JavaScript handler thay vì addEventListener: {inline_events[:3]}")

        # 3. Phân tích mã CSS (+15đ)
        css_content = css_file.read_text(encoding="utf-8", errors="ignore") if has_css else ""
        has_css_vars = bool(re.search(r"--[\w-]+:", css_content))
        has_root = ":root" in css_content
        if has_css_vars or has_root:
            score += 15.0
        else:
            issues.append("CSS chưa sử dụng biến tùy biến (CSS Custom Properties --var) để dễ bảo trì.")

        # 4. Phân tích mã JavaScript (+15đ)
        js_content = js_file.read_text(encoding="utf-8", errors="ignore") if has_js else ""
        has_event_listener = "addEventListener" in js_content
        has_validation = bool(re.search(r"test\(|match\(|indexOf|length", js_content))
        if has_event_listener and has_validation:
            score += 15.0
        elif has_event_listener or has_validation:
            score += 7.5
            issues.append("JavaScript nên sử dụng đầy đủ addEventListener và kiểm tra tính hợp lệ dữ liệu.")
        else:
            issues.append("JavaScript chưa bắt sự kiện submit hoặc chưa có logic kiểm tra dữ liệu.")

        # 5. Kiểm tra tính nhất quán trạng thái giữa HTML, CSS và DOM (+15đ)
        state_consistency_score = 15.0
        hidden_tags = soup.find_all(attrs={"hidden": True})
        if hidden_tags:
            has_general_hidden = bool(re.search(r'(?:^|[,\s\}])\[hidden\]\s*\{[^}]*display\s*:\s*none', css_content))
            for ht in hidden_tags:
                parent = ht.parent
                if parent and parent.name == "button":
                    ht_class = ht.get("class", [])
                    tag_selector = ht_class[0] if ht_class else ht.name
                    has_specific_hidden = bool(re.search(rf'(?:svg\[hidden\]|\.{tag_selector})\s*\{{[^}}]*display\s*:\s*none', css_content))
                    if not has_general_hidden and not has_specific_hidden:
                        state_consistency_score -= 15.0
                        issues.append(
                            f"[Thiếu quy tắc ẩn trạng thái] Phần tử {ht.name}.{tag_selector} mang thuộc tính 'hidden' nhưng CSS thiếu quy tắc [hidden] {{ display: none; }} hoặc .{tag_selector} {{ display: none; }}."
                        )
                        break

        # Đọc thêm lỗi layout từ render_report.json nếu có
        render_report_file = run_dir / "render_report.json"
        if render_report_file.exists():
            try:
                import json
                rep = json.loads(render_report_file.read_text(encoding="utf-8"))
                for v in rep.get("dom_metrics", {}).values():
                    for l_iss in v.get("layout_issues", []):
                        if l_iss.get("type") == "MULTIPLE_VISIBLE_ICONS":
                            if "[Lỗi điều khiển trạng thái]" not in "".join(issues):
                                state_consistency_score = max(0.0, state_consistency_score - 10.0)
                                issues.append(f"[Lỗi điều khiển trạng thái] {l_iss.get('message')} tại {l_iss.get('target')}.")
                                break
            except Exception:
                pass

        score += max(0.0, state_consistency_score)

        score = min(max(round(score, 2), 0.0), 100.0)
        return MetricResult(
            metric_name=self.name,
            score=score,
            raw_value={
                "has_html": has_html,
                "has_css": has_css,
                "has_js": has_js,
                "inline_styles_count": len(inline_style_elements),
                "inline_events_count": len(inline_events),
                "has_css_vars": has_css_vars,
                "has_event_listener": has_event_listener,
            },
            issues=issues,
        )

