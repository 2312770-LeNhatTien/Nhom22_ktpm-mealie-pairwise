"""Kiểm thử quản lý công thức theo ba mức phủ của model PICT."""

from uuid import uuid4

import pytest

from chung import doc_case


MO_TA = {
    "none": "",
    "short": "Mon an nhanh",
    "accented": "Món ăn đặc biệt của gia đình Việt",
}
SO_MUC = {"none": 0, "one": 1, "two": 2}


def tham_so(c, nen):
    """Đổi nhãn PICT thành dữ liệu gửi qua API."""
    body = {
        "description": MO_TA[c["description"]],
        "recipeServings": float(c["servings"]),
        "recipeIngredient": [
            {"note": f"nguyen lieu {i}"} for i in range(int(c["ingredients"]))
        ],
        "recipeInstructions": [
            {"text": f"Buoc {i}"} for i in range(int(c["instructions"]))
        ],
        "recipeCategory": nen["cats"][:SO_MUC[c["categories"]]],
        "tags": nen["tags"][:SO_MUC[c["tags"]]],
    }
    if c["time"] == "both":
        body.update(prepTime="15 minutes", cookTime="30 minutes")
    return body


def kiem_tra_ma(loi, thao_tac, ma, mong_doi, bat_bien="I2"):
    if ma >= 500:
        loi.append(f"I1: {thao_tac} trả lỗi máy chủ {ma}")
    if ma not in mong_doi:
        loi.append(f"{bat_bien}: {thao_tac} trả {ma}, mong đợi {mong_doi}")
        return False
    return True


def doi_chieu(loi, da_luu, body, cong_khai):
    for khoa in ("description", "prepTime", "cookTime"):
        if (da_luu.get(khoa) or "") != body.get(khoa, ""):
            loi.append(f"I3: {khoa} đọc lại khác giá trị đã gửi")
    if da_luu.get("recipeServings") != body["recipeServings"]:
        loi.append("I3: số khẩu phần đọc lại khác giá trị đã gửi")
    for khoa, truong in (
        ("recipeIngredient", "note"),
        ("recipeInstructions", "text"),
        ("recipeCategory", "slug"),
        ("tags", "slug"),
    ):
        co = [muc.get(truong) for muc in da_luu.get(khoa, [])]
        muon = [muc[truong] for muc in body[khoa]]
        if khoa in ("recipeCategory", "tags"):
            co, muon = set(co), set(muon)
        if co != muon:
            loi.append(f"I3: {khoa} đọc lại khác giá trị đã gửi")
    if (da_luu.get("settings") or {}).get("public") is not cong_khai:
        loi.append("I3: trạng thái công khai đọc lại khác giá trị đã gửi")


def kiem_tra(api, nen, c):
    loi = []
    body = tham_so(c, nen)
    cong_khai = c["public"] == "true"
    ten = f"PW-R-{uuid4().hex}"
    duong_dan = None
    try:
        ma, slug = api("POST", "/api/recipes", json={"name": ten})
        if isinstance(slug, str) and slug == ten.lower():
            duong_dan = f"/api/recipes/{slug}"
        if not kiem_tra_ma(loi, "tạo công thức", ma, (201,)):
            return loi
        if not duong_dan:
            loi.append("I3: slug tạo mới không khớp tên của ca kiểm thử")
            return loi
        ma, _ = api("PATCH", duong_dan, json=body)
        if not kiem_tra_ma(loi, "sửa công thức", ma, (200,)):
            return loi
        ma, da_luu = api("GET", duong_dan)
        if not kiem_tra_ma(loi, "đọc công thức", ma, (200,)):
            return loi
        settings = {**da_luu["settings"], "public": cong_khai}
        ma, _ = api("PATCH", duong_dan, json={"settings": settings})
        if not kiem_tra_ma(loi, "sửa chế độ công khai", ma, (200,)):
            return loi
        ma, da_luu = api("GET", duong_dan)
        if kiem_tra_ma(loi, "đọc công thức sau khi sửa", ma, (200,)):
            doi_chieu(loi, da_luu, body, cong_khai)
    finally:
        if duong_dan:
            ma, _ = api("DELETE", duong_dan)
            kiem_tra_ma(loi, "xóa công thức", ma, (200, 204))
            ma, _ = api("GET", duong_dan)
            kiem_tra_ma(loi, "đọc sau khi xóa", ma, (404,), "I5")
    return loi


@pytest.mark.parametrize("c", doc_case("recipe.o2.tsv", "R"))
def test_cong_thuc_2wise(api, nen, c):
    loi = kiem_tra(api, nen, c)
    assert not loi, "\n".join(loi)


@pytest.mark.o3
@pytest.mark.parametrize("c", doc_case("recipe.o3.tsv", "R", 3))
def test_cong_thuc_3wise(api, nen, c):
    loi = kiem_tra(api, nen, c)
    assert not loi, "\n".join(loi)


@pytest.mark.het
@pytest.mark.parametrize("c", doc_case("recipe.all.tsv", "R", 4))
def test_cong_thuc_thu_het(api, nen, c):
    loi = kiem_tra(api, nen, c)
    assert not loi, "\n".join(loi)
