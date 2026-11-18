"""Chay cac ca am tinh / ca bien cua 4 luong (tach rieng khoi cac case Pairwise).

Moi ca: gui mot yeu cau sai hoac sat bien, so sanh ma tra ve voi ket qua mong doi.
Ket qua mong doi lay tu quy tac chung: du lieu sai phai bi tu choi bang 4xx (khong
duoc luu va khong duoc loi 500). Ca nao khac mong doi duoc ghi la "KHAC MONG DOI".

Cach chay: python scripts/chay_ca_am_tinh.py   (dung chung bien MEALIE_URL, MEALIE_USER, MEALIE_PASS)
"""
import json
import os
import uuid
import datetime as dt

import chay_thu_4_luong as base

api = base.api
KQ = []


def ca(ma, luong, mo_ta, mong_doi, thuc_te, dat, ghi_chu=""):
    KQ.append(dict(ma=ma, luong=luong, mo_ta=mo_ta, mong_doi=mong_doi, thuc_te=thuc_te, dat=dat, ghi_chu=ghi_chu))
    print(f"{'DAT        ' if dat else 'KHAC MONG DOI'} {ma:5s} {luong:10s} {mo_ta} | mong doi: {mong_doi} | thuc te: {thuc_te}")


def main():
    base.dang_nhap()
    nen = base.chuan_bi()
    hom_nay = dt.date.today().isoformat()

    # ---------------- Cong thuc
    s, _ = api("POST", "/api/recipes", json={"name": ""})
    ca("CT-N1", "Cong thuc", "Tao cong thuc ten rong", "4xx", s, 400 <= s < 500, "500 = AssertionError trong validate_name" if s == 500 else "")
    s, slug = api("POST", "/api/recipes", json={"name": "PW-N-" + uuid.uuid4().hex[:5]})
    s, _ = api("PATCH", f"/api/recipes/{slug}", json={"name": ""})
    ca("CT-N2", "Cong thuc", "Sua ten cong thuc thanh rong", "4xx", s, 400 <= s < 500)
    s, _ = api("PATCH", f"/api/recipes/{slug}", json={"recipeServings": -5})
    s2, r = api("GET", f"/api/recipes/{slug}")
    ca("CT-N3", "Cong thuc", "So khau phan am (-5)", "4xx, khong luu", f"{s}, luu {r['recipeServings']}", 400 <= s < 500)
    s, _ = api("PATCH", f"/api/recipes/{slug}", json={"recipeServings": "abc"})
    ca("CT-N4", "Cong thuc", "So khau phan la chu", "4xx", s, 400 <= s < 500)
    s, _ = api("POST", "/api/recipes", json={"name": "   "})
    ca("CT-N5", "Cong thuc", "Ten chi toan dau cach", "4xx", s, 400 <= s < 500)
    api("DELETE", f"/api/recipes/{slug}")

    # ---------------- Tim kiem
    s, d = api("GET", "/api/recipes", params={"categories": "khong-ton-tai", "perPage": 50})
    ca("TK-N1", "Tim kiem", "Loc category khong ton tai", "danh sach rong (hoac 4xx)", f"{s}, {d['total'] if s == 200 else '-'} ket qua", s != 200 or d["total"] == 0)
    s, d = api("GET", "/api/recipes", params={"categories": "mon-chinh", "require_all_categories": "true", "perPage": 50})
    s0, d0 = api("GET", "/api/recipes", params={"categories": ["mon-chinh", "trang-mieng"], "require_all_categories": "true", "perPage": 50})
    s1, d1 = api("GET", "/api/recipes", params={"categories": ["mon-chinh", "trang-mieng"], "requireAllCategories": "true", "perPage": 50})
    ca("TK-N2", "Tim kiem", "Ten tham so sai kieu chu (require_all_categories)", "bo qua tham so la (hanh vi chung cua FastAPI): loc nhu mac dinh", f"{s0}, {d0['total']} ket qua (ten dung cho {d1['total']})", s0 == 200 and d0["total"] > d1["total"], "khong phai loi, can luu y khi viet test")
    s, d = api("GET", "/api/recipes", params={"orderBy": "random", "perPage": 10})
    ca("TK-N3", "Tim kiem", "orderBy=random khong co paginationSeed", "4xx", s, 400 <= s < 500)
    s, d = api("GET", "/api/recipes", params={"perPage": -1})
    ca("TK-N4", "Tim kiem", "perPage = -1", "tra tat ca (thiet ke: -1 = lay tat ca)", f"{s}, {len(d['items'])}/{d['total']} cong thuc", s == 200 and len(d["items"]) == d["total"])

    # ---------------- Ke hoach bua an
    s, d = api("POST", "/api/households/mealplans", json={"date": hom_nay, "entryType": "brunch", "title": "x"})
    ca("KH-N1", "Ke hoach", "entryType khong hop le", "4xx", s, 400 <= s < 500)
    s, d = api("POST", "/api/households/mealplans", json={"date": "2026-13-45", "entryType": "lunch", "title": "x"})
    ca("KH-N2", "Ke hoach", "Ngay khong ton tai", "4xx", s, 400 <= s < 500)
    s, d = api("POST", "/api/households/mealplans", json={"date": hom_nay, "entryType": "lunch"})
    ca("KH-N3", "Ke hoach", "Khong co tieu de va khong co cong thuc", "4xx", s, 400 <= s < 500)
    ma_gia = str(uuid.uuid4())
    s, d = api("POST", "/api/households/mealplans", json={"date": hom_nay, "entryType": "lunch", "title": "PW-N", "recipeId": ma_gia})
    ca("KH-N4", "Ke hoach", "recipeId khong ton tai", "4xx", f"{s}" + (", van luu recipeId gia" if s == 201 else ""), 400 <= s < 500)
    if s == 201:
        api("DELETE", f"/api/households/mealplans/{d['id']}")

    # ---------------- Mua sam
    s, lst = api("POST", "/api/households/shopping/lists", json={"name": "PW-N"})
    lid = lst["id"]
    s, _ = api("POST", "/api/households/shopping/items", json={"shoppingListId": str(uuid.uuid4()), "note": "x"})
    ca("MS-N1", "Mua sam", "shoppingListId khong ton tai", "404 hoac 4xx", s, 400 <= s < 500, "500 = ValidationError khi luu" if s == 500 else "")
    s, d = api("POST", "/api/households/shopping/items", json={"shoppingListId": lid, "note": "am", "quantity": -3})
    n = len(d.get("createdItems", [])) if isinstance(d, dict) else "-"
    ca("MS-N2", "Mua sam", "So luong am (-3)", "4xx", f"{s}, tao {n} muc", 400 <= s < 500)
    s, d = api("POST", "/api/households/shopping/items", json={"shoppingListId": lid, "note": "am le", "quantity": -0.5})
    ca("MS-N3", "Mua sam", "So luong am le (-0.5)", "4xx", s, 400 <= s < 500, "500 = KeyError '-' trong display_fraction" if s == 500 else "")
    s, d = api("POST", "/api/households/shopping/items", json={"shoppingListId": lid, "note": "food gia", "foodId": str(uuid.uuid4())})
    ca("MS-N4", "Mua sam", "foodId khong ton tai", "4xx", f"{s}" + (", van luu foodId gia" if s == 201 else ""), 400 <= s < 500)
    s, d = api("POST", "/api/households/shopping/lists", json={"name": ""})
    ca("MS-N5", "Mua sam", "Tao danh sach ten rong", "4xx", s, 400 <= s < 500)
    if s == 201:
        api("DELETE", f"/api/households/shopping/lists/{d['id']}")
    s, d = api("POST", "/api/households/shopping/lists", json={})
    if s == 201:
        api("DELETE", f"/api/households/shopping/lists/{d['id']}")
    api("DELETE", f"/api/households/shopping/lists/{lid}")

    dat = sum(1 for x in KQ if x["dat"])
    print(f"\nTong: {len(KQ)} ca am tinh, dat mong doi {dat}, khac mong doi {len(KQ) - dat}")
    with open(os.path.join(base.HERE, "ket_qua_am_tinh.json"), "w", encoding="utf-8") as f:
        json.dump(KQ, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
