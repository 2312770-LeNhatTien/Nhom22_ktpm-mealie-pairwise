# TV5 API và tự động hóa: Nguyễn Đình Tuấn

Sản phẩm của bạn gồm bốn thứ: `docs/api-3-luong.md` (bảng request và response của 3 luồng), đề mục A.6 trong `docs/muc-a.md` kèm 3 sơ đồ luồng dữ liệu, và script mẫu trong `tests/` chạy được 16 case của luồng household.

Làm theo thứ tự từ Việc 1 đến Việc 6. Việc sau dùng kết quả của việc trước.

## Việc 1. Cài Python và môi trường chạy test

Mở Command Prompt ở thư mục gốc của repo:

```bat
python --version
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest --version
```

- Dòng 2 tạo thư mục `.venv` chứa một bản Python riêng cho repo này. Thư mục đó đã nằm trong `.gitignore`, không bị commit.
- Dòng 3 bật môi trường. Đầu dòng lệnh hiện thêm chữ `(.venv)` là đã bật. **Mỗi lần mở Command Prompt mới phải gõ lại dòng này.**
- Dòng 4 cài `pytest` và `requests` đúng phiên bản ghi trong `requirements.txt`.

Thử chạy khi chưa có test nào:

```bat
pytest tests -v
```

In ra `no tests ran` là môi trường đã sẵn sàng.

Hai thư viện dùng trong đề tài:

| Thư viện | Dùng để |
| --- | --- |
| `requests` | Gửi request HTTP tới Mealie và đọc kết quả |
| `pytest` | Tìm các hàm tên bắt đầu bằng `test_`, chạy từng hàm, báo cái nào đạt, cái nào hỏng |

## Việc 2. Gọi thử API trên trang /docs

Mealie tự sinh một trang liệt kê toàn bộ API và cho bấm gọi thử.

1. Chạy Mealie, mở http://localhost:9925/docs.
2. Bấm nút **Authorize** ở góc trên bên phải.
3. Điền `username` là `nhom22@example.com`, `password` là `Nhom22@Mealie`. Các ô `client_id`, `client_secret` để trống. Bấm **Authorize**, rồi **Close**.
4. Kéo xuống nhóm **Households: Self Service**, mở dòng `GET /api/households/preferences`.
5. Bấm **Try it out**, rồi **Execute**.
6. Xem phần **Server response**: mã 200 và một đoạn JSON có 9 trường cấu hình.

Chụp màn hình kết quả, lưu thành `docs/evidence/F-00-docs.png`.

Mỗi API trên trang này cho biết ba thứ bạn cần ghi lại: đường dẫn và method, các tham số hoặc body phải gửi (phần **Parameters** và **Request body**), và dạng kết quả trả về (phần **Responses**).

## Việc 3. Lấy token và gọi API từ dòng lệnh

Script test không bấm nút được, nó phải tự đăng nhập. Mealie đăng nhập bằng token: gửi tài khoản và mật khẩu một lần, nhận về một chuỗi dài, các lần gọi sau gửi kèm chuỗi đó.

Trong Command Prompt (gõ `curl.exe`, có đuôi `.exe`):

```bat
curl.exe -X POST http://localhost:9925/api/auth/token -d "username=nhom22@example.com&password=Nhom22@Mealie"
```

Kết quả:

```json
{"access_token":"eyJhbGciOi...","token_type":"bearer","expires_in":172800}
```

Chép chuỗi trong `access_token` (không lấy dấu ngoặc kép), dán vào chỗ `TOKEN`:

```bat
curl.exe http://localhost:9925/api/households/preferences -H "Authorization: Bearer TOKEN"
```

Cùng việc đó viết bằng Python. Tạo tạm file `thu_api.py` ở thư mục gốc của repo. File này chỉ để tập, **không commit**, thử xong thì xóa:

```python
import requests

BASE_URL = "http://localhost:9925"

# 1. Đăng nhập để lấy token
r = requests.post(
    f"{BASE_URL}/api/auth/token",
    data={"username": "nhom22@example.com", "password": "Nhom22@Mealie"},
    timeout=10,
)
print("Đăng nhập:", r.status_code)
headers = {"Authorization": "Bearer " + r.json()["access_token"]}

# 2. Đọc cấu hình household
r = requests.get(f"{BASE_URL}/api/households/preferences", headers=headers, timeout=10)
print("Cấu hình household:", r.status_code)
print(r.json())
```

```bat
python thu_api.py
```

In ra hai dòng có số 200 và một đoạn cấu hình là đạt. Đọc hiểu từng dòng của file này trước khi sang việc sau, vì script test chỉ là đoạn này lặp lại nhiều lần và thêm bước so sánh.

| Viết trong Python | Ý nghĩa |
| --- | --- |
| `requests.post(url, data={...})` | Gửi dạng form. API đăng nhập dùng dạng này |
| `requests.put(url, json={...})` | Gửi dạng JSON. Hầu hết API còn lại dùng dạng này |
| `headers={"Authorization": "Bearer ..."}` | Gắn token để Mealie biết ai đang gọi |
| `r.status_code` | Mã kết quả: 200, 201 là thành công; 401 chưa đăng nhập; 403 không đủ quyền; 422 dữ liệu sai dạng |
| `r.json()` | Kết quả trả về, đã đổi thành dict hoặc list của Python |

## Việc 4. Ghi request và response của 3 luồng

Sản phẩm: `docs/api-3-luong.md`. Tự tay gọi từng API trên máy mình bằng trang `/docs` hoặc bằng Python, rồi ghi lại. Bảng tham khảo đã gọi thử trước nằm ở [api-da-kiem-chung.md](api-da-kiem-chung.md); kết quả của bạn phải khớp với bảng đó, chỗ nào không khớp thì báo trong nhóm.

Số lần gọi cần ghi:

| Luồng | Cần ghi |
| --- | --- |
| Cấu hình household | 4 lần gọi: lưu cấu hình, tạo công thức, đọc công thức, xóa công thức |
| Tìm kiếm và lọc | 1 API `GET /api/recipes`, ghi từng tham số và 4–5 ví dụ gọi |
| Phân quyền | Tạo user, đăng nhập bằng user đó, rồi 6 hành động |

Mẫu ghi cho một lần gọi:

````markdown
### Lưu cấu hình household

- **Gọi:** `PUT /api/households/preferences`
- **Quyền cần có:** `canManageHousehold`
- **Gửi:**

```json
{"privateHousehold": false, "firstDayOfWeek": 3, "recipePublic": true}
```

- **Nhận:** 200, JSON gồm 9 trường vừa gửi và `id`
- **Khi sai:** 403 nếu không đủ quyền; 422 nếu `firstDayOfWeek` không phải số
````

Để thử luồng phân quyền trên trang `/docs`: tạo user bằng `POST /api/admin/users`, bấm **Authorize → Logout**, rồi **Authorize** lại bằng user vừa tạo. Xong nhớ đăng nhập lại bằng tài khoản dùng chung.

Dọn dẹp sau khi thử: xóa các user thử ở `http://localhost:9925/admin/manage/users`, xóa category thử ở `http://localhost:9925/group/data/categories`.

## Việc 5. Vẽ luồng dữ liệu của 3 nghiệp vụ

Sản phẩm: đề mục A.6 trong `docs/muc-a.md` và 3 hình trong `docs/so-do/`.

Mỗi luồng vẽ một sơ đồ tuần tự: 5 cột dọc **Client → Routes → Services → Repos → Database**, mũi tên ngang đi từ trái sang phải theo thứ tự thời gian, trên mỗi mũi tên ghi tên hàm thật.

Cách vẽ trong draw.io:

1. Mở https://app.diagrams.net. Vẽ 5 hình chữ nhật xếp hàng ngang ở trên cùng, ghi tên 5 cột.
2. Từ mỗi hình kéo một đường thẳng đứng nét đứt xuống dưới.
3. Vẽ mũi tên ngang giữa các đường đứng, bấm đúp vào mũi tên để ghi tên hàm. Mũi tên trả kết quả về vẽ nét đứt.
4. Lưu thành `docs/so-do/luong-household.drawio`, xuất PNG cùng tên. Tương tự cho `luong-tim-kiem` và `luong-phan-quyen`.

Tên file và hàm dưới đây đã đối chiếu với mã nguồn `v3.28.0`. Mở từng file ra xem trước khi đưa vào sơ đồ, để khi bị hỏi bạn chỉ được đúng chỗ. Đường dẫn tính từ thư mục `mealie/` của mã nguồn.

### Luồng cấu hình household

| # | Từ → tới | Diễn ra gì | File, hàm |
| --- | --- | --- | --- |
| 1 | Client → Routes | `PUT /api/households/preferences` kèm JSON 9 trường | `routes/households/controller_household_self_service.py`, hàm `update_household_preferences` |
| 2 | Routes | Pydantic kiểm tra kiểu dữ liệu, sai thì trả 422 | `schema/household/household_preferences.py` |
| 3 | Routes | Kiểm tra quyền `canManageHousehold`, thiếu thì trả 403 | `routes/_base/checks.py`, hàm `can_manage_household` |
| 4 | Routes → Repos → Database | Ghi cấu hình vào bảng `household_preferences` | `self.repos.household_preferences.update(...)`; bảng khai báo ở `db/models/household/preferences.py` |
| 5 | Client → Routes | `POST /api/recipes` kèm tên công thức | `routes/recipe/recipe_crud_routes.py`, hàm `create_one` |
| 6 | Routes → Services | Đọc cấu hình household, gán 5 cài đặt mặc định cho công thức | `services/recipe/recipe_service.py`, hàm `create_one` |
| 7 | Services → Repos → Database | Lưu công thức, trả về slug | |
| 8 | Client → Routes | `GET /api/recipes/{slug}` để đọc lại phần `settings` | `routes/recipe/recipe_crud_routes.py` |

Bước 6 là chỗ đáng nói nhất: hai API khác nhau được nối với nhau qua cấu hình lưu trong cơ sở dữ liệu. Test của nhóm kiểm tra đúng mối nối này.

### Luồng tìm kiếm và lọc

| # | Từ → tới | Diễn ra gì | File, hàm |
| --- | --- | --- | --- |
| 1 | Client → Routes | `GET /api/recipes` kèm các tham số trên URL | `routes/recipe/recipe_crud_routes.py`, hàm `get_all` |
| 2 | Routes | Pydantic kiểm tra tham số. `orderBy=random` thiếu `paginationSeed` bị từ chối ở đây | `schema/response/pagination.py`, lớp `RequestQuery` (lớp cha của `PaginationQuery`), hàm `validate_randseed` |
| 3 | Routes → Repos | Chuyển toàn bộ tham số xuống tầng truy vấn | `repos/repository_recipes.py`, hàm `page_all` |
| 4 | Repos | Dựng điều kiện lọc theo category và tag | `repos/repository_recipes.py`, hàm `_build_recipe_filter` |
| 5 | Repos | Thêm điều kiện tìm theo từ khóa | `repos/repository_generic.py`, hàm `add_search_to_query` |
| 6 | Repos | Thêm sắp xếp và phân trang | `repos/repository_generic.py`, hàm `add_pagination_to_query` và `add_order_by_to_query` |
| 7 | Repos → Database | Chạy một câu SQL | |
| 8 | Routes → Client | Trả JSON gồm `items`, `total`, `total_pages` | |

Luồng này không có tầng Services: Routes gọi thẳng Repos. Ghi rõ điều đó trên sơ đồ.

### Luồng phân quyền

| # | Từ → tới | Diễn ra gì | File, hàm |
| --- | --- | --- | --- |
| 1 | Client → Routes | Admin tạo user bằng `POST /api/admin/users` kèm 5 cờ quyền | `routes/admin/admin_management_users.py`, hàm `create_one` |
| 2 | Routes → Database | Lưu user. Nếu `admin` là true thì bật cả 4 cờ còn lại | `db/models/users/users.py`, hàm `_set_permissions` |
| 3 | Client → Routes | User mới đăng nhập, nhận token | `routes/auth/auth.py`, hàm `get_token` |
| 4 | Client → Routes | User gọi một hành động kèm token | controller của hành động đó |
| 5 | Routes | Đọc token, tìm ra user | `core/dependencies/dependencies.py`, hàm `get_current_user` |
| 6 | Routes | Kiểm tra cờ quyền, thiếu thì trả 403 | xem bảng dưới |
| 7 | Routes → Repos → Database | Đủ quyền thì thực hiện, trả 200 hoặc 201 | |

Chỗ kiểm tra quyền của từng hành động:

| Hành động | Kiểm tra ở đâu |
| --- | --- |
| Tạo category | `routes/organizers/controller_categories.py`, gọi `self.checks.can_organize()` |
| Lưu cấu hình household | `routes/households/controller_household_self_service.py`, gọi `self.checks.can_manage_household()` |
| Xem thành viên, đặt quyền thành viên | cùng file trên, gọi `self.checks.can_manage()` |
| Tạo lời mời | `routes/households/controller_invitations.py`, hàm `create_invite_token`, tự kiểm tra `self.user.can_invite` |
| Xem danh sách user của admin | `core/dependencies/dependencies.py`, hàm `get_admin_user` |

Bốn hàm `can_...` nằm trong lớp `OperationChecks` của `routes/_base/checks.py`.

### Viết A.6

Dưới mỗi hình viết 2–3 câu trả lời ba câu hỏi: dữ liệu vào là gì, được kiểm tra ở đâu, được lưu hoặc đọc ở đâu. Khung:

```markdown
## A.6 Luồng dữ liệu của 3 nghiệp vụ

### A.6.1 Cấu hình household

![Hình. Luồng dữ liệu của nghiệp vụ cấu hình household](so-do/luong-household.png)

<2–3 câu>

### A.6.2 Tìm kiếm và lọc công thức

### A.6.3 Phân quyền
```

## Việc 6. Script mẫu chạy 16 case household

Mục tiêu: mỗi dòng trong `cases/household.tsv` trở thành một test chạy tự động. Thầy lưu ý không được chỉ có bảng test case mà không có script chạy, nên phần này là bằng chứng nhóm đã chạy được thật.

Mỗi test làm ba bước:

1. Lưu cấu hình household theo đúng dòng case.
2. Tạo một công thức mới.
3. Đọc lại công thức, so 5 cài đặt của nó với 5 tùy chọn `recipe...` vừa lưu.

Hai file dưới đây là bản tham khảo đã chạy đạt 16 trên 16 case với Mealie `v3.28.0`. Tự gõ lại vào máy và đọc hiểu từng phần, vì người viết phải giải thích được khi thầy hỏi.

### File `tests/conftest.py`

Chứa phần dùng chung cho mọi file test. pytest tự đọc file có tên này.

```python
"""Phần dùng chung cho mọi file test: địa chỉ Mealie, đăng nhập, đọc file case."""
import csv
import uuid
from pathlib import Path

import pytest
import requests

BASE_URL = "http://localhost:9925"
ADMIN_EMAIL = "nhom22@example.com"
ADMIN_PASSWORD = "Nhom22@Mealie"

CASES_DIR = Path(__file__).resolve().parent.parent / "cases"


def doc_cases(ten_file):
    """Đọc một file .tsv do PICT sinh ra, trả về danh sách dict (mỗi dict là một test case)."""
    with open(CASES_DIR / ten_file, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def dang_nhap(email, mat_khau):
    """Gọi API đăng nhập, trả về header Authorization để gắn vào các lần gọi sau."""
    r = requests.post(
        f"{BASE_URL}/api/auth/token",
        data={"username": email, "password": mat_khau},
        timeout=10,
    )
    assert r.status_code == 200, f"Đăng nhập thất bại: {r.status_code} {r.text}"
    return {"Authorization": "Bearer " + r.json()["access_token"]}


@pytest.fixture(scope="session")
def admin():
    """Header của tài khoản admin dùng chung. Chỉ đăng nhập một lần cho cả lượt chạy."""
    return dang_nhap(ADMIN_EMAIL, ADMIN_PASSWORD)


def ten_khong_trung(tien_to):
    """Tạo tên không trùng để các case không giẫm lên dữ liệu của nhau."""
    return f"{tien_to} {uuid.uuid4().hex[:8]}"
```

| Phần | Giải thích |
| --- | --- |
| `CASES_DIR` | Đường dẫn tới thư mục `cases/`, tính từ vị trí file này nên chạy ở máy nào cũng đúng |
| `doc_cases` | Đọc file `.tsv`. Dòng đầu là tên cột, mỗi dòng sau thành một dict như `{"recipePublic": "true", "firstDayOfWeek": "3", ...}`. Mọi giá trị đều là chuỗi |
| `dang_nhap` | Đúng đoạn đăng nhập ở Việc 3, gói lại thành hàm |
| `@pytest.fixture(scope="session")` | Đánh dấu `admin` là thứ pytest chuẩn bị sẵn. Test nào có tham số tên `admin` sẽ nhận được header này. `scope="session"` nghĩa là chỉ đăng nhập một lần cho cả lượt chạy |
| `ten_khong_trung` | Gắn thêm 8 ký tự ngẫu nhiên vào tên, để chạy lại nhiều lần không bị trùng tên công thức |

### File `tests/test_household.py`

```python
"""Luồng 2: cấu hình household quyết định cài đặt mặc định của công thức mới."""
import pytest
import requests

from conftest import BASE_URL, doc_cases, ten_khong_trung

CASES = doc_cases("household.tsv")

# Tên cột trong file case trùng với tên trường của API, nên chỉ cần đổi kiểu dữ liệu.
TRUONG_BOOL = [
    "privateHousehold",
    "showAnnouncements",
    "lockRecipeEditsFromOtherHouseholds",
    "recipePublic",
    "recipeShowNutrition",
    "recipeShowAssets",
    "recipeLandscapeView",
    "recipeDisableComments",
]

# Cài đặt của công thức mới <- tùy chọn của household (theo recipe_service.py)
ANH_XA = {
    "public": "recipePublic",
    "showNutrition": "recipeShowNutrition",
    "showAssets": "recipeShowAssets",
    "landscapeView": "recipeLandscapeView",
    "disableComments": "recipeDisableComments",
}


def thanh_body(case):
    """Đổi một dòng trong file case (toàn chuỗi) thành body JSON đúng kiểu."""
    body = {ten: case[ten] == "true" for ten in TRUONG_BOOL}
    body["firstDayOfWeek"] = int(case["firstDayOfWeek"])
    return body


@pytest.mark.parametrize("case", CASES, ids=[f"case{i + 1:02d}" for i in range(len(CASES))])
def test_cong_thuc_moi_nhan_mac_dinh_cua_household(admin, case):
    body = thanh_body(case)

    # Bước 1: lưu cấu hình household
    r = requests.put(f"{BASE_URL}/api/households/preferences", headers=admin, json=body, timeout=10)
    assert r.status_code == 200, r.text
    da_luu = r.json()
    for ten, gia_tri in body.items():
        assert da_luu[ten] == gia_tri, f"{ten}: gửi {gia_tri}, Mealie lưu {da_luu[ten]}"

    # Bước 2: tạo một công thức mới
    r = requests.post(f"{BASE_URL}/api/recipes", headers=admin, json={"name": ten_khong_trung("Case household")}, timeout=10)
    assert r.status_code == 201, r.text
    slug = r.json()

    try:
        # Bước 3: đọc lại công thức và so cài đặt với cấu hình vừa lưu
        r = requests.get(f"{BASE_URL}/api/recipes/{slug}", headers=admin, timeout=10)
        assert r.status_code == 200, r.text
        settings = r.json()["settings"]
        for truong_cong_thuc, truong_household in ANH_XA.items():
            assert settings[truong_cong_thuc] == body[truong_household], (
                f"settings.{truong_cong_thuc} = {settings[truong_cong_thuc]}, "
                f"mong đợi {body[truong_household]} (theo {truong_household})"
            )
    finally:
        # Dọn dẹp: xóa công thức vừa tạo để lần chạy sau không bị ảnh hưởng
        requests.delete(f"{BASE_URL}/api/recipes/{slug}", headers=admin, timeout=10)
```

| Phần | Giải thích |
| --- | --- |
| `CASES = doc_cases("household.tsv")` | Đọc 16 dòng case một lần khi pytest nạp file |
| `thanh_body` | File case chỉ có chuỗi `"true"`, `"false"`, `"3"`. Hàm này đổi thành `True`, `False`, `3` để gửi đi đúng kiểu |
| `@pytest.mark.parametrize("case", CASES, ids=...)` | Bảo pytest chạy hàm bên dưới 16 lần, mỗi lần với một dòng case. `ids` đặt tên `case01` đến `case16` để nhìn kết quả biết dòng nào |
| `assert điều_kiện, thông_báo` | Điều kiện sai thì test hỏng và in ra thông báo. Đây là chỗ so kết quả thật với kết quả mong đợi |
| `try ... finally` | Phần `finally` luôn chạy, kể cả khi test hỏng, nên công thức thử luôn được xóa |

### Chạy và đọc kết quả

Mealie phải đang chạy, môi trường `.venv` đã bật, đứng ở thư mục gốc của repo:

```bat
pytest tests -v
```

Kết quả đạt có dạng:

```text
tests/test_household.py::test_cong_thuc_moi_nhan_mac_dinh_cua_household[case01] PASSED [  6%]
...
tests/test_household.py::test_cong_thuc_moi_nhan_mac_dinh_cua_household[case16] PASSED [100%]
============================== 16 passed in 2.17s ==============================
```

Chụp màn hình, lưu thành `docs/evidence/F-01-pytest-household.png`.

Các lệnh hay dùng:

| Lệnh | Tác dụng |
| --- | --- |
| `pytest tests -v` | Chạy tất cả, mỗi case một dòng |
| `pytest tests -v -k case03` | Chỉ chạy case có tên chứa `case03` |
| `pytest tests -x` | Dừng ngay ở case hỏng đầu tiên |
| `pytest tests -v > ket-qua.txt` | Ghi kết quả ra file |

Khi một case hỏng, pytest in ra dòng `assert` bị sai kèm thông báo, ví dụ `settings.public = False, mong đợi True (theo recipePublic)`. Đọc thông báo đó trước, rồi mới xem code.

### Lỗi thường gặp

| Hiện tượng | Nguyên nhân | Cách xử lý |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'requests'` | Chưa bật `.venv` hoặc chưa cài thư viện | `.venv\Scripts\activate` rồi `pip install -r requirements.txt` |
| `ConnectionError` hoặc `Connection refused` | Mealie chưa chạy | `docker compose up -d`, chờ một phút |
| `Đăng nhập thất bại: 401` | Chưa thiết lập lần đầu, hoặc mật khẩu khác bảng dùng chung | Làm lại phần thiết lập lần đầu trong [00-bat-dau.md](00-bat-dau.md) |
| `FileNotFoundError: ... household.tsv` | Thiếu file case | `git pull`; kiểm tra thư mục `cases/` |
| `collected 0 items` | Tên file không bắt đầu bằng `test_`, hoặc đứng sai thư mục | Đổi tên file; đứng ở thư mục gốc của repo |
| `UnicodeDecodeError` khi đọc file case | File case bị ghi bằng bảng mã khác, thường do sinh bằng PowerShell | Sinh lại bằng `scripts\sinh_case.bat` trong Command Prompt |
| Đổi cổng Mealie sang 9926 thì test không chạy | `BASE_URL` trong `conftest.py` vẫn là 9925 | Sửa tạm trên máy mình, không commit |

### Điều cần biết khi chạy

- Test **thay đổi cấu hình household** của Mealie đang chạy. Sau một lượt, cấu hình là của case cuối cùng. Chạy test trên máy sắp dùng để demo thì báo Quý đặt lại cấu hình trước khi demo.
- Test dùng tài khoản dùng chung, là admin nên luôn đủ quyền `canManageHousehold`.
- Ghi vào `tests/README.md`: cách bật `.venv`, lệnh chạy, và kết quả mong đợi là 16 case đạt.

### Tách commit

Chia việc này thành nhiều commit nhỏ, đúng thứ tự làm:

```bat
git add tests/conftest.py
git commit -m "[F] Thêm conftest: đăng nhập và đọc file case"
git add tests/test_household.py
git commit -m "[F] Thêm test 16 case pairwise của luồng household"
git add tests/README.md docs/evidence/F-01-pytest-household.png
git commit -m "[F] Ghi cách chạy test và ảnh kết quả"
```

## Sau giữa kỳ

Hai luồng còn lại viết theo đúng khuôn này: `test_search.py` đọc `cases/search.tsv`, `test_permissions.py` đọc `cases/permissions.tsv`. Khác biệt chính là phải đổi các nhãn trong file case (`none`, `one`, `two`, `match`) thành giá trị thật dựa trên dữ liệu mẫu. Chưa cần làm trước giữa kỳ.

## Câu hỏi nên chuẩn bị sẵn

- Vì sao nhóm kiểm thử qua API mà không qua giao diện?
- Token là gì, vì sao phải đăng nhập trước khi gọi?
- Một dòng trong file case đi vào test như thế nào?
- Kết quả mong đợi của luồng household lấy từ đâu?
- Nếu một case hỏng, làm sao biết lỗi do Mealie hay do test?
