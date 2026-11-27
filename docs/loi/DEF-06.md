# DEF-06: recipeId và foodId không tồn tại vẫn được lưu

1. **Luồng và test phát hiện:** Kế hoạch bữa ăn và Danh sách mua sắm, `tests/test_am_tinh.py::test_kh_n4_recipe_id_khong_ton_tai` và `test_ms_n4_food_id_khong_ton_tai`.
2. **Môi trường:** Mealie v3.28.0 chạy bằng Docker (SQLite); Python 3.12/3.13; pytest 9.x.
3. **Cách tái hiện:**
   - Kế hoạch bữa ăn: Gửi `POST /api/households/mealplans` với `recipeId` là một UUID ngẫu nhiên không tồn tại.
   - Danh sách mua sắm: Gửi `POST /api/households/shopping/items` với `foodId` là một UUID ngẫu nhiên không tồn tại.
4. **Mong đợi:** Trả về mã lỗi 4xx (404 Not Found hoặc 422 Unprocessable Entity), từ chối lưu vì khóa ngoại không tồn tại.
   **Thực tế:** Cả hai API đều trả về mã 201 Created và lưu thành công mục với ID khóa ngoại giả.
5. **Nguyên nhân (file và hàm trong mã Mealie v3.28.0):** 
   - Trong hệ cơ sở dữ liệu SQLite mặc định của Mealie, ràng buộc khóa ngoại (foreign key constraint) không được bật cưỡng bức (`PRAGMA foreign_keys = ON`).
   - Ở tầng xử lý nghiệp vụ (`mealie/services/mealplans/mealplan_service.py` và `mealie/services/shopping_list/shopping_list_service.py`), mã nguồn không thực hiện truy vấn kiểm tra sự tồn tại của `recipeId` trong bảng công thức hoặc `foodId` trong bảng thực phẩm trước khi tạo bản ghi mới. Do đó, các khóa ngoại mồ côi (orphaned foreign keys) vẫn được ghi trực tiếp vào cơ sở dữ liệu.
6. **Mức độ:** Thấp — API không phát sinh lỗi 500, nhưng vi phạm tính toàn vẹn tham chiếu dữ liệu.
7. **Bằng chứng:** `docs/evidence/G-am-tinh-lan1.log`, `G-am-tinh-lan1.xml`, `G-am-tinh-lan2.log`, `G-am-tinh-lan2.xml`.
8. **Test bị ảnh hưởng:** `test_kh_n4_recipe_id_khong_ton_tai`, `test_ms_n4_food_id_khong_ton_tai`.
