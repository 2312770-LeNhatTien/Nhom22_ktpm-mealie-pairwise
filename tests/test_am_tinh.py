"""18 test du lieu sai va gia tri bien (test am) cho 4 luong:
  - Cong thuc: CT-N1 .. CT-N5
  - Tim kiem va loc: TK-N1 .. TK-N4
  - Ke hoach bua an: KH-N1 .. KH-N4
  - Danh sach mua sam: MS-N1 .. MS-N5

Quy tac chung: Du lieu sai phai bi tu choi bang ma 4xx (khong luu, khong bi loi 500).
Cac ca phat hien loi that tren Mealie v3.28.0 duoc danh dau xfail kem giai thich.
"""
import datetime as dt
import uuid
import pytest

TODAY = dt.date.today().isoformat()


# ==============================================================================
# Luong 1: Cong thuc (CT-N1 .. CT-N5)
# ==============================================================================

@pytest.mark.xfail(reason="DEF: Mealie ném 500 (AssertionError trong validate_name) khi tạo công thức tên rỗng", strict=False)
def test_ct_n1_tao_cong_thuc_ten_rong(api):
    """CT-N1: Tao cong thuc voi ten rong -> mong doi 4xx."""
    s, d = api("POST", "/api/recipes", json={"name": ""})
    try:
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        if s == 201 and isinstance(d, dict) and "slug" in d:
            api("DELETE", f"/api/recipes/{d['slug']}")


@pytest.mark.xfail(reason="DEF: Mealie ném 500 khi sửa tên công thức thành rỗng qua PATCH", strict=False)
def test_ct_n2_sua_ten_cong_thuc_thanh_rong(api):
    """CT-N2: Sua ten cong thuc thanh rong -> mong doi 4xx."""
    s_create, slug = api("POST", "/api/recipes", json={"name": "PW-N-" + uuid.uuid4().hex[:5]})
    assert s_create == 201, f"Không tạo được công thức mẫu: {s_create}"
    try:
        s, _ = api("PATCH", f"/api/recipes/{slug}", json={"name": ""})
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        api("DELETE", f"/api/recipes/{slug}")


@pytest.mark.xfail(reason="DEF: Mealie cho phép lưu số khẩu phần âm (-5) và trả 200 thay vì 4xx", strict=False)
def test_ct_n3_so_khau_phan_am(api):
    """CT-N3: So khau phan am (-5) -> mong doi 4xx, khong luu gia tri am."""
    s_create, slug = api("POST", "/api/recipes", json={"name": "PW-N-" + uuid.uuid4().hex[:5]})
    assert s_create == 201, f"Không tạo được công thức mẫu: {s_create}"
    try:
        s, _ = api("PATCH", f"/api/recipes/{slug}", json={"recipeServings": -5})
        s2, r = api("GET", f"/api/recipes/{slug}")
        servings = r.get("recipeServings") if isinstance(r, dict) else r
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}, recipeServings lưu: {servings}"
    finally:
        api("DELETE", f"/api/recipes/{slug}")


def test_ct_n4_so_khau_phan_la_chu(api):
    """CT-N4: So khau phan la chu ('abc') -> mong doi 4xx."""
    s_create, slug = api("POST", "/api/recipes", json={"name": "PW-N-" + uuid.uuid4().hex[:5]})
    assert s_create == 201, f"Không tạo được công thức mẫu: {s_create}"
    try:
        s, _ = api("PATCH", f"/api/recipes/{slug}", json={"recipeServings": "abc"})
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        api("DELETE", f"/api/recipes/{slug}")


def test_ct_n5_ten_chi_toan_dau_cach(api):
    """CT-N5: Ten chi toan dau cach ('   ') -> mong doi 4xx."""
    s, d = api("POST", "/api/recipes", json={"name": "   "})
    try:
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        if s == 201 and isinstance(d, dict) and "slug" in d:
            api("DELETE", f"/api/recipes/{d['slug']}")


# ==============================================================================
# Luong 2: Tim kiem va loc (TK-N1 .. TK-N4)
# ==============================================================================

@pytest.mark.xfail(reason="DEF: Lọc category không tồn tại trả về toàn bộ 12 công thức thay vì rỗng/4xx", strict=False)
def test_tk_n1_loc_category_khong_ton_tai(api):
    """TK-N1: Loc category khong ton tai -> mong doi danh sach rong (total=0) hoac 4xx."""
    s, d = api("GET", "/api/recipes", params={"categories": "khong-ton-tai", "perPage": 50})
    total = d.get("total") if isinstance(d, dict) else None
    assert s != 200 or total == 0, f"Mong đợi total=0 hoặc 4xx nhưng nhận được status={s}, total={total}"


def test_tk_n2_ten_tham_so_sai_kieu_chu(api, nen):
    """TK-N2: Ten tham so sai kieu chu (require_all_categories thay vi requireAllCategories).
    Hanh vi chung FastAPI: bo qua tham so la, loc theo mac dinh (OR).
    Do do d0['total'] (khi bo qua tham so -> OR) phai >= d1['total'] (khi dung requireAllCategories=true -> AND).
    """
    cats = [x["slug"] for x in nen["cats"][:2]]
    s0, d0 = api("GET", "/api/recipes", params={"categories": cats, "require_all_categories": "true", "perPage": 50})
    s1, d1 = api("GET", "/api/recipes", params={"categories": cats, "requireAllCategories": "true", "perPage": 50})
    assert s0 == 200 and s1 == 200, f"API trả lỗi: s0={s0}, s1={s1}"
    assert d0.get("total", 0) >= d1.get("total", 0), (
        f"Kỳ vọng d0['total'] ({d0.get('total')}) >= d1['total'] ({d1.get('total')})"
    )


def test_tk_n3_random_khong_co_seed(api):
    """TK-N3: orderBy=random khong co paginationSeed -> mong doi 4xx."""
    s, d = api("GET", "/api/recipes", params={"orderBy": "random", "perPage": 10})
    assert 400 <= s < 500, f"Mong đợi 4xx khi thiếu paginationSeed nhưng nhận được {s}"


def test_tk_n4_per_page_am_mot_lay_tat_ca(api):
    """TK-N4: perPage = -1 -> thiet ke cua Mealie: tra ve tat ca cong thuc."""
    s, d = api("GET", "/api/recipes", params={"perPage": -1})
    assert s == 200, f"Mong đợi 200 nhưng nhận được {s}"
    items = d.get("items", []) if isinstance(d, dict) else []
    total = d.get("total") if isinstance(d, dict) else None
    assert len(items) == total, f"Kỳ vọng trả tất cả ({total} items) nhưng chỉ có {len(items)}"


# ==============================================================================
# Luong 3: Ke hoach bua an (KH-N1 .. KH-N4)
# ==============================================================================

def test_kh_n1_entry_type_khong_hop_le(api):
    """KH-N1: entryType khong hop le ('brunch') -> mong doi 4xx."""
    s, d = api("POST", "/api/households/mealplans", json={"date": TODAY, "entryType": "brunch", "title": "x"})
    try:
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        if s == 201 and isinstance(d, dict) and "id" in d:
            api("DELETE", f"/api/households/mealplans/{d['id']}")


def test_kh_n2_ngay_khong_ton_tai(api):
    """KH-N2: Ngay khong ton tai ('2026-13-45') -> mong doi 4xx."""
    s, d = api("POST", "/api/households/mealplans", json={"date": "2026-13-45", "entryType": "lunch", "title": "x"})
    try:
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        if s == 201 and isinstance(d, dict) and "id" in d:
            api("DELETE", f"/api/households/mealplans/{d['id']}")


def test_kh_n3_khong_tieu_de_khong_cong_thuc(api):
    """KH-N3: Khong co tieu de va khong co recipeId -> mong doi 4xx."""
    s, d = api("POST", "/api/households/mealplans", json={"date": TODAY, "entryType": "lunch"})
    try:
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        if s == 201 and isinstance(d, dict) and "id" in d:
            api("DELETE", f"/api/households/mealplans/{d['id']}")


@pytest.mark.xfail(reason="DEF: Mealie cho phép tạo kế hoạch bữa ăn với recipeId không tồn tại (trả 201)", strict=False)
def test_kh_n4_recipe_id_khong_ton_tai(api):
    """KH-N4: recipeId la UUID ngau nhien khong ton tai -> mong doi 4xx."""
    fake_recipe_id = str(uuid.uuid4())
    s, d = api("POST", "/api/households/mealplans", json={"date": TODAY, "entryType": "lunch", "title": "PW-N", "recipeId": fake_recipe_id})
    try:
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        if s == 201 and isinstance(d, dict) and "id" in d:
            api("DELETE", f"/api/households/mealplans/{d['id']}")


# ==============================================================================
# Luong 4: Danh sach mua sam (MS-N1 .. MS-N5)
# ==============================================================================

@pytest.mark.xfail(reason="DEF: Mealie ném 500 (ValidationError) khi thêm mục vào shoppingListId không tồn tại", strict=False)
def test_ms_n1_shopping_list_id_khong_ton_tai(api):
    """MS-N1: shoppingListId khong ton tai -> mong doi 404 hoac 4xx."""
    s, _ = api("POST", "/api/households/shopping/items", json={"shoppingListId": str(uuid.uuid4()), "note": "x"})
    assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"


@pytest.mark.xfail(reason="DEF: Mealie cho phép thêm mục mua sắm số lượng âm (-3) và trả 201", strict=False)
def test_ms_n2_so_luong_am(api):
    """MS-N2: So luong am (-3) -> mong doi 4xx."""
    s_lst, lst = api("POST", "/api/households/shopping/lists", json={"name": "PW-N-MS2"})
    assert s_lst == 201, f"Không tạo được danh sách mẫu: {s_lst}"
    lid = lst["id"]
    try:
        s, d = api("POST", "/api/households/shopping/items", json={"shoppingListId": lid, "note": "am", "quantity": -3})
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        api("DELETE", f"/api/households/shopping/lists/{lid}")


@pytest.mark.xfail(reason="DEF: Mealie ném 500 (KeyError '-' trong display_fraction) khi số lượng âm lẻ (-0.5)", strict=False)
def test_ms_n3_so_luong_am_le(api):
    """MS-N3: So luong am le (-0.5) -> mong doi 4xx."""
    s_lst, lst = api("POST", "/api/households/shopping/lists", json={"name": "PW-N-MS3"})
    assert s_lst == 201, f"Không tạo được danh sách mẫu: {s_lst}"
    lid = lst["id"]
    try:
        s, d = api("POST", "/api/households/shopping/items", json={"shoppingListId": lid, "note": "am le", "quantity": -0.5})
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        api("DELETE", f"/api/households/shopping/lists/{lid}")


@pytest.mark.xfail(reason="DEF: Mealie cho phép thêm mục mua sắm với foodId không tồn tại (trả 201)", strict=False)
def test_ms_n4_food_id_khong_ton_tai(api):
    """MS-N4: foodId la UUID ngau nhien khong ton tai -> mong doi 4xx."""
    s_lst, lst = api("POST", "/api/households/shopping/lists", json={"name": "PW-N-MS4"})
    assert s_lst == 201, f"Không tạo được danh sách mẫu: {s_lst}"
    lid = lst["id"]
    try:
        s, d = api("POST", "/api/households/shopping/items", json={"shoppingListId": lid, "note": "food gia", "foodId": str(uuid.uuid4())})
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        api("DELETE", f"/api/households/shopping/lists/{lid}")


@pytest.mark.xfail(reason="DEF: Mealie cho phép tạo danh sách mua sắm với tên rỗng (trả 201)", strict=False)
def test_ms_n5_tao_danh_sach_ten_rong(api):
    """MS-N5: Tao danh sach mua sam ten rong -> mong doi 4xx."""
    s, d = api("POST", "/api/households/shopping/lists", json={"name": ""})
    try:
        assert 400 <= s < 500, f"Mong đợi 4xx nhưng nhận được {s}"
    finally:
        if s == 201 and isinstance(d, dict) and "id" in d:
            api("DELETE", f"/api/households/shopping/lists/{d['id']}")
