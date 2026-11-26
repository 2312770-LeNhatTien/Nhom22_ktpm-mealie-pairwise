"""Nạp dữ liệu mẫu (3 category, 3 tag, 12 công thức) vào Mealie local, chỉ dùng Python stdlib.

python scripts/chuan_bi_muc_c.py seed
Tài khoản admin mặc định theo README; có thể đổi bằng MEALIE_EMAIL/MEALIE_PASSWORD.
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
PASSWORD = os.environ.get("MEALIE_PASSWORD", "MyPassword")
EMAIL = os.environ.get("MEALIE_EMAIL", "changeme@example.com")
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
    inventory = {"recordedAt": now(), "baseUrl": api.base, "version": api.get("/api/app/about")["version"],
                 "categories": list(organizers["categories"].values()), "tags": list(organizers["tags"].values()),
                 "recipes": recipes}
    save("C-seed-inventory.json", inventory)
    print("Seed OK: 3 category, 3 tag, 12 công thức. Không tạo trùng khi chạy lại.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["seed"])
    parser.add_argument("--base-url", default="http://localhost:9925")
    args = parser.parse_args()
    url = urlparse(args.base_url)
    if url.scheme != "http" or url.hostname not in {"localhost", "127.0.0.1", "::1"} or url.username or url.password or url.path not in {"", "/"} or url.query or url.fragment:
        parser.error("Chỉ chạy trên HTTP localhost của môi trường lab.")
    api = Api(args.base_url.rstrip("/"))
    version = api.get("/api/app/about")["version"]
    if version != "v3.28.0":
        raise RuntimeError(f"Sai phiên bản Mealie: {version}")
    seed(api)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
