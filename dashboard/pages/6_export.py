import streamlit as st
import pandas as pd
import json
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
    m3_elevated_card
)
from dashboard.icons import get_svg

st.set_page_config(page_title="Xuất Dữ Liệu - WebGenBench (M3)", page_icon=":material/download:", layout="wide")
apply_m3_theme()

m3_header(
    title="Trung Tâm Xuất Dữ Liệu (Export Center)",
    icon_name="download"
)

db = DBManager()
db.init_db()
runs = db.list_all_runs()

if not runs:
    m3_banner("Chưa có dữ liệu nào trong cơ sở dữ liệu để xuất.", banner_type="warning", icon_name="warning")
    st.stop()

# Xây dựng bảng phẳng toàn diện (Full Flat Dataset)
flat_records = []
for r in runs:
    try:
        trace = db.get_run_full_trace(r["run_id"])
        run_data = trace["run"]
        proj_data = trace["project"]
        m = trace["automatic_metrics"]
        score_data = trace["score"]
        
        flat_records.append({
            "run_id": run_data["id"],
            "ide_name": run_data["ide_name"],
            "agent_name": run_data["agent_name"],
            "model_name": run_data["model_name"],
            "task_id": run_data["task_id"],
            "prompt_condition": run_data["prompt_condition"],
            "status": run_data["status"],
            "duration_seconds": run_data["duration_seconds"],
            "total_loc": proj_data.get("total_lines_of_code", 0),
            "file_count": proj_data.get("file_count", 0),
            "sha256_hash": proj_data.get("sha256_hash", ""),
            "blind_code": run_data["blind_code"],
            "html_validity_score": m.get("html_validity", {}).get("raw_score", 0.0),
            "accessibility_score": m.get("accessibility", {}).get("raw_score", 0.0),
            "responsive_score": m.get("responsive", {}).get("raw_score", 0.0),
            "design_similarity_score": m.get("design_similarity", {}).get("raw_score", 0.0),
            "code_quality_score": m.get("code_quality", {}).get("raw_score", 0.0),
            "runtime_cleanliness_score": m.get("runtime_cleanliness", {}).get("raw_score", 0.0),
            "weighted_total_score": score_data.get("weighted_total_score", 0.0),
            "start_time": run_data.get("start_time", ""),
        })
    except Exception:
        pass

df_flat = pd.DataFrame(flat_records)

col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    m3_card(value=str(len(df_flat)), label="Tổng số bản ghi", secondary="Số lượt chạy trong CSDL", badge="Dataset", badge_type="primary", icon_name="task")
with col_info2:
    m3_card(value=f"{len(df_flat.columns)} Cột", label="Số trường dữ liệu", secondary="Bảng phẳng đã chuẩn hóa", badge="SPSS/R Ready", badge_type="success", icon_name="analytics")
with col_info3:
    m3_card(value="UTF-8-SIG", label="Mã hóa tiếng Việt", secondary="Mở trực tiếp trên MS Excel", badge="Excel", badge_type="neutral", icon_name="check_circle")

st.markdown("<br>", unsafe_allow_html=True)

# 3 Phân vùng xuất dữ liệu
col_csv, col_json, col_md = st.columns(3)

with col_csv:
    st.markdown(f"""
    <div class="m3-card" style="height:100%; display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div style="font-weight:700; color:#0B57D0; font-size:1.1rem; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
                {get_svg("chart_bar", size=22, color="#0B57D0")}
                <span>Bảng Dữ Liệu (.CSV)</span>
            </div>
            <div style="font-size:0.88rem; color:#444746; margin-bottom:15px;">Dành cho phân tích thống kê định lượng trên SPSS, R, Python hoặc Microsoft Excel.</div>
        </div>
    """, unsafe_allow_html=True)
    csv_bytes = df_flat.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="Tải xuống file CSV",
        data=csv_bytes,
        file_name="webgenbench_dataset_export.csv",
        mime="text/csv",
        type="primary",
        icon=":material/download:",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col_json:
    st.markdown(f"""
    <div class="m3-card" style="height:100%; display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div style="font-weight:700; color:#0B57D0; font-size:1.1rem; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
                {get_svg("code", size=22, color="#0B57D0")}
                <span>Toàn Bộ Hồ Sơ (.JSON)</span>
            </div>
            <div style="font-size:0.88rem; color:#444746; margin-bottom:15px;">Dữ liệu cấu trúc lồng nhau đầy đủ bao gồm cây lỗi DOM, các cảnh báo chi tiết và ảnh chụp.</div>
        </div>
    """, unsafe_allow_html=True)
    full_export = [db.get_run_full_trace(r["run_id"]) for r in runs if "run_id" in r]
    json_bytes = json.dumps(full_export, indent=2, ensure_ascii=False).encode('utf-8')
    st.download_button(
        label="Tải xuống file JSON",
        data=json_bytes,
        file_name="webgenbench_full_traces.json",
        mime="application/json",
        icon=":material/download:",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col_md:
    st.markdown(f"""
    <div class="m3-card" style="height:100%; display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div style="font-weight:700; color:#0B57D0; font-size:1.1rem; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
                {get_svg("task", size=22, color="#0B57D0")}
                <span>Báo Cáo Khóa Luận (.MD)</span>
            </div>
            <div style="font-size:0.88rem; color:#444746; margin-bottom:15px;">Bản tóm tắt kết quả nghiên cứu bằng định dạng Markdown sẵn sàng chèn vào báo cáo.</div>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        table_ide = df_flat.groupby('ide_name')[['weighted_total_score', 'html_validity_score', 'accessibility_score', 'responsive_score', 'design_similarity_score', 'code_quality_score', 'runtime_cleanliness_score', 'duration_seconds']].mean().to_markdown()
    except Exception:
        table_ide = df_flat.groupby('ide_name')[['weighted_total_score', 'duration_seconds']].mean().to_string()

    try:
        table_cond = df_flat.groupby(['ide_name', 'prompt_condition'])[['weighted_total_score', 'design_similarity_score', 'duration_seconds']].mean().to_markdown()
    except Exception:
        table_cond = df_flat.groupby(['ide_name', 'prompt_condition'])[['weighted_total_score', 'duration_seconds']].mean().to_string()

    md_content = f"""# BÁO CÁO KẾT QUẢ THỰC NGHIỆM WEBGENBENCH

## 1. Tóm tắt tổng quan
- **Tổng số lần chạy:** {len(df_flat)}
- **Thời gian thực hiện:** {df_flat['duration_seconds'].mean():.1f}s (Trung bình)
- **Tổng số dòng mã sinh ra:** {df_flat['total_loc'].sum():,} LOC

## 2. Bảng tổng hợp điểm số theo IDE
{table_ide}

## 3. So sánh điều kiện Prompt
{table_cond}
"""
    st.download_button(
        label="Tải xuống Báo cáo MD",
        data=md_content.encode('utf-8'),
        file_name="webgenbench_research_summary.md",
        mime="text/markdown",
        icon=":material/download:",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# Xem trước bảng dữ liệu phẳng
st.markdown(f"""
<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
    {get_svg("visibility", size=20, color="#0B57D0")}
    <span style="font-weight:700; font-size:1.1rem; color:#1F1F1F;">Xem Trước Bảng Dữ Liệu Phẳng (Flat Dataset Preview)</span>
</div>
""", unsafe_allow_html=True)
st.dataframe(df_flat, use_container_width=True, hide_index=True)
