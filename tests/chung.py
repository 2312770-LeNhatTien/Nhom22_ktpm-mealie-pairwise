import csv
import os

import pytest
import requests

URL = os.environ.get("MEALIE_URL") or os.environ.get("MEALIE_BASE_URL") or "http://localhost:9925"
USER = os.environ.get("MEALIE_USER", "nhom22@example.com")
PASS = os.environ.get("MEALIE_PASS") or os.environ.get("MEALIE_PASSWORD") or "Nhom22@Mealie"
GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Api:
    def __init__(self):
        self.s = requests.Session()
        r = requests.post(URL + "/api/auth/token", data={"username": USER, "password": PASS}, timeout=30)
        assert r.status_code == 200, f"Dang nhap that bai: {r.status_code} {r.text[:200]}"
        self.s.headers["Authorization"] = "Bearer " + r.json()["access_token"]

    def __call__(self, method, path, **kw):
        r = self.s.request(method, URL + path, timeout=30, **kw)
        try:
            body = r.json()
        except ValueError:
            body = r.text
        return r.status_code, body


def doc_case(ten, ma, so_chu=2):
    duong_dan = os.path.join(GOC, "cases", ten)
    if not os.path.exists(duong_dan):
        thieu = pytest.mark.skip(reason=f"chua co cases/{ten}")
        return [pytest.param(None, id=f"{ma}-thieu-file", marks=thieu)]
    with open(duong_dan, encoding="utf-8-sig", newline="") as f:
        dong = list(csv.DictReader(f, delimiter="\t"))
    return [pytest.param(d, id=f"{ma}{i:0{so_chu}d}") for i, d in enumerate(dong, 1)]
