# Bằng chứng mục C

Nhóm dùng Mealie v3.28.0 ở cổng 9925 để chuẩn bị dữ liệu và kiểm tra ba luồng. Trình thiết lập lần đầu được chụp ở bản riêng cổng 9926.

| File | Nội dung |
| --- | --- |
| `C-environment.json` | Kết quả lệnh Docker, thông tin hệ điều hành và đường dẫn SQLite |
| `C-seed-inventory.json` | 3 category, 3 tag, 12 công thức và hai user lab |
| `C-api-verification.json` | 16 bước kiểm tra API và kết quả khôi phục dữ liệu |
| `C-04`, `C-08`, `C-09` PNG | Trang đăng nhập, trang chủ và Swagger |
| `C-05` đến `C-07` PNG | Account Details, Summary và Setup Complete trên cổng 9926 |
| `C-onboarding-verification.json` | Đăng nhập admin sau thiết lập trả 200, đúng tài khoản nhóm |
| `C-10` đến `C-12` PNG | Danh sách 12 món, lọc category còn 5, thêm tag còn 2 |
| `C-20` đến `C-23` PNG | Cài đặt household trước/sau và công thức mới nhận cài đặt mặc định |
| `C-30` PNG | Thành viên household và các quyền của user lab |
| `C-31` đến `C-33` PNG | Server response trong Swagger: user bị chặn 403, admin cấp quyền 200, user tạo category 201 |
| `C-swagger-verification.json` | Request, kết quả của lần chụp Swagger và kiểm tra dọn dữ liệu sau đó |

Ảnh C-31 đến C-33 giữ phần Request URL và Server response. Phần cURL chứa token nằm ngoài khung chụp. Các ảnh này được chụp trực tiếp trên `/docs`; JSON kiểm tra tự động lưu riêng để đối chiếu.

Ảnh C-08 và C-10 được chụp riêng: C-08 là trang chủ của admin; C-10 là danh sách công thức trong phiên user `khongquyen`. Bảng kết quả lọc nằm ở [seed-data.md](../seed-data.md).

Bản thiết lập cổng 9926 dùng container `mealie-onboarding`, volume riêng `mealie-onboarding-data`. Site Settings: tắt Advanced Content, tắt Public Access, bật Use Seed Data, thống nhất với README và hướng dẫn bắt đầu. Dữ liệu có sẵn của Mealie khác bộ 12 công thức của nhóm; vẫn cần chạy script nạp dữ liệu.

## Ảnh môi trường cần bổ sung

Các ảnh hiển thị lại log bằng HTML đã được bỏ. Cần chụp ba ảnh Command Prompt thật trước khi nghiệm thu mục C:

| Tên ảnh | Lệnh chạy trước khi chụp |
| --- | --- |
| `C-01-docker-version.png` | `docker --version`, `docker compose version` |
| `C-02-compose-up.png` | `docker compose up -d` |
| `C-03-compose-ps.png` | `docker compose ps`, thấy healthy và cổng 9925 |

Mở Command Prompt ở `D:\Nhom22_ktpm-mealie-pairwise`, chạy từng nhóm lệnh rồi chụp cả cửa sổ, gồm dòng lệnh và kết quả. Không dùng ảnh HTML thay cho ảnh terminal.

Thời điểm chạy vẫn được giữ trong JSON gốc. Log và ảnh lưu trong repo không chứa mật khẩu/token đăng nhập. Tài khoản example.com là dữ liệu lab đã quy ước trong README. Kết quả 16 bước chỉ dùng kiểm tra môi trường, chưa thay cho toàn bộ bộ test Pairwise. Video demo thuộc việc riêng.
