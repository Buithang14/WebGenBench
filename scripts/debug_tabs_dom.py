from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501/analytics", wait_until="networkidle")
    page.wait_for_timeout(1000)

    # Inspect the tabs DOM
    dom_info = page.evaluate("""() => {
        const tabList = document.querySelector('.stTabs [data-baseweb="tab-list"]');
        const firstTab = document.querySelector('.stTabs [data-baseweb="tab"]');
        const tabHighlight = document.querySelector('.stTabs [data-baseweb="tab-highlight"]');
        const tabBorder = document.querySelector('.stTabs [data-baseweb="tab-border"]');
        
        // Find panels or content container
        const panels = document.querySelectorAll('[data-baseweb="tab-panel"]');
        const allTabContents = document.querySelectorAll('[data-testid="stTabContent"], [data-testid="stTabs"] > div');

        const firstTitle = document.querySelector('.stTabs h5, .stTabs [data-testid="stMarkdown"] h5');

        return {
            tabListHeight: tabList ? tabList.getBoundingClientRect().height : null,
            tabListOverflow: tabList ? getComputedStyle(tabList).overflow : null,
            firstTabHeight: firstTab ? firstTab.getBoundingClientRect().height : null,
            firstTabPadding: firstTab ? getComputedStyle(firstTab).padding : null,
            firstTabLineHeight: firstTab ? getComputedStyle(firstTab).lineHeight : null,
            firstTabOverflow: firstTab ? getComputedStyle(firstTab).overflow : null,
            firstTabParentOverflow: firstTab && firstTab.parentElement ? getComputedStyle(firstTab.parentElement).overflow : null,
            panelsCount: panels.length,
            panelPadding: panels.length > 0 ? getComputedStyle(panels[0]).padding : null,
            panelMargin: panels.length > 0 ? getComputedStyle(panels[0]).margin : null,
            firstTitleMarginTop: firstTitle ? getComputedStyle(firstTitle).marginTop : null,
            firstTitlePaddingTop: firstTitle ? getComputedStyle(firstTitle).paddingTop : null,
            firstTitleTop: firstTitle ? firstTitle.getBoundingClientRect().top : null,
            tabBottom: firstTab ? firstTab.getBoundingClientRect().bottom : null,
            tabListHTML: tabList ? tabList.outerHTML.slice(0, 400) : null
        };
    }""")
    print("DOM Info on /analytics tabs:")
    for k, v in dom_info.items():
        print(f"  {k}: {v}")

    page.screenshot(path="d:/WebGenBench/docs/screenshots/debug_tabs.png")
    browser.close()
