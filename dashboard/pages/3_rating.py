import streamlit as st
import datetime
from pathlib import Path
import sys
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from storage.db_manager import DBManager
from storage.models import HumanRating, Run
from experiment.task_loader import load_task
from qualitative.blind_mapper import BlindMapper
from qualitative.agreement import compute_inter_rater_agreement, calculate_sample_consensus
from dashboard.theme import (
    apply_m3_theme,
    m3_header,
    m3_card,
    m3_elevated_card,
    m3_banner,
    m3_chip
)
from dashboard.icons import get_svg

st.set_page_config(page_title="Chấm Điểm Ẩn Danh - WebGenBench (M3)", page_icon=":material/gavel:", layout="wide")
apply_m3_theme()

m3_header(
    title="Phòng Chấm Điểm Ẩn Danh (Blind Qualitative Rating)",
    subtitle="Màn hình 3 theo Kế hoạch: Dành cho chuyên gia chấm điểm độc lập không bị thiên kiến thương hiệu IDE & Phân tích hệ số đồng thuận (Inter-Rater Reliability)",
    icon_name="gavel"
)

db = DBManager()
db.init_db()
mapper = BlindMapper(db_manager=db)
mapper.ensure_blind_codes_assigned()

tab_rating, tab_agreement = st.tabs([
    "1. Phiếu Chấm Điểm Ẩn Danh (Rating)",
    "2. Độ Đồng Thuận (Inter-Rater)"
])

# ==================== TAB 1: PHIẾU CHẤM ĐIỂM ====================
with tab_rating:
    samples = mapper.get_blind_sample_list()
    if not samples:
        m3_banner("Chưa có mẫu thí nghiệm nào trong hệ thống.", banner_type="warning", icon_name="warning")
        st.stop()

    selected_sample = st.selectbox(
        "Chọn Mẫu Giao Diện Cần Đánh Giá (Mã Ẩn Danh):",
        options=samples,
        format_func=lambda s: f"Mẫu: {s['blind_code']} (Nhiệm vụ: {s['task_id']})"
    )

    run_id = selected_sample["run_id"]
    blind_code = selected_sample["blind_code"]

    try:
        trace_data = db.get_run_full_trace(run_id)
    except Exception as e:
        m3_banner(f"Lỗi nạp dữ liệu mẫu: {e}", banner_type="error", icon_name="error")
        st.stop()

    screenshots = trace_data["screenshots"]

    col_view, col_form = st.columns([1.2, 1.0])

    with col_view:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
            {get_svg("visibility", size=22, color="#0B57D0")}
            <span style="font-weight:700; font-size:1.1rem; color:#1F1F1F;">Mẫu Giao Diện: <code>{blind_code}</code></span>
        </div>
        """, unsafe_allow_html=True)
        
        viewport_map = {sc["viewport_width"]: sc for sc in screenshots}
        vp_choice = st.radio("Kích thước quan sát:", [1440, 768, 375], format_func=lambda x: f"{x}px ({'Desktop' if x==1440 else ('Tablet' if x==768 else 'Mobile')})", horizontal=True)
        
        sc = viewport_map.get(vp_choice)
        if sc:
            img_p = ROOT_DIR / sc["image_path"]
            if img_p.exists():
                st.image(str(img_p), caption=f"Ảnh kết xuất thực tế ({vp_choice}px)", use_column_width=True)
            else:
                m3_banner("Chưa có ảnh kết xuất.", banner_type="info", icon_name="info")
        else:
            m3_banner("Chưa có ảnh kết xuất.", banner_type="info", icon_name="info")

        with st.expander("Xem Ảnh Thiết Kế Gốc Để Đối Chiếu"):
            try:
                task_data = load_task(selected_sample["task_id"])
                ref_path = ROOT_DIR / task_data.meta.reference_image
                if ref_path.exists():
                    st.image(str(ref_path), use_column_width=True)
            except Exception:
                pass

    with col_form:
        st.markdown(f"""
        <div style="background:var(--md-sys-color-surface-container); border-radius:16px; padding:18px 24px; border:1px solid var(--md-sys-color-outline-variant); margin-bottom:18px; display:flex; align-items:center; gap:10px; box-shadow: var(--md-elevation-1);">
            {get_svg("star", size=22, color="#0B57D0")}
            <span style="font-weight:700; color:#0B57D0; font-size:1.15rem;">Phiếu Đánh Giá Chuyên Gia (Thang 1 - 5)</span>
        </div>
        """, unsafe_allow_html=True)
        
        rater_id = st.text_input("Tên / Mã chuyên gia đánh giá (Rater ID):", placeholder="Ví dụ: Rater_1, Rater_2, ChuyenGia_A...")
        
        st.markdown("##### 1. Bố cục (Layout)")
        st.caption("Khung card căn giữa, khoảng cách padding, cấu trúc tỷ lệ chuẩn so với yêu cầu đề bài.")
        score_layout = st.radio("Điểm Bố cục (1: Kém → 5: Hoàn hảo):", [1, 2, 3, 4, 5], index=3, horizontal=True, key="sc_layout")

        st.markdown("##### 2. Thẩm mỹ (Aesthetics)")
        st.caption("Độ hài hòa màu sắc, độ tương phản chữ, font chữ, bóng đổ card và hiệu ứng giao diện.")
        score_aesthetics = st.radio("Điểm Thẩm mỹ (1: Thô sơ → 5: Rất đẹp):", [1, 2, 3, 4, 5], index=3, horizontal=True, key="sc_aesthetics")

        st.markdown("##### 3. Dễ đọc (Readability)")
        st.caption("Font chữ dễ đọc, phân cấp thông tin rõ ràng, nhãn label và ô nhập trực quan.")
        score_readability = st.radio("Điểm Dễ đọc (1: Khó đọc → 5: Rất trực quan):", [1, 2, 3, 4, 5], index=3, horizontal=True, key="sc_readability")

        st.markdown("##### 4. Đầy đủ (Completeness)")
        st.caption("Đầy đủ các trường dữ liệu, icon ẩn/hiện, remember me, forgot password, nút submit.")
        score_completeness = st.radio("Điểm Hoàn thiện (1: Thiếu nhiều → 5: Đầy đủ 100%):", [1, 2, 3, 4, 5], index=4, horizontal=True, key="sc_completeness")

        comment = st.text_area("Ghi chú / Nhận xét chuyên môn (Tùy chọn):", placeholder="Ghi chú về chi tiết giao diện, lỗi hiển thị hoặc điểm sáng...")

        avg_score = round((score_layout + score_aesthetics + score_readability + score_completeness) / 4.0, 2)
        st.metric("Điểm Trung Bình Đánh Giá", f"{avg_score} / 5.0")

        if st.button("Lưu Điểm Chấm", type="primary", icon=":material/save:", use_container_width=True):
            if not rater_id.strip():
                st.error("Vui lòng nhập Tên/Mã chuyên gia đánh giá!")
                st.stop()

            with db.get_session() as session:
                rating_obj = HumanRating(
                    run_id=run_id,
                    blind_code=blind_code,
                    rater_id=rater_id.strip(),
                    layout_score=score_layout,
                    aesthetics_score=score_aesthetics,
                    readability_score=score_readability,
                    completeness_score=score_completeness,
                    average_rating=avg_score,
                    comment=comment.strip() if comment.strip() else None,
                    rated_at=datetime.datetime.now(),
                )
                session.add(rating_obj)
                session.commit()

            st.success(f"Đã lưu thành công đánh giá của chuyên gia {rater_id} cho mẫu {blind_code}!")
            st.rerun()

    st.divider()
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        {get_svg("history", size=20, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.1rem; color:#1F1F1F;">Lịch Sử Đánh Giá Của Các Chuyên Gia Cho Mẫu [{blind_code}]</span>
    </div>
    """, unsafe_allow_html=True)

    existing_ratings = trace_data.get("human_ratings", [])
    if existing_ratings:
        for r in existing_ratings:
            st.markdown(f"""
            <div style="background:var(--md-sys-color-surface-container); border-radius:14px; padding:16px 22px; margin-bottom:12px; border:1px solid var(--md-sys-color-outline-variant); box-shadow: var(--md-elevation-1);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><b>Chuyên gia:</b> <code>{r['rater_id']}</code></div>
                    {m3_chip(f"TB: {r['average_rating']}/5.0", chip_type="primary", icon_name="star")}
                </div>
                <div style="font-size:0.88rem; color:#444746; margin-top:6px;">
                    Bố cục: <b>{r['layout_score']}</b> &nbsp;|&nbsp; Thẩm mỹ: <b>{r['aesthetics_score']}</b> &nbsp;|&nbsp; Trải nghiệm: <b>{r['readability_score']}</b> &nbsp;|&nbsp; Hoàn thiện: <b>{r['completeness_score']}</b>
                </div>
                <div style="font-size:0.92rem; color:#1F1F1F; margin-top:8px; font-style:italic;">"{r.get('comment') or 'Không có bình luận'}"</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        m3_banner("Mẫu này chưa có đánh giá nào từ chuyên gia.", banner_type="info", icon_name="info")

# ==================== TAB 2: ĐỘ ĐỒNG THUẬN ====================
with tab_agreement:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
        {get_svg("analytics", size=22, color="#0B57D0")}
        <span style="font-weight:700; font-size:1.15rem; color:#1F1F1F;">Hệ Số Đồng Thuận Giữa Các Chuyên Gia (Inter-Rater Reliability)</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Thống kê mức độ tương thích và độ tin cậy giữa các người chấm độc lập phục vụ báo cáo khoa học (Cohen's Kappa / Agreement %)")

    agreement_data = compute_inter_rater_agreement(db_manager=db)

    if agreement_data.get("status") == "NO_DATA":
        m3_banner("Chưa có dữ liệu đánh giá nào để tính toán độ đồng thuận.", banner_type="info", icon_name="info")
    elif agreement_data.get("status") == "INSUFFICIENT_RATERS":
        m3_banner(agreement_data.get("message", ""), banner_type="warning", icon_name="warning")
        m3_banner("Để tính được chỉ số đồng thuận, cần có ít nhất 1 mẫu được chấm bởi từ 2 chuyên gia khác nhau (ví dụ: Rater_1 và Rater_2 cùng chấm Sample_001).", banner_type="info", icon_name="info")
    else:
        col_ag1, col_ag2, col_ag3, col_ag4 = st.columns(4)
        with col_ag1:
            m3_card(value=f"{agreement_data['exact_agreement_pct']}%", label="Đồng thuận tuyệt đối", secondary="Chấm cùng một mức điểm", badge="Exact", badge_type="primary", icon_name="check_circle")
        with col_ag2:
            m3_card(value=f"{agreement_data['within_one_point_pct']}%", label="Đồng thuận (±1 Điểm)", secondary="Chênh lệch tối đa 1 điểm", badge="Within-1", badge_type="success", icon_name="check_circle")
        with col_ag3:
            m3_card(value=f"{agreement_data['mean_score_difference']}", label="Độ lệch điểm TB", secondary="Khoảng cách chấm trung bình", badge="Mean Diff", badge_type="neutral", icon_name="tune")
        with col_ag4:
            m3_card(value=f"{agreement_data['kappa_reliability_estimate']:.2f}", label="Cohen's Kappa", secondary="Hệ số tin cậy đo lường", badge="Kappa", badge_type="primary", icon_name="shield_check")

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-top:20px; margin-bottom:8px;">
            {get_svg("table_chart", size=20, color="#0B57D0")}
            <span style="font-weight:700; font-size:1.05rem; color:#1F1F1F;">Tổng Hợp Điểm Đồng Thuận Theo Từng Mẫu (Consensus Summary)</span>
        </div>
        """, unsafe_allow_html=True)
        
        with db.get_session() as session:
            all_ratings = session.query(HumanRating).all()
            grouped: dict = {}
            for r in all_ratings:
                key = r.blind_code or r.run_id
                grouped.setdefault(key, []).append({
                    "layout_score": r.layout_score,
                    "aesthetics_score": r.aesthetics_score,
                    "readability_score": r.readability_score,
                    "completeness_score": r.completeness_score,
                    "average_rating": r.average_rating,
                })

        consensus_rows = []
        for s_code, r_list in grouped.items():
            c_res = calculate_sample_consensus(r_list)
            consensus_rows.append({
                "Mã Mẫu": s_code,
                "Số Người Chấm": c_res["rater_count"],
                "Điểm TB": f"{c_res['overall_avg']:.2f}",
                "Độ Lệch Chuẩn (SD)": f"±{c_res['overall_std']:.2f}",
                "Bố Cục (Mean±SD)": f"{c_res['layout_stats']['mean']:.1f} ± {c_res['layout_stats']['std']:.1f}",
                "Thẩm Mỹ (Mean±SD)": f"{c_res['aesthetics_stats']['mean']:.1f} ± {c_res['aesthetics_stats']['std']:.1f}",
                "Dễ Đọc (Mean±SD)": f"{c_res['readability_stats']['mean']:.1f} ± {c_res['readability_stats']['std']:.1f}",
                "Hoàn Thiện (Mean±SD)": f"{c_res['completeness_stats']['mean']:.1f} ± {c_res['completeness_stats']['std']:.1f}",
            })

        st.dataframe(pd.DataFrame(consensus_rows), use_container_width=True, hide_index=True)
