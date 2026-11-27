# DEF-02: Tên công thức rỗng gây lỗi server 500

1. **Luồng và test phát hiện:** Quản lý công thức, `tests/test_am_tinh.py::test_ct_n1_tao_cong_thuc_ten_rong` và `test_ct_n2_sua_ten_cong_thuc_thanh_rong`.
2. **Môi trường:** Mealie v3.28.0 chạy bằng Docker (SQLite); Python 3.12/3.13; pytest 9.x.
3. **Cách tái hiện:**
   - Tạo mới: Gửi `POST /api/recipes` với nội dung `{"name": ""}`.
   - Sửa: Tạo một công thức hợp lệ, sau đó gửi `PATCH /api/recipes/{slug}` với nội dung `{"name": ""}`.
4. **Mong đợi:** Trả về mã lỗi 4xx (422 Unprocessable Entity), từ chối tạo/sửa công thức.
   **Thực tế:** Mealie trả về mã 500 Internal Server Error.
5. **Nguyên nhân (file và hàm trong mã Mealie v3.28.0):** Trong schema và service tạo/sửa công thức (`mealie/schema/recipe/recipe_schema.py` và `mealie/services/recipe/recipe_service.py`), trường `name` không được cấu hình ràng buộc `min_length=1` ở tầng Pydantic. Khi xử lý tạo slug từ tên (`slugify(name)`), hàm nhận chuỗi rỗng và ném ngoại lệ (`AssertionError` trong hàm `validate_name` hoặc lỗi sinh slug) không được bắt (unhandled exception), khiến FastAPI trả về mã lỗi máy chủ 500 thay vì trả về lỗi 422 từ chối dữ liệu đầu vào.
6. **Mức độ:** Trung bình — lỗi 500 xảy ra khi gửi dữ liệu rỗng ở thao tác cơ bản, tuy nhiên không làm hỏng dữ liệu hiện có trong hệ thống.
7. **Bằng chứng:** `docs/evidence/G-am-tinh-lan1.log`, `G-am-tinh-lan1.xml`, `G-am-tinh-lan2.log`, `G-am-tinh-lan2.xml`.
8. **Test bị ảnh hưởng:** `test_ct_n1_tao_cong_thuc_ten_rong`, `test_ct_n2_sua_ten_cong_thuc_thanh_rong`.
