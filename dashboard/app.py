import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Thêm thư mục gốc vào sys.path để import các module của WebGenBench
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from storage.db_manager import DBManager
from config.loader import load_scoring, load_tools, load_settings
from experiment.task_loader import list_available_tasks
from dashboard.theme import (
    apply_m3_theme,
    m3_header,
    m3_card,
    m3_elevated_card,
    m3_banner,
    m3_chip,
    M3_PALETTE
)
from dashboard.icons import get_svg

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="WebGenBench - Material Design 3",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_db():
    db = DBManager()
    db.init_db()
    outputs_dir = ROOT_DIR / "outputs"
    if outputs_dir.exists():
        for run_dir in outputs_dir.iterdir():
            if run_dir.is_dir() and (run_dir / "run_metadata.json").exists():
                try:
                    db.sync_run_from_disk(run_dir.name)
                except Exception:
                    pass
    return db


def home_page():
    apply_m3_theme()
    m3_header(
        title="WebGenBench Control Center",
        subtitle="Hệ thống tự động hóa đánh giá năng lực sinh giao diện web của các AI Coding Agents theo tiêu chuẩn Google Material Design 3 và Kế hoạch NCKH",
        icon_name="dashboard"
    )

    db = get_db()
    all_runs = db.list_all_runs()

    # Thanh bên Sidebar theo phong cách M3 Navigation Drawer
    with st.sidebar:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom: 1.2rem;">
            <div style="background:#0B57D0; color:white; border-radius:12px; padding:6px 10px; display:flex; align-items:center; justify-content:center; box-shadow: var(--md-elevation-1);">
                {get_svg("code", size=24, color="#FFFFFF")}
            </div>
            <div>
                <div style="font-weight:700; font-size:1.1rem; color:#1F1F1F; line-height:1.2;">WebGenBench</div>
                <div style="font-size:0.75rem; color:#444746; font-weight:600; letter-spacing:0.5px;">MATERIAL YOU EDITION</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            {get_svg("desktop", size=18, color="#0B57D0")}
            <span style="font-weight:700; font-size:0.95rem; color:#1F1F1F;">Công Cụ IDE Mục Tiêu</span>
        </div>
        """, unsafe_allow_html=True)

        tools_cfg = load_tools()
        for k, v in tools_cfg.tools.items():
            st.markdown(f"""
            <div style="background:var(--md-sys-color-surface-container); border-radius:12px; padding:8px 12px; margin-bottom:6px; border:1px solid var(--md-sys-color-outline-variant);">
                <div style="font-weight:700; color:#0B57D0; font-size:0.88rem;">{v.name}</div>
                <div style="font-size:0.78rem; color:#444746;">Agent: <b>{v.agent_name}</b> ({v.fixed_model})</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        tasks = list_available_tasks()
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            {get_svg("task", size=18, color="#0B57D0")}
            <span style="font-weight:700; font-size:0.95rem; color:#1F1F1F;">Danh Mục Bài Tập ({len(tasks)} tasks)</span>
        </div>
        """, unsafe_allow_html=True)

        for t in tasks:
            st.markdown(m3_chip(f"Task: {t}", icon_name="task", chip_type="primary"), unsafe_allow_html=True)

        st.divider()
        if st.button("Làm mới dữ liệu từ đĩa", icon=":material/refresh:", use_container_width=True):
            outputs_dir = ROOT_DIR / "outputs"
            count = 0
            if outputs_dir.exists():
                for r_dir in outputs_dir.iterdir():
                    if r_dir.is_dir() and (r_dir / "run_metadata.json").exists():
                        try:
                            db.sync_run_from_disk(r_dir.name)
                            count += 1
                        except Exception:
                            pass
            st.success(f"Đã đồng bộ {count} lượt chạy!")
            st.rerun()

    # Thống kê nhanh KPIs bằng M3 Card Container
    col1, col2, col3, col4 = st.columns(4)
    total_runs = len(all_runs)
    avg_score = 0.0
    scores = [r["weighted_total_score"] for r in all_runs if r["weighted_total_score"] is not None]
    if scores:
        avg_score = sum(scores) / len(scores)

    successful_runs = sum(1 for r in all_runs if r["status"] == "SUCCESS")
    total_loc = sum(r["total_loc"] for r in all_runs)

    with col1:
        m3_card(value=str(total_runs), label="Tổng lượt chạy (Runs)", secondary="Số lượt kiểm thử đã ghi nhận", badge="M3 Active", badge_type="primary", icon_name="rocket")
    with col2:
        m3_card(value=f"{avg_score:.1f}", label="Điểm trung bình (/100)", secondary="Trung bình chuẩn hóa 6 tiêu chí", badge="Tốt" if avg_score >= 70 else "Trung bình", badge_type="success" if avg_score >= 70 else "warning", icon_name="trophy")
    with col3:
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        m3_card(value=f"{success_rate:.0f}%", label="Tỷ lệ thành công", secondary=f"{successful_runs}/{total_runs} lượt hoàn tất", badge="Success", badge_type="success", icon_name="check_circle")
    with col4:
        m3_card(value=f"{total_loc:,}", label="Tổng dòng mã (LOC)", secondary="Mã nguồn HTML/CSS/JS do AI sinh", badge="Code", badge_type="neutral", icon_name="code")

    st.markdown("<br>", unsafe_allow_html=True)

    if not all_runs:
        m3_banner(
            "Chưa có lượt chạy nào trong cơ sở dữ liệu. Hãy chuyển sang trang <b>Điều Khiển Thí Nghiệm</b> để thực hiện lượt chạy đầu tiên!",
            banner_type="info",
            icon_name="info"
        )
        return

    # Bảng tổng quan Leaderboard M3
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        {get_svg("trophy", size=24, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.3rem; color:#1F1F1F;">Bảng Xếp Hạng Toàn Bộ Các Lần Chạy</span>
    </div>
    """, unsafe_allow_html=True)

    df = pd.DataFrame(all_runs)
    df["weighted_total_score"] = df["weighted_total_score"].apply(lambda x: f"{x:.2f} đ" if x is not None else "N/A")
    df["duration_seconds"] = df["duration_seconds"].apply(lambda x: f"{x:.1f}s")
    
    col_order = ["run_id", "ide_name", "task_id", "prompt_condition", "weighted_total_score", "duration_seconds", "total_loc", "status", "start_time"]
    rename_cols = {
        "run_id": "Mã Run",
        "ide_name": "IDE",
        "task_id": "Bài tập",
        "prompt_condition": "Điều kiện",
        "weighted_total_score": "Điểm tổng hợp",
        "duration_seconds": "Thời gian",
        "total_loc": "Tổng LOC",
        "status": "Trạng thái",
        "start_time": "Thời điểm chạy"
    }
    df_display = df[col_order].rename(columns=rename_cols)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Biểu đồ Radar 6 tiêu chí phối màu Material Design 3
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-top:24px; margin-bottom:12px;">
        {get_svg("analytics", size=24, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.3rem; color:#1F1F1F;">Biểu Đồ Radar 6 Tiêu Chí Đánh Giá</span>
    </div>
    """, unsafe_allow_html=True)

    col_chart, col_weights = st.columns([2, 1])

    radar_fig = go.Figure()
    categories = [
        "HTML Validity",
        "Accessibility",
        "Responsive",
        "Design Similarity",
        "Code Quality",
        "Runtime Cleanliness"
    ]

    for idx, run_item in enumerate(all_runs[:4]):
        try:
            trace = db.get_run_full_trace(run_item["run_id"])
            m = trace["automatic_metrics"]
            values = [
                m.get("html_validity", {}).get("raw_score", 0),
                m.get("accessibility", {}).get("raw_score", 0),
                m.get("responsive", {}).get("raw_score", 0),
                m.get("design_similarity", {}).get("raw_score", 0),
                m.get("code_quality", {}).get("raw_score", 0),
                m.get("runtime_cleanliness", {}).get("raw_score", 0),
            ]
            values.append(values[0])
            color = M3_PALETTE[idx % len(M3_PALETTE)]
            radar_fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=f"{run_item['run_id']} ({run_item['ide_name'].upper()})",
                line=dict(color=color, width=2.5),
            ))
        except Exception:
            pass

    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#E1E3E1"),
            angularaxis=dict(gridcolor="#E1E3E1"),
            bgcolor="#F0F4F9"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        margin=dict(l=40, r=40, t=20, b=20),
        height=380,
        font=dict(family="Plus Jakarta Sans", color="#1F1F1F")
    )

    with col_chart:
        st.plotly_chart(radar_fig, use_container_width=True)

    with col_weights:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            {get_svg("tune", size=20, color="#0B57D0")}
            <span style="font-weight:700; font-size:1.05rem; color:#1F1F1F;">Trọng Số Tiêu Chuẩn (100%)</span>
        </div>
        """, unsafe_allow_html=True)
        scoring_cfg = load_scoring()
        weights_data = {
            "Tiêu chí": [
                "HTML Validity",
                "Accessibility",
                "Responsive Design",
                "Design Similarity",
                "Code Quality",
                "Runtime Cleanliness"
            ],
            "Tỷ lệ": [
                f"{scoring_cfg.weights.html_validity * 100:.0f}%",
                f"{scoring_cfg.weights.accessibility * 100:.0f}%",
                f"{scoring_cfg.weights.responsive * 100:.0f}%",
                f"{scoring_cfg.weights.design_similarity * 100:.0f}%",
                f"{scoring_cfg.weights.code_quality * 100:.0f}%",
                f"{scoring_cfg.weights.runtime_cleanliness * 100:.0f}%"
            ]
        }
        st.table(pd.DataFrame(weights_data))

    st.divider()
    m3_elevated_card(f"""
        <div style="font-weight:700; color:#0B57D0; margin-bottom:10px; font-size:1.15rem; display:flex; align-items:center; gap:8px;">
            {get_svg("task", size=24, color="#0B57D0")}
            <span>5 Khu Vực Chức Năng Cốt Lõi (Theo Giao diện.docx & Plan.docx):</span>
        </div>
        <div style="font-size:0.92rem; color:#444746; line-height:1.9;">
            • <b>1. Quản lý Bài tập & Nạp Prompt (Task & Prompt Manager):</b> Thao tác trực tiếp với 8 bài tập (T01 → T08), ô soạn thảo Prompt lớn, danh sách yêu cầu UI & kỹ thuật, upload ảnh thiết kế mẫu kèm xem trước.<br>
            • <b>2. Điều khiển Chạy Thí nghiệm (Experiment Control Panel):</b> Chế độ 1 chạy đơn lẻ (Cursor/Windsurf/VS Code, Text vs Text+Image, nút Bắt đầu & Chấm điểm lại); Chế độ 2 chạy hàng loạt 144 runs với thanh tiến trình và Live Log.<br>
            • <b>3. Cấu hình Trọng số & Hệ thống (Settings & Scoring Config):</b> 6 thanh kéo sliders tinh chỉnh tỷ lệ % tiêu chí, nút Recalculate cập nhật toàn bộ CSDL, cấu hình đường dẫn .exe của 3 IDE, Model cố định và Timeout.<br>
            • <b>4. Soi Chi tiết Kết quả (Run Inspector):</b> Bộ lọc lượt chạy, so sánh ảnh trực quan đặt cạnh nhau (Ảnh mẫu gốc vs 3 cỡ Mobile, Tablet, Desktop), bảng điểm 6 tiêu chí & danh sách lỗi bắt được, trình xem code index.html, style.css, script.js.<br>
            • <b>5. Chấm điểm Định tính Ẩn danh & Xuất Báo cáo (Blind Review & Analytics):</b> Màn hình người chấm ẩn danh Sample #037 với 4 tiêu chí 1-5 sao + nhận xét; Biểu đồ so sánh 3 IDE, so sánh Text vs Text+Image, hệ số đồng thuận Fleiss' Kappa và nút Xuất CSV đưa vào khóa luận.
        </div>
    """)


# Hệ thống Navigation Streamlit chuẩn xác theo Giao diện.docx & Plan.docx với Google Material Symbols (SVG) & URL tiếng Anh tinh gọn
pg = st.navigation(
    pages=[
        st.Page(home_page, title="Tổng Quan", icon=":material/dashboard:", default=True),
        st.Page("pages/0_tasks.py", title="Quản Lý Bài Tập", icon=":material/task:", url_path="tasks"),
        st.Page("pages/1_experiments.py", title="Điều Khiển Thí Nghiệm", icon=":material/rocket_launch:", url_path="experiments"),
        st.Page("pages/2_inspect.py", title="Chi Tiết Lần Chạy", icon=":material/manage_search:", url_path="inspect"),
        st.Page("pages/3_rating.py", title="Chấm Điểm Ẩn Danh", icon=":material/gavel:", url_path="rating"),
        st.Page("pages/4_analytics.py", title="Phân Tích & Biểu Đồ", icon=":material/analytics:", url_path="analytics"),
        st.Page("pages/5_weights.py", title="Cấu Hình & Trọng Số", icon=":material/tune:", url_path="weights"),
        st.Page("pages/6_export.py", title="Xuất Báo Cáo", icon=":material/download:", url_path="export"),
    ]
)

# Chạy trang điều hướng
pg.run()
