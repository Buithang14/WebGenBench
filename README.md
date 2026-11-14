# 🌐 WebGenBench (Web Generation Benchmark)

> **Hệ thống tự động hóa đánh giá năng lực sinh mã giao diện Web của các công cụ IDE tích hợp AI Coding Agent (Cursor, Windsurf, VS Code Copilot).**  
> Dự án phục vụ Nghiên cứu Khoa học (NCKH), kết hợp giữa Tự động hóa Desktop GUI, Thị giác máy tính (Computer Vision), Kết xuất trình duyệt không đầu (Headless Browser), Cơ sở dữ liệu quan hệ và Giao diện Web Dashboard chuẩn **Google Material Design 3**.

---

## 📌 1. Giới Thiệu & Mô Hình Thực Nghiệm

**WebGenBench** cung cấp một khung thực nghiệm khép kín, khách quan và có thể tái lập 100% để đo lường, so sánh hiệu quả sinh mã HTML/CSS/JS giữa các AI Coding IDEs hàng đầu.

### Ma trận thí nghiệm chuẩn (144 lượt chạy):
$$\text{Quy mô} = 3 \text{ IDEs} \times 8 \text{ Tasks} \times 2 \text{ Điều kiện Prompt} \times 3 \text{ Lần lặp lại} = 144 \text{ Runs}$$

* **3 IDEs / Agents mục tiêu:** Cursor (Claude 3.5 Sonnet / GPT-4o), Windsurf (Cascade), VS Code (GitHub Copilot Chat).
* **8 Tasks benchmark:** Đa dạng từ Landing Page, Dashboard, E-commerce Card, Authentication Form, Portfolio đến Multi-step Wizard.
* **2 Điều kiện Prompt:**
  1. `text_only`: Chỉ cung cấp văn bản đặc tả yêu cầu chức năng và giao diện.
  2. `text_image`: Cung cấp văn bản đặc tả kèm ảnh thiết kế mẫu (Design Ground Truth).
* **3 Lần lặp lại (Repetitions):** Kiểm soát tính ngẫu nhiên (temperature) của mô hình sinh mã.

---

## 🛠️ 2. Toàn Bộ Công Nghệ Cốt Lõi (Tech Stack)

Dự án được xây dựng hoàn toàn bằng **Python 3.12** với kiến trúc phân tầng chuyên sâu:

| Phân hệ hệ thống | Công nghệ / Thư viện chính | Vai trò & Mục đích sử dụng |
| :--- | :--- | :--- |
| **GUI Automation** | `pywinauto`, `pywin32`, `pyautogui`, `pyperclip` | Tương tác cấp OS với cửa sổ IDE, quản lý handle, mô phỏng phím tắt (`Ctrl+L`, `Ctrl+I`), tiêm prompt qua Clipboard không mất ký tự. |
| **Phát hiện hoàn tất** | `watchdog`, `Pillow`, `OpenCV` | Lắng nghe sự kiện hệ thống tệp thời gian thực và đo độ lệch điểm ảnh (RMS diff) trạng thái nút Generate / Stop để phát hiện thời điểm AI dừng sinh mã. |
| **Kết xuất & Runtime** | `playwright` (Chromium Engine), `http.server` | Trình duyệt không đầu kết xuất đa kích thước (375px, 768px, 1440px), máy chủ HTTP tĩnh cục bộ chặn lỗi CORS, bắt lỗi console JS runtime và đo đạc tràn ngang DOM. |
| **Thị giác máy tính (CV)** | `scikit-image` (`ssim`), `opencv-python` (`cv2`) | Đo chỉ số tương đồng cấu trúc thị giác (SSIM) giữa ảnh sinh ra và ảnh mẫu; thuật toán phát hiện biên (Contours) khoanh vùng ROI và so sánh biểu đồ màu sắc (Color Histogram). |
| **Chuẩn hóa Web & a11y** | `beautifulsoup4`, `html5lib` | Phân tích cú pháp DOM, kiểm tra tính hợp chuẩn W3C (DOCTYPE, semantics HTML5) và tiêu chuẩn tiếp cận Web WCAG 2.1 (ARIA, label, alt text). |
| **Cơ sở dữ liệu ORM** | `SQLAlchemy 2.0`, `SQLite 3` | Quản lý quan hệ thực thể chặt chẽ 7 bảng (`experiments`, `runs`, `projects`, `screenshots`, `metrics`, `scores`, `human_ratings`) trong CSDL nhúng `webgenbench.db`. |
| **Thống kê & Đánh giá định tính** | `numpy` | Thống kê mô tả (Mean, Std Dev) và tính toán độ đồng thuận chuyên gia (Inter-Rater Reliability): Exact Agreement %, Within-1 Agreement, Cohen's & Fleiss' Kappa. |
| **Web Dashboard** | `streamlit` (≥ 1.33.0), `plotly`, `pandas` | Giao diện bảng điều khiển tương tác, biểu đồ Radar Chart 6 tiêu chí, Boxplot phân bố thời gian/LOC và xuất dữ liệu báo cáo. |
| **Hệ thống Thiết kế UI/UX** | **Google Material Design 3 (Material You)** | Bảng màu Google Blue M3 Baseline, Tonal Elevation (Level 1–4), Shape Corner Tokens, Surface Containers, phông chữ Plus Jakarta Sans & Roboto Flex. |
| **Biểu tượng Icon** | **Google Material Symbols (SVG)** | Bộ icon vector SVG native nhúng trực tiếp, độ sắc nét cao, độc lập 100% không phụ thuộc internet hay webfont. |
| **Bố cục Responsive** | **Fluid Responsive Engine (% / vw / clamp)** | Tự động thích ứng đa màn hình (Laptop 1366px, MacBook 1440px, Full HD 1920px, 2K 2560px), khóa thanh kéo dãn sidebar chống lệch layout. |
| **Hạ tầng, CLI & Test** | `click`, `pydantic` (v2), `pyyaml`, `loguru`, `pytest` | Khung CLI dòng lệnh, kiểm soát kiểu dữ liệu nghiêm ngặt, cấu hình khai báo YAML, ghi log đa cấp và bộ kiểm thử tự động 28 ca test. |

---

## 📊 3. Bộ 6 Tiêu Chí Đánh Giá Định Lượng (Scoring Engine)

Hệ thống chấm điểm tự động chuẩn hóa thang điểm từ **0.0 đến 100.0** với trọng số linh hoạt (lưu tại `config/scoring.yaml` và CSDL):

```text
Điểm Tổng Hợp (Weighted Score) = Σ (Điểm Tiêu Chí × Trọng Số)
```

1. **HTML Validity (Trọng số mặc định: 15%):** Đánh giá tính hợp chuẩn W3C, khai báo DOCTYPE, ngôn ngữ thẻ `<html>`, cấu trúc thẻ cân bằng và tính chuẩn mực ngữ nghĩa (Semantic HTML5: `<header>`, `<main>`, `<nav>`, `<footer>`).
2. **Accessibility (WCAG 2.1 a11y) (Trọng số: 20%):** Kiểm tra khả năng tiếp cận người dùng khuyết tật: nhãn `label` cho form input, thuộc tính `alt` cho ảnh, tiêu đề phân cấp logic (`h1`-`h6`), độ tương phản màu sắc và các thuộc tính hỗ trợ ARIA.
3. **Responsive Design (Trọng số: 20%):** Kiểm tra độ co giãn trên 3 kích thước màn hình (Mobile 375px, Tablet 768px, Desktop 1440px), phát hiện lỗi tràn ngang thanh cuộn (`scrollWidth > clientWidth`) và thẻ meta viewport.
4. **Design Similarity (Trọng số: 25%):** Thuật toán thị giác máy tính kết hợp:
   - **SSIM (Structural Similarity Index):** Đo độ tương đồng về cấu trúc và hình khối.
   - **Color Histogram Matching:** Đo mức độ tương đồng bảng màu thực tế.
   - **Card/ROI Bounding Box:** Tự động cắt tách và so sánh vùng nội dung chính.
5. **Code Quality (Trọng số: 10%):** Đánh giá tổ chức mã nguồn, tách bạch CSS/JS, độ dài dòng code hợp lý (LOC), tỷ lệ chú thích và tái sử dụng class.
6. **Runtime Cleanliness (Trọng số: 10%):** Đo độ sạch runtime khi trang hoạt động: không phát sinh ngoại lệ JavaScript (`window.onerror`), không có lỗi Console Error (`console.error`), không có tài nguyên 404/500 bị hỏng (Failed Network Requests).

---

## 🧑‍⚖️ 4. Phân Hệ Đánh Giá Định Tính (Blind Human Evaluation)

Bên cạnh 6 tiêu chí định lượng tự động, WebGenBench tích hợp phân hệ **Chấm điểm mù (Blind Evaluation)** phục vụ kiểm chứng khoa học:
* **Mã hóa ẩn danh:** Mỗi lượt chạy được cấp một mã ngẫu nhiên (ví dụ `Sample_001`), ẩn hoàn toàn thông tin IDE, Agent và Model nhằm loại bỏ định kiến đánh giá của con người.
* **4 khía cạnh định tính (Thang điểm 1 - 5):**
  1. *Bố cục thị giác (Layout & Balance)*
  2. *Thẩm mỹ & Màu sắc (Aesthetics & Typography)*
  3. *Trải nghiệm đọc (Readability & Visual Hierarchy)*
  4. *Độ hoàn thiện tổng thể (Completeness & Production-readiness)*
* **Độ tin cậy & Hệ số đồng thuận (Inter-Rater Reliability):**
  - Tỷ lệ đồng thuận tuyệt đối (*Exact Agreement %*)
  - Tỷ lệ đồng thuận sai lệch ≤ 1 điểm (*Within-1 Point Agreement %*)
  - Hệ số tương quan nội bộ **Cohen's Kappa** và **Fleiss' Kappa**.

---

## 💻 5. Hướng Dẫn Cài Đặt & Khởi Động

### Yêu cầu hệ thống:
* **Hệ điều hành:** Windows 10 / 11 (hỗ trợ đầy đủ GUI Automation cho Cursor / Windsurf / VS Code).
* **Python:** Phiên bản 3.12+ (khuyến nghị Python 3.12.x).

### Các bước cài đặt:

```bash
# 1. Di chuyển vào thư mục dự án
cd d:\WebGenBench

# 2. Tạo môi trường ảo (nếu chưa có)
python -m venv .venv

# 3. Kích hoạt môi trường ảo
.venv\Scripts\activate

# 4. Cài đặt các gói phụ thuộc
pip install -r requirements.txt

# 5. Cài đặt trình duyệt Chromium cho Playwright
playwright install chromium
```

---

## 🚀 6. Vận Hành Giao Diện Web (Streamlit Dashboard)

Khởi động giao diện Web Dashboard trực quan theo chuẩn Google Material Design 3:

```bash
# Cách 1: Khởi động qua lệnh CLI WebGenBench
python main.py dashboard

# Cách 2: Khởi động trực tiếp qua Streamlit
streamlit run dashboard/app.py
```

Truy cập ứng dụng tại: **`http://localhost:8501`**

### Sơ đồ điều hướng các trang (URL RESTful tiếng Anh chuẩn & 5 Khu Vực Chức Năng):
| URL Path | Tên Trang | Khu Vực Thiết Kế (Giao diện.docx) | Chức Năng Chính |
| :--- | :--- | :--- | :--- |
| **`/`** | **Tổng Quan (Overview)** | Trung tâm điều khiển | KPI Cards tổng quan, tiến độ thực nghiệm 144 runs, bảng xếp hạng IDE và biểu đồ Radar 6 tiêu chí M3. |
| **`/tasks`** | **Quản Lý Bài Tập (Tasks)** | **Khu vực 1: Quản lý Bài tập & Nạp Prompt** | Danh sách 8 bài tập (T01 → T08), nút `[+ Thêm / Tạo bài tập mới]`, trình soạn thảo Prompt kèm `[Lưu Prompt]`, quản lý danh sách yêu cầu UI & Technical, tải ảnh thiết kế mẫu kèm live preview. |
| **`/experiments`** | **Điều Khiển Thí Nghiệm** | **Khu vực 2: Điều khiển Chạy Thí nghiệm** | Chế độ chạy đơn (Single Run) với `[▶ Bắt đầu Chạy & Chấm điểm]` và `[🔄 Chấm điểm lại]`; Chế độ chiến dịch 144 runs với `[🚀 Khởi chạy Chiến dịch 144 Runs]`, `[⏸ Tạm dừng / Chạy tiếp]`, thanh tiến độ chi tiết và Live Log viewer. |
| **`/inspect`** | **Chi Tiết Lần Chạy (Inspect)** | **Khu vực 4: Soi Chi tiết Kết quả** | Bộ chọn lọc Run, so sánh trực quan Side-by-side (Ground Truth vs 3 Viewports 1440px, 768px, 375px), thẻ điểm 6 tiêu chí, bảng danh sách lỗi phát hiện chi tiết, Code Viewer (HTML/CSS/JS) với syntax highlighting. |
| **`/rating`** | **Chấm Điểm Ẩn Danh (Rating)** | **Khu vực 5: Chấm điểm Định tính Ẩn danh** | Chấm điểm mù ẩn danh tên IDE (Sample #001), 4 nhóm tiêu chí (1-5 sao: Bố cục, Thẩm mỹ, Trải nghiệm đọc, Hoàn thiện), khung nhận xét và nút `[Lưu Điểm Chấm]`. |
| **`/analytics`** | **Phân Tích & So Sánh** | **Khu vực 5: Phân tích & Xuất Báo cáo** | Biểu đồ so sánh 3 IDEs (Radar, Bar chart, Boxplot), so sánh Text-only vs Text+Image, đo độ đồng thuận Fleiss' Kappa, nút `[📥 Xuất file CSV đưa vào khóa luận]`. |
| **`/weights`** | **Cấu Hình Trọng Số & Hệ Thống** | **Khu vực 3: Cấu hình Trọng số & Hệ thống** | 6 thanh trượt trọng số (HTML 15%, a11y 20%, Responsive 20%, Similarity 25%, Code 10%, Runtime 10%) kèm `[Lưu & Tính lại toàn bộ điểm]`; Quản lý đường dẫn thực thi .exe của 3 IDEs, model name và tham số timeout/cooldown. |
| **`/export`** | **Trung Tâm Xuất Báo Cáo** | **Khu vực 5: Phân tích & Xuất Báo cáo** | Xuất dữ liệu nghiên cứu khoa học: tải bảng dữ liệu CSV, JSON metadata, báo cáo tóm tắt Markdown và hồ sơ chi tiết từng run. |

---

## ⌨️ 7. Vận Hành Qua Giao Diện Dòng Lệnh (CLI)

WebGenBench hỗ trợ hệ thống lệnh CLI mạnh mẽ phục vụ tự động hóa không cần mở giao diện Web:

```bash
# Kiểm tra môi trường và cấu hình hệ thống
python main.py check-config

# Hiển thị thông tin chi tiết bài tập T01
python main.py show-task -t T01

# Kiểm thử tương tác GUI với Cursor (Smoke Test)
python main.py test-ide -i cursor -a smoke-test

# Chạy tự động 1 lượt benchmark (Vertical Slice)
python main.py run-once -i cursor -t T01 -c text_only

# Kết xuất Playwright và chụp ảnh 3 viewports cho một Run
python main.py render -r run_001

# Chấm điểm tự động 6 tiêu chí cho một Run
python main.py evaluate -r run_001

# Khởi tạo CSDL SQLite và đồng bộ dữ liệu từ outputs/
python main.py init-db

# Truy vết toàn bộ hồ sơ thí nghiệm từ SQLite
python main.py inspect-run -r run_001

# Tính lại điểm tổng hợp cho toàn bộ Runs theo trọng số mới
python main.py recalculate-scores
```

---

## 🧪 8. Kiểm Thử Tự Động (Automated Testing)

Dự án có bộ kiểm thử tự động toàn diện bảo vệ toàn bộ logic thu thập, tính điểm, cơ sở dữ liệu và giao diện:

```bash
# Chạy toàn bộ 28 ca kiểm thử
.venv\Scripts\python.exe -m pytest -v
```

*Kết quả kiểm thử chuẩn: 27 passed, 1 skipped (giả lập cửa sổ OS Cursor) trong ~90 giây.*

---

## 📁 9. Cấu Trúc Thư Mục Dự Án Mới Nhất

```text
WebGenBench/
├── automation/                 # Phân hệ Tự động hóa Desktop GUI
│   ├── base_adapter.py         # Lớp cơ sở định nghĩa Adapter cho các IDE
│   ├── clipboard_helper.py     # Hỗ trợ dán prompt an toàn qua Clipboard OS
│   ├── completion_detector.py  # Bộ phát hiện hoàn tất (Watchdog + RMS Diff)
│   ├── cursor/                 # Adapter điều khiển IDE Cursor
│   ├── tools/                  # Công cụ trợ giúp kiểm tra UI Automation (inspect controls)
│   ├── vscode/                 # Adapter điều khiển VS Code Copilot
│   └── windsurf/               # Adapter điều khiển Windsurf
├── collection/                 # Thu thập mã nguồn sinh ra, mã băm SHA-256, đếm LOC
├── config/                     # Quản lý cấu hình khai báo YAML & Pydantic Schemas
│   ├── loader.py               # Trình nạp cấu hình hệ thống
│   ├── logger.py               # Cấu hình Loguru logging
│   ├── scoring.yaml            # Trọng số 6 tiêu chí chấm điểm
│   ├── settings.yaml           # Cấu hình timing, viewports, đường dẫn
│   └── tools.yaml              # Cấu hình danh mục 3 IDE và AI Agents
├── dashboard/                  # Ứng dụng Web Dashboard (Streamlit chuẩn M3)
│   ├── app.py                  # Trang chủ Streamlit & Bộ định tuyến (/overview)
│   ├── icons.py                # Kho biểu tượng vector SVG (Google Material Symbols)
│   ├── theme.py                # Google Material Design 3 Tokens, CSS & Responsive Engine
│   └── pages/                  # Các trang chức năng (URL RESTful tiếng Anh & 5 Khu vực):
│       ├── 0_tasks.py          # URL: /tasks (Khu vực 1: Quản lý Bài tập & Nạp Prompt T01-T08)
│       ├── 1_experiments.py    # URL: /experiments (Khu vực 2: Điều khiển thí nghiệm & Ma trận 144 runs)
│       ├── 2_inspect.py        # URL: /inspect (Khu vực 4: Chi tiết lần chạy, Side-by-side & Code Viewer)
│       ├── 3_rating.py         # URL: /rating (Khu vực 5: Chấm điểm ẩn danh 4 nhóm & 1-5 sao)
│       ├── 4_analytics.py      # URL: /analytics (Khu vực 5: Phân tích so sánh đa chiều & Fleiss' Kappa)
│       ├── 5_weights.py        # URL: /weights (Khu vực 3: Cấu hình trọng số 6 tiêu chí & Hệ thống IDE)
│       └── 6_export.py         # URL: /export (Khu vực 5: Trung tâm xuất dữ liệu CSV khóa luận/JSON/MD)
├── designs/                    # Ảnh thiết kế chuẩn (Design Ground Truth) cho 8 Tasks
├── docs/                       # Tài liệu nghiên cứu & Tài nguyên hình ảnh minh họa
│   └── screenshots/            # Ảnh chụp giao diện các trang và kiểm chứng responsive
├── experiment/                 # Quản lý thực thi thực nghiệm
│   ├── batch_runner.py         # Quản lý ma trận 144 lượt chạy & Hàng đợi
│   ├── single_runner.py        # Điều phối trọn vẹn 1 lượt chạy (Vertical Slice)
│   └── task_loader.py          # Nạp đề bài, metadata và ảnh thiết kế
├── logs/                       # Thư mục chứa tệp nhật ký thực thi (log files)
├── metrics/                    # Bộ máy đo lường 6 tiêu chí định lượng tự động
│   ├── accessibility.py        # Tiêu chuẩn tiếp cận WCAG 2.1 (a11y)
│   ├── code_quality.py         # Chất lượng mã nguồn, LOC, tỷ lệ CSS/JS
│   ├── design_similarity.py    # SSIM, Contour ROI, Color Histogram Matching
│   ├── html_validity.py        # Tính hợp chuẩn W3C & Cú pháp ngữ nghĩa HTML5
│   ├── responsive.py           # Kiểm tra co giãn 3 viewports & Lỗi tràn ngang
│   └── runtime_cleanliness.py  # Bắt ngoại lệ JavaScript runtime & Lỗi mạng 404
├── outputs/                    # Kho lưu trữ artifacts từng lượt chạy (code, screenshots, reports)
├── qualitative/                # Phân hệ chấm điểm định tính (Human Evaluation)
│   ├── agreement.py            # Tính toán thống kê & Độ đồng thuận (Fleiss' Kappa, Exact %)
│   └── blind_mapper.py         # Quản lý mã hóa ẩn danh hai chiều (Sample_001 <-> run_id)
├── rendering/                  # Bộ kết xuất trình duyệt Playwright Chromium & HTTP Server
├── scoring/                    # Bộ tính toán và chuẩn hóa điểm số tổng hợp động
├── storage/                    # Cơ sở dữ liệu SQLite & Mô hình SQLAlchemy ORM
│   ├── db_manager.py           # Quản lý phiên CSDL và truy vết thí nghiệm A-Z
│   ├── models.py               # Lược đồ quan hệ 7 bảng dữ liệu
│   └── webgenbench.db          # Tệp CSDL SQLite cục bộ
├── tasks/                      # Tập dữ liệu 8 bài tập benchmark (prompt, spec, HTML mẫu)
├── tests/                      # Bộ kiểm thử tự động pytest (28 ca kiểm thử)
├── workspace/                  # Thư mục làm việc tạm thời cho các AI IDEs
├── main.py                     # Điểm vào chính của ứng dụng dòng lệnh (CLI Entry Point)
├── README.md                   # Tài liệu hướng dẫn dự án chi tiết
└── requirements.txt            # Danh sách thư viện phụ thuộc Python
```

---

## 📜 10. Giấy Phép & Tác Quyền

Dự án được xây dựng phục vụ mục đích Nghiên cứu Khoa học (Scientific Research & Benchmarking). Mọi dữ liệu thực nghiệm và mã nguồn đều tuân thủ các quy định về tính minh bạch, đạo đức nghiên cứu và khả năng tái lập kết quả khoa học.
