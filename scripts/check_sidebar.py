from playwright.sync_api import sync_playwright
import pprint

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.goto('http://localhost:8501/', wait_until='networkidle')
    page.wait_for_timeout(1000)
    links = page.evaluate("""() => {
        const nav = document.querySelector('[data-testid="stSidebarNav"]');
        if (!nav) return 'no nav';
        const aTags = Array.from(nav.querySelectorAll('a'));
        return aTags.map(a => ({
            href: a.getAttribute('href'),
            text: a.innerText,
            innerHTML: a.innerHTML
        }));
    }""")
    pprint.pprint(links)
    page.screenshot(path='d:/WebGenBench/docs/screenshots/home_sidebar_check.png')
    browser.close()
