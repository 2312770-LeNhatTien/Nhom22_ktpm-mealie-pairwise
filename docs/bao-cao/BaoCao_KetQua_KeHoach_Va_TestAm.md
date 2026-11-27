# Báo cáo kết quả kiểm thử luồng Kế hoạch bữa ăn và 18 ca âm tính

**Nhóm 22 — Kiểm thử phần mềm (Đề tài: R02 Mealie v3.28.0 + K06 Pairwise Microsoft PICT)**  
**Người thực hiện:** Hồ Quốc Tiến (MSSV: 2312769)  
**Thẻ việc:** CK-18, CK-19  
**Ngày hoàn thành:** 27/11/2026  

---

## 1. Tóm tắt kết luận (Executive Summary)

1. **Luồng Kế hoạch bữa ăn (Mealplan):** Đã kiểm thử tự động trên Mealie v3.28.0 qua đầy đủ 3 mức độ phủ:
   - 2-wise (Pairwise, 16 ca: `M01` .. `M16`)
   - 3-wise (48 ca: `M01` .. `M48`)
   - Thử hết toàn bộ tổ hợp (96 ca: `M001` .. `M096`)  
   **Kết quả:** 100% ca kiểm thử đều **ĐẠT (PASSED)**. Tất cả các bất biến cốt lõi **I1** (không lỗi 500), **I2** (mã HTTP tạo 201, đọc 200), **I3** (toàn vẹn dữ liệu tạo/đọc lại) và **I5** (xóa dữ liệu sạch trong khối `try ... finally`) đều được bảo đảm.

2. **Bộ 18 test âm tính và giá trị biên (Negative Tests):** Đã chuyển đổi từ script chạy thử sang bộ kiểm thử chuẩn `pytest` (`tests/test_am_tinh.py`) với cơ chế quản lý lỗi tập trung tại `tests/loi_da_bao.py`:
   - **8 ca ĐẠT:** Mealie từ chối hợp lệ bằng mã `4xx` (400 hoặc 422).
   - **9 ca LỖI THẬT (DEF-02 đến DEF-07):** Phát hiện 9 ca lỗi thật (lỗi 500 máy chủ hoặc chấp nhận lưu dữ liệu sai với mã 200/201). Cả 9 ca đều được gắn mã lỗi chính xác trong `tests/loi_da_bao.py`.
   - **1 ca HÀNH VI CẦN BIẾT (TK-N1):** Lọc category không tồn tại trả về toàn bộ 12 công thức do cơ chế query builder không thêm điều kiện lọc.
   - Nhờ cơ chế `LOI_DA_BAO` và `pytest_collection_modifyitems`, toàn bộ các ca lỗi được gắn `xfail`, giúp CI GitHub Actions luôn đạt trạng thái **XANH (PASS 100%)**.

3. **Phân tích nguyên nhân lỗi DEF-01 đến DEF-07 và Hành vi cần biết:** Đã xác định rõ file và hàm gây lỗi trong mã nguồn Mealie v3.28.0, hoàn thiện đầy đủ phiếu lỗi chi tiết trong thư mục `docs/loi/`.

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

| Mã ca | Luồng | Mô tả ca kiểm thử | Kết quả thực tế Mealie v3.28.0 | Phân loại & Mã DEF |
| :---: | :--- | :--- | :--- | :---: |
| **CT-N1** | Công thức | Tạo công thức tên rỗng `""` | Trả mã 500 (`AssertionError` trong `validate_name`) | **DEF-02 (XFAIL)** |
| **CT-N2** | Công thức | Sửa tên công thức thành rỗng qua PATCH | Trả mã 500 | **DEF-02 (XFAIL)** |
| **CT-N3** | Công thức | Số khẩu phần âm (`recipeServings: -5`) | Trả mã 200, lưu khẩu phần = `-5.0` | **DEF-05 (XFAIL)** |
| **CT-N4** | Công thức | Số khẩu phần là chuỗi chữ (`"abc"`) | Từ chối bằng mã 422 Unprocessable Entity | **Đạt** |
| **CT-N5** | Công thức | Tên chỉ toàn dấu cách (`"   "`) | Từ chối bằng mã 422 Unprocessable Entity | **Đạt** |
| **TK-N1** | Tìm kiếm | Lọc category không tồn tại | Trả mã 200, hiển thị toàn bộ 12 công thức | **Hành vi cần biết (XFAIL)** |
| **TK-N2** | Tìm kiếm | Tên tham số sai kiểu chữ (`require_all_categories`) | FastAPI bỏ qua tham số lạ, lọc theo mặc định (OR) | **Đạt (FastAPI)** |
| **TK-N3** | Tìm kiếm | `orderBy=random` không có `paginationSeed` | Từ chối bằng mã 400 Bad Request | **Đạt** |
| **TK-N4** | Tìm kiếm | `perPage = -1` | Trả toàn bộ công thức theo thiết kế của Mealie | **Đạt** |
| **KH-N1** | Kế hoạch | `entryType` không hợp lệ (`"brunch"`) | Từ chối bằng mã 422 Unprocessable Entity | **Đạt** |
| **KH-N2** | Kế hoạch | Ngày không tồn tại (`"2026-13-45"`) | Từ chối bằng mã 422 Unprocessable Entity | **Đạt** |
| **KH-N3** | Kế hoạch | Không có tiêu đề và không có `recipeId` | Từ chối bằng mã 422 Unprocessable Entity | **Đạt** |
| **KH-N4** | Kế hoạch | `recipeId` không tồn tại (UUID ngẫu nhiên) | Trả mã 201 Created, vẫn lưu `recipeId` giả | **DEF-06 (XFAIL)** |
| **MS-N1** | Mua sắm | `shoppingListId` không tồn tại | Trả mã 500 (`ValidationError` khi lưu) | **DEF-03 (XFAIL)** |
| **MS-N2** | Mua sắm | Số lượng âm (`quantity: -3`) | Trả mã 201 Created, lưu số lượng `-3` | **DEF-04 (XFAIL)** |
| **MS-N3** | Mua sắm | Số lượng âm lẻ (`quantity: -0.5`) | Trả mã 500 (`KeyError '-'` trong `display_fraction`) | **DEF-04 (XFAIL)** |
| **MS-N4** | Mua sắm | `foodId` không tồn tại | Trả mã 201 Created, vẫn lưu `foodId` giả | **DEF-06 (XFAIL)** |
| **MS-N5** | Mua sắm | Tạo danh sách mua sắm tên rỗng `""` | Trả mã 201 Created, tạo danh sách tên rỗng | **DEF-07 (XFAIL)** |

**Tổng hợp:** 8 ca Đạt mong đợi, 9 ca Lỗi thật (DEF-02 đến DEF-07), 1 ca Hành vi cần biết (TK-N1).

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

## 5. Danh sách lỗi phần mềm ghi nhận (DEF-01 đến DEF-07) và Hành vi cần biết

### 5.1. Bảng tổng hợp lỗi

| Mã lỗi | Tên lỗi | Luồng / Ca test | Mức độ | Trạng thái |
| :---: | :--- | :---: | :---: | :---: |
| **DEF-01** | Sắp xếp tên công thức không theo alphabet tiếng Việt | Tìm kiếm (Sắp xếp) | Thấp | Đã lập phiếu |
| **DEF-02** | Tên công thức rỗng gây lỗi 500 | Công thức (CT-N1, CT-N2) | Trung bình | Đã lập phiếu |
| **DEF-03** | Thêm mục mua sắm vào danh sách không tồn tại gây lỗi 500 | Mua sắm (MS-N1) | Trung bình | Đã lập phiếu |
| **DEF-04** | Số lượng mua sắm âm (-3 lưu 201, -0.5 lỗi 500) | Mua sắm (MS-N2, MS-N3) | Trung bình | Đã lập phiếu |
| **DEF-05** | Số khẩu phần âm vẫn được lưu | Công thức (CT-N3) | Thấp | Đã lập phiếu |
| **DEF-06** | recipeId / foodId không tồn tại vẫn được lưu | Kế hoạch, Mua sắm (KH-N4, MS-N4) | Thấp | Đã lập phiếu |
| **DEF-07** | Tạo danh sách mua sắm tên rỗng vẫn được lưu | Mua sắm (MS-N5) | Thấp | Đã lập phiếu |

---

### 5.2. Phân tích nguyên nhân chi tiết trong mã nguồn Mealie v3.28.0

#### DEF-01: Sắp xếp tên công thức không theo alphabet tiếng Việt (Thấp)
- **File & Hàm:** `mealie/repos/repository_generic.py` -> `QueryFilterBuilder.get_order_attr` trong `mealie/services/query_filter/builder.py` -> `_transform_model_attr`.
- **Nguyên nhân:** Khi xử lý `orderBy=name`, hàm `_transform_model_attr` bọc cột tên bằng `func.lower()`. Do Mealie mặc định chạy SQLite và không cấu hình collation tiếng Việt, SQLite thực hiện so sánh theo mã điểm Unicode nhị phân (Code Point). Ký tự có dấu `'à'` (`U+00E0` = 224) có mã lớn hơn chữ cái ASCII `'h'` (`U+0068` = 104), dẫn đến *"Chè đậu"* bị xếp trước *"Cà phê sữa"*.

#### DEF-02: Tên công thức rỗng gây lỗi 500 (Trung bình)
- **File & Hàm:** `mealie/schema/recipe/recipe.py` — hàm `create_recipe_slug()`: trường `name: str` trong class `CreateRecipe` không có ràng buộc `min_length=1`; khi `slugify(name)` trả về chuỗi rỗng, hàm ném `SlugError` chưa được bắt ở route, khiến FastAPI trả về mã 500.
- **Nguyên nhân:** Thiếu ràng buộc `min_length=1` trên trường `name` và chưa có xử lý `SlugError` trong route handler. Khi tên rỗng, `slugify("")` trả về chuỗi rỗng → `SlugError` không được bắt → HTTP 500 thay vì 422.

#### DEF-03: Thêm mục mua sắm vào danh sách không tồn tại gây lỗi 500 (Trung bình)
- **File & Hàm:** `mealie/routes/households/controller_shopping_lists.py` — hàm `create_one()` → gọi service; `mealie/services/household_services/shopping_lists.py` — hàm `bulk_create_items()`: không kiểm tra sự tồn tại của `shoppingListId` trước khi lưu, ngoại lệ DB không được bắt ở controller.
- **Nguyên nhân:** Service không kiểm tra sự tồn tại của `shoppingListId` trước khi tạo item. Khi lưu vào CSDL, DB ném lỗi vi phạm toàn vẹn dữ liệu, ngoại lệ truyền lên controller mà không được bắt, dẫn đến HTTP 500 thay vì 404 Not Found.

#### DEF-04: Số lượng mua sắm âm (-3 lưu 201, -0.5 lỗi 500) (Trung bình)
- **File & Hàm:** `mealie/schema/household/group_shopping_list.py` — class `ShoppingListItemBase`, trường `quantity: float = 1` không có ràng buộc `ge=0`; `mealie/schema/recipe/recipe_ingredient.py` — hàm `display_fraction()` (dòng ~30–35): dùng dict `SUPERSCRIPT` tra từng ký tự, gây `KeyError: '-'` với số âm.
- **Nguyên nhân:** Trường `quantity` không có ràng buộc giá trị không âm (`ge=0`), cho phép `-3` lưu thành công vào CSDL. Khi số lượng là số âm lẻ (`-0.5`), hàm `display_fraction` trong `recipe_ingredient.py` tra dict `SUPERSCRIPT` gặp ký tự `'-'` không có trong dict → `KeyError: '-'` không được bắt → HTTP 500.

#### DEF-05: Số khẩu phần âm vẫn được lưu (Thấp)
- **File & Hàm:** `mealie/schema/recipe/recipe.py` — class `RecipeSummary`, trường `recipe_servings: float = 0` không có ràng buộc `ge=0`.
- **Nguyên nhân:** Schema `RecipeSummary` định nghĩa `recipe_servings: float = 0` nhưng không khai báo điều kiện `ge=0`. Khi gửi `PATCH` với `recipeServings: -5`, Mealie chấp nhận cập nhật và trả về HTTP 200, lưu trữ giá trị `-5.0` phi thực tế vào CSDL.

#### DEF-06: recipeId / foodId không tồn tại vẫn được lưu (Thấp)
- **File & Hàm:** `mealie/db/models/household/mealplan.py` — cột `recipe_id` có `ForeignKey("recipes.id")` nhưng SQLite mặc định không bật kiểm tra khóa ngoại (`PRAGMA foreign_keys = OFF`); `mealie/schema/household/group_shopping_list.py` — class `ShoppingListItemBase`, trường `food_id: UUID4 | None = None` không được kiểm tra sự tồn tại trước khi lưu.
- **Nguyên nhân:** SQLite không bật kiểm tra khóa ngoại theo mặc định, nên dù FK được khai báo trong model, bản ghi mồ côi vẫn được ghi vào DB. Tầng service cũng không có truy vấn kiểm tra tồn tại `foodId` trước khi lưu.

#### DEF-07: Tạo danh sách mua sắm tên rỗng vẫn được lưu (Thấp)
- **File & Hàm:** `mealie/schema/household/group_shopping_list.py` — class `ShoppingListCreate`, trường `name: str | None = None` không có ràng buộc `min_length=1` hay validator kiểm tra chuỗi rỗng/khoảng trắng.
- **Nguyên nhân:** Trường `name` kiểu `str | None = None` không có tham số `min_length=1`. Khi người dùng gửi chuỗi rỗng `""`, schema vẫn coi là hợp lệ và tạo bản ghi danh sách mua sắm không có tên trong CSDL với mã HTTP 201.

---

### 5.3. Hành vi cần biết: Lọc category không tồn tại trả về toàn bộ công thức (TK-N1)

- **File & Hàm:** `mealie/services/query_filter/builder.py`, `mealie/repos/repository_recipes.py`.
- **Mô tả hành vi:** Khi gửi request `GET /api/recipes?categories=khong-ton-tai`, API trả về mã HTTP 200 và danh sách chứa toàn bộ 12 công thức (`total = 12`) thay vì trả về danh sách rỗng (`total = 0`).
- **Bản chất kỹ thuật:** Trong QueryBuilder của Mealie, trước khi thêm điều kiện lọc theo category, hệ thống thực hiện truy vấn bảng `categories` theo slug/name truyền vào. Nếu không tìm thấy category nào khớp, QueryBuilder sẽ bỏ qua và không gắn mệnh đề `WHERE` vào câu truy vấn SQLAlchemy. Do đó, truy vấn SELECT thực thi lấy toàn bộ công thức. Đây là đặc tính xử lý mặc định của Query Builder trong thiết kế Mealie, nhóm ghi nhận là **Hành vi cần biết** để người dùng và bên tích hợp lưu ý.
