# Các API của 3 luồng: kết quả gọi thử

Mọi kết quả trong file này lấy từ việc gọi thật vào backend Mealie `v3.28.0` (commit `0552eaa4a80031b8572849cca0ed95d07f1be001`) chạy từ mã nguồn, chế độ production, cơ sở dữ liệu SQLite. Đây là tài liệu tham khảo: mỗi người vẫn phải tự gọi lại trên Mealie của máy mình và ghi kết quả của mình vào báo cáo.

Địa chỉ gốc: `http://localhost:9925`. Tên trường trong JSON viết kiểu `recipePublic`.

## 1. Đăng nhập

| Gọi | Gửi | Kết quả |
| --- | --- | --- |
| `POST /api/auth/token` | Dạng form, hai trường `username` và `password` | 200, JSON có `access_token`, `token_type` là `bearer`, `expires_in` là `172800` (giây) |
| như trên, sai mật khẩu | | 401, `{"detail": "Unauthorized"}` |
| Gọi một API cần đăng nhập mà không gửi token | | 401, `{"detail": "Could not validate credentials"}` |

- Trường `username` nhận cả email (`nhom22@example.com`) lẫn username (`nhom22`).
- Mọi lần gọi sau gửi kèm header `Authorization: Bearer <access_token>`.
- API đăng nhập còn đặt một cookie phiên. Nếu code test dùng `requests.Session()` thì các lần gọi sau vẫn được coi là đã đăng nhập dù không gửi header. Muốn thử trường hợp "không có token" phải dùng một phiên mới, hoặc gọi thẳng `requests.get(...)`.

## 2. Luồng cấu hình household

| Bước | Gọi | Gửi | Kết quả |
| --- | --- | --- | --- |
| 1 | `GET /api/households/preferences` | | 200, JSON 9 trường và `id` |
| 2 | `PUT /api/households/preferences` | JSON 9 trường | 200, trả về đúng 9 giá trị vừa gửi |
| 3 | `POST /api/recipes` | `{"name": "Tên không trùng"}` | 201, trả về một chuỗi là slug, ví dụ `"thu-f14ed4ab"` |
| 4 | `GET /api/recipes/{slug}` | | 200, JSON công thức, có phần `settings` |
| 5 | `DELETE /api/recipes/{slug}` | | 200 |

Chín trường của bước 2:

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

Với cấu hình trên, công thức tạo ở bước 3 có:

```json
"settings": {"public": true, "showNutrition": true, "showAssets": false,
             "landscapeView": true, "disableComments": true, "locked": false}
```

Quy tắc, đúng với hàm `create_one` trong `mealie/services/recipe/recipe_service.py`:

| Cài đặt của công thức mới | Lấy từ tùy chọn của household |
| --- | --- |
| `settings.public` | `recipePublic` |
| `settings.showNutrition` | `recipeShowNutrition` |
| `settings.showAssets` | `recipeShowAssets` |
| `settings.landscapeView` | `recipeLandscapeView` |
| `settings.disableComments` | `recipeDisableComments` |
| `settings.locked` | luôn là `false` |

Giá trị không hợp lệ:

| Gửi | Kết quả |
| --- | --- |
| `firstDayOfWeek: "abc"` | 422, lỗi "Input should be a valid integer" |
| `recipePublic: "maybe"` | 422, lỗi "Input should be a valid boolean" |
| `firstDayOfWeek: 7` | **200**, Mealie lưu giá trị 7 |
| `firstDayOfWeek: -1` | **200**, Mealie lưu giá trị -1 |
| Body rỗng `{}` | **200**, mọi trường quay về giá trị mặc định |

Một tuần chỉ có các ngày từ 0 đến 6, nhưng API nhận cả 7 và -1. Đây là ứng viên cho danh sách hành vi bất thường.

## 3. Luồng tìm kiếm và lọc

Một lần gọi `GET /api/recipes` với các tham số trên URL.

| Tham số | Giá trị | Ghi chú |
| --- | --- | --- |
| `categories` | id hoặc slug của category, lặp lại tham số để truyền nhiều cái | Slug của "Món chính" là `mon-chinh` |
| `tags` | id hoặc slug của tag | Slug của "Nhanh" là `nhanh` |
| `requireAllCategories`, `requireAllTags` | `true` hoặc `false` | `false`: có ít nhất một cái. `true`: phải có đủ |
| `search` | từ khóa | Tìm gần đúng, xem bên dưới |
| `orderBy` | `name`, `created_at`, `rating`, `random` | |
| `orderDirection` | `asc`, `desc` | |
| `paginationSeed` | chuỗi bất kỳ | Bắt buộc khi `orderBy=random` |
| `page`, `perPage` | số nguyên | |

Kết quả trả về có dạng:

```json
{"page": 1, "per_page": 50, "total": 12, "total_pages": 1, "items": [...], "next": null, "previous": null}
```

Các trường ở lớp ngoài viết kiểu `per_page`, `total_pages`. Mỗi phần tử trong `items` có `name`, `slug`, `recipeCategory`, `tags`.

Kết quả gọi thử trên bộ dữ liệu mẫu 12 công thức (xem [TV2-moi-truong-demo.md](TV2-moi-truong-demo.md)):

| Gọi | Kết quả |
| --- | --- |
| `categories=mon-chinh` | 5 công thức |
| `categories=mon-chinh&categories=trang-mieng&requireAllCategories=false` | 8 công thức |
| `categories=mon-chinh&categories=trang-mieng&requireAllCategories=true` | 1 công thức: Xôi xoài |
| `tags=nhanh&tags=chay&requireAllTags=true` | 2 công thức: Gỏi cuốn chay, Sinh tố bơ |
| `categories=mon-chinh&tags=chay` | 2 công thức: Gỏi cuốn chay, Xôi xoài. Lọc category và tag cùng lúc là phép "và" |
| `orderBy=name&orderDirection=asc` | Bánh flan, Bún chả, Chè đậu, Cà phê sữa, Cơm trắng, ... |
| `perPage=1` | 1 công thức, `total_pages` bằng tổng số |
| `orderBy=random` không có `paginationSeed` | 422, lỗi "paginationSeed is required when orderBy is random" |
| `orderBy=random&paginationSeed=abc123`, gọi hai lần | Hai lần cùng thứ tự |
| `orderBy=khongtontai` | 400, lỗi "Invalid order_by statement" |
| `orderDirection=sai` | 422, lỗi "Input should be 'asc' or 'desc'" |
| `perPage=abc` | 422 |
| `perPage=0` | **200**, không có công thức nào, `total_pages` là 0 |
| `perPage=-1` | **200**, trả về tất cả công thức |
| `categories=khong-ton-tai` | **200**, trả về tất cả 12 công thức |

Tìm theo từ khóa:

| `search` | Kết quả |
| --- | --- |
| `Phở` hoặc `pho` | Phở bò |
| `bò` hoặc `bo` | Phở bò, Sinh tố bơ |
| `Cơm` | Cơm trắng |
| `phở bò trà` | Phở bò, Sinh tố bơ, Trà đá, Cơm trắng |
| `xyzkhongco` | không có công thức nào |

Điều rút ra cho việc viết kết quả mong đợi:

- Tìm kiếm không phân biệt dấu và tìm theo từng từ, chỉ cần khớp một từ. Nên kiểm tra "công thức mong đợi có trong kết quả", không so bằng tuyệt đối.
- Sắp xếp theo tên so theo mã ký tự chứ không theo từ điển tiếng Việt, nên "Chè đậu" đứng trước "Cà phê sữa". Khi kiểm tra thứ tự, hoặc dùng đúng quy tắc này, hoặc chỉ kiểm tra `asc` và `desc` cho ra hai danh sách ngược nhau.
- Lọc theo category không tồn tại trả về tất cả thay vì rỗng. Ứng viên cho danh sách hành vi bất thường.

## 4. Luồng phân quyền

Tạo user, dùng token của admin:

```text
POST /api/admin/users
{"username": "u1", "fullName": "User 1", "email": "u1@example.com", "password": "MatKhau@123",
 "group": "Home", "household": "Family",
 "admin": false, "canInvite": false, "canManage": false, "canManageHousehold": false, "canOrganize": false}
```

Kết quả 201, JSON của user kèm `id`. Sau đó đăng nhập bằng user vừa tạo và thực hiện hành động.

| Hành động trong model | Gọi | Gửi |
| --- | --- | --- |
| `createCategory` | `POST /api/organizers/categories` | `{"name": "Tên không trùng"}` |
| `updateHouseholdPrefs` | `PUT /api/households/preferences` | JSON 9 trường |
| `listMembers` | `GET /api/households/members` | |
| `setMemberPermissions` | `PUT /api/households/permissions` | `{"userId": "<id của một user khác>", "canInvite": false, "canManage": false, "canManageHousehold": false, "canOrganize": false}` |
| `createInvite` | `POST /api/households/invitations` | `{"uses": 1}` |
| `adminListUsers` | `GET /api/admin/users` | |

Status code nhận được với từng loại user:

| User được tạo với | createCategory | updateHouseholdPrefs | listMembers | setMemberPermissions | createInvite | adminListUsers |
| --- | --- | --- | --- | --- | --- | --- |
| không quyền nào | 403 | 403 | 403 | 403 | 403 | 403 |
| chỉ `canOrganize` | 201 | 403 | 403 | 403 | 403 | 403 |
| chỉ `canManageHousehold` | 403 | 200 | 403 | 403 | 403 | 403 |
| chỉ `canManage` | 403 | 403 | 200 | 200 | 403 | 403 |
| chỉ `canInvite` | 403 | 403 | 403 | 403 | 201 | 403 |
| đủ 4 quyền, không admin | 201 | 200 | 200 | 200 | 201 | 403 |
| chỉ `admin: true` | 201 | 200 | 200 | 200 | 201 | 200 |

Quy tắc:

- Hành động thành công khi user có cờ tương ứng **hoặc** là admin.
- Tạo user với `admin: true` thì Mealie tự bật cả 4 cờ còn lại. JSON trả về lúc tạo đã cho thấy điều đó (hàm `_set_permissions` trong `mealie/db/models/users/users.py`).
- `adminListUsers` chỉ phụ thuộc vào `admin`.
- Bị từ chối thì nhận 403 với `{"detail": "Forbidden"}`. Riêng tạo lời mời nhận `{"detail": "User is not allowed to create invite tokens"}`.

Một điểm lệch quan sát được: tạo category và tag cần `canOrganize`, nhưng `POST /api/organizers/tools` trả về **201 với cả user không có quyền nào**. Trên giao diện, quyền này được ghi là "User can manage foods, tags, and categories", không nhắc tới tool. Chưa kết luận được đây là lỗi hay chủ ý; ứng viên cho danh sách hành vi bất thường.

## 5. Danh sách hành vi đáng chú ý

Gom lại để người giữ luồng tái hiện bằng test của mình ở giai đoạn sau. Chỉ đưa vào báo cáo những gì test của nhóm đã tái hiện được.

| # | Luồng | Hành vi |
| --- | --- | --- |
| 1 | Household | `firstDayOfWeek` nhận 7 và -1 |
| 2 | Household | `PUT` với body rỗng đưa mọi trường về mặc định mà không báo lỗi |
| 3 | Tìm kiếm | Lọc theo category không tồn tại trả về tất cả |
| 4 | Tìm kiếm | `perPage=-1` trả về tất cả, `perPage=0` trả về danh sách rỗng |
| 5 | Tìm kiếm | Tìm `bò` ra cả "Sinh tố bơ" |
| 6 | Tìm kiếm | Sắp xếp theo tên không theo thứ tự từ điển tiếng Việt |
| 7 | Phân quyền | Tạo tool không cần quyền `canOrganize` |
