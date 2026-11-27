# DEF-02: Tên công thức rỗng gây lỗi server 500

1. **Luồng và test phát hiện:** Quản lý công thức, `tests/test_am_tinh.py::test_ct_n1_tao_cong_thuc_ten_rong` và `test_ct_n2_sua_ten_cong_thuc_thanh_rong`.
2. **Môi trường:** Mealie v3.28.0 chạy bằng Docker (SQLite); Python 3.13; pytest 9.2.0.
3. **Cách tái hiện:**
   - Tạo mới: Gửi `POST /api/recipes` với nội dung `{"name": ""}`.
   - Sửa: Tạo một công thức hợp lệ, sau đó gửi `PATCH /api/recipes/{slug}` với nội dung `{"name": ""}`.
4. **Mong đợi:** Trả về mã lỗi 4xx (422 Unprocessable Entity), từ chối tạo/sửa công thức.
   **Thực tế:** Mealie trả về mã 500 Internal Server Error.
5. **Nguyên nhân (file và hàm trong mã Mealie v3.28.0):**
   - Schema: `mealie/schema/recipe/recipe.py` — class `CreateRecipe` (dòng 115), trường `name: str` (dòng 116) và class `RecipeSummary` (dòng 119), trường `name: str | None = None` (dòng 127) không có ràng buộc `min_length=1`, nên chuỗi rỗng `""` đi qua tầng Pydantic.
   - Model (dòng gây lỗi 500 từ `docker compose logs mealie`): `mealie/db/models/recipe/recipe.py`, hàm `validate_name` (dòng 187) thực hiện `assert name != ""` và ném ra `AssertionError`. Ngoại lệ này không được controller bắt thành lỗi 4xx nên FastAPI trả về mã 500.
6. **Mức độ:** Trung bình — lỗi 500 xảy ra khi gửi dữ liệu rỗng ở thao tác cơ bản, tuy nhiên không làm hỏng dữ liệu hiện có trong hệ thống.
7. **Bằng chứng:** `docs/evidence/G-am-tinh-lan1.log`, `G-am-tinh-lan1.xml`, `G-am-tinh-lan2.log`, `G-am-tinh-lan2.xml`.
8. **Test bị ảnh hưởng:** `test_ct_n1_tao_cong_thuc_ten_rong`, `test_ct_n2_sua_ten_cong_thuc_thanh_rong`.
