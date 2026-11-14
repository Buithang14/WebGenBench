from playwright.sync_api import sync_playwright

TEST_CSS = """
/* Modern Streamlit Tabs (React-Aria & BaseWeb compatible) */
div[data-testid="stTabs"] {
    margin-top: 1rem !important;
    margin-bottom: 2rem !important;
}

div[role="tablist"],
.stTabs [role="tablist"],
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 2px solid var(--md-sys-color-surface-container-highest, #E1E7F0) !important;
    gap: 10px !important;
    padding-top: 4px !important;
    padding-bottom: 12px !important;
    margin-bottom: 1.5rem !important;
    overflow: visible !important;
    flex-wrap: wrap !important;
    height: auto !important;
}

div[data-testid="stTab"],
[role="tab"],
.stTabs [role="tab"],
.stTabs [data-baseweb="tab"] {
    border-radius: var(--md-shape-corner-full, 9999px) !important;
    padding: 10px 22px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    color: var(--md-sys-color-on-surface-variant, #444746) !important;
    background-color: var(--md-sys-color-surface-container, #F0F4F9) !important;
    border: 1px solid var(--md-sys-color-outline-variant, #C4C7C5) !important;
    transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
    height: auto !important;
    min-height: 44px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
    cursor: pointer !important;
    overflow: visible !important;
}

div[data-testid="stTab"] p,
[role="tab"] p,
.stTabs [role="tab"] p {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.4 !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    color: inherit !important;
}

div[data-testid="stTab"]:hover,
[role="tab"]:hover {
    background-color: var(--md-sys-color-surface-container-high, #E9EEF6) !important;
    border-color: var(--md-sys-color-primary, #0B57D0) !important;
    color: var(--md-sys-color-primary, #0B57D0) !important;
}

div[data-testid="stTab"][aria-selected="true"],
[role="tab"][aria-selected="true"],
div[data-testid="stTab"][data-selected="true"],
[data-baseweb="tab"][aria-selected="true"] {
    background-color: var(--md-sys-color-primary-container, #D3E3FD) !important;
    color: var(--md-sys-color-on-primary-container, #041E49) !important;
    border: 1.5px solid var(--md-sys-color-primary, #0B57D0) !important;
    font-weight: 700 !important;
    box-shadow: var(--md-elevation-1, 0 1px 3px rgba(0,0,0,0.12)) !important;
}

div[data-testid="stTab"][aria-selected="true"] p,
[role="tab"][aria-selected="true"] p {
    font-weight: 700 !important;
    color: var(--md-sys-color-on-primary-container, #041E49) !important;
}

/* Ẩn thanh line indicator 2px mặc định của React-Aria để dùng chuẩn M3 Pill */
.react-aria-SelectionIndicator,
div[data-testid="stTab"] .react-aria-SelectionIndicator,
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] {
    display: none !important;
}

/* Tab Panel: Đệm nội dung bên trong mỗi tab rộng rãi, thoáng đãng */
div[data-testid="stTabPanel"],
div[role="tabpanel"],
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.6rem !important;
    padding-bottom: 2rem !important;
    padding-left: 0.25rem !important;
    padding-right: 0.25rem !important;
}

/* Tiêu đề các mục h5, h4 bên trong tab */
.stTabs h5,
.stTabs [data-testid="stMarkdownContainer"] h5,
h5 {
    margin-top: 1.4rem !important;
    margin-bottom: 1.1rem !important;
    padding-top: 6px !important;
    padding-bottom: 6px !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    color: var(--md-sys-color-on-surface, #1F1F1F) !important;
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501/analytics", wait_until="networkidle")
    page.wait_for_timeout(1000)

    # First take screenshot without TEST_CSS
    page.screenshot(path="d:/WebGenBench/docs/screenshots/tabs_before.png")

    # Add TEST_CSS
    page.add_style_tag(content=TEST_CSS)
    page.wait_for_timeout(500)

    # Take screenshot with TEST_CSS
    page.screenshot(path="d:/WebGenBench/docs/screenshots/tabs_after.png")
    page.screenshot(path="C:/Users/jimmy/.gemini/antigravity/brain/c0cfbd33-cafc-4871-9c26-44df1a642285/tabs_after.png")

    # Inspect metrics
    metrics = page.evaluate("""() => {
        const tab = document.querySelector('[data-testid="stTab"]');
        const panel = document.querySelector('[data-testid="stTabPanel"]');
        const h5 = document.querySelector('h5');
        return {
            tabHeight: tab ? tab.getBoundingClientRect().height : null,
            tabPadding: tab ? getComputedStyle(tab).padding : null,
            tabBorderRadius: tab ? getComputedStyle(tab).borderRadius : null,
            tabBg: tab ? getComputedStyle(tab).backgroundColor : null,
            panelPadding: panel ? getComputedStyle(panel).padding : null,
            h5RectTop: h5 ? h5.getBoundingClientRect().top : null,
            tabRectBottom: tab ? tab.getBoundingClientRect().bottom : null,
            distanceBetweenTabAndContent: (h5 && tab) ? (h5.getBoundingClientRect().top - tab.getBoundingClientRect().bottom) : null
        };
    }""")
    print("Metrics after applying TEST_CSS:")
    import pprint
    pprint.pprint(metrics)

    browser.close()
