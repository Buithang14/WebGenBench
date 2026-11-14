import asyncio
import os
import shutil
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\jimmy\.gemini\antigravity\brain\c0cfbd33-cafc-4871-9c26-44df1a642285"
DOCS_DIR = r"d:\WebGenBench\docs\screenshots"

PAGES = [
    ("m3_01_overview", "http://localhost:8501/"),
    ("m3_02_tasks", "http://localhost:8501/tasks"),
    ("m3_03_experiments", "http://localhost:8501/experiments"),
    ("m3_04_inspect", "http://localhost:8501/inspect"),
    ("m3_05_rating", "http://localhost:8501/rating"),
    ("m3_06_analytics", "http://localhost:8501/analytics"),
    ("m3_07_weights", "http://localhost:8501/weights"),
    ("m3_08_export", "http://localhost:8501/export"),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("Starting M3 Showcase capture across 8 pages with NEW PADDING...")

        for name, url in PAGES:
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=20000)
            await page.wait_for_timeout(1200)

            # Check computed padding across key elements
            metrics = await page.evaluate('''() => {
                const getPad = sel => {
                    const el = document.querySelector(sel);
                    return el ? getComputedStyle(el).padding : null;
                };
                const sb = document.querySelector('section[data-testid="stSidebar"]');
                return {
                    sidebarWidth: sb ? sb.getBoundingClientRect().width : null,
                    mainBlockPadding: getPad('[data-testid="stMainBlockContainer"]'),
                    sidebarUserContentPad: getPad('[data-testid="stSidebarUserContent"]'),
                    sidebarNavPad: getPad('[data-testid="stSidebarNav"] a'),
                    cardPad: getPad('.m3-card'),
                    btnPad: getPad('.stButton button'),
                    downloadBtnPad: getPad('.stDownloadButton button'),
                    tabPanelPad: getPad('[data-baseweb="tab-panel"]'),
                    metricPad: getPad('[data-testid="stMetric"]'),
                    bannerPad: getPad('.m3-banner')
                };
            }''')
            print(f"[{name}] Computed Padding Metrics: {metrics}")

            artifact_path = os.path.join(ARTIFACT_DIR, f"{name}.png")
            docs_path = os.path.join(DOCS_DIR, f"{name}.png")

            await page.screenshot(path=artifact_path, full_page=False)
            shutil.copy2(artifact_path, docs_path)
            print(f"Saved: {artifact_path} & {docs_path}")

        # Also capture collapsed sidebar state on overview
        await page.goto("http://localhost:8501/", wait_until="networkidle", timeout=15000)
        await page.wait_for_timeout(1000)
        # Collapse sidebar
        await page.evaluate('''() => {
            const collapseBtn = document.querySelector('button[data-testid="stSidebarCollapseButton"]') || 
                                document.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
                                document.querySelector('button[aria-label="Collapse sidebar"]') ||
                                document.querySelector('button[kind="header"]');
            if (collapseBtn) collapseBtn.click();
        }''')
        await page.wait_for_timeout(800)

        collapsed_artifact = os.path.join(ARTIFACT_DIR, "m3_sidebar_collapsed_fullwidth.png")
        collapsed_docs = os.path.join(DOCS_DIR, "m3_sidebar_collapsed_fullwidth.png")
        await page.screenshot(path=collapsed_artifact, full_page=False)
        shutil.copy2(collapsed_artifact, collapsed_docs)
        print("Captured collapsed sidebar state with enhanced padding.")

        await browser.close()
        print("All showcase captures completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
