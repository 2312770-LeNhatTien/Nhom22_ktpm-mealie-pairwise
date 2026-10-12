"""Phần dùng chung cho mọi file test: địa chỉ Mealie, đăng nhập, đọc file case."""
import csv
import os
import uuid
from pathlib import Path

import pytest
import requests

# Mặc định theo bảng dùng chung trong README. Máy nào đổi cổng thì đặt biến môi trường
# MEALIE_BASE_URL thay vì sửa file này, ví dụ:  set MEALIE_BASE_URL=http://localhost:9926
BASE_URL = os.getenv("MEALIE_BASE_URL", "http://localhost:9925").rstrip("/")
ADMIN_EMAIL = os.getenv("MEALIE_USER", "nhom22@example.com")
ADMIN_PASSWORD = os.getenv("MEALIE_PASSWORD", "Nhom22@Mealie")

CASES_DIR = Path(__file__).resolve().parent.parent / "cases"


def doc_cases(ten_file):
    """Đọc một file .tsv do PICT sinh ra, trả về danh sách dict (mỗi dict là một test case)."""
    with open(CASES_DIR / ten_file, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def dang_nhap(email, mat_khau):
    """Gọi API đăng nhập, trả về header Authorization để gắn vào các lần gọi sau."""
    r = requests.post(
        f"{BASE_URL}/api/auth/token",
        data={"username": email, "password": mat_khau},
        timeout=10,
    )
    assert r.status_code == 200, f"Đăng nhập thất bại: {r.status_code} {r.text}"
    return {"Authorization": "Bearer " + r.json()["access_token"]}


@pytest.fixture(scope="session")
def admin():
    """Header của tài khoản admin dùng chung. Chỉ đăng nhập một lần cho cả lượt chạy."""
    return dang_nhap(ADMIN_EMAIL, ADMIN_PASSWORD)


def ten_khong_trung(tien_to):
    """Tạo tên không trùng để các case không giẫm lên dữ liệu của nhau."""
    return f"{tien_to} {uuid.uuid4().hex[:8]}"
