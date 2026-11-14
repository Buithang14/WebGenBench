import streamlit as st
import time
from pathlib import Path
import sys
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from experiment.task_loader import load_task, list_available_tasks
from config.loader import load_tools
from experiment.single_runner import execute_single_run
from experiment.batch_runner import BatchRunner
from rendering.browser_renderer import BrowserRenderer
from metrics.evaluator import evaluate_run
from storage.db_manager import DBManager
from dashboard.theme import (
    apply_m3_theme,
    m3_header,
    m3_card,
    m3_elevated_card,
    m3_outlined_card,
    m3_banner,
    m3_chip
)
from dashboard.icons import get_svg

st.set_page_config(page_title="Điều Khiển Thí Nghiệm - WebGenBench (M3)", page_icon=":material/rocket_launch:", layout="wide")
apply_m3_theme()

m3_header(
    title="Quản Lý & Điều Khiển Thí Nghiệm (Experiment Runner)",
    subtitle="Màn hình 1 theo Kế hoạch: Điều khiển chạy đơn lẻ hoặc quản lý tiến độ ma trận 144 lần chạy tự động (Start / Resume / Retry)",
    icon_name="rocket"
)

db = DBManager()
db.init_db()
batch_runner = BatchRunner(db_manager=db)
tools_config = load_tools()
available_tasks = list_available_tasks()

tab_single, tab_batch = st.tabs([
    "Chạy Đơn Lẻ (Single Run)",
    "Ma Trận & Hàng Đợi 144 Lần Chạy (Batch Matrix Runner)"
])

# ==================== TAB 1: CHẠY ĐƠN LẺ ====================
with tab_single:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:15px;">
        {get_svg("play", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">1. Thiết Lập & Khởi Động Lượt Chạy Đơn Lẻ</span>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.1, 0.9])

    with col_left:
        ide_options = list(tools_config.tools.keys())
        selected_ide = st.selectbox(
            "Chọn Công cụ IDE (AI Agent):",
            options=ide_options,
            format_func=lambda x: f"{tools_config.tools[x].name} ({tools_config.tools[x].agent_name})",
            help="IDE tích hợp AI Agent sẽ được tự động mở và gửi lệnh."
        )
        
        selected_task_id = st.selectbox(
            "Chọn Bài tập Benchmark (Task):",
            options=available_tasks,
            index=0 if available_tasks else None
        )

        condition = st.radio(
            "Điều kiện thực nghiệm (Prompt Condition):",
            options=["text_only", "text_image"],
            format_func=lambda x: "Điều kiện A: Chỉ Prompt văn bản (text_only)" if x == "text_only" else "Điều kiện B: Prompt văn bản + Ảnh tham chiếu (text_image)",
            help="Điều kiện B sẽ sao chép ảnh thiết kế chuẩn vào clipboard và dán vào panel của AI Agent."
        )

        custom_run_id = st.text_input(
            "Mã định danh lần chạy (Run ID - Tùy chọn):",
            placeholder="Để trống để tự động sinh theo chuẩn: ide_task_condition_timestamp...",
            help="Ví dụ: cursor_T01_text_only_rep1"
        )

        with st.expander("Tham số nâng cao (Thời gian chờ & Tự động chấm điểm)"):
            timeout_sec = st.slider("Timeout tối đa chờ sinh code (giây):", min_value=60, max_value=600, value=180, step=30)
            quiet_sec = st.slider("Thời gian tĩnh lặng file trước khi chốt (giây):", min_value=5, max_value=30, value=10, step=1)
            auto_eval = st.checkbox("Tự động Render Chromium và Chấm điểm ngay sau khi sinh code", value=True)

        if st.button("BẮT ĐẦU CHẠY SINGLE RUN", type="primary", icon=":material/play_arrow:", use_container_width=True):
            if not selected_task_id:
                st.error("Vui lòng chọn bài tập!")
                st.stop()

            run_id_val = custom_run_id.strip() if custom_run_id.strip() else None

            progress_bar = st.progress(0, text="Đang khởi tạo môi trường...")
            status_box = st.empty()

            try:
                progress_bar.progress(20, text=f"Đang khởi chạy {selected_ide.upper()} và nạp prompt vào AI Agent...")
                status_box.info("Đang thực thi GUI Automation trên màn hình desktop. Vui lòng không chạm chuột/bàn phím...")

                res = execute_single_run(
                    ide_name=selected_ide,
                    task_id=selected_task_id,
                    condition=condition,
                    run_id=run_id_val,
                    timeout_seconds=timeout_sec,
                    quiet_period_seconds=quiet_sec,
                )

                actual_run_id = res.get("run_id")

                if res.get("status") != "SUCCESS":
                    progress_bar.progress(100, text="Quá trình sinh code thất bại!")
                    status_box.error(f"Lượt chạy kết thúc với lỗi: {res.get('error_message')}")
                    st.stop()

                progress_bar.progress(60, text="Sinh code thành công! Đang tiến hành kết xuất Playwright...")
                status_box.success(f"AI đã hoàn tất sinh mã trong {res.get('duration_seconds')}s!")

                if auto_eval:
                    progress_bar.progress(75, text="Đang kết xuất Chromium và chụp ảnh 3 viewports...")
                    renderer = BrowserRenderer()
                    render_report = renderer.render_run(actual_run_id)

                    progress_bar.progress(90, text="Đang chấm điểm 6 nhóm tiêu chí định lượng...")
                    eval_report = evaluate_run(run_id=actual_run_id, task_id=selected_task_id)

                    progress_bar.progress(98, text="Đang đồng bộ dữ liệu vào SQLite...")
                    db.sync_run_from_disk(actual_run_id)

                progress_bar.progress(100, text="Hoàn tất trọn vẹn toàn bộ quy trình!")
                st.balloons()
                st.success(f"Lượt chạy [{actual_run_id}] đã hoàn thành xuất sắc!")

            except Exception as e:
                progress_bar.progress(100, text="Đã xảy ra lỗi!")
                status_box.error(f"Đã xảy ra lỗi trong quá trình thực thi: {e}")

    with col_right:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            {get_svg("task", size=20, color="#0B57D0")}
            <span style="font-weight:700; font-size:1.05rem; color:#1F1F1F;">Thông Tin Đề Bài & Ảnh Chuẩn</span>
        </div>
        """, unsafe_allow_html=True)
        
        if selected_task_id:
            try:
                task_data = load_task(selected_task_id)
                meta = task_data.meta
                st.markdown(f"**Bài tập:** `{meta.task_id}` - *{meta.title_vi}*")
                ref_img_path = ROOT_DIR / meta.reference_image
                if ref_img_path.exists():
                    st.image(str(ref_img_path), caption=f"Ảnh chuẩn: {meta.reference_image}", use_column_width=True)
                with st.expander("Xem nội dung Prompt"):
                    st.code(task_data.prompt_text, language="markdown")
            except Exception as e:
                st.error(f"Lỗi nạp bài tập: {e}")

# ==================== TAB 2: MA TRẬN 144 LẦN CHẠY ====================
with tab_batch:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
        {get_svg("analytics", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">2. Quản Lý Tiến Độ Ma Trận Thí Nghiệm (144 Runs Matrix)</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Thiết kế nghiên cứu: 3 IDE × Tasks × 2 Điều kiện (Text-only / Text+Image) × 3 Lần lặp lại (Repetitions)")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        batch_ides = st.multiselect("Lọc IDE trong ma trận:", options=list(tools_config.tools.keys()), default=list(tools_config.tools.keys()))
    with col_f2:
        batch_tasks = st.multiselect("Lọc Tasks trong ma trận:", options=available_tasks, default=available_tasks)
    with col_f3:
        batch_reps = st.slider("Số lần lặp lại mỗi bài (Repetitions):", min_value=1, max_value=5, value=3)

    planned_matrix = batch_runner.generate_full_matrix(ides=batch_ides, tasks=batch_tasks, repetitions=batch_reps)
    progress_stats = batch_runner.get_matrix_progress(planned_matrix)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        m3_card(value=str(progress_stats["total_planned"]), label="Tổng lượt dự kiến", secondary="Toàn bộ ma trận thử nghiệm", badge="Planned", badge_type="primary", icon_name="task")
    with c2:
        m3_card(value=str(progress_stats["completed_count"]), label="Đã hoàn thành", secondary=f"{progress_stats['progress_percent']}% tiến độ", badge="Success", badge_type="success", icon_name="check_circle")
    with c3:
        m3_card(value=str(progress_stats["pending_count"]), label="Đang chờ thực thi", secondary="Các run chưa chạy", badge="Pending", badge_type="neutral", icon_name="history")
    with c4:
        m3_card(value=str(progress_stats["failed_count"]), label="Thất bại / Lỗi", secondary="Cần chạy lại (Retry)", badge="Failed" if progress_stats["failed_count"] > 0 else "Clean", badge_type="error" if progress_stats["failed_count"] > 0 else "success", icon_name="error")

    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(progress_stats["progress_percent"] / 100.0, text=f"Tiến độ ma trận: {progress_stats['progress_percent']}% ({progress_stats['completed_count']}/{progress_stats['total_planned']} Runs)")

    action_cols = st.columns([1, 1, 2])
    with action_cols[0]:
        start_resume_btn = st.button("Bắt Đầu / Tiếp Tục (Start / Resume)", icon=":material/play_circle:", type="primary", use_container_width=True)
    with action_cols[1]:
        retry_btn = st.button("Chạy Lại Các Lượt Lỗi (Retry Failed)", icon=":material/replay:", use_container_width=True)

    if start_resume_btn:
        pending_list = progress_stats["pending"]
        if not pending_list:
            m3_banner("Toàn bộ các lượt chạy trong ma trận đã hoàn thành 100%!", banner_type="success", icon_name="check_circle")
        else:
            next_run = pending_list[0]
            m3_banner(
                f"Đang chuẩn bị chạy lượt tiếp theo trong hàng đợi: <b>{next_run['run_id']}</b> (IDE: {next_run['ide_name'].upper()}, Task: {next_run['task_id']}, ĐK: {next_run['prompt_condition']})...",
                banner_type="info",
                icon_name="info"
            )
            m3_banner(
                "Để đảm bảo tính tương tác của chuột và bàn phím trên Desktop, hệ thống khuyên dùng lệnh CLI chạy batch liên tục để tránh bị Streamlit timeout.",
                banner_type="warning",
                icon_name="warning"
            )
            st.code(f"python main.py run-once -i {next_run['ide_name']} -t {next_run['task_id']} -c {next_run['prompt_condition']} -r {next_run['run_id']}", language="bash")

    if retry_btn:
        failed_list = progress_stats["failed"]
        if not failed_list:
            m3_banner("Không có lượt chạy nào bị lỗi cần chạy lại.", banner_type="info", icon_name="info")
        else:
            m3_banner(f"Có {len(failed_list)} lượt chạy bị lỗi. Bấm vào từng lượt trong bảng bên dưới để chạy lại.", banner_type="warning", icon_name="warning")

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-top:20px; margin-bottom:8px;">
        {get_svg("table_chart", size=20, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.05rem; color:#1F1F1F;">Bảng Chi Tiết Hàng Đợi Toàn Bộ Ma Trận</span>
    </div>
    """, unsafe_allow_html=True)

    all_matrix_items = progress_stats["completed"] + progress_stats["failed"] + progress_stats["pending"]
    df_matrix = pd.DataFrame(all_matrix_items)
    if not df_matrix.empty:
        col_rename = {
            "run_id": "Mã Lần Chạy",
            "ide_name": "IDE",
            "task_id": "Bài Tập",
            "prompt_condition": "Điều Kiện",
            "repetition": "Lần Lặp",
            "status": "Trạng Thái",
            "duration": "Thời Gian (s)"
        }
        st.dataframe(df_matrix.rename(columns=col_rename), use_container_width=True, hide_index=True)
