"""Nạp seed và xác minh ba luồng mục C trên Mealie local, chỉ dùng Python stdlib.

python scripts/chuan_bi_muc_c.py seed
python scripts/chuan_bi_muc_c.py verify
Tài khoản lab mặc định theo README; có thể đổi bằng MEALIE_EMAIL/MEALIE_PASSWORD.
Không ghi token hoặc mật khẩu vào bằng chứng.
"""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "evidence"
PASSWORD = os.environ.get("MEALIE_PASSWORD", "Nhom22@Mealie")
EMAIL = os.environ.get("MEALIE_EMAIL", "nhom22@example.com")
FLAGS = ["canInvite", "canManage", "canManageHousehold", "canOrganize"]
RECIPES = [
    ("Phở bò", ["Món chính"], []),
    ("Bún chả", ["Món chính"], ["Nhanh"]),
    ("Gỏi cuốn chay", ["Món chính"], ["Nhanh", "Chay"]),
    ("Lẩu thái", ["Món chính"], ["Cay"]),
    ("Chè đậu", ["Tráng miệng"], ["Chay"]),
    ("Bánh flan", ["Tráng miệng"], []),
    ("Sinh tố bơ", ["Đồ uống", "Tráng miệng"], ["Nhanh", "Chay"]),
    ("Trà đá", ["Đồ uống"], ["Nhanh"]),
    ("Cà phê sữa", ["Đồ uống"], []),
    ("Nước mắm pha", [], ["Cay"]),
    ("Cơm trắng", [], []),
    ("Xôi xoài", ["Món chính", "Tráng miệng"], ["Chay"]),
]


class Api:
    def __init__(self, base, email=EMAIL):
        self.base = base
        self.token = None
        _, data = self.call("POST", "/api/auth/token", form={"username": email, "password": PASSWORD})
        self.token = data["access_token"]

    def call(self, method, path, body=None, form=None, expected=None):
        headers = {}
        data = None
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        if form is not None:
            data = urlencode(form).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = Request(self.base + path, data=data, headers=headers, method=method)
        try:
            response = urlopen(req, timeout=30)
        except HTTPError as error:
            response = error
        with response:
            status = response.status
            text = response.read().decode("utf-8")
        result = json.loads(text) if text else None
        if expected is None:
            ok = 200 <= status < 300
        else:
            ok = status == expected
        if not ok:
            raise RuntimeError(f"{method} {path}: HTTP {status}, expected {expected or '2xx'}; {text[:400]}")
        return status, result

    def get(self, path):
        return self.call("GET", path)[1]


def all_items(api, path):
    items = []
    page = 1
    while True:
        data = api.get(path + ("&" if "?" in path else "?") + f"page={page}&perPage=100")
        if isinstance(data, list):
            return data
        items.extend(data["items"])
        if page >= data["total_pages"]:
            return items
        page += 1


def save(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def now():
    return datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds")


def seed(api):
    me = api.get("/api/users/self")
    if not me["admin"]:
        raise RuntimeError("Seed cần tài khoản admin của môi trường lab.")
    organizers = {}
    for kind, names in [("categories", ["Món chính", "Tráng miệng", "Đồ uống"]), ("tags", ["Nhanh", "Chay", "Cay"])]:
        found = {x["name"]: x for x in all_items(api, "/api/organizers/" + kind)}
        for name in names:
            if name not in found:
                _, found[name] = api.call("POST", "/api/organizers/" + kind, {"name": name}, expected=201)
        organizers[kind] = {n: found[n] for n in names}
    existing = {x["name"]: x for x in all_items(api, "/api/recipes")}
    recipes = []
    for name, cats, tags in RECIPES:
        if name not in existing:
            _, slug = api.call("POST", "/api/recipes", {"name": name}, expected=201)
        else:
            slug = existing[name]["slug"]
        recipe = api.get("/api/recipes/" + slug)
        expected_cats = [organizers["categories"][c] for c in cats]
        expected_tags = [organizers["tags"][t] for t in tags]
        # Chỉ bổ sung cho công thức vừa tạo; không ghi đè công thức cùng tên đã có.
        if name in existing:
            for field, desired in [("recipeCategory", cats), ("tags", tags)]:
                if {x["name"] for x in recipe[field]} != set(desired):
                    raise RuntimeError(f"{name}: {field} đã có khác seed; cần kiểm tra thủ công, không ghi đè.")
        else:
            recipe["recipeCategory"] = expected_cats
            recipe["tags"] = expected_tags
            api.call("PUT", "/api/recipes/" + slug, recipe, expected=200)
        recipes.append({"name": name, "slug": slug, "categories": cats, "tags": tags})
    users = {x["email"]: x for x in all_items(api, "/api/admin/users")}
    accounts = []
    for username, enabled in [("khongquyen", False), ("duquyen", True)]:
        email = username + "@example.com"
        if email not in users:
            body = {"username": username, "fullName": username, "email": email, "password": PASSWORD,
                    "group": me["group"], "household": me["household"], "admin": False,
                    **{f: enabled for f in FLAGS}}
            _, users[email] = api.call("POST", "/api/admin/users", body, expected=201)
        u = Api(api.base, email).get("/api/users/self")
        if u["admin"] or any(u[f] != enabled for f in FLAGS) or u["group"] != me["group"] or u["household"] != me["household"]:
            raise RuntimeError(f"{email}: tài khoản đã có khác seed; không tự sửa quyền.")
        accounts.append({k: u[k] for k in ["id", "username", "email", "admin", "group", "household", *FLAGS]})
    inventory = {"recordedAt": now(), "baseUrl": api.base, "version": api.get("/api/app/about")["version"],
                 "categories": list(organizers["categories"].values()), "tags": list(organizers["tags"].values()),
                 "recipes": recipes, "users": accounts}
    save("C-seed-inventory.json", inventory)
    print("Seed OK: 3 category, 3 tag, 12 công thức, 2 user lab. Không tạo trùng khi chạy lại.")


def verify(api):
    records = []
    def record(label, method, path, body=None, expected=200, check=None):
        status, data = api.call(method, path, body, expected=expected)
        if check is not None and not check(data):
            raise RuntimeError("Kết quả sai: " + label)
        records.append({"step": label, "method": method, "path": path, "request": body,
                        "status": status, "response": data, "passed": True})
        return data
    all_recipes = api.get("/api/recipes?perPage=100")
    if all_recipes["total"] != 12 or {x["name"] for x in all_recipes["items"]} != {x[0] for x in RECIPES}:
        raise RuntimeError("Cần đúng bộ 12 công thức seed, không có công thức demo tồn dư.")
    cases = [
        ("C-10 đủ 12 công thức", {}, {x[0] for x in RECIPES}),
        ("C-11 Món chính", {"categories": "mon-chinh"}, {"Bún chả", "Gỏi cuốn chay", "Lẩu thái", "Phở bò", "Xôi xoài"}),
        ("C-12 Món chính và Chay", {"categories": "mon-chinh", "tags": "chay"}, {"Gỏi cuốn chay", "Xôi xoài"}),
        ("Hai category OR", {"categories": ["mon-chinh", "trang-mieng"], "requireAllCategories": "false"}, {"Bún chả", "Gỏi cuốn chay", "Lẩu thái", "Phở bò", "Xôi xoài", "Bánh flan", "Chè đậu", "Sinh tố bơ"}),
        ("Hai category AND", {"categories": ["mon-chinh", "trang-mieng"], "requireAllCategories": "true"}, {"Xôi xoài"}),
        ("Hai tag AND", {"tags": ["nhanh", "chay"], "requireAllTags": "true"}, {"Gỏi cuốn chay", "Sinh tố bơ"}),
    ]
    for label, query, names in cases:
        path = "/api/recipes?" + urlencode({"perPage": 50, **query}, doseq=True)
        d = record(label, "GET", path, check=lambda d, names=names: d["total"] == len(names) and {x["name"] for x in d["items"]} == names)
        # Giữ response gọn, đủ chứng minh tập kết quả.
        records[-1]["response"] = {"total": d["total"], "names": [x["name"] for x in d["items"]]}
    asc = record("C-13 sắp xếp tăng", "GET", "/api/recipes?perPage=50&orderBy=name&orderDirection=asc")
    desc = record("C-13 sắp xếp giảm", "GET", "/api/recipes?perPage=50&orderBy=name&orderDirection=desc",
                  check=lambda d: [x["name"] for x in d["items"]] == [x["name"] for x in asc["items"]][::-1])
    for row, data in zip(records[-2:], [asc, desc]):
        row["response"] = {"total": data["total"], "names": [x["name"] for x in data["items"]]}

    original = record("C-20 cấu hình ban đầu", "GET", "/api/households/preferences")
    changed = {k: v for k, v in original.items() if k != "id"}
    changed.update(recipeShowNutrition=not original["recipeShowNutrition"], recipeDisableComments=not original["recipeDisableComments"])
    slug = None
    try:
        record("C-21 lưu cấu hình", "PUT", "/api/households/preferences", changed,
               check=lambda d: all(d[k] == v for k, v in changed.items()))
        slug = record("C-22 tạo công thức mới", "POST", "/api/recipes", {"name": "C22 Demo " + uuid.uuid4().hex[:8]}, expected=201)
        mapping = {"public": "recipePublic", "showNutrition": "recipeShowNutrition", "showAssets": "recipeShowAssets",
                   "landscapeView": "recipeLandscapeView", "disableComments": "recipeDisableComments"}
        d = record("C-23 công thức kế thừa đủ 5 tùy chọn", "GET", "/api/recipes/" + slug,
                   check=lambda d: all(d["settings"][k] == changed[v] for k, v in mapping.items()))
        records[-1]["response"] = {"name": d["name"], "settings": d["settings"]}
    finally:
        # Khôi phục cấu hình ngay cả khi kiểm tra/xóa công thức gặp lỗi.
        try:
            if slug is not None:
                api.call("DELETE", "/api/recipes/" + slug, expected=200)
        finally:
            api.call("PUT", "/api/households/preferences", original, expected=200)
    if api.get("/api/households/preferences") != original:
        raise RuntimeError("Chưa khôi phục đúng cấu hình household.")

    user_api = Api(api.base, "khongquyen@example.com")
    user = user_api.get("/api/users/self")
    if user["admin"] or any(user[f] for f in FLAGS):
        raise RuntimeError("User khongquyen chưa ở trạng thái không quyền.")
    records.append({"step": "C-30 user không quyền", "response": {"username": user["username"], "admin": user["admin"], **{f: user[f] for f in FLAGS}}, "passed": True})
    name = "C22 Permission " + uuid.uuid4().hex[:8]
    status, data = user_api.call("POST", "/api/organizers/categories", {"name": name}, expected=403)
    records.append({"step": "C-31 tạo category bị chặn", "method": "POST", "path": "/api/organizers/categories", "status": status, "response": data, "passed": True})
    category_id = None
    permissions = {"userId": user["id"], **{f: user[f] for f in FLAGS}}
    try:
        record("C-32 admin cấp canOrganize", "PUT", "/api/households/permissions", {**permissions, "canOrganize": True})
        records[-1]["response"] = {k: records[-1]["response"][k] for k in ["username", "admin", *FLAGS]}
        user_api = Api(api.base, "khongquyen@example.com")
        status, category = user_api.call("POST", "/api/organizers/categories", {"name": name}, expected=201)
        category_id = category["id"]
        records.append({"step": "C-33 tạo category được phép", "method": "POST", "path": "/api/organizers/categories", "status": status, "response": category, "passed": True})
    finally:
        try:
            if category_id is not None:
                api.call("DELETE", "/api/organizers/categories/" + category_id, expected=200)
        finally:
            api.call("PUT", "/api/households/permissions", permissions, expected=200)
    restored = Api(api.base, "khongquyen@example.com").get("/api/users/self")
    if any(restored[f] for f in FLAGS) or restored["admin"]:
        raise RuntimeError("Chưa khôi phục user không quyền.")
    if api.get("/api/recipes?perPage=1")["total"] != 12:
        raise RuntimeError("Còn công thức demo tồn dư.")
    save("C-api-verification.json", {"recordedAt": now(), "baseUrl": api.base, "version": api.get("/api/app/about")["version"],
         "steps": records, "cleanup": {"householdRestored": True, "userPermissionsRestored": True, "recipeTotal": 12, "temporaryCategoryDeleted": True}})
    print(f"PASS: {len(records)} bước xác minh; 3 luồng; đã khôi phục household, quyền user và xóa dữ liệu tạm.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["seed", "verify"])
    parser.add_argument("--base-url", default="http://localhost:9925")
    args = parser.parse_args()
    url = urlparse(args.base_url)
    if url.scheme != "http" or url.hostname not in {"localhost", "127.0.0.1", "::1"} or url.username or url.password or url.path not in {"", "/"} or url.query or url.fragment:
        parser.error("Chỉ chạy trên HTTP localhost của môi trường lab.")
    api = Api(args.base_url.rstrip("/"))
    version = api.get("/api/app/about")["version"]
    if version != "v3.28.0":
        raise RuntimeError(f"Sai phiên bản Mealie: {version}")
    {"seed": seed, "verify": verify}[args.action](api)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
