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
from config.loader import load_scoring, load_tools, load_settings
from dashboard.theme import (
    apply_m3_theme,
    m3_header,
    m3_banner,
    m3_chip,
    m3_card,
    m3_elevated_card
)
from dashboard.icons import get_svg

st.set_page_config(
    page_title="Cấu Hình Trọng Số & Hệ Thống - WebGenBench (M3)",
    page_icon=":material/tune:",
    layout="wide"
)
apply_m3_theme()

m3_header(
    title="Cấu Hình Trọng Số & Hệ Thống (Settings & Scoring Config)",
    subtitle="Tinh chỉnh luật chấm điểm 6 tiêu chí định lượng, cấu hình đường dẫn thực thi của 3 IDE, Model cố định và thời gian chờ",
    icon_name="tune"
)

SCORING_YAML_PATH = ROOT_DIR / "config" / "scoring.yaml"
SETTINGS_YAML_PATH = ROOT_DIR / "config" / "settings.yaml"
TOOLS_YAML_PATH = ROOT_DIR / "config" / "tools.yaml"

calculator = ScoreCalculator()
current_weights = calculator.load_weights()
db = DBManager()
db.init_db()

tab_weights, tab_ide_config = st.tabs([
    "1. Trọng Số Chấm Điểm 6 Tiêu Chí (Scoring Weights)",
    "2. Cấu Hình 3 IDE & Tham Số Hệ Thống (IDE & Timing Config)"
])

# ==================== TAB 1: TRỌNG SỐ 6 TIÊU CHÍ ====================
with tab_weights:
    col_sliders, col_sim = st.columns([1.1, 1.9], gap="large")

    with col_sliders:
        st.markdown(f"""
        <div style="background:var(--md-sys-color-surface-container); border-radius:16px; padding:14px 20px; border:1px solid var(--md-sys-color-outline-variant); margin-bottom:15px; display:flex; align-items:center; gap:8px; box-shadow: var(--md-elevation-1);">
            {get_svg("tune", size=22, color="#0B57D0")}
            <span style="font-weight:700; color:#0B57D0; font-size:1.1rem;">6 Thanh Kéo (Sliders) Trọng Số</span>
        </div>
        """, unsafe_allow_html=True)

        w_html = st.slider("1. HTML Validity (mặc định 15%):", min_value=0.0, max_value=0.5, value=float(current_weights.get("html_validity", 0.15)), step=0.05, format="%.2f")
        w_a11y = st.slider("2. Accessibility (mặc định 20%):", min_value=0.0, max_value=0.5, value=float(current_weights.get("accessibility", 0.20)), step=0.05, format="%.2f")
        w_resp = st.slider("3. Responsive (mặc định 20%):", min_value=0.0, max_value=0.5, value=float(current_weights.get("responsive", 0.20)), step=0.05, format="%.2f")
        w_design = st.slider("4. Design Similarity (mặc định 25%):", min_value=0.0, max_value=0.5, value=float(current_weights.get("design_similarity", 0.25)), step=0.05, format="%.2f")
        w_code = st.slider("5. Code Quality (mặc định 10%):", min_value=0.0, max_value=0.5, value=float(current_weights.get("code_quality", 0.10)), step=0.05, format="%.2f")
        w_runtime = st.slider("6. Runtime Cleanliness (mặc định 10%):", min_value=0.0, max_value=0.5, value=float(current_weights.get("runtime_cleanliness", 0.10)), step=0.05, format="%.2f")

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
            m3_banner(f"Tổng trọng số hiện tại: <b>{total_weight * 100:.1f}%</b>. Tổng trọng số BẮT BUỘC phải bằng 100% (1.00) để lưu!", banner_type="error", icon_name="warning")

        btn_cols = st.columns([1.2, 1.0])
        with btn_cols[0]:
            can_save = abs(total_weight - 1.0) < 1e-4
            if st.button("Lưu & Tính lại toàn bộ điểm (Recalculate)", type="primary", icon=":material/save:", disabled=not can_save, use_container_width=True):
                yaml_content = {"weights": new_weights}
                with open(SCORING_YAML_PATH, "w", encoding="utf-8") as f:
                    yaml.dump(yaml_content, f, allow_unicode=True, default_flow_style=False)

                updated_count = calculator.recalculate_all_scores(db)
                st.success(f"Đã lưu trọng số mới và tính lại điểm thành công cho {updated_count} lượt chạy trong CSDL!")
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
            <span style="font-weight:700; color:#0B57D0; font-size:1.1rem;">Mô Phỏng Điểm Số Thời Gian Thực</span>
        </div>
        """, unsafe_allow_html=True)
        
        runs = db.list_all_runs()
        if not runs:
            m3_banner("Chưa có lượt chạy nào để mô phỏng điểm số.", banner_type="info", icon_name="info")
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
                        "Mã Lượt Chạy": r["run_id"],
                        "IDE": r["ide_name"].upper(),
                        "Bài Tập": r["task_id"],
                        "Điểm Hiện Tại": f"{old_total:.2f}đ",
                        "Điểm Mới (Mô Phỏng)": f"{new_total:.2f}đ",
                        "Chênh Lệch": f"{diff:+.2f}đ",
                    })
                except Exception:
                    pass

            st.dataframe(pd.DataFrame(sim_records), use_container_width=True, hide_index=True)
            st.caption("Bảng mô phỏng tự động tính toán lại điểm số tương ứng ngay khi bạn di chuyển các thanh trượt bên trái.")

# ==================== TAB 2: CẤU HÌNH IDE & HỆ THỐNG ====================
with tab_ide_config:
    st.markdown(f"""
    <div style="background:var(--md-sys-color-surface-container); border-radius:16px; padding:14px 20px; border:1px solid var(--md-sys-color-outline-variant); margin-bottom:15px; display:flex; align-items:center; gap:8px; box-shadow: var(--md-elevation-1);">
        {get_svg("desktop", size=22, color="#0B57D0")}
        <span style="font-weight:700; color:#0B57D0; font-size:1.1rem;">Cấu Hình Đường Dẫn 3 IDE & Model Cố Định</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Xem và cập nhật đường dẫn thực thi (.exe) của 3 IDE trên máy tính, tên Model cố định của AI Agent và tham số Timeout.")

    # Đọc cấu hình settings và tools hiện tại
    with open(SETTINGS_YAML_PATH, "r", encoding="utf-8") as f:
        settings_raw = yaml.safe_load(f)
    with open(TOOLS_YAML_PATH, "r", encoding="utf-8") as f:
        tools_raw = yaml.safe_load(f)

    execs = settings_raw.get("executables", {})
    tools_dict = tools_raw.get("tools", {})
    timing = settings_raw.get("timing", {})

    col_ide1, col_ide2, col_ide3 = st.columns(3)

    # 1. Cursor
    with col_ide1:
        st.markdown(f"""
        <div style="font-weight:700; color:#0B57D0; font-size:1.05rem; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
            {get_svg("code", size=18, color="#0B57D0")}
            <span>1. Cursor IDE</span>
        </div>
        """, unsafe_allow_html=True)
        cursor_exe = st.text_input("Đường dẫn Cursor.exe:", value=execs.get("cursor", ""), key="cfg_cursor_exe")
        cursor_exists = Path(cursor_exe).exists() if cursor_exe else False
        st.caption(f"Trạng thái tệp: {'✅ Đã tìm thấy file .exe' if cursor_exists else '⚠️ File không tồn tại hoặc sai đường dẫn'}")
        
        cursor_model = st.text_input("Model AI cố định (Cursor):", value=tools_dict.get("cursor", {}).get("fixed_model", "claude-3-5-sonnet-20241022"), key="cfg_cursor_model")
        cursor_agent = st.text_input("Tên Agent:", value=tools_dict.get("cursor", {}).get("agent_name", "Cursor Agent"), key="cfg_cursor_agent")

    # 2. Windsurf
    with col_ide2:
        st.markdown(f"""
        <div style="font-weight:700; color:#006874; font-size:1.05rem; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
            {get_svg("rocket", size=18, color="#006874")}
            <span>2. Windsurf IDE</span>
        </div>
        """, unsafe_allow_html=True)
        windsurf_exe = st.text_input("Đường dẫn Windsurf.exe:", value=execs.get("windsurf", ""), key="cfg_windsurf_exe")
        windsurf_exists = Path(windsurf_exe).exists() if windsurf_exe else False
        st.caption(f"Trạng thái tệp: {'✅ Đã tìm thấy file .exe' if windsurf_exists else '⚠️ File không tồn tại hoặc sai đường dẫn'}")
        
        windsurf_model = st.text_input("Model AI cố định (Windsurf):", value=tools_dict.get("windsurf", {}).get("fixed_model", "claude-3-5-sonnet"), key="cfg_windsurf_model")
        windsurf_agent = st.text_input("Tên Agent:", value=tools_dict.get("windsurf", {}).get("agent_name", "Cascade"), key="cfg_windsurf_agent")

    # 3. VS Code
    with col_ide3:
        st.markdown(f"""
        <div style="font-weight:700; color:#146C2E; font-size:1.05rem; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
            {get_svg("task", size=18, color="#146C2E")}
            <span>3. Visual Studio Code</span>
        </div>
        """, unsafe_allow_html=True)
        vscode_exe = st.text_input("Đường dẫn Code.exe:", value=execs.get("vscode", ""), key="cfg_vscode_exe")
        vscode_exists = Path(vscode_exe).exists() if vscode_exe else False
        st.caption(f"Trạng thái tệp: {'✅ Đã tìm thấy file .exe' if vscode_exists else '⚠️ File không tồn tại hoặc sai đường dẫn'}")
        
        vscode_model = st.text_input("Model AI cố định (VS Code):", value=tools_dict.get("vscode", {}).get("fixed_model", "gpt-4o"), key="cfg_vscode_model")
        vscode_agent = st.text_input("Tên Agent:", value=tools_dict.get("vscode", {}).get("agent_name", "GitHub Copilot Agent"), key="cfg_vscode_agent")

    st.divider()

    # Tham số thời gian chờ tối đa (Timeout & Timing)
    st.markdown(f"""
    <div style="font-weight:700; color:#1F1F1F; font-size:1.05rem; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
        {get_svg("history", size=20, color="#0B57D0")}
        <span>Tham Số Thời Gian Chờ (Timeout & Timing)</span>
    </div>
    """, unsafe_allow_html=True)
    
    t_c1, t_c2, t_c3 = st.columns(3)
    with t_c1:
        new_timeout = st.number_input("Timeout tối đa chờ sinh code (giây):", min_value=30, max_value=600, value=int(timing.get("timeout_seconds", 180)), step=10)
    with t_c2:
        new_quiet = st.number_input("Thời gian tĩnh lặng file trước khi xác nhận (giây):", min_value=3, max_value=60, value=int(timing.get("quiet_period_seconds", 10)), step=1)
    with t_c3:
        new_cooldown = st.number_input("Thời gian nghỉ cooldown giữa các lượt chạy (giây):", min_value=1, max_value=60, value=int(timing.get("cooldown_seconds", 10)), step=1)

    if st.button("Lưu Cấu Hình IDE & Hệ Thống", type="primary", icon=":material/save:"):
        try:
            # 1. Cập nhật settings.yaml
            settings_raw["executables"]["cursor"] = cursor_exe.strip()
            settings_raw["executables"]["windsurf"] = windsurf_exe.strip()
            settings_raw["executables"]["vscode"] = vscode_exe.strip()
            
            settings_raw["timing"]["timeout_seconds"] = int(new_timeout)
            settings_raw["timing"]["quiet_period_seconds"] = int(new_quiet)
            settings_raw["timing"]["cooldown_seconds"] = int(new_cooldown)
            
            with open(SETTINGS_YAML_PATH, "w", encoding="utf-8") as f:
                yaml.dump(settings_raw, f, allow_unicode=True, default_flow_style=False)

            # 2. Cập nhật tools.yaml
            if "cursor" in tools_dict:
                tools_dict["cursor"]["fixed_model"] = cursor_model.strip()
                tools_dict["cursor"]["agent_name"] = cursor_agent.strip()
            if "windsurf" in tools_dict:
                tools_dict["windsurf"]["fixed_model"] = windsurf_model.strip()
                tools_dict["windsurf"]["agent_name"] = windsurf_agent.strip()
            if "vscode" in tools_dict:
                tools_dict["vscode"]["fixed_model"] = vscode_model.strip()
                tools_dict["vscode"]["agent_name"] = vscode_agent.strip()

            tools_raw["tools"] = tools_dict
            with open(TOOLS_YAML_PATH, "w", encoding="utf-8") as f:
                yaml.dump(tools_raw, f, allow_unicode=True, default_flow_style=False)

            st.success("Đã cập nhật toàn bộ cấu hình IDE và tham số hệ thống thành công!")
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi lưu cấu hình: {e}")
