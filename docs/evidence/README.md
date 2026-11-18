# Bằng chứng

Nhóm dùng Mealie v3.28.0 ở cổng 9925 để chuẩn bị dữ liệu và kiểm tra môi trường. Trình thiết lập lần đầu được chụp ở bản riêng cổng 9926.

| File | Nội dung |
| --- | --- |
| `C-environment.json` | Kết quả lệnh Docker, thông tin hệ điều hành và đường dẫn SQLite |
| `C-seed-inventory.json` | 3 category, 3 tag và 12 công thức mẫu |
| `C-onboarding-verification.json` | Đăng nhập admin sau thiết lập trả 200, đúng tài khoản nhóm |
| `C-01` đến `C-03` PNG | Lệnh kiểm tra phiên bản, Compose up và Compose ps; container healthy ở cổng 9925 |
| `C-04`, `C-08`, `C-09` PNG | Trang đăng nhập, trang chủ và Swagger |
| `C-05` đến `C-07` PNG | Account Details, Summary và Setup Complete trên cổng 9926 |
| `C-10` đến `C-12` PNG | Danh sách 12 món, lọc category còn 5, thêm tag còn 2 |
| `D-01` PNG | Thống kê của PICT cho 4 model (19, 14, 16 và 9 test case ở mức 2-wise) |
| `D-02` PNG | Kết quả `kiem_tra_cap.py --all`: cả 4 file case phủ 100% cặp giá trị |

Hai ảnh D-01 và D-02 là kết quả in ra của lệnh, lưu thành ảnh để đưa vào báo cáo; có thể chạy lại bằng `scripts\sinh_case.bat` và `python scripts\kiem_tra_cap.py --all`.

Bảng kết quả lọc nằm ở [seed-data.md](../seed-data.md).

Bản thiết lập cổng 9926 dùng container `mealie-onboarding`, volume riêng `mealie-onboarding-data`. Site Settings: tắt Advanced Content, tắt Public Access, bật Use Seed Data, thống nhất với README và hướng dẫn bắt đầu. Dữ liệu có sẵn của Mealie khác bộ 12 công thức của nhóm; vẫn cần chạy script nạp dữ liệu.

## Ảnh môi trường

Ba ảnh dưới đây chụp trực tiếp kết quả lệnh trong Windows PowerShell tại thư mục repo:

| Tên ảnh | Lệnh chạy trước khi chụp |
| --- | --- |
| `C-01-docker-version.png` | `docker --version`, `docker compose version` |
| `C-02-compose-up.png` | `docker compose up -d` |
| `C-03-compose-ps.png` | `docker compose ps`, thấy healthy và cổng 9925 |

Các ảnh giữ nguyên dòng lệnh và kết quả: Docker 29.8.0, Compose v5.5.1, container `mealie` Running, image v3.28.0, trạng thái healthy và ánh xạ cổng `9925:9000`. PowerShell chạy được các lệnh Docker này. Thời gian Up trong ảnh và log JSON có thể khác nhau do được ghi nhận ở hai lần kiểm tra.

Thời điểm chạy vẫn được giữ trong JSON gốc. Log và ảnh lưu trong repo không chứa mật khẩu/token đăng nhập. Tài khoản example.com là dữ liệu lab đã quy ước trong README.
