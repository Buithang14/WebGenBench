import json
import time
import socket
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.sync_api import sync_playwright

from config.logger import logger
from config.loader import load_settings


class QuietHTTPHandler(SimpleHTTPRequestHandler):
    """Handler phục vụ tệp tĩnh, tắt log request ra stdout để giữ log sạch."""
    def log_message(self, format, *args):
        pass


class BrowserRenderer:
    """Module kết xuất trình duyệt Playwright, bắt lỗi runtime và đo đạc DOM."""

    VIEWPORT_CONFIGS = {
        375: {"width": 375, "height": 812, "name": "mobile"},
        768: {"width": 768, "height": 1024, "name": "tablet"},
        1440: {"width": 1440, "height": 900, "name": "desktop"},
    }

    def __init__(self, base_outputs_dir: Optional[Path] = None):
        self.base_outputs_dir = Path(base_outputs_dir) if base_outputs_dir else Path("outputs")
        self.settings = load_settings()

    @staticmethod
    def _find_free_port() -> int:
        """Tìm một cổng TCP khả dụng trên localhost."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    def _start_local_server(self, project_dir: Path) -> tuple[ThreadingHTTPServer, int, threading.Thread]:
        """Khởi chạy máy chủ HTTP tĩnh cục bộ phục vụ các tệp của project."""
        port = self._find_free_port()
        handler_factory = partial(QuietHTTPHandler, directory=str(project_dir))
        server = ThreadingHTTPServer(("127.0.0.1", port), handler_factory)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        logger.info(f"Đã kích hoạt máy chủ HTTP tĩnh tại http://127.0.0.1:{port} (trỏ tới {project_dir})")
        return server, port, thread

    def render_run(self, run_id: str) -> Dict[str, Any]:
        """Thực hiện kết xuất Chromium cho một Run cụ thể."""
        run_dir = (self.base_outputs_dir / run_id).resolve()
        project_dir = run_dir / "project"
        screenshots_dir = run_dir / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        if not project_dir.exists():
            raise FileNotFoundError(f"Thư mục project không tồn tại: {project_dir}")

        # Tìm entry html
        entry_html = "index.html"
        if not (project_dir / "index.html").exists():
            html_files = list(project_dir.glob("*.html"))
            if html_files:
                entry_html = html_files[0].name
            else:
                raise FileNotFoundError(f"Không tìm thấy tệp HTML nào trong: {project_dir}")

        server, port, server_thread = self._start_local_server(project_dir)
        base_url = f"http://127.0.0.1:{port}/{entry_html}"

        console_errors: List[str] = []
        console_warnings: List[str] = []
        page_errors: List[str] = []
        failed_requests: List[Dict[str, str]] = []

        dom_metrics: Dict[str, Any] = {}
        screenshots_paths: Dict[str, str] = {}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                # Gắn event listeners
                def on_console(msg):
                    if msg.type == "error":
                        console_errors.append(msg.text)
                        logger.warning(f"[Browser Console Error] {msg.text}")
                    elif msg.type == "warning":
                        console_warnings.append(msg.text)

                def on_page_error(exc):
                    page_errors.append(str(exc))
                    logger.error(f"[Browser PageError] {exc}")

                def on_request_failed(req):
                    failed_requests.append({
                        "url": req.url,
                        "failure": req.failure or "unknown error",
                    })
                    logger.warning(f"[Browser RequestFailed] {req.url} - {req.failure}")

                page.on("console", on_console)
                page.on("pageerror", on_page_error)
                page.on("requestfailed", on_request_failed)

                # Duyệt qua các viewport cấu hình
                configured_viewports = self.settings.viewports if self.settings else [375, 768, 1440]

                for vp_width in configured_viewports:
                    cfg = self.VIEWPORT_CONFIGS.get(vp_width, {"width": vp_width, "height": 900, "name": f"{vp_width}px"})
                    w = cfg["width"]
                    h = cfg["height"]
                    logger.info(f"Đang render viewport: {w}x{h} ({cfg.get('name')})...")

                    page.set_viewport_size({"width": w, "height": h})
                    page.goto(base_url, wait_until="networkidle", timeout=15000)
                    # Chờ ngắn 300ms cho các hiệu ứng CSS transition / layout settle
                    time.sleep(0.3)

                    # Chụp ảnh screenshot
                    shot_path = screenshots_dir / f"viewport_{w}px.png"
                    page.screenshot(path=str(shot_path), full_page=False)
                    screenshots_paths[str(w)] = shot_path.as_posix()

                    # Đo đạc thông số DOM qua JavaScript trong trang
                    dom_eval = page.evaluate("""() => {
                        const body = document.body || document.documentElement;
                        const docEl = document.documentElement;
                        
                        const scrollWidth = Math.max(docEl.scrollWidth, body.scrollWidth);
                        const clientWidth = docEl.clientWidth;
                        const has_horizontal_overflow = scrollWidth > clientWidth + 2;

                        const element_issues = [];
                        const layout_issues = [];

                        // 1. Kiểm tra hiển thị nhiều icon đồng thời trong 1 nút/control
                        document.querySelectorAll('button, .toggle-password, [role="button"]').forEach((btn, idx) => {
                            const icons = btn.querySelectorAll('svg, img');
                            const visibleIcons = [];
                            icons.forEach(ic => {
                                const s = window.getComputedStyle(ic);
                                const r = ic.getBoundingClientRect();
                                if (s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0' && r.width > 0 && r.height > 0) {
                                    visibleIcons.push({
                                        tag: ic.tagName,
                                        className: ic.className ? (ic.className.baseVal || ic.className) : '',
                                        w: Math.round(r.width),
                                        h: Math.round(r.height),
                                        top: Math.round(r.top)
                                    });
                                }
                            });
                            if (visibleIcons.length > 1) {
                                layout_issues.push({
                                    type: 'MULTIPLE_VISIBLE_ICONS',
                                    target: `${btn.tagName}.${btn.className || idx}`,
                                    message: `Nút điều khiển hiển thị đồng thời ${visibleIcons.length} icon (ví dụ: cả 2 icon mắt ẩn/hiện cùng hiện gây biến dạng giao diện)`,
                                    details: visibleIcons
                                });
                            }
                        });

                        // 2. Kiểm tra lệch tâm dọc (Vertical Misalignment) giữa nút trong input và ô input
                        document.querySelectorAll('.password-wrap, .field, form > div').forEach(wrap => {
                            const inp = wrap.querySelector('input');
                            const btn = wrap.querySelector('button, .toggle-password');
                            if (inp && btn) {
                                const rInp = inp.getBoundingClientRect();
                                const rBtn = btn.getBoundingClientRect();
                                if (rInp.height > 0 && rBtn.height > 0) {
                                    const inpCenterY = rInp.top + rInp.height / 2;
                                    const btnCenterY = rBtn.top + rBtn.height / 2;
                                    const offset = Math.abs(inpCenterY - btnCenterY);
                                    if (offset > 6) {
                                        layout_issues.push({
                                            type: 'BUTTON_VERTICAL_MISALIGNMENT',
                                            target: `${btn.tagName}.${btn.className}`,
                                            message: `Nút con bên trong ô nhập bị lệch tâm dọc ${offset.toFixed(1)}px (> 6px) so với tâm ô input`,
                                            details: { inpCenterY, btnCenterY, offset }
                                        });
                                    }
                                }
                            }
                        });

                        // 3. Kiểm tra đè/chồng lấn tọa độ giữa các phần tử anh em (Sibling Overlap)
                        document.querySelectorAll('form, .card, main > section').forEach(container => {
                            const children = Array.from(container.children).filter(el => {
                                const s = window.getComputedStyle(el);
                                const r = el.getBoundingClientRect();
                                return s.display !== 'none' && s.position !== 'absolute' && s.position !== 'fixed' && r.height > 0;
                            });
                            for (let i = 0; i < children.length - 1; i++) {
                                const r1 = children[i].getBoundingClientRect();
                                const r2 = children[i + 1].getBoundingClientRect();
                                if (r1.bottom > r2.top + 4 && r2.bottom > r1.top + 4) {
                                    layout_issues.push({
                                        type: 'SIBLING_OVERLAP',
                                        target: `${children[i].tagName} và ${children[i+1].tagName}`,
                                        message: `Phần tử bị chồng lấn tọa độ lên phần tử kế tiếp (${Math.round(r1.bottom - r2.top)}px)`,
                                        details: { el1: children[i].className, el2: children[i+1].className }
                                    });
                                }
                            }
                        });

                        // 4. Kiểm tra kích thước vùng chạm tương tác (Touch Target Size >= 24x24px)
                        document.querySelectorAll('button, a, input:not([type="hidden"])').forEach(el => {
                            const r = el.getBoundingClientRect();
                            if (r.width > 0 && r.height > 0 && (r.width < 24 || r.height < 24)) {
                                layout_issues.push({
                                    type: 'TOUCH_TARGET_TOO_SMALL',
                                    target: el.tagName + (el.id ? '#' + el.id : (el.className ? '.' + el.className : '')),
                                    message: `Vùng bấm tương tác quá nhỏ (${Math.round(r.width)}x${Math.round(r.height)}px < 24x24px chuẩn WCAG)`,
                                    details: { w: r.width, h: r.height }
                                });
                            }
                        });

                        // 5. Kiểm tra độ tương phản màu sắc văn bản cơ bản
                        function parseRgb(colorStr) {
                            const match = colorStr.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                            if (!match) return null;
                            return [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
                        }
                        function relLuminance([r, g, b]) {
                            const a = [r, g, b].map(v => {
                                v /= 255;
                                return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
                            });
                            return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
                        }
                        const contrast_issues = [];
                        document.querySelectorAll('h1, h2, p, label, button, a').forEach(el => {
                            const text = el.innerText ? el.innerText.trim() : '';
                            if (!text) return;
                            const s = window.getComputedStyle(el);
                            const fg = parseRgb(s.color);
                            let cur = el;
                            let bg = null;
                            while (cur && cur !== document) {
                                const bgStr = window.getComputedStyle(cur).backgroundColor;
                                const parsed = parseRgb(bgStr);
                                if (parsed && !(parsed[0] === 0 && parsed[1] === 0 && parsed[2] === 0 && bgStr.includes('0)'))) {
                                    bg = parsed;
                                    break;
                                }
                                cur = cur.parentElement;
                            }
                            if (!bg) bg = [255, 255, 255];
                            if (fg && bg) {
                                const l1 = relLuminance(fg);
                                const l2 = relLuminance(bg);
                                const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
                                if (ratio < 4.5 && ratio > 1.0) {
                                    contrast_issues.push({
                                        text: text.slice(0, 30),
                                        ratio: Math.round(ratio * 100) / 100,
                                        tag: el.tagName
                                    });
                                }
                            }
                        });

                        // 6. Lấy bounding box của khối Card chính
                        const mainCard = document.querySelector('.card, .login-card, section.card, .form-container, form');
                        let main_card_bbox = null;
                        if (mainCard) {
                            const r = mainCard.getBoundingClientRect();
                            main_card_bbox = {
                                left: Math.round(r.left),
                                top: Math.round(r.top),
                                width: Math.round(r.width),
                                height: Math.round(r.height)
                            };
                        }

                        return {
                            scrollWidth: scrollWidth,
                            clientWidth: clientWidth,
                            has_horizontal_overflow: has_horizontal_overflow,
                            element_issues: element_issues,
                            layout_issues: layout_issues,
                            contrast_issues: contrast_issues.slice(0, 5),
                            main_card_bbox: main_card_bbox,
                        };
                    }""")

                    dom_metrics[str(w)] = dom_eval

                browser.close()

        finally:
            server.shutdown()
            server.server_close()
            logger.info("Đã đóng trình duyệt Playwright và dừng máy chủ HTTP nội bộ.")

        report = {
            "run_id": run_id,
            "entry_html": entry_html,
            "server_url": base_url,
            "screenshots": screenshots_paths,
            "dom_metrics": dom_metrics,
            "runtime_errors": {
                "console_errors": console_errors,
                "console_warnings": console_warnings,
                "page_errors": page_errors,
                "failed_requests": failed_requests,
            },
        }

        report_file = run_dir / "render_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.success(f"Đã lưu báo cáo render tại: {report_file}")
        return report

