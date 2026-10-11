# TV2 Môi trường và demo: Nguyễn Phú Quý

Sản phẩm của bạn là mục C của báo cáo và phần demo trong buổi thuyết trình. Mục C đạt khi một người chưa biết gì làm theo là chạy được Mealie, và có ảnh chứng minh hệ thống chạy được cùng 3 luồng nghiệp vụ.

Làm xong [00-bat-dau.md](00-bat-dau.md) trước. Trong lúc tự cài, chụp màn hình từng bước luôn, vì đó chính là bằng chứng của mục C.

## Việc 1. Ghi lại quá trình cài đặt và lỗi thường gặp

Chụp các ảnh sau, lưu vào `docs/evidence/`:

| Tên file | Chụp gì |
| --- | --- |
| `C-01-docker-version.png` | Kết quả lệnh `docker --version` và `docker compose version` |
| `C-02-compose-up.png` | Kết quả lệnh `docker compose up -d` |
| `C-03-compose-ps.png` | Kết quả lệnh `docker compose ps`, thấy container `mealie` đang chạy |
| `C-04-login.png` | Trang đăng nhập ở `http://localhost:9925` |
| `C-05-setup-account.png` | Bước Account Details của trình thiết lập |
| `C-06-setup-summary.png` | Bước Summary |
| `C-07-setup-complete.png` | Màn hình Setup Complete |
| `C-08-home.png` | Trang chủ sau khi đăng nhập bằng tài khoản dùng chung |
| `C-09-api-docs.png` | Trang `http://localhost:9925/docs` |

Cách chụp trên Windows: bấm **Windows + Shift + S**, kéo chọn vùng, rồi dán vào Paint và lưu thành PNG. Che thông tin cá nhân nếu lọt vào ảnh.

Nếu đã cài xong mà chưa kịp chụp các bước thiết lập: chạy `docker compose down -v`, rồi `docker compose up -d` và làm lại, lần này chụp đủ.

Hỏi 4 bạn còn lại đã gặp lỗi gì khi cài. Ghi mỗi lỗi một dòng: hiện tượng, nguyên nhân, cách sửa. Phần này cho thấy nhóm đã cài thật.

## Việc 2. Tạo dữ liệu mẫu

Test chỉ lặp lại được khi dữ liệu ban đầu cố định. Bảng dưới đây là bộ dữ liệu đề xuất. Nó đã được nạp thử vào Mealie v3.28.0 và cho đúng các số ở bảng kết quả bên dưới. Thống nhất với Toàn trước khi tạo, vì bảng này quyết định kết quả mong đợi của luồng tìm kiếm.

**Category:** `Món chính`, `Tráng miệng`, `Đồ uống`. Tạo ở `/group/data/categories`.

**Tag:** `Nhanh`, `Chay`, `Cay`. Tạo ở `/group/data/tags`.

**Công thức:** tạo ở `/g/home/r/create/new`. Chỉ cần điền tên, rồi gắn category và tag. Gõ đúng tên, đúng dấu.

| # | Tên công thức | Category | Tag |
| --- | --- | --- | --- |
| 1 | Phở bò | Món chính | |
| 2 | Bún chả | Món chính | Nhanh |
| 3 | Gỏi cuốn chay | Món chính | Nhanh, Chay |
| 4 | Lẩu thái | Món chính | Cay |
| 5 | Chè đậu | Tráng miệng | Chay |
| 6 | Bánh flan | Tráng miệng | |
| 7 | Sinh tố bơ | Đồ uống, Tráng miệng | Nhanh, Chay |
| 8 | Trà đá | Đồ uống | Nhanh |
| 9 | Cà phê sữa | Đồ uống | |
| 10 | Nước mắm pha | | Cay |
| 11 | Cơm trắng | | |
| 12 | Xôi xoài | Món chính, Tráng miệng | Chay |

Bộ này có đủ các trường hợp cần cho luồng tìm kiếm: công thức không có category, có một, có hai; tương tự với tag.

Kết quả lọc đúng của bộ dữ liệu này, dùng để tự kiểm tra sau khi tạo (vào `/g/home/recipes/finder` lọc thử):

| Lọc theo | Số công thức | Gồm |
| --- | --- | --- |
| Category Món chính | 5 | Bún chả, Gỏi cuốn chay, Lẩu thái, Phở bò, Xôi xoài |
| Category Tráng miệng | 4 | Bánh flan, Chè đậu, Sinh tố bơ, Xôi xoài |
| Category Đồ uống | 3 | Cà phê sữa, Sinh tố bơ, Trà đá |
| Món chính hoặc Tráng miệng | 8 | |
| Món chính và Tráng miệng (bắt buộc đủ cả hai) | 1 | Xôi xoài |
| Tag Nhanh | 4 | Bún chả, Gỏi cuốn chay, Sinh tố bơ, Trà đá |
| Tag Chay | 4 | Chè đậu, Gỏi cuốn chay, Sinh tố bơ, Xôi xoài |
| Tag Cay | 2 | Lẩu thái, Nước mắm pha |
| Tag Nhanh và Chay (bắt buộc đủ cả hai) | 2 | Gỏi cuốn chay, Sinh tố bơ |
| Category Món chính và tag Chay | 2 | Gỏi cuốn chay, Xôi xoài |

**Tài khoản:** tạo ở `/admin/manage/users/create`, cùng group `Home` và household `Family` với admin.

| Username | Email | Mật khẩu | Quyền |
| --- | --- | --- | --- |
| `khongquyen` | `khongquyen@example.com` | `Nhom22@Mealie` | Bỏ tích hết mọi quyền |
| `duquyen` | `duquyen@example.com` | `Nhom22@Mealie` | Tích đủ 4 quyền, không tích Administrator |

Bốn quyền trên giao diện tương ứng với tên trong API:

| Trên giao diện (tiếng Anh) | Tên trong API |
| --- | --- |
| User can invite others to group | `canInvite` |
| User can manage group settings | `canManage` |
| User can manage household | `canManageHousehold` |
| User can manage foods, tags, and categories | `canOrganize` |

Xong thì điền `docs/seed-data.md` đúng với những gì đã tạo.

## Việc 3. Chụp bằng chứng 3 luồng nghiệp vụ

Mỗi luồng 3–4 ảnh theo đúng thứ tự thao tác.

**Luồng 1, tìm kiếm và lọc** (`/g/home/recipes/finder` hoặc trang chủ):

| Tên file | Chụp gì |
| --- | --- |
| `C-10-search-danh-sach.png` | Danh sách đủ 12 công thức |
| `C-11-search-loc-category.png` | Lọc theo category Món chính, ra 5 công thức |
| `C-12-search-loc-them-tag.png` | Lọc thêm tag Chay, còn 2 công thức |
| `C-13-search-sap-xep.png` | Đổi cách sắp xếp |

**Luồng 2, cấu hình household** (`/household`):

| Tên file | Chụp gì |
| --- | --- |
| `C-20-household-cai-dat.png` | Màn hình cài đặt household lúc đầu |
| `C-21-household-doi.png` | Sau khi bật hai tùy chọn mặc định của công thức, ví dụ hiện thông tin dinh dưỡng và tắt bình luận |
| `C-22-household-tao-cong-thuc.png` | Tạo một công thức mới |
| `C-23-household-ket-qua.png` | Phần cài đặt của công thức mới, thấy nó nhận đúng hai tùy chọn vừa bật |

**Luồng 3, phân quyền:**

| Tên file | Chụp gì |
| --- | --- |
| `C-30-permission-tao-user.png` | Admin tạo user `khongquyen` |
| `C-31-permission-bi-chan.png` | Đăng nhập bằng `khongquyen`, vào `/group/data/categories` thử tạo category: bị từ chối hoặc không thấy nút tạo |
| `C-32-permission-cap-quyen.png` | Admin cấp quyền quản lý category và tag ở `/household/members` |
| `C-33-permission-duoc-phep.png` | `khongquyen` tạo category thành công |

Chụp xong ảnh `C-32` và `C-33` thì bỏ quyền vừa cấp, để tài khoản `khongquyen` trở lại đúng như bảng dữ liệu mẫu.

## Việc 4. Viết mục C

Tạo `docs/muc-c.md` theo khung sau. Phần trong ngoặc nhọn là chỗ bạn điền.

```markdown
# Mục C. Môi trường và cách chạy hệ thống

## C.1 Môi trường và phiên bản

| Thành phần | Phiên bản |
| --- | --- |
| Hệ điều hành | <Windows 10 hoặc 11, bản nào> |
| Docker Desktop | <số phiên bản> |
| Mealie | v3.28.0, commit 0552eaa4a80031b8572849cca0ed95d07f1be001 |
| Docker image | ghcr.io/mealie-recipes/mealie:v3.28.0 |

## C.2 Lệnh build và run

<Dán nội dung docker-compose.yml, giải thích từng dòng: image, ports, volumes, environment>
<Bảng các lệnh: up, ps, logs, stop, start, down -v>
<Các bước thiết lập lần đầu, kèm ảnh C-05 đến C-07>

## C.3 Cơ sở dữ liệu và service

<SQLite, nằm trong volume mealie-data ở đường dẫn /app/data trong container>
<Không có service nào khác. Cổng 9925 trên máy nối vào cổng 9000 trong container>
<Bảng biến môi trường: ALLOW_SIGNUP, TZ, BASE_URL, PUID, PGID>

## C.4 Dữ liệu mẫu

<Tài khoản dùng chung, 2 tài khoản thường>
<3 category, 3 tag, bảng 12 công thức. Dẫn tới docs/seed-data.md>

## C.5 Bằng chứng

<Ảnh C-01 đến C-09: hệ thống chạy được>
<Ảnh C-10 đến C-33: ba luồng nghiệp vụ, mỗi ảnh một dòng chú thích>

## C.6 Lỗi thường gặp

| Hiện tượng | Nguyên nhân | Cách sửa |
| --- | --- | --- |
```

Ý nghĩa các dòng trong `docker-compose.yml` để viết C.2 và C.3:

| Dòng | Ý nghĩa |
| --- | --- |
| `image` | Bản đóng gói chính thức của Mealie, đúng phiên bản nhóm đã chốt. Không dùng `latest` vì nó thay đổi theo thời gian |
| `ports: "9925:9000"` | Mealie trong container nghe cổng 9000, máy mình truy cập qua cổng 9925 |
| `volumes: mealie-data:/app/data/` | Nơi lưu file SQLite và ảnh. Tắt container dữ liệu vẫn còn, chỉ mất khi chạy `down -v` |
| `ALLOW_SIGNUP: "false"` | Tắt tự đăng ký, tài khoản mới do admin tạo |
| `PUID`, `PGID` | Mã người dùng mà Mealie chạy bên trong container |
| `TZ` | Múi giờ |
| `BASE_URL` | Địa chỉ truy cập, Mealie dùng để tạo link |

Lấy số phiên bản Docker Desktop: mở Docker Desktop, bấm biểu tượng bánh răng, hoặc gõ `docker version`.

Viết xong thì mở Pull Request và nhờ Nhật Tiến cài lại từ đầu theo đúng tài liệu.

## Việc 5. Chuẩn bị demo

Trong bài nói 10 phút, phần của bạn khoảng 2 phút: 30 giây nói về môi trường, 90 giây demo trực tiếp luồng household.

Kịch bản demo, viết lại vào `docs/demo-kich-ban.md` và tập theo:

1. Mở sẵn hai tab: `/household` và `/g/home`. Đăng nhập sẵn.
2. Ở tab household: bật hai tùy chọn mặc định của công thức, lưu.
3. Sang tab trang chủ: tạo công thức mới tên "Demo", lưu.
4. Mở phần cài đặt của công thức "Demo": chỉ cho thấy hai tùy chọn vừa bật đã được áp dụng.
5. Nói một câu kết: "Luồng này có 9 tùy chọn kết hợp với nhau, nhóm sẽ dùng Pairwise để kiểm thử các tổ hợp".

Chuẩn bị dự phòng:

- Quay video màn hình chạy đủ 3 luồng, dài 2–3 phút. Trên Windows 11 dùng **Snipping Tool** (chế độ quay video) hoặc bấm **Windows + G**.
- Tối trước buổi báo cáo, chạy `docker compose up -d` trên máy sẽ dùng để chắc chắn image đã có sẵn. Khi đã có image, chạy Mealie không cần mạng.
- Xóa công thức "Demo" sau mỗi lần tập, và đưa cài đặt household về như cũ.
- Script test của Tuấn thay đổi cài đặt household mỗi lần chạy. Nếu máy demo vừa chạy test thì mở `/household` kiểm tra lại trước khi demo.
