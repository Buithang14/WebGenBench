"""dashboard/theme.py
Hệ thống Thiết kế Google Material Design 3 (Material You / M3) dành cho WebGenBench.
Cung cấp Design Tokens chuẩn hóa (Màu sắc, Kiểu chữ Typography, Độ cao Elevation, Bo góc Shapes)
và các thành phần UI (M3 Cards, Chips, Buttons, Banners, và Plotly Theme).
"""

import streamlit as st
from dashboard.icons import get_svg

# ==================== MATERIAL DESIGN 3 DESIGN TOKENS (CSS) ====================
M3_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Roboto+Flex:wght@400;500;600;700&display=swap');

:root {
    /* M3 Dynamic Baseline Color System (Google Blue Palette) */
    --md-sys-color-primary: #0B57D0;
    --md-sys-color-on-primary: #FFFFFF;
    --md-sys-color-primary-container: #D3E3FD;
    --md-sys-color-on-primary-container: #041E49;

    --md-sys-color-secondary: #00639B;
    --md-sys-color-on-secondary: #FFFFFF;
    --md-sys-color-secondary-container: #C2E7FF;
    --md-sys-color-on-secondary-container: #001D35;

    --md-sys-color-tertiary: #006874;
    --md-sys-color-on-tertiary: #FFFFFF;
    --md-sys-color-tertiary-container: #97F0FF;
    --md-sys-color-on-tertiary-container: #001F24;

    --md-sys-color-error: #BA1A1A;
    --md-sys-color-on-error: #FFFFFF;
    --md-sys-color-error-container: #FFDAD6;
    --md-sys-color-on-error-container: #410002;

    --md-sys-color-background: #F8F9FA;
    --md-sys-color-on-background: #1F1F1F;

    --md-sys-color-surface: #F8F9FA;
    --md-sys-color-on-surface: #1F1F1F;
    --md-sys-color-surface-variant: #E1E3E1;
    --md-sys-color-on-surface-variant: #444746;

    /* M3 Surface Container Roles (Tonal Elevation) */
    --md-sys-color-surface-container-lowest: #FFFFFF;
    --md-sys-color-surface-container-low: #F7F2FA;
    --md-sys-color-surface-container: #F0F4F9;
    --md-sys-color-surface-container-high: #E9EEF6;
    --md-sys-color-surface-container-highest: #E1E7F0;

    --md-sys-color-outline: #747775;
    --md-sys-color-outline-variant: #C4C7C5;
    --md-sys-color-surface-tint: #0B57D0;

    /* Semantic Status Tokens */
    --md-sys-color-success: #146C2E;
    --md-sys-color-success-container: #C4EED0;
    --md-sys-color-on-success-container: #002107;

    --md-sys-color-warning: #8F4C00;
    --md-sys-color-warning-container: #FFE08B;
    --md-sys-color-on-warning-container: #2A1700;

    --md-sys-color-info: #00639B;
    --md-sys-color-info-container: #C2E7FF;
    --md-sys-color-on-info-container: #001D35;

    /* M3 Shape Corner Tokens */
    --md-shape-corner-none: 0px;
    --md-shape-corner-extra-small: 4px;
    --md-shape-corner-small: 8px;
    --md-shape-corner-medium: 12px;
    --md-shape-corner-large: 16px;
    --md-shape-corner-extra-large: 28px;
    --md-shape-corner-full: 9999px;

    /* M3 Elevation Shadows */
    --md-elevation-1: 0px 1px 3px 1px rgba(0, 0, 0, 0.08), 0px 1px 2px 0px rgba(0, 0, 0, 0.12);
    --md-elevation-2: 0px 2px 6px 2px rgba(0, 0, 0, 0.08), 0px 1px 2px 0px rgba(0, 0, 0, 0.12);
    --md-elevation-3: 0px 4px 8px 3px rgba(0, 0, 0, 0.08), 0px 1px 3px 0px rgba(0, 0, 0, 0.14);
    --md-elevation-4: 0px 6px 10px 4px rgba(0, 0, 0, 0.08), 0px 2px 3px 0px rgba(0, 0, 0, 0.14);
}

/* ==================== GLOBAL TYPOGRAPHY & APP BASE ==================== */
html, body, p, div, label, .stMarkdown, .stText, .stButton, .stTextInput, .stSelectbox {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

span:not([data-testid="stIconMaterial"]):not([data-testid="stIconMaterial"] *) {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Ensure Material Symbols are NEVER overridden by general typography */
[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"] *,
.material-symbols-rounded,
.material-symbols-outlined,
.material-icons {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: 20px !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    display: inline-block !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
    -webkit-font-feature-settings: 'liga' !important;
    -webkit-font-smoothing: antialiased !important;
    width: 24px !important;
    min-width: 24px !important;
    overflow: hidden !important;
}

.stApp {
    background-color: var(--md-sys-color-surface) !important;
    color: var(--md-sys-color-on-surface) !important;
}

/* M3 Display & Headline Typography (Responsive Fluid clamp) */
.m3-display-title {
    font-size: clamp(1.5rem, 1.9vw, 2.2rem) !important;
    font-weight: 800 !important;
    color: var(--md-sys-color-on-surface) !important;
    letter-spacing: -0.5px;
    line-height: 1.35 !important;
    margin-top: 0.25rem !important;
    margin-bottom: 0.4rem !important;
    padding-top: 4px !important;
    padding-bottom: 4px !important;
    display: flex;
    align-items: center;
    gap: 14px;
    overflow: visible !important;
}

.m3-headline-subtitle {
    font-size: clamp(0.85rem, 0.95vw, 1.05rem) !important;
    color: var(--md-sys-color-on-surface-variant) !important;
    font-weight: 500 !important;
    margin-bottom: 1.6rem !important;
    line-height: 1.6;
}

/* ==================== M3 CARDS & CONTAINERS ==================== */
/* Filled Card (Default) */
.m3-card {
    background: var(--md-sys-color-surface-container) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    border-radius: var(--md-shape-corner-large) !important;
    padding: clamp(0.9rem, 1.2vw, 1.35rem) !important;
    box-shadow: var(--md-elevation-1) !important;
    transition: all 0.2s cubic-bezier(0.2, 0.0, 0, 1.0);
}

.m3-card:hover {
    box-shadow: var(--md-elevation-2) !important;
    background: var(--md-sys-color-surface-container-high) !important;
    border-color: var(--md-sys-color-primary) !important;
}

/* Elevated Card (White surface + Level 1 shadow) */
.m3-card-elevated {
    background: var(--md-sys-color-surface-container-lowest) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    border-radius: var(--md-shape-corner-large) !important;
    padding: clamp(0.95rem, 1.3vw, 1.45rem) !important;
    box-shadow: var(--md-elevation-1) !important;
    transition: all 0.2s cubic-bezier(0.2, 0.0, 0, 1.0);
}

.m3-card-elevated:hover {
    box-shadow: var(--md-elevation-3) !important;
    transform: translateY(-2px);
}

/* Outlined Card (Flat with outline) */
.m3-card-outlined {
    background: var(--md-sys-color-surface-container-lowest) !important;
    border: 1px solid var(--md-sys-color-outline) !important;
    border-radius: var(--md-shape-corner-large) !important;
    padding: clamp(0.9rem, 1.2vw, 1.35rem) !important;
}

.m3-card-value {
    font-size: clamp(1.6rem, 2vw, 2.3rem) !important;
    font-weight: 800 !important;
    color: var(--md-sys-color-primary) !important;
    line-height: 1.1;
    margin-bottom: 0.25rem;
}

.m3-card-label {
    font-size: clamp(0.75rem, 0.8vw, 0.85rem) !important;
    font-weight: 600 !important;
    color: var(--md-sys-color-on-surface-variant) !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

/* ==================== M3 CHIPS & BADGES ==================== */
.m3-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: var(--md-shape-corner-full);
    font-size: 0.82rem;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 6px;
    letter-spacing: 0.2px;
}

.m3-chip-primary {
    background-color: var(--md-sys-color-primary-container);
    color: var(--md-sys-color-on-primary-container);
    border: 1px solid transparent;
}

.m3-chip-secondary {
    background-color: var(--md-sys-color-secondary-container);
    color: var(--md-sys-color-on-secondary-container);
    border: 1px solid transparent;
}

.m3-chip-tertiary {
    background-color: var(--md-sys-color-tertiary-container);
    color: var(--md-sys-color-on-tertiary-container);
    border: 1px solid transparent;
}

.m3-chip-success {
    background-color: var(--md-sys-color-success-container);
    color: var(--md-sys-color-success);
    border: 1px solid transparent;
}

.m3-chip-warning {
    background-color: var(--md-sys-color-warning-container);
    color: var(--md-sys-color-warning);
    border: 1px solid transparent;
}

.m3-chip-error {
    background-color: var(--md-sys-color-error-container);
    color: var(--md-sys-color-error);
    border: 1px solid transparent;
}

.m3-chip-neutral {
    background-color: var(--md-sys-color-surface-container-highest);
    color: var(--md-sys-color-on-surface-variant);
    border: 1px solid var(--md-sys-color-outline-variant);
}

/* ==================== M3 CALLOUT BANNERS ==================== */
.m3-banner {
    border-radius: var(--md-shape-corner-medium);
    padding: 14px 18px;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    border: 1px solid transparent;
    font-size: 0.92rem;
    line-height: 1.5;
}

.m3-banner-info {
    background-color: var(--md-sys-color-info-container);
    color: var(--md-sys-color-on-info-container);
    border-color: #A6D4FF;
}

.m3-banner-success {
    background-color: var(--md-sys-color-success-container);
    color: var(--md-sys-color-on-success-container);
    border-color: #92E2AA;
}

.m3-banner-warning {
    background-color: var(--md-sys-color-warning-container);
    color: var(--md-sys-color-on-warning-container);
    border-color: #FFD159;
}

.m3-banner-error {
    background-color: var(--md-sys-color-error-container);
    color: var(--md-sys-color-on-error-container);
    border-color: #FFB4AB;
}

/* ==================== STREAMLIT COMPONENT OVERRIDES ==================== */

/* Buttons -> M3 Filled Button (40px height, full pill) */
.stButton > button {
    border-radius: var(--md-shape-corner-full) !important;
    padding: 0.65rem 1.6rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.2px !important;
    transition: all 0.2s cubic-bezier(0.2, 0.0, 0, 1.0) !important;
    border: none !important;
    box-shadow: var(--md-elevation-1) !important;
    height: auto !important;
}

.stButton > button:hover {
    box-shadow: var(--md-elevation-2) !important;
    transform: translateY(-1px);
}

.stButton > button:active {
    box-shadow: var(--md-elevation-1) !important;
    transform: translateY(0);
}

.stButton > button[kind="primary"] {
    background-color: var(--md-sys-color-primary) !important;
    color: var(--md-sys-color-on-primary) !important;
}

.stButton > button[kind="secondary"] {
    background-color: var(--md-sys-color-surface-container-high) !important;
    color: var(--md-sys-color-on-surface) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
}

/* Inputs & Form Fields -> M3 Outlined Text Field */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stNumberInput > div > div > input,
.stTextArea textarea {
    border-radius: var(--md-shape-corner-medium) !important;
    border: 1px solid var(--md-sys-color-outline) !important;
    background-color: var(--md-sys-color-surface-container-lowest) !important;
    color: var(--md-sys-color-on-surface) !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.95rem !important;
    transition: border 0.15s ease, box-shadow 0.15s ease !important;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus-within,
.stTextArea textarea:focus {
    border: 2px solid var(--md-sys-color-primary) !important;
    box-shadow: 0 0 0 3px var(--md-sys-color-primary-container) !important;
    outline: none !important;
}

/* Tabs -> M3 Primary Navigation Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 2px solid var(--md-sys-color-surface-container-highest) !important;
    gap: 8px !important;
    padding-bottom: 2px !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: var(--md-shape-corner-full) !important;
    padding: 8px 22px !important;
    font-weight: 600 !important;
    color: var(--md-sys-color-on-surface-variant) !important;
    border: none !important;
    background-color: transparent !important;
    transition: all 0.2s ease !important;
}

.stTabs [aria-selected="true"] {
    background-color: var(--md-sys-color-primary-container) !important;
    color: var(--md-sys-color-on-primary-container) !important;
    box-shadow: var(--md-elevation-1) !important;
}

/* Expander -> M3 Surface Container */
.streamlit-expanderHeader {
    border-radius: var(--md-shape-corner-medium) !important;
    background-color: var(--md-sys-color-surface-container) !important;
    font-weight: 600 !important;
    color: var(--md-sys-color-on-surface) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    padding: 10px 16px !important;
}

.streamlit-expanderContent {
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    border-top: none !important;
    border-radius: 0 0 var(--md-shape-corner-medium) var(--md-shape-corner-medium) !important;
    background-color: var(--md-sys-color-surface-container-lowest) !important;
    padding: 1.2rem !important;
}

/* Sidebar -> M3 Navigation Drawer (Responsive fluid % / vw, khóa kéo resize) */
section[data-testid="stSidebar"],
.stSidebar,
[data-testid="stSidebar"] {
    background-color: var(--md-sys-color-surface-container-high) !important;
    border-right: 1px solid var(--md-sys-color-outline-variant) !important;
    width: clamp(240px, 18vw, 320px) !important;
    min-width: clamp(230px, 16vw, 250px) !important;
    max-width: clamp(260px, 19vw, 330px) !important;
    resize: none !important;
    overflow-x: hidden !important;
}

[data-testid="stSidebar"] * {
    max-width: 100% !important;
    box-sizing: border-box !important;
}

[data-testid="stSidebarUserContent"] {
    width: 100% !important;
    padding-left: clamp(0.75rem, 1vw, 1.2rem) !important;
    padding-right: clamp(0.75rem, 1vw, 1.2rem) !important;
    overflow-x: hidden !important;
}

/* Vô hiệu hóa và ẩn hoàn toàn bộ kéo chỉnh kích thước (Disable Sidebar Resizer) */
[data-testid="stSidebarResizeHandle"],
div[style*="cursor: col-resize"],
div[style*="cursor: se-resize"],
div[style*="cursor: ew-resize"],
div[style*="col-resize"] {
    display: none !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
    visibility: hidden !important;
    cursor: default !important;
}

/* Streamlit Header Bar: Đảm bảo trong suốt và không che khuất tiêu đề trang */
header[data-testid="stHeader"],
.stHeader {
    background-color: transparent !important;
    background: transparent !important;
    pointer-events: none !important;
}

header[data-testid="stHeader"] * {
    pointer-events: auto !important;
}

/* Main Container: Co giãn linh hoạt theo tỷ lệ phần trăm (Fluid % / vw / vh) */
.block-container, [data-testid="stMainBlockContainer"] {
    padding-top: clamp(4.2rem, 5.8vh, 5.5rem) !important;
    padding-bottom: clamp(1.8rem, 3.5vh, 3.5rem) !important;
    padding-left: clamp(1rem, 2.5vw, 2.8rem) !important;
    padding-right: clamp(1rem, 2.5vw, 2.8rem) !important;
    max-width: 100% !important;
    width: 100% !important;
}

/* Sidebar Active Nav Link Pill (M3 Navigation Drawer Active Indicator) */
[data-testid="stSidebarNav"] a {
    white-space: nowrap !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: var(--md-sys-color-secondary-container) !important;
    color: var(--md-sys-color-on-secondary-container) !important;
    border-radius: var(--md-shape-corner-full) !important;
    font-weight: 700 !important;
    box-shadow: var(--md-elevation-1) !important;
}

[data-testid="stSidebarNav"] a:hover:not([aria-current="page"]) {
    background-color: var(--md-sys-color-surface-container-highest) !important;
    border-radius: var(--md-shape-corner-full) !important;
}

/* Dataframe & Tables */
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border-radius: var(--md-shape-corner-large) !important;
    overflow: hidden !important;
    box-shadow: var(--md-elevation-1) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    background-color: var(--md-sys-color-surface-container-lowest) !important;
}

/* Sliders -> M3 Slider Accent */
.stSlider [data-baseweb="slider"] {
    padding-top: 10px !important;
}

/* Metrics -> M3 Metric Container */
[data-testid="stMetric"] {
    background-color: var(--md-sys-color-surface-container) !important;
    padding: 12px 18px !important;
    border-radius: var(--md-shape-corner-large) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    box-shadow: var(--md-elevation-1) !important;
}

[data-testid="stMetricValue"] {
    font-weight: 800 !important;
    color: var(--md-sys-color-primary) !important;
}

[data-testid="stMetricLabel"] {
    font-weight: 600 !important;
    color: var(--md-sys-color-on-surface-variant) !important;
}

/* Alerts / Notification Callouts */
.stAlert {
    border-radius: var(--md-shape-corner-medium) !important;
    border: none !important;
    box-shadow: var(--md-elevation-1) !important;
}

div[data-testid="stNotification"] {
    border-radius: var(--md-shape-corner-medium) !important;
}
</style>
"""


# ==================== M3 PLOTLY COLOR PALETTE & LAYOUT ====================
M3_PALETTE = [
    "#0B57D0",  # Google Primary Blue
    "#006874",  # Tertiary Cyan-Teal
    "#984061",  # Deep Rose
    "#4A6267",  # Slate Slate-Teal
    "#7D5260",  # Neutral Plum
    "#146C2E",  # M3 Forest Green
    "#8F4C00",  # M3 Amber Orange
    "#5B5D72"   # Steel Neutral
]


def apply_m3_theme():
    """Áp dụng toàn bộ hệ thống phong cách Google Material Design 3 (M3) cho trang Streamlit."""
    st.markdown(M3_CSS, unsafe_allow_html=True)


def m3_header(title: str, subtitle: str = "", icon_name: str = "dashboard"):
    """Hiển thị tiêu đề chuẩn Material Design 3 Display Typography kết hợp icon vector SVG."""
    svg_icon = get_svg(icon_name, size=34, color="#0B57D0")
    st.markdown(f'<div class="m3-display-title">{svg_icon}<span>{title}</span></div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="m3-headline-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def m3_card(value: str, label: str, secondary: str = "", badge: str = "", badge_type: str = "primary", icon_name: str = ""):
    """Hiển thị thẻ Card chỉ số chuẩn Material Design 3 Elevation & Surface Container với icon SVG."""
    badge_svg = get_svg(icon_name, size=15, color="#041E49") + " " if icon_name else ""
    badge_html = f'<span class="m3-chip m3-chip-{badge_type}">{badge_svg}{badge}</span>' if badge else ""
    sec_html = f'<div style="font-size:0.85rem; color:#444746; margin-top:4px;">{secondary}</div>' if secondary else ""
    
    html = f"""
    <div class="m3-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div class="m3-card-value">{value}</div>
            {badge_html}
        </div>
        <div class="m3-card-label">{label}</div>
        {sec_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def m3_elevated_card(content_html: str):
    """Hiển thị khối Card nổi (Elevated Card) chuẩn M3 cho nội dung tùy biến."""
    html = f'<div class="m3-card-elevated">{content_html}</div>'
    st.markdown(html, unsafe_allow_html=True)


def m3_outlined_card(content_html: str):
    """Hiển thị khối Card viền ngoài (Outlined Card) chuẩn M3."""
    html = f'<div class="m3-card-outlined">{content_html}</div>'
    st.markdown(html, unsafe_allow_html=True)


def m3_banner(message: str, banner_type: str = "info", icon_name: str = "info"):
    """Hiển thị thông báo dạng Tonal Banner theo tiêu chuẩn Google Material 3."""
    svg = get_svg(icon_name, size=20, color="#0B57D0" if banner_type == "info" else "#1F1F1F")
    html = f"""
    <div class="m3-banner m3-banner-{banner_type}">
        <div style="flex-shrink:0;">{svg}</div>
        <div>{message}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def m3_chip(label: str, icon_name: str = "", chip_type: str = "primary") -> str:
    """Tạo chuỗi HTML cho chip chuẩn Material Design 3."""
    svg = (get_svg(icon_name, size=14, color="currentColor") + " ") if icon_name else ""
    return f'<span class="m3-chip m3-chip-{chip_type}">{svg}{label}</span>'


def m3_plotly_layout(height: int = 380, title: str = "") -> dict:
    """Cung cấp cấu hình layout Plotly đồng bộ hoàn hảo với Material Design 3 tokens."""
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        font=dict(
            family="Plus Jakarta Sans, Roboto, sans-serif",
            color="#1F1F1F",
            size=12
        ),
        margin=dict(l=40, r=40, t=40 if title else 20, b=40),
        xaxis=dict(
            gridcolor="#E1E3E1",
            linecolor="#C4C7C5",
            zerolinecolor="#C4C7C5",
            tickfont=dict(size=11, color="#444746")
        ),
        yaxis=dict(
            gridcolor="#E1E3E1",
            linecolor="#C4C7C5",
            zerolinecolor="#C4C7C5",
            tickfont=dict(size=11, color="#444746")
        ),
        hoverlabel=dict(
            bgcolor="#313033",
            font_size=12,
            font_family="Plus Jakarta Sans",
            font_color="#F4EFF4",
            bordercolor="rgba(0,0,0,0)"
        )
    )
    if title:
        layout["title"] = dict(
            text=title,
            font=dict(size=14, color="#1F1F1F", weight=700)
        )
    return layout
