# Báo cáo kết quả kiểm thử Danh sách mua sắm và Tái lập môi trường (Mục H)

**Nhóm 22 — Kiểm thử phần mềm (Đề tài: R02 Mealie v3.28.0 + K06 Pairwise Microsoft PICT)**  
**Người thực hiện:** Nguyễn Phú Quý (MSSV: 2312731)  
**Thẻ việc:** CK-02, CK-07, CK-10, CK-12, CK-17, CK-18  
**Ngày thực hiện:** 27/11/2026  

---

## 1. Dựng lại Mealie sạch bằng một lệnh (CK-02)

Script `scripts/dung_lai.bat` thực hiện xóa sạch container/volume (`docker compose down -v`), dựng lại Mealie (`docker compose up -d --wait`), thiết lập biến môi trường tài khoản mặc định (`changeme@example.com` / `MyPassword`) và nạp dữ liệu mẫu bằng `python scripts\chuan_bi_muc_c.py seed`.

Kết quả chạy thử liên tiếp trên máy thật:

| Lần chạy | Điều kiện | Thời gian dựng & nạp seed | Kết quả |
| --- | --- | --- | --- |
| Lần 1 | Chưa có image cục bộ (có kéo image `v3.28.0`) | `15:17:18,82` → `15:18:31,19` (~72,4 giây) | `Container mealie Healthy`; nạp đủ 3 category, 3 tag, 12 công thức |
| Lần 2 | Đã có image cục bộ | `15:18:45,70` → `15:19:20,82` (~35,1 giây) | `Container mealie Healthy`; nạp đủ 3 category, 3 tag, 12 công thức |
| Lần chạy trong `may_sach.bat` | Dựng sạch lại trước 2 lượt pytest mục H | `15:22:36,14` → `15:23:12,73` (~36,6 giây) | `Container mealie Healthy`; nạp đủ 3 category, 3 tag, 12 công thức |

---

## 2. Kết quả kiểm thử luồng Danh sách mua sắm (CK-07, CK-10, CK-12)

### 2.1. Phạm vi và cách kiểm tra (`tests/test_mua_sam.py`)
- **Mô hình:** `models/shopping.txt` gồm 6 tham số (`note`, `quantity`, `unit`, `food`, `label`, `checked`), tổng `3 × 3 × 2 × 2 × 2 × 2 = 144` tổ hợp.
- **Quy trình mỗi ca test:**
  1. Tạo một danh sách mua sắm riêng có tiền tố `PW-MS-` (`POST /api/households/shopping/lists`) để tránh Mealie gộp các mục trùng giữa các test.
  2. Thêm một mục vào danh sách (`POST /api/households/shopping/items`) với dữ liệu đã ánh xạ từ dòng case (dùng `nen["unit"]`, `nen["food"]`, `nen["label"]` từ fixture `nen`).
  3. Đọc lại danh sách (`GET /api/households/shopping/lists/{lid}`) để kiểm tra bất biến **I3** (`quantity`, `note`, `checked`, `unitId`, `foodId`, `labelId`).
  4. Đổi trạng thái `checked` (`PUT /api/households/shopping/items/{id}`) và đọc lại để xác nhận cập nhật được lưu.
  5. Trong khối `try ... finally`, luôn xóa mục (`DELETE /api/households/shopping/items`) và xóa danh sách (`DELETE /api/households/shopping/lists/{lid}`), sau đó kiểm tra đọc lại danh sách trả mã `404` (bất biến **I5**).
- **Bất biến áp dụng:** **I1** (không lỗi 500), **I2** (mã trạng thái đúng: tạo 201, đọc/sửa 200), **I3** (đọc lại khớp dữ liệu), **I5** (xóa xong không còn).

### 2.2. Số liệu thực thi thực tế trên Mealie v3.28.0

| Mức kiểm thử | File case | Số ca | Đạt (PASSED) | Không đạt (FAILED) | Thời gian | Bằng chứng |
| --- | --- | :---: | :---: | :---: | :---: | --- |
| **2-wise (Pairwise) — Lần 1** | `cases/shopping.o2.tsv` | 9 (`L01`..`L09`) | 9 | 0 | 3,41s | `docs/evidence/G-mua-sam-lan1.xml`, `.log` |
| **2-wise (Pairwise) — Lần 2** | `cases/shopping.o2.tsv` | 9 (`L01`..`L09`) | 9 | 0 | 2,97s | `docs/evidence/G-mua-sam-lan2.xml`, `.log` |
| **3-wise** | `cases/shopping.o3.tsv` | 23 (`L01`..`L23`) | 23 | 0 | 7,46s | `docs/evidence/G-mua-sam-3wise.xml`, `.log` |
| **Thử hết (Exhaustive)** | `cases/shopping.all.tsv` | 144 (`L001`..`L144`) | 144 | 0 | 40,36s | `docs/evidence/G-mua-sam-thu-het.xml`, `.log` |

### 2.3. Nhận xét
- Hai lần chạy 2-wise liên tiếp đều đạt **9/9**, không có sai lệch giữa các lần chạy.
- Mở rộng sang 3-wise (23 ca) và thử hết toàn bộ 144 tổ hợp đều đạt **100%**, không phát hiện thêm lỗi nào bị Pairwise bỏ sót trên miền giá trị hợp lệ của mô hình `models/shopping.txt`.
- Kết hợp với kết quả kiểm tra độc lập bằng `scripts/kiem_tra_cap.py` (độ phủ cặp đạt **100,0%** với 81/81 cặp hợp lệ), bộ Pairwise gồm **9 ca** đã đại diện đầy đủ tương tác cặp của luồng danh sách mua sắm trong khi giảm **93,75%** số lượng ca so với thử hết (144 ca).

---

## 3. Tái lập kết quả và ghim phiên bản — Mục H (CK-17)

### 3.1. Thông tin phiên bản đã ghim (`docs/evidence/H-phien-ban.txt`)
- **Mealie:** tag `v3.28.0`, mã nguồn commit `0552eaa4a80031b8572849cca0ed95d07f1be001`
- **Digest Docker image thực tế:** `ghcr.io/mealie-recipes/mealie@sha256:8b02290f4d1806f02acac6f25f6d48a3c965612fda1f8e914d5af533276f8688`
- **Docker:** `Docker version 29.9.3, build 5457199`
- **Python:** `Python 3.13.2`
- **Thư viện Python (`pip freeze`):** `pytest==9.1.1`, `requests==2.34.2` (cùng các gói phụ thuộc ghi đầy đủ trong `docs/evidence/H-phien-ban.txt`)
- **Commit repo nhóm khi chạy kiểm chứng sạch:** `b018adb9113a56ee517b5a19bd16e19eabf40c9f` (tag `v1.0-cuoi-ky` sẽ được gắn sau khi các PR cuối kỳ của nhóm được gộp vào `main`).

### 3.2. Kết quả chạy sạch 2 lần liên tiếp (`scripts/may_sach.bat`)

Quy trình chạy lại trên môi trường sạch (xóa container và volume cũ, dựng mới Mealie, cài đặt `.venv` từ `requirements.txt`, chạy bộ `pytest` mặc định gồm 46 test: 16 kế hoạch bữa ăn + 9 mua sắm + 19 tìm kiếm + 2 kiểm tra thứ tự tên):

| Lần chạy | Lệnh | Tổng số test | PASSED | FAILED | XFAIL | Thời gian | File kết quả |
| --- | --- | :---: | :---: | :---: | :---: | :---: | --- |
| **Lần 1** | `pytest -v --junitxml=docs\evidence\H-may-sach-lan1.xml` | 46 | 44 | 0 | 2 (`DEF-01`) | 5,44s | `docs/evidence/H-may-sach-lan1.xml` |
| **Lần 2** | `pytest -v --junitxml=docs\evidence\H-may-sach-lan2.xml` | 46 | 44 | 0 | 2 (`DEF-01`) | 4,72s | `docs/evidence/H-may-sach-lan2.xml` |

Cả hai lần chạy cho kết quả giống nhau hoàn toàn (**44 passed, 0 failed, 2 xfailed**), chứng minh bộ kiểm thử chạy lại được ổn định trên môi trường Docker đã ghim phiên bản.
