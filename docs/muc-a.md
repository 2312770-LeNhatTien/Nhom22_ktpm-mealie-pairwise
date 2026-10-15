# Mục A. Phân tích hệ thống

Hệ thống được phân tích là Mealie, phiên bản `v3.28.0` (commit `0552eaa4a80031b8572849cca0ed95d07f1be001`). Mọi nhận xét trong mục này đều dựa trên đúng phiên bản đó.

## A.1 Mục tiêu hệ thống

Mealie là một ứng dụng web quản lý công thức nấu ăn, mã nguồn mở (giấy phép AGPL), do người dùng tự cài trên máy hoặc máy chủ của mình. Dự án tự giới thiệu là "a self hosted recipe manager, meal planner and shopping list", tức là gom ba việc vào một chỗ: lưu công thức, lên kế hoạch bữa ăn và lập danh sách đi chợ.

Bài toán Mealie giải quyết khá quen thuộc với một gia đình. Công thức nấu ăn thường nằm rải rác ở nhiều trang web, ảnh chụp, ghi chú. Khi cần lên thực đơn cho cả tuần thì phải tìm lại từng món, rồi tự chép nguyên liệu ra giấy để đi chợ. Mealie cho phép dán đường dẫn của một trang công thức để hệ thống tự lấy tên món, nguyên liệu và các bước về, hoặc nhập tay những công thức của gia đình. Từ kho công thức đó, người dùng xếp món vào từng ngày và tạo danh sách mua sắm dùng chung cho cả nhà.

Người dùng mà Mealie nhắm tới là một gia đình hoặc một nhóm nhỏ dùng chung một bản cài đặt, không phải một dịch vụ công cộng. Vì vậy hệ thống có sẵn cơ chế chia người dùng thành nhóm và hộ gia đình, kèm phân quyền cho từng người.

Các nhóm chức năng chính:

| Nhóm chức năng | Nội dung |
| --- | --- |
| Công thức | Tạo bằng tay, nhập từ URL, nhập từ ứng dụng khác (Nextcloud, Paprika, Tandoor...), sửa, xóa, bình luận, đánh giá, chia sẻ bằng link |
| Tổ chức | Gắn category, tag, dụng cụ cho công thức; gom công thức thành sổ (cookbook) |
| Tìm kiếm | Tìm theo từ khóa, lọc theo category và tag, sắp xếp, phân trang |
| Kế hoạch bữa ăn | Xếp món vào từng ngày, theo từng bữa |
| Danh sách mua sắm | Lập danh sách, thêm nguyên liệu từ công thức |
| Người dùng | Nhiều người dùng, chia theo group và household, phân quyền từng người |
| Quản trị | Quản lý user, group, household, sao lưu và khôi phục dữ liệu |
| REST API | Mọi chức năng trên đều gọi được qua API. Trang `/docs` của bản `v3.28.0` liệt kê 266 thao tác trên 182 đường dẫn |

Về mặt kỹ thuật, Mealie gồm một backend viết bằng Python (FastAPI) cung cấp REST API và một giao diện web viết bằng Vue. Giao diện chỉ là một ứng dụng gọi vào API đó. Đây là lý do nhóm chọn kiểm thử qua API: test gọi đúng vào nơi xử lý nghiệp vụ, không phụ thuộc vào giao diện.

Hai khái niệm riêng của Mealie xuất hiện trong cả ba luồng kiểm thử:

- **Group:** một nhóm lớn dùng chung kho công thức, category và tag. Bản cài mặc định có sẵn group tên `Home`.
- **Household:** một hộ gia đình nằm trong group. Mỗi user thuộc đúng một household. Kế hoạch bữa ăn và danh sách mua sắm là của riêng từng household. Bản cài mặc định có sẵn household tên `Family`. Mỗi household có một bộ cài đặt riêng, trong đó có các giá trị mặc định áp cho công thức mới.

## A.2 Actor

Hệ thống có năm actor chính và một actor phụ.

| Actor | Là ai | Làm được gì |
| --- | --- | --- |
| Khách | Người chưa đăng nhập | Xem công thức được để công khai, hoặc mở công thức qua link chia sẻ |
| Người dùng | Người đã đăng nhập, không có quyền riêng nào | Tạo, sửa, tìm công thức; lập kế hoạch bữa ăn; danh sách mua sắm; sổ công thức; bình luận, đánh giá; tạo API token cho mình |
| Người dùng có quyền riêng | Người dùng được cấp thêm một hoặc nhiều trong 4 quyền | Mọi việc của người dùng, cộng với việc mà quyền đó cho phép (bảng dưới) |
| Admin | Quản trị viên của bản cài đặt | Mọi việc ở trên, cộng với quản lý user, group, household, sao lưu và cài đặt hệ thống |
| Ứng dụng gọi API | Một chương trình gọi REST API thay cho người dùng bằng token | Làm được đúng những gì user cấp token làm được. Script test của nhóm thuộc loại này |
| Trang web công thức (actor phụ) | Trang web bên ngoài | Cung cấp nội dung khi người dùng nhập công thức từ URL |

Bốn quyền riêng mà admin hoặc người quản lý có thể cấp cho một user:

| Quyền (tên trong API) | Cho phép |
| --- | --- |
| `canOrganize` | Tạo, sửa, xóa category và tag |
| `canManageHousehold` | Đổi cài đặt của household |
| `canManage` | Xem danh sách thành viên, đặt quyền cho thành viên khác, đổi cài đặt của group |
| `canInvite` | Tạo lời mời để người mới đăng ký vào household |

Một số điểm rút ra khi đối chiếu với mã nguồn và gọi thử API:

- Bản cài của nhóm tắt tự đăng ký (`ALLOW_SIGNUP: "false"`), nên tài khoản mới chỉ có khi admin tạo hoặc khi có lời mời.
- Khi tạo user với `admin` bật, Mealie tự bật luôn cả 4 quyền riêng. Vì vậy admin luôn làm được mọi việc của người dùng có quyền riêng.
- Người dùng không có quyền nào vẫn tạo được công thức, kế hoạch bữa ăn và danh sách mua sắm. Việc bị chặn là những việc ảnh hưởng tới cả nhóm: gọi API tạo category bị từ chối với mã 403.
- Khách chỉ xem được một công thức khi **cả ba** điều kiện cùng đúng: group không để riêng tư, household không để riêng tư (`privateHousehold` tắt) và công thức được đánh dấu công khai. Mặc định group để riêng tư, nên bản mới cài không cho khách xem gì.
- Link chia sẻ là ngoại lệ: người có link mở được công thức đó dù household đang để riêng tư.

Các quyền được kiểm tra ở tầng API, trong lớp `OperationChecks` của `mealie/routes/_base/checks.py` và hàm `get_admin_user` của `mealie/core/dependencies/dependencies.py`.

## A.3 Use case

![Hình. Sơ đồ use case của Mealie và phạm vi kiểm thử của nhóm](so-do/use-case.png)

Sơ đồ có 9 use case đại diện cho các nhóm chức năng ở A.1. Mũi tên đầu tam giác rỗng giữa các actor là quan hệ kế thừa: Admin làm được mọi việc của người dùng có quyền riêng, người dùng có quyền riêng làm được mọi việc của người dùng. Ba use case tô vàng là phạm vi kiểm thử của nhóm. Actor "Script test của nhóm" ở bên phải là chương trình gọi REST API thay cho người dùng; trên sơ đồ nó chỉ được nối với ba use case mà nhóm kiểm thử.

| Mã | Use case | Actor | Mô tả ngắn | API chính |
| --- | --- | --- | --- | --- |
| UC1 | Xem công thức công khai | Khách | Xem công thức mà không cần đăng nhập, khi group, household và công thức đều để công khai | `GET /api/explore/groups/{group}/recipes` |
| UC2 | Quản lý công thức | Người dùng, trang web công thức | Tạo bằng tay hoặc nhập từ URL, sửa, xóa | `POST /api/recipes`, `POST /api/recipes/create/url` |
| **UC3** | **Tìm kiếm và lọc công thức** | Người dùng | Tìm theo từ khóa, lọc theo category và tag, sắp xếp, phân trang | `GET /api/recipes` |
| UC4 | Lập kế hoạch bữa ăn và danh sách mua sắm | Người dùng | Xếp món vào ngày, lập danh sách đi chợ | `/api/households/mealplans`, `/api/households/shopping/lists` |
| UC5 | Quản lý category và tag | Người dùng có quyền `canOrganize` | Tạo, sửa, xóa category và tag dùng chung trong group | `POST /api/organizers/categories` |
| **UC6** | **Cấu hình household** | Người dùng có quyền `canManageHousehold` | Đổi 9 tùy chọn của household, trong đó 5 tùy chọn là giá trị mặc định cho công thức mới | `PUT /api/households/preferences` |
| **UC7** | **Phân quyền cho thành viên** | Người dùng có quyền `canManage` | Xem thành viên của household và bật, tắt 4 quyền riêng của từng người | `PUT /api/households/permissions` |
| UC8 | Mời thành viên mới | Người dùng có quyền `canInvite` | Tạo lời mời để người mới đăng ký | `POST /api/households/invitations` |
| UC9 | Quản trị hệ thống | Admin | Quản lý user, group, household; sao lưu và khôi phục | `/api/admin/users`, `/api/admin/backups` |

Nhóm chọn UC3, UC6 và UC7 vì cả ba đều là nơi nhiều tham số độc lập gặp nhau trong một lần xử lý, đúng loại bài toán mà kỹ thuật Pairwise nhắm tới:

- **UC3 Tìm kiếm và lọc:** một API nhận cùng lúc 9 tham số (từ khóa, category, tag, hai cờ "bắt buộc đủ", cột sắp xếp, chiều sắp xếp, seed, kích thước trang). Thử hết cần 5.832 tổ hợp hợp lệ.
- **UC6 Cấu hình household:** 9 tùy chọn đi cùng nhau, thử hết cần 1.792 tổ hợp. Kết quả kiểm tra được rõ ràng: công thức tạo sau khi lưu cấu hình phải nhận đúng 5 giá trị mặc định. Luồng này nối UC6 với UC2.
- **UC7 Phân quyền:** 5 cờ (admin và 4 quyền riêng) kết hợp với 6 hành động, tổng cộng 192 tổ hợp. Test không chỉ gọi UC7 mà kiểm tra hệ quả của nó: với mỗi bộ quyền, hệ thống phải cho phép hoặc từ chối đúng các hành động thuộc UC5, UC6, UC7, UC8 và UC9.

Các use case còn lại (UC1, UC2, UC4, UC5, UC8, UC9) nằm ngoài phạm vi, chỉ được dùng tới khi một luồng kiểm thử cần, ví dụ tạo công thức trong luồng household.

## A.4 Cây thư mục và module

Số liệu đếm trên tag `v3.28.0` (commit `0552eaa4a80031b8572849cca0ed95d07f1be001`): backend có **463** file Python trong `mealie/`, giao diện có **227** file `.vue` trong `frontend/`, và dự án có sẵn **137** file test `test_*.py` trong `tests/`.

Mealie là một ứng dụng web viết theo kiểu "backend + frontend tách riêng nhưng đóng gói chung": backend Python (FastAPI) cung cấp REST API dưới đường dẫn `/api`, frontend Nuxt/Vue được build thành file tĩnh và chính backend phục vụ các file này, nên khi chạy bằng Docker chỉ có **một container, một cổng**.

### Khái niệm riêng của Mealie: group và household

Mealie tổ chức dữ liệu theo hai cấp. **Group** là nhóm lớn nhất, dùng chung dữ liệu như công thức, category, tag. Trong một group có nhiều **household** (hộ gia đình); mỗi user thuộc đúng một household. Cấu hình household (`/api/households/preferences`) quyết định cài đặt mặc định của công thức mới, và quyền của user (`canManageHousehold`, `canManage`, `canInvite`, `canOrganize`, `admin`) cũng xoay quanh household. Luồng 2 (cấu hình household) và luồng 3 (phân quyền) của nhóm đều dựa trên khái niệm này.

### Bảng module

Tầng nào gọi tầng nào: `routes → services → repos → db`. Thư mục `schema` (kiểu dữ liệu) và `core` (cấu hình, đăng nhập) được các tầng trên dùng chung.

| Thư mục | Vai trò | Liên quan tới kiểm thử của nhóm |
| --- | --- | --- |
| `mealie/routes/` | Tầng API. Mỗi thư mục con là một nhóm API (`recipe/`, `households/`, `users/`, `admin/`, `organizers/`...). Nhận request HTTP, kiểm tra quyền, rồi gọi service hoặc repo. Tất cả được gom dưới tiền tố `/api` trong `routes/__init__.py` | Script test của nhóm gọi vào đây, qua cổng 9925. `routes/_base/checks.py` chứa các phép kiểm tra quyền của luồng phân quyền; `routes/recipe/recipe_crud_routes.py` chứa API tìm kiếm và tạo công thức |
| `mealie/schema/` | Định nghĩa dữ liệu vào và ra bằng Pydantic, kèm luật kiểm tra hợp lệ. Request sai luật bị từ chối với lỗi 422 hoặc 400 trước khi chạm tới nghiệp vụ | Nguồn để biết mỗi API có tham số nào và nhận giá trị nào, nên là **đầu vào để viết model PICT**. Ví dụ `schema/household/household_preferences.py` có 9 tham số của luồng household; `schema/response/pagination.py` có luật "`orderBy=random` thì bắt buộc có `paginationSeed`" |
| `mealie/services/` | Xử lý nghiệp vụ: tạo công thức, nhập từ URL, lên kế hoạch bữa ăn, bộ lọc, lịch chạy nền... | `services/recipe/recipe_service.py` gán cài đặt mặc định cho công thức mới theo cấu hình household (luồng 2); `services/query_filter/` phân tích và dựng bộ lọc (luồng 1) |
| `mealie/repos/` | Tầng truy vấn cơ sở dữ liệu. Mỗi "repository" bọc một bảng và cung cấp các hàm thêm, sửa, xóa, lọc, sắp xếp, phân trang | `repos/repository_generic.py` thực hiện sắp xếp, phân trang của luồng tìm kiếm; `repos/repository_recipes.py` thực hiện lọc theo category, tag |
| `mealie/db/` | Model bảng dữ liệu bằng SQLAlchemy (`db/models/`) và khởi tạo kết nối, chạy nâng cấp cấu trúc (`init_db.py`, `db_setup.py`) | Cho biết dữ liệu lưu ở đâu khi phân tích nguyên nhân lỗi. `db/models/household/preferences.py` là bảng cấu hình household; `db/models/users/users.py` có hàm `_set_permissions` quyết định quyền của user |
| `mealie/core/` | Cấu hình ứng dụng (`core/settings/settings.py`), bảo mật và đăng nhập (`core/security/`, `core/dependencies/`) | Tài khoản mặc định `changeme@example.com` và các biến môi trường nằm trong `settings.py`. `get_admin_user` trong `core/dependencies/dependencies.py` chặn người không phải admin |
| `mealie/alembic/` | 53 bước nâng cấp cấu trúc cơ sở dữ liệu giữa các phiên bản | Không kiểm thử, chỉ nhắc tên |
| `frontend/` | Giao diện web: Nuxt 4, Vue 3, Vuetify, TypeScript | Dùng để demo bằng tay. Test của nhóm không đi qua giao diện |
| `tests/` | Test có sẵn của dự án (pytest cho backend, Playwright cho giao diện) | Tham khảo cách dự án gọi API. Nhóm không sửa |

Ngoài ra `mealie/app.py` là điểm khởi động: tạo ứng dụng FastAPI, gắn router `/api`, bật bộ lập lịch (`start_scheduler`) và gắn giao diện (`mount_spa`).

## A.5 Dependency

Phiên bản lấy đúng từ `pyproject.toml` và `frontend/package.json` của tag `v3.28.0`. Chỉ liệt kê các thư viện quan trọng; ba thư viện **in đậm** là những cái ảnh hưởng trực tiếp tới kết quả kiểm thử của nhóm.

### Backend (Python 3.14)

| Thư viện | Phiên bản | Dùng để |
| --- | --- | --- |
| **FastAPI** | 0.141.1 | Khung viết API: khai báo đường dẫn, nhận và trả JSON, tự sinh trang `/docs` mô tả toàn bộ API |
| Uvicorn | 0.53.0 | Máy chủ chạy ứng dụng FastAPI |
| **Pydantic** | 2.13.5 | Kiểm tra và chuyển kiểu dữ liệu vào ra. Lỗi 422 mà API trả về khi dữ liệu sai là do Pydantic báo |
| **SQLAlchemy** | 2.0.54 | Ánh xạ bảng dữ liệu thành lớp Python, sinh câu lệnh SQL |
| Alembic | 1.20.0 | Quản lý các bước nâng cấp cấu trúc cơ sở dữ liệu |
| recipe-scrapers | 15.12.0 | Lấy công thức từ URL của các trang nấu ăn (ngoài phạm vi kiểm thử) |
| bcrypt, PyJWT | 5.0.0, 2.14.0 | Băm mật khẩu; tạo và kiểm tra token đăng nhập |
| Authlib, python-ldap | 1.8.0, 3.4.8 | Đăng nhập qua OIDC và LDAP (nhóm không dùng) |
| Pillow | 12.3.0 | Xử lý ảnh công thức |
| rapidfuzz | 3.14.6 | So khớp chuỗi gần đúng (dùng trong `services/matching.py` để khớp tên nguyên liệu); không liên quan tới ô tìm kiếm công thức |

### Frontend

| Thư viện | Phiên bản | Dùng để |
| --- | --- | --- |
| Nuxt | ^4.4.6 | Khung xây ứng dụng Vue, build ra file tĩnh để backend phục vụ |
| Vue | ^3.5.35 | Thư viện dựng giao diện |
| Vuetify | ^4.1.2 | Bộ thành phần giao diện (nút, bảng, hộp thoại) |
| TypeScript | ^5.3 | Ngôn ngữ viết giao diện, có kiểm tra kiểu |

### Cơ sở dữ liệu

SQLite là mặc định (`DB_ENGINE = "sqlite"` trong `core/settings/settings.py`); có thể đổi sang PostgreSQL nhờ `psycopg2-binary`. Nhóm dùng SQLite, file nằm trong volume `mealie-data` của Docker.

## A.6 Luồng dữ liệu của 3 nghiệp vụ

_Phần của Nguyễn Đình Tuấn._
