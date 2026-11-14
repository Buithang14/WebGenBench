from playwright.sync_api import sync_playwright
import pprint
import time

pages_to_check = [
    {"name": "analytics", "url": "http://localhost:8501/analytics", "shot": "tabs_1_line_analytics.png"},
    {"name": "inspect", "url": "http://localhost:8501/inspect", "shot": "tabs_1_line_inspect.png"},
    {"name": "experiments", "url": "http://localhost:8501/experiments", "shot": "tabs_1_line_experiments.png"},
    {"name": "tasks", "url": "http://localhost:8501/tasks", "shot": "tabs_1_line_tasks.png"},
    {"name": "weights", "url": "http://localhost:8501/weights", "shot": "tabs_1_line_weights.png"}
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    results = {}

    for item in pages_to_check:
        print(f"\nChecking {item['name']} at {item['url']}...")
        page.goto(item["url"], wait_until="networkidle")
        page.wait_for_timeout(1500)

        # Inspect tabs
        metrics = page.evaluate("""() => {
            const tabLists = Array.from(document.querySelectorAll('[role="tablist"]'));
            return tabLists.map((tabList, idx) => {
                const tabs = Array.from(tabList.querySelectorAll('[data-testid="stTab"], [role="tab"]'));
                const tabTops = tabs.map(t => Math.round(t.getBoundingClientRect().top));
                const allOnSameLine = tabTops.length > 0 ? tabTops.every(top => Math.abs(top - tabTops[0]) <= 2) : true;
                const tabListRect = tabList.getBoundingClientRect();
                const totalTabsWidth = tabs.reduce((acc, t) => acc + t.getBoundingClientRect().width, 0);

                return {
                    listIndex: idx,
                    tabCount: tabs.length,
                    tabListHeight: Math.round(tabListRect.height),
                    tabListWidth: Math.round(tabListRect.width),
                    totalTabsWidth: Math.round(totalTabsWidth),
                    allOnSameLine: allOnSameLine,
                    tabTops: tabTops,
                    tabs: tabs.map(t => ({
                        text: t.innerText.trim(),
                        width: Math.round(t.getBoundingClientRect().width),
                        height: Math.round(t.getBoundingClientRect().height),
                        top: Math.round(t.getBoundingClientRect().top)
                    }))
                };
            });
        }""")

        results[item["name"]] = metrics
        print(f"Results for {item['name']}:")
        pprint.pprint(metrics)

        # Save screenshots
        page.screenshot(path=f"d:/WebGenBench/docs/screenshots/{item['shot']}")
        page.screenshot(path=f"C:/Users/jimmy/.gemini/antigravity/brain/c0cfbd33-cafc-4871-9c26-44df1a642285/{item['shot']}")

    browser.close()
    print("\nAll verification checks complete!")
