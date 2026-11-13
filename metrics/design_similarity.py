import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Any, List
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from metrics.base_metric import BaseMetric, MetricResult
from config.logger import logger


class DesignSimilarityMetric(BaseMetric):
    """Đánh giá độ tương đồng giao diện thị giác giữa ảnh kết xuất và ảnh thiết kế chuẩn."""

    STANDARD_SIZE = (1440, 900)
    CARD_STANDARDIZED_SIZE = (500, 600)

    def __init__(self):
        super().__init__(name="design_similarity")

    def _load_and_preprocess(self, image_path: Path) -> np.ndarray:
        """Đọc và chuẩn hóa ảnh về kích thước chuẩn (1440x900) dưới định dạng BGR."""
        pil_img = Image.open(image_path).convert("RGB")
        pil_img = pil_img.resize(self.STANDARD_SIZE, Image.Resampling.LANCZOS)
        rgb_arr = np.array(pil_img)
        bgr_arr = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)
        return bgr_arr

    @staticmethod
    def _find_card_roi(image_bgr: np.ndarray) -> tuple[int, int, int, int]:
        """Tự động định vị và khoanh vùng khối Card/Form chính (Region of Interest - ROI)."""
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        corners = [gray[10, 10], gray[10, -10], gray[-10, 10], gray[-10, -10]]
        bg_val = int(np.median(corners))
        diff = np.abs(gray.astype(np.int32) - bg_val)
        mask = (diff > 8).astype(np.uint8) * 255
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0, 0, image_bgr.shape[1], image_bgr.shape[0]
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        pad = 15
        H, W = image_bgr.shape[:2]
        return max(0, x - pad), max(0, y - pad), min(W - x, w + 2 * pad), min(H - y, h + 2 * pad)

    def evaluate(self, run_dir: Path, task_meta: Optional[Any] = None) -> MetricResult:
        screenshots_dir = run_dir / "screenshots"
        actual_shot = screenshots_dir / "viewport_1440px.png"

        # Tìm ảnh thiết kế chuẩn
        task_id = "T01"
        if task_meta and hasattr(task_meta, "task_id"):
            task_id = task_meta.task_id
        elif task_meta and isinstance(task_meta, dict):
            task_id = task_meta.get("task_id", "T01")

        base_dir = Path(__file__).resolve().parent.parent
        reference_shot = base_dir / "designs" / f"{task_id}_reference.png"

        issues: List[str] = []

        if not actual_shot.exists():
            return MetricResult(
                metric_name=self.name,
                score=0.0,
                raw_value={"error": "Missing viewport_1440px.png"},
                issues=["Chưa có ảnh chụp viewport_1440px.png để so sánh."],
            )

        if not reference_shot.exists():
            issues.append(f"Không tìm thấy ảnh thiết kế mẫu tại {reference_shot.name}, sử dụng điểm cơ bản.")
            return MetricResult(
                metric_name=self.name,
                score=75.0,
                raw_value={"warning": "Missing reference image"},
                issues=issues,
            )

        try:
            # 1. Nạp và chuẩn hóa 2 ảnh full-page (1440x900)
            img_act = self._load_and_preprocess(actual_shot)
            img_ref = self._load_and_preprocess(reference_shot)

            # 2. Đánh giá toàn khung hình (Full-frame) - Trọng số 30%
            gray_act = cv2.cvtColor(img_act, cv2.COLOR_BGR2GRAY)
            gray_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY)

            ssim_full, _ = ssim(gray_ref, gray_act, full=True)
            full_ssim_score = max(0.0, float(ssim_full)) * 100.0

            hist_act_full = cv2.calcHist([img_act], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist_ref_full = cv2.calcHist([img_ref], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            cv2.normalize(hist_act_full, hist_act_full)
            cv2.normalize(hist_ref_full, hist_ref_full)
            full_hist_score = max(0.0, float(cv2.compareHist(hist_ref_full, hist_act_full, cv2.HISTCMP_CORREL))) * 100.0

            full_frame_score = (0.50 * full_ssim_score) + (0.50 * full_hist_score)

            # 3. Đánh giá vùng giao diện chính (Card ROI Cropping) - Trọng số 70%
            xr, yr, wr, hr = self._find_card_roi(img_ref)
            xa, ya, wa, ha = self._find_card_roi(img_act)

            roi_ref = img_ref[yr:yr+hr, xr:xr+wr]
            roi_act = img_act[ya:ya+ha, xa:xa+wa]

            # Đưa ROI về cùng kích thước chuẩn để so sánh cấu trúc chi tiết
            roi_ref_resized = cv2.resize(roi_ref, self.CARD_STANDARDIZED_SIZE, interpolation=cv2.INTER_LANCZOS4)
            roi_act_resized = cv2.resize(roi_act, self.CARD_STANDARDIZED_SIZE, interpolation=cv2.INTER_LANCZOS4)

            gray_roi_ref = cv2.cvtColor(roi_ref_resized, cv2.COLOR_BGR2GRAY)
            gray_roi_act = cv2.cvtColor(roi_act_resized, cv2.COLOR_BGR2GRAY)

            ssim_roi, _ = ssim(gray_roi_ref, gray_roi_act, full=True)
            roi_ssim_score = max(0.0, float(ssim_roi)) * 100.0

            # So sánh biểu đồ màu sắc trong Card ROI
            hist_roi_act = cv2.calcHist([roi_act_resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist_roi_ref = cv2.calcHist([roi_ref_resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            cv2.normalize(hist_roi_act, hist_roi_act)
            cv2.normalize(hist_roi_ref, hist_roi_ref)
            roi_hist_score = max(0.0, float(cv2.compareHist(hist_roi_ref, hist_roi_act, cv2.HISTCMP_CORREL))) * 100.0

            # So sánh tỷ lệ khung hình (Aspect Ratio) của khối Card
            ar_ref = wr / float(max(hr, 1))
            ar_act = wa / float(max(ha, 1))
            ar_similarity = max(0.0, 1.0 - abs(ar_ref - ar_act) / ar_ref) * 100.0

            # So sánh đường viền và chi tiết typography trong Card
            edges_roi_act = cv2.Canny(gray_roi_act, 100, 200)
            edges_roi_ref = cv2.Canny(gray_roi_ref, 100, 200)
            act_den = np.sum(edges_roi_act > 0) / float(edges_roi_act.size)
            ref_den = np.sum(edges_roi_ref > 0) / float(edges_roi_ref.size)
            edge_sim = max(0.0, 1.0 - abs(act_den - ref_den) / (ref_den + 1e-5)) * 100.0

            roi_composite_score = (
                0.40 * roi_ssim_score +
                0.30 * roi_hist_score +
                0.15 * ar_similarity +
                0.15 * edge_sim
            )

            # 4. Điểm tổng hợp: 30% Full-frame + 70% Card ROI
            final_score = (0.30 * full_frame_score) + (0.70 * roi_composite_score)
            final_score = min(max(round(final_score, 2), 0.0), 100.0)

            if roi_ssim_score < 75.0:
                issues.append(f"Cấu trúc nội dung chi tiết trong Card có sự khác biệt (ROI SSIM: {roi_ssim_score:.1f}%).")
            if ar_similarity < 85.0:
                issues.append(f"Tỷ lệ khung hình khối Card chưa tương đồng với thiết kế mẫu (Tỷ lệ: {ar_similarity:.1f}%).")

            return MetricResult(
                metric_name=self.name,
                score=final_score,
                raw_value={
                    "full_frame_score": round(full_frame_score, 2),
                    "roi_ssim": round(roi_ssim_score, 2),
                    "roi_hist": round(roi_hist_score, 2),
                    "roi_aspect_ratio_sim": round(ar_similarity, 2),
                    "roi_composite_score": round(roi_composite_score, 2),
                    "card_bbox_detected": {"x": int(xa), "y": int(ya), "w": int(wa), "h": int(ha)},
                },
                issues=issues,
            )

        except Exception as e:
            logger.error(f"Lỗi khi tính DesignSimilarityMetric: {e}")
            return MetricResult(
                metric_name=self.name,
                score=50.0,
                raw_value={"error": str(e)},
                issues=[f"Lỗi phân tích hình ảnh: {e}"],
            )

