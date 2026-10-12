# Bằng chứng mục C

Thu trên bản Mealie local ngày 12/10/2026. Phân biệt dữ liệu đo thật với hướng dẫn trước khi dùng trong báo cáo.

| File | Nguồn và ý nghĩa |
| --- | --- |
| `C-environment.json` | Đầu ra lệnh Docker, OS và đường dẫn SQLite thực tế |
| `C-seed-inventory.json` | Category/tag, 12 công thức và hai user đã nạp vào API |
| `C-api-verification.json` | 16 bước API đã thực thi, status/response và kiểm tra khôi phục |
| `C-01` đến `C-03` PNG | Ảnh trình duyệt chụp trang hiển thị log môi trường, không phải terminal |
| `C-04`, `C-08`, `C-09` PNG | Trang đăng nhập, trang chủ, Swagger của Mealie |
| `C-05` đến `C-07` PNG | Ảnh người dùng gửi từ bản phụ cổng 9926: Account Details, Summary, Setup Complete |
| `C-onboarding-verification.json` | API đăng nhập sau wizard trả 200, admin đúng thông tin lab, version v3.28.0 và 0 công thức trên bản phụ |
| `C-10` đến `C-12` PNG | Giao diện 12 món, lọc còn 5, thêm tag còn 2 |
| `C-20` đến `C-23` PNG | Giao diện household trước/sau và công thức mới kế thừa cài đặt |
| `C-30` PNG | Giao diện quyền thành viên |
| `C-31` đến `C-33` PNG | Ảnh trình duyệt chụp log API: 403, cấp quyền, 201 |
| `C-API-summary.png` | Ảnh tổng hợp log 16 bước, không phải kết quả cả bộ Pairwise |

HTML `*-log.html` chỉ trình bày JSON gốc, không gọi API và không tạo số liệu thử nghiệm. Sau khi chạy lại seed/verify, chạy `python scripts/tao_trang_bang_chung_c.py` để cập nhật HTML; phải chụp lại PNG nếu muốn ảnh khớp lần chạy mới. Các UUID/tên demo có thể khác giữa các lần; kiểm tra thời điểm trong JSON/HTML.

Để xem HTML tại máy local, từ gốc repo chạy `python -m http.server 8765 --bind 127.0.0.1 --directory docs/evidence`, mở `http://127.0.0.1:8765/C-api-log.html`; Ctrl+C để dừng. Chỉ phục vụ thư mục bằng chứng.

Ảnh wizard do người dùng chụp trên container `mealie-onboarding`, volume riêng `mealie-onboarding-data` mới tạo ngày 12/10/2026 lúc 11:16:21 (UTC+7). Giữ nguyên ảnh gốc được gửi, không chỉnh sửa nội dung. Đã xác minh tài khoản admin đăng nhập API được sau wizard. Summary có Use Seed Data được bật; đây là dữ liệu dựng sẵn của Mealie, khác bộ seed 12 công thức của nhóm ở cổng 9925.

Chưa có phản hồi cài máy của bốn bạn khác; phần đọc chéo hướng dẫn Compose/seed vẫn cần người khác kiểm tra độc lập từ môi trường sạch. Chưa quay video/kịch bản demo (việc 5 nằm ngoài đợt này).

Log không chứa mật khẩu/token; email example.com và mật khẩu trong tài liệu seed là dữ liệu lab đã quy ước trong README.
