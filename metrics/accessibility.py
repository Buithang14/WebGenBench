import re
from pathlib import Path
from typing import Optional, Any, List
from bs4 import BeautifulSoup

from metrics.base_metric import BaseMetric, MetricResult


class AccessibilityMetric(BaseMetric):
    """Đánh giá khả năng tiếp cận (Accessibility - a11y theo tinh thần WCAG)."""

    def __init__(self):
        super().__init__(name="accessibility")

    def evaluate(self, run_dir: Path, task_meta: Optional[Any] = None) -> MetricResult:
        project_dir = run_dir / "project"
        html_file = project_dir / "index.html"

        if not html_file.exists():
            return MetricResult(
                metric_name=self.name,
                score=0.0,
                raw_value={"error": "Missing HTML file"},
                issues=["Không tìm thấy file index.html."],
            )

        raw_content = html_file.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(raw_content, "html.parser")
        issues: List[str] = []
        score = 0.0

        # 1. Kiểm tra nhãn label cho các ô input (+25đ)
        inputs = [
            inp for inp in soup.find_all("input")
            if inp.get("type", "text").lower() not in ["hidden", "submit", "button", "reset"]
        ]
        unlabeled_inputs = []
        for inp in inputs:
            inp_id = inp.get("id")
            has_label = False
            if inp_id and soup.find("label", attrs={"for": inp_id}):
                has_label = True
            elif inp.find_parent("label"):
                has_label = True
            elif inp.get("aria-label") or inp.get("aria-labelledby"):
                has_label = True

            if not has_label:
                unlabeled_inputs.append(inp.get("name") or inp.get("id") or str(inp)[:30])

        if inputs:
            ratio = (len(inputs) - len(unlabeled_inputs)) / len(inputs)
            score += 25.0 * ratio
            if unlabeled_inputs:
                issues.append(f"Có {len(unlabeled_inputs)} input thiếu nhãn label rõ ràng: {unlabeled_inputs}")
        else:
            score += 25.0

        # 2. Kiểm tra thuộc tính alt của thẻ <img> (+10đ)
        images = soup.find_all("img")
        missing_alt = [img for img in images if img.get("alt") is None]
        if images:
            alt_ratio = (len(images) - len(missing_alt)) / len(images)
            score += 10.0 * alt_ratio
            if missing_alt:
                issues.append(f"Có {len(missing_alt)} ảnh <img> thiếu thuộc tính 'alt'.")
        else:
            score += 10.0

        # 3. Kiểm tra nhãn cho các nút <button> (+20đ)
        buttons = soup.find_all("button")
        unlabeled_buttons = []
        for btn in buttons:
            text = btn.get_text(strip=True)
            aria = btn.get("aria-label") or btn.get("aria-labelledby")
            title = btn.get("title")
            if not (text or aria or title or btn.find(["svg", "img", "span"])):
                unlabeled_buttons.append(str(btn)[:30])

        if buttons:
            btn_ratio = (len(buttons) - len(unlabeled_buttons)) / len(buttons)
            score += 20.0 * btn_ratio
            if unlabeled_buttons:
                issues.append(f"Có {len(unlabeled_buttons)} nút <button> thiếu nhãn mô tả hành động.")
        else:
            score += 20.0

        # 4. Phân cấp tiêu đề (Heading Hierarchy) (+15đ)
        headings = [int(tag.name[1]) for tag in soup.find_all(re.compile(r"^h[1-6]$"))]
        has_h1 = 1 in headings
        if has_h1:
            score += 15.0
        else:
            issues.append("Trang thiếu thẻ tiêu đề chính cấp 1 (<h1>).")

        # 5. Sử dụng thuộc tính ARIA và hỗ trợ form (+15đ)
        aria_elements = soup.find_all(lambda el: any(k.startswith("aria-") or k == "role" for k in el.attrs.keys()))
        form_elements = soup.find_all(["input", "form", "select", "textarea"])
        has_aria_or_support = len(aria_elements) > 0 or any(el.get("autocomplete") or el.get("required") for el in form_elements)
        if has_aria_or_support:
            score += 15.0
        else:
            issues.append("Khuyến nghị bổ sung các thuộc tính hỗ trợ tiếp cận (ARIA roles, autocomplete, required).")

        # 6. Kiểm tra số liệu tiếp cận thực tế từ render_report.json (+15đ)
        render_report_file = run_dir / "render_report.json"
        runtime_a11y_score = 15.0
        if render_report_file.exists():
            try:
                import json
                rep = json.loads(render_report_file.read_text(encoding="utf-8"))
                dom_m = rep.get("dom_metrics", {})
                # Lấy số liệu tại viewport desktop (1440px) hoặc viewport đầu tiên
                v_data = dom_m.get("1440") or (list(dom_m.values())[0] if dom_m else {})
                layout_iss = v_data.get("layout_issues", [])
                contrast_iss = v_data.get("contrast_issues", [])

                # Trừ điểm nếu vùng bấm tương tác quá nhỏ (<24x24px)
                small_targets = [x for x in layout_iss if x.get("type") == "TOUCH_TARGET_TOO_SMALL"]
                if small_targets:
                    runtime_a11y_score -= min(5.0 * len(small_targets), 8.0)
                    for st in small_targets[:2]:
                        issues.append(f"[Kích thước vùng bấm] {st.get('message')} tại {st.get('target')}")

                # Trừ điểm nếu hiển thị đồng thời nhiều icon trạng thái gây mơ hồ cho người dùng
                multi_icons = [x for x in layout_iss if x.get("type") == "MULTIPLE_VISIBLE_ICONS"]
                if multi_icons:
                    runtime_a11y_score -= 5.0
                    issues.append(f"[Trạng thái tương tác] Nút điều khiển hiển thị icon mâu thuẫn (không rõ ràng trạng thái ẩn/hiện).")

                # Trừ điểm nếu độ tương phản màu sắc không đạt chuẩn WCAG AA (< 4.5:1)
                if contrast_iss:
                    runtime_a11y_score -= min(3.0 * len(contrast_iss), 6.0)
                    for ci in contrast_iss[:2]:
                        issues.append(f"[Độ tương phản thấp] Text '{ci.get('text')}' có tỷ lệ {ci.get('ratio')}:1 (< 4.5:1 chuẩn WCAG AA)")

            except Exception:
                pass

        score += max(0.0, runtime_a11y_score)

        score = min(max(round(score, 2), 0.0), 100.0)
        return MetricResult(
            metric_name=self.name,
            score=score,
            raw_value={
                "total_inputs": len(inputs),
                "unlabeled_inputs_count": len(unlabeled_inputs),
                "total_images": len(images),
                "missing_alt_images_count": len(missing_alt),
                "total_buttons": len(buttons),
                "has_h1": has_h1,
                "aria_elements_count": len(aria_elements),
            },
            issues=issues,
        )

