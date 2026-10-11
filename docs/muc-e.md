# MỤC E: XÂY DỰNG MÔ HÌNH PICT VÀ SINH TẬP CA KIỂM THỬ

**Người phụ trách:** Bùi Ngọc Toàn (MSSV: 2312776 - TV4)  
**Đề tài:** R02 Mealie + K06 Combinatorial/Pairwise Testing  
**Hệ thống kiểm thử:** Mealie v3.28.0 (Commit SHA: `0552eaa4a80031b8572849cca0ed95d07f1be001`)  
**Công cụ sinh ca kiểm thử:** Microsoft PICT (Pairwise Independent Combinatorial Testing v3.7.4)

---

## E.1. TỔNG QUAN VỀ QUY TRÌNH THIẾT KẾ MÔ HÌNH PICT

Quy trình thiết kế mô hình kiểm thử tổ hợp Pairwise cho Mealie bao gồm 5 bước chặt chẽ:
1. **Phân tích giao diện API và Schema:** Đọc OpenAPI specification (`/docs`) và mã nguồn backend Mealie để trích xuất danh sách tham số (query parameters, request body fields, authorization roles).
2. **Phân vùng tương đương & Giá trị đại diện:** Với mỗi tham số, xác định miền giá trị hợp lệ, áp dụng kỹ thuật phân vùng tương đương (Equivalence Partitioning) và biên (Boundary Values) để chọn ra tập giá trị đại diện rời rạc.
3. **Mô hình hóa dưới định dạng PICT:** Viết file đặc tả mô hình (`models/*.txt`) theo cú pháp Microsoft PICT: `<Tên tham số>: <Giá trị 1>, <Giá trị 2>, ...`.
4. **Xác định và khai báo các ràng buộc nghiệp vụ (Constraints):** Sử dụng các mệnh đề logic `IF ... THEN` nhằm loại bỏ các tổ hợp vô nghĩa hoặc không khả thi về mặt ngữ nghĩa hệ thống (Semantic Infeasibility).
5. **Sinh tập test cases và thẩm định độ phủ:** Chạy công cụ PICT để sinh tập ca kiểm thử tối ưu (`cases/*.tsv`) và sử dụng cờ `/s` để kiểm tra độ phủ 100% 2-way Combinatorial Coverage.

---

## E.2. CHI TIẾT MÔ HÌNH HÓA 3 LUỒNG NGHIỆP VỤ

### 1. Luồng 1: Cấu hình Household (Household Preferences)
- **Endpoint API:** `PUT /api/households/preferences`
- **File model:** `models/household.txt`
- **File test cases sinh ra:** `cases/household.tsv`

#### Bảng tham số và phân vùng giá trị:
| STT | Tham số (JSON Body Field) | Kiểu dữ liệu | Các giá trị đại diện | Ý nghĩa nghiệp vụ |
|:---:|:---|:---:|:---|:---|
| 1 | `privateHousehold` | boolean | `true, false` | Ẩn/hiện household đối với người dùng ngoài |
| 2 | `showAnnouncements` | boolean | `true, false` | Bật/tắt hiển thị thông báo hệ thống |
| 3 | `lockRecipeEditsFromOtherHouseholds` | boolean | `true, false` | Khóa quyền chỉnh sửa công thức từ household khác |
| 4 | `firstDayOfWeek` | integer | `0, 1, 2, 3, 4, 5, 6` | Ngày đầu tuần (0: Thứ hai, ..., 6: Chủ nhật) |
| 5 | `recipePublic` | boolean | `true, false` | Cho phép công thức mặc định công khai |
| 6 | `recipeShowNutrition` | boolean | `true, false` | Hiển thị bảng thông tin dinh dưỡng |
| 7 | `recipeShowAssets` | boolean | `true, false` | Hiển thị tệp đính kèm công thức |
| 8 | `recipeLandscapeView` | boolean | `true, false` | Chế độ xem xoay ngang mặc định |
| 9 | `recipeDisableComments` | boolean | `true, false` | Vô hiệu hóa bình luận trên công thức |

#### Thống kê độ phức tạp & kết quả sinh:
- **Số tham số:** 9 tham số.
- **Không gian vét cạn (Exhaustive):** $2^8 \times 7 = 1.792$ ca kiểm thử.
- **Tổng số cặp cần phủ (2-way Combinations):** 224 cặp.
- **Số test case sinh ra bởi PICT:** **16 ca kiểm thử** (phủ 100% cặp giá trị).
- **Tỷ lệ giảm thiểu:** **99,1%** so với vét cạn.

---

### 2. Luồng 2: Tìm kiếm và Lọc công thức (Recipe Search & Filter)
- **Endpoint API:** `GET /api/recipes`
- **File model:** `models/search.txt`
- **File test cases sinh ra:** `cases/search.tsv`

#### Bảng tham số và phân vùng giá trị:
| STT | Tham số (Query Param) | Kiểu dữ liệu | Các giá trị đại diện | Ý nghĩa nghiệp vụ |
|:---:|:---|:---:|:---|:---|
| 1 | `search` | string | `none, match, nomatch` | `none`: bỏ trống; `match`: khớp từ khóa; `nomatch`: từ khóa không tồn tại |
| 2 | `categories` | string | `none, one, two` | `none`: không lọc; `one`: lọc theo 1 category; `two`: lọc theo 2 categories |
| 3 | `tags` | string | `none, one, two` | `none`: không lọc; `one`: lọc theo 1 tag; `two`: lọc theo 2 tags |
| 4 | `requireAllCategories` | boolean | `true, false` | Điều kiện AND (true) hoặc OR (false) giữa các categories |
| 5 | `requireAllTags` | boolean | `true, false` | Điều kiện AND (true) hoặc OR (false) giữa các tags |
| 6 | `orderBy` | string | `none, name, created_at, rating, random` | Tiêu chí sắp xếp kết quả |
| 7 | `orderDirection` | string | `asc, desc` | Hướng sắp xếp (tăng dần/giảm dần) |
| 8 | `paginationSeed` | string | `none, abc123` | Seed cố định thứ tự ngẫu nhiên khi phân trang |
| 9 | `perPage` | integer | `1, 10, 50` | Kích thước trang (Biên nhỏ nhất: 1, Mặc định: 10, Lớn: 50) |

#### Ràng buộc nghiệp vụ (Constraints):
```text
IF [orderBy] = "random" THEN [paginationSeed] = "abc123";
```
*Giải thích nghiệp vụ:* Theo logic của backend Mealie, việc phân trang với `orderBy = "random"` đòi hỏi tham số `paginationSeed` để giữ nguyên thứ tự sắp xếp ngẫu nhiên giữa các trang kế tiếp nhau. Do đó, nếu chọn sắp xếp ngẫu nhiên, hệ thống bắt buộc phải nhận một seed xác định nhằm đảm bảo tính tất định (determinism) khi kiểm thử.

#### Thống kê độ phức tạp & kết quả sinh:
- **Số tham số:** 9 tham số, có 1 ràng buộc điều kiện.
- **Không gian vét cạn lý thuyết:** $3 \times 3 \times 3 \times 2 \times 2 \times 5 \times 2 \times 2 \times 3 = 5.832$ ca kiểm thử.
- **Tổng số cặp cần phủ hợp lệ (2-way Combinations):** 273 cặp.
- **Số test case sinh ra bởi PICT:** **19 ca kiểm thử** (phủ 100% cặp giá trị hợp lệ).
- **Tỷ lệ giảm thiểu:** **99,7%** so với vét cạn.

---

### 3. Luồng 3: Phân quyền người dùng (User Permissions & Access Control)
- **Endpoint API:** `POST /api/admin/users` (cấp quyền) & Các Action APIs tương ứng
- **File model:** `models/permissions.txt`
- **File test cases sinh ra:** `cases/permissions.tsv`

#### Bảng tham số và phân vùng giá trị:
| STT | Tham số (Role / Flag) | Kiểu dữ liệu | Các giá trị đại diện | Quyền hạn tương ứng |
|:---:|:---|:---:|:---|:---|
| 1 | `admin` | boolean | `true, false` | Quyền Quản trị viên hệ thống (Superuser) |
| 2 | `canInvite` | boolean | `true, false` | Quyền tạo link mời thành viên mới |
| 3 | `canManage` | boolean | `true, false` | Quyền quản lý công thức và danh mục chung |
| 4 | `canManageHousehold` | boolean | `true, false` | Quyền cấu hình và chỉnh sửa Household |
| 5 | `canOrganize` | boolean | `true, false` | Quyền tạo và quản lý tags/categories |
| 6 | `action` | string | `createCategory, updateHouseholdPrefs, listMembers, setMemberPermissions, createInvite, adminListUsers` | Thao tác API người dùng thực thi kiểm tra |

#### Ma trận kỳ vọng quyền hạn (Oracle Matrix):
| Hành động (`action`) | Endpoint kiểm tra | Yêu cầu quyền tối thiểu | Kỳ vọng HTTP Status khi Có quyền / Không có quyền |
|:---|:---|:---|:---:|
| `adminListUsers` | `GET /api/admin/users` | `admin = true` | 200 OK / 403 Forbidden |
| `setMemberPermissions` | `PUT /api/households/members/{id}` | `admin = true` hoặc `canManageHousehold = true` | 200 OK / 403 Forbidden |
| `updateHouseholdPrefs` | `PUT /api/households/preferences` | `admin = true` hoặc `canManageHousehold = true` | 200 OK / 403 Forbidden |
| `createInvite` | `POST /api/households/invites` | `admin = true` hoặc `canInvite = true` | 201 Created / 403 Forbidden |
| `createCategory` | `POST /api/categories` | `admin = true` hoặc `canOrganize = true` hoặc `canManage = true` | 201 Created / 403 Forbidden |
| `listMembers` | `GET /api/households/members` | Mọi thành viên đã đăng nhập | 200 OK |

#### Thống kê độ phức tạp & kết quả sinh:
- **Số tham số:** 6 tham số.
- **Không gian vét cạn (Exhaustive):** $2^5 \times 6 = 192$ ca kiểm thử.
- **Tổng số cặp cần phủ (2-way Combinations):** 100 cặp.
- **Số test case sinh ra bởi PICT:** **14 ca kiểm thử** (phủ 100% cặp giá trị).
- **Tỷ lệ giảm thiểu:** **92,7%** so với vét cạn.

---

## E.3. HƯỚNG DẪN TÁI HIỆN VÀ TỰ ĐỘNG HÓA SINH TEST CASES

Để tự động sinh lại toàn bộ tập test cases từ các file model, thực hiện bằng một trong hai cách sau:

### Cách 1: Sử dụng batch script của dự án
1. Đảm bảo file thực thi `pict.exe` nằm trong thư mục gốc hoặc biến môi trường `PATH`.
2. Mở Command Prompt (`cmd`) tại thư mục gốc của repository:
```bat
scripts\sinh_case.bat
```
Script sẽ tự động duyệt qua 4 models (`demo`, `household`, `search`, `permissions`), xuất kết quả ra thư mục `cases/*.tsv` và in bảng thống kê độ phủ Combinations của từng model.

### Cách 2: Chạy trực tiếp từng lệnh PICT
```bat
pict models\household.txt > cases\household.tsv
pict models\household.txt /s

pict models\search.txt > cases\search.tsv
pict models\search.txt /s

pict models\permissions.txt > cases\permissions.tsv
pict models\permissions.txt /s
```

---

## E.4. KẾT QUẢ VÀ ĐÁNH GIÁ CHẤT LƯỢNG BỘ TEST CASES

1. **Độ phủ cặp giá trị (2-way Coverage):** Toàn bộ 3 mô hình đều đạt **100% độ phủ các cặp giá trị hợp lệ** (được chứng thực bằng thông số thống kê từ công cụ PICT).
2. **Kích thước bộ test tối ưu:** Tổng cộng toàn bộ 3 luồng nghiệp vụ chỉ cần **49 test cases** (16 + 19 + 14) để kiểm thử thay vì **7.816 test cases** nếu vét cạn, giảm **99,37%** tổng số ca kiểm thử cần thực hiện.
3. **Tính sẵn sàng cho tự động hóa (Automation Readiness):** Các file `.tsv` được cấu trúc dạng bảng chuẩn (tab-separated), các cột khớp 1-1 với tên trường payload và query params trong API của Mealie, giúp các kịch bản kiểm thử tự động hóa (Mục F) đọc dữ liệu trực tiếp và thực thi (Data-driven Testing) mà không cần bước tiền xử lý phức tạp.
