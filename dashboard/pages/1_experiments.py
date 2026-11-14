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

st.set_page_config(
    page_title="Điều Khiển Thí Nghiệm - WebGenBench (M3)",
    page_icon=":material/rocket_launch:",
    layout="wide"
)
apply_m3_theme()

m3_header(
    title="Khu Vực Điều Khiển Chạy Thí Nghiệm",
    icon_name="rocket"
)

db = DBManager()
db.init_db()
batch_runner = BatchRunner(db_manager=db)
tools_config = load_tools()
available_tasks = list_available_tasks()

tab_single, tab_batch = st.tabs([
    "Chế Độ 1 – Chạy Thử 1 Lượt (Single Run)",
    "Chế Độ 2 – Chạy Hàng Loạt 144 Lần (Batch Experiment)"
])

# ==================== CHẾ ĐỘ 1: CHẠY THỬ 1 LƯỢT ====================
with tab_single:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; padding-top:10px; margin-top:8px; margin-bottom:18px;">
        {get_svg("play", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">Thiết Lập Thực Nghiệm Đơn Lẻ</span>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.1, 0.9], gap="large")

    with col_left:
        # 1. Ô chọn Công cụ IDE
        ide_options = list(tools_config.tools.keys())
        selected_ide = st.selectbox(
            "1. Chọn Công cụ IDE (AI Coding Agent):",
            options=ide_options,
            format_func=lambda x: f"{tools_config.tools[x].name} ({tools_config.tools[x].agent_name} - {tools_config.tools[x].fixed_model})",
            help="Hệ thống sẽ tự động khởi chạy IDE này và nạp prompt vào AI Agent."
        )
        
        # 2. Ô chọn Bài tập
        selected_task_id = st.selectbox(
            "2. Chọn Bài tập (T01 → T08):",
            options=available_tasks,
            index=0 if available_tasks else None,
            format_func=lambda x: f"[{x}] {load_task(x).meta.name} - {load_task(x).meta.title_vi}"
        )

        # 3. Ô chọn Điều kiện
        condition = st.radio(
            "3. Chọn Điều kiện thực nghiệm:",
            options=["text_only", "text_image"],
            format_func=lambda x: "Chỉ có chữ (Text-only)" if x == "text_only" else "Chữ + Ảnh thiết kế (Text + Image)",
            help="Text + Image sẽ nạp cả nội dung văn bản và đính kèm ảnh tham chiếu thiết kế vào cửa sổ AI Agent."
        )

        custom_run_id = st.text_input(
            "Mã định danh lần chạy (Run ID - Tùy chọn):",
            placeholder="Để trống để tự động sinh (ví dụ: cursor_T01_text_only_rep1)",
            help="Nếu để trống, hệ thống sẽ tự động sinh mã định danh theo chuẩn NCKH."
        )

        with st.expander("Tham số thời gian chờ & Render"):
            timeout_sec = st.slider("Timeout tối đa chờ sinh code (giây):", min_value=60, max_value=600, value=180, step=30)
            quiet_sec = st.slider("Thời gian tĩnh lặng file trước khi xác nhận (giây):", min_value=5, max_value=30, value=10, step=1)

        # Nhóm 2 nút bấm to rõ ràng theo đúng đặc tả Plan & Giao diện.docx
        btn_col1, btn_col2 = st.columns([1.2, 1.0])
        with btn_col1:
            start_btn = st.button("Bắt đầu Chạy & Chấm điểm", type="primary", icon=":material/play_arrow:", use_container_width=True)
        with btn_col2:
            reeval_btn = st.button("Chấm điểm lại", icon=":material/replay:", use_container_width=True, help="Chạy lại Render Playwright và tính điểm 6 tiêu chí cho code đã sinh ra.")

        # Xử lý nút: Bắt đầu chạy & chấm điểm
        if start_btn:
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

        # Xử lý nút: Chấm điểm lại (Re-evaluate)
        if reeval_btn:
            target_id = custom_run_id.strip()
            if not target_id:
                # Lấy run_id gần nhất có sẵn của bài tập này
                all_runs = db.list_all_runs()
                matched = [r["run_id"] for r in all_runs if r["task_id"] == selected_task_id and r["ide_name"] == selected_ide]
                if matched:
                    target_id = matched[-1]
                else:
                    st.warning("Vui lòng nhập Run ID cần chấm điểm lại hoặc đảm bảo đã có sẵn lượt chạy trong outputs/.")
                    st.stop()

            st.info(f"Đang tiến hành chấm điểm lại cho: <b>{target_id}</b>...", icon=":material/sync:")
            try:
                renderer = BrowserRenderer()
                renderer.render_run(target_id)
                eval_res = evaluate_run(run_id=target_id, task_id=selected_task_id)
                db.sync_run_from_disk(target_id)
                st.success(f"Đã chấm điểm lại thành công cho [{target_id}]! Điểm mới: {eval_res.get('total_score', 0):.2f}/100")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi chấm điểm lại: {e}")

    with col_right:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            {get_svg("task", size=20, color="#0B57D0")}
            <span style="font-weight:700; font-size:1.05rem; color:#1F1F1F;">Thông Tin Đề Bài & Ảnh Thiết Kế Mẫu</span>
        </div>
        """, unsafe_allow_html=True)
        
        if selected_task_id:
            try:
                task_data = load_task(selected_task_id)
                meta = task_data.meta
                st.markdown(f"**Bài tập:** `[{meta.task_id}] {meta.name}` - *{meta.title_vi}*")
                ref_img_path = ROOT_DIR / meta.reference_image
                if ref_img_path.exists():
                    st.image(str(ref_img_path), caption=f"Ảnh thiết kế mẫu: {meta.reference_image}", use_container_width=True)
                with st.expander("Xem trước Prompt chuẩn"):
                    st.code(task_data.prompt_text, language="markdown")
            except Exception as e:
                st.error(f"Lỗi nạp bài tập: {e}")

# ==================== CHẾ ĐỘ 2: CHẠY HÀNG LOẠT 144 LẦN ====================
with tab_batch:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; padding-top:10px; margin-top:8px; margin-bottom:10px;">
        {get_svg("analytics", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">Chiến Dịch Thí Nghiệm Ma Trận 144 Runs</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Thiết kế ma trận đầy đủ: 3 IDEs × 8 Tasks × 2 Điều kiện (Text-only / Text+Image) × 3 Lần lặp = 144 Lượt chạy")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        batch_ides = st.multiselect("Lọc IDE trong chiến dịch:", options=list(tools_config.tools.keys()), default=list(tools_config.tools.keys()))
    with col_f2:
        batch_tasks = st.multiselect("Lọc Tasks trong chiến dịch:", options=available_tasks, default=available_tasks)
    with col_f3:
        batch_reps = st.slider("Số lần lặp lại mỗi bài (Repetitions):", min_value=1, max_value=5, value=3)

    planned_matrix = batch_runner.generate_full_matrix(ides=batch_ides, tasks=batch_tasks, repetitions=batch_reps)
    progress_stats = batch_runner.get_matrix_progress(planned_matrix)

    # Thẻ thống kê KPI ma trận
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

    # Thanh tiến trình hiển thị rõ lượt thứ mấy đúng đặc tả Giao diện.docx
    completed_idx = progress_stats["completed_count"]
    total_planned = progress_stats["total_planned"]
    current_run_info = ""
    if progress_stats["pending"]:
        next_item = progress_stats["pending"][0]
        current_run_info = f" - Đang chuẩn bị: {next_item['ide_name'].upper()} - {next_item['task_id']} ({next_item['prompt_condition']})"
    elif completed_idx == total_planned and total_planned > 0:
        current_run_info = " - Toàn bộ 144 lượt chạy đã hoàn thành xuất sắc!"

    st.progress(
        progress_stats["progress_percent"] / 100.0,
        text=f"Đang chạy {completed_idx}/{total_planned}{current_run_info}"
    )

    # Các nút điều khiển chiến dịch theo đặc tả
    action_cols = st.columns([1.2, 1.2, 1.0])
    with action_cols[0]:
        start_batch_btn = st.button("Khởi chạy Chiến dịch 144 Runs", icon=":material/rocket_launch:", type="primary", use_container_width=True)
    with action_cols[1]:
        pause_resume_btn = st.button("Tạm dừng / Chạy tiếp", icon=":material/pause_circle:", use_container_width=True)
    with action_cols[2]:
        retry_failed_btn = st.button("Chạy Lại Các Lượt Lỗi", icon=":material/replay:", use_container_width=True)

    if start_batch_btn or pause_resume_btn:
        pending_list = progress_stats["pending"]
        if not pending_list:
            m3_banner("Chiến dịch 144 runs đã hoàn tất 100%! Không còn lượt chạy nào trong hàng đợi.", banner_type="success", icon_name="check_circle")
        else:
            next_run = pending_list[0]
            m3_banner(
                f"Lệnh tự động cho lượt kế tiếp trong hàng đợi 144 runs: <b>{next_run['run_id']}</b>",
                banner_type="info",
                icon_name="info"
            )
            st.code(f"python main.py run-once -i {next_run['ide_name']} -t {next_run['task_id']} -c {next_run['prompt_condition']} -r {next_run['run_id']}", language="bash")
            st.caption("Khuyến nghị: Chạy qua giao diện dòng lệnh CLI (main.py) đối với chiến dịch dài để hệ thống điều khiển chuột và phím xuyên suốt mà không phụ thuộc phiên trình duyệt.")

    if retry_failed_btn:
        failed_list = progress_stats["failed"]
        if not failed_list:
            m3_banner("Tuyệt vời! Không có lượt chạy nào trong ma trận bị lỗi.", banner_type="success", icon_name="check_circle")
        else:
            m3_banner(f"Phát hiện {len(failed_list)} lượt chạy bị lỗi. Bấm vào mã lỗi trong danh sách dưới để thử lại.", banner_type="warning", icon_name="warning")

    # Khung xem Nhật ký hoạt động trực tiếp (Live Log) theo đặc tả Giao diện.docx
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-top:20px; margin-bottom:8px;">
        <div style="display:flex; align-items:center; gap:8px;">
            {get_svg("code", size=20, color="#0B57D0")}
            <span style="font-weight:700; font-size:1.05rem; color:#1F1F1F;">Nhật Ký Hoạt Động Trực Tiếp (Live Log)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    log_file = ROOT_DIR / "logs" / "webgenbench.log"
    if not log_file.exists():
        # Fallback thử tìm tệp log bất kỳ trong logs/
        log_candidates = list((ROOT_DIR / "logs").glob("*.log"))
        log_file = log_candidates[0] if log_candidates else None

    if log_file and log_file.exists():
        try:
            log_lines = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            recent_logs = "\n".join(log_lines[-40:])
            st.code(recent_logs or "Chưa có log mới ghi nhận...", language="log")
        except Exception as e:
            st.caption(f"Không thể đọc file log: {e}")
    else:
        st.info("Chưa có tệp nhật ký ghi nhận trong logs/. Khi có lượt chạy diễn ra, log sẽ hiển thị tại đây.")

    # Bảng chi tiết hàng đợi
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-top:16px; margin-bottom:8px;">
        {get_svg("table_chart", size=20, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.05rem; color:#1F1F1F;">Chi Tiết Hàng Đợi 144 Lượt Chạy</span>
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
