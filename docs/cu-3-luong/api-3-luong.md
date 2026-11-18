# Request và response của 3 luồng

Người ghi: Nguyễn Đình Tuấn (TV5). Mọi kết quả dưới đây được ghi lại bằng cách gọi thật vào backend Mealie `v3.28.0` (commit `0552eaa4a80031b8572849cca0ed95d07f1be001`), cơ sở dữ liệu SQLite, cổng 9925, đăng nhập bằng tài khoản dùng chung `nhom22@example.com`. Kết quả khớp với bảng tham khảo trong [huong-dan/api-da-kiem-chung.md](huong-dan/api-da-kiem-chung.md).

Quy ước: địa chỉ gốc `http://localhost:9925`. JSON gửi đi và nhận về dùng tên trường kiểu `recipePublic`; riêng lớp ngoài của kết quả phân trang dùng `per_page`, `total_pages`. Mọi API trừ đăng nhập đều cần header `Authorization: Bearer <access_token>`.

## 1. Đăng nhập

### Lấy token

- **Gọi:** `POST /api/auth/token`
- **Gửi:** dạng form (không phải JSON), hai trường `username` và `password`. `username` nhận cả email lẫn tên đăng nhập.
- **Nhận:** 200, JSON `{"access_token": "eyJ...", "token_type": "bearer", "expires_in": 172800}`
- **Khi sai:** 401 `{"detail": "Unauthorized"}` nếu sai tài khoản hoặc mật khẩu. Gọi một API khác mà không gửi token thì nhận 401 `{"detail": "Could not validate credentials"}`.

Lưu ý khi viết test: API đăng nhập đặt thêm một cookie phiên. Nếu dùng `requests.Session()` thì các lần gọi sau vẫn được coi là đã đăng nhập dù không gửi header, nên muốn thử trường hợp "không có token" phải gọi bằng `requests.get(...)` trần.

## 2. Luồng cấu hình household

Thứ tự gọi: lưu cấu hình, tạo công thức, đọc công thức, xóa công thức. Kết quả mong đợi của cả luồng: cài đặt của công thức mới bằng 5 tùy chọn `recipe...` vừa lưu.

### Đọc cấu hình household

- **Gọi:** `GET /api/households/preferences`
- **Quyền cần có:** chỉ cần đăng nhập
- **Nhận:** 200, JSON gồm 9 trường cấu hình và `id`

### Lưu cấu hình household

- **Gọi:** `PUT /api/households/preferences`
- **Quyền cần có:** `canManageHousehold`
- **Gửi:**

```json
{
  "privateHousehold": false,
  "showAnnouncements": false,
  "lockRecipeEditsFromOtherHouseholds": false,
  "firstDayOfWeek": 3,
  "recipePublic": true,
  "recipeShowNutrition": true,
  "recipeShowAssets": false,
  "recipeLandscapeView": true,
  "recipeDisableComments": true
}
```

- **Nhận:** 200, JSON gồm đúng 9 giá trị vừa gửi và `id` của cấu hình
- **Khi sai:** 403 nếu không đủ quyền; 422 nếu sai kiểu dữ liệu

### Tạo công thức mới

- **Gọi:** `POST /api/recipes`
- **Quyền cần có:** chỉ cần đăng nhập
- **Gửi:** `{"name": "Thu household abc"}` (tên không được trùng công thức đã có)
- **Nhận:** 201, một chuỗi JSON là slug của công thức: `"thu-household-abc"`

### Đọc lại công thức

- **Gọi:** `GET /api/recipes/{slug}`
- **Nhận:** 200, JSON công thức. Phần cần so sánh:

```json
"settings": {"public": true, "showNutrition": true, "showAssets": false,
             "landscapeView": true, "disableComments": true, "locked": false}
```

| Cài đặt của công thức | Phải bằng tùy chọn |
| --- | --- |
| `settings.public` | `recipePublic` |
| `settings.showNutrition` | `recipeShowNutrition` |
| `settings.showAssets` | `recipeShowAssets` |
| `settings.landscapeView` | `recipeLandscapeView` |
| `settings.disableComments` | `recipeDisableComments` |

`settings.locked` không lấy từ household, luôn là `false` với công thức mới.

### Xóa công thức

- **Gọi:** `DELETE /api/recipes/{slug}`
- **Nhận:** 200, JSON của công thức vừa xóa. Gọi `GET` lại cùng slug nhận 404 `{"detail": {"message": "No Entry Found", ...}}`.

### Giá trị không hợp lệ khi lưu cấu hình

| Gửi | Kết quả |
| --- | --- |
| `firstDayOfWeek: "abc"` | 422, `Input should be a valid integer, unable to parse string as an integer` |
| `recipePublic: "maybe"` | 422, `Input should be a valid boolean, unable to interpret input` |
| `firstDayOfWeek: 7` | **200**, Mealie lưu 7 |
| `firstDayOfWeek: -1` | **200**, Mealie lưu -1 |
| Body rỗng `{}` | **200**, mọi trường quay về giá trị mặc định của schema |

Một tuần chỉ có các ngày từ 0 đến 6 nhưng API nhận cả 7 và -1; đây là hành vi đáng ghi lại ở mục G nếu test của nhóm tái hiện được.

## 3. Luồng tìm kiếm và lọc

### Danh sách công thức

- **Gọi:** `GET /api/recipes` với các tham số trên URL
- **Quyền cần có:** chỉ cần đăng nhập
- **Nhận:** 200, JSON phân trang `{"items": [...], "total": 12, "page": 1, "per_page": 50, "total_pages": 1, "next": null, "previous": null}`. Mỗi phần tử của `items` có `name`, `slug`, `recipeCategory`, `tags`, `createdAt`...

| Tham số | Giá trị | Ghi chú |
| --- | --- | --- |
| `search` | từ khóa | Tìm theo tên |
| `categories`, `tags` | slug hoặc id; lặp lại tham số để truyền nhiều giá trị | Slug của "Món chính" là `mon-chinh`, của "Tráng miệng" là `trang-mieng`, của tag "Chay" là `chay` |
| `requireAllCategories`, `requireAllTags` | `true` hoặc `false` | `false` (mặc định): có ít nhất một giá trị. `true`: phải có đủ mọi giá trị |
| `orderBy` | `name`, `created_at`, `rating`, `random` | Tên cột sai nhận 400 |
| `orderDirection` | `asc`, `desc` | Giá trị khác nhận 422 |
| `paginationSeed` | chuỗi bất kỳ | Bắt buộc khi `orderBy=random` |
| `page`, `perPage` | số nguyên | |

Tên tham số phải viết kiểu camelCase. Gửi `require_all_categories` (kiểu snake_case) **không báo lỗi mà bị bỏ qua**: gọi với `categories=mon-chinh&categories=trang-mieng&require_all_categories=true` vẫn trả về kết quả của chế độ "có ít nhất một" (8 công thức, thay vì 1).

### Dữ liệu mẫu dùng để ghi các ví dụ

Các ví dụ dưới đây chạy trên bộ dữ liệu mẫu chính thức của nhóm (12 công thức, 3 category, 3 tag, do TV2 chuẩn bị, xem [seed-data.md](seed-data.md)). Nạp lại bộ này bằng `python scripts\chuan_bi_muc_c.py seed`; số kết quả bên dưới khớp bảng "Kết quả mong đợi" trong `seed-data.md`.

| # | Công thức | Category | Tag |
| --- | --- | --- | --- |
| 1 | Phở bò | Món chính | |
| 2 | Bún chả | Món chính | Nhanh |
| 3 | Gỏi cuốn chay | Món chính | Nhanh, Chay |
| 4 | Lẩu thái | Món chính | Cay |
| 5 | Chè đậu | Tráng miệng | Chay |
| 6 | Bánh flan | Tráng miệng | |
| 7 | Sinh tố bơ | Đồ uống, Tráng miệng | Nhanh, Chay |
| 8 | Trà đá | Đồ uống | Nhanh |
| 9 | Cà phê sữa | Đồ uống | |
| 10 | Nước mắm pha | | Cay |
| 11 | Cơm trắng | | |
| 12 | Xôi xoài | Món chính, Tráng miệng | Chay |

### Ví dụ gọi

| Gọi | Kết quả |
| --- | --- |
| `categories=mon-chinh` | 200, 5 công thức: Bún chả, Gỏi cuốn chay, Lẩu thái, Phở bò, Xôi xoài |
| `categories=mon-chinh&categories=trang-mieng&requireAllCategories=false` | 200, 8 công thức (hợp hai category, Xôi xoài chỉ đếm một lần) |
| `categories=mon-chinh&categories=trang-mieng&requireAllCategories=true` | 200, 1 công thức: Xôi xoài |
| `tags=nhanh&tags=chay&requireAllTags=true` | 200, 2 công thức: Gỏi cuốn chay, Sinh tố bơ |
| `tags=nhanh&tags=chay&requireAllTags=false` | 200, 6 công thức: Bún chả, Chè đậu, Gỏi cuốn chay, Sinh tố bơ, Trà đá, Xôi xoài |
| `categories=mon-chinh&tags=chay` | 200, 2 công thức: Gỏi cuốn chay, Xôi xoài. Lọc category và tag cùng lúc là phép "và" |
| `orderBy=name&orderDirection=asc` | 200, 12 công thức theo thứ tự: Bánh flan, Bún chả, Chè đậu, Cà phê sữa, Cơm trắng, Gỏi cuốn chay, Lẩu thái, Nước mắm pha, Phở bò, Sinh tố bơ, Trà đá, Xôi xoài; `desc` cho thứ tự ngược lại. **Chè đậu đứng trước Cà phê sữa** vì Mealie so sánh theo mã ký tự: chữ `h` có mã nhỏ hơn chữ `à`, nên "Chè" đứng trước "Cà"; đây không phải thứ tự bảng chữ cái tiếng Việt, khi viết kết quả mong đợi phải dùng đúng thứ tự này |
| `orderBy=created_at&orderDirection=asc` | 200, theo thứ tự tạo: Phở bò đầu tiên, Xôi xoài cuối cùng (đúng thứ tự script seed tạo từ 1 đến 12); `desc` cho thứ tự ngược lại. Thứ tự này phụ thuộc vào lần nạp seed trên máy chạy |
| `orderBy=name&orderDirection=asc&perPage=2&page=2` | 200, 2 công thức (Chè đậu, Cà phê sữa), `total` 12, `total_pages` 6 |
| `orderBy=random&paginationSeed=abc123`, gọi hai lần | 200, hai lần cùng thứ tự |
| `search=pho` | 200, 1 công thức: Phở bò |
| `search=bò` | 200, 2 công thức: Phở bò và Sinh tố bơ. Tìm kiếm **không phân biệt dấu**, nên "bò" khớp cả "bơ"; `search=bo` cho cùng kết quả |
| `search=xyzkhongco` | 200, `items` rỗng, `total` 0 |

### Khi sai

| Gọi | Kết quả |
| --- | --- |
| `orderBy=random` không có `paginationSeed` | 422, `paginationSeed is required when orderBy is random` |
| `orderBy=khongtontai` | 400, `Invalid order_by statement "khongtontai": "khongtontai" is invalid` |
| `orderBy=name&orderDirection=sai` | 422, `Input should be 'asc' or 'desc'` |
| `perPage=abc` | 422, `Input should be a valid integer` |

### Hành vi cần chú ý

| Gọi | Kết quả |
| --- | --- |
| `categories=khong-ton-tai` | **200**, trả về cả 12 công thức (không lọc) thay vì rỗng |
| `perPage=0` | **200**, `items` rỗng, `total_pages` 0 |
| `perPage=-1` | **200**, trả về tất cả 12 công thức |

## 4. Luồng phân quyền

### Tạo user

- **Gọi:** `POST /api/admin/users`
- **Quyền cần có:** admin
- **Gửi:**

```json
{
  "username": "u1", "fullName": "User 1", "email": "u1@example.com", "password": "MatKhau@123",
  "group": "Home", "household": "Family",
  "admin": false, "canInvite": false, "canManage": false, "canManageHousehold": false, "canOrganize": false
}
```

- **Nhận:** 201, JSON của user kèm `id` và các cờ đã lưu. Tạo với `admin: true` thì JSON trả về có cả `canInvite`, `canManage`, `canManageHousehold`, `canOrganize` và `advanced` đều là `true` (Mealie tự bật, hàm `_set_permissions`).
- **Khi sai:** 403 nếu người gọi không phải admin; 409 nếu trùng username hoặc email

`group` và `household` là tên, lấy từ `GET /api/users/self` của tài khoản admin (`Home` và `Family` với Mealie mới cài). Sau đó đăng nhập bằng user vừa tạo (mục 1) rồi thực hiện hành động.

### Sáu hành động

| Hành động trong model | Gọi | Gửi | Nhận khi đủ quyền | Cờ quyết định |
| --- | --- | --- | --- | --- |
| `createCategory` | `POST /api/organizers/categories` | `{"name": "Tên không trùng"}` | 201 | `canOrganize` |
| `updateHouseholdPrefs` | `PUT /api/households/preferences` | JSON 9 trường (mục 2) | 200 | `canManageHousehold` |
| `listMembers` | `GET /api/households/members` | | 200 | `canManage` |
| `setMemberPermissions` | `PUT /api/households/permissions` | `{"userId": "<id user khác>", "canInvite": false, "canManage": false, "canManageHousehold": false, "canOrganize": false}` | 200 | `canManage` |
| `createInvite` | `POST /api/households/invitations` | `{"uses": 1}` | 201 | `canInvite` |
| `adminListUsers` | `GET /api/admin/users` | | 200 | `admin` |

Thiếu quyền thì nhận 403: `{"detail": "Forbidden"}`, riêng `createInvite` nhận `{"detail": "User is not allowed to create invite tokens"}`.

`setMemberPermissions` còn có hai kết quả khác: 403 `User is not allowed to change their own permissions` khi `userId` là chính người gọi, 404 `User not found` khi không có user đó. Vì vậy case "thành công" phải nhắm vào một user khác cùng household.

### Kết quả theo loại user

| User được tạo với | createCategory | updateHouseholdPrefs | listMembers | setMemberPermissions | createInvite | adminListUsers |
| --- | --- | --- | --- | --- | --- | --- |
| không quyền nào | 403 | 403 | 403 | 403 | 403 | 403 |
| chỉ `canOrganize` | 201 | 403 | 403 | 403 | 403 | 403 |
| chỉ `canManageHousehold` | 403 | 200 | 403 | 403 | 403 | 403 |
| chỉ `canManage` | 403 | 403 | 200 | 200 | 403 | 403 |
| chỉ `canInvite` | 403 | 403 | 403 | 403 | 201 | 403 |
| đủ 4 quyền, không admin | 201 | 200 | 200 | 200 | 201 | 403 |
| chỉ `admin: true` | 201 | 200 | 200 | 200 | 201 | 200 |

Quy tắc rút ra: hành động thành công khi user có cờ tương ứng **hoặc là admin**; `adminListUsers` chỉ phụ thuộc vào `admin`.

### Hành vi bất thường: tạo tool không cần quyền

Cùng các user trên, `POST /api/organizers/tools` với `{"name": "..."}` trả về **201 ngay cả với user không có quyền nào**, trong khi `POST /api/organizers/tags` và `POST /api/organizers/categories` trả 403 khi thiếu `canOrganize`. Trong mã nguồn, controller của tool (`routes/organizers/controller_tools.py`) không gọi `self.checks.can_organize()` như category và tag. Chưa kết luận được đây là lỗi hay chủ ý; nếu test của nhóm tái hiện được thì đưa vào mục G.

## Dọn dẹp sau khi thử

Xóa các user thử tại `http://localhost:9925/admin/manage/users`, xóa category và tag thử tại `http://localhost:9925/group/data/categories` và `/group/data/tags`, xóa công thức thử. Giữ nguyên bộ dữ liệu mẫu 12 công thức, 3 category, 3 tag của TV2 (xem [seed-data.md](seed-data.md)). Cấu hình household sau khi thử nên trả về như ban đầu (`PUT` lại 9 giá trị đã đọc ở đầu mục 2).
