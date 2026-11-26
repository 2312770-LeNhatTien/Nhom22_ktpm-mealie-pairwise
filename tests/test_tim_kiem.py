import pytest

from chung import doc_case


@pytest.fixture(scope="module")
def tat_ca(api):
    s, d = api("GET", "/api/recipes", params={"perPage": 200})
    return d["items"]


def tham_so(c, nen):
    p = {"perPage": int(c["perPage"]), "page": 1}
    if c["search"] == "match":
        p["search"] = "chè"
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


def kiem_tra(api, nen, tat_ca, c):
    p = tham_so(c, nen)
    s, d = api("GET", "/api/recipes", params=p)
    if s != 200:
        return [f"I1/I2: trả {s}"]
    loi = []
    items = d["items"]
    if len(items) > int(c["perPage"]):
        loi.append("I6: vượt perPage")
    for it in items:
        if not dung_bo_loc(it, p, c):
            loi.append(f"I6: {it['name']} sai bộ lọc")
    if c["search"] == "nomatch" and items:
        loi.append("I6: từ khóa không có mà vẫn có kết quả")
    if c["search"] == "none" and int(c["perPage"]) == 50:
        muon = {r["id"] for r in tat_ca if dung_bo_loc(r, p, c)}
        co = {it["id"] for it in items}
        if muon != co:
            loi.append(f"I6: thiếu {len(muon - co)}, thừa {len(co - muon)} công thức")
    if c["orderBy"] == "created_at" and len(items) > 1:
        ngay = [it["createdAt"] for it in items]
        if ngay != sorted(ngay, reverse=(c["orderDirection"] == "desc")):
            loi.append("I6: sai thứ tự created_at")
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
