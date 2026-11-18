"""Chay thu 4 luong nghiep vu bang cac case Pairwise (PICT) tren Mealie.

Luong 1: Cong thuc       - cap nhat thong tin roi doc lai   (cases/recipe.o2.tsv)
Luong 2: Tim kiem, loc   - goi GET /api/recipes             (cases/search.o2.tsv)
Luong 3: Ke hoach bua an - tao muc, doc lai theo ngay, xoa  (cases/mealplan.o2.tsv)
Luong 4: Danh sach mua   - them muc, doc lai, tick, xoa     (cases/shopping.o2.tsv)

Cach chay:
    set MEALIE_URL=http://localhost:9925
    set MEALIE_USER=nhom22@example.com
    set MEALIE_PASS=Nhom22@Mealie
    python scripts/chay_thu_4_luong.py

Script tu tao du lieu rieng (ten bat dau bang "PW-") va tu don sau khi chay.
"""
import csv
import datetime as dt
import json
import os
import sys
import time
import uuid

import requests

URL = os.environ.get("MEALIE_URL", "http://localhost:9925")
USER = os.environ.get("MEALIE_USER", "nhom22@example.com")
PASS = os.environ.get("MEALIE_PASS", "Nhom22@Mealie")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
S = requests.Session()
TODAY = dt.date.today()
KET_QUA = []  # (luong, case, dat?, ghi chu)


def api(method, path, **kw):
    r = S.request(method, URL + path, timeout=30, **kw)
    try:
        body = r.json()
    except ValueError:
        body = r.text
    return r.status_code, body


def dang_nhap():
    r = requests.post(URL + "/api/auth/token", data={"username": USER, "password": PASS}, timeout=30)
    r.raise_for_status()
    S.headers["Authorization"] = "Bearer " + r.json()["access_token"]


def doc_case(ten):
    with open(os.path.join(ROOT, "cases", ten), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def ghi(luong, ten, dat, ghi_chu=""):
    KET_QUA.append((luong, ten, dat, ghi_chu))
    print(("PASS " if dat else "FAIL ") + f"{luong} {ten} {ghi_chu}")


# ---------------------------------------------------------------- du lieu nen
def tim_hoac_tao(path_list, path_create, ten):
    s, d = api("GET", path_list, params={"perPage": 200})
    for it in d["items"]:
        if it.get("name") == ten:
            return it
    s, d = api("POST", path_create, json={"name": ten})
    assert s in (200, 201), (path_create, s, d)
    return d


def chuan_bi():
    nen = {}
    s, d = api("GET", "/api/organizers/categories", params={"perPage": 50})
    cats = {c["name"]: c for c in d["items"]}
    s, d = api("GET", "/api/organizers/tags", params={"perPage": 50})
    tags = {t["name"]: t for t in d["items"]}
    nen["cats"] = [cats["Món chính"], cats["Tráng miệng"]]
    nen["tags"] = [tags["Chay"], tags["Nhanh"]]
    nen["unit"] = tim_hoac_tao("/api/units", "/api/units", "PW-gram")
    nen["food"] = tim_hoac_tao("/api/foods", "/api/foods", "PW-ca chua")
    s, d = api("GET", "/api/groups/labels", params={"perPage": 200})
    lab = next((x for x in d["items"] if x["name"] == "PW-rau cu"), None)
    if lab is None:
        s, lab = api("POST", "/api/groups/labels", json={"name": "PW-rau cu", "color": "#4caf50"})
    nen["label"] = lab
    s, d = api("GET", "/api/recipes", params={"search": "Phở bò", "perPage": 1})
    nen["recipe_id"] = d["items"][0]["id"]
    return nen


# ---------------------------------------------------------------- luong 1
MOTA = {"none": None, "short": "Mon an nhanh", "accented": "Món ăn đặc biệt của gia đình Việt"}


def luong_cong_thuc(nen):
    for i, c in enumerate(doc_case("recipe.o2.tsv"), 1):
        ten = f"PW-R{i:02d}-{uuid.uuid4().hex[:5]}"
        s, slug = api("POST", "/api/recipes", json={"name": ten})
        if s != 201:
            ghi("CT", f"R{i:02d}", False, f"tao that bai {s}")
            continue
        body = {
            "recipeServings": float(c["servings"]),
            "recipeIngredient": [{"note": f"nguyen lieu {k}"} for k in range(int(c["ingredients"]))],
            "recipeInstructions": [{"text": f"Buoc {k}"} for k in range(int(c["instructions"]))],
            "recipeCategory": nen["cats"][: {"none": 0, "one": 1, "two": 2}[c["categories"]]],
            "tags": nen["tags"][: {"none": 0, "one": 1, "two": 2}[c["tags"]]],
        }
        if MOTA[c["description"]]:
            body["description"] = MOTA[c["description"]]
        if c["time"] == "both":
            body["prepTime"], body["cookTime"] = "15 minutes", "30 minutes"
        s1, _ = api("PATCH", f"/api/recipes/{slug}", json=body)
        s2, r = api("GET", f"/api/recipes/{slug}")
        # public nam trong settings, gui rieng giong giao dien
        loi = []
        if s1 != 200:
            loi.append(f"PATCH={s1}")
        else:
            s3, _ = api("PATCH", f"/api/recipes/{slug}", json={"settings": {**r["settings"], "public": c["public"] == "true"}})
            s2, r = api("GET", f"/api/recipes/{slug}")
            if s3 != 200:
                loi.append(f"PATCH settings={s3}")
            if r["settings"]["public"] != (c["public"] == "true"):
                loi.append("public sai")
            if r["recipeServings"] != float(c["servings"]):
                loi.append("servings sai")
            if (r["description"] or "") != (MOTA[c["description"]] or ""):
                loi.append("description sai")
            if len(r["recipeIngredient"]) != int(c["ingredients"]):
                loi.append("so nguyen lieu sai")
            if len(r["recipeInstructions"]) != int(c["instructions"]):
                loi.append("so buoc sai")
            if sorted(x["slug"] for x in r["recipeCategory"]) != sorted(x["slug"] for x in body["recipeCategory"]):
                loi.append("category sai")
            if sorted(x["slug"] for x in r["tags"]) != sorted(x["slug"] for x in body["tags"]):
                loi.append("tag sai")
            if c["time"] == "both" and (r["prepTime"], r["cookTime"]) != ("15 minutes", "30 minutes"):
                loi.append("thoi gian sai")
        api("DELETE", f"/api/recipes/{slug}")
        s4, _ = api("GET", f"/api/recipes/{slug}")
        if s4 != 404:
            loi.append("xoa xong van doc duoc")
        ghi("CT", f"R{i:02d}", not loi, "; ".join(loi))


# ---------------------------------------------------------------- luong 2
TAT_CA = []


def loc_dung(r, p, c):
    """Cong thuc r co thoa bo loc trong p khong (tinh tay, khong dung API loc)."""
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


def luong_tim_kiem(nen):
    s, d = api("GET", "/api/recipes", params={"perPage": 200})
    TAT_CA[:] = d["items"]
    for i, c in enumerate(doc_case("search.o2.tsv"), 1):
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
        s, d = api("GET", "/api/recipes", params=p)
        loi = []
        if s != 200:
            loi.append(f"status={s}")
        else:
            items = d["items"]
            if len(items) > int(c["perPage"]):
                loi.append("vuot perPage")
            for it in items:
                cs = {x["slug"] for x in it["recipeCategory"]}
                ts = {x["slug"] for x in it["tags"]}
                if "categories" in p:
                    want = set(p["categories"])
                    if (c["requireAllCategories"] == "true" and not want <= cs) or (c["requireAllCategories"] == "false" and not want & cs):
                        loi.append(f"{it['name']}: sai category")
                if "tags" in p:
                    want = set(p["tags"])
                    if (c["requireAllTags"] == "true" and not want <= ts) or (c["requireAllTags"] == "false" and not want & ts):
                        loi.append(f"{it['name']}: sai tag")
                if "search" in p and p["search"] == "zzzzkhongco":
                    loi.append("nomatch ma van co ket qua")
            # day du: voi perPage=50 va khong tim tu khoa, ket qua phai dung bang tap mong doi
            if c["search"] == "none" and int(c["perPage"]) == 50:
                muon = {r["id"] for r in TAT_CA if loc_dung(r, p, c)}
                co = {it["id"] for it in items}
                if muon != co:
                    loi.append(f"thieu {len(muon - co)}, thua {len(co - muon)} cong thuc")
            if c["orderBy"] == "created_at" and len(items) > 1:
                ds = [it["dateAdded"] for it in items]
                if ds != sorted(ds, reverse=(c["orderDirection"] == "desc")):
                    loi.append("sai thu tu created_at")
            if c["orderBy"] == "random":
                s2, d2 = api("GET", "/api/recipes", params=p)
                if [x["id"] for x in d2["items"]] != [x["id"] for x in items]:
                    loi.append("cung seed khac thu tu")
        ghi("TK", f"S{i:02d}", not loi, "; ".join(sorted(set(loi))[:3]))


# ---------------------------------------------------------------- luong 3
NGAY = {"past": TODAY - dt.timedelta(7), "today": TODAY, "future": TODAY + dt.timedelta(7)}
TIEU_DE = {"title_short": "Banh mi", "title_accented": "Bữa sáng đặc biệt", "recipe_and_title": "Mon cua ba"}


def luong_ke_hoach(nen):
    for i, c in enumerate(doc_case("mealplan.o2.tsv"), 1):
        ngay = NGAY[c["date"]].isoformat()
        body = {"date": ngay, "entryType": c["entryType"]}
        if c["content"] in TIEU_DE:
            body["title"] = TIEU_DE[c["content"]]
        if c["content"].startswith("recipe"):
            body["recipeId"] = nen["recipe_id"]
        if c["text"] == "note":
            body["text"] = "ghi chu"
        s, d = api("POST", "/api/households/mealplans", json=body)
        loi = []
        if s != 201:
            ghi("KH", f"M{i:02d}", False, f"POST={s}")
            continue
        s2, ds = api("GET", "/api/households/mealplans", params={"start_date": ngay, "end_date": ngay, "perPage": 100})
        tim = [x for x in ds["items"] if x["id"] == d["id"]]
        if not tim:
            loi.append("khong doc lai duoc theo ngay")
        else:
            x = tim[0]
            if x["entryType"] != c["entryType"]:
                loi.append("entryType sai")
            if x["date"] != ngay:
                loi.append("ngay sai")
            if (x["title"] or "") != body.get("title", ""):
                loi.append("title sai")
            if (x["text"] or "") != body.get("text", ""):
                loi.append("text sai")
            if x["recipeId"] != body.get("recipeId"):
                loi.append("recipeId sai")
        api("DELETE", f"/api/households/mealplans/{d['id']}")
        s3, ds = api("GET", "/api/households/mealplans", params={"start_date": ngay, "end_date": ngay, "perPage": 100})
        if any(x["id"] == d["id"] for x in ds["items"]):
            loi.append("xoa xong van con")
        ghi("KH", f"M{i:02d}", not loi, "; ".join(loi))


# ---------------------------------------------------------------- luong 4
def luong_mua_sam(nen):
    for i, c in enumerate(doc_case("shopping.o2.tsv"), 1):
        s, lst = api("POST", "/api/households/shopping/lists", json={"name": f"PW-L{i:02d}"})
        lid = lst["id"]
        body = {"shoppingListId": lid, "quantity": float(c["quantity"]), "checked": c["checked"] == "true"}
        note = {"none": None, "short": "Muoi", "accented": "Hành lá tươi"}[c["note"]]
        if note:
            body["note"] = note
        if c["unit"] != "none":
            body["unitId"] = nen["unit"]["id"]
        if c["food"] != "none":
            body["foodId"] = nen["food"]["id"]
        if c["label"] != "none":
            body["labelId"] = nen["label"]["id"]
        s, d = api("POST", "/api/households/shopping/items", json=body)
        loi = []
        if s != 201 or not d.get("createdItems"):
            ghi("MS", f"L{i:02d}", False, f"POST={s}, createdItems={len(d.get('createdItems', [])) if isinstance(d, dict) else '?'}")
            api("DELETE", f"/api/households/shopping/lists/{lid}")
            continue
        item = d["createdItems"][0]
        s, full = api("GET", f"/api/households/shopping/lists/{lid}")
        it = next((x for x in full["listItems"] if x["id"] == item["id"]), None)
        if it is None:
            loi.append("khong doc lai duoc")
        else:
            if it["quantity"] != float(c["quantity"]):
                loi.append("quantity sai")
            if (it["note"] or "") != (note or ""):
                loi.append("note sai")
            if it["checked"] != (c["checked"] == "true"):
                loi.append("checked sai")
            for khoa, cot, key in (("unitId", "unit", "unit"), ("foodId", "food", "food"), ("labelId", "label", "label")):
                muon = nen[key]["id"] if c[cot] != "none" else None
                if it[khoa] != muon:
                    loi.append(f"{khoa} sai")
            # buoc 3: tick / bo tick
            it["checked"] = not it["checked"]
            s, _ = api("PUT", f"/api/households/shopping/items/{it['id']}", json=it)
            s, full2 = api("GET", f"/api/households/shopping/lists/{lid}")
            it2 = next((x for x in full2["listItems"] if x["id"] == it["id"]), None)
            if s != 200 or it2 is None or it2["checked"] != it["checked"]:
                loi.append("doi checked khong luu")
        api("DELETE", f"/api/households/shopping/items", params={"ids": item["id"]})
        api("DELETE", f"/api/households/shopping/lists/{lid}")
        ghi("MS", f"L{i:02d}", not loi, "; ".join(loi))


def main():
    dang_nhap()
    nen = chuan_bi()
    t0 = time.time()
    luong_cong_thuc(nen)
    luong_tim_kiem(nen)
    luong_ke_hoach(nen)
    luong_mua_sam(nen)
    print("\n== TONG KET ==")
    for lg, ten in (("CT", "Cong thuc"), ("TK", "Tim kiem"), ("KH", "Ke hoach bua an"), ("MS", "Danh sach mua sam")):
        ds = [x for x in KET_QUA if x[0] == lg]
        print(f"{ten:20s}: {sum(1 for x in ds if x[2])}/{len(ds)} dat")
    print(f"Tong thoi gian: {time.time() - t0:.1f} giay")
    with open(os.path.join(HERE, "ket_qua.json"), "w", encoding="utf-8") as f:
        json.dump([{"luong": a, "case": b, "dat": c, "ghi_chu": d} for a, b, c, d in KET_QUA], f, ensure_ascii=False, indent=1)
    sys.exit(0 if all(x[2] for x in KET_QUA) else 1)


if __name__ == "__main__":
    main()
