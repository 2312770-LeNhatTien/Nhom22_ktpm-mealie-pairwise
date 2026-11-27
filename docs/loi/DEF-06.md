# DEF-06: recipeId và foodId không tồn tại vẫn được lưu

1. **Luồng và test phát hiện:** Kế hoạch bữa ăn và Danh sách mua sắm, `tests/test_am_tinh.py::test_kh_n4_recipe_id_khong_ton_tai` và `test_ms_n4_food_id_khong_ton_tai`.
2. **Môi trường:** Mealie v3.28.0 chạy bằng Docker (SQLite); Python 3.12/3.13; pytest 9.x.
3. **Cách tái hiện:**
   - Kế hoạch bữa ăn: Gửi `POST /api/households/mealplans` với `recipeId` là một UUID ngẫu nhiên không tồn tại.
   - Danh sách mua sắm: Gửi `POST /api/households/shopping/items` với `foodId` là một UUID ngẫu nhiên không tồn tại.
4. **Mong đợi:** Trả về mã lỗi 4xx (404 Not Found hoặc 422 Unprocessable Entity), từ chối lưu vì khóa ngoại không tồn tại.
   **Thực tế:** Cả hai API đều trả về mã 201 Created và lưu thành công mục với ID khóa ngoại giả.
5. **Nguyên nhân (file và hàm trong mã Mealie v3.28.0):**
   - Kế hoạch bữa ăn: `mealie/db/models/household/mealplan.py` — cột `recipe_id` được khai báo `ForeignKey("recipes.id")` nhưng SQLite mặc định không bật kiểm tra khóa ngoại (`PRAGMA foreign_keys = OFF`), nên bản ghi mồ côi vẫn được ghi vào DB mà không có lỗi.
   - Danh sách mua sắm: `mealie/schema/household/group_shopping_list.py` — class `ShoppingListItemBase`, trường `food_id: UUID4 | None = None` không được kiểm tra sự tồn tại trước khi lưu (không có truy vấn tồn tại ở service hay controller).
6. **Mức độ:** Thấp — API không phát sinh lỗi 500, nhưng vi phạm tính toàn vẹn tham chiếu dữ liệu.
7. **Bằng chứng:** `docs/evidence/G-am-tinh-lan1.log`, `G-am-tinh-lan1.xml`, `G-am-tinh-lan2.log`, `G-am-tinh-lan2.xml`.
8. **Test bị ảnh hưởng:** `test_kh_n4_recipe_id_khong_ton_tai`, `test_ms_n4_food_id_khong_ton_tai`.
