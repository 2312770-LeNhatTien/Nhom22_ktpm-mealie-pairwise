"""Tạo bảng công việc giữa kỳ trên GitHub từ file scripts/cong-viec.json.

Cần có GitHub CLI (lệnh gh) đã đăng nhập bằng tài khoản có quyền ghi vào repo.
Chạy lại nhiều lần không tạo trùng: thẻ nào đã có (trùng tiêu đề) thì bỏ qua.

    python scripts/tao_bang_cong_viec.py --thu     xem trước, không ghi gì lên GitHub
    python scripts/tao_bang_cong_viec.py           tạo nhãn, mốc Giữa kỳ và các thẻ (Issues)
    python scripts/tao_bang_cong_viec.py --bang    làm như trên, rồi tạo bảng Projects và xếp thẻ vào cột
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FILE_VIEC = Path(__file__).resolve().parent / "cong-viec.json"
TEN_BANG = "Nhóm 22 - Giữa kỳ"
MAU_NHAN = {
    "TV1": "1d76db",
    "TV2": "0e8a16",
    "TV3": "fbca04",
    "TV4": "d93f0b",
    "TV5": "5319e7",
    "NHOM": "6a737d",
}

GH = shutil.which("gh")


class LoiGh(Exception):
    pass


def gh(*tham_so):
    """Chạy một lệnh gh, trả về phần in ra. Lệnh hỏng thì báo lỗi kèm lời gh in ra."""
    kq = subprocess.run([GH, *tham_so], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if kq.returncode != 0:
        raise LoiGh((kq.stderr or kq.stdout).strip())
    return kq.stdout.strip()


def kiem_tra_gh():
    if GH is None:
        sys.exit(
            "Chưa cài GitHub CLI. Cài bằng lệnh:  winget install --id GitHub.cli\n"
            "Cài xong đóng Command Prompt, mở lại rồi chạy:  gh auth login"
        )
    try:
        gh("auth", "status")
    except LoiGh as loi:
        sys.exit(f"GitHub CLI chưa đăng nhập. Chạy:  gh auth login\n\n{loi}")


def tao_nhan(repo, nguoi, thu):
    print("== Nhãn ==")
    for ma, ng in nguoi.items():
        if thu:
            print(f"  sẽ tạo nhãn: {ng['nhan']}")
            continue
        gh("label", "create", ng["nhan"], "--repo", repo, "--color", MAU_NHAN.get(ma, "ededed"),
           "--description", f"Việc của {ng['ten']}", "--force")
        print(f"  đã có nhãn: {ng['nhan']}")


def tao_moc(repo, moc, thu):
    print("== Mốc ==")
    da_co = gh("api", f"repos/{repo}/milestones?state=all&per_page=100", "--jq", ".[].title").splitlines()
    if moc["ten"] in da_co:
        print(f"  đã có mốc: {moc['ten']}")
    elif thu:
        print(f"  sẽ tạo mốc: {moc['ten']}, hạn {moc['han']}")
    else:
        # 12:00 UTC để GitHub hiển thị đúng ngày hạn ở mọi múi giờ
        gh("api", "-X", "POST", f"repos/{repo}/milestones", "-f", f"title={moc['ten']}",
           "-f", f"description={moc['mo_ta']}", "-f", f"due_on={moc['han']}T12:00:00Z")
        print(f"  đã tạo mốc: {moc['ten']}, hạn {moc['han']}")


def doc_the_da_co(repo):
    """Trả về dict: tiêu đề -> thông tin thẻ đã có trên GitHub (bỏ qua Pull Request)."""
    ra = gh("api", f"repos/{repo}/issues?state=all&per_page=100", "--paginate", "--jq",
            ".[] | select(.pull_request | not) | "
            "{number, state, title, url: .html_url} | @json")
    return {t["title"]: t for t in map(json.loads, filter(None, ra.splitlines()))}


def tao_mot_the(repo, the, moc):
    """Tạo một thẻ có nhãn tên người làm, trả về (số thẻ, đường dẫn)."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(the["noi_dung"])
    try:
        url = gh("issue", "create", "--repo", repo, "--title", the["tieu_de"], "--body-file", f.name,
                 "--label", the["nhan"], "--milestone", moc)
    finally:
        os.unlink(f.name)
    url = url.splitlines()[-1].strip()
    return int(url.rstrip("/").rsplit("/", 1)[1]), url


def tao_the(repo, du_lieu, thu):
    print("== Thẻ công việc ==")
    moc = du_lieu["milestone"]["ten"]
    da_co = doc_the_da_co(repo)
    moi = 0
    for the in du_lieu["the"]:
        cu = da_co.get(the["tieu_de"])
        if cu:
            print(f"  #{cu['number']} đã có: {the['tieu_de']}")
            continue
        if thu:
            print(f"  sẽ tạo: {the['tieu_de']}  [{the['nhan']}]" + ("  (đóng luôn vì đã xong)" if the["da_xong"] else ""))
            moi += 1
            continue
        so, url = tao_mot_the(repo, the, moc)
        if the["da_xong"]:
            gh("issue", "close", str(so), "--repo", repo, "--reason", "completed")
        da_co[the["tieu_de"]] = {"number": so, "state": "closed" if the["da_xong"] else "open",
                                 "title": the["tieu_de"], "url": url}
        moi += 1
        print(f"  #{so} đã tạo: {the['tieu_de']}  [{the['nhan']}]")
    if thu:
        print(f"  Sẽ tạo {moi} thẻ mới, đang có {len(da_co)} thẻ trên repo.")
    else:
        print(f"  Tạo mới {moi} thẻ, tổng cộng {len(da_co)} thẻ trên repo.")
    return da_co


def tao_bang(repo, du_lieu, da_co):
    print("== Bảng Projects ==")
    chu, ten_repo = repo.split("/")
    ds = json.loads(gh("project", "list", "--owner", chu, "--format", "json", "--limit", "100")).get("projects", [])
    bang = next((b for b in ds if b["title"] == TEN_BANG), None)
    if bang is None:
        bang = json.loads(gh("project", "create", "--owner", chu, "--title", TEN_BANG, "--format", "json"))
        print(f"  đã tạo bảng: {bang['url']}")
        try:
            gh("project", "link", str(bang["number"]), "--owner", chu, "--repo", ten_repo)
        except LoiGh:
            print("  chưa gắn được bảng vào repo. Làm tay: tab Projects của repo → Link a project.")
    else:
        print(f"  bảng đã có: {bang['url']}")
    so = str(bang["number"])

    truong = json.loads(gh("project", "field-list", so, "--owner", chu, "--format", "json"))["fields"]
    cot = next((t for t in truong if t["name"] == "Status"), None)
    lua_chon = {o["name"]: o["id"] for o in (cot or {}).get("options", [])}

    trong_bang = json.loads(gh("project", "item-list", so, "--owner", chu, "--format", "json", "--limit", "500"))
    co_san = {(i.get("content") or {}).get("url"): i for i in trong_bang.get("items", [])}

    them = 0
    for the in du_lieu["the"]:
        tt = da_co.get(the["tieu_de"])
        if tt is None:
            continue
        muc = co_san.get(tt["url"])
        if muc is None:
            muc = json.loads(gh("project", "item-add", so, "--owner", chu, "--url", tt["url"], "--format", "json"))
            them += 1
        elif muc.get("status"):
            continue  # thẻ đã được xếp cột, không đụng vào
        ten_cot = "Done" if tt["state"] == "closed" else ("In Progress" if the.get("dang_lam") else "Todo")
        if cot and ten_cot in lua_chon:
            gh("project", "item-edit", "--id", muc["id"], "--project-id", bang["id"],
               "--field-id", cot["id"], "--single-select-option-id", lua_chon[ten_cot])
    print(f"  Thêm {them} thẻ vào bảng.")
    print(f"  Mở bảng: {bang['url']}")
    print("  Nếu bảng đang hiện dạng danh sách: bấm mũi tên cạnh tên View → Layout → Board.")


HUONG_DAN_BANG_TAY = """
Chưa tạo được bảng Projects tự động. Các thẻ vẫn nằm đủ ở tab Issues. Có hai cách:

1. Cấp thêm quyền cho GitHub CLI rồi chạy lại:
       gh auth refresh -s project
       python scripts/tao_bang_cong_viec.py --bang

2. Tạo bằng tay, mất khoảng 2 phút:
   - Mở repo trên GitHub → tab Projects → Link a project → New project → chọn Board → Create.
   - Trong bảng: bấm "+ Add item" ở cuối cột → "Add item from repository" → chọn repo → tích hết → Add.
"""


def main():
    for luong in (sys.stdout, sys.stderr):
        if hasattr(luong, "reconfigure"):
            luong.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description="Tạo bảng công việc giữa kỳ trên GitHub.")
    ap.add_argument("--thu", action="store_true", help="chỉ in ra những gì sẽ làm, không ghi gì lên GitHub")
    ap.add_argument("--bang", action="store_true", help="tạo thêm bảng Projects và xếp thẻ vào cột")
    tham_so = ap.parse_args()

    kiem_tra_gh()
    du_lieu = json.loads(FILE_VIEC.read_text(encoding="utf-8"))
    repo = du_lieu["repo"]
    print(f"Repo: {repo}" + ("   (chạy thử, không ghi gì)" if tham_so.thu else ""))

    try:
        tao_nhan(repo, du_lieu["nguoi"], tham_so.thu)
        tao_moc(repo, du_lieu["milestone"], tham_so.thu)
        da_co = tao_the(repo, du_lieu, tham_so.thu)
    except LoiGh as loi:
        sys.exit(f"\nGitHub từ chối một lệnh:\n{loi}\n\nSửa xong chạy lại lệnh này, các phần đã tạo sẽ không bị tạo trùng.")

    if tham_so.bang and not tham_so.thu:
        try:
            tao_bang(repo, du_lieu, da_co)
        except (LoiGh, KeyError, ValueError) as loi:
            print(f"\n{loi}")
            print(HUONG_DAN_BANG_TAY)

    print(f"\nXong. Danh sách thẻ: https://github.com/{repo}/issues")


if __name__ == "__main__":
    main()
