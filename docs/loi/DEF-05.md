# DEF-05: Số khẩu phần ăn âm vẫn được chấp nhận và lưu

1. **Luồng và test phát hiện:** Quản lý công thức, `tests/test_am_tinh.py::test_ct_n3_so_khau_phan_am`.
2. **Môi trường:** Mealie v3.28.0 chạy bằng Docker (SQLite); Python 3.13; pytest 9.2.0.
3. **Cách tái hiện:**
   Tạo một công thức mới, sau đó gửi `PATCH /api/recipes/{slug}` với nội dung:
   ```json
   {
     "recipeServings": -5
   }
   ```
   Đọc lại công thức qua `GET /api/recipes/{slug}`.
4. **Mong đợi:** Trả về mã lỗi 4xx (422 Unprocessable Entity), từ chối cập nhật số khẩu phần ăn âm.
   **Thực tế:** Mealie trả về mã 200 OK, và đọc lại thấy `recipeServings` được lưu là `-5.0`.
5. **Nguyên nhân (file và hàm trong mã Mealie v3.28.0):**
   - File: `mealie/schema/recipe/recipe.py` — class `RecipeSummary` (dòng 119), trường `recipe_servings: float = 0` (dòng 130) không có ràng buộc `ge=0` (greater than or equal 0). Pydantic không từ chối giá trị âm, nên mọi giá trị `float` đều được chấp nhận và truyền thẳng vào DB mà không qua bước kiểm tra ngữ nghĩa.
6. **Mức độ:** Thấp — không làm crash máy chủ (API trả mã 200), nhưng lưu trữ dữ liệu vô lý làm sai lệch hiển thị công thức trên giao diện.
7. **Bằng chứng:** `docs/evidence/G-am-tinh-lan1.log`, `G-am-tinh-lan1.xml`, `G-am-tinh-lan2.log`, `G-am-tinh-lan2.xml`.
8. **Test bị ảnh hưởng:** `test_ct_n3_so_khau_phan_am`.
