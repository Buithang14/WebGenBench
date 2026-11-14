from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.goto('http://localhost:8501/', wait_until='networkidle')
    page.wait_for_timeout(1000)

    info = page.evaluate("""() => {
        const getPad = sel => {
            const el = document.querySelector(sel);
            return el ? getComputedStyle(el).padding : 'not found';
        };
        const getMargin = sel => {
            const el = document.querySelector(sel);
            return el ? getComputedStyle(el).margin : 'not found';
        };
        return {
            blockContainerPad: getPad('.block-container'),
            sidebarPad: getPad('section[data-testid="stSidebar"]'),
            sidebarUserContentPad: getPad('[data-testid="stSidebarUserContent"]'),
            sidebarNavULPad: getPad('[data-testid="stSidebarNav"] ul'),
            sidebarNavLinkPad: getPad('[data-testid="stSidebarNav"] a'),
            cardPad: getPad('.m3-card'),
            btnPad: getPad('.stButton button'),
            colPad: getPad('[data-testid="column"]'),
            tabsPanelPad: getPad('[data-baseweb="tab-panel"]'),
            dfPad: getPad('[data-testid="stDataFrame"]')
        };
    }""")
    print('Current computed padding values on Overview page:')
    for k, v in info.items():
        print(f'  {k}: {v}')
    browser.close()
