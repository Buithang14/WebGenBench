import re
from pathlib import Path
from typing import Optional, Any, List
from bs4 import BeautifulSoup

from metrics.base_metric import BaseMetric, MetricResult


class HTMLValidityMetric(BaseMetric):
    """Đánh giá tính hợp chuẩn W3C, ngữ nghĩa và cấu trúc của mã HTML."""

    def __init__(self):
        super().__init__(name="html_validity")

    def evaluate(self, run_dir: Path, task_meta: Optional[Any] = None) -> MetricResult:
        project_dir = run_dir / "project"
        html_file = project_dir / "index.html"

        if not html_file.exists():
            # Thử tìm file .html bất kỳ
            candidates = list(project_dir.glob("*.html"))
            if candidates:
                html_file = candidates[0]
            else:
                return MetricResult(
                    metric_name=self.name,
                    score=0.0,
                    raw_value={"error": "Missing HTML file"},
                    issues=["Không tìm thấy tệp HTML nào trong thư mục project."],
                )

        raw_content = html_file.read_text(encoding="utf-8", errors="ignore")
        issues: List[str] = []
        score = 0.0

        # 1. Kiểm tra <!DOCTYPE html> (+15đ)
        has_doctype = bool(re.search(r"<!DOCTYPE\s+html", raw_content, re.IGNORECASE))
        if has_doctype:
            score += 15.0
        else:
            issues.append("Thiếu khai báo chuẩn <!DOCTYPE html> ở đầu trang.")

        # Phân tích DOM bằng BeautifulSoup
        soup = BeautifulSoup(raw_content, "html.parser")

        # 2. Kiểm tra thuộc tính lang trong thẻ <html> (+15đ)
        html_tag = soup.find("html")
        has_lang = False
        if html_tag and html_tag.get("lang"):
            has_lang = True
            score += 15.0
        else:
            issues.append("Thẻ <html> thiếu thuộc tính 'lang' chỉ định ngôn ngữ.")

        # 3. Kiểm tra <meta charset="..."> (+15đ)
        has_charset = bool(soup.find("meta", charset=True) or soup.find("meta", attrs={"http-equiv": re.compile("content-type", re.I)}))
        if has_charset:
            score += 15.0
        else:
            issues.append("Thiếu thẻ khai báo bảng mã <meta charset='UTF-8'>.")

        # 4. Kiểm tra <meta name="viewport" ...> (+15đ)
        has_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))
        if has_viewport:
            score += 15.0
        else:
            issues.append("Thiếu thẻ cấu hình hiển thị <meta name='viewport'>.")

        # 5. Kiểm tra thẻ <title> (+10đ)
        title_tag = soup.find("title")
        has_title = False
        if title_tag and title_tag.text.strip():
            has_title = True
            score += 10.0
        else:
            issues.append("Thiếu hoặc để trống thẻ <title> tiêu đề trang.")

        # 6. Kiểm tra trùng lặp ID (+15đ)
        all_ids = [el.get("id") for el in soup.find_all(id=True)]
        duplicate_ids = set([x for x in all_ids if all_ids.count(x) > 1])
        if not duplicate_ids:
            score += 15.0
        else:
            issues.append(f"Phát hiện các ID bị trùng lặp: {list(duplicate_ids)}")

        # 7. Kiểm tra thẻ ngữ nghĩa HTML5 (+15đ)
        semantic_tags = ["main", "section", "header", "footer", "article", "nav", "form"]
        found_semantic = [tag for tag in semantic_tags if soup.find(tag)]
        if len(found_semantic) >= 2:
            score += 15.0
        elif len(found_semantic) == 1:
            score += 7.5
            issues.append("Chỉ sử dụng 1 loại thẻ ngữ nghĩa HTML5, nên bổ sung thêm cấu trúc rõ ràng.")
        else:
            issues.append("Thiếu các thẻ ngữ nghĩa HTML5 chuẩn (<main>, <header>, <form>, <section>).")

        score = min(max(round(score, 2), 0.0), 100.0)
        return MetricResult(
            metric_name=self.name,
            score=score,
            raw_value={
                "has_doctype": has_doctype,
                "has_lang": has_lang,
                "has_charset": has_charset,
                "has_viewport": has_viewport,
                "has_title": has_title,
                "duplicate_ids": list(duplicate_ids),
                "semantic_tags_found": found_semantic,
            },
            issues=issues,
        )

