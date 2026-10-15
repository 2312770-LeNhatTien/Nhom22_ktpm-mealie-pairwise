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

# Cài đặt của công thức mới <- tùy chọn của household (theo recipe_service.py, hàm create_one)
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


@pytest.fixture(scope="module", autouse=True)
def khoi_phuc_cau_hinh(admin):
    """Test này đổi cấu hình household. Lưu cấu hình ban đầu, chạy xong thì trả lại như cũ."""
    r = requests.get(f"{BASE_URL}/api/households/preferences", headers=admin, timeout=10)
    assert r.status_code == 200, r.text
    ban_dau = {ten: r.json()[ten] for ten in TRUONG_BOOL + ["firstDayOfWeek"]}
    yield
    requests.put(f"{BASE_URL}/api/households/preferences", headers=admin, json=ban_dau, timeout=10)


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
    r = requests.post(
        f"{BASE_URL}/api/recipes", headers=admin, json={"name": ten_khong_trung("Case household")}, timeout=10
    )
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
