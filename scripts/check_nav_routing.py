from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501/", wait_until="networkidle")
    page.wait_for_timeout(1000)

    # Click on Phân Tích & Biểu Đồ
    page.click("text=Phân Tích & Biểu Đồ")
    page.wait_for_timeout(1500)

    page.screenshot(path="d:/WebGenBench/docs/screenshots/analytics_clicked_from_nav.png")
    
    # Check sidebar nav items
    links = page.evaluate("""() => {
        const aTags = Array.from(document.querySelectorAll('[data-testid="stSidebarNav"] a'));
        return aTags.map(a => a.innerText.trim());
    }""")
    print("Sidebar links after clicking from home:", links)
    browser.close()
