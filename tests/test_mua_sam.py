"""Luong danh sach mua sam: tao danh sach, them muc, doc lai, doi trang thai checked, xoa.

Moi dong trong cases/shopping.*.tsv la mot test case.
Bao gom cac muc phu:
  - 2-wise (Pairwise, 9 test): cases/shopping.o2.tsv
  - 3-wise (23 test): cases/shopping.o3.tsv
  - Thu het (144 test): cases/shopping.all.tsv
"""
import uuid

import pytest

from chung import doc_case

NOTE = {
    "none": None,
    "short": "Muoi",
    "accented": "Hành lá tươi",
}


def tham_so(c, lid, nen):
    """Doi nhan trong file case thanh du lieu that gui len API."""
    note = NOTE[c["note"]]
    body = {
        "shoppingListId": lid,
        "quantity": float(c["quantity"]),
        "checked": c["checked"] == "true",
    }
    if note:
        body["note"] = note
    if c["unit"] != "none":
        body["unitId"] = nen["unit"]["id"]
    if c["food"] != "none":
        body["foodId"] = nen["food"]["id"]
    if c["label"] != "none":
        body["labelId"] = nen["label"]["id"]
    return note, body


def kiem_tra(api, nen, c):
    """Chay mot case danh sach mua sam, kiem tra cac bat bien I1, I2, I3, I5."""
    s, lst = api("POST", "/api/households/shopping/lists", json={"name": f"PW-MS-{uuid.uuid4().hex[:6]}"})
    if s == 500:
        return ["I1: lỗi server 500 khi tạo danh sách mua sắm"]
    if s != 201 or not isinstance(lst, dict) or not lst.get("id"):
        return [f"I2: tạo danh sách trả {s}"]

    lid = lst["id"]
    item_id = None
    loi = []
    try:
        note, body = tham_so(c, lid, nen)
        s1, d = api("POST", "/api/households/shopping/items", json=body)
        if s1 == 500:
            return ["I1: lỗi server 500 khi thêm mục mua sắm"]
        if s1 != 201:
            return [f"I2: thêm mục trả {s1}"]
        created = d.get("createdItems", []) if isinstance(d, dict) else []
        if not created:
            return ["I2: thêm mục thành công nhưng không có createdItems"]

        item_id = created[0]["id"]

        # I2, I3: doc lai danh sach va kiem tra du lieu da luu
        s2, full = api("GET", f"/api/households/shopping/lists/{lid}")
        if s2 == 500:
            loi.append("I1: lỗi server 500 khi đọc danh sách")
        elif s2 != 200 or not isinstance(full, dict):
            loi.append(f"I2: đọc danh sách trả {s2}")
        else:
            it = next((x for x in full.get("listItems", []) if x.get("id") == item_id), None)
            if it is None:
                loi.append("I3: không đọc lại được mục vừa thêm")
            else:
                if it.get("quantity") != float(c["quantity"]):
                    loi.append(f"I3: quantity={it.get('quantity')} khác {float(c['quantity'])}")
                if (it.get("note") or "") != (note or ""):
                    loi.append(f"I3: note={it.get('note')!r} khác {(note or '')!r}")
                if it.get("checked") != (c["checked"] == "true"):
                    loi.append(f"I3: checked={it.get('checked')} khác {c['checked'] == 'true'}")
                for khoa, cot, key in (
                    ("unitId", "unit", "unit"),
                    ("foodId", "food", "food"),
                    ("labelId", "label", "label"),
                ):
                    muon = nen[key]["id"] if c[cot] != "none" else None
                    if it.get(khoa) != muon:
                        loi.append(f"I3: {khoa}={it.get(khoa)} khác {muon}")

                # Cap nhat trang thai checked (tick / bo tick) va doc lai
                trang_thai_moi = not it["checked"]
                s3, _ = api(
                    "PUT",
                    f"/api/households/shopping/items/{item_id}",
                    json={**it, "checked": trang_thai_moi},
                )
                if s3 == 500:
                    loi.append("I1: lỗi server 500 khi cập nhật checked")
                elif s3 != 200:
                    loi.append(f"I2: cập nhật checked trả {s3}")
                else:
                    s4, full2 = api("GET", f"/api/households/shopping/lists/{lid}")
                    if s4 == 500:
                        loi.append("I1: lỗi server 500 khi đọc lại sau cập nhật")
                    elif s4 != 200 or not isinstance(full2, dict):
                        loi.append(f"I2: đọc lại sau cập nhật trả {s4}")
                    else:
                        it2 = next((x for x in full2.get("listItems", []) if x.get("id") == item_id), None)
                        if it2 is None or it2.get("checked") != trang_thai_moi:
                            loi.append("I3: đổi checked không lưu")
    finally:
        # I5: luon xoa muc va danh sach da tao du test pass hay fail
        if item_id:
            api("DELETE", "/api/households/shopping/items", params={"ids": item_id})
        api("DELETE", f"/api/households/shopping/lists/{lid}")

    # I5: kiem tra xoa danh sach xong khong con nua
    s5, _ = api("GET", f"/api/households/shopping/lists/{lid}")
    if s5 != 404:
        loi.append(f"I5: xóa danh sách xong đọc lại trả {s5} thay vì 404")

    return loi


@pytest.mark.parametrize("c", doc_case("shopping.o2.tsv", "L"))
def test_mua_sam_2wise(api, nen, c):
    loi = kiem_tra(api, nen, c)
    assert not loi, "; ".join(sorted(set(loi)))


@pytest.mark.o3
@pytest.mark.parametrize("c", doc_case("shopping.o3.tsv", "L", 2))
def test_mua_sam_3wise(api, nen, c):
    loi = kiem_tra(api, nen, c)
    assert not loi, "; ".join(sorted(set(loi)))


@pytest.mark.het
@pytest.mark.parametrize("c", doc_case("shopping.all.tsv", "L", 3))
def test_mua_sam_thu_het(api, nen, c):
    loi = kiem_tra(api, nen, c)
    assert not loi, "; ".join(sorted(set(loi)))
