import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from storage.db_manager import DBManager
from dashboard.theme import (
    apply_m3_theme,
    m3_header,
    m3_card,
    m3_banner,
    m3_chip,
    m3_plotly_layout,
    M3_PALETTE
)
from dashboard.icons import get_svg

st.set_page_config(page_title="Phân Tích & So Sánh - WebGenBench (M3)", page_icon=":material/analytics:", layout="wide")
apply_m3_theme()

m3_header(
    title="Phân Tích & So Sánh Nghiên Cứu (Analytics & Comparison)",
    subtitle="Màn hình 4 theo Kế hoạch: So sánh 3 công cụ (Bar chart & Boxplot độ ổn định), so sánh Điều kiện A vs B và biểu đồ 6 tiêu chí",
    icon_name="analytics"
)

db = DBManager()
db.init_db()
runs = db.list_all_runs()

if not runs:
    m3_banner("Chưa có dữ liệu lượt chạy nào. Vui lòng chạy ít nhất 1 bài benchmark!", banner_type="warning", icon_name="warning")
    st.stop()

# 1. Bộ lọc nâng cao
st.sidebar.markdown(f"""
<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
    {get_svg("tune", size=18, color="#0B57D0")}
    <span style="font-weight:700; font-size:1rem; color:#1F1F1F;">Bộ Lọc Phân Tích</span>
</div>
""", unsafe_allow_html=True)

all_tasks = sorted(list(set(r["task_id"] for r in runs)))
all_ides = sorted(list(set(r["ide_name"] for r in runs)))
all_conditions = sorted(list(set(r["prompt_condition"] for r in runs)))

selected_tasks = st.sidebar.multiselect("Lọc theo Bài tập (Task):", options=all_tasks, default=all_tasks)
selected_ides = st.sidebar.multiselect("Lọc theo IDE:", options=all_ides, default=all_ides)
selected_conditions = st.sidebar.multiselect("Lọc theo Điều kiện:", options=all_conditions, default=all_conditions)

# Áp dụng bộ lọc
filtered_runs = [
    r for r in runs
    if r["task_id"] in selected_tasks
    and r["ide_name"] in selected_ides
    and r["prompt_condition"] in selected_conditions
]

if not filtered_runs:
    m3_banner("Không có kết quả nào thỏa mãn bộ lọc hiện tại!", banner_type="info", icon_name="info")
    st.stop()

# Nạp chi tiết các metrics
detailed_records = []
for r in filtered_runs:
    try:
        trace = db.get_run_full_trace(r["run_id"])
        m = trace["automatic_metrics"]
        score_info = trace["score"]
        detailed_records.append({
            "Run ID": r["run_id"],
            "IDE": r["ide_name"].upper(),
            "Task": r["task_id"],
            "Điều kiện": r["prompt_condition"],
            "Điểm tổng": score_info.get("weighted_total_score", 0.0),
            "HTML Validity": m.get("html_validity", {}).get("raw_score", 0.0),
            "Accessibility": m.get("accessibility", {}).get("raw_score", 0.0),
            "Responsive": m.get("responsive", {}).get("raw_score", 0.0),
            "Design Similarity": m.get("design_similarity", {}).get("raw_score", 0.0),
            "Code Quality": m.get("code_quality", {}).get("raw_score", 0.0),
            "Runtime Cleanliness": m.get("runtime_cleanliness", {}).get("raw_score", 0.0),
            "Thời gian (s)": r["duration_seconds"],
            "Tổng LOC": r["total_loc"],
            "Trạng thái": r["status"]
        })
    except Exception:
        pass

df_detail = pd.DataFrame(detailed_records)

tab_overview, tab_boxplot, tab_cond, tab_metrics, tab_agreement = st.tabs([
    "1. So Sánh 3 IDE (Bar Chart)",
    "2. Độ Ổn Định (Boxplot)",
    "3. So Sánh Chữ vs Chữ+Ảnh",
    "4. 6 Nhóm Tiêu Chí",
    "5. Độ Đồng Thuận Giữa Những Người Chấm"
])

# ==================== TAB 1: XẾP HẠNG & BAR CHART ====================
with tab_overview:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        {get_svg("chart_bar", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">1. Tổng Điểm Chuẩn Hóa Theo Lượt Chạy (0 - 100 Điểm)</span>
    </div>
    """, unsafe_allow_html=True)

    fig_total = px.bar(
        df_detail,
        x="Run ID",
        y="Điểm tổng",
        color="IDE",
        text="Điểm tổng",
        hover_data=["Task", "Điều kiện", "Thời gian (s)", "Tổng LOC"],
        labels={"Điểm tổng": "Điểm chuẩn hóa (/100)"},
        color_discrete_sequence=M3_PALETTE
    )
    fig_total.update_traces(texttemplate='%{text:.2f}đ', textposition='outside', marker_line_width=0)
    fig_total.update_layout(**m3_plotly_layout(height=380))
    fig_total.update_layout(yaxis=dict(range=[0, 110], gridcolor="#E1E3E1"))
    st.plotly_chart(fig_total, use_container_width=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        ide_group = df_detail.groupby("IDE")["Điểm tổng"].mean().reset_index()
        fig_ide = px.bar(
            ide_group,
            x="IDE",
            y="Điểm tổng",
            color="IDE",
            title="Điểm Trung Bình Theo Từng IDE",
            text="Điểm tổng",
            color_discrete_sequence=M3_PALETTE
        )
        fig_ide.update_traces(texttemplate='%{text:.2f}đ', textposition='outside')
        fig_ide.update_layout(**m3_plotly_layout(height=350, title="Điểm Trung Bình Theo Từng IDE"))
        fig_ide.update_layout(yaxis=dict(range=[0, 110], gridcolor="#E1E3E1"))
        st.plotly_chart(fig_ide, use_container_width=True)

    with col_s2:
        ide_time = df_detail.groupby("IDE")["Thời gian (s)"].mean().reset_index()
        fig_time = px.bar(
            ide_time,
            x="IDE",
            y="Thời gian (s)",
            color="IDE",
            title="Thời Gian Sinh Code Trung Bình (Giây)",
            text="Thời gian (s)",
            color_discrete_sequence=M3_PALETTE
        )
        fig_time.update_traces(texttemplate='%{text:.1f}s', textposition='outside')
        fig_time.update_layout(**m3_plotly_layout(height=350, title="Thời Gian Sinh Code Trung Bình (Giây)"))
        st.plotly_chart(fig_time, use_container_width=True)

# ==================== TAB 2: BOXPLOT ĐỘ ỔN ĐỊNH ====================
with tab_boxplot:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
        {get_svg("box", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">2. Biểu Đồ Hộp (Boxplot) Đo Độ Phân Tán & Độ Ổn Định</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Yêu cầu Màn hình 4 trong Plan.docx: Thể hiện độ ổn định chất lượng mã sinh ra giữa các lần lặp lại (Repetitions)")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        fig_box_ide = px.box(
            df_detail,
            x="IDE",
            y="Điểm tổng",
            color="IDE",
            points="all",
            title="Phân Bố Điểm Tổng Theo Từng IDE",
            labels={"Điểm tổng": "Điểm tổng (/100)"},
            color_discrete_sequence=M3_PALETTE
        )
        fig_box_ide.update_layout(**m3_plotly_layout(height=400, title="Phân Bố Điểm Tổng Theo Từng IDE"))
        fig_box_ide.update_layout(yaxis=dict(range=[0, 105], gridcolor="#E1E3E1"))
        st.plotly_chart(fig_box_ide, use_container_width=True)

    with col_b2:
        fig_box_time = px.box(
            df_detail,
            x="IDE",
            y="Thời gian (s)",
            color="IDE",
            points="all",
            title="Phân Bố Thời Gian Thực Thi Theo Từng IDE",
            labels={"Thời gian (s)": "Thời gian (giây)"},
            color_discrete_sequence=M3_PALETTE
        )
        fig_box_time.update_layout(**m3_plotly_layout(height=400, title="Phân Bố Thời Gian Thực Thi Theo Từng IDE"))
        st.plotly_chart(fig_box_time, use_container_width=True)

# ==================== TAB 3: ĐIỀU KIỆN A VS B ====================
with tab_cond:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
        {get_svg("contrast", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">3. So Sánh Hiệu Quả: Điều Kiện A (Text-only) vs Điều Kiện B (Text + Image)</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Đo lường mức độ cải thiện điểm số và độ tương đồng thiết kế khi có thêm ảnh tham chiếu")

    cond_comp = df_detail.groupby(["IDE", "Điều kiện"])[["Điểm tổng", "Design Similarity", "Thời gian (s)"]].mean().reset_index()
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fig_cond_score = px.bar(
            cond_comp,
            x="IDE",
            y="Điểm tổng",
            color="Điều kiện",
            barmode="group",
            text="Điểm tổng",
            title="Điểm Tổng Hợp: Prompt Chữ vs Prompt + Ảnh",
            color_discrete_sequence=["#0B57D0", "#984061"]
        )
        fig_cond_score.update_traces(texttemplate='%{text:.1f}đ', textposition='outside')
        fig_cond_score.update_layout(**m3_plotly_layout(height=380, title="Điểm Tổng Hợp: Prompt Chữ vs Prompt + Ảnh"))
        fig_cond_score.update_layout(yaxis=dict(range=[0, 110], gridcolor="#E1E3E1"))
        st.plotly_chart(fig_cond_score, use_container_width=True)

    with col_c2:
        fig_cond_sim = px.bar(
            cond_comp,
            x="IDE",
            y="Design Similarity",
            color="Điều kiện",
            barmode="group",
            text="Design Similarity",
            title="Độ Tương Đồng Thị Giác (Design Similarity): Text vs Text+Image",
            color_discrete_sequence=["#0B57D0", "#984061"]
        )
        fig_cond_sim.update_traces(texttemplate='%{text:.1f}đ', textposition='outside')
        fig_cond_sim.update_layout(**m3_plotly_layout(height=380, title="Độ Tương Đồng Thị Giác: Text vs Text+Image"))
        fig_cond_sim.update_layout(yaxis=dict(range=[0, 110], gridcolor="#E1E3E1"))
        st.plotly_chart(fig_cond_sim, use_container_width=True)

# ==================== TAB 4: 6 TIÊU CHÍ ====================
with tab_metrics:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        {get_svg("analytics", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">4. So Sánh Chi Tiết 6 Nhóm Tiêu Chí Giữa Các IDE</span>
    </div>
    """, unsafe_allow_html=True)
    metric_cols = ["HTML Validity", "Accessibility", "Responsive", "Design Similarity", "Code Quality", "Runtime Cleanliness"]

    df_melted = df_detail.melt(
        id_vars=["Run ID", "IDE", "Task", "Điều kiện"],
        value_vars=metric_cols,
        var_name="Tiêu chí",
        value_name="Điểm thành phần"
    )

    fig_metrics = px.bar(
        df_melted,
        x="Tiêu chí",
        y="Điểm thành phần",
        color="IDE",
        barmode="group",
        labels={"Điểm thành phần": "Điểm thô (0 - 100)"},
        title="Điểm số trung bình từng tiêu chí đo lường",
        color_discrete_sequence=M3_PALETTE
    )
    fig_metrics.update_layout(**m3_plotly_layout(height=420, title="Điểm số trung bình từng tiêu chí đo lường"))
    fig_metrics.update_layout(yaxis=dict(range=[0, 110], gridcolor="#E1E3E1"))
    st.plotly_chart(fig_metrics, use_container_width=True)

# ==================== TAB 5: ĐỘ ĐỒNG THUẬN GIỮA NHỮNG NGƯỜI CHẤM ====================
with tab_agreement:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        {get_svg("gavel", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">5. Phân Tích Độ Đồng Thuận Giữa Những Người Chấm (Inter-Rater Agreement)</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Kiểm định độ tin cậy khoa học của phương pháp chấm điểm mù: Tỷ lệ đồng thuận tuyệt đối (Exact %), Trong phạm vi 1 điểm (Within-1) và hệ số Fleiss' Kappa.")

    from qualitative.agreement import compute_inter_rater_agreement
    iaa_stats = compute_inter_rater_agreement(db)

    c_iaa1, c_iaa2, c_iaa3 = st.columns(3)
    with c_iaa1:
        m3_card(
            value=f"{iaa_stats.get('exact_agreement_percent', 0.0):.1f}%",
            label="Đồng thuận tuyệt đối",
            secondary="Exact Agreement",
            badge="Exact",
            badge_type="primary",
            icon_name="check_circle"
        )
    with c_iaa2:
        m3_card(
            value=f"{iaa_stats.get('within_1_agreement_percent', 0.0):.1f}%",
            label="Đồng thuận sai lệch ≤ 1đ",
            secondary="Within-1 Point Agreement",
            badge="Within-1",
            badge_type="success",
            icon_name="task"
        )
    with c_iaa3:
        kappa_val = iaa_stats.get("fleiss_kappa_approx", 0.0)
        m3_card(
            value=f"{kappa_val:.3f}",
            label="Hệ số Fleiss' Kappa",
            secondary=iaa_stats.get("kappa_interpretation", "N/A"),
            badge="Kappa",
            badge_type="secondary",
            icon_name="analytics"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    m3_banner(
        f"<b>Tổng số lượt chấm ghi nhận:</b> {iaa_stats.get('total_ratings', 0)} lượt trên {iaa_stats.get('samples_rated_count', 0)} mẫu thử nghiệm bởi {iaa_stats.get('distinct_raters_count', 0)} chuyên gia độc lập. "
        f"Mức độ đồng thuận: <b>{iaa_stats.get('kappa_interpretation', 'N/A')}</b>.",
        banner_type="info",
        icon_name="info"
    )

st.divider()

st.markdown(f"""
<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
    {get_svg("download", size=20, color="#0B57D0")}
    <span style="font-weight:700; font-size:1.1rem; color:#1F1F1F;">Bảng Dữ Liệu Tổng Hợp & Xuất Khóa Luận</span>
</div>
""", unsafe_allow_html=True)
st.dataframe(df_detail, use_container_width=True, hide_index=True)
csv_data = df_detail.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 Xuất file CSV đưa vào khóa luận",
    data=csv_data,
    file_name="webgenbench_analytics_matrix.csv",
    mime="text/csv",
    type="primary",
    icon=":material/download:"
)
