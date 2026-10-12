"""Tạo trang HTML chỉ đọc từ JSON bằng chứng mục C để xem/chụp ảnh.

Không gọi API, không tạo kết quả thử nghiệm. Chạy sau chuan_bi_muc_c.py verify.
"""
import html
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs" / "evidence"
STYLE = """
body {font:18px/1.5 'Segoe UI',sans-serif;margin:32px;color:#172334;background:#fff;max-width:1250px}
h1 {font-size:28px;margin:0 0 8px} h2 {font-size:21px;margin:16px 0 8px}
pre {font:16px/1.5 Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;
background:#f3f5f7;border:1px solid #ccd3dc;padding:18px}
p {margin:8px 0} table {border-collapse:collapse;width:100%;font-size:16px}
td,th {border:1px solid #ccd3dc;padding:8px;text-align:left} th {background:#edf1f5}
"""


def page(filename, title, timestamp, source, content, base_url):
    text = f'''<!doctype html><html lang="vi"><meta charset="utf-8">
<title>{html.escape(title)}</title><style>{STYLE}</style>
<h1>{html.escape(title)}</h1><p>Nhóm 22 · Mealie v3.28.0 · {html.escape(base_url.removeprefix('http://'))}</p>
<p>Thời điểm ghi log: {html.escape(timestamp)}</p>
<p>Nguồn: {html.escape(source)}. Trang hiển thị log đã ghi nhận; không phải ảnh terminal.</p>
{content}</html>'''
    (OUT / filename).write_bytes(text.replace("\r\n", "\n").encode("utf-8"))


def pre(text):
    return "<pre>" + html.escape(text) + "</pre>"


def main():
    env = json.loads((OUT / "C-environment.json").read_text(encoding="utf-8-sig"))
    api = json.loads((OUT / "C-api-verification.json").read_text(encoding="utf-8"))
    for filename, title, text in [
        ("C-01-log.html", "Phiên bản môi trường lab", f"{env['windows']['Caption']} {env['windows']['Version']}\nDocker Desktop {env['dockerDesktop']}\n\n> docker --version\n{env['dockerVersion']}\n\n> docker compose version\n{env['composeVersion']}"),
        ("C-02-log.html", "Khởi chạy Mealie", "> docker compose up -d\n" + env["composeUp"]),
        ("C-03-log.html", "Trạng thái container và SQLite", "> docker compose ps\n" + env["composePs"] + "\n\n> ls -l /app/data/mealie.db (trong container)\n" + env["database"] + "\n\nImage digest:\n" + env["imageDigest"]),
    ]:
        page(filename, title, env["recordedAt"], "C-environment.json", pre(text), api["baseUrl"])
    for code in ["C-31", "C-32", "C-33"]:
        row = next(r for r in api["steps"] if r["step"].startswith(code))
        content = f"<h2>{html.escape(row['method'] + ' ' + row['path'])}</h2>"
        if row.get("request"):
            content += "<h2>Request JSON</h2>" + pre(json.dumps(row["request"], ensure_ascii=False, indent=2))
        content += f"<h2>HTTP {row['status']}</h2>" + pre(json.dumps(row["response"], ensure_ascii=False, indent=2))
        page(code + "-log.html", row["step"], api["recordedAt"], "C-api-verification.json", content, api["baseUrl"])
    rows = "".join(f"<tr><td>{html.escape(r['step'])}</td><td>{r.get('status', '—')}</td><td>{'PASS' if r['passed'] else 'FAIL'}</td></tr>" for r in api["steps"])
    page("C-api-log.html", "Kết quả kiểm tra ba luồng API", api["recordedAt"], "C-api-verification.json",
         "<table><tr><th>Bước</th><th>HTTP</th><th>Kết quả</th></tr>" + rows + "</table><h2>Trạng thái sau dọn dữ liệu</h2>" + pre(json.dumps(api["cleanup"], ensure_ascii=False, indent=2)), api["baseUrl"])
    print("Created 7 read-only evidence pages from recorded JSON.")


if __name__ == "__main__":
    main()
