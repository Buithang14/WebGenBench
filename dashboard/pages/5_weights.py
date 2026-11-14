import streamlit as st
import pandas as pd
import yaml
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from storage.db_manager import DBManager
from scoring.calculator import ScoreCalculator
from config.loader import load_scoring
from dashboard.theme import (
    apply_m3_theme,
    m3_header,
    m3_banner,
    m3_chip,
    m3_elevated_card
)
from dashboard.icons import get_svg

st.set_page_config(page_title="Điều Chỉnh Trọng Số - WebGenBench (M3)", page_icon=":material/tune:", layout="wide")
apply_m3_theme()

m3_header(
    title="Điều Chỉnh Trọng Số & Tính Điểm Động",
    subtitle="Mô phỏng và cập nhật lại điểm tổng hợp toàn bộ các lần chạy theo triết lý đánh giá mới với Material Design 3",
    icon_name="tune"
)

SCORING_YAML_PATH = ROOT_DIR / "config" / "scoring.yaml"

calculator = ScoreCalculator()
current_weights = calculator.load_weights()
db = DBManager()
db.init_db()

col_sliders, col_sim = st.columns([1.2, 1.8])

with col_sliders:
    st.markdown(f"""
    <div style="background:var(--md-sys-color-surface-container); border-radius:16px; padding:14px 20px; border:1px solid var(--md-sys-color-outline-variant); margin-bottom:15px; display:flex; align-items:center; gap:8px; box-shadow: var(--md-elevation-1);">
        {get_svg("tune", size=22, color="#0B57D0")}
        <span style="font-weight:700; color:#0B57D0; font-size:1.1rem;">1. Tinh chỉnh Trọng số 6 Tiêu chí</span>
    </div>
    """, unsafe_allow_html=True)

    w_html = st.slider("HTML Validity:", min_value=0.0, max_value=0.5, value=float(current_weights.get("html_validity", 0.15)), step=0.05, format="%.2f")
    w_a11y = st.slider("Accessibility (a11y):", min_value=0.0, max_value=0.5, value=float(current_weights.get("accessibility", 0.20)), step=0.05, format="%.2f")
    w_resp = st.slider("Responsive Design:", min_value=0.0, max_value=0.5, value=float(current_weights.get("responsive", 0.20)), step=0.05, format="%.2f")
    w_design = st.slider("Design Similarity:", min_value=0.0, max_value=0.5, value=float(current_weights.get("design_similarity", 0.25)), step=0.05, format="%.2f")
    w_code = st.slider("Code Quality:", min_value=0.0, max_value=0.5, value=float(current_weights.get("code_quality", 0.10)), step=0.05, format="%.2f")
    w_runtime = st.slider("Runtime Cleanliness:", min_value=0.0, max_value=0.5, value=float(current_weights.get("runtime_cleanliness", 0.10)), step=0.05, format="%.2f")

    total_weight = round(w_html + w_a11y + w_resp + w_design + w_code + w_runtime, 4)

    new_weights = {
        "html_validity": round(w_html, 4),
        "accessibility": round(w_a11y, 4),
        "responsive": round(w_resp, 4),
        "design_similarity": round(w_design, 4),
        "code_quality": round(w_code, 4),
        "runtime_cleanliness": round(w_runtime, 4),
    }

    if abs(total_weight - 1.0) < 1e-4:
        m3_banner(f"Tổng trọng số chuẩn xác: <b>{total_weight * 100:.0f}%</b> (1.00)", banner_type="success", icon_name="check_circle")
    else:
        m3_banner(f"Tổng trọng số hiện tại: <b>{total_weight * 100:.1f}%</b>. Tổng trọng số BẮT BUỘC phải bằng đúng 100% (1.00) để lưu!", banner_type="error", icon_name="warning")

    btn_cols = st.columns(2)
    with btn_cols[0]:
        can_save = abs(total_weight - 1.0) < 1e-4
        if st.button("Lưu & Cập nhật CSDL", type="primary", icon=":material/save:", disabled=not can_save, use_container_width=True):
            yaml_content = {"weights": new_weights}
            with open(SCORING_YAML_PATH, "w", encoding="utf-8") as f:
                yaml.dump(yaml_content, f, allow_unicode=True, default_flow_style=False)

            updated_count = calculator.recalculate_all_scores(db)
            st.success(f"Đã lưu trọng số mới và tính lại điểm thành công cho {updated_count} lượt chạy!")
            st.rerun()

    with btn_cols[1]:
        if st.button("Khôi phục mặc định", icon=":material/restart_alt:", use_container_width=True):
            default_weights = {
                "weights": {
                    "html_validity": 0.15,
                    "accessibility": 0.20,
                    "responsive": 0.20,
                    "design_similarity": 0.25,
                    "code_quality": 0.10,
                    "runtime_cleanliness": 0.10,
                }
            }
            with open(SCORING_YAML_PATH, "w", encoding="utf-8") as f:
                yaml.dump(default_weights, f, allow_unicode=True, default_flow_style=False)
            calculator.recalculate_all_scores(db)
            st.info("Đã khôi phục trọng số mặc định chuẩn NCKH!")
            st.rerun()

with col_sim:
    st.markdown(f"""
    <div style="background:var(--md-sys-color-surface-container); border-radius:16px; padding:14px 20px; border:1px solid var(--md-sys-color-outline-variant); margin-bottom:15px; display:flex; align-items:center; gap:8px; box-shadow: var(--md-elevation-1);">
        {get_svg("analytics", size=22, color="#0B57D0")}
        <span style="font-weight:700; color:#0B57D0; font-size:1.1rem;">2. Mô Phỏng Thay Đổi Điểm Số Thời Gian Thực</span>
    </div>
    """, unsafe_allow_html=True)
    
    runs = db.list_all_runs()
    if not runs:
        m3_banner("Chưa có lượt chạy nào để mô phỏng.", banner_type="info", icon_name="info")
    else:
        sim_records = []
        for r in runs:
            try:
                trace = db.get_run_full_trace(r["run_id"])
                m = trace["automatic_metrics"]
                old_total = trace["score"].get("weighted_total_score", 0.0)

                raw_scores = {
                    "html_validity": m.get("html_validity", {}).get("raw_score", 0.0),
                    "accessibility": m.get("accessibility", {}).get("raw_score", 0.0),
                    "responsive": m.get("responsive", {}).get("raw_score", 0.0),
                    "design_similarity": m.get("design_similarity", {}).get("raw_score", 0.0),
                    "code_quality": m.get("code_quality", {}).get("raw_score", 0.0),
                    "runtime_cleanliness": m.get("runtime_cleanliness", {}).get("raw_score", 0.0),
                }

                new_total = sum(raw_scores[k] * new_weights.get(k, 0.0) for k in raw_scores)
                diff = new_total - old_total

                sim_records.append({
                    "Run ID": r["run_id"],
                    "IDE": r["ide_name"].upper(),
                    "Điểm hiện tại": f"{old_total:.2f}đ",
                    "Điểm mới (mô phỏng)": f"{new_total:.2f}đ",
                    "Chênh lệch": f"{diff:+.2f}đ",
                })
            except Exception:
                pass

        st.dataframe(pd.DataFrame(sim_records), use_container_width=True, hide_index=True)
        st.caption("Bảng mô phỏng tự động tính toán lại điểm số tương ứng ngay khi bạn di chuyển các thanh trượt bên trái.")
