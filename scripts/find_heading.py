from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501/analytics", wait_until="networkidle")
    page.wait_for_timeout(1000)
    info = page.evaluate("""() => {
        const all = document.querySelectorAll('*');
        const found = [];
        for (const el of all) {
            if (el.children.length === 0 && el.innerText && el.innerText.includes('Tổng Điểm Chuẩn Hóa')) {
                found.push({
                    tag: el.tagName,
                    parentTag: el.parentElement.tagName,
                    text: el.innerText,
                    outerHTML: el.outerHTML,
                    parentOuterHTML: el.parentElement.outerHTML
                });
            }
        }
        return found;
    }""")
    import pprint
    pprint.pprint(info)
    browser.close()
