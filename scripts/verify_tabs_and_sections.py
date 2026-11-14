from playwright.sync_api import sync_playwright
import os
import shutil

ARTIFACT_DIR = r"C:\Users\jimmy\.gemini\antigravity\brain\c0cfbd33-cafc-4871-9c26-44df1a642285"
DOCS_DIR = r"d:\WebGenBench\docs\screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    # Test /analytics specifically
    print("Navigating to /analytics...")
    page.goto("http://localhost:8501/analytics", wait_until="networkidle")
    page.wait_for_timeout(1500)

    analytics_metrics = page.evaluate("""() => {
        const tab = document.querySelector('[data-testid="stTab"]');
        const tabList = document.querySelector('[role="tablist"]');
        const panel = document.querySelector('[data-testid="stTabPanel"]');
        const titleSpan = Array.from(document.querySelectorAll('span')).find(s => s.innerText && s.innerText.includes('Tổng Điểm Chuẩn Hóa'));
        const titleContainer = titleSpan ? titleSpan.parentElement : null;

        return {
            tab: {
                height: tab ? tab.getBoundingClientRect().height : null,
                padding: tab ? getComputedStyle(tab).padding : null,
                borderRadius: tab ? getComputedStyle(tab).borderRadius : null,
                backgroundColor: tab ? getComputedStyle(tab).backgroundColor : null,
                color: tab ? getComputedStyle(tab).color : null,
                boxShadow: tab ? getComputedStyle(tab).boxShadow : null,
                fontSize: tab ? getComputedStyle(tab).fontSize : null
            },
            tabList: {
                height: tabList ? tabList.getBoundingClientRect().height : null,
                gap: tabList ? getComputedStyle(tabList).gap : null,
                paddingTop: tabList ? getComputedStyle(tabList).paddingTop : null,
                paddingBottom: tabList ? getComputedStyle(tabList).paddingBottom : null,
                borderBottom: tabList ? getComputedStyle(tabList).borderBottom : null
            },
            panel: {
                paddingTop: panel ? getComputedStyle(panel).paddingTop : null,
                paddingBottom: panel ? getComputedStyle(panel).paddingBottom : null,
                marginTop: panel ? getComputedStyle(panel).marginTop : null
            },
            sectionTitle: {
                rectTop: titleContainer ? titleContainer.getBoundingClientRect().top : null,
                tabRectBottom: tab ? tab.getBoundingClientRect().bottom : null,
                gapToTab: (titleContainer && tab) ? (titleContainer.getBoundingClientRect().top - tab.getBoundingClientRect().bottom) : null
            }
        };
    }""")
    print("Analytics Metrics:")
    import pprint
    pprint.pprint(analytics_metrics)

    # Capture zoomed-in tabs area
    analytics_shot = os.path.join(ARTIFACT_DIR, "analytics_tabs_padded.png")
    analytics_docs = os.path.join(DOCS_DIR, "analytics_tabs_padded.png")
    page.screenshot(path=analytics_shot)
    shutil.copy2(analytics_shot, analytics_docs)
    print("Saved analytics screenshot.")

    # Now verify all pages with tabs
    pages_to_check = [
        ("overview", "http://localhost:8501/"),
        ("tasks", "http://localhost:8501/tasks"),
        ("experiments", "http://localhost:8501/experiments"),
        ("inspect", "http://localhost:8501/inspect"),
        ("rating", "http://localhost:8501/rating"),
        ("analytics", "http://localhost:8501/analytics"),
        ("weights", "http://localhost:8501/weights"),
        ("export", "http://localhost:8501/export"),
    ]

    for name, url in pages_to_check:
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(1000)
        shot_path = os.path.join(ARTIFACT_DIR, f"m3_page_{name}_items_padded.png")
        docs_path = os.path.join(DOCS_DIR, f"m3_page_{name}_items_padded.png")
        page.screenshot(path=shot_path)
        shutil.copy2(shot_path, docs_path)
        print(f"Verified & saved {name}: {shot_path}")

    browser.close()
    print("All verifications completed successfully!")
