from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501/", wait_until="networkidle")
    page.wait_for_timeout(1000)

    # Check how stIconMaterial elements look before
    before = page.evaluate("""() => {
        const icons = Array.from(document.querySelectorAll('[data-testid="stIconMaterial"]'));
        return icons.map(i => ({
            tag: i.tagName,
            text: i.innerText,
            width: i.getBoundingClientRect().width,
            height: i.getBoundingClientRect().height
        }));
    }""")
    print("Before replacement:", before[:4])

    # Inject SVG replacement script
    page.evaluate("""() => {
        const svgMap = {
            "dashboard": '<path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>',
            "task": '<path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>',
            "rocket_launch": '<path d="M12 2.5s4 3.5 4 8.5c0 2.5-1 4.5-2 5.5l1.5 2.5-2.5-.5-1.5 3-1.5-3-2.5.5L9 16.5c-1-1-2-3-2-5.5 0-5 4-8.5 4-8.5zm0 5a2 2 0 100 4 2 2 0 000-4z"/>',
            "manage_search": '<path d="M7 9H2V7h5v2zm0 3H2v-2h5v2zm13.59 7-3.83-3.83c-.8.52-1.74.83-2.76.83-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5c0 1.02-.31 1.96-.83 2.75L22 17.59 20.59 19zM14 11c0 1.66 1.34 3 3 3s3-1.34 3-3-1.34-3-3-3-3 1.34-3 3zM2 15h10v-2H2v2z"/>',
            "gavel": '<path d="M1 21h12v2H1zM5.245 8.07l2.83-2.827 8.995 8.994-2.828 2.829zM12.317 1l5.657 5.656-2.828 2.83-5.657-5.658zM21.503 14.435l1.414 1.415-5.656 5.656-1.415-1.414z"/>',
            "analytics": '<path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>',
            "tune": '<path d="M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z"/>',
            "download": '<path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>'
        };

        document.querySelectorAll('[data-testid="stIconMaterial"]').forEach(span => {
            const iconName = span.innerText.trim();
            const path = svgMap[iconName];
            if (path) {
                span.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor" style="vertical-align: middle; display: inline-block;"><path d="${path.match(/d="([^"]+)"/)[1]}"/></svg>`;
                span.style.fontFamily = 'inherit';
                span.style.fontSize = '0';
            }
        });
    }""")

    page.screenshot(path="d:/WebGenBench/docs/screenshots/sidebar_with_real_svg.png")

    after = page.evaluate("""() => {
        const svgCount = document.querySelectorAll('[data-testid="stSidebarNav"] svg').length;
        return { svgCountInSidebarNav: svgCount };
    }""")
    print("After replacement:", after)
    browser.close()
