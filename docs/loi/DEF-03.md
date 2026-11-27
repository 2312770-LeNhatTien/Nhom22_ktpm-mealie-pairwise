# DEF-03: Thêm mục mua sắm vào danh sách không tồn tại gây lỗi server 500

1. **Luồng và test phát hiện:** Danh sách mua sắm, `tests/test_am_tinh.py::test_ms_n1_shopping_list_id_khong_ton_tai`.
2. **Môi trường:** Mealie v3.28.0 chạy bằng Docker (SQLite); Python 3.12/3.13; pytest 9.x.
3. **Cách tái hiện:**
   Gửi `POST /api/households/shopping/items` với nội dung:
   ```json
   {
     "shoppingListId": "00000000-0000-0000-0000-000000000000",
     "note": "kiem thu loi"
   }
   ```
4. **Mong đợi:** Trả về mã lỗi 404 Not Found hoặc 4xx từ chối vì danh sách mua sắm không tồn tại.
   **Thực tế:** Mealie trả về mã 500 Internal Server Error.
5. **Nguyên nhân (file và hàm trong mã Mealie v3.28.0):** Trong `mealie/repos/repository_shopping_list.py` và `mealie/services/shopping_list/shopping_list_service.py`, hàm thêm mục (`create` / `add_item`) không thực hiện truy vấn kiểm tra sự tồn tại của `shoppingListId` trước khi ghi dữ liệu. Khi thực hiện nạp đối tượng quan hệ cha (parent relationship) bị `None` hoặc khi commit gặp vi phạm ràng buộc dữ liệu, hệ thống ném ra `ValidationError` / ngoại lệ không được xử lý ở controller, dẫn đến trả về mã 500 thay vì kiểm tra và trả về mã lỗi 404.
6. **Mức độ:** Trung bình — gây lỗi máy chủ 500 khi gọi API với ID không hợp lệ.
7. **Bằng chứng:** `docs/evidence/G-am-tinh-lan1.log`, `G-am-tinh-lan1.xml`, `G-am-tinh-lan2.log`, `G-am-tinh-lan2.xml`.
8. **Test bị ảnh hưởng:** `test_ms_n1_shopping_list_id_khong_ton_tai`.
