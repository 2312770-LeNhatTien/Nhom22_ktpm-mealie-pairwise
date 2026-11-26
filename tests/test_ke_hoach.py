"""Luong ke hoach bua an: POST /api/households/mealplans, doc lai theo ngay, xoa.

Moi dong trong cases/mealplan.*.tsv la mot test case.
Bao gom cac muc phu:
  - 2-wise (Pairwise, 16 test): cases/mealplan.o2.tsv
  - 3-wise (48 test): cases/mealplan.o3.tsv
  - Thu het (96 test): cases/mealplan.all.tsv
"""
import datetime as dt
import pytest

from chung import doc_case

TODAY = dt.date.today()
NGAY = {
    "past": TODAY - dt.timedelta(days=7),
    "today": TODAY,
    "future": TODAY + dt.timedelta(days=7),
}
TIEU_DE = {
    "title_short": "Banh mi",
    "title_accented": "Bữa sáng đặc biệt",
    "recipe_and_title": "Món của bà",
}


def tham_so(c, nen):
    """Doi nhan trong file case thanh du lieu that gui len API."""
    ngay = NGAY[c["date"]].isoformat()
    body = {"date": ngay, "entryType": c["entryType"]}
    if c["content"] in TIEU_DE:
        body["title"] = TIEU_DE[c["content"]]
    if c["content"].startswith("recipe"):
        body["recipeId"] = nen["recipe_id"]
    if c["text"] == "note":
        body["text"] = "ghi chu"
    return ngay, body


def kiem_tra(api, nen, c):
    """Chay mot case ke hoach bua an, kiem tra cac bat bien I1, I2, I3, I5."""
    ngay, body = tham_so(c, nen)
    s, d = api("POST", "/api/households/mealplans", json=body)
    if s == 500:
        return ["I1: lỗi server 500 khi tạo mục kế hoạch"]
    if s != 201:
        return [f"I2: tạo trả {s}"]

    plan_id = d.get("id") if isinstance(d, dict) else None
    if not plan_id:
        return ["I2: tạo thành công nhưng không có id"]

    loi = []
    try:
        # I2, I3: doc lai theo ngay vua tao
        s2, ds = api(
            "GET",
            "/api/households/mealplans",
            params={"start_date": ngay, "end_date": ngay, "perPage": 100},
        )
        if s2 == 500:
            loi.append("I1: lỗi server 500 khi đọc lại")
        elif s2 != 200:
            loi.append(f"I2: đọc trả {s2}")
        else:
            items = ds.get("items", []) if isinstance(ds, dict) else []
            tim = [x for x in items if x.get("id") == plan_id]
            if not tim:
                loi.append("I3: không đọc lại được mục theo ngày")
            else:
                x = tim[0]
                if x.get("entryType") != c["entryType"]:
                    loi.append(f"I3: entryType={x.get('entryType')} khác {c['entryType']}")
                if x.get("date") != ngay:
                    loi.append(f"I3: date={x.get('date')} khác {ngay}")
                if (x.get("title") or "") != body.get("title", ""):
                    loi.append(f"I3: title={x.get('title')} khác {body.get('title', '')}")
                if (x.get("text") or "") != body.get("text", ""):
                    loi.append(f"I3: text={x.get('text')} khác {body.get('text', '')}")
                if x.get("recipeId") != body.get("recipeId"):
                    loi.append(f"I3: recipeId={x.get('recipeId')} khác {body.get('recipeId')}")
    finally:
        # I5: luon xoa muc da tao du test pass hay fail
        api("DELETE", f"/api/households/mealplans/{plan_id}")

    # I5: kiem tra xoa xong khong con nua
    s3, ds3 = api(
        "GET",
        "/api/households/mealplans",
        params={"start_date": ngay, "end_date": ngay, "perPage": 100},
    )
    if s3 == 200 and isinstance(ds3, dict):
        if any(x.get("id") == plan_id for x in ds3.get("items", [])):
            loi.append("I5: xóa xong vẫn còn")

    return loi


@pytest.mark.parametrize("c", doc_case("mealplan.o2.tsv", "M"))
def test_ke_hoach_2wise(api, nen, c):
    loi = kiem_tra(api, nen, c)
    assert not loi, "; ".join(sorted(set(loi)))


@pytest.mark.o3
@pytest.mark.parametrize("c", doc_case("mealplan.o3.tsv", "M", 2))
def test_ke_hoach_3wise(api, nen, c):
    loi = kiem_tra(api, nen, c)
    assert not loi, "; ".join(sorted(set(loi)))


@pytest.mark.het
@pytest.mark.parametrize("c", doc_case("mealplan.all.tsv", "M", 3))
def test_ke_hoach_thu_het(api, nen, c):
    loi = kiem_tra(api, nen, c)
    assert not loi, "; ".join(sorted(set(loi)))
