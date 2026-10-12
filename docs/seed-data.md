# Dữ liệu mẫu của Nhóm 22

Đã nạp và kiểm tra bộ dữ liệu dưới đây trên Mealie v3.28.0 ngày 12/10/2026, group `Home`, household `Family`. Khi đổi dữ liệu mẫu phải sửa file này cùng commit. Tên và nhãn giữ đúng bảng trong hướng dẫn TV2 để Toàn dùng làm oracle tìm kiếm.

Người phụ trách: Nguyễn Phú Quý (TV2), thống nhất với Bùi Ngọc Toàn (TV4) vì bảng công thức quyết định kết quả mong đợi của luồng tìm kiếm.

## Tài khoản

| Tài khoản | Mật khẩu | Quyền | Dùng cho |
| --- | --- | --- | --- |
| `nhom22@example.com` | `Nhom22@Mealie` | admin, tạo ở bước thiết lập lần đầu | Tạo dữ liệu, luồng household |
| `khongquyen@example.com` | `Nhom22@Mealie` | admin=false; cả 4 quyền false | Luồng phân quyền |
| `duquyen@example.com` | `Nhom22@Mealie` | admin=false; cả 4 quyền true | Luồng phân quyền |

Username lần lượt là `nhom22`, `khongquyen`, `duquyen`. Bốn quyền: `canInvite`, `canManage`, `canManageHousehold`, `canOrganize`. Mật khẩu chỉ dùng cho bản lab local của môn học, theo README.

## Category và tag

| Loại | Tên |
| --- | --- |
| Category 1 | Món chính (`mon-chinh`) |
| Category 2 | Tráng miệng (`trang-mieng`) |
| Category 3 | Đồ uống (`do-uong`) |
| Tag 1 | Nhanh (`nhanh`) |
| Tag 2 | Chay (`chay`) |
| Tag 3 | Cay (`cay`) |

## Công thức

Đúng 12 công thức; ô trống nghĩa là không gắn nhãn. Chỉ cần tên và category/tag; không cần URL, ảnh hay nguyên liệu đầy đủ.

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

## Tạo lại dữ liệu

Chạy Mealie và hoàn tất admin theo [mục C](muc-c.md). Tạo thủ công tại `/group/data/categories`, `/group/data/tags`, `/g/home/r/create/new`, `/admin/manage/users/create` theo bảng trên, hoặc nạp bằng API tại thư mục gốc repo:

```bat
python scripts\chuan_bi_muc_c.py seed
python scripts\chuan_bi_muc_c.py verify
```

Cần Python 3.10 trở lên, chỉ dùng thư viện chuẩn; không cần cài requirements để chạy script này. Mặc định địa chỉ `http://localhost:9925`; có thể thêm `--base-url http://localhost:9926`. Chỉ nhận HTTP loopback. Admin mặc định theo bảng; nếu cần, đặt `MEALIE_EMAIL` và `MEALIE_PASSWORD`. Mật khẩu này cũng dùng cho hai user lab mới.

`seed` không tạo trùng khi chạy lại. Nếu công thức cùng tên có nhãn khác hoặc user có quyền khác bảng, script dừng để kiểm tra thủ công, không ghi đè. Script không xóa dữ liệu ngoài seed. `verify` yêu cầu đúng 12 công thức để kiểm tra tổng số; nếu có dữ liệu khác, dùng bản lab riêng hoặc kiểm tra dữ liệu thừa trước, không tự xóa cả volume.

## Kết quả mong đợi

| Bộ lọc | Tổng | Gồm |
| --- | --- | --- |
| Không lọc | 12 | Toàn bộ bảng |
| Món chính | 5 | Bún chả, Gỏi cuốn chay, Lẩu thái, Phở bò, Xôi xoài |
| Tráng miệng | 4 | Bánh flan, Chè đậu, Sinh tố bơ, Xôi xoài |
| Đồ uống | 3 | Cà phê sữa, Sinh tố bơ, Trà đá |
| Món chính OR Tráng miệng | 8 | Hợp hai category, không đếm trùng Xôi xoài |
| Món chính AND Tráng miệng | 1 | Xôi xoài |
| Nhanh | 4 | Bún chả, Gỏi cuốn chay, Sinh tố bơ, Trà đá |
| Chay | 4 | Chè đậu, Gỏi cuốn chay, Sinh tố bơ, Xôi xoài |
| Cay | 2 | Lẩu thái, Nước mắm pha |
| Nhanh AND Chay | 2 | Gỏi cuốn chay, Sinh tố bơ |
| Món chính AND tag Chay | 2 | Gỏi cuốn chay, Xôi xoài |

`verify` gọi 6 truy vấn đại diện (không lọc, Món chính, Món chính+Chay, category OR/AND, tag AND), kiểm tra tập tên chính xác và sắp xếp tăng/giảm. Các dòng lọc đơn còn lại suy ra từ bảng seed, không phải tất cả đều có lần gọi riêng trong log.

## Khôi phục sau demo

Xóa đúng công thức/category tạm do demo tạo; giữ nguyên 12 món và ba category/tag. Trả user `khongquyen` về cả bốn quyền false và admin=false. Khôi phục toàn bộ cấu hình household đã ghi trước demo. Trạng thái ban đầu máy này: `privateHousehold=true`, `showAnnouncements=true`, `lockRecipeEditsFromOtherHouseholds=true`, `firstDayOfWeek=0`; cả năm cờ `recipe...` false.

Không chạy demo và test đồng thời vì cùng thay đổi cấu hình/quyền. Script `verify` dùng `finally` để khôi phục khi có lỗi; nếu mất kết nối/mất điện, phải kiểm tra lại thủ công.

[Inventory thực tế](evidence/C-seed-inventory.json) ghi ID trên máy đã chạy. UUID sẽ khác trên máy mới; tra theo tên/slug, không chép cứng UUID. [Log xác minh](evidence/C-api-verification.json) ghi status/response của ba luồng và trạng thái sau dọn dẹp.
