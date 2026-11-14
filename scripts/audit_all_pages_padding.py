from playwright.sync_api import sync_playwright

PAGES = [
    ("overview", "http://localhost:8501/"),
    ("tasks", "http://localhost:8501/tasks"),
    ("experiments", "http://localhost:8501/experiments"),
    ("inspect", "http://localhost:8501/inspect"),
    ("rating", "http://localhost:8501/rating"),
    ("analytics", "http://localhost:8501/analytics"),
    ("weights", "http://localhost:8501/weights"),
    ("export", "http://localhost:8501/export"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    for name, url in PAGES:
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(800)
        report = page.evaluate("""() => {
            const getPad = sel => {
                const els = document.querySelectorAll(sel);
                if (els.length === 0) return 'none';
                return getComputedStyle(els[0]).padding;
            };
            return {
                mainBlock: getPad('[data-testid="stMainBlockContainer"]'),
                card: getPad('.m3-card'),
                elevatedCard: getPad('.m3-card-elevated'),
                banner: getPad('.m3-banner'),
                tabPanel: getPad('[data-baseweb="tab-panel"]'),
                tabBtn: getPad('[data-baseweb="tab"]'),
                expanderHeader: getPad('.streamlit-expanderHeader'),
                expanderContent: getPad('.streamlit-expanderContent'),
                slider: getPad('.stSlider [data-baseweb="slider"]'),
                codePre: getPad('.stCode pre'),
                fileUploader: getPad('[data-testid="stFileUploader"]'),
                radioLabel: getPad('.stRadio div[role="radiogroup"] label'),
                button: getPad('.stButton button'),
                downloadBtn: getPad('.stDownloadButton button'),
                metric: getPad('[data-testid="stMetric"]')
            };
        }""")
        print(f"=== Page {name} ({url}) ===")
        for k, v in report.items():
            if v != 'none':
                print(f"  {k}: {v}")
    browser.close()
