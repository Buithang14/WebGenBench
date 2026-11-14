from playwright.sync_api import sync_playwright
import re
import pprint

emoji_regex = re.compile(r'[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50-\u2b55]')

pages = [
    {"name": "00_overview", "nav_text": "Tổng Quan", "path": "svg_00_overview.png"},
    {"name": "01_tasks", "nav_text": "Quản Lý Bài Tập", "path": "svg_01_tasks.png"},
    {"name": "02_experiments", "nav_text": "Điều Khiển Thí Nghiệm", "path": "svg_02_experiments.png"},
    {"name": "03_inspect", "nav_text": "Chi Tiết Lần Chạy", "path": "svg_03_inspect.png"},
    {"name": "04_rating", "nav_text": "Chấm Điểm Ẩn Danh", "path": "svg_04_rating.png"},
    {"name": "05_analytics", "nav_text": "Phân Tích & Biểu Đồ", "path": "svg_05_analytics.png"},
    {"name": "06_weights", "nav_text": "Cấu Hình & Trọng Số", "path": "svg_06_weights.png"},
    {"name": "07_export", "nav_text": "Xuất Báo Cáo", "path": "svg_07_export.png"},
]

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501/", wait_until="networkidle")
    page.wait_for_timeout(1000)

    for pinfo in pages:
        print(f"\nNavigating to: {pinfo['nav_text']}...")
        page.click(f"text={pinfo['nav_text']}")
        page.wait_for_timeout(1200)

        # Inspect DOM for SVG count and emojis
        page_stats = page.evaluate("""() => {
            const svgs = document.querySelectorAll('svg');
            const bodyText = document.body.innerText;
            const sidebarIcons = document.querySelectorAll('[data-testid="stSidebarNav"] span[data-testid="stIconMaterial"]');
            
            return {
                totalSvgCount: svgs.length,
                sidebarIconCount: sidebarIcons.length,
                bodyTextSample: bodyText.substring(0, 300)
            };
        }""")

        # Search for emojis in full page text
        full_text = page.inner_text("body")
        found_emojis = list(set(emoji_regex.findall(full_text)))

        results.append({
            "page": pinfo["name"],
            "title": pinfo["nav_text"],
            "svg_count": page_stats["totalSvgCount"],
            "sidebar_icons": page_stats["sidebarIconCount"],
            "emojis_found": found_emojis
        })

        # Save screenshots
        dest1 = f"d:/WebGenBench/docs/screenshots/{pinfo['path']}"
        dest2 = f"C:/Users/jimmy/.gemini/antigravity/brain/c0cfbd33-cafc-4871-9c26-44df1a642285/{pinfo['path']}"
        page.screenshot(path=dest1)
        page.screenshot(path=dest2)
        print(f"Captured: {pinfo['path']} (SVGs: {page_stats['totalSvgCount']}, Emojis: {found_emojis})")

    browser.close()

print("\n===== FULL AUDIT REPORT =====")
pprint.pprint(results)
