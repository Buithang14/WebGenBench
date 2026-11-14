from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:8501/inspect", wait_until="networkidle")

    # Let's test injecting SVG directly into a tab's DOM to see how gorgeous it looks!
    page.evaluate("""() => {
        const tabs = document.querySelectorAll('[data-testid="stTab"]');
        if (tabs[0]) {
            const p = tabs[0].querySelector('p');
            if (p) {
                p.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="vertical-align: middle; margin-right: 6px;"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg> ` + p.innerText;
            }
        }
    }""")
    page.screenshot(path="d:/WebGenBench/docs/screenshots/tab_with_svg_injected.png")
    browser.close()
