import sys
import time
from pathlib import Path
from typing import Optional
import click

from config.logger import logger
from config.loader import load_all_configs
from experiment.task_loader import load_task, list_available_tasks
from automation.cursor.cursor_adapter import CursorAdapter

BASE_DIR = Path(__file__).resolve().parent

REQUIRED_DIRECTORIES = [
    "workspace",
    "outputs",
    "logs",
    "tasks",
    "designs",
]

@click.group()
def cli():
    """WebGenBench - Nền tảng đánh giá năng lực sinh giao diện web của các IDE AI."""
    pass


@cli.command(name="check-config")
def check_config():
    """Kiểm tra và xác thực toàn bộ cấu hình, thư mục và môi trường của WebGenBench."""
    logger.info(">>> Bắt đầu quá trình kiểm tra cấu hình hệ thống WebGenBench...")

    # 1. Kiểm tra sự tồn tại của các thư mục cốt lõi
    logger.info("Kiểm tra sự tồn tại của các thư mục quan trọng:")
    all_dirs_exist = True
    for dir_name in REQUIRED_DIRECTORIES:
        dir_path = BASE_DIR / dir_name
        exists = dir_path.is_dir()
        status_text = "[OK] Đã tồn tại" if exists else "[THIẾU] Chưa tồn tại"
        logger.info(f" - Thư mục '{dir_name}/': {status_text}")
        if not exists:
            all_dirs_exist = False

    if not all_dirs_exist:
        logger.error("Một số thư mục bắt buộc bị thiếu. Vui lòng kiểm tra lại!")
        sys.exit(1)

    # 2. Đọc và xác thực cấu hình YAML
    try:
        app_config = load_all_configs()
        logger.info("Xác thực các file cấu hình YAML thành công!")
    except Exception as e:
        logger.error(f"Lỗi khi đọc/xác thực cấu hình: {e}")
        sys.exit(1)

    # 3. In bảng tóm tắt cấu hình 3 IDE
    click.echo("\n" + "=" * 70)
    click.echo("           BẢNG CẤU HÌNH CÁC CÔNG CỤ IDE (AI AGENTS)")
    click.echo("=" * 70)
    header_tools = f"{'Mã công cụ':<12} | {'Tên IDE':<18} | {'Agent':<22} | {'Shortcut':<10}"
    click.echo(header_tools)
    click.echo("-" * 70)
    for tool_key, tool in app_config.tools.tools.items():
        row = f"{tool_key:<12} | {tool.name:<18} | {tool.agent_name:<22} | {tool.shortcut:<10}"
        click.echo(row)
    click.echo("=" * 70)

    # 4. In bảng trọng số 6 tiêu chí chấm điểm
    weights = app_config.scoring.weights
    click.echo("\n" + "=" * 70)
    click.echo("           BẢNG TRỌNG SỐ 6 NHÓM TIÊU CHÍ ĐÁNH GIÁ")
    click.echo("=" * 70)
    header_scoring = f"{'STT':<4} | {'Nhóm tiêu chí':<25} | {'Trọng số':<12} | {'Tỷ lệ':<8}"
    click.echo(header_scoring)
    click.echo("-" * 70)
    
    scoring_items = [
        ("1", "HTML Validity", weights.html_validity),
        ("2", "Accessibility", weights.accessibility),
        ("3", "Responsive Design", weights.responsive),
        ("4", "Design Similarity", weights.design_similarity),
        ("5", "Code Quality", weights.code_quality),
        ("6", "Runtime Cleanliness", weights.runtime_cleanliness),
    ]
    
    total_weight = sum(item[2] for item in scoring_items)
    for idx, name, w in scoring_items:
        click.echo(f"{idx:<4} | {name:<25} | {w:<12.2f} | {w * 100:>5.1f}%")
    click.echo("-" * 70)
    click.echo(f"{'TỔNG':<4} | {'TẤT CẢ TIÊU CHÍ':<25} | {total_weight:<12.2f} | {total_weight * 100:>5.1f}%")
    click.echo("=" * 70)

    # 5. Tóm tắt thông số Timing & Viewports
    click.echo("\n" + "=" * 70)
    click.echo("           THÔNG SỐ THỜI GIAN & ĐỘ RỘNG MÀN HÌNH CHỤP ẢNH")
    click.echo("=" * 70)
    timing = app_config.settings.timing
    click.echo(f" - Timeout tối đa         : {timing.timeout_seconds}s")
    click.echo(f" - Thời gian tĩnh (quiet) : {timing.quiet_period_seconds}s")
    click.echo(f" - Thời gian chờ (cooldown): {timing.cooldown_seconds}s")
    click.echo(f" - Viewports kiểm thử     : {app_config.settings.viewports} (px)")
    click.echo("=" * 70 + "\n")

    logger.success("Hoàn tất kiểm tra: Hệ thống sẵn sàng cho Milestone 2!")


@cli.command(name="show-task")
@click.option("--task-id", "-t", default="T01", help="Mã định danh của bài tập (mặc định: T01)")
def show_task(task_id: str):
    """Hiển thị thông tin chi tiết, yêu cầu và nội dung prompt của một bài tập benchmark."""
    logger.info(f">>> Đang nạp và kiểm tra dữ liệu bài tập benchmark '{task_id}'...")

    try:
        task_data = load_task(task_id)
    except Exception as e:
        logger.error(f"Không thể nạp bài tập '{task_id}': {e}")
        available = list_available_tasks()
        if available:
            logger.info(f"Các bài tập hiện có: {', '.join(available)}")
        sys.exit(1)

    meta = task_data.meta

    click.echo("\n" + "=" * 75)
    click.echo(f"        THÔNG TIN BÀI TẬP BENCHMARK: [{meta.task_id}] {meta.name.upper()}")
    click.echo("=" * 75)
    click.echo(f" - Tiêu đề tiếng Việt     : {meta.title_vi}")
    click.echo(f" - File prompt định nghĩa : {meta.prompt_file}")
    click.echo(f" - Các file kết quả mong đợi : {', '.join(meta.expected_files)}")
    
    # Kích thước ảnh thiết kế
    dim_str = f"{task_data.image_dimensions[0]}x{task_data.image_dimensions[1]} px" if task_data.image_dimensions else "Chưa xác định"
    click.echo(f" - Ảnh thiết kế chuẩn     : {meta.reference_image} [Kích thước: {dim_str}]")

    # Danh sách yêu cầu giao diện (UI)
    click.echo("\n" + "-" * 75)
    click.echo(" [YÊU CẦU GIAO DIỆN (UI)]:")
    for idx, req in enumerate(meta.ui_requirements, 1):
        click.echo(f"   {idx}. {req}")

    # Danh sách yêu cầu kỹ thuật
    click.echo("\n" + "-" * 75)
    click.echo(" [YÊU CẦU KỸ THUẬT]:")
    for idx, req in enumerate(meta.technical_requirements, 1):
        click.echo(f"   {idx}. {req}")

    # Nội dung Prompt chuẩn
    click.echo("\n" + "-" * 75)
    click.echo(" [NỘI DUNG PROMPT CHUẨN SẼ GỬI VÀO CÁC IDE AI AGENTS]:")
    click.echo("-" * 75)
    click.echo(task_data.prompt_text)
    click.echo("=" * 75 + "\n")

    logger.success(f"Xác thực bài tập '{task_id}' thành công! Dữ liệu đầu vào đã sẵn sàng.")


@cli.command(name="test-ide")
@click.option("--ide", "-i", type=click.Choice(["cursor", "windsurf", "vscode"], case_sensitive=False), default="cursor", help="Tên IDE cần kiểm tra (cursor, windsurf, vscode)")
@click.option("--action", "-a", type=click.Choice(["smoke-test", "check-path", "launch", "inspect", "close", "test-prompt"], case_sensitive=False), default="smoke-test", help="Hành động kiểm tra")
@click.option("--condition", "-c", type=click.Choice(["text_only", "text_image"], case_sensitive=False), default="text_only", help="Điều kiện thực nghiệm (text_only hoặc text_image)")
def test_ide(ide: str, action: str, condition: str):
    """Kiểm tra điều khiển GUI Automation cho các công cụ IDE."""
    ide = ide.lower()
    logger.info(f">>> Bắt đầu kiểm tra IDE '{ide}' với hành động '{action}' (điều kiện: {condition})...")

    if ide == "cursor":
        adapter = CursorAdapter()
    else:
        logger.error(f"IDE '{ide}' chưa được triển khai trong Milestone này.")
        sys.exit(1)

    if action == "check-path":
        try:
            exe_path = adapter.resolve_executable_path()
            logger.success(f"Đường dẫn file thực thi {ide.upper()}: {exe_path}")
        except Exception as e:
            logger.error(f"Lỗi kiểm tra đường dẫn {ide}: {e}")
            sys.exit(1)
        return

    workspace_run = BASE_DIR / "workspace" / "current_run"
    log_dir = BASE_DIR / "logs"

    if action in ["smoke-test", "launch", "test-prompt"]:
        # 1. Kiểm tra đường dẫn
        try:
            exe_path = adapter.resolve_executable_path()
            logger.info(f"1. Xác nhận đường dẫn thực thi: {exe_path}")
        except Exception as e:
            logger.error(f"Không tìm thấy Cursor.exe: {e}")
            sys.exit(1)

        # 2. Chuẩn bị thư mục workspace/current_run sạch
        adapter.prepare_workspace(workspace_run)
        logger.info(f"2. Đã dọn dẹp thư mục làm việc: {workspace_run}")

        # 3. Mở IDE
        logger.info("3. Đang mở IDE...")
        if not adapter.launch_ide(workspace_run):
            logger.error("Mở IDE thất bại!")
            sys.exit(1)

        # 4. Kết nối cửa sổ và focus
        logger.info("4. Đang kết nối cửa sổ và focus...")
        if not adapter.connect_window(timeout=25):
            logger.error("Không thể kết nối tới cửa sổ IDE!")
            adapter.close_ide()
            sys.exit(1)

        adapter.focus_and_maximize()

        if action == "smoke-test":
            # 5. Xuất cây UI Automation
            tree_file = log_dir / "cursor_ui_tree.txt"
            logger.info(f"5. Đang xuất cây giao diện ra {tree_file.name}...")
            adapter.dump_ui_tree(tree_file, max_depth=4)

            # 6. Chờ 2 giây rồi đóng an toàn
            logger.info("6. Chờ 2 giây trước khi đóng cửa sổ an toàn...")
            time.sleep(2.0)
            adapter.close_ide()
            logger.success("Hoàn tất quy trình Smoke Test thành công!")

        elif action == "test-prompt":
            # 5. Nạp prompt và gửi lệnh
            test_prompt = "Hãy tạo một file hello.html đơn giản có tiêu đề Hello WebGenBench ngay trong thư mục hiện tại."
            image_path = None
            if condition == "text_image":
                image_path = BASE_DIR / "designs" / "T01_reference.png"
                logger.info(f"Đính kèm ảnh thiết kế theo điều kiện text_image: {image_path}")

            logger.info("5. Đang nạp prompt vào Cursor Agent...")
            submit_ok = adapter.submit_prompt(prompt_text=test_prompt, image_path=image_path)
            if not submit_ok:
                logger.error("Submit prompt thất bại!")
                adapter.close_ide()
                sys.exit(1)

            # 6. Chờ 5 giây quan sát rồi đóng IDE
            logger.info("6. Chờ 5 giây trước khi đóng cửa sổ...")
            time.sleep(5.0)
            adapter.close_ide()
            logger.success("Hoàn tất kiểm thử nạp prompt cho Cursor Agent!")

        else:
            logger.info("IDE đã được mở và giữ nguyên theo yêu cầu.")

    elif action == "inspect":
        if not adapter.connect_window(timeout=10):
            logger.error("Không tìm thấy cửa sổ Cursor đang chạy để inspect.")
            sys.exit(1)
        tree_file = log_dir / "cursor_ui_tree.txt"
        adapter.dump_ui_tree(tree_file, max_depth=4)
        logger.success(f"Đã xuất cây UI ra: {tree_file}")

    elif action == "close":
        if adapter.connect_window(timeout=5):
            adapter.close_ide()
            logger.success("Đã đóng cửa sổ Cursor.")
        else:
            logger.warning("Không tìm thấy cửa sổ Cursor nào để đóng.")


@cli.command(name="run-once")
@click.option("--ide", "-i", type=click.Choice(["cursor", "windsurf", "vscode"], case_sensitive=False), default="cursor", help="Tên IDE thực hiện benchmark")
@click.option("--task", "-t", default="T01", help="Mã bài tập benchmark (ví dụ: T01)")
@click.option("--condition", "-c", type=click.Choice(["text_only", "text_image"], case_sensitive=False), default="text_only", help="Điều kiện thực nghiệm (text_only hoặc text_image)")
@click.option("--run-id", "-r", default=None, help="Mã định danh lần chạy (tùy chọn, mặc định tự sinh)")
@click.option("--timeout", default=180, type=int, help="Thời gian tối đa chờ sinh code (giây)")
@click.option("--quiet", default=10, type=int, help="Thời gian tĩnh lặng file trước khi xác nhận xong (giây)")
def run_once(ide: str, task: str, condition: str, run_id: Optional[str], timeout: int, quiet: int):
    """Chạy trọn vẹn 1 lượt benchmark tự động (Vertical Slice) cho bài tập."""
    from experiment.single_runner import execute_single_run

    logger.info(f"Khởi động Single Runner: IDE={ide}, Task={task}, Condition={condition}, RunID={run_id}")
    res = execute_single_run(
        ide_name=ide,
        task_id=task,
        condition=condition,
        run_id=run_id,
        timeout_seconds=timeout,
        quiet_period_seconds=quiet,
    )
    if res.get("status") == "SUCCESS":
        logger.success(f"Lượt chạy {res.get('run_id')} thành công trong {res.get('duration_seconds')}s!")
    else:
        logger.error(f"Lượt chạy {res.get('run_id')} kết thúc với trạng thái: {res.get('status')} ({res.get('error_message')})")
        sys.exit(1)


@cli.command(name="render")
@click.option("--run-id", "-r", required=True, help="Mã định danh lần chạy cần render (ví dụ: run_001)")
def render_cli(run_id: str):
    """Mở project trên Chromium bằng Playwright, bắt lỗi runtime và chụp ảnh 3 viewport."""
    from rendering.browser_renderer import BrowserRenderer

    logger.info(f"Bắt đầu kết xuất trình duyệt cho: [{run_id}]...")
    renderer = BrowserRenderer()
    try:
        report = renderer.render_run(run_id)
        click.echo("\n" + "=" * 70)
        click.echo(f"   KẾT QUẢ RENDER PLAYWRIGHT CHO RUN: {run_id}")
        click.echo("=" * 70)
        click.echo(f" - Entry file HTML     : {report['entry_html']}")
        click.echo(f" - Server URL test     : {report['server_url']}")
        click.echo(f" - Lỗi Console Error   : {len(report['runtime_errors']['console_errors'])}")
        click.echo(f" - Lỗi PageError (JS)  : {len(report['runtime_errors']['page_errors'])}")
        click.echo(f" - Lỗi Request Failed  : {len(report['runtime_errors']['failed_requests'])}")
        click.echo("\n [ẢNH SCREENSHOT ĐÃ CHỤP]:")
        for vp, path in report["screenshots"].items():
            click.echo(f"   * Viewport {vp}px -> {path}")
        click.echo("=" * 70 + "\n")
        logger.success(f"Hoàn thành render và lưu báo cáo tại: outputs/{run_id}/render_report.json")
    except Exception as e:
        logger.error(f"Render thất bại: {e}")
        sys.exit(1)


@cli.command(name="evaluate")
@click.option("--run-id", "-r", required=True, help="Mã định danh lần chạy cần chấm điểm (ví dụ: run_001)")
@click.option("--task", "-t", default=None, help="Mã bài tập (tùy chọn, mặc định lấy từ metadata)")
def evaluate_cli(run_id: str, task: Optional[str]):
    """Chạy toàn bộ bộ máy chấm điểm định lượng 6 tiêu chí cho một Run."""
    from metrics.evaluator import evaluate_run

    logger.info(f"Bắt đầu quy trình chấm điểm tự động cho: [{run_id}]...")
    try:
        report = evaluate_run(run_id=run_id, task_id=task)

        click.echo("\n" + "=" * 80)
        click.echo(f"   BẢNG ĐIỂM ĐÁNH GIÁ ĐỊNH LƯỢNG WEBGENBENCH: [{run_id}] (Task: {report['task_id']})")
        click.echo("=" * 80)
        click.echo(f"{'Tiêu chí đánh giá':<26} | {'Điểm':<8} | {'Trọng số':<8} | {'Đóng góp':<10} | {'Trạng thái'}")
        click.echo("-" * 80)

        metric_titles = {
            "html_validity": "1. HTML Validity",
            "accessibility": "2. Accessibility (a11y)",
            "responsive": "3. Responsive Design",
            "design_similarity": "4. Design Similarity",
            "code_quality": "5. Code Quality",
            "runtime_cleanliness": "6. Runtime Cleanliness",
        }

        for k, info in report["metrics"].items():
            name_vi = metric_titles.get(k, k)
            sc = info["score"]
            w = info["weight"]
            cb = info["weighted_contribution"]
            status = "Xuất sắc" if sc >= 85 else ("Tốt" if sc >= 70 else "Cần cải thiện")
            click.echo(f"{name_vi:<26} | {sc:>6.1f}   | {w:>6.2f}   | {cb:>6.2f}đ    | {status}")

        click.echo("=" * 80)
        click.echo(f"  TỔNG ĐIỂM CHUẨN HÓA (TOTAL WEIGHTED SCORE):  {report['total_score']:.2f} / 100.00")
        click.echo("=" * 80 + "\n")

        # In danh sách cảnh báo nếu có
        issues_found = []
        for k, info in report["metrics"].items():
            for iss in info.get("issues", []):
                issues_found.append(f"[{metric_titles.get(k, k)}] {iss}")

        if issues_found:
            click.echo(" [CÁC VẤN ĐỀ CẦN LƯU Ý]:")
            for iss in issues_found[:8]:
                click.echo(f"   ! {iss}")
            if len(issues_found) > 8:
                click.echo(f"   ... và {len(issues_found) - 8} vấn đề khác (xem chi tiết trong metrics_report.json).")
            click.echo("")

        logger.success(f"Hoàn tất chấm điểm! Báo cáo đầy đủ: outputs/{run_id}/metrics_report.json")

    except Exception as e:
        logger.error(f"Đánh giá thất bại: {e}")
        sys.exit(1)


@cli.command(name="init-db")
def init_db_cli():
    """Khởi tạo CSDL SQLite và tự động đồng bộ các Run sẵn có trong outputs/ vào CSDL."""
    from storage.db_manager import DBManager

    logger.info(">>> Bắt đầu khởi tạo cơ sở dữ liệu SQLite cho WebGenBench...")
    db_manager = DBManager()
    db_manager.init_db()

    outputs_dir = BASE_DIR / "outputs"
    synced_count = 0
    if outputs_dir.exists():
        for run_dir in outputs_dir.iterdir():
            if run_dir.is_dir() and (run_dir / "run_metadata.json").exists():
                run_id = run_dir.name
                try:
                    db_manager.sync_run_from_disk(run_id)
                    synced_count += 1
                except Exception as e:
                    logger.warning(f"Lỗi khi đồng bộ {run_id}: {e}")

    click.echo("\n" + "=" * 70)
    click.echo("        KHỞI TẠO CƠ SỞ DỮ LIỆU SQLITE THÀNH CÔNG")
    click.echo("=" * 70)
    click.echo(f" - Đường dẫn CSDL     : {db_manager.db_path}")
    click.echo(f" - Số Run đã đồng bộ  : {synced_count}")
    click.echo("=" * 70 + "\n")
    logger.success("Hoàn tất khởi tạo CSDL và đồng bộ dữ liệu vào SQLite!")


@cli.command(name="recalculate-scores")
def recalculate_scores_cli():
    """Tính lại điểm tổng hợp cho toàn bộ các Run trong CSDL theo trọng số mới nhất trong config/scoring.yaml."""
    from storage.db_manager import DBManager
    from scoring.calculator import ScoreCalculator

    logger.info(">>> Đang nạp trọng số mới từ config/scoring.yaml và tính lại điểm số...")
    db_manager = DBManager()
    calculator = ScoreCalculator()
    weights = calculator.load_weights()

    click.echo("\n" + "=" * 70)
    click.echo("     ÁP DỤNG TRỌNG SỐ MỚI TỪ CONFIG/SCORING.YAML")
    click.echo("=" * 70)
    for k, v in weights.items():
        click.echo(f" - {k:<25}: {v:.2f} ({v*100:>5.1f}%)")
    click.echo("=" * 70)

    updated_count = calculator.recalculate_all_scores(db_manager)
    click.echo(f"\n[OK] Đã cập nhật lại điểm tổng hợp cho {updated_count} lượt chạy trong SQLite và file báo cáo.")
    logger.success("Hoàn tất tính lại điểm động thành công!")


@cli.command(name="inspect-run")
@click.option("--run-id", "-r", required=True, help="Mã định danh lần chạy cần truy vết (ví dụ: run_001)")
def inspect_run_cli(run_id: str):
    """Truy vấn từ SQLite và in ra hồ sơ truy vết đầy đủ từ A-Z của run_id."""
    from storage.db_manager import DBManager

    logger.info(f">>> Đang truy vết hồ sơ dữ liệu của [{run_id}] từ CSDL SQLite...")
    db_manager = DBManager()
    try:
        trace = db_manager.get_run_full_trace(run_id)
    except KeyError as e:
        logger.error(str(e))
        sys.exit(1)

    run = trace["run"]
    proj = trace["project"]
    screenshots = trace["screenshots"]
    metrics = trace["automatic_metrics"]
    score = trace["score"]

    click.echo("\n" + "=" * 80)
    click.echo(f"          HỒ SƠ TRUY VẾT THÍ NGHIỆM TỪ SQLITE: [{run_id}]")
    click.echo("=" * 80)
    click.echo(" [THÔNG TIN LƯỢT CHẠY (RUN)]:")
    click.echo(f"  - IDE / Agent           : {run['ide_name'].upper()} / {run['agent_name']}")
    click.echo(f"  - Mã bài tập (Task ID)  : {run['task_id']}")
    click.echo(f"  - Điều kiện thực nghiệm : {run['prompt_condition']}")
    click.echo(f"  - Trạng thái / Thời gian: {run['status']} (thực thi trong {run['duration_seconds']}s)")
    click.echo(f"  - Mã ẩn danh định tính  : {run['blind_code']}")
    click.echo(f"  - Thời điểm bắt đầu     : {run['start_time']}")

    click.echo("\n" + "-" * 80)
    click.echo(" [SẢN PHẨM SINH RA (PROJECT)]:")
    click.echo(f"  - Thư mục lưu trữ       : {proj.get('folder_path')}")
    click.echo(f"  - File HTML chính       : {proj.get('entry_html_file')}")
    click.echo(f"  - Tổng số dòng mã (LOC) : {proj.get('total_lines_of_code')} LOC ({proj.get('file_count')} files)")
    click.echo(f"  - Mã băm SHA-256        : {proj.get('sha256_hash')}")
    click.echo(f"  - Danh sách files       : {', '.join(proj.get('files', []))}")

    click.echo("\n" + "-" * 80)
    click.echo(" [ẢNH CHỤP GIAO DIỆN (SCREENSHOTS & VIEWPORT AUDIT)]:")
    for sc in screenshots:
        audit = sc.get("layout_audit", {})
        layout_issues = audit.get("layout_issues", [])
        overflow_str = "CÓ TRÀN NGANG!" if sc["has_horizontal_overflow"] else "Không tràn"
        click.echo(f"  * Viewport {sc['viewport_width']}px: {overflow_str} | Số lỗi bố cục: {len(layout_issues)}")
        click.echo(f"    Ảnh: {sc['image_path']}")

    click.echo("\n" + "-" * 80)
    click.echo(" [ĐIỂM SỐ 6 TIÊU CHÍ TỰ ĐỘNG (AUTOMATIC METRICS)]:")
    metric_names_vi = {
        "html_validity": "HTML Validity",
        "accessibility": "Accessibility",
        "responsive": "Responsive Design",
        "design_similarity": "Design Similarity",
        "code_quality": "Code Quality",
        "runtime_cleanliness": "Runtime Cleanliness",
    }
    for m_key, m_info in metrics.items():
        name_label = metric_names_vi.get(m_key, m_key)
        issues_cnt = len(m_info.get("issues", []))
        click.echo(f"  * {name_label:<22}: {m_info['raw_score']:>5.1f}/100 ({issues_cnt} cảnh báo)")

    click.echo("\n" + "=" * 80)
    click.echo(f"  TỔNG ĐIỂM CHUẨN HÓA TRONG SQLITE: {score.get('weighted_total_score', 0.0):.2f} / 100.00")
    click.echo(f"  Cập nhật lúc: {score.get('updated_at')}")
    click.echo("=" * 80 + "\n")
    logger.success(f"Truy vết thành công dữ liệu lượt chạy [{run_id}] từ CSDL SQLite!")


@cli.command(name="dashboard")
@click.option("--port", "-p", default=8501, type=int, help="Cổng chạy Streamlit Web Server (mặc định: 8501)")
def dashboard_cli(port: int):
    """Khởi động Giao diện Web Dashboard (Streamlit) của WebGenBench trên trình duyệt."""
    import subprocess
    app_path = BASE_DIR / "dashboard" / "app.py"
    logger.info(f">>> Đang khởi động Web Dashboard tại: http://localhost:{port} ...")
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(port)]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        logger.info("Đã dừng Web Dashboard.")


if __name__ == "__main__":
    cli()
