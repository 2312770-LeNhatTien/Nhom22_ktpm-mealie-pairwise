# Dữ liệu mẫu của Nhóm 22

Bộ dữ liệu dưới đây dùng trên Mealie v3.28.0, group `Home`, household `Family`. Khi đổi dữ liệu mẫu phải sửa file này cùng commit.

Người phụ trách: Nguyễn Phú Quý. Bùi Ngọc Toàn dùng bảng công thức này để xác định kết quả mong đợi của luồng tìm kiếm.

## Tài khoản

| Tài khoản | Mật khẩu | Quyền | Dùng cho |
| --- | --- | --- | --- |
| `nhom22@example.com` | `Nhom22@Mealie` | admin, tạo ở bước thiết lập lần đầu | Tạo dữ liệu và chạy test |

Mật khẩu chỉ dùng cho bản lab local của môn học, theo README.

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

Chạy Mealie và hoàn tất admin theo [mục C](muc-c.md). Tạo thủ công tại `/group/data/categories`, `/group/data/tags`, `/g/home/r/create/new` theo bảng trên, hoặc nạp bằng API tại thư mục gốc repo:

```bat
python scripts\chuan_bi_muc_c.py seed
```

Cần Python 3.10 trở lên, chỉ dùng thư viện chuẩn; không cần cài requirements để chạy script này. Mặc định địa chỉ `http://localhost:9925`; có thể thêm `--base-url http://localhost:9926`. Chỉ nhận HTTP loopback. Admin mặc định theo bảng; nếu cần, đặt `MEALIE_EMAIL` và `MEALIE_PASSWORD`.

`seed` không tạo trùng khi chạy lại. Nếu công thức cùng tên có nhãn khác bảng, script dừng để kiểm tra thủ công, không ghi đè. Script không xóa dữ liệu ngoài seed.

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

## Khôi phục sau khi test

Xóa đúng dữ liệu tạm do test tạo; giữ nguyên 12 món và ba category/tag. Không chạy hai lượt test cùng lúc vì cùng thay đổi dữ liệu trên một bản Mealie.

[Inventory thực tế](evidence/C-seed-inventory.json) ghi ID trên máy đã chạy. UUID sẽ khác trên máy mới; tra theo tên hoặc slug, không chép cứng UUID.
