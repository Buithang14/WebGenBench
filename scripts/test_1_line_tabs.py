from playwright.sync_api import sync_playwright

TEST_CSS = """
/* Khóa cứng tablist thành 1 DÒNG DUY NHẤT */
div[data-testid="stTabs"] div[role="tablist"],
div[role="tablist"],
.stTabs [role="tablist"],
.stTabs [data-baseweb="tab-list"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    white-space: nowrap !important;
    gap: 6px !important;
    padding-top: 4px !important;
    padding-bottom: 8px !important;
    margin-bottom: 1.5rem !important;
    scrollbar-width: none !important;
    height: 48px !important;
    min-height: 48px !important;
    max-height: 48px !important;
    align-items: center !important;
}

div[role="tablist"]::-webkit-scrollbar {
    display: none !important;
}

/* Tinh chỉnh padding & font-size để các tab vừa vặn trên 1 dòng */
div[data-testid="stTab"],
[role="tab"],
.stTabs [role="tab"],
.stTabs [data-baseweb="tab"] {
    flex-shrink: 0 !important;
    border-radius: var(--md-shape-corner-full, 9999px) !important;
    padding: 6px 14px !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    letter-spacing: 0.1px !important;
    color: var(--md-sys-color-on-surface-variant, #444746) !important;
    background-color: var(--md-sys-color-surface-container, #F0F4F9) !important;
    border: 1px solid var(--md-sys-color-outline-variant, #C4C7C5) !important;
    transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
    height: 36px !important;
    min-height: 36px !important;
    max-height: 36px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
    cursor: pointer !important;
    overflow: hidden !important;
    white-space: nowrap !important;
}

div[data-testid="stTab"] p,
[role="tab"] p,
.stTabs [role="tab"] p,
div[data-testid="stTab"] [data-testid="stMarkdownContainer"] p {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.2 !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    color: inherit !important;
    white-space: nowrap !important;
}

div[data-testid="stTab"][aria-selected="true"],
[role="tab"][aria-selected="true"],
div[data-testid="stTab"][data-selected="true"] {
    background-color: var(--md-sys-color-primary-container, #D3E3FD) !important;
    color: var(--md-sys-color-on-primary-container, #041E49) !important;
    border: 1.5px solid var(--md-sys-color-primary, #0B57D0) !important;
    font-weight: 700 !important;
}

div[data-testid="stTab"][aria-selected="true"] p,
[role="tab"][aria-selected="true"] p {
    font-weight: 700 !important;
    color: var(--md-sys-color-on-primary-container, #041E49) !important;
}

.react-aria-SelectionIndicator,
div[data-testid="stTab"] .react-aria-SelectionIndicator {
    display: none !important;
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501/analytics", wait_until="networkidle")
    page.wait_for_timeout(1000)

    # Apply TEST_CSS
    page.add_style_tag(content=TEST_CSS)
    page.wait_for_timeout(500)

    # Inspect metrics
    tab_list_info = page.evaluate("""() => {
        const tabList = document.querySelector('[role="tablist"]');
        const tabs = Array.from(document.querySelectorAll('[data-testid="stTab"]'));
        const tabTops = tabs.map(t => t.getBoundingClientRect().top);
        const allOnSameLine = tabTops.every(top => Math.abs(top - tabTops[0]) < 2);

        return {
            tabListHeight: tabList ? tabList.getBoundingClientRect().height : null,
            tabListWidth: tabList ? tabList.getBoundingClientRect().width : null,
            tabCount: tabs.length,
            tabTops: tabTops,
            allOnSameLine: allOnSameLine,
            totalTabsWidth: tabs.reduce((acc, t) => acc + t.getBoundingClientRect().width, 0),
            individualTabs: tabs.map(t => ({
                text: t.innerText.trim(),
                width: t.getBoundingClientRect().width,
                height: t.getBoundingClientRect().height,
                top: t.getBoundingClientRect().top
            }))
        };
    }""")
    print("Tablist 1-line check with compact M3 Pill:")
    import pprint
    pprint.pprint(tab_list_info)

    page.screenshot(path="d:/WebGenBench/docs/screenshots/tabs_1_line_verified.png")
    page.screenshot(path="C:/Users/jimmy/.gemini/antigravity/brain/c0cfbd33-cafc-4871-9c26-44df1a642285/tabs_1_line_verified.png")
    browser.close()
