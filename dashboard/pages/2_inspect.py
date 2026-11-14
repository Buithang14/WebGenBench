import streamlit as st
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from storage.db_manager import DBManager
from experiment.task_loader import load_task
from dashboard.theme import (
    apply_m3_theme,
    m3_header,
    m3_card,
    m3_banner,
    m3_chip,
    m3_elevated_card
)
from dashboard.icons import get_svg

st.set_page_config(page_title="Chi Tiết Lần Chạy - WebGenBench (M3)", page_icon=":material/manage_search:", layout="wide")
apply_m3_theme()

m3_header(
    title="Truy Vết & So Sánh Chi Tiết Lần Chạy",
    subtitle="Màn hình 2 theo Kế hoạch: Đối chiếu 3 ảnh kết xuất với ảnh thiết kế gốc (Ground Truth), thanh tra DOM layout và xem code",
    icon_name="search"
)

db = DBManager()
db.init_db()
runs = db.list_all_runs()

if not runs:
    m3_banner("Chưa có lượt chạy nào trong cơ sở dữ liệu.", banner_type="warning", icon_name="warning")
    st.stop()

run_ids = [r["run_id"] for r in runs]
selected_run_id = st.selectbox("Chọn Lượt Chạy (Run ID) cần kiểm tra:", options=run_ids, index=0)

try:
    trace = db.get_run_full_trace(selected_run_id)
except Exception as e:
    m3_banner(f"Không thể truy vết dữ liệu của {selected_run_id}: {e}", banner_type="error", icon_name="error")
    st.stop()

run_info = trace["run"]
proj_info = trace["project"]
screenshots = trace["screenshots"]
metrics_info = trace["automatic_metrics"]
score_info = trace["score"]

# Header tóm tắt thông tin lần chạy M3 Container
col_h1, col_h2, col_h3, col_h4 = st.columns(4)
with col_h1:
    st.metric("IDE / Agent", f"{run_info['ide_name'].upper()}", run_info.get('agent_name'))
with col_h2:
    st.metric("Bài tập / Điều kiện", f"{run_info['task_id']}", run_info['prompt_condition'])
with col_h3:
    st.metric("Tổng Điểm Chuẩn Hóa", f"{score_info.get('weighted_total_score', 0.0):.2f} / 100")
with col_h4:
    st.metric("Thời gian / Tổng LOC", f"{run_info['duration_seconds']}s", f"{proj_info.get('total_lines_of_code', 0)} LOC")

st.markdown(f"""
<div style="background:var(--md-sys-color-surface-container); border-radius:12px; padding:10px 16px; border:1px solid var(--md-sys-color-outline-variant); margin-bottom:1.5rem; font-size:0.88rem; color:#444746; display:flex; align-items:center; gap:8px; box-shadow: var(--md-elevation-1);">
    {get_svg("shield_check", size=18, color="#0B57D0")}
    <span><b>Mã SHA-256 xác thực:</b> <code>{proj_info.get('sha256_hash', 'N/A')}</code> &nbsp;|&nbsp; 🕒 <b>Thời điểm chạy:</b> <code>{run_info.get('start_time', 'N/A')}</code></span>
</div>
""", unsafe_allow_html=True)

# 4 Tab chuyên sâu
tab_visual, tab_metrics, tab_code, tab_runtime = st.tabs([
    "So Sánh Thị Giác & Viewports",
    "Chi Tiết 6 Tiêu Chí & Cảnh Báo",
    "Mã Nguồn Sinh Ra",
    "Lỗi Runtime Trình Duyệt"
])

# TAB 1: SO SÁNH THỊ GIÁC
with tab_visual:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        {get_svg("visibility", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.1rem; color:#1F1F1F;">So Sánh Giao Diện Sinh Ra Với Ảnh Thiết Kế Chuẩn</span>
    </div>
    """, unsafe_allow_html=True)
    
    ref_img_path = None
    try:
        task_data = load_task(run_info["task_id"])
        ref_img_path = ROOT_DIR / task_data.meta.reference_image
    except Exception:
        pass

    col_ref, col_actual = st.columns([1, 1.2])

    with col_ref:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:6px;">
            {get_svg("trophy", size=18, color="#0B57D0")}
            <span style="font-weight:700; font-size:1rem; color:#1F1F1F;">Ảnh Thiết Kế Chuẩn (Ground Truth)</span>
        </div>
        """, unsafe_allow_html=True)
        if ref_img_path and ref_img_path.exists():
            st.image(str(ref_img_path), caption=f"Mục tiêu thiết kế ({ref_img_path.name})", use_column_width=True)
        else:
            m3_banner("Không tìm thấy ảnh thiết kế chuẩn.", banner_type="info", icon_name="info")

    with col_actual:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:6px;">
            {get_svg("desktop", size=18, color="#0B57D0")}
            <span style="font-weight:700; font-size:1rem; color:#1F1F1F;">Ảnh Kết Xuất Thực Tế (Playwright Headless)</span>
        </div>
        """, unsafe_allow_html=True)
        
        viewport_map = {sc["viewport_width"]: sc for sc in screenshots}
        vp_selected = st.radio(
            "Chọn kích thước màn hình quan sát:",
            options=[1440, 768, 375],
            format_func=lambda x: f"Desktop {x}px" if x == 1440 else (f"Tablet {x}px" if x == 768 else f"Mobile {x}px"),
            horizontal=True
        )

        sc_target = viewport_map.get(vp_selected)
        if sc_target:
            img_p = ROOT_DIR / sc_target["image_path"]
            if img_p.exists():
                st.image(str(img_p), caption=f"Giao diện thực tế tại {vp_selected}px", use_column_width=True)
            else:
                m3_banner(f"Không tìm thấy file ảnh tại: {img_p}", banner_type="warning", icon_name="warning")
            
            if sc_target["has_horizontal_overflow"]:
                m3_banner(
                    "<b>PHÁT HIỆN LỖI TRÀN NGANG (Horizontal Overflow):</b> Trang web bị tràn khung hình khiến xuất hiện thanh cuộn ngang không mong muốn trên thiết bị này!",
                    banner_type="error",
                    icon_name="error"
                )
            else:
                m3_banner(
                    "Giao diện đáp ứng tốt (Responsive), không bị lỗi tràn thanh cuộn ngang trên viewport này.",
                    banner_type="success",
                    icon_name="check_circle"
                )

            audit = sc_target.get("layout_audit", {})
            issues = audit.get("layout_issues", [])
            if issues:
                with st.expander(f"Chi tiết {len(issues)} cảnh báo DOM Layout"):
                    for iss in issues:
                        st.write(f"- {iss}")
        else:
            m3_banner(f"Chưa có ảnh chụp cho viewport {vp_selected}px.", banner_type="info", icon_name="info")

# TAB 2: CHI TIẾT 6 TIÊU CHÍ & CẢNH BÁO
with tab_metrics:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        {get_svg("analytics", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.1rem; color:#1F1F1F;">Bảng Điểm Định Lượng 6 Tiêu Chí (Material 3 Cards)</span>
    </div>
    """, unsafe_allow_html=True)
    
    metric_labels = {
        "html_validity": ("1. HTML Validity", 0.15),
        "accessibility": ("2. Accessibility (a11y)", 0.20),
        "responsive": ("3. Responsive Design", 0.20),
        "design_similarity": ("4. Design Similarity", 0.25),
        "code_quality": ("5. Code Quality", 0.10),
        "runtime_cleanliness": ("6. Runtime Cleanliness", 0.10),
    }

    cols = st.columns(3)
    idx = 0
    for m_key, (m_label, default_w) in metric_labels.items():
        m_data = metrics_info.get(m_key, {})
        sc = m_data.get("raw_score", 0.0)
        issues = m_data.get("issues", [])
        
        status_color = "var(--md-sys-color-success)" if sc >= 85 else ("var(--md-sys-color-warning)" if sc >= 70 else "var(--md-sys-color-error)")
        status_chip_type = "success" if sc >= 85 else ("warning" if sc >= 70 else "error")
        status_text = "Xuất sắc" if sc >= 85 else ("Tốt" if sc >= 70 else "Cần cải thiện")

        with cols[idx % 3]:
            st.markdown(f"""
            <div class="m3-card" style="margin-bottom: 16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight: 700; color: #1F1F1F; font-size:1rem;">{m_label}</div>
                    {m3_chip(status_text, chip_type=status_chip_type)}
                </div>
                <div style="font-size: 2.2rem; font-weight: 800; color: {status_color}; margin: 6px 0;">{sc:.1f} <span style="font-size: 0.95rem; color: #444746;">/ 100</span></div>
                <div style="font-size: 0.85rem; color: #444746;">Đóng góp: <b>{(sc * default_w):.2f}đ</b> (Trọng số: {default_w*100:.0f}%)</div>
            </div>
            """, unsafe_allow_html=True)
            
            if issues:
                with st.expander(f"Cảnh báo ({len(issues)} vấn đề)"):
                    for iss in issues:
                        st.caption(f"• {iss}")
        idx += 1

# TAB 3: MÃ NGUỒN SINH RA
with tab_code:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        {get_svg("code", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.1rem; color:#1F1F1F;">Duyệt Toàn Bộ Mã Nguồn Dự Án</span>
    </div>
    """, unsafe_allow_html=True)
    proj_dir = ROOT_DIR / "outputs" / selected_run_id / "project"
    
    if proj_dir.exists():
        files = sorted([p for p in proj_dir.rglob("*") if p.is_file()])
        if files:
            file_tabs = st.tabs([f.name for f in files])
            for f_tab, f_path in zip(file_tabs, files):
                with f_tab:
                    ext = f_path.suffix.lower()
                    lang = "html" if ext == ".html" else ("css" if ext == ".css" else ("javascript" if ext == ".js" else "text"))
                    content = f_path.read_text(encoding="utf-8", errors="ignore")
                    st.caption(f"Đường dẫn: `{f_path.relative_to(ROOT_DIR)}` ({len(content.splitlines())} dòng)")
                    st.code(content, language=lang)
        else:
            m3_banner("Không tìm thấy file mã nguồn nào trong thư mục project.", banner_type="info", icon_name="info")
    else:
        m3_banner("Thư mục project không tồn tại.", banner_type="warning", icon_name="warning")

# TAB 4: LỖI RUNTIME TRÌNH DUYỆT
with tab_runtime:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        {get_svg("warning", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.1rem; color:#1F1F1F;">Báo Cáo Runtime từ Playwright Chromium</span>
    </div>
    """, unsafe_allow_html=True)
    report_file = ROOT_DIR / "outputs" / selected_run_id / "render_report.json"
    
    if report_file.exists():
        report_data = json.loads(report_file.read_text(encoding="utf-8"))
        errs = report_data.get("runtime_errors", {})
        
        c_errs = errs.get("console_errors", [])
        p_errs = errs.get("page_errors", [])
        f_reqs = errs.get("failed_requests", [])

        col_e1, col_e2, col_e3 = st.columns(3)
        col_e1.metric("Console Errors", len(c_errs))
        col_e2.metric("Page JS Errors", len(p_errs))
        col_e3.metric("Failed Network Requests", len(f_reqs))

        if not c_errs and not p_errs and not f_reqs:
            m3_banner("Hoàn hảo! Không có bất kỳ lỗi JavaScript runtime hay request tài nguyên nào bị lỗi 404/500.", banner_type="success", icon_name="check_circle")
        else:
            if c_errs:
                st.error("Console Errors:")
                for e in c_errs:
                    st.code(e)
            if p_errs:
                st.error("Page Errors:")
                for e in p_errs:
                    st.code(e)
            if f_reqs:
                st.error("Failed Requests:")
                st.json(f_reqs)
    else:
        m3_banner("Chưa có file render_report.json cho lượt chạy này.", banner_type="info", icon_name="info")
