import streamlit as st
import yaml
from pathlib import Path
import sys
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from experiment.task_loader import list_available_tasks, load_task, find_task_directory
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
    page_title="Quản Lý Bài Tập & Prompt - WebGenBench (M3)",
    page_icon=":material/task:",
    layout="wide"
)
apply_m3_theme()

m3_header(
    title="Quản Lý Bài Tập & Nạp Prompt",
    subtitle="Soạn thảo prompt chuẩn, chỉnh sửa yêu cầu UI/Kỹ thuật và cập nhật ảnh thiết kế tham chiếu (Design Ground Truth)",
    icon_name="task"
)

# 1. Nạp danh sách bài tập hiện có
tasks_list = list_available_tasks()
if not tasks_list:
    m3_banner("Chưa tìm thấy bài tập nào trong thư mục tasks/.", banner_type="warning", icon_name="warning")
    st.stop()

# Layout hàng trên: Bộ chọn bài tập + Nút tạo mới
top_col1, top_col2 = st.columns([3, 1])

with top_col1:
    selected_task_id = st.selectbox(
        "Chọn Bài Tập Cần Quản Lý (T01 → T08):",
        options=tasks_list,
        index=0,
        format_func=lambda tid: f"[{tid}] {load_task(tid).meta.name} - {load_task(tid).meta.title_vi}"
    )

with top_col2:
    st.write("")
    st.write("")
    show_create_modal = st.button("+ Thêm / Tạo bài tập mới", type="primary", icon=":material/add_circle:", use_container_width=True)

# Khung tạo bài tập mới (Expander)
if show_create_modal or st.session_state.get("is_creating_task", False):
    st.session_state["is_creating_task"] = True
    with st.expander("✨ Biểu mẫu tạo bài tập Benchmark mới", expanded=True):
        c1, c2, c3 = st.columns([1, 1.5, 2])
        with c1:
            new_id = st.text_input("Mã bài tập (Task ID):", placeholder="Ví dụ: T09")
        with c2:
            new_name = st.text_input("Tên tiếng Anh (Name):", placeholder="Ví dụ: Contact Form")
        with c3:
            new_title_vi = st.text_input("Tiêu đề tiếng Việt:", placeholder="Ví dụ: Biểu mẫu liên hệ hiện đại")
        
        new_prompt = st.text_area(
            "Nội dung Prompt chuẩn ban đầu:",
            placeholder="Hãy viết mô tả yêu cầu chi tiết cho AI Agent sinh mã...",
            height=140
        )
        
        btn_c1, btn_c2 = st.columns([1, 4])
        with btn_c1:
            if st.button("Lưu Bài Tập Mới", type="primary", icon=":material/save:"):
                if not new_id or not new_name or not new_title_vi:
                    st.error("Vui lòng điền đầy đủ Mã, Tên và Tiêu đề bài tập!")
                else:
                    safe_slug = new_name.lower().replace(" ", "_").replace("-", "_")
                    new_task_dir = ROOT_DIR / "tasks" / f"{new_id}_{safe_slug}"
                    new_task_dir.mkdir(parents=True, exist_ok=True)
                    
                    # File prompt.txt
                    prompt_file = new_task_dir / "prompt.txt"
                    prompt_file.write_text(new_prompt.strip() or f"Tạo giao diện {new_title_vi}", encoding="utf-8")
                    
                    # File task_meta.yaml
                    meta_content = {
                        "task_id": new_id,
                        "name": new_name,
                        "title_vi": new_title_vi,
                        "prompt_file": f"tasks/{new_task_dir.name}/prompt.txt",
                        "reference_image": f"designs/{new_id}_reference.png",
                        "expected_files": ["index.html", "style.css", "script.js"],
                        "ui_requirements": ["Giao diện căn giữa màn hình.", "Responsive trên 3 viewports."],
                        "technical_requirements": ["Sử dụng HTML5 ngữ nghĩa.", "CSS thuần và JS thuần."],
                    }
                    meta_file = new_task_dir / "task_meta.yaml"
                    with open(meta_file, "w", encoding="utf-8") as f:
                        yaml.dump(meta_content, f, allow_unicode=True, default_flow_style=False)
                    
                    st.session_state["is_creating_task"] = False
                    st.success(f"Đã tạo thành công bài tập [{new_id}] {new_name}!")
                    st.rerun()
        with btn_c2:
            if st.button("Hủy bỏ", icon=":material/close:"):
                st.session_state["is_creating_task"] = False
                st.rerun()

# 2. Nạp dữ liệu của bài tập đang chọn
try:
    task_data = load_task(selected_task_id)
except Exception as e:
    m3_banner(f"Lỗi khi đọc bài tập '{selected_task_id}': {e}", banner_type="error", icon_name="error")
    st.stop()

task_dir = find_task_directory(selected_task_id)
meta_file_path = task_dir / "task_meta.yaml"
prompt_file_path = task_data.prompt_path

# Thẻ thông tin nhanh về bài tập
st.markdown(f"""
<div style="background:var(--md-sys-color-surface-container); border-radius:16px; padding:14px 20px; border:1px solid var(--md-sys-color-outline-variant); margin-top:10px; margin-bottom:18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; box-shadow: var(--md-elevation-1);">
    <div style="display:flex; align-items:center; gap:12px;">
        <div style="background:#0B57D0; color:white; border-radius:12px; padding:8px 12px; font-weight:800; font-size:1.1rem;">
            {task_data.meta.task_id}
        </div>
        <div>
            <div style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">{task_data.meta.name}</div>
            <div style="font-size:0.88rem; color:#444746;">{task_data.meta.title_vi}</div>
        </div>
    </div>
    <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
        <span class="m3-chip m3-chip-primary">{get_svg("code", size=14, color="#041E49")} {', '.join(task_data.meta.expected_files)}</span>
        <span class="m3-chip m3-chip-secondary">{get_svg("task", size=14, color="#001D35")} {len(task_data.meta.ui_requirements)} Yêu cầu UI</span>
        <span class="m3-chip m3-chip-tertiary">{get_svg("tune", size=14, color="#001F24")} {len(task_data.meta.technical_requirements)} Yêu cầu Kỹ thuật</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 3. Phân chia 2 cột làm việc: Cột trái (Soạn Prompt & Yêu cầu) | Cột phải (Ảnh thiết kế mẫu)
col_editor, col_image = st.columns([1.5, 1.2], gap="large")

with col_editor:
    # A. Ô soạn thảo Prompt lớn
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        {get_svg("code", size=20, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.05rem; color:#1F1F1F;">1. Ô Soạn Thảo Prompt Chuẩn (Câu Lệnh)</span>
    </div>
    """, unsafe_allow_html=True)
    
    edited_prompt = st.text_area(
        label="Nội dung Prompt gửi vào các AI Agent (Cursor, Windsurf, VS Code):",
        value=task_data.prompt_text,
        height=260,
        help="Nội dung câu lệnh đặc tả sẽ được tiêm trực tiếp vào cửa sổ chat của IDE khi chạy Benchmark."
    )
    
    save_prompt_col, _ = st.columns([1, 2])
    with save_prompt_col:
        if st.button("Lưu Prompt", type="primary", icon=":material/save:", use_container_width=True):
            try:
                prompt_file_path.write_text(edited_prompt.strip(), encoding="utf-8")
                st.success("Đã lưu nội dung Prompt thành công!")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi lưu prompt: {e}")
    
    st.divider()

    # B. Danh sách Yêu cầu Giao diện & Kỹ thuật
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        {get_svg("task", size=20, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.05rem; color:#1F1F1F;">2. Danh Sách Yêu Cầu Giao Diện & Kỹ Thuật</span>
    </div>
    """, unsafe_allow_html=True)
    
    req_tab_ui, req_tab_tech = st.tabs(["Yêu Cầu Giao Diện (UI)", "Yêu Cầu Kỹ Thuật (Technical)"])
    
    with req_tab_ui:
        st.caption("Nhập mỗi yêu cầu giao diện trên một dòng riêng biệt:")
        ui_text_value = "\n".join(task_data.meta.ui_requirements)
        edited_ui_reqs = st.text_area(
            "Danh sách yêu cầu UI:",
            value=ui_text_value,
            height=160,
            label_visibility="collapsed"
        )
    
    with req_tab_tech:
        st.caption("Nhập mỗi yêu cầu kỹ thuật trên một dòng riêng biệt:")
        tech_text_value = "\n".join(task_data.meta.technical_requirements)
        edited_tech_reqs = st.text_area(
            "Danh sách yêu cầu kỹ thuật:",
            value=tech_text_value,
            height=160,
            label_visibility="collapsed"
        )
        
    save_reqs_col, _ = st.columns([1, 2])
    with save_reqs_col:
        if st.button("Lưu Danh Sách Yêu Cầu", icon=":material/done_all:", use_container_width=True):
            try:
                with open(meta_file_path, "r", encoding="utf-8") as f:
                    curr_meta = yaml.safe_load(f)
                
                new_ui_list = [line.strip() for line in edited_ui_reqs.split("\n") if line.strip()]
                new_tech_list = [line.strip() for line in edited_tech_reqs.split("\n") if line.strip()]
                
                curr_meta["ui_requirements"] = new_ui_list
                curr_meta["technical_requirements"] = new_tech_list
                
                with open(meta_file_path, "w", encoding="utf-8") as f:
                    yaml.dump(curr_meta, f, allow_unicode=True, default_flow_style=False)
                
                st.success("Đã cập nhật danh sách yêu cầu thành công!")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi lưu yêu cầu: {e}")

with col_image:
    # C. Khung nạp Ảnh thiết kế mẫu (Design Reference)
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        {get_svg("desktop", size=20, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.05rem; color:#1F1F1F;">3. Khung Nạp Ảnh Thiết Kế Mẫu (Design Reference)</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="font-size:0.88rem; color:#444746; margin-bottom:10px;">
        Đường dẫn ảnh mẫu hiện tại: <code>{task_data.meta.reference_image}</code>
    </div>
    """, unsafe_allow_html=True)
    
    # Hiển thị ảnh hiện tại
    ref_path = task_data.reference_image_path
    if ref_path.exists():
        try:
            with Image.open(ref_path) as img:
                w, h = img.size
                file_kb = ref_path.stat().st_size / 1024
            st.image(str(ref_path), caption=f"Ảnh mẫu chuẩn: {w}×{h} px ({file_kb:.1f} KB)", use_container_width=True)
        except Exception as e:
            st.warning(f"Không thể đọc file ảnh mẫu: {e}")
    else:
        m3_banner("Chưa có ảnh thiết kế mẫu cho bài tập này.", banner_type="warning", icon_name="warning")
        
    # Nút upload ảnh PNG mới
    uploaded_file = st.file_uploader(
        "Tải ảnh thiết kế mẫu mới lên (Upload PNG / JPG):",
        type=["png", "jpg", "jpeg"],
        help="Chọn bức ảnh thiết kế chuẩn độ phân giải cao (khuyến nghị 1440x900) từ máy tính của bạn."
    )
    
    if uploaded_file is not None:
        try:
            preview_img = Image.open(uploaded_file)
            st.image(preview_img, caption=f"Xem trước ảnh vừa tải lên: {preview_img.size[0]}×{preview_img.size[1]} px", use_container_width=True)
            
            if st.button("Xác nhận & Lưu ảnh làm Design Reference", type="primary", icon=":material/upload_file:", use_container_width=True):
                target_design_path = ROOT_DIR / task_data.meta.reference_image
                target_design_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Lưu đè ảnh mới
                preview_img.save(target_design_path)
                
                # Sao chép vào thư mục task nếu cần
                local_task_ref = task_dir / "reference.png"
                preview_img.save(local_task_ref)
                
                st.success(f"Đã lưu ảnh thiết kế mẫu thành công vào {target_design_path}!")
                st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi xử lý file ảnh: {e}")

