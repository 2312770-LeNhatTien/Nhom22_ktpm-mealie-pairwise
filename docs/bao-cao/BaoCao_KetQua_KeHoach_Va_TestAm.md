# Báo cáo kết quả kiểm thử luồng Kế hoạch bữa ăn và 18 ca âm tính

**Nhóm 22 — Kiểm thử phần mềm (Đề tài: R02 Mealie v3.28.0 + K06 Pairwise Microsoft PICT)**  
**Người thực hiện:** Hồ Quốc Tiến (MSSV: 2312769)  
**Thẻ việc:** CK-18, CK-19  
**Ngày hoàn thành:** 26/11/2026  

---

## 1. Tóm tắt kết luận (Executive Summary)

1. **Luồng Kế hoạch bữa ăn (Mealplan):** Đã kiểm thử tự động trên Mealie v3.28.0 qua đầy đủ 3 mức độ phủ:
   - 2-wise (Pairwise, 16 ca: `M01` .. `M16`)
   - 3-wise (48 ca: `M01` .. `M48`)
   - Thử hết toàn bộ tổ hợp (96 ca: `M001` .. `M096`)  
   **Kết quả:** 100% ca kiểm thử đều **ĐẠT (PASSED)**. Tất cả các bất biến cốt lõi **I1** (không lỗi 500), **I2** (mã HTTP tạo 201, đọc 200), **I3** (toàn vẹn dữ liệu tạo/đọc lại) và **I5** (xóa dữ liệu sạch trong khối `try ... finally`) đều được bảo đảm.

2. **Bộ 18 test âm tính và giá trị biên (Negative Tests):** Đã chuyển đổi từ script chạy thử sang bộ kiểm thử chuẩn `pytest` (`tests/test_am_tinh.py`).
   - **8 ca ĐẠT:** Mealie từ chối hợp lệ bằng mã `4xx` (400 hoặc 422).
   - **10 ca KHÁC MONG ĐỢI:** Phát hiện 10 lỗi thật của Mealie v3.28.0 (4 ca ném lỗi 500, 6 ca chấp nhận và lưu dữ liệu sai với mã 200/201). Cả 10 ca đã được đánh dấu `@pytest.mark.xfail(strict=False)` theo đúng cơ chế kiểm thử hồi quy (mục 5.6 tài liệu hướng dẫn), giúp CI GitHub Actions luôn đạt trạng thái **XANH (PASS 100%)**.

3. **Phân tích nguyên nhân lỗi DEF-01 (CK-14):** Đã xác định rõ file và hàm gây lỗi trong mã nguồn Mealie v3.28.0 (`repository_recipes.py` và `repository_generic.py`), giải thích chi tiết cơ chế sắp xếp mã điểm Unicode Code Point trong hệ CSDL.

---

## 2. Kết quả kiểm thử luồng Kế hoạch bữa ăn (CK-06, CK-12)

### 2.1. Mục tiêu và phạm vi
- **API kiểm thử:** 
  - `POST /api/households/mealplans`: Tạo mục kế hoạch bữa ăn theo ngày.
  - `GET /api/households/mealplans?start_date={d}&end_date={d}`: Đọc lại dữ liệu theo ngày để đối chiếu.
  - `DELETE /api/households/mealplans/{id}`: Xóa mục kế hoạch và kiểm tra lại không còn (I5).
- **Mô hình tham số (4 yếu tố):**
  - `entryType`: breakfast, lunch, dinner, side (4 giá trị)
  - `date`: past, today, future (3 giá trị)
  - `content`: recipe, title_short, title_accented, recipe_and_title (4 giá trị)
  - `text`: none, note (2 giá trị)

### 2.2. Bảng kết quả thực thi

| Mức kiểm thử | File dữ liệu case | Tổng số ca | Đạt (PASS) | Lỗi (FAIL) | Tỷ lệ đạt |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **2-wise (Pairwise)** | `cases/mealplan.o2.tsv` | 16 | 16 | 0 | **100%** |
| **3-wise** | `cases/mealplan.o3.tsv` | 48 | 48 | 0 | **100%** |
| **Thử hết (All)** | `cases/mealplan.all.tsv` | 96 | 96 | 0 | **100%** |
| **Tổng cộng** | **Tất cả các mức** | **160** | **160** | **0** | **100%** |

---

## 3. Kết quả 18 test dữ liệu sai và giá trị biên (CK-08)

Quy tắc kỳ vọng: Dữ liệu sai phạm vi hoặc giá trị biên phải bị từ chối bằng mã `4xx`, không được gây lỗi máy chủ 500 và không được lưu dữ liệu sai lệch.

| Mã ca | Luồng | Mô tả ca kiểm thử | Kết quả thực tế Mealie v3.28.0 | Phân loại |
| :---: | :--- | :--- | :--- | :---: |
| **CT-N1** | Công thức | Tạo công thức tên rỗng `""` | Trả mã 500 (`AssertionError` trong `validate_name`) | **Lỗi thật (XFAIL)** |
| **CT-N2** | Công thức | Sửa tên công thức thành rỗng qua PATCH | Trả mã 500 | **Lỗi thật (XFAIL)** |
| **CT-N3** | Công thức | Số khẩu phần âm (`recipeServings: -5`) | Trả mã 200, lưu khẩu phần = `-5.0` | **Lỗi thật (XFAIL)** |
| **CT-N4** | Công thức | Số khẩu phần là chuỗi chữ (`"abc"`) | Từ chối bằng mã 422 Unprocessable Entity | **Đạt** |
| **CT-N5** | Công thức | Tên chỉ toàn dấu cách (`"   "`) | Từ chối bằng mã 422 Unprocessable Entity | **Đạt** |
| **TK-N1** | Tìm kiếm | Lọc category không tồn tại | Trả mã 200, hiển thị toàn bộ 12 công thức | **Lỗi thật (XFAIL)** |
| **TK-N2** | Tìm kiếm | Tên tham số sai kiểu chữ (`require_all_categories`) | FastAPI bỏ qua tham số lạ, lọc theo mặc định (OR) | **Đạt (FastAPI)** |
| **TK-N3** | Tìm kiếm | `orderBy=random` không có `paginationSeed` | Từ chối bằng mã 400 Bad Request | **Đạt** |
| **TK-N4** | Tìm kiếm | `perPage = -1` | Trả toàn bộ công thức theo thiết kế của Mealie | **Đạt** |
| **KH-N1** | Kế hoạch | `entryType` không hợp lệ (`"brunch"`) | Từ chối bằng mã 422 Unprocessable Entity | **Đạt** |
| **KH-N2** | Kế hoạch | Ngày không tồn tại (`"2026-13-45"`) | Từ chối bằng mã 422 Unprocessable Entity | **Đạt** |
| **KH-N3** | Kế hoạch | Không có tiêu đề và không có `recipeId` | Từ chối bằng mã 422 Unprocessable Entity | **Đạt** |
| **KH-N4** | Kế hoạch | `recipeId` không tồn tại (UUID ngẫu nhiên) | Trả mã 201 Created, vẫn lưu `recipeId` giả | **Lỗi thật (XFAIL)** |
| **MS-N1** | Mua sắm | `shoppingListId` không tồn tại | Trả mã 500 (`ValidationError` khi lưu) | **Lỗi thật (XFAIL)** |
| **MS-N2** | Mua sắm | Số lượng âm (`quantity: -3`) | Trả mã 201 Created, lưu số lượng `-3` | **Lỗi thật (XFAIL)** |
| **MS-N3** | Mua sắm | Số lượng âm lẻ (`quantity: -0.5`) | Trả mã 500 (`KeyError '-'` trong `display_fraction`) | **Lỗi thật (XFAIL)** |
| **MS-N4** | Mua sắm | `foodId` không tồn tại | Trả mã 201 Created, vẫn lưu `foodId` giả | **Lỗi thật (XFAIL)** |
| **MS-N5** | Mua sắm | Tạo danh sách mua sắm tên rỗng `""` | Trả mã 201 Created, tạo danh sách tên rỗng | **Lỗi thật (XFAIL)** |

**Tổng hợp:** 8 ca Đạt mong đợi, 10 ca phát hiện lỗi thật (được bảo vệ bằng `XFAIL` trong kiểm thử hồi quy).

---

## 4. Đối chiếu số liệu thiết kế và thực thi (CK-19)

Đối chiếu số lượng ca kiểm thử giữa **Báo cáo giữa kỳ** (thiết kế bằng PICT) và **Báo cáo cuối kỳ** (thực thi kiểm thử bằng pytest):

- **Kế hoạch bữa ăn:**
  - Thiết kế 2-wise: 16 ca ➔ Thực thi pytest: đúng 16 ca (**Khớp 100%**).
  - Thiết kế 3-wise: 48 ca ➔ Thực thi pytest: đúng 48 ca (**Khớp 100%**).
  - Thiết kế thử hết: 96 ca ➔ Thực thi pytest: đúng 96 ca (**Khớp 100%**).
- **Kiểm thử âm tính toàn hệ thống:**
  - Thiết kế giữa kỳ: 18 ca ➔ Thực thi pytest: đúng 18 ca (**Khớp 100%**).
- **Kết luận:** Số liệu thực tế trong mã kiểm thử khớp hoàn toàn 100% với tài liệu thiết kế giữa kỳ, không có bất kỳ sai lệch nào.

---

## 5. Nguyên nhân gốc lỗi DEF-01 (CK-14)

- **Mã lỗi:** DEF-01 (Mức độ: Thấp)
- **Tên lỗi:** Sắp xếp tên công thức không theo alphabet tiếng Việt.
- **Nguyên nhân trong mã nguồn Mealie v3.28.0:**
  Trong `mealie/repos/repository_recipes.py` và `mealie/repos/repository_generic.py`, khi xử lý tham số `orderBy=name`, truy vấn SQLAlchemy gọi thẳng `.order_by(RecipeModel.name.asc())` trên cơ sở dữ liệu mà không cấu hình Collation tiếng Việt (như `COLLATE "vi_VN"`). CSDL so sánh chuỗi theo mã điểm nhị phân Unicode (Code Point). Ký tự có dấu `'à'` (`U+00E0`, mã 224) có giá trị mã lớn hơn chữ cái ASCII `'h'` (`U+0068`, mã 104), dẫn đến kết quả *"Chè đậu"* bị xếp trước *"Cà phê sữa"*.
