# Danh sách lỗi đã ghi nhận

| Mã DEF | Luồng | Mức độ | Tiêu đề tóm tắt | Test phát hiện | Trạng thái |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **DEF-01** | Tìm kiếm | Thấp | Sắp xếp tên không theo alphabet tiếng Việt | `test_sap_xep_ten_theo_bang_chu_cai[asc]`, `[desc]` | Đã xác định nguyên nhân |
| **DEF-02** | Công thức | Trung bình | Tên công thức rỗng gây lỗi server 500 | `test_ct_n1_tao_cong_thuc_ten_rong`, `test_ct_n2_sua_ten_cong_thuc_thanh_rong` | Đã xác định nguyên nhân |
| **DEF-03** | Mua sắm | Trung bình | Thêm mục vào shoppingListId không tồn tại gây lỗi 500 | `test_ms_n1_shopping_list_id_khong_ton_tai` | Đã xác định nguyên nhân |
| **DEF-04** | Mua sắm | Trung bình | Số lượng mua sắm âm (-3 lưu 201, -0.5 gây lỗi 500) | `test_ms_n2_so_luong_am`, `test_ms_n3_so_luong_am_le` | Đã xác định nguyên nhân |
| **DEF-05** | Công thức | Thấp | Số khẩu phần âm (-5) vẫn được lưu | `test_ct_n3_so_khau_phan_am` | Đã xác định nguyên nhân |
| **DEF-06** | Kế hoạch & Mua sắm | Thấp | recipeId / foodId không tồn tại vẫn được lưu | `test_kh_n4_recipe_id_khong_ton_tai`, `test_ms_n4_food_id_khong_ton_tai` | Đã xác định nguyên nhân |
| **DEF-07** | Mua sắm | Thấp | Tạo danh sách mua sắm với tên rỗng vẫn được | `test_ms_n5_tao_danh_sach_ten_rong` | Đã xác định nguyên nhân |

Chi tiết từng lỗi nằm trong phiếu tương ứng (`DEF-01.md` đến `DEF-07.md`).

---

## Hành vi cần biết (Known Behaviors)

1. **Lọc category không tồn tại trả về toàn bộ công thức (`TK-N1`):**
   - **Mô tả:** Khi gửi yêu cầu `GET /api/recipes?categories=khong-ton-tai&perPage=50`, kết quả trả về `status = 200` và `total = 12` (toàn bộ công thức mẫu trong hệ thống), thay vì trả về danh sách rỗng (`total = 0`).
   - **Giải thích:** Trong Mealie v3.28.0, hàm xử lý bộ lọc category chuyển đổi các slug truyền vào thành danh sách ID category tương ứng trong CSDL. Nếu không tìm thấy slug nào hợp lệ trong database, danh sách ID trở thành rỗng; khi đó điều kiện lọc `IN (category_ids)` bị bỏ qua, dẫn đến API trả về toàn bộ danh sách công thức. Đây là hành vi do thiết kế logic xây dựng câu truy vấn của hệ thống, không tính là lỗi mà ghi nhận là **hành vi cần biết** để lưu ý khi thiết kế ca kiểm thử và tích hợp API.
