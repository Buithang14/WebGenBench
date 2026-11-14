from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501/analytics", wait_until="networkidle")
    page.wait_for_timeout(1500)
    info = page.evaluate("""() => {
        const tab = document.querySelector('[data-testid="stTab"]');
        const tabList = document.querySelector('[role="tablist"]');
        const panel = document.querySelector('[role="tabpanel"]');
        const content = document.querySelector('[data-testid="stTabContent"]');
        const h5 = document.querySelector('h5');

        return {
            tab: {
                height: tab ? tab.getBoundingClientRect().height : null,
                padding: tab ? getComputedStyle(tab).padding : null,
                lineHeight: tab ? getComputedStyle(tab).lineHeight : null,
                fontSize: tab ? getComputedStyle(tab).fontSize : null,
                border: tab ? getComputedStyle(tab).border : null,
                borderRadius: tab ? getComputedStyle(tab).borderRadius : null,
                overflow: tab ? getComputedStyle(tab).overflow : null,
                background: tab ? getComputedStyle(tab).background : null,
            },
            tabList: {
                height: tabList ? tabList.getBoundingClientRect().height : null,
                gap: tabList ? getComputedStyle(tabList).gap : null,
                padding: tabList ? getComputedStyle(tabList).padding : null,
                borderBottom: tabList ? getComputedStyle(tabList).borderBottom : null,
                overflow: tabList ? getComputedStyle(tabList).overflow : null
            },
            panel: {
                tag: panel ? panel.tagName : null,
                attributes: panel ? Array.from(panel.attributes).map(a => `${a.name}="${a.value}"`).join(' ') : null,
                padding: panel ? getComputedStyle(panel).padding : null,
                margin: panel ? getComputedStyle(panel).margin : null,
            },
            h5: {
                text: h5 ? h5.innerText : null,
                marginTop: h5 ? getComputedStyle(h5).marginTop : null,
                paddingTop: h5 ? getComputedStyle(h5).paddingTop : null,
                rectTop: h5 ? h5.getBoundingClientRect().top : null,
                tabBottom: tab ? tab.getBoundingClientRect().bottom : null
            }
        };
    }""")
    import pprint
    pprint.pprint(info)
    browser.close()
