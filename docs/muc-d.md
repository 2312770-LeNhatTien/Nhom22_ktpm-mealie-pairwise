# MỤC D: KẾ HOẠCH ÁP DỤNG KỸ THUẬT KIỂM THỬ PAIRWISE (COMBINATORIAL TESTING)

**Người phụ trách:** Bùi Ngọc Toàn (MSSV: 2312776 - TV4)  
**Đề tài:** R02 Mealie + K06 Combinatorial/Pairwise Testing  
**Hệ thống kiểm thử:** Mealie v3.28.0 (Commit SHA: `0552eaa4a80031b8572849cca0ed95d07f1be001`)  
**Công cụ sinh ca kiểm thử:** Microsoft PICT (Pairwise Independent Combinatorial Testing)

---

## D.1. NGUYÊN LÝ KỸ THUẬT PAIRWISE TESTING

#### 1. Cơ sở lý thuyết và bản chất khoa học
- **Khái niệm:** Kiểm thử tổ hợp từng cặp (Pairwise Testing / 2-way Combinatorial Testing) là phương pháp thiết kế ca kiểm thử hộp đen dựa trên nguyên lý: phần lớn lỗi phần mềm trong thực tế phát sinh do tương tác giữa một tham số đơn lẻ hoặc do sự tương tác giữa một cặp 2 tham số với nhau.
- **Cơ sở thực nghiệm (nghiên cứu của NIST - D. Richard Kuhn và cộng sự):**
  Bài báo nền tảng của hướng nghiên cứu này là:
  > **D. R. Kuhn, D. R. Wallace, A. M. Gallo, Jr.** (2004), *"Software Fault Interactions and Implications for Software Testing"*, IEEE Transactions on Software Engineering, Vol. 30, No. 6, pp. 418–421. DOI: 10.1109/TSE.2004.24.

  Nhóm tác giả phân tích lỗi thật của nhiều loại hệ thống (thiết bị y tế, trình duyệt, máy chủ web, cơ sở dữ liệu phân tán của NASA) và thấy lỗi thường chỉ bị kích hoạt bởi một tổ hợp rất ít điều kiện. Chương trình nghiên cứu tổ hợp của NIST tổng kết: phần lớn lỗi do tương tác của **không quá 3 tham số**, tỷ lệ lỗi cần 4 đến 6 tham số giảm rất nhanh, và số tham số tối đa từng quan sát được là **6**. Hệ quả: nếu mọi lỗi đều do tối đa *t* tham số gây ra thì phủ hết các bộ *t* giá trị gần như tương đương vét cạn. Với *t* = 2 đó là Pairwise.
- **Tài liệu về công cụ:** J. Czerwonka (Microsoft), *"Pairwise Testing in Real World: Practical Extensions to Test Case Generators"*, 2006. File PDF nằm trong thư mục `doc/` của repo `microsoft/pict`; bài mô tả các mở rộng thực tế của PICT như ràng buộc, test âm và bậc tổ hợp `/o:N` mà nhóm dùng ở các mục sau.
- **Bài toán bùng nổ tổ hợp (Combinatorial Explosion):** Khi một hệ thống hoặc API có $N$ tham số, mỗi tham số có $V_i$ giá trị khả dĩ, phương pháp vét cạn (Exhaustive Testing) đòi hỏi không gian thử nghiệm là $\prod_{i=1}^N V_i$. Với các chức năng như Cấu hình Mealie (9 tham số) hay Tìm kiếm Mealie (9 tham số), số lượng tổ hợp vét cạn lên tới hàng nghìn ca (1.792 và 5.832), quá nhiều để thiết kế kết quả mong đợi và phân tích từng ca bằng tay, dù chạy tự động vẫn tốn công bảo trì.
- **Mục tiêu của Pairwise:** Chọn ra một tập con nhỏ nhất các ca kiểm thử sao cho **mọi cặp giá trị $(P_i = v_a, P_j = v_b)$ của hai tham số bất kỳ đều xuất hiện cùng nhau ít nhất một lần** trong tập test case. Nhờ đó, số lượng test case giảm rất mạnh (ở ba model của nhóm: từ 92,7% đến 99,7%) trong khi vẫn giữ được khả năng phát hiện phần lớn lỗi do một hoặc hai tham số gây ra.

### 2. Ví dụ trực quan: Giảm từ 18 tổ hợp xuống 9 tổ hợp
Xét chức năng sắp xếp và phân trang danh sách công thức Mealie với 3 tham số (`models/demo.txt`):
- `orderBy`: 3 giá trị (`name`, `created_at`, `random`)
- `orderDirection`: 2 giá trị (`asc`, `desc`)
- `perPage`: 3 giá trị (`1`, `10`, `50`)

- **Không gian vét cạn (Exhaustive):** $3 \times 2 \times 3 = 18$ ca thử nghiệm.
- **Tổng số cặp cần phủ (Pairs):**
  - Cặp (`orderBy`, `orderDirection`): $3 \times 2 = 6$ cặp.
  - Cặp (`orderBy`, `perPage`): $3 \times 3 = 9$ cặp.
  - Cặp (`orderDirection`, `perPage`): $2 \times 3 = 6$ cặp.
  - $\rightarrow$ Tổng cộng có $6 + 9 + 6 = 21$ cặp giá trị duy nhất cần phủ (được kiểm chứng qua lệnh `pict models/demo.txt /s`).
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

## D.2. LÝ DO CHỌN PHẠM VI KIỂM THỬ TRÊN MEALIE VÀ BẢNG SO SÁNH

Nhóm giới hạn phạm vi kiểm thử vào **3 luồng nghiệp vụ cốt lõi** thuộc các tầng API của Mealie v3.28.0 thay vì kiểm thử toàn bộ hệ thống.

### Bảng so sánh Pairwise (/o:2), 3-wise (/o:3) và Exhaustive:
Dưới đây là số liệu thực tế được chạy trực tiếp bằng công cụ Microsoft PICT v3.7.4 trên máy cục bộ với 3 mô hình của nhóm:

| Luồng nghiệp vụ | Endpoint API | Số tham số | Số cặp cần phủ (2-way) | Pairwise (2-way) | 3-wise (/o:3) | Exhaustive | Tỷ lệ giảm Pairwise vs Exhaustive |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Cấu hình Household** | `PUT /api/households/preferences` | 9 | 224 | **16** | 53 | 1.792 | **Giảm 99,1%** |
| **Tìm kiếm và Lọc công thức** | `GET /api/recipes` | 9 (1 ràng buộc) | 273 | **19** | 67 | 5.832 | **Giảm 99,7%** |
| **Phân quyền người dùng** | `POST /api/admin/users` & Action APIs | 6 | 100 | **14** | 41 | 192 | **Giảm 92,7%** |
| **Tổng cộng** | | | **597** | **49** | **161** | **7.816** | **Giảm 99,37%** |

#### Nhận xét số liệu:
1. **Hiệu quả giảm thiểu vượt trội:** So với thử nghiệm vét cạn (7.816 ca kiểm thử), kỹ thuật Pairwise chỉ cần **49 test cases** (giảm 99,37% tổng số ca kiểm thử) mà vẫn đảm bảo độ phủ 100% tất cả 597 cặp giá trị tương tác hợp lệ của hệ thống.
2. **Chi phí nâng bậc lên 3-wise:** Khi nâng từ bậc 2 (Pairwise - 49 cases) lên bậc 3 (3-wise - 161 cases), số lượng test case tăng hơn gấp 3 lần (tăng 228%).
3. **Lý do chọn chạy đối chứng Exhaustive cho luồng Household:** Luồng Cấu hình Household có không gian vét cạn là 1.792 ca kiểm thử, hoàn toàn nằm trong khả năng tự động hóa bằng script HTTP API. Vì vậy, nhóm quyết định chạy toàn bộ 1.792 ca vét cạn ở giai đoạn sau giữa kỳ để đối chứng trực tiếp với 16 ca Pairwise, từ đó đo lường thực tế xem Pairwise có bỏ sót lỗi nghiệp vụ nào hay không.

### Phân tích chi tiết từng luồng:
1. **Luồng 1: Cấu hình Household (`household_preferences`)**
   - Định nghĩa trong: `mealie/schema/household/household_preferences.py`.
   - Gồm 8 cờ boolean (`privateHousehold`, `showAnnouncements`, `lockRecipeEditsFromOtherHouseholds`, `recipePublic`, `recipeShowNutrition`, `recipeShowAssets`, `recipeLandscapeView`, `recipeDisableComments`) và 1 tham số số nguyên `firstDayOfWeek` (7 giá trị: 0-6).
   - Vét cạn: $2^8 \times 7 = 1.792$ tổ hợp. Pairwise rút gọn xuống **16 case** (giảm 99,1%).
   - *Lý do chọn:* Các cờ cấu hình household quyết định giá trị mặc định cho toàn bộ công thức mới được tạo ra trong household đó. Đây là nơi kiểm thử lý tưởng cho việc gán cấu hình mặc định (default inheritance).
   - *Lưu ý miền giá trị:* trong schema, `firstDayOfWeek` chỉ được khai báo là `int`, không có giới hạn 0-6. Model chỉ lấy 7 giá trị hợp lệ 0-6; các giá trị ngoài miền (ví dụ -1, 7) không thuộc pairwise mà sẽ được thử bằng test âm riêng sau giữa kỳ.

2. **Luồng 2: Tìm kiếm và Lọc công thức (`recipe_search_and_filter`)**
   - Định nghĩa trong: `mealie/schema/response/pagination.py` và hàm `get_all` tại `mealie/routes/recipe/recipe_crud_routes.py`.
   - Gồm 9 tham số: từ khóa tìm kiếm (`search`), danh mục (`categories`), thẻ (`tags`), logic giao/hợp (`requireAllCategories`, `requireAllTags`), tiêu chí sắp xếp (`orderBy`), hướng sắp xếp (`orderDirection`), seed ngẫu nhiên (`paginationSeed`), số bản ghi mỗi trang (`perPage`).
   - Có ràng buộc logic thực tế (Constraint): khi `orderBy = random`, Mealie bắt buộc phải có `paginationSeed`. Ràng buộc này nằm trong `RequestQuery.validate_randseed` (`mealie/schema/response/pagination.py`): thiếu seed thì validator ném lỗi và FastAPI trả **422**. Trong model PICT nó được viết là `IF [orderBy] = "random" THEN [paginationSeed] = "abc123";`. Giá trị `none` của `orderBy` nghĩa là *không gửi tham số này*; khi đó Mealie dùng mặc định `orderDirection=desc`.
   - Vét cạn: 5.832 tổ hợp hợp lệ. Pairwise rút gọn xuống **19 case** (giảm 99,7%).
   - *Lý do chọn:* Phức tạp về mặt logic truy vấn cơ sở dữ liệu (SQLAlchemy queries, JOIN, ORDER BY, OFFSET/LIMIT).

3. **Luồng 3: Phân quyền người dùng (`user_permissions`)**
   - Định nghĩa trong: `mealie/schema/user/user.py` và các controller phân quyền tại `mealie/routes/_base/checks.py`.
   - Gồm 5 cờ quyền hạn (`admin`, `canInvite`, `canManage`, `canManageHousehold`, `canOrganize`) và 1 biến hành động (`action` với 6 API nghiệp vụ).
   - Vét cạn: $2^5 \times 6 = 192$ tổ hợp. Pairwise rút gọn xuống **14 case** (giảm 92,7%).
   - *Lý do chọn:* Logic bảo mật có tính tương tác cao: khi user là `admin`, Mealie tự động cấp mọi quyền (hàm `_set_permissions` trong `mealie/db/models/users/users.py`); khi user không phải admin, hành động chỉ thành công khi có cờ quyền tương ứng.
   - *Bảng kết quả mong đợi (oracle), đã đối chiếu với mã nguồn v3.28.0:*

| `action` | API | Điều kiện thành công | Thành công | Bị chặn |
|:---|:---|:---|:---:|:---:|
| `createCategory` | `POST /api/organizers/categories` | `canOrganize` hoặc `admin` | 201 | 403 |
| `updateHouseholdPrefs` | `PUT /api/households/preferences` | `canManageHousehold` hoặc `admin` | 200 | 403 |
| `listMembers` | `GET /api/households/members` | `canManage` hoặc `admin` | 200 | 403 |
| `setMemberPermissions` | `PUT /api/households/permissions` | `canManage` hoặc `admin`, và đối tượng là *user khác* cùng household | 200 | 403 |
| `createInvite` | `POST /api/households/invitations` | `canInvite` hoặc `admin` (đăng nhập bằng mật khẩu đang bật, mặc định bật) | 201 | 403 |
| `adminListUsers` | `GET /api/admin/users` | chỉ `admin` | 200 | 403 |

   - *Hai chi tiết dễ làm sai oracle:* (1) khi tạo user với `admin=true`, bốn cờ còn lại tự bật dù model gửi `false`, nên "hành động thành công" phải tính theo *cờ hiệu lực sau khi lưu*, không theo cờ đã gửi; đây chính là tương tác hai tham số mà Pairwise nhắm tới. (2) `setMemberPermissions` bị từ chối (403) nếu user tự đổi quyền của chính mình, nên script phải nhắm vào một user khác, ví dụ `khongquyen`.
   - *Ngoài model, chưa kết luận:* trong mã nguồn, API tạo category, tag và food có kiểm tra `canOrganize`, còn API tạo tool (`POST /api/organizers/tools`) thì không thấy kiểm tra này. Nhóm chưa coi đây là lỗi; nếu thêm `createTool` vào `action` sau giữa kỳ và kết quả xác nhận thì sẽ phân tích ở mục G.

---

## D.3. CÁC GIẢ ĐỊNH KIỂM THỬ (ASSUMPTIONS)

1. **Giả định về cơ chế phát sinh lỗi:** Khiếm khuyết trong backend Mealie chủ yếu bắt nguồn từ xử lý sai một tham số đơn lẻ hoặc do xung đột logic giữa 2 tham số gửi lên cùng lúc.
2. **Tính đại diện của phân vùng tương đương (Equivalence Partitioning):**
   - Tham số dạng chuỗi hoặc mảng được rút gọn thành các nhãn đại diện:
     - `search`: `none` (chuỗi rỗng), `match` (từ khóa khớp 100% dữ liệu seed), `nomatch` (từ khóa không tồn tại).
     - `categories`, `tags`: `none`, `one` (chọn 1 phần tử), `two` (chọn 2 phần tử).
     - `paginationSeed`: `none`, `abc123`.
   - Giả định rằng mọi giá trị cụ thể trong cùng một lớp tương đương sẽ có cùng hành vi phản hồi từ hệ thống.
3. **Kết quả mong đợi suy ra từ mã nguồn:** oracle của ba luồng được viết dựa trên mã nguồn Mealie v3.28.0 (validator phân trang, `OperationChecks`, `_set_permissions`, `create_one` của `recipe_service`). Nếu Mealie đổi hành vi ở phiên bản khác thì oracle phải viết lại; vì vậy nhóm chốt đúng một tag.
4. **Môi trường thử nghiệm đơn nhất và tất định:**
   - Phiên bản ứng dụng cố định: Mealie v3.28.0 chạy trên Docker Container cổng 9925.
   - Cơ sở dữ liệu: SQLite mặc định của Mealie.
   - Dữ liệu mẫu (Seed Data) do TV2 khởi tạo (`docs/seed-data.md`: 12 công thức, 3 category, 3 tag, 2 user phân quyền) là cố định và không bị thay đổi ngẫu nhiên giữa các lần test.
  - Test chạy tuần tự, không chạy song song với demo hoặc với nhau, vì cùng thay đổi cấu hình household và quyền user.

---

## D.4. RỦI RO, GIỚI HẠN VÀ BIỆN PHÁP GIẢM THIỂU

| STT | Rủi ro / Giới hạn | Hậu quả tiềm ẩn | Biện pháp giảm thiểu của nhóm |
|:---:|:---|:---|:---|
| 1 | **Bỏ sót lỗi tương tác từ 3 tham số trở lên (Higher-order Interactions)** | Nếu có bug chỉ xuất hiện khi 3 hoặc 4 tham số cùng có giá trị đặc thù, Pairwise (2-way) sẽ bỏ sót. | - Thực hiện chạy bộ **3-wise (53 case)** và **Exhaustive (1.792 case)** đối chứng cho Luồng Cấu hình Household.<br>- Lập bảng đối sánh tỷ lệ bắt lỗi giữa Pairwise, 3-wise và Exhaustive sau giữa kỳ. |
| 2 | **Chọn sai giá trị đại diện cho phân vùng** | Nếu bug chỉ phát sinh tại một ký tự đặc biệt hoặc giá trị biên cực đại mà không được đưa vào model, test sẽ không bắt được. | - Bổ sung các ca kiểm thử âm (Negative Test) độc lập (ví dụ: gửi `orderBy=random` mà không có seed để kiểm tra lỗi 422). |
| 3 | **Khó khăn trong việc xác định Oracle (Kết quả mong đợi)** | Khi tham số ngẫu nhiên phối hợp, việc tính toán chính xác danh sách kết quả trả về bằng tay rất phức tạp. | - Sử dụng **Điều kiện bất biến (Invariants)** thay vì so khớp cứng kết quả: kiểm tra status code 200, số lượng $\le$ perPage, tất cả item trả về đều chứa tag/category đã chọn. |
| 4 | **Hiện tượng ô nhiễm trạng thái (State Pollution)** | Các ca kiểm thử tạo dữ liệu hoặc cập nhật cấu hình có thể làm sai lệch kết quả của các ca kiểm thử kế tiếp. | - Mỗi test case tạo công thức với tên định danh độc nhất (kèm timestamp/UUID).<br>- Hỗ trợ script reset/dựng lại môi trường nhanh chóng. |
| 5 | **Oracle sai do tương tác giữa các cờ quyền** | Nếu script tính kết quả mong đợi theo cờ *đã gửi* thay vì cờ *hiệu lực* (admin tự bật 4 cờ còn lại), nhiều case sẽ fail giả và bị nhầm là lỗi của Mealie. | - Dùng bảng oracle ở D.2 và tính cờ hiệu lực trước khi so sánh.<br>- Khi một case fail, kiểm tra lại oracle trước khi kết luận lỗi hệ thống (bước 2 của quy trình RCA). |
| 6 | **Giá trị ngoài miền không nằm trong model** | Ví dụ `firstDayOfWeek` = 7 hoặc -1, chuỗi tìm kiếm có ký tự đặc biệt: Pairwise chỉ dùng giá trị hợp lệ nên không chạm tới. | - Viết test âm riêng sau giữa kỳ, tách khỏi bộ pairwise và đánh dấu rõ là test âm. |

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

### 3. Tiêu chí đối chứng (Pairwise so với 3-wise và Exhaustive):
- Với luồng Household, chạy cả bộ 16 case Pairwise, 53 case 3-wise và 1.792 case Exhaustive, rồi lập bảng so sánh số case FAIL và nhóm lỗi tìm được của từng bộ.
- Nếu Exhaustive hoặc 3-wise tìm ra lỗi mà Pairwise bỏ sót thì ghi nhận đó là *giới hạn của kỹ thuật* trong mục G, không coi là lỗi của đợt test.
- Với luồng Phân quyền (192 tổ hợp), cũng chạy đối chứng Exhaustive vì chi phí thấp.

### 4. Tiêu chí nghiệm thu đợt kiểm thử (Test Run Acceptance):
- Toàn bộ các ca kiểm thử Pairwise được thực thi tự động qua test script, không có can thiệp thủ công.
- Mọi ca kiểm thử FAIL đều phải trải qua quy trình phân tích nguyên nhân gốc rễ (Root Cause Analysis - RCA) và phân loại chính xác thành:
  1. *Lỗi hệ thống Mealie (System Bug)*.
  2. *Lỗi kịch bản kiểm thử (Test Script / Oracle Error)*.
  3. *Lỗi dữ liệu mẫu / môi trường (Environment / Seed Data Issue)*.

---

## D.6. TÁI LẬP SỐ LIỆU CỦA MỤC D

Mọi con số ở D.1 và D.2 kiểm lại được bằng lệnh, chạy trong **Command Prompt** (không dùng PowerShell cho lệnh có dấu `>`) ở thư mục gốc repo:

```bat
pict models\household.txt /s          :: số cặp cần phủ (224) và số case sinh ra (16)
pict models\household.txt /o:3 /s    :: bộ 3-wise: 53 case
python scripts\kiem_tra_cap.py --all  :: kiểm tra độc lập, không dùng PICT
```

`scripts/kiem_tra_cap.py` tự liệt kê toàn bộ tổ hợp hợp lệ của model (kể cả ràng buộc), tính tập cặp cần phủ rồi đối chiếu với file `cases/*.tsv`. Kết quả trên bốn model của nhóm:

| Model | Tổ hợp hợp lệ | Cặp cần phủ | Số case | Cặp bị sót |
|:---|:---:|:---:|:---:|:---:|
| `demo.txt` | 18 | 21 | 9 | 0 |
| `household.txt` | 1.792 | 224 | 16 | 0 |
| `search.txt` | 5.832 | 273 | 19 | 0 |
| `permissions.txt` | 192 | 100 | 14 | 0 |

Bộ 53 case 3-wise của Household cũng phủ 100% cặp. Số case Pairwise có thể lệch 1-2 tùy phiên bản PICT, vì có nhiều bộ test cùng phủ đủ mọi cặp; điều kiện nghiệm thu là *độ phủ 100%*, không phải đúng 16, 19 hay 14 case.
