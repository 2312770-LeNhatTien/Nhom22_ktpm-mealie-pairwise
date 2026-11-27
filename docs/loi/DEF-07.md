# DEF-07: Tạo danh sách mua sắm với tên rỗng vẫn được chấp nhận

1. **Luồng và test phát hiện:** Danh sách mua sắm, `tests/test_am_tinh.py::test_ms_n5_tao_danh_sach_ten_rong`.
2. **Môi trường:** Mealie v3.28.0 chạy bằng Docker (SQLite); Python 3.12/3.13; pytest 9.x.
3. **Cách tái hiện:**
   Gửi `POST /api/households/shopping/lists` với nội dung:
   ```json
   {
     "name": ""
   }
   ```
4. **Mong đợi:** Trả về mã lỗi 4xx (422 Unprocessable Entity), từ chối tạo danh sách có tên rỗng.
   **Thực tế:** Mealie trả về mã 201 Created và tạo thành công một danh sách mua sắm có tên rỗng `""`.
5. **Nguyên nhân (file và hàm trong mã Mealie v3.28.0):** Trong schema `ShoppingListIn` (`mealie/schema/shopping_list/shopping_list_schema.py`), trường `name` được khai báo là kiểu `str` thông thường mà không có ràng buộc `min_length=1` hoặc validator kiểm tra chuỗi rỗng / khoảng trắng. Hệ thống chấp nhận chuỗi rỗng và lưu vào cột `name` của bảng `shopping_lists` mà không ném lỗi.
6. **Mức độ:** Thấp — API hoạt động bình thường nhưng cho phép tạo các danh sách không có tên, gây khó khăn cho trải nghiệm người dùng trên giao diện.
7. **Bằng chứng:** `docs/evidence/G-am-tinh-lan1.log`, `G-am-tinh-lan1.xml`, `G-am-tinh-lan2.log`, `G-am-tinh-lan2.xml`.
8. **Test bị ảnh hưởng:** `test_ms_n5_tao_danh_sach_ten_rong`.
