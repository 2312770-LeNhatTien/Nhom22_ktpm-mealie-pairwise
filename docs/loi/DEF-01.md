# DEF-01: Sắp xếp tên công thức không theo alphabet tiếng Việt

1. **Luồng và test phát hiện:** Tìm kiếm, `tests/test_tim_kiem.py::test_sap_xep_ten_theo_bang_chu_cai[asc]` và `[desc]`.
2. **Môi trường:** Mealie v3.28.0 chạy bằng Docker trên Ubuntu 24.04/WSL; dữ liệu seed sạch gồm 12 công thức. Docker client/engine 29.1.3; Docker Compose 2.40.3; Python 3.12.3; pytest 9.1.1.
3. **Cách tái hiện:** Đăng nhập bằng tài khoản test, nạp dữ liệu mẫu, rồi gửi:

   ```http
   GET /api/recipes?perPage=50&orderBy=name&orderDirection=asc
   ```

   Với seed hiện tại, kiểm tra vị trí của `Cà phê sữa` và `Chè đậu` trong `items`.

4. **Mong đợi:** Tên được xếp theo alphabet tiếng Việt, không phân biệt dấu; `Cà phê sữa` đứng trước `Chè đậu`.

   **Thực tế:** `Cà phê sữa` đứng sau `Chè đậu`. Chiều `desc` cho thứ tự đảo tương ứng.

5. **Nguyên nhân (file và hàm trong mã Mealie v3.28.0):**

6. **Mức độ:** Thấp — danh sách vẫn trả về đầy đủ và API không lỗi, nhưng thứ tự tên chưa phù hợp với cách đọc alphabet tiếng Việt.
7. **Bằng chứng:** `docs/evidence/G-tim-kiem-lan1.log`, `G-tim-kiem-lan1.xml`, `G-tim-kiem-lan2.log` và `G-tim-kiem-lan2.xml`.
8. **Test bị ảnh hưởng:** `test_sap_xep_ten_theo_bang_chu_cai[asc]`, `test_sap_xep_ten_theo_bang_chu_cai[desc]`.
