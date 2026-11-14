from playwright.sync_api import sync_playwright

TEST_CSS = """
[data-testid="stSidebarNav"] a span[data-testid="stIconMaterial"] {
    font-size: 0px !important;
    line-height: 0 !important;
    display: inline-block !important;
    width: 22px !important;
    height: 22px !important;
    color: transparent !important;
    background-color: var(--md-sys-color-on-surface-variant, #444746) !important;
    -webkit-mask-size: contain !important;
    mask-size: contain !important;
    -webkit-mask-repeat: no-repeat !important;
    mask-repeat: no-repeat !important;
    -webkit-mask-position: center !important;
    mask-position: center !important;
    vertical-align: middle !important;
    flex-shrink: 0 !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] span[data-testid="stIconMaterial"] {
    background-color: var(--md-sys-color-primary, #0B57D0) !important;
}

[data-testid="stSidebarNav"] a:hover:not([aria-current="page"]) span[data-testid="stIconMaterial"] {
    background-color: var(--md-sys-color-primary, #0B57D0) !important;
}

/* 1. Tổng Quan (dashboard) */
[data-testid="stSidebarNav"] a[href$="/"] span[data-testid="stIconMaterial"],
[data-testid="stSidebarNav"] a[href$=":8501/"] span[data-testid="stIconMaterial"],
[data-testid="stSidebarNav"] a[href$=":8501"] span[data-testid="stIconMaterial"] {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") !important;
}

/* 2. Quản Lý Bài Tập (task) */
[data-testid="stSidebarNav"] a[href*="/tasks"] span[data-testid="stIconMaterial"] {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") !important;
}

/* 3. Điều Khiển Thí Nghiệm (rocket) */
[data-testid="stSidebarNav"] a[href*="/experiments"] span[data-testid="stIconMaterial"] {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 2.5s4 3.5 4 8.5c0 2.5-1 4.5-2 5.5l1.5 2.5-2.5-.5-1.5 3-1.5-3-2.5.5L9 16.5c-1-1-2-3-2-5.5 0-5 4-8.5 4-8.5zm0 5a2 2 0 100 4 2 2 0 000-4z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 2.5s4 3.5 4 8.5c0 2.5-1 4.5-2 5.5l1.5 2.5-2.5-.5-1.5 3-1.5-3-2.5.5L9 16.5c-1-1-2-3-2-5.5 0-5 4-8.5 4-8.5zm0 5a2 2 0 100 4 2 2 0 000-4z'/%3E%3C/svg%3E") !important;
}

/* 4. Chi Tiết Lần Chạy (inspect) */
[data-testid="stSidebarNav"] a[href*="/inspect"] span[data-testid="stIconMaterial"] {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M7 9H2V7h5v2zm0 3H2v-2h5v2zm13.59 7-3.83-3.83c-.8.52-1.74.83-2.76.83-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5c0 1.02-.31 1.96-.83 2.75L22 17.59 20.59 19zM14 11c0 1.66 1.34 3 3 3s3-1.34 3-3-1.34-3-3-3-3 1.34-3 3zM2 15h10v-2H2v2z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M7 9H2V7h5v2zm0 3H2v-2h5v2zm13.59 7-3.83-3.83c-.8.52-1.74.83-2.76.83-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5c0 1.02-.31 1.96-.83 2.75L22 17.59 20.59 19zM14 11c0 1.66 1.34 3 3 3s3-1.34 3-3-1.34-3-3-3-3 1.34-3 3zM2 15h10v-2H2v2z'/%3E%3C/svg%3E") !important;
}

/* 5. Chấm Điểm Ẩn Danh (rating) */
[data-testid="stSidebarNav"] a[href*="/rating"] span[data-testid="stIconMaterial"] {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M1 21h12v2H1zM5.245 8.07l2.83-2.827 8.995 8.994-2.828 2.829zM12.317 1l5.657 5.656-2.828 2.83-5.657-5.658zM21.503 14.435l1.414 1.415-5.656 5.656-1.415-1.414z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M1 21h12v2H1zM5.245 8.07l2.83-2.827 8.995 8.994-2.828 2.829zM12.317 1l5.657 5.656-2.828 2.83-5.657-5.658zM21.503 14.435l1.414 1.415-5.656 5.656-1.415-1.414z'/%3E%3C/svg%3E") !important;
}

/* 6. Phân Tích & Biểu Đồ (analytics) */
[data-testid="stSidebarNav"] a[href*="/analytics"] span[data-testid="stIconMaterial"] {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z'/%3E%3C/svg%3E") !important;
}

/* 7. Cấu Hình & Trọng Số (weights) */
[data-testid="stSidebarNav"] a[href*="/weights"] span[data-testid="stIconMaterial"] {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z'/%3E%3C/svg%3E") !important;
}

/* 8. Xuất Báo Cáo (export) */
[data-testid="stSidebarNav"] a[href*="/export"] span[data-testid="stIconMaterial"] {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z'/%3E%3C/svg%3E") !important;
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501/", wait_until="networkidle")
    page.wait_for_timeout(1000)

    # Apply CSS mask
    page.add_style_tag(content=TEST_CSS)
    page.wait_for_timeout(500)

    page.screenshot(path="d:/WebGenBench/docs/screenshots/sidebar_css_svg_mask.png")
    page.screenshot(path="C:/Users/jimmy/.gemini/antigravity/brain/c0cfbd33-cafc-4871-9c26-44df1a642285/sidebar_css_svg_mask.png")

    # Click on another link and check
    page.click("text=Phân Tích & Biểu Đồ")
    page.wait_for_timeout(1000)
    page.add_style_tag(content=TEST_CSS)
    page.screenshot(path="d:/WebGenBench/docs/screenshots/sidebar_css_svg_mask_analytics.png")
    browser.close()

print("CSS SVG Mask test completed!")
