import streamlit as st
import json
import pandas as pd
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

st.set_page_config(
    page_title="Chi Tiết Lần Chạy - WebGenBench (M3)",
    page_icon=":material/manage_search:",
    layout="wide"
)
apply_m3_theme()

m3_header(
    title="Khu Vực Soi Chi Tiết Kết Quả (Run Inspector)",
    icon_name="search"
)

db = DBManager()
db.init_db()
runs = db.list_all_runs()

if not runs:
    m3_banner("Chưa có lượt chạy nào trong cơ sở dữ liệu. Hãy thực hiện chạy benchmark trong trang Điều Khiển Thí Nghiệm!", banner_type="warning", icon_name="warning")
    st.stop()

# 1. Bộ lọc chọn lượt chạy: Chọn run_001, run_002...
filter_col1, filter_col2, filter_col3 = st.columns([1.5, 1, 1])

all_ides = sorted(list(set(r["ide_name"] for r in runs)))
all_tasks = sorted(list(set(r["task_id"] for r in runs)))

with filter_col2:
    f_ide = st.selectbox("Lọc theo IDE:", options=["Tất cả"] + all_ides)
with filter_col3:
    f_task = st.selectbox("Lọc theo Bài tập:", options=["Tất cả"] + all_tasks)

filtered_runs = [
    r for r in runs
    if (f_ide == "Tất cả" or r["ide_name"] == f_ide)
    and (f_task == "Tất cả" or r["task_id"] == f_task)
]

if not filtered_runs:
    filtered_runs = runs

run_ids = [r["run_id"] for r in filtered_runs]
with filter_col1:
    selected_run_id = st.selectbox(
        "Bộ lọc chọn lượt chạy (Run ID):",
        options=run_ids,
        index=0,
        format_func=lambda rid: f"{rid} - {next((r['ide_name'].upper() for r in runs if r['run_id']==rid), '')} ({next((r['task_id'] for r in runs if r['run_id']==rid), '')})"
    )

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

# Header tóm tắt thông tin lần chạy chuẩn Material Design 3
col_h1, col_h2, col_h3, col_h4 = st.columns(4)
with col_h1:
    st.metric("Công Cụ IDE / Agent", f"{run_info['ide_name'].upper()}", run_info.get('agent_name'))
with col_h2:
    st.metric("Bài Tập & Điều Kiện", f"{run_info['task_id']}", f"{run_info['prompt_condition']}")
with col_h3:
    st.metric("Tổng Điểm Chuẩn Hóa", f"{score_info.get('weighted_total_score', 0.0):.2f} / 100")
with col_h4:
    st.metric("Thời Gian / Dòng Mã (LOC)", f"{run_info['duration_seconds']}s", f"{proj_info.get('total_lines_of_code', 0)} LOC")

st.markdown(f"""
<div style="background:var(--md-sys-color-surface-container); border-radius:14px; padding:14px 22px; border:1px solid var(--md-sys-color-outline-variant); margin-bottom:1.8rem; font-size:0.9rem; color:#444746; display:flex; align-items:center; gap:10px; box-shadow: var(--md-elevation-1);">
    {get_svg("shield_check", size=20, color="#0B57D0")}
    <span><b>Mã SHA-256 xác thực:</b> <code>{proj_info.get('sha256_hash', 'N/A')}</code> &nbsp;|&nbsp; {get_svg("schedule", size=16, color="#0B57D0")} <b>Thời điểm chạy:</b> <code>{run_info.get('start_time', 'N/A')}</code> &nbsp;|&nbsp; {get_svg("label", size=16, color="#0B57D0")} <b>Mã ẩn danh:</b> <code>{run_info.get('blind_code', 'N/A')}</code></span>
</div>
""", unsafe_allow_html=True)

# 4 Tab chuyên sâu theo đúng đặc tả Giao diện.docx
tab_visual, tab_metrics, tab_code, tab_runtime = st.tabs([
    "1. So Sánh Ảnh Trực Quan",
    "2. Bảng Điểm 6 Tiêu Chí & Lỗi",
    "3. Trình Xem Code",
    "4. Nhật Ký Lỗi Runtime"
])

# ==================== TAB 1: SO SÁNH ẢNH TRỰC QUAN ĐẶT CẠNH NHAU ====================
with tab_visual:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; padding-top:10px; margin-top:8px; margin-bottom:18px;">
        {get_svg("visibility", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">So Sánh Ảnh Trực Quan: Ảnh Gốc Mẫu vs 3 Cỡ Màn Hình Thực Tế</span>
    </div>
    """, unsafe_allow_html=True)
    
    ref_img_path = None
    try:
        task_data = load_task(run_info["task_id"])
        ref_img_path = ROOT_DIR / task_data.meta.reference_image
    except Exception:
        pass

    viewport_map = {sc["viewport_width"]: sc for sc in screenshots}

    col_ref, col_actual = st.columns([1, 1.2], gap="large")

    with col_ref:
        st.markdown(f"""
        <div style="background:var(--md-sys-color-surface-container); border-radius:14px; padding:14px 18px; border:1px solid var(--md-sys-color-outline-variant); margin-bottom:12px; display:flex; align-items:center; gap:8px;">
            {get_svg("trophy", size=20, color="#0B57D0")}
            <span style="font-weight:700; color:#0B57D0; font-size:1.02rem;">Bên Trái: Ảnh Thiết Kế Mẫu Gốc (Ground Truth)</span>
        </div>
        """, unsafe_allow_html=True)
        if ref_img_path and ref_img_path.exists():
            st.image(str(ref_img_path), caption=f"Mục tiêu thiết kế chuẩn: {ref_img_path.name}", use_container_width=True)
        else:
            m3_banner("Không tìm thấy ảnh thiết kế mẫu gốc.", banner_type="info", icon_name="info")

    with col_actual:
        st.markdown(f"""
        <div style="background:var(--md-sys-color-surface-container); border-radius:14px; padding:14px 18px; border:1px solid var(--md-sys-color-outline-variant); margin-bottom:12px; display:flex; align-items:center; gap:8px;">
            {get_svg("desktop", size=20, color="#0B57D0")}
            <span style="font-weight:700; color:#0B57D0; font-size:1.02rem;">Bên Phải: 3 Ảnh Thực Tế AI Sinh Ra (Mobile, Tablet, Desktop)</span>
        </div>
        """, unsafe_allow_html=True)

        vp_subtab1, vp_subtab2, vp_subtab3, vp_subtab_all = st.tabs([
            "Desktop (1440px)",
            "Tablet (768px)",
            "Mobile (375px)",
            "Cả 3 Kích Thước"
        ])

        with vp_subtab1:
            sc_1440 = viewport_map.get(1440)
            if sc_1440 and (ROOT_DIR / sc_1440["image_path"]).exists():
                st.image(str(ROOT_DIR / sc_1440["image_path"]), caption="Kết xuất Desktop (1440×900 px)", use_container_width=True)
                if sc_1440["has_horizontal_overflow"]:
                    m3_banner("CẢNH BÁO: Bị tràn ngang trên màn hình Desktop 1440px!", banner_type="error", icon_name="error")
            else:
                m3_banner("Chưa có ảnh chụp cho Desktop 1440px.", banner_type="info", icon_name="info")

        with vp_subtab2:
            sc_768 = viewport_map.get(768)
            if sc_768 and (ROOT_DIR / sc_768["image_path"]).exists():
                st.image(str(ROOT_DIR / sc_768["image_path"]), caption="Kết xuất Tablet (768×1024 px)", use_container_width=True)
                if sc_768["has_horizontal_overflow"]:
                    m3_banner("CẢNH BÁO: Bị tràn ngang trên Tablet 768px!", banner_type="error", icon_name="error")
            else:
                m3_banner("Chưa có ảnh chụp cho Tablet 768px.", banner_type="info", icon_name="info")

        with vp_subtab3:
            sc_375 = viewport_map.get(375)
            if sc_375 and (ROOT_DIR / sc_375["image_path"]).exists():
                st.image(str(ROOT_DIR / sc_375["image_path"]), caption="Kết xuất Mobile (375×812 px)", use_container_width=True)
                if sc_375["has_horizontal_overflow"]:
                    m3_banner("CẢNH BÁO: Bị tràn ngang trên Điện thoại 375px!", banner_type="error", icon_name="error")
            else:
                m3_banner("Chưa có ảnh chụp cho Mobile 375px.", banner_type="info", icon_name="info")

        with vp_subtab_all:
            col_v1, col_v2, col_v3 = st.columns([1, 1.2, 1.6])
            with col_v1:
                st.markdown(f"<div style='display:flex; align-items:center; gap:6px; font-size:0.85rem; color:#444746; margin-bottom:6px;'>{get_svg('smartphone', size=16, color='#0B57D0')} <span>Điện thoại (375px)</span></div>", unsafe_allow_html=True)
                if sc_375 and (ROOT_DIR / sc_375["image_path"]).exists():
                    st.image(str(ROOT_DIR / sc_375["image_path"]), use_container_width=True)
            with col_v2:
                st.markdown(f"<div style='display:flex; align-items:center; gap:6px; font-size:0.85rem; color:#444746; margin-bottom:6px;'>{get_svg('tablet_mac', size=16, color='#0B57D0')} <span>Máy tính bảng (768px)</span></div>", unsafe_allow_html=True)
                if sc_768 and (ROOT_DIR / sc_768["image_path"]).exists():
                    st.image(str(ROOT_DIR / sc_768["image_path"]), use_container_width=True)
            with col_v3:
                st.markdown(f"<div style='display:flex; align-items:center; gap:6px; font-size:0.85rem; color:#444746; margin-bottom:6px;'>{get_svg('desktop_windows', size=16, color='#0B57D0')} <span>Máy tính bàn (1440px)</span></div>", unsafe_allow_html=True)
                if sc_1440 and (ROOT_DIR / sc_1440["image_path"]).exists():
                    st.image(str(ROOT_DIR / sc_1440["image_path"]), use_container_width=True)

# ==================== TAB 2: BẢNG ĐIỂM 6 TIÊU CHÍ & DANH SÁCH LỖI BẮT ĐƯỢC ====================
with tab_metrics:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; padding-top:10px; margin-top:8px; margin-bottom:18px;">
        {get_svg("analytics", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">Bảng Điểm 6 Tiêu Chí & Danh Sách Lỗi Bắt Được</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Hiện rõ từng tiêu chí đạt bao nhiêu điểm, trọng số đóng góp và các lỗi cụ thể bị trừ điểm.")

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
    all_detected_issues = []

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
                with st.expander(f"Lỗi bị trừ điểm ({len(issues)} vấn đề)"):
                    for iss in issues:
                        st.caption(f"• {iss}")
                        all_detected_issues.append((m_label, iss))
        idx += 1

    # Bảng tổng hợp toàn bộ danh sách lỗi bắt được
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-top:20px; margin-bottom:8px;">
        {get_svg("error", size=20, color="#BA1A1A")}
        <span style="font-weight:700; font-size:1.05rem; color:#BA1A1A;">Danh Sách Toàn Bộ Lỗi Hệ Thống Bắt Được ({len(all_detected_issues)} lỗi)</span>
    </div>
    """, unsafe_allow_html=True)

    if all_detected_issues:
        issues_df = pd.DataFrame(all_detected_issues, columns=["Nhóm Tiêu Chí", "Chi Tiết Lỗi / Vi Phạm"])
        st.dataframe(issues_df, use_container_width=True, hide_index=True)
    else:
        m3_banner("Tuyệt vời! Không phát hiện lỗi nào trên cả 6 tiêu chí.", banner_type="success", icon_name="check_circle")

# ==================== TAB 3: TRÌNH XEM CODE (CODE VIEWER) ====================
with tab_code:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; padding-top:10px; margin-top:8px; margin-bottom:18px;">
        {get_svg("code", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">Trình Xem Code (Code Viewer): Xem Trực Tiếp index.html, style.css, script.js</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Xem trực tiếp mã nguồn mà AI Agent đã sinh ra ngay trên giao diện với highlight cú pháp chuẩn.")

    proj_dir = ROOT_DIR / "outputs" / selected_run_id / "project"
    
    if proj_dir.exists():
        expected_names = ["index.html", "style.css", "script.js"]
        available_files = []
        for name in expected_names:
            p = proj_dir / name
            if p.exists():
                available_files.append(p)

        # Bổ sung các file khác nếu AI sinh thêm
        all_other_files = [p for p in proj_dir.rglob("*") if p.is_file() and p not in available_files]
        all_display_files = available_files + all_other_files

        if all_display_files:
            file_tabs = st.tabs([f.name for f in all_display_files])
            for f_tab, f_path in zip(file_tabs, all_display_files):
                with f_tab:
                    ext = f_path.suffix.lower()
                    lang = "html" if ext == ".html" else ("css" if ext == ".css" else ("javascript" if ext == ".js" else "text"))
                    content = f_path.read_text(encoding="utf-8", errors="ignore")
                    
                    st.markdown(f"<div style='display:flex; align-items:center; gap:8px; font-weight:700; font-size:1.05rem; color:#1F1F1F; margin-top:4px; margin-bottom:8px;'>{get_svg('description', size=20, color='#0B57D0')} <span>{f_path.name}</span></div>", unsafe_allow_html=True)
                    c_info1, c_info2 = st.columns([3, 1])
                    with c_info1:
                        st.caption(f"Đường dẫn: `{f_path.relative_to(ROOT_DIR)}` &nbsp;|&nbsp; Kích thước: `{len(content.splitlines())} dòng ({len(content)} bytes)`")
                    with c_info2:
                        st.download_button(f"Tải {f_path.name}", data=content, file_name=f_path.name, icon=":material/download:", use_container_width=True)
                        
                    st.code(content, language=lang, line_numbers=True)
        else:
            m3_banner("Không tìm thấy file mã nguồn nào trong thư mục project.", banner_type="info", icon_name="info")
    else:
        m3_banner(f"Thư mục project không tồn tại tại: {proj_dir}", banner_type="warning", icon_name="warning")

# ==================== TAB 4: NHẬT KÝ LỖI RUNTIME ====================
with tab_runtime:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; padding-top:10px; margin-top:8px; margin-bottom:18px;">
        {get_svg("bug_report", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">Nhật Ký Lỗi Runtime Thu Thập Từ Playwright</span>
    </div>
    """, unsafe_allow_html=True)

    render_report_path = ROOT_DIR / "outputs" / selected_run_id / "render_report.json"
    if render_report_path.exists():
        try:
            report_data = json.loads(render_report_path.read_text(encoding="utf-8"))
            errs = report_data.get("runtime_errors", {})

            console_errs = errs.get("console_errors", [])
            page_errs = errs.get("page_errors", [])
            failed_reqs = errs.get("failed_requests", [])

            c1, c2, c3 = st.columns(3)
            with c1:
                m3_card(value=str(len(console_errs)), label="Console Errors", secondary="Lỗi ghi nhận trong console", badge_type="error" if console_errs else "success", badge=str(len(console_errs)), icon_name="error")
            with c2:
                m3_card(value=str(len(page_errs)), label="Page Exceptions (JS)", secondary="Ngoại lệ JavaScript chưa bắt", badge_type="error" if page_errs else "success", badge=str(len(page_errs)), icon_name="warning")
            with c3:
                m3_card(value=str(len(failed_reqs)), label="Failed Requests", secondary="Lỗi tải ảnh/CDN/404", badge_type="error" if failed_reqs else "success", badge=str(len(failed_reqs)), icon_name="info")

            st.markdown("<br>", unsafe_allow_html=True)
            if page_errs:
                st.error("Danh sách ngoại lệ JavaScript (Page Errors):")
                for pe in page_errs:
                    st.code(pe, language="text")

            if console_errs:
                st.warning("Danh sách thông điệp Console Errors:")
                for ce in console_errs:
                    st.code(ce, language="text")

            if failed_reqs:
                st.warning("Danh sách yêu cầu mạng thất bại (Failed Network Requests):")
                for fr in failed_reqs:
                    st.write(f"- {fr}")

            if not page_errs and not console_errs and not failed_reqs:
                m3_banner("Tuyệt vời! Không có bất kỳ lỗi Runtime nào được ghi nhận trong quá trình kết xuất trình duyệt.", banner_type="success", icon_name="check_circle")

        except Exception as e:
            st.error(f"Lỗi đọc render_report.json: {e}")
    else:
        m3_banner("Chưa có báo cáo render_report.json cho lượt chạy này.", banner_type="info", icon_name="info")
