# MỤC D: KẾ HOẠCH ÁP DỤNG KỸ THUẬT KIỂM THỬ PAIRWISE (COMBINATORIAL TESTING)

**Người phụ trách:** Bùi Ngọc Toàn (MSSV: 2312776 - TV4)  
**Đề tài:** R02 Mealie + K06 Combinatorial/Pairwise Testing  
**Hệ thống kiểm thử:** Mealie v3.28.0 (Commit SHA: `0552eaa4a80031b8572849cca0ed95d07f1be001`)  
**Công cụ sinh ca kiểm thử:** Microsoft PICT (Pairwise Independent Combinatorial Testing)

---

## D.1. NGUYÊN LÝ KỸ THUẬT PAIRWISE TESTING

### 1. Cơ sở lý thuyết và bản chất khoa học
- **Khái niệm:** Kiểm thử tổ hợp từng cặp (Pairwise Testing / 2-way Combinatorial Testing) là phương pháp thiết kế ca kiểm thử hộp đen dựa trên nguyên lý: phần lớn lỗi phần mềm trong thực tế phát sinh do tương tác giữa một tham số đơn lẻ hoặc do sự tương tác giữa một cặp 2 tham số với nhau.
- **Cơ sở thực nghiệm (Nghiên cứu của NIST & D. Richard Kuhn):** Các nghiên cứu thực nghiệm quy mô lớn của Viện Tiêu chuẩn và Công nghệ Quốc gia Hoa Kỳ (NIST) trên nhiều hệ thống phần mềm thực tế chỉ ra rằng:
  - Khoảng **67% - 93%** khiếm khuyết được kích hoạt bởi tương tác của tối đa 2 tham số.
  - Trên **90%** khiếm khuyết được kích hoạt bởi tối đa 3 tham số.
  - Rất hiếm khiếm khuyết (dưới 1%) đòi hỏi sự tương tác đồng thời của 4 tham số trở lên để bộc lộ.
- **Bài toán bùng nổ tổ hợp (Combinatorial Explosion):** Khi một hệ thống hoặc API có $N$ tham số, mỗi tham số có $V_i$ giá trị khả dĩ, phương pháp vét cạn (Exhaustive Testing) đòi hỏi không gian thử nghiệm là $\prod_{i=1}^N V_i$. Với các chức năng như Cấu hình Mealie (9 tham số) hay Tìm kiếm Mealie (9 tham số), số lượng tổ hợp vét cạn lên đến hàng nghìn tới hàng triệu ca thử nghiệm, hoàn toàn bất khả thi để thực thi thủ công hoặc tự động trong chu kỳ release ngắn.
- **Mục tiêu của Pairwise:** Chọn ra một tập con nhỏ nhất các ca kiểm thử sao cho **mọi cặp giá trị $(P_i = v_a, P_j = v_b)$ của hai tham số bất kỳ đều xuất hiện cùng nhau ít nhất một lần** trong tập test case. Nhờ đó, số lượng test case giảm từ 90% đến hơn 99% trong khi vẫn giữ được khả năng phát hiện phần lớn lỗi.

### 2. Ví dụ trực quan: Giảm từ 18 tổ hợp xuống 9 tổ hợp
Xét chức năng sắp xếp và phân trang danh sách công thức Mealie với 3 tham số:
- `orderBy`: 3 giá trị (`name`, `created_at`, `random`)
- `orderDirection`: 2 giá trị (`asc`, `desc`)
- `perPage`: 3 giá trị (`1`, `10`, `50`)

- **Không gian vét cạn (Exhaustive):** $3 \times 2 \times 3 = 18$ ca thử nghiệm.
- **Tổng số cặp cần phủ (Pairs):**
  - Cặp (`orderBy`, `orderDirection`): $3 \times 2 = 6$ cặp.
  - Cặp (`orderBy`, `perPage`): $3 \times 3 = 9$ cặp.
  - Cặp (`orderDirection`, `perPage`): $2 \times 3 = 6$ cặp.
  - $\rightarrow$ Tổng cộng có $6 + 9 + 6 = 21$ cặp giá trị duy nhất cần phủ.
- **Bộ 9 test case do PICT sinh ra phủ trọn vẹn 100% (21/21 cặp):**

| # | orderBy | orderDirection | perPage | Các cặp mới được phủ |
|:---:|:---|:---:|:---:|:---|
| 1 | random | asc | 1 | (random, asc), (random, 1), (asc, 1) |
| 2 | created_at | asc | 50 | (created_at, asc), (created_at, 50), (asc, 50) |
| 3 | name | desc | 1 | (name, desc), (name, 1), (desc, 1) |
| 4 | name | asc | 10 | (name, asc), (name, 10), (asc, 10) |
| 5 | created_at | desc | 1 | (created_at, desc), (created_at, 1) |
| 6 | name | desc | 50 | (name, 50), (desc, 50) |
| 7 | created_at | desc | 10 | (created_at, 10), (desc, 10) |
| 8 | random | desc | 10 | (random, desc), (random, 10) |
| 9 | random | asc | 50 | (random, 50) |

*Kết quả:* Tiết kiệm 50% số test case so với vét cạn mà vẫn đảm bảo mọi cặp giá trị tương tác đều được kiểm thử.

---

## D.2. LÝ DO CHỌN PHẠM VI KIỂM THỬ TRÊN MEALIE

Nhóm giới hạn phạm vi kiểm thử vào **3 luồng nghiệp vụ cốt lõi** thuộc các tầng API của Mealie v3.28.0 thay vì kiểm thử toàn bộ hệ thống:

| STT | Luồng nghiệp vụ | Endpoint API | Số tham số | Số case Exhaustive | Số case Pairwise (PICT) | Tỷ lệ giảm |
|:---:|:---|:---|:---:|:---:|:---:|:---:|
| 1 | **Cấu hình Household (Household Preferences)** | `PUT /api/households/preferences` | 9 | 1.792 | **16** | **99,1%** |
| 2 | **Tìm kiếm và Lọc công thức (Recipe Search & Filter)** | `GET /api/recipes` | 9 (có 1 ràng buộc) | 5.832 | **19** | **99,7%** |
| 3 | **Phân quyền người dùng (User Permissions)** | `POST /api/admin/users` & Action APIs | 6 | 192 | **14** | **92,7%** |

### Phân tích chi tiết từng luồng:
1. **Luồng 1: Cấu hình Household (`household_preferences`)**
   - Định nghĩa trong: `mealie/schema/household/household_preferences.py`.
   - Gồm 8 cờ boolean (`privateHousehold`, `showAnnouncements`, `lockRecipeEditsFromOtherHouseholds`, `recipePublic`, `recipeShowNutrition`, `recipeShowAssets`, `recipeLandscapeView`, `recipeDisableComments`) và 1 tham số số nguyên `firstDayOfWeek` (7 giá trị: 0-6).
   - Vét cạn: $2^8 \times 7 = 1.792$ tổ hợp. Pairwise rút gọn xuống **16 case** (giảm 99,1%).
   - *Lý do chọn:* Các cờ cấu hình household quyết định giá trị mặc định cho toàn bộ công thức mới được tạo ra trong household đó. Đây là nơi kiểm thử lý tưởng cho việc gán cấu hình mặc định (default inheritance).

2. **Luồng 2: Tìm kiếm và Lọc công thức (`recipe_search_and_filter`)**
   - Định nghĩa trong: `mealie/schema/response/pagination.py` và hàm `get_all` tại `mealie/routes/recipe/recipe_crud_routes.py`.
   - Gồm 9 tham số: từ khóa tìm kiếm (`search`), danh mục (`categories`), thẻ (`tags`), logic giao/hợp (`requireAllCategories`, `requireAllTags`), tiêu chí sắp xếp (`orderBy`), hướng sắp xếp (`orderDirection`), seed ngẫu nhiên (`paginationSeed`), số lượng trang (`perPage`).
   - Có ràng buộc logic thực tế (Constraint): Khi `orderBy = random`, Mealie bắt buộc phải có `paginationSeed` để kết quả phân trang ổn định.
   - Vét cạn: 5.832 tổ hợp hợp lệ. Pairwise rút gọn xuống **19 case** (giảm 99,7%).
   - *Lý do chọn:* Phức tạp về mặt logic truy vấn cơ sở dữ liệu (SQLAlchemy queries, JOIN, ORDER BY, OFFSET/LIMIT).

3. **Luồng 3: Phân quyền người dùng (`user_permissions`)**
   - Định nghĩa trong: `mealie/schema/user/user.py` và các controller phân quyền tại `mealie/routes/_base/checks.py`.
   - Gồm 5 cờ quyền hạn (`admin`, `canInvite`, `canManage`, `canManageHousehold`, `canOrganize`) và 1 biến hành động (`action` với 6 API nghiệp vụ).
   - Vét cạn: $2^5 \times 6 = 192$ tổ hợp. Pairwise rút gọn xuống **14 case** (giảm 92,7%).
   - *Lý do chọn:* Logic bảo mật có tính tương tác cao: khi user là `admin`, Mealie tự động cấp mọi quyền; khi user không phải admin, hành động chỉ thành công khi có cờ quyền tương ứng.

---

## D.3. CÁC GIẢ ĐỊNH KIỂM THỬ (ASSUMPTIONS)

1. **Giả định về cơ chế phát sinh lỗi:** Khiếm khuyết trong backend Mealie chủ yếu bắt nguồn từ xử lý sai một tham số đơn lẻ hoặc do xung đột logic giữa 2 tham số gửi lên cùng lúc.
2. **Tính đại diện của phân vùng tương đương (Equivalence Partitioning):**
   - Tham số dạng chuỗi hoặc mảng được rút gọn thành các nhãn đại diện:
     - `search`: `none` (chuỗi rỗng), `match` (từ khóa khớp 100% dữ liệu seed), `nomatch` (từ khóa không tồn tại).
     - `categories`, `tags`: `none`, `one` (chọn 1 phần tử), `two` (chọn 2 phần tử).
     - `paginationSeed`: `none`, `abc123`.
   - Giả định rằng mọi giá trị cụ thể trong cùng một lớp tương đương sẽ có cùng hành vi phản hồi từ hệ thống.
3. **Môi trường thử nghiệm đơn nhất và tất định:**
   - Phiên bản ứng dụng cố định: Mealie v3.28.0 chạy trên Docker Container cổng 9925.
   - Cơ sở dữ liệu: SQLite mặc định của Mealie.
   - Dữ liệu mẫu (Seed Data) do TV2 khởi tạo là cố định và không bị thay đổi ngẫu nhiên giữa các lần test.

---

## D.4. RỦI RO, GIỚI HẠN VÀ BIỆN PHÁP GIẢM THIỂU

| STT | Rủi ro / Giới hạn | Hậu quả tiềm ẩn | Biện pháp giảm thiểu của nhóm |
|:---:|:---|:---|:---|
| 1 | **Bỏ sót lỗi tương tác từ 3 tham số trở lên (Higher-order Interactions)** | Nếu có bug chỉ xuất hiện khi 3 hoặc 4 tham số cùng có giá trị đặc thù, Pairwise (2-way) sẽ bỏ sót. | - Thực hiện chạy bộ **3-wise (53 case)** và **Exhaustive (1.792 case)** đối chứng cho Luồng Cấu hình Household.<br>- Lập bảng đối sánh tỷ lệ bắt lỗi giữa Pairwise, 3-wise và Exhaustive sau giữa kỳ. |
| 2 | **Chọn sai giá trị đại diện cho phân vùng** | Nếu bug chỉ phát sinh tại một ký tự đặc biệt hoặc giá trị biên cực đại mà không được đưa vào model, test sẽ không bắt được. | - Bổ sung các ca kiểm thử âm (Negative Test) độc lập (ví dụ: gửi `orderBy=random` mà không có seed để kiểm tra lỗi 422). |
| 3 | **Khó khăn trong việc xác định Oracle (Kết quả mong đợi)** | Khi tham số ngẫu nhiên phối hợp, việc tính toán chính xác danh sách kết quả trả về bằng tay rất phức tạp. | - Sử dụng **Điều kiện bất biến (Invariants)** thay vì so khớp cứng kết quả: kiểm tra status code 200, số lượng $\le$ perPage, tất cả item trả về đều chứa tag/category đã chọn. |
| 4 | **Hiện tượng ô nhiễm trạng thái (State Pollution)** | Các ca kiểm thử tạo dữ liệu hoặc cập nhật cấu hình có thể làm sai lệch kết quả của các ca kiểm thử kế tiếp. | - Mỗi test case tạo công thức với tên định danh độc nhất (kèm timestamp/UUID).<br>- Hỗ trợ script reset/dựng lại môi trường nhanh chóng. |

---

## D.5. TIÊU CHÍ ĐÁNH GIÁ (PASS / FAIL & ACCEPTANCE CRITERIA)

### 1. Tiêu chí Pass / Fail của từng ca kiểm thử:
Một ca kiểm thử được đánh giá là **PASS** khi đáp ứng đủ các điều kiện sau:
- **HTTP Status Code:** Trả về chính xác mã trạng thái theo thiết kế (200 OK cho truy vấn/cập nhật hợp lệ; 201 Created cho tạo mới; 403 Forbidden cho hành động không đủ quyền; 422 Unprocessable Entity cho tham số sai quy cách).
- **Tính toàn vẹn dữ liệu (Data Integrity):** Dữ liệu trả về hoặc dữ liệu được lưu trong cơ sở dữ liệu phản ánh chính xác cấu hình đã gửi lên.
- **Tính bất biến nghiệp vụ (Business Invariants):**
  - Luồng Household: 5 giá trị cài đặt (`public`, `showNutrition`, `showAssets`, `landscapeView`, `disableComments`) của công thức mới tạo phải khớp hoàn toàn với cấu hình household tương ứng.
  - Luồng Search: Danh sách công thức thỏa mãn đúng bộ lọc và chiều sắp xếp đã yêu cầu.
  - Luồng Permission: Không phát sinh truy cập trái phép hoặc leo thang đặc quyền.

Một ca kiểm thử bị đánh giá là **FAIL** khi:
- HTTP Status Code trả về khác với mong đợi.
- Dữ liệu trả về vi phạm các điều kiện bất biến nghiệp vụ.
- Phát sinh lỗi máy chủ 500 (Internal Server Error).

### 2. Tiêu chí độ phủ (Coverage Criterion):
- Đạt **100% độ phủ cặp 2 tham số (100% 2-way Combinatorial Coverage)** trên toàn bộ không gian giá trị hợp lệ của từng model PICT, được xác thực thông qua lệnh `pict <model_file> /s`.

### 3. Tiêu chí nghiệm thu đợt kiểm thử (Test Run Acceptance):
- Toàn bộ các ca kiểm thử Pairwise được thực thi tự động qua test script, không có can thiệp thủ công.
- Mọi ca kiểm thử FAIL đều phải trải qua quy trình phân tích nguyên nhân gốc rễ (Root Cause Analysis - RCA) và phân loại chính xác thành:
  1. *Lỗi hệ thống Mealie (System Bug)*.
  2. *Lỗi kịch bản kiểm thử (Test Script / Oracle Error)*.
  3. *Lỗi dữ liệu mẫu / môi trường (Environment / Seed Data Issue)*.
