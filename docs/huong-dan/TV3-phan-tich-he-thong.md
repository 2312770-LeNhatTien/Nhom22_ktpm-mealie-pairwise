# TV3 Phân tích hệ thống: Hồ Quốc Tiến

Sản phẩm của bạn là hai đề mục A.4, A.5 trong `docs/muc-a.md` và toàn bộ `docs/muc-b.md`. Thầy không yêu cầu hiểu hết code. Chỉ cần nắm cấu trúc chung và 3–5 module đụng tới phần kiểm thử.

## Việc 1. Lấy mã nguồn đúng phiên bản

Mã nguồn Mealie không nằm trong repo nhóm, clone riêng ra một thư mục khác:

```bat
D:
git clone --branch v3.28.0 --depth 1 https://github.com/mealie-recipes/mealie.git
cd mealie
git rev-parse HEAD
```

Lệnh cuối phải in ra `0552eaa4a80031b8572849cca0ed95d07f1be001`. Chụp lại dòng này, lưu thành `docs/evidence/A-01-sha.png`. Mở thư mục `mealie` bằng VS Code để đọc.

## Việc 2. Đọc theo thứ tự này

Đọc lướt để biết mỗi nơi chứa gì, không đọc từng dòng.

1. `README.md`: Mealie tự giới thiệu là gì.
2. `pyproject.toml`: danh sách thư viện backend.
3. `mealie/app.py`: nơi ứng dụng khởi động, gắn các router, bật bộ lập lịch, gắn giao diện.
4. `mealie/routes/`: mỗi thư mục con là một nhóm API.
5. Một luồng đi xuyên các tầng. Lấy luồng cấu hình household làm mẫu:
   - `mealie/routes/households/controller_household_self_service.py`, hàm `update_household_preferences`: nhận request, kiểm tra quyền.
   - `mealie/schema/household/household_preferences.py`: định nghĩa 9 trường của cấu hình.
   - `mealie/repos/`: tầng ghi xuống cơ sở dữ liệu.
   - `mealie/db/models/household/preferences.py`: bảng dữ liệu.

Mẹo tìm trong VS Code: bấm **Ctrl + Shift + F** rồi gõ tên hàm hoặc đường dẫn API, ví dụ `/preferences`.

## Việc 3. Viết A.4 Cây thư mục và module

Số liệu đếm trên tag `v3.28.0`: backend có 463 file Python trong `mealie/`, giao diện có 227 file `.vue`, dự án có sẵn 137 file test.

Bảng dưới đây là khung. Giữ cột đầu, viết lại hai cột sau bằng lời của bạn sau khi đã mở từng thư mục ra xem.

| Thư mục | Vai trò | Liên quan tới kiểm thử của nhóm |
| --- | --- | --- |
| `mealie/routes/` | Tầng API: nhận request HTTP, kiểm tra quyền, gọi service | Script test gọi vào đây. `routes/_base/checks.py` chứa các phép kiểm tra quyền của luồng phân quyền |
| `mealie/schema/` | Định nghĩa dữ liệu vào và ra bằng Pydantic, kèm luật kiểm tra hợp lệ | Nguồn để biết mỗi API có tham số nào, nhận giá trị nào. Đây là đầu vào để viết model PICT |
| `mealie/services/` | Xử lý nghiệp vụ | `services/recipe/recipe_service.py` gán cài đặt mặc định cho công thức mới theo household; `services/query_filter/` xử lý bộ lọc |
| `mealie/repos/` | Tầng truy vấn cơ sở dữ liệu | `repos/repository_generic.py` thực hiện phân trang và sắp xếp của luồng tìm kiếm |
| `mealie/db/` | Model bảng dữ liệu (SQLAlchemy) và khởi tạo DB | Cho biết dữ liệu lưu ở đâu. `db/models/users/users.py` có hàm `_set_permissions` quyết định quyền của user |
| `mealie/core/` | Cấu hình, bảo mật, đăng nhập | Tài khoản có sẵn và các biến môi trường nằm trong `core/settings/settings.py` |
| `mealie/alembic/` | Các bước nâng cấp cấu trúc DB | Không kiểm thử, chỉ nhắc tên |
| `frontend/` | Giao diện web | Dùng để demo. Test của nhóm không đi qua đây |
| `tests/` | Test có sẵn của dự án (pytest, Playwright) | Tham khảo cách họ gọi API. Nhóm không sửa |

## Việc 4. Viết A.5 Dependency

Lập bảng thư viện chính, mỗi cái một dòng nói nó dùng để làm gì. Phiên bản lấy đúng từ `pyproject.toml` và `frontend/package.json` của tag `v3.28.0`.

Backend (Python 3.14):

| Thư viện | Dùng để |
| --- | --- |
| FastAPI | Khung viết API: khai báo đường dẫn, nhận và trả JSON, tự sinh trang `/docs` |
| Uvicorn | Máy chủ chạy ứng dụng FastAPI |
| Pydantic | Kiểm tra và chuyển kiểu dữ liệu vào ra. Lỗi 422 mà API trả về là do Pydantic báo |
| SQLAlchemy | Ánh xạ bảng dữ liệu thành lớp Python, sinh câu lệnh SQL |
| Alembic | Quản lý các bước nâng cấp cấu trúc cơ sở dữ liệu |
| recipe-scrapers | Lấy công thức từ URL của các trang nấu ăn |
| bcrypt, PyJWT | Băm mật khẩu, tạo và kiểm tra token đăng nhập |
| Authlib, python-ldap | Đăng nhập qua OIDC và LDAP (nhóm không dùng) |
| Pillow | Xử lý ảnh công thức |
| rapidfuzz | So khớp chuỗi gần đúng |

Frontend: Nuxt 4, Vue 3, Vuetify 4, TypeScript.

Cơ sở dữ liệu: SQLite mặc định, có thể đổi sang PostgreSQL. Nhóm dùng SQLite.

Chỉ cần 8–10 thư viện quan trọng, không liệt kê hết. Tô đậm những cái liên quan tới kiểm thử: FastAPI, Pydantic, SQLAlchemy.

## Việc 5. Vẽ sơ đồ kiến trúc (mục B)

Dùng draw.io ở https://app.diagrams.net. Vẽ sơ đồ mức container, tức là các khối chạy được và đường nối giữa chúng.

Các khối cần có:

1. **Người dùng và trình duyệt.** Gọi tới cổng 9925 bằng HTTP.
2. **Script test của nhóm (pytest).** Cũng gọi tới cổng 9925 nhưng đi thẳng vào API. Vẽ khối này bằng màu khác để thấy nhóm kiểm thử ở đâu.
3. **Container Mealie.** Vẽ thành một khung lớn, bên trong có:
   - Giao diện: file tĩnh do chính backend phục vụ (hàm `mount_spa` trong `mealie/routes/spa/__init__.py`).
   - API FastAPI, chia ba tầng xếp dọc: Routes → Services → Repos.
   - Bộ lập lịch chạy nền (hàm `start_scheduler` trong `mealie/app.py`).
4. **Volume `mealie-data`.** File SQLite và ảnh công thức. Nối với tầng Repos bằng mũi tên ghi "SQL".
5. **Trang web bên ngoài.** Mealie tải công thức từ URL khi người dùng nhập link. Ghi chú "ngoài phạm vi kiểm thử".

Cách vẽ:

1. Kéo hình chữ nhật từ khung bên trái, bấm đúp để gõ tên.
2. Khung lớn chứa các khối con: vẽ một hình chữ nhật to, đưa nó xuống dưới cùng bằng chuột phải → **To Back**.
3. Mũi tên: rê chuột vào cạnh một khối, kéo từ chấm xanh sang khối kia. Bấm đúp vào mũi tên để ghi giao thức.
4. **File → Save** thành `docs/so-do/kien-truc.drawio`. **File → Export as → PNG**, tích **Transparent Background** bỏ đi để nền trắng, lưu thành `docs/so-do/kien-truc.png`.

Dưới hình viết 3–4 câu đọc sơ đồ: request đi từ đâu, qua những tầng nào, dữ liệu nằm ở đâu, nhóm kiểm thử ở điểm nào.

## Việc 6. Giải thích 5 module (mục B)

Chọn 5 dòng đầu của bảng ở Việc 3. Với mỗi module viết một đoạn 4–6 câu theo mẫu:

- Module này làm gì.
- File và hàm quan trọng nhất, ghi tên thật.
- Luồng nào của nhóm đi qua nó, đi qua như thế nào.

Tên file và hàm thật để dẫn, đã đối chiếu với mã nguồn `v3.28.0`:

| Luồng | Routes | Services, kiểm tra | Repos, DB |
| --- | --- | --- | --- |
| Tìm kiếm và lọc | `routes/recipe/recipe_crud_routes.py`, hàm `get_all` | `services/query_filter/` | `repos/repository_generic.py`, hàm `add_order_by_to_query` |
| Cấu hình household | `routes/households/controller_household_self_service.py`, hàm `update_household_preferences`; `routes/recipe/recipe_crud_routes.py`, hàm `create_one` | `services/recipe/recipe_service.py`, hàm `create_one` đọc cấu hình household để gán cài đặt cho công thức mới | `db/models/household/preferences.py` |
| Phân quyền | controller của từng hành động | `routes/_base/checks.py`, lớp `OperationChecks`; `core/dependencies/dependencies.py`, hàm `get_admin_user` | `db/models/users/users.py`, hàm `_set_permissions` |

Khung cho `docs/muc-b.md`:

```markdown
# Mục B. Kiến trúc hệ thống

## B.1 Sơ đồ kiến trúc

![Hình. Sơ đồ kiến trúc mức container của Mealie](so-do/kien-truc.png)

<3–4 câu đọc sơ đồ>

## B.2 Các module liên quan tới kiểm thử

### B.2.1 Routes
### B.2.2 Schema
### B.2.3 Services
### B.2.4 Repos
### B.2.5 DB
```

## Tự kiểm tra trước khi mở Pull Request

- Đưa sơ đồ cho một bạn chưa đọc code. Bạn đó kể lại được "request đi từ đâu tới đâu" là đạt.
- Mỗi module trong bảng trả lời được câu hỏi "nó liên quan gì tới phần kiểm thử của nhóm".
- Mọi tên file và tên hàm trong bài đều mở ra được trong mã nguồn.
