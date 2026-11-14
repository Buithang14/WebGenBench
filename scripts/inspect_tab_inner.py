from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501/analytics", wait_until="networkidle")
    page.wait_for_timeout(1000)
    res = page.evaluate("""() => {
        const tab = document.querySelector('[data-testid="stTab"]');
        return {
            innerHTML: tab ? tab.innerHTML : null,
            outerHTML: tab ? tab.outerHTML : null,
            childCount: tab ? tab.children.length : 0,
            children: tab ? Array.from(tab.children).map(c => ({
                tag: c.tagName,
                className: c.className,
                computedStyle: {
                    padding: getComputedStyle(c).padding,
                    margin: getComputedStyle(c).margin,
                    height: getComputedStyle(c).height,
                    lineHeight: getComputedStyle(c).lineHeight,
                    overflow: getComputedStyle(c).overflow
                },
                outerHTML: c.outerHTML
            })) : []
        };
    }""")
    import pprint
    pprint.pprint(res)
    browser.close()
