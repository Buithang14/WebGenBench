from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import yaml

tasks_data = [
    {
        'id': 'T02',
        'dir': 'T02_registration',
        'name': 'Registration Form',
        'title_vi': 'Biểu mẫu đăng ký thành viên đa trường',
        'expected_files': ['index.html', 'style.css', 'script.js'],
        'ui_reqs': [
            'Form đăng ký căn giữa màn hình với tiêu đề và mô tả ngắn gọn.',
            'Các trường thông tin: Họ và tên, Email, Mật khẩu, Xác nhận mật khẩu, và Số điện thoại.',
            'Nút toggle ẩn/hiện cho cả 2 ô mật khẩu.',
            'Checkbox đồng ý điều khoản dịch vụ và chính sách bảo mật.',
            'Nút Đăng ký tài khoản nổi bật với trạng thái loading khi submit.',
            'Responsive mượt mà trên Mobile (375px), Tablet (768px) và Desktop (1440px).'
        ],
        'tech_reqs': [
            'Sử dụng HTML5 ngữ nghĩa chuẩn W3C (<form>, <input>, <label>, <button>).',
            'Kiểm tra tính hợp lệ dữ liệu bằng JavaScript thuần: định dạng email regex, mật khẩu tối thiểu 8 ký tự và khớp xác nhận.',
            'Toàn bộ CSS viết trong style.css, không dùng thư viện ngoài.',
            'Toàn bộ tương tác trong script.js.'
        ],
        'prompt': """Hãy xây dựng giao diện web cho 'Biểu mẫu đăng ký thành viên' (Registration Form) hiện đại và chuyên nghiệp.
Yêu cầu cụ thể:
1. Giao diện dạng thẻ (Card) căn giữa màn hình cả chiều ngang và dọc với nền sáng trang nhã.
2. Bao gồm các trường: Họ và tên (Full Name), Email, Mật khẩu (Password), Xác nhận mật khẩu (Confirm Password), Số điện thoại (Phone).
3. Có chức năng ẩn/hiện mật khẩu bằng nút bấm hoặc icon mắt.
4. Checkbox đồng ý với Điều khoản dịch vụ và Chính sách quyền riêng tư.
5. Nút 'Đăng Ký Ngay' (Register) phong cách hiện đại, hiệu ứng hover rõ ràng.
6. Xác thực form bằng JavaScript: báo lỗi khi bỏ trống, email sai định dạng, mật khẩu < 8 ký tự hoặc xác nhận mật khẩu không khớp.
7. Đảm bảo Responsive chuẩn cho điện thoại (375px), tablet (768px) và desktop (1440px).
8. Tạo đúng 3 file index.html, style.css, script.js ngay tại thư mục gốc của project, không dùng thư viện ngoài."""
    },
    {
        'id': 'T03',
        'dir': 'T03_dashboard',
        'name': 'Analytics Dashboard',
        'title_vi': 'Bảng điều khiển phân tích số liệu KPI',
        'expected_files': ['index.html', 'style.css', 'script.js'],
        'ui_reqs': [
            'Bố cục dạng Dashboard với Sidebar thu gọn và khu vực nội dung chính.',
            'Thanh Header trên cùng có thanh tìm kiếm, thông báo và ảnh đại diện người dùng.',
            'Hàng thẻ KPI Metrics (4 thẻ): Doanh thu, Người dùng mới, Tỷ lệ chuyển đổi, Đơn hàng.',
            'Khu vực biểu đồ hoặc bảng số liệu thống kê hoạt động gần đây.',
            'Thiết kế responsive thích ứng tốt từ màn hình di động đến màn hình rộng.'
        ],
        'tech_reqs': [
            'Sử dụng cấu trúc CSS Grid và Flexbox hiện đại.',
            'Các thẻ số liệu có màu sắc phân biệt và icon trực quan.',
            'Tương tác JavaScript để lọc hoặc cập nhật số liệu mẫu.',
            'Chỉ sử dụng 3 file index.html, style.css, script.js tại thư mục gốc.'
        ],
        'prompt': """Hãy xây dựng giao diện web cho 'Bảng điều khiển số liệu KPI' (Analytics Dashboard) hiện đại.
Yêu cầu:
1. Bố cục gồm Thanh điều hướng bên trái (Sidebar) và Khu vực làm việc chính (Main Content).
2. Header chứa ô tìm kiếm (Search bar) và thông tin tài khoản người dùng.
3. 4 thẻ chỉ số KPI: Doanh thu ($45,230, +12%), Khách hàng mới (1,240, +5%), Tỷ lệ hoàn thành (89.4%), Đơn hàng đang xử lý (342).
4. Bảng danh sách giao dịch gần nhất với các cột: Mã đơn, Khách hàng, Trạng thái (Thành công/Đang xử lý/Hủy), Số tiền.
5. Thiết kế sạch đẹp, độ tương phản cao, chuẩn responsive trên Mobile, Tablet và Desktop.
6. Tạo đúng 3 file index.html, style.css, script.js tại thư mục gốc, không dùng framework ngoài."""
    },
    {
        'id': 'T04',
        'dir': 'T04_product_grid',
        'name': 'E-commerce Product Grid',
        'title_vi': 'Lưới danh sách sản phẩm thương mại điện tử',
        'expected_files': ['index.html', 'style.css', 'script.js'],
        'ui_reqs': [
            'Lưới hiển thị danh sách sản phẩm (3 đến 4 cột trên Desktop, 2 cột trên Tablet, 1 cột trên Mobile).',
            'Mỗi thẻ sản phẩm gồm: Ảnh sản phẩm, Tên, Đánh giá sao, Giá bán và Giá khuyến mãi, Nút Thêm vào giỏ hàng.',
            'Thanh lọc theo danh mục sản phẩm và ô sắp xếp theo giá.',
            'Huy hiệu giảm giá (Sale badge) nổi bật trên góc ảnh.'
        ],
        'tech_reqs': [
            'Sử dụng CSS Grid với auto-fit / minmax để co giãn tự nhiên.',
            'JavaScript xử lý tăng số lượng giỏ hàng khi bấm Thêm vào giỏ.',
            'Chuẩn HTML5 ngữ nghĩa và a11y alt text cho ảnh.',
            'Tạo đúng 3 file index.html, style.css, script.js tại thư mục gốc.'
        ],
        'prompt': """Hãy xây dựng giao diện web cho 'Lưới danh sách sản phẩm thương mại điện tử' (E-commerce Product Grid).
Yêu cầu:
1. Header có giỏ hàng với số lượng món hàng cập nhật động khi bấm mua.
2. Thanh lọc sản phẩm theo phân loại (Tất cả, Đồ điện tử, Thời trang, Phụ kiện) và sắp xếp theo giá.
3. Lưới sản phẩm ít nhất 6 mặt hàng mẫu: ảnh sản phẩm, tag giảm giá, tên sản phẩm, đánh giá sao (4.5★), giá gốc và giá giảm.
4. Nút 'Thêm vào giỏ hàng' có hiệu ứng phản hồi khi bấm.
5. Responsive hoàn hảo từ 375px đến 1440px.
6. Tạo đúng 3 file index.html, style.css, script.js tại thư mục gốc."""
    },
    {
        'id': 'T05',
        'dir': 'T05_pricing_table',
        'name': 'Pricing Table',
        'title_vi': 'Bảng giá dịch vụ và so sánh các gói cước',
        'expected_files': ['index.html', 'style.css', 'script.js'],
        'ui_reqs': [
            '3 gói dịch vụ: Gói Cơ Bản (Starter), Gói Chuyên Nghiệp (Pro - Nổi bật nhất), Gói Doanh Nghiệp (Enterprise).',
            'Công tắc chuyển đổi (Toggle) giữa thanh toán Theo tháng (Monthly) và Theo năm (Annually) kèm giảm giá 20%.',
            'Danh sách tính năng đi kèm có dấu tích xanh hoặc gạch chéo.',
            'Nút Đăng ký gói (Call to Action) nổi bật cho từng gói.'
        ],
        'tech_reqs': [
            'CSS Flexbox/Grid căn đều 3 cột, gói Pro có viền sáng hoặc huy hiệu Phổ biến nhất.',
            'JavaScript chuyển đổi số tiền khi gạt toggle tháng/năm.',
            'Semantic markup và responsive tốt.',
            'Đúng 3 file index.html, style.css, script.js tại thư mục gốc.'
        ],
        'prompt': """Hãy xây dựng giao diện web cho 'Bảng giá dịch vụ phần mềm SaaS' (Pricing Table).
Yêu cầu:
1. Tiêu đề và phụ đề giới thiệu các gói giá minh bạch.
2. Công tắc gạt (Toggle Switch) chuyển đổi giữa 'Thanh toán hàng tháng' và 'Thanh toán hàng năm (Tiết kiệm 20%)'.
3. 3 thẻ bảng giá: Starter ($19/tháng), Professional ($49/tháng - gói nổi bật với badge 'Most Popular'), Enterprise ($99/tháng).
4. Mỗi gói liệt kê 5-6 tính năng với dấu kiểm tích hợp.
5. Nút 'Bắt đầu sử dụng' phù hợp với từng gói.
6. Thay đổi giá tự động khi gạt switch hàng tháng/hàng năm.
7. Responsive 375px, 768px, 1440px.
8. Đúng 3 file index.html, style.css, script.js tại thư mục gốc."""
    },
    {
        'id': 'T06',
        'dir': 'T06_user_profile',
        'name': 'User Profile & Settings',
        'title_vi': 'Hồ sơ người dùng và cài đặt tài khoản',
        'expected_files': ['index.html', 'style.css', 'script.js'],
        'ui_reqs': [
            'Bố cục dạng Tab chuyển đổi: Thông tin cá nhân, Mật khẩu & Bảo mật, Cài đặt thông báo.',
            'Khu vực ảnh đại diện (Avatar) có nút thay đổi ảnh.',
            'Form chỉnh sửa thông tin: Họ tên, Tên hiển thị, Email, Tiểu sử cá nhân, Múi giờ.',
            'Các nút Lưu thay đổi và Hủy bỏ.'
        ],
        'tech_reqs': [
            'Tabs chuyển đổi hoạt động mượt mà bằng JavaScript thuần.',
            'Form inputs có floating label hoặc layout chuẩn thẩm mỹ.',
            'Thông báo lưu thành công (toast notification) khi bấm Lưu.',
            'Đúng 3 file index.html, style.css, script.js tại thư mục gốc.'
        ],
        'prompt': """Hãy xây dựng giao diện web cho 'Hồ sơ người dùng & Cài đặt tài khoản' (User Profile & Settings).
Yêu cầu:
1. Sidebar hoặc Tab điều hướng: Thông tin chung (Profile), Bảo mật (Security), Thông báo (Notifications).
2. Phần ảnh đại diện (Avatar) với nút đổi ảnh và xem trước ảnh.
3. Form nhập thông tin: Họ và tên, Email, Tiêu đề công việc, Giới thiệu bản thân (Bio textarea).
4. Nhóm nút thao tác: 'Lưu thay đổi' (Save Changes) và 'Hủy' (Cancel).
5. Khi bấm Lưu, hiện thông báo Toast 'Đã lưu thay đổi thành công!'.
6. Responsive mượt mà từ 375px đến 1440px.
7. Đúng 3 file index.html, style.css, script.js tại thư mục gốc."""
    },
    {
        'id': 'T07',
        'dir': 'T07_checkout_wizard',
        'name': 'Multi-step Checkout Wizard',
        'title_vi': 'Quy trình đặt hàng và thanh toán đa bước',
        'expected_files': ['index.html', 'style.css', 'script.js'],
        'ui_reqs': [
            'Thanh tiến trình (Step Progress Bar): Bước 1 - Giao hàng, Bước 2 - Phương thức thanh toán, Bước 3 - Xác nhận đơn.',
            'Nội dung từng bước chuyển đổi mượt mà không tải lại trang.',
            'Tóm tắt đơn hàng (Order Summary) hiển thị cố định ở cột bên phải.',
            'Nút Quay lại và Tiếp tục / Đặt hàng tương ứng với từng bước.'
        ],
        'tech_reqs': [
            'JavaScript quản lý trạng thái từng bước (Step State Management).',
            'Kiểm tra hợp lệ trước khi cho phép chuyển sang bước tiếp theo.',
            'Đúng 3 file index.html, style.css, script.js tại thư mục gốc.'
        ],
        'prompt': """Hãy xây dựng giao diện web cho 'Quy trình thanh toán đa bước' (Multi-step Checkout Wizard).
Yêu cầu:
1. Thanh chỉ báo tiến trình (Stepper Indicator) gồm 3 bước: 1. Địa chỉ nhận hàng -> 2. Thanh toán -> 3. Hoàn tất.
2. Bước 1: Nhập thông tin người nhận (Họ tên, SĐT, Địa chỉ, Ghi chú giao hàng).
3. Bước 2: Chọn phương thức thanh toán (Thẻ tín dụng / Ví điện tử / COD) với form nhập thẻ.
4. Cột bên phải hiển thị Bảng tóm tắt đơn hàng (Sản phẩm, Phí vận chuyển, Thuế, Tổng tiền).
5. Nút 'Quay lại' và 'Tiếp tục' có kiểm tra xác thực trước khi bước tiếp.
6. Responsive trên Mobile (375px), Tablet (768px), Desktop (1440px).
7. Đúng 3 file index.html, style.css, script.js tại thư mục gốc."""
    },
    {
        'id': 'T08',
        'dir': 'T08_landing_hero',
        'name': 'Landing Page Hero Section',
        'title_vi': 'Trang đích giới thiệu sản phẩm công nghệ',
        'expected_files': ['index.html', 'style.css', 'script.js'],
        'ui_reqs': [
            'Thanh Navigation bar trên cùng có Logo, Menu điều hướng, và nút Đăng ký dùng thử.',
            'Phần Hero chính với Tiêu đề lớn (Headline ấn tượng), đoạn giới thiệu ngắn và 2 nút Call-to-Action (Bắt đầu miễn phí / Xem video demo).',
            'Khung minh họa trực quan (App preview / Product Mockup card).',
            'Dải logo các thương hiệu đối tác tin cậy (Social proof badges).'
        ],
        'tech_reqs': [
            'Thiết kế đồ họa hiện đại với gradient hoặc hiệu ứng thẻ kính mờ (glassmorphism).',
            'Mobile menu toggle (hamburger button) cho màn hình nhỏ.',
            'Responsive chuẩn mực từ 375px đến 1440px.',
            'Đúng 3 file index.html, style.css, script.js tại thư mục gốc.'
        ],
        'prompt': """Hãy xây dựng giao diện web cho 'Trang đích giới thiệu sản phẩm công nghệ' (Landing Page Hero Section).
Yêu cầu:
1. Navbar trên cùng cố định (Sticky Header) với Logo thương hiệu, các liên kết (Tính năng, Bảng giá, Tài liệu) và nút 'Bắt đầu ngay'.
2. Tiêu đề chính lớn (Headline), phụ đề thuyết phục và nhóm 2 nút CTA: 'Dùng thử 14 ngày' và 'Xem bản demo'.
3. Khu vực hình ảnh minh họa sản phẩm hoặc mockup bảng điều khiển ứng dụng ấn tượng.
4. Hàng logo đối tác tin cậy bên dưới để tăng độ uy tín.
5. Menu Hamburger hoạt động trên điện thoại di động (375px).
6. Tương thích responsive hoàn hảo trên Mobile, Tablet, Desktop.
7. Đúng 3 file index.html, style.css, script.js tại thư mục gốc."""
    }
]

base_dir = Path(__file__).resolve().parent.parent
tasks_dir = base_dir / 'tasks'
designs_dir = base_dir / 'designs'

for t in tasks_data:
    t_dir = tasks_dir / t['dir']
    t_dir.mkdir(parents=True, exist_ok=True)
    
    prompt_file = t_dir / 'prompt.txt'
    prompt_file.write_text(t['prompt'], encoding='utf-8')
    
    meta_file = t_dir / 'task_meta.yaml'
    meta_content = {
        'task_id': t['id'],
        'name': t['name'],
        'title_vi': t['title_vi'],
        'prompt_file': f"tasks/{t['dir']}/prompt.txt",
        'reference_image': f"designs/{t['id']}_reference.png",
        'expected_files': t['expected_files'],
        'ui_requirements': t['ui_reqs'],
        'technical_requirements': t['tech_reqs'],
    }
    with open(meta_file, 'w', encoding='utf-8') as f:
        yaml.dump(meta_content, f, allow_unicode=True, default_flow_style=False)
        
    ref_img_path = designs_dir / f"{t['id']}_reference.png"
    if not ref_img_path.exists():
        w, h = 1440, 900
        img = Image.new('RGB', (w, h), color='#F8F9FA')
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([200, 120, 1240, 780], radius=24, fill='#FFFFFF', outline='#D3E3FD', width=3)
        draw.rounded_rectangle([200, 120, 1240, 220], radius=24, fill='#0B57D0')
        try:
            f_title = ImageFont.truetype('arialbd.ttf', 32)
            f_sub = ImageFont.truetype('arial.ttf', 18)
        except Exception:
            f_title = f_sub = ImageFont.load_default()
        draw.text((250, 150), f"[{t['id']}] {t['name']}", fill='#FFFFFF', font=f_title)
        draw.text((250, 250), f"Ảnh thiết kế mẫu chuẩn NCKH: {t['title_vi']}", fill='#1F1F1F', font=f_sub)
        draw.text((250, 290), f"Yêu cầu tệp đầu ra: {', '.join(t['expected_files'])}", fill='#00639B', font=f_sub)
        
        y_pos = 350
        for idx, req in enumerate(t['ui_reqs'][:5], 1):
            draw.text((260, y_pos), f"{idx}. {req[:85]}...", fill='#444746', font=f_sub)
            y_pos += 45
        img.save(ref_img_path)
        print(f"Generated reference image for {t['id']}")

print("All 8 tasks initialized successfully!")

