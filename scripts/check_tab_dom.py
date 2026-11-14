from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:8501/inspect", wait_until="networkidle")
    
    # Test what markdown does in tabs
    res = page.evaluate("""() => {
        const tabs = Array.from(document.querySelectorAll('[data-testid="stTab"]'));
        return tabs.map(t => ({
            text: t.innerText,
            innerHTML: t.innerHTML
        }));
    }""")
    print("Tabs innerHTML:")
    import pprint
    pprint.pprint(res[:2])
    browser.close()
