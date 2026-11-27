# DEF-04: Số lượng mua sắm âm (-3 vẫn lưu, -0.5 gây lỗi 500)

1. **Luồng và test phát hiện:** Danh sách mua sắm, `tests/test_am_tinh.py::test_ms_n2_so_luong_am` và `test_ms_n3_so_luong_am_le`.
2. **Môi trường:** Mealie v3.28.0 chạy bằng Docker (SQLite); Python 3.12/3.13; pytest 9.x.
3. **Cách tái hiện:**
   - Trường hợp số nguyên âm: Tạo một danh sách mua sắm, gửi `POST /api/households/shopping/items` với `quantity: -3`. Kết quả: Mealie trả mã 201 Created và lưu số lượng âm.
   - Trường hợp số thập phân âm: Gửi `POST /api/households/shopping/items` với `quantity: -0.5`. Kết quả: Mealie trả mã 500 Internal Server Error.
4. **Mong đợi:** Mã 4xx (422 Unprocessable Entity) từ chối mọi giá trị số lượng âm (`quantity > 0`).
   **Thực tế:** Với số nguyên âm (-3), Mealie chấp nhận và lưu vào CSDL (201); với số thập phân âm (-0.5), hệ thống sập với mã 500.
5. **Nguyên nhân (file và hàm trong mã Mealie v3.28.0):** 
   - Trong schema `ShoppingItemIn` (`mealie/schema/shopping_list/shopping_list_schema.py`), trường `quantity` được định nghĩa là `float` nhưng thiếu ràng buộc giá trị dương `gt=0` (greater than 0) của Pydantic. Do đó, các giá trị số âm đều vượt qua tầng validate dữ liệu.
   - Khi `quantity = -0.5`, hàm tiện ích hiển thị phân số `display_fraction` (trong `mealie/core/utils.py` hoặc `mealie/services/units/fractions.py`) thực hiện phân tích chuỗi ký tự số thập phân. Ký tự dấu âm `'-'` không nằm trong bảng ánh xạ phân số (fraction map), gây ra ngoại lệ `KeyError: '-'` không được bắt, làm sập request với mã 500.
6. **Mức độ:** Trung bình — vừa lưu dữ liệu sai (số lượng âm), vừa gây lỗi 500 với số thập phân âm.
7. **Bằng chứng:** `docs/evidence/G-am-tinh-lan1.log`, `G-am-tinh-lan1.xml`, `G-am-tinh-lan2.log`, `G-am-tinh-lan2.xml`.
8. **Test bị ảnh hưởng:** `test_ms_n2_so_luong_am`, `test_ms_n3_so_luong_am_le`.
