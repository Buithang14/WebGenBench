import json
from pathlib import Path
from PIL import Image

from metrics.html_validity import HTMLValidityMetric
from metrics.accessibility import AccessibilityMetric
from metrics.responsive import ResponsiveMetric
from metrics.design_similarity import DesignSimilarityMetric
from metrics.code_quality import CodeQualityMetric
from metrics.runtime_cleanliness import RuntimeCleanlinessMetric


def test_html_validity_metric(tmp_path: Path):
    run_dir = tmp_path / "run_test"
    proj_dir = run_dir / "project"
    proj_dir.mkdir(parents=True)

    html = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Login Test</title>
</head>
<body>
  <main>
    <section>
      <form id="f1">
        <label for="u">User</label>
        <input id="u" type="text">
      </form>
    </section>
  </main>
</body>
</html>"""
    (proj_dir / "index.html").write_text(html, encoding="utf-8")

    metric = HTMLValidityMetric()
    res = metric.evaluate(run_dir)
    assert res.score >= 90.0
    assert len(res.issues) == 0


def test_accessibility_metric(tmp_path: Path):
    run_dir = tmp_path / "run_test"
    proj_dir = run_dir / "project"
    proj_dir.mkdir(parents=True, exist_ok=True)

    html = """<!DOCTYPE html>
<html>
<body>
  <h1>Đăng nhập</h1>
  <form>
    <label for="email">Email</label>
    <input id="email" type="email" autocomplete="email" required>
    <button type="submit">Gửi</button>
  </form>
  <img src="logo.png" alt="Logo">
</body>
</html>"""
    (proj_dir / "index.html").write_text(html, encoding="utf-8")

    metric = AccessibilityMetric()
    res = metric.evaluate(run_dir)
    assert res.score == 100.0


def test_responsive_metric(tmp_path: Path):
    run_dir = tmp_path / "run_test"
    proj_dir = run_dir / "project"
    proj_dir.mkdir(parents=True, exist_ok=True)

    css = """
body { display: flex; justify-content: center; }
@media (max-width: 768px) {
  body { flex-direction: column; }
}
"""
    (proj_dir / "style.css").write_text(css, encoding="utf-8")

    render_rep = {
        "dom_metrics": {
            "375": {"scrollWidth": 375, "clientWidth": 375, "has_horizontal_overflow": False},
            "768": {"scrollWidth": 768, "clientWidth": 768, "has_horizontal_overflow": False},
            "1440": {"scrollWidth": 1440, "clientWidth": 1440, "has_horizontal_overflow": False},
        }
    }
    (run_dir / "render_report.json").write_text(json.dumps(render_rep), encoding="utf-8")

    metric = ResponsiveMetric()
    res = metric.evaluate(run_dir)
    assert res.score == 100.0


def test_code_quality_metric(tmp_path: Path):
    run_dir = tmp_path / "run_test"
    proj_dir = run_dir / "project"
    proj_dir.mkdir(parents=True, exist_ok=True)

    (proj_dir / "index.html").write_text("<!DOCTYPE html><html><body><button id='b'>Click</button></body></html>", encoding="utf-8")
    (proj_dir / "style.css").write_text(":root { --primary: blue; } body { color: var(--primary); }", encoding="utf-8")
    (proj_dir / "script.js").write_text("document.getElementById('b').addEventListener('click', () => { test(); });", encoding="utf-8")

    metric = CodeQualityMetric()
    res = metric.evaluate(run_dir)
    assert res.score >= 95.0
    assert res.raw_value["inline_styles_count"] == 0
    assert res.raw_value["inline_events_count"] == 0


def test_runtime_cleanliness_metric(tmp_path: Path):
    run_dir = tmp_path / "run_test"
    run_dir.mkdir(parents=True, exist_ok=True)

    clean_report = {
        "runtime_errors": {
            "page_errors": [],
            "console_errors": [],
            "failed_requests": [],
            "console_warnings": [],
        }
    }
    (run_dir / "render_report.json").write_text(json.dumps(clean_report), encoding="utf-8")

    metric = RuntimeCleanlinessMetric()
    res = metric.evaluate(run_dir)
    assert res.score == 100.0

    # Test với lỗi
    error_report = {
        "runtime_errors": {
            "page_errors": ["Uncaught ReferenceError: foo is not defined"],
            "console_errors": ["Failed to load resource"],
            "failed_requests": [],
            "console_warnings": ["DevTools warning"],
        }
    }
    (run_dir / "render_report.json").write_text(json.dumps(error_report), encoding="utf-8")
    res_err = metric.evaluate(run_dir)
    assert res_err.score == 50.0  # 100 - 30 - 15 - 5 = 50.0
    assert len(res_err.issues) == 3


def test_design_similarity_metric_identical(tmp_path: Path):
    run_dir = tmp_path / "run_test"
    shots_dir = run_dir / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    # Tạo ảnh trắng có một hình chữ nhật xanh ở giữa
    img = Image.new("RGB", (1440, 900), color=(240, 240, 240))
    shot_path = shots_dir / "viewport_1440px.png"
    img.save(shot_path)

    # Giả lập ref image
    designs_dir = Path("designs")
    designs_dir.mkdir(exist_ok=True)
    ref_path = designs_dir / "TTEST_reference.png"
    img.save(ref_path)

    try:
        metric = DesignSimilarityMetric()
        res = metric.evaluate(run_dir, task_meta={"task_id": "TTEST"})
        assert res.score >= 95.0
    finally:
        ref_path.unlink(missing_ok=True)

