import math
import unicodedata

import pytest

from chung import doc_case

TU_KHOA = "ch"


def bo_dau(s):
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()


@pytest.fixture(scope="module")
def tat_ca(api):
    s, d = api("GET", "/api/recipes", params={"perPage": 200})
    return d["items"]


def tham_so(c, nen):
    p = {"perPage": int(c["perPage"]), "page": 1}
    if c["search"] == "match":
        p["search"] = TU_KHOA
    elif c["search"] == "nomatch":
        p["search"] = "zzzzkhongco"
    if c["categories"] != "none":
        p["categories"] = [x["slug"] for x in nen["cats"][: 1 if c["categories"] == "one" else 2]]
    if c["tags"] != "none":
        p["tags"] = [x["slug"] for x in nen["tags"][: 1 if c["tags"] == "one" else 2]]
    p["requireAllCategories"] = c["requireAllCategories"]
    p["requireAllTags"] = c["requireAllTags"]
    if c["orderBy"] != "none":
        p["orderBy"] = c["orderBy"]
        p["orderDirection"] = c["orderDirection"]
    if c["paginationSeed"] != "none":
        p["paginationSeed"] = c["paginationSeed"]
    return p


def dung_bo_loc(r, p, c):
    cs = {x["slug"] for x in r["recipeCategory"]}
    ts = {x["slug"] for x in r["tags"]}
    ok = True
    if "categories" in p:
        want = set(p["categories"])
        ok &= want <= cs if c["requireAllCategories"] == "true" else bool(want & cs)
    if "tags" in p:
        want = set(p["tags"])
        ok &= want <= ts if c["requireAllTags"] == "true" else bool(want & ts)
    return ok


def khop(r, p, c):
    if c["search"] == "nomatch":
        return False
    if c["search"] == "match" and bo_dau(TU_KHOA) not in bo_dau(r["name"]):
        return False
    return dung_bo_loc(r, p, c)


def lay_cac_trang_sau(api, p, tong_trang, loi):
    ds = []
    for trang in range(2, tong_trang + 1):
        q = dict(p)
        q["page"] = trang
        s, d = api("GET", "/api/recipes", params=q)
        if s != 200:
            loi.append(f"I1/I2: trang {trang} trả {s}")
            break
        ds += d["items"]
    return ds


def kiem_tra(api, nen, tat_ca, c):
    p = tham_so(c, nen)
    s, d = api("GET", "/api/recipes", params=p)
    if s != 200:
        return [f"I1/I2: trả {s}"]
    loi = []
    per = int(c["perPage"])
    items = d["items"]
    muon = {r["id"] for r in tat_ca if khop(r, p, c)}
    if d["page"] != 1 or d["per_page"] != per:
        loi.append(f"I3: page={d['page']}, per_page={d['per_page']}")
    if d["total"] != len(muon):
        loi.append(f"I3: total={d['total']} nhưng cần {len(muon)}")
    if d["total_pages"] != math.ceil(len(muon) / per):
        loi.append(f"I3: total_pages={d['total_pages']} sai")
    if len(items) != min(per, len(muon)):
        loi.append(f"I3: trang 1 có {len(items)} công thức, cần {min(per, len(muon))}")
    for it in items:
        if not dung_bo_loc(it, p, c):
            loi.append(f"I6: {it['name']} sai bộ lọc")
    if c["search"] == "nomatch" and items:
        loi.append("I6: từ khóa không có mà vẫn có kết quả")
    tat_ca_trang = items + lay_cac_trang_sau(api, p, d["total_pages"], loi)
    ids = [it["id"] for it in tat_ca_trang]
    if len(ids) != len(set(ids)):
        loi.append("I7: có công thức xuất hiện ở hai trang")
    if set(ids) != muon:
        loi.append(f"I7: duyệt hết trang thiếu {len(muon - set(ids))}, thừa {len(set(ids) - muon)} công thức")
    if c["orderBy"] == "created_at" and len(tat_ca_trang) > 1:
        ngay = [it["createdAt"] for it in tat_ca_trang]
        if ngay != sorted(ngay, reverse=(c["orderDirection"] == "desc")):
            loi.append("I6: sai thứ tự created_at")
    if c["orderBy"] == "name" and len(tat_ca_trang) > 1:
        ten = [it["name"] for it in tat_ca_trang]
        if ten != sorted(ten, reverse=(c["orderDirection"] == "desc")):
            loi.append("I6: sai thứ tự name theo mã Unicode")
    if c["orderBy"] == "random":
        s2, d2 = api("GET", "/api/recipes", params=p)
        if s2 != 200:
            loi.append(f"I1/I2: gọi lần 2 trả {s2}")
        elif [x["id"] for x in d2["items"]] != [x["id"] for x in items]:
            loi.append("I6: cùng seed mà khác thứ tự")
    return loi


@pytest.mark.parametrize("c", doc_case("search.o2.tsv", "S"))
def test_tim_kiem_2wise(api, nen, tat_ca, c):
    loi = kiem_tra(api, nen, tat_ca, c)
    assert not loi, "; ".join(sorted(set(loi)))


@pytest.mark.o3
@pytest.mark.parametrize("c", doc_case("search.o3.tsv", "S", 3))
def test_tim_kiem_3wise(api, nen, tat_ca, c):
    loi = kiem_tra(api, nen, tat_ca, c)
    assert not loi, "; ".join(sorted(set(loi)))


@pytest.mark.het
@pytest.mark.parametrize("c", doc_case("search.all.tsv", "S", 4))
def test_tim_kiem_thu_het(api, nen, tat_ca, c):
    loi = kiem_tra(api, nen, tat_ca, c)
    assert not loi, "; ".join(sorted(set(loi)))


@pytest.mark.parametrize("huong", ["asc", "desc"])
def test_sap_xep_ten_theo_bang_chu_cai(api, huong):
    s, d = api("GET", "/api/recipes", params={"perPage": 50, "orderBy": "name", "orderDirection": huong})
    assert s == 200
    ten = [it["name"] for it in d["items"]]
    mong_doi = sorted(ten, key=bo_dau, reverse=(huong == "desc"))
    assert ten == mong_doi, f"thứ tự {huong} khác bảng chữ cái: {ten}"
