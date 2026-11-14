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

    /* M3 Spacing Tokens */
    --md-spacing-xs: 4px;
    --md-spacing-s: 8px;
    --md-spacing-m: 16px;
    --md-spacing-l: 24px;
    --md-spacing-xl: 32px;
    --md-spacing-2xl: 48px;
}

/* ==================== GLOBAL TYPOGRAPHY & APP BASE ==================== */
html, body, p, div, label, .stMarkdown, .stText, .stButton, .stTextInput, .stSelectbox {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

span:not([data-testid="stIconMaterial"]):not([data-testid="stIconMaterial"] *):not([data-testid="stExpanderIcon"]):not([data-testid="stExpanderIcon"] *) {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Ensure Material Symbols are NEVER overridden by general typography */
[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"] *,
[data-testid="stExpanderIcon"],
[data-testid="stExpanderIcon"] *,
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
    margin-top: 0.5rem !important;
    margin-bottom: 0.6rem !important;
    padding-top: 6px !important;
    padding-bottom: 6px !important;
    display: flex;
    align-items: center;
    gap: 16px;
    overflow: visible !important;
}

.m3-headline-subtitle {
    font-size: clamp(0.88rem, 0.98vw, 1.08rem) !important;
    color: var(--md-sys-color-on-surface-variant) !important;
    font-weight: 500 !important;
    margin-bottom: 2rem !important;
    line-height: 1.65;
}

/* ==================== M3 CARDS & CONTAINERS ==================== */
/* Filled Card (Default) */
.m3-card {
    background: var(--md-sys-color-surface-container) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    border-radius: var(--md-shape-corner-large) !important;
    padding: clamp(1.2rem, 1.6vw, 1.75rem) !important;
    box-shadow: var(--md-elevation-1) !important;
    transition: all 0.2s cubic-bezier(0.2, 0.0, 0, 1.0);
    margin-bottom: 1.25rem !important;
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
    padding: clamp(1.3rem, 1.75vw, 1.9rem) !important;
    box-shadow: var(--md-elevation-1) !important;
    transition: all 0.2s cubic-bezier(0.2, 0.0, 0, 1.0);
    margin-bottom: 1.25rem !important;
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
    padding: clamp(1.2rem, 1.6vw, 1.75rem) !important;
    margin-bottom: 1.25rem !important;
}

.m3-card-value {
    font-size: clamp(1.6rem, 2vw, 2.3rem) !important;
    font-weight: 800 !important;
    color: var(--md-sys-color-primary) !important;
    line-height: 1.1;
    margin-bottom: 0.45rem !important;
}

.m3-card-label {
    font-size: clamp(0.75rem, 0.8vw, 0.85rem) !important;
    font-weight: 600 !important;
    color: var(--md-sys-color-on-surface-variant) !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 0.35rem !important;
}

/* ==================== M3 CHIPS & BADGES ==================== */
.m3-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px !important;
    border-radius: var(--md-shape-corner-full);
    font-size: 0.82rem;
    font-weight: 600;
    margin-right: 8px !important;
    margin-bottom: 8px !important;
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
    padding: 18px 24px !important;
    margin-bottom: 1.6rem !important;
    display: flex;
    align-items: flex-start;
    gap: 16px !important;
    border: 1px solid transparent;
    font-size: 0.95rem;
    line-height: 1.55;
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

/* Buttons -> M3 Filled Button (42px height, full pill) */
.stButton > button,
.stButton button,
.stDownloadButton > button,
.stDownloadButton button,
[data-testid="stDownloadButton"] button {
    border-radius: var(--md-shape-corner-full) !important;
    padding: 0.75rem 1.85rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.2px !important;
    transition: all 0.2s cubic-bezier(0.2, 0.0, 0, 1.0) !important;
    border: none !important;
    box-shadow: var(--md-elevation-1) !important;
    min-height: 42px !important;
    height: auto !important;
    margin-top: 0.25rem !important;
    margin-bottom: 0.25rem !important;
}

.stButton > button:hover,
.stButton button:hover,
.stDownloadButton > button:hover,
.stDownloadButton button:hover,
[data-testid="stDownloadButton"] button:hover {
    box-shadow: var(--md-elevation-2) !important;
    transform: translateY(-1px);
}

.stButton > button:active,
.stButton button:active,
.stDownloadButton > button:active,
.stDownloadButton button:active,
[data-testid="stDownloadButton"] button:active {
    box-shadow: var(--md-elevation-1) !important;
    transform: translateY(0);
}

.stButton > button[kind="primary"],
.stButton button[kind="primary"] {
    background-color: var(--md-sys-color-primary) !important;
    color: var(--md-sys-color-on-primary) !important;
}

.stButton > button[kind="secondary"],
.stButton button[kind="secondary"] {
    background-color: var(--md-sys-color-surface-container-high) !important;
    color: var(--md-sys-color-on-surface) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
}

/* Download Button -> M3 Outlined / Tonal Button */
.stDownloadButton > button,
.stDownloadButton button,
[data-testid="stDownloadButton"] button {
    border: 1px solid var(--md-sys-color-primary) !important;
    background-color: var(--md-sys-color-surface-container-lowest) !important;
    color: var(--md-sys-color-primary) !important;
    box-shadow: var(--md-elevation-1) !important;
}

.stDownloadButton > button:hover,
.stDownloadButton button:hover,
[data-testid="stDownloadButton"] button:hover {
    background-color: var(--md-sys-color-primary-container) !important;
    color: var(--md-sys-color-on-primary-container) !important;
    box-shadow: var(--md-elevation-2) !important;
    transform: translateY(-1px);
}

/* Inputs & Form Fields -> M3 Outlined Text Field with Generous Padding */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stTextArea textarea {
    border-radius: var(--md-shape-corner-medium) !important;
    border: 1px solid var(--md-sys-color-outline) !important;
    background-color: var(--md-sys-color-surface-container-lowest) !important;
    color: var(--md-sys-color-on-surface) !important;
    padding: 0.75rem 1.15rem !important;
    font-size: 0.95rem !important;
    min-height: 44px !important;
    transition: border 0.15s ease, box-shadow 0.15s ease !important;
}

.stMultiSelect [data-rac][role="group"] {
    border-radius: var(--md-shape-corner-medium) !important;
    border: 1px solid var(--md-sys-color-outline) !important;
    background-color: var(--md-sys-color-surface-container-lowest) !important;
    min-height: 44px !important;
    padding: 4px 6px !important;
    display: flex !important;
    flex-wrap: wrap !important;
    align-items: center !important;
}

.stMultiSelect [data-testid="stMultiSelectTagsContainer"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 4px !important;
    width: auto !important;
    max-width: 100% !important;
}

.stMultiSelect [data-testid="stMultiSelectTagsContainer"] > span {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 4px !important;
    width: auto !important;
}

.stMultiSelect input[data-rac] {
    min-width: 28px !important;
    flex: 1 1 28px !important;
    width: auto !important;
}

.stTextInput, .stSelectbox, .stMultiSelect, .stNumberInput, .stTextArea {
    margin-bottom: 0.85rem !important;
}

/* Multiselect Tags -> Material 3 Filter Chips */
[data-testid="stMultiSelect"] span[data-tag],
[data-baseweb="tag"] {
    background-color: var(--md-sys-color-primary) !important;
    color: var(--md-sys-color-on-primary) !important;
    border-radius: 8px !important;
    padding: 3px 8px !important;
    margin: 2px 2px !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    width: auto !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}
[data-testid="stMultiSelect"] span[data-tag] > span,
[data-baseweb="tag"] > span {
    color: var(--md-sys-color-on-primary) !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    display: inline-block !important;
    width: auto !important;
}
[data-testid="stMultiSelect"] span[data-tag] button,
[data-baseweb="tag"] button {
    color: var(--md-sys-color-on-primary) !important;
}
[data-testid="stMultiSelect"] span[data-tag] svg,
[data-baseweb="tag"] svg {
    stroke: var(--md-sys-color-on-primary) !important;
    fill: var(--md-sys-color-on-primary) !important;
}

[data-testid="stWidgetLabel"] {
    margin-bottom: 6px !important;
    padding-bottom: 2px !important;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus-within,
.stTextArea textarea:focus {
    border: 2px solid var(--md-sys-color-primary) !important;
    box-shadow: 0 0 0 3px var(--md-sys-color-primary-container) !important;
    outline: none !important;
}

/* ==================== TABS & CÁC MỤC (M3 PRIMARY TABS & SECTION ITEMS - 1 DÒNG DUY NHẤT) ==================== */
div[data-testid="stTabs"] {
    margin-top: 1.0rem !important;
    margin-bottom: 2.0rem !important;
}

/* Tab List / Khóa cứng danh sách các mục tab thành 1 DÒNG DUY NHẤT */
div[data-testid="stTabs"] div[role="tablist"],
div[role="tablist"],
.stTabs [role="tablist"],
.stTabs [data-baseweb="tab-list"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    white-space: nowrap !important;
    background-color: transparent !important;
    border-bottom: 1.5px solid var(--md-sys-color-surface-container-highest) !important;
    gap: 8px !important;
    padding-top: 4px !important;
    padding-bottom: 10px !important;
    margin-bottom: 1.4rem !important;
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
    height: 48px !important;
    min-height: 48px !important;
    max-height: 48px !important;
    align-items: center !important;
}

div[role="tablist"]::-webkit-scrollbar,
div[data-testid="stTabs"] div[role="tablist"]::-webkit-scrollbar {
    display: none !important;
    height: 0px !important;
    width: 0px !important;
}

/* Từng mục tab (Tab Item Button / M3 Pill kích thước gọn gàng, hiển thị 1 dòng) */
div[data-testid="stTab"],
[role="tab"],
.stTabs [role="tab"],
.stTabs [data-baseweb="tab"] {
    flex-shrink: 0 !important;
    border-radius: var(--md-shape-corner-full, 9999px) !important;
    padding: 6px 14px !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    letter-spacing: 0.1px !important;
    color: var(--md-sys-color-on-surface-variant) !important;
    background-color: var(--md-sys-color-surface-container) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
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

/* Nội dung chữ bên trong từng tab */
div[data-testid="stTab"] p,
[role="tab"] p,
.stTabs [role="tab"] p,
div[data-testid="stTab"] [data-testid="stMarkdownContainer"] p {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.25 !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    color: inherit !important;
    white-space: nowrap !important;
}

/* Hiệu ứng hover cho từng mục tab */
div[data-testid="stTab"]:hover:not([aria-selected="true"]),
[role="tab"]:hover:not([aria-selected="true"]) {
    background-color: var(--md-sys-color-surface-container-high) !important;
    border-color: var(--md-sys-color-primary) !important;
    color: var(--md-sys-color-primary) !important;
}

/* Mục tab đang được chọn (Active M3 Pill) */
div[data-testid="stTab"][aria-selected="true"],
[role="tab"][aria-selected="true"],
div[data-testid="stTab"][data-selected="true"],
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: var(--md-sys-color-primary-container) !important;
    color: var(--md-sys-color-on-primary-container) !important;
    border: 1.5px solid var(--md-sys-color-primary) !important;
    font-weight: 700 !important;
    box-shadow: var(--md-elevation-1) !important;
}

div[data-testid="stTab"][aria-selected="true"] p,
[role="tab"][aria-selected="true"] p,
div[data-testid="stTab"][aria-selected="true"] [data-testid="stMarkdownContainer"] p {
    font-weight: 700 !important;
    color: var(--md-sys-color-on-primary-container) !important;
}

/* Triệt tiêu thanh line indicator 2px mặc định chèn dính vào tab pill */
.react-aria-SelectionIndicator,
div[data-testid="stTab"] .react-aria-SelectionIndicator,
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] {
    display: none !important;
    height: 0px !important;
    opacity: 0 !important;
}

/* Khung nội dung của từng mục tab (Tab Panel) - Bổ sung khoảng đệm rộng rãi */
div[data-testid="stTabPanel"],
div[role="tabpanel"],
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.8rem !important;
    padding-bottom: 2.2rem !important;
    padding-left: 0.25rem !important;
    padding-right: 0.25rem !important;
    margin-top: 0.5rem !important;
}

/* Chuẩn hóa khoảng cách đệm (Padding & Margin) cho tiêu đề các mục (Section Items) */
.m3-section-title,
.stTabs h4, .stTabs h5,
h4, h5 {
    padding-top: 8px !important;
    padding-bottom: 6px !important;
    margin-top: 1.4rem !important;
    margin-bottom: 1.2rem !important;
    line-height: 1.45 !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

/* Expander -> M3 Surface Container */
.streamlit-expanderHeader,
[data-testid="stExpander"] details summary {
    border-radius: var(--md-shape-corner-medium) !important;
    background-color: var(--md-sys-color-surface-container) !important;
    font-weight: 600 !important;
    color: var(--md-sys-color-on-surface) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    padding: 14px 22px !important;
}

.streamlit-expanderContent,
[data-testid="stExpanderDetails"],
[data-testid="stExpander"] details > div:last-child {
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    border-top: none !important;
    border-radius: 0 0 var(--md-shape-corner-medium) var(--md-shape-corner-medium) !important;
    background-color: var(--md-sys-color-surface-container-lowest) !important;
    padding: 1.6rem 2rem !important;
}

[data-testid="stExpander"] {
    margin-bottom: 1.5rem !important;
}

/* Sidebar Expander Customization: gọn gàng chuẩn M3 trong thanh điều hướng */
section[data-testid="stSidebar"] [data-testid="stExpander"] details summary,
.stSidebar [data-testid="stExpander"] details summary {
    padding: 10px 14px !important;
    font-size: 0.92rem !important;
}

section[data-testid="stSidebar"] [data-testid="stExpanderDetails"],
section[data-testid="stSidebar"] [data-testid="stExpander"] details > div:last-child,
.stSidebar [data-testid="stExpanderDetails"],
.stSidebar [data-testid="stExpander"] details > div:last-child {
    padding: 10px 8px !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] {
    margin-top: 10px !important;
    margin-bottom: 1rem !important;
}

/* Sidebar MultiSelect Tag styling: không bị co rúm chữ */
[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-tag],
.stSidebar [data-testid="stMultiSelect"] span[data-tag] {
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
    min-width: 46px !important;
    width: auto !important;
    flex-shrink: 0 !important;
    background-color: var(--md-sys-color-primary) !important;
    color: var(--md-sys-color-on-primary) !important;
    border-radius: 8px !important;
    padding: 3px 8px !important;
    margin: 2px !important;
}

[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-tag] > span,
.stSidebar [data-testid="stMultiSelect"] span[data-tag] > span {
    display: inline-block !important;
    width: auto !important;
    color: var(--md-sys-color-on-primary) !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
}

/* Sidebar -> M3 Navigation Drawer: Khóa cứng độ rộng bất biến 100% đồng nhất giữa tất cả các trang */
section[data-testid="stSidebar"]:not([data-collapsed="true"]),
.stSidebar:not([data-collapsed="true"]),
[data-testid="stSidebar"]:not([data-collapsed="true"]) {
    background-color: var(--md-sys-color-surface-container-high) !important;
    border-right: 1px solid var(--md-sys-color-outline-variant) !important;
    width: clamp(290px, 19.5vw, 320px) !important;
    min-width: clamp(290px, 19.5vw, 320px) !important;
    max-width: clamp(290px, 19.5vw, 320px) !important;
    flex: 0 0 clamp(290px, 19.5vw, 320px) !important;
    resize: none !important;
    overflow-x: hidden !important;
    box-sizing: border-box !important;
}

/* Sidebar khi bấm thu gọn (data-collapsed="true"): Triệt tiêu độ rộng & lề để nhường toàn bộ diện tích cho nội dung chính */
section[data-testid="stSidebar"][data-collapsed="true"],
.stSidebar[data-collapsed="true"],
[data-testid="stSidebar"][data-collapsed="true"] {
    width: 0px !important;
    min-width: 0px !important;
    max-width: 0px !important;
    flex: 0 0 0px !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    overflow: hidden !important;
    pointer-events: none !important;
}

/* Đảm bảo Main Viewport co giãn 100% lấp đầy toàn bộ màn hình khi thu gọn */
.stAppViewContainer {
    width: 100% !important;
    max-width: 100% !important;
}

.stMain {
    width: 100% !important;
    max-width: 100% !important;
    flex: 1 1 100% !important;
}

[data-testid="stSidebar"] * {
    max-width: 100% !important;
    box-sizing: border-box !important;
}

[data-testid="stSidebarUserContent"] {
    width: 100% !important;
    padding-left: clamp(1.15rem, 1.4vw, 1.5rem) !important;
    padding-right: clamp(1.15rem, 1.4vw, 1.5rem) !important;
    padding-top: 1.6rem !important;
    padding-bottom: 4rem !important;
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

/* Ẩn nút Deploy thừa trên localhost */
.stAppDeployButton,
[data-testid="stAppDeployButton"],
.stDeployButton,
[data-testid="stDeployButton"] {
    display: none !important;
}

/* Ẩn container chứa thẻ <style> để triệt tiêu flex gap thừa phía trên tiêu đề */
div[data-testid="stElementContainer"]:has(style):not(:has(.m3-card)):not(:has(.m3-display-title)):not(:has(.m3-banner)) {
    display: none !important;
}

/* Streamlit Header Bar: Đảm bảo trong suốt, thu gọn tối đa và không che khuất tiêu đề trang */
header[data-testid="stHeader"],
.stHeader {
    background-color: transparent !important;
    background: transparent !important;
    height: 2.25rem !important;
    min-height: 2.25rem !important;
    pointer-events: none !important;
    z-index: 99 !important;
}

header[data-testid="stHeader"] * {
    pointer-events: auto !important;
}

/* Main Container: Co giãn linh hoạt theo tỷ lệ phần trăm với padding thoáng đãng, rộng rãi */
.block-container, [data-testid="stMainBlockContainer"] {
    padding-top: clamp(2rem, 3.2vh, 3rem) !important;
    padding-bottom: clamp(3.5rem, 6vh, 6rem) !important;
    padding-left: clamp(1.8rem, 3.5vw, 4.2rem) !important;
    padding-right: clamp(1.8rem, 3.5vw, 4.2rem) !important;
    max-width: 100% !important;
    width: 100% !important;
}

/* Sidebar Active Nav Link Pill (M3 Navigation Drawer Active Indicator) */
[data-testid="stSidebarNav"] {
    padding-top: 0.8rem !important;
    padding-bottom: 1.2rem !important;
    width: 100% !important;
}

[data-testid="stSidebarNav"] ul {
    padding-left: 0.25rem !important;
    padding-right: 0.25rem !important;
    gap: 4px !important;
    display: flex !important;
    flex-direction: column !important;
}

[data-testid="stSidebarNav"] a {
    white-space: nowrap !important;
    padding: 10px 18px !important;
    margin-bottom: 4px !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
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

/* Biểu tượng vector SVG chuẩn Google Material Symbols cho thanh menu Sidebar */
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

/* Dataframe & Tables -> M3 Elevated Table Container */
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border-radius: var(--md-shape-corner-large) !important;
    overflow: hidden !important;
    box-shadow: var(--md-elevation-1) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    background-color: var(--md-sys-color-surface-container-lowest) !important;
    padding: 10px !important;
    margin: 1.4rem 0 !important;
}

/* Sliders -> M3 Slider Accent with Padding */
.stSlider {
    padding: 0.6rem 0.25rem 1.25rem 0.25rem !important;
    margin-bottom: 1rem !important;
}

.stSlider [data-baseweb="slider"] {
    padding-top: 12px !important;
}

.stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: var(--md-sys-color-primary) !important;
    border: 2px solid #FFFFFF !important;
    box-shadow: var(--md-elevation-2) !important;
    width: 20px !important;
    height: 20px !important;
}

.stSlider [data-baseweb="slider"] div:has(> div[role="slider"]) {
    height: 6px !important;
    border-radius: var(--md-shape-corner-full) !important;
}

/* Progress Bar -> M3 Linear Progress Indicator */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--md-sys-color-primary) 0%, var(--md-sys-color-secondary) 100%) !important;
    border-radius: var(--md-shape-corner-full) !important;
    height: 8px !important;
}

.stProgress > div > div > div {
    background-color: var(--md-sys-color-surface-container-highest) !important;
    border-radius: var(--md-shape-corner-full) !important;
    height: 8px !important;
    overflow: hidden !important;
}

/* File Uploader -> M3 File Dropzone Container */
[data-testid="stFileUploader"] {
    background-color: var(--md-sys-color-surface-container-low) !important;
    border: 2px dashed var(--md-sys-color-outline-variant) !important;
    border-radius: var(--md-shape-corner-large) !important;
    padding: 1.8rem 2.2rem !important;
    margin-bottom: 1.5rem !important;
    transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] {
    padding: 1.4rem !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--md-sys-color-primary) !important;
    background-color: var(--md-sys-color-surface-container) !important;
}

[data-testid="stFileUploader"] button {
    border-radius: var(--md-shape-corner-full) !important;
    background-color: var(--md-sys-color-secondary-container) !important;
    color: var(--md-sys-color-on-secondary-container) !important;
    font-weight: 600 !important;
    border: none !important;
    padding: 0.6rem 1.4rem !important;
}

/* Radio Buttons & Checkboxes -> M3 Selection Controls */
.stRadio > div, [data-testid="stRadio"] > div {
    gap: 12px !important;
}

.stRadio [data-testid="stWidgetLabel"] p,
.stCheckbox [data-testid="stWidgetLabel"] p {
    font-weight: 600 !important;
    color: var(--md-sys-color-on-surface) !important;
    font-size: 0.95rem !important;
    margin-bottom: 8px !important;
}

.stRadio div[role="radiogroup"] label,
[data-testid="stRadio"] label,
.stCheckbox label,
[data-testid="stCheckbox"] label {
    background: var(--md-sys-color-surface-container-lowest) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    border-radius: var(--md-shape-corner-medium) !important;
    padding: 10px 18px !important;
    margin: 4px 0 !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}

.stRadio div[role="radiogroup"] label:hover,
[data-testid="stRadio"] label:hover,
.stCheckbox label:hover,
[data-testid="stCheckbox"] label:hover {
    background: var(--md-sys-color-surface-container) !important;
    border-color: var(--md-sys-color-primary) !important;
}

.stRadio div[role="radiogroup"] label:has(input:checked),
[data-testid="stRadio"] label:has(input:checked) {
    background: var(--md-sys-color-primary-container) !important;
    border-color: var(--md-sys-color-primary) !important;
    color: var(--md-sys-color-on-primary-container) !important;
    font-weight: 700 !important;
}

/* Code Blocks -> M3 Dark Surface Container */
.stCode, [data-testid="stCode"] {
    background-color: #1A1C1E !important;
    border: 1px solid #444746 !important;
    border-radius: var(--md-shape-corner-medium) !important;
    overflow: hidden !important;
    margin: 1.4rem 0 !important;
    padding: 2px !important;
}

.stCode pre {
    background-color: transparent !important;
    font-family: 'Roboto Flex', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    padding: 1.35rem 1.75rem !important;
    color: #E2E2E6 !important;
}

/* Dividers -> M3 Outline Variant */
hr, [data-testid="stDivider"] {
    border: none !important;
    border-top: 1px solid var(--md-sys-color-outline-variant) !important;
    margin: 2rem 0 !important;
    opacity: 0.8 !important;
}

/* Metrics -> M3 Metric Container */
[data-testid="stMetric"] {
    background-color: var(--md-sys-color-surface-container) !important;
    padding: 18px 24px !important;
    border-radius: var(--md-shape-corner-large) !important;
    border: 1px solid var(--md-sys-color-outline-variant) !important;
    box-shadow: var(--md-elevation-1) !important;
    margin-bottom: 0.85rem !important;
}

[data-testid="stMetricValue"] {
    font-weight: 800 !important;
    color: var(--md-sys-color-primary) !important;
}

[data-testid="stMetricLabel"] {
    font-weight: 600 !important;
    color: var(--md-sys-color-on-surface-variant) !important;
}

/* Streamlit Columns & Horizontal Blocks: Bổ sung khoảng đệm giữa các cột */
[data-testid="column"] {
    padding: 0.5rem 0.8rem !important;
}

div[data-testid="stHorizontalBlock"] {
    gap: 1.25rem !important;
}

/* Alerts / Notification Callouts */
.stAlert {
    border-radius: var(--md-shape-corner-medium) !important;
    border: none !important;
    box-shadow: var(--md-elevation-1) !important;
    padding: 16px 22px !important;
    margin-bottom: 1.4rem !important;
}

div[data-testid="stNotification"] {
    border-radius: var(--md-shape-corner-medium) !important;
    padding: 14px 20px !important;
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
