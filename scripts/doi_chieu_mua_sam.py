"""Chạy riêng bằng pytest để lấy số liệu mua sắm cho bảng CK-16."""

import csv
from pathlib import Path
from uuid import uuid4

import pytest

from chay_thu_4_luong import api, chuan_bi, dang_nhap


CASES = Path(__file__).resolve().parents[1] / "cases"
LISTS = "/api/households/shopping/lists"
ITEMS = "/api/households/shopping/items"
NOTES = {"none": "", "short": "Muoi", "accented": "Hành lá tươi"}


def doc_cases(muc):
    with (CASES / f"shopping.{muc}.tsv").open(encoding="utf-8-sig", newline="") as f:
        return [
            pytest.param(case, id=f"L{i:03d}")
            for i, case in enumerate(csv.DictReader(f, delimiter="\t"), 1)
        ]


@pytest.fixture(scope="session")
def nen():
    dang_nhap()
    return chuan_bi()


def goi(method, path, expected, **kwargs):
    status, data = api(method, path, **kwargs)
    assert status < 500, f"I1: {method} {path} trả {status}"
    assert status in expected, f"I2: {method} {path} trả {status}, mong đợi {expected}"
    return data


def kiem_tra(nen, case):
    created = goi("POST", LISTS, (201,), json={"name": f"PW-L-{uuid4().hex}"})
    list_path = f"{LISTS}/{created['id']}"
    try:
        body = {
            "shoppingListId": created["id"],
            "quantity": float(case["quantity"]),
            "checked": case["checked"] == "true",
            "note": NOTES[case["note"]],
        }
        for field in ("unit", "food", "label"):
            if case[field] != "none":
                body[f"{field}Id"] = nen[field]["id"]

        result = goi("POST", ITEMS, (201,), json=body)
        assert len(result["createdItems"]) == 1, "I3: phải tạo đúng một mục"
        item_id = result["createdItems"][0]["id"]
        current = goi("GET", list_path, (200,))
        item = next((row for row in current["listItems"] if row["id"] == item_id), None)
        assert item is not None, "I3: mục vừa tạo không xuất hiện trong danh sách"
        for field in ("quantity", "checked", "unitId", "foodId", "labelId"):
            assert item.get(field) == body.get(field), f"I3: {field} đọc lại khác giá trị gửi"
        assert (item.get("note") or "") == body["note"], "I3: ghi chú đọc lại không khớp"

        checked = not body["checked"]
        goi("PUT", f"{ITEMS}/{item_id}", (200,), json={**item, "checked": checked})
        current = goi("GET", list_path, (200,))
        assert any(
            row["id"] == item_id and row["checked"] == checked
            for row in current["listItems"]
        ), "I3: trạng thái đã mua không được lưu"

        goi("DELETE", ITEMS, (200, 204), params={"ids": item_id})
        current = goi("GET", list_path, (200,))
        assert all(row["id"] != item_id for row in current["listItems"]), "I5: mục vẫn còn"
    finally:
        goi("DELETE", list_path, (200, 204))
        goi("GET", list_path, (404,))


@pytest.mark.parametrize("case", doc_cases("o2"))
def test_mua_sam_2wise(nen, case):
    kiem_tra(nen, case)


@pytest.mark.o3
@pytest.mark.parametrize("case", doc_cases("o3"))
def test_mua_sam_3wise(nen, case):
    kiem_tra(nen, case)


@pytest.mark.het
@pytest.mark.parametrize("case", doc_cases("all"))
def test_mua_sam_thu_het(nen, case):
    kiem_tra(nen, case)
