# tests

Bộ test tự động của nhóm, viết bằng Python với `pytest` (chạy test) và `requests` (gọi API của Mealie). Mỗi dòng trong `cases/*.tsv` là một test.

| File | Làm gì |
| --- | --- |
| `../pytest.ini` | Mặc định chỉ chạy bộ 2-wise. 3-wise và thử hết phải chạy tay bằng `-m o3` và `-m het` |
| `chung.py` | Đăng nhập một lần, hàm `Api` để gọi API, hàm `doc_case` đọc file case |
| `conftest.py` | Fixture `api` và `nen` (dữ liệu nền dùng chung), tự đánh dấu xfail cho lỗi đã báo |
| `loi_da_bao.py` | Bảng lỗi đã báo (mã DEF), test nào có tên trong bảng sẽ là xfail |
| `test_tim_kiem.py` | Luồng tìm kiếm và lọc: `GET /api/recipes`, 3 mức 2-wise, 3-wise, thử hết |

Các luồng khác (công thức, kế hoạch bữa ăn, mua sắm, test âm) làm theo đúng cấu trúc của `test_tim_kiem.py` trong file riêng của từng người.

## Cài đặt (làm một lần trên mỗi máy)

Cài Python 3.10 trở lên, lúc cài nhớ tích **Add python.exe to PATH**. Mở Command Prompt ở thư mục gốc của repo:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Mỗi lần mở Command Prompt mới phải chạy lại lệnh `activate`.

## Chuẩn bị Mealie

```bat
docker compose up -d --wait
python scripts\chuan_bi_muc_c.py seed
```

Chờ khoảng một phút cho Mealie chạy xong. Lệnh `seed` nạp 12 công thức mẫu, 3 category, 3 tag (chạy lại không tạo trùng). Muốn Mealie sạch hoàn toàn thì chạy `scripts\dung_lai.bat`.

## Biến môi trường

Đặt trong cùng cửa sổ Command Prompt sẽ chạy test:

```bat
set MEALIE_URL=http://localhost:9925
set MEALIE_USER=changeme@example.com
set MEALIE_PASS=MyPassword
set MEALIE_EMAIL=changeme@example.com
set MEALIE_PASSWORD=MyPassword
```

- `MEALIE_URL`, `MEALIE_USER`, `MEALIE_PASS` dùng cho test. Không đặt thì lấy đúng ba giá trị trên.
- `MEALIE_EMAIL`, `MEALIE_PASSWORD` dùng cho script nạp dữ liệu mẫu.
- Mealie mới dựng mặc định có tài khoản `changeme@example.com` / `MyPassword`; test, seed và CI đều dùng tài khoản này nếu không đặt biến.
- Máy nào đã chạy trình thiết lập trên giao diện và dùng tài khoản riêng (ví dụ `nhom22@example.com` / `Nhom22@Mealie`) thì đặt cả bốn biến `MEALIE_USER`, `MEALIE_PASS`, `MEALIE_EMAIL`, `MEALIE_PASSWORD` theo tài khoản đó; hoặc chạy `scripts\dung_lai.bat` để quay về mặc định.
- Tên cũ `MEALIE_BASE_URL` và `MEALIE_PASSWORD` vẫn dùng được thay cho `MEALIE_URL` và `MEALIE_PASS`.

## Lệnh chạy

| Lệnh | Tác dụng |
| --- | --- |
| `pytest` | Bộ mặc định: 2-wise (tìm kiếm 19 test) và 2 test thứ tự tên (đang xfail) |
| `pytest -m o3` | Bộ 3-wise (tìm kiếm 67 test) |
| `pytest -m het` | Thử hết mọi tổ hợp (tìm kiếm 5.832 test, cần có `cases/search.all.tsv`, chạy khoảng 1 đến 2 phút) |
| `pytest -k tim_kiem` | Chỉ các test có chữ `tim_kiem` |
| `pytest -k "tim_kiem_2wise and S07"` | Đúng một test |
| `pytest -x` | Dừng ở test đỏ đầu tiên |
| `pytest -v --junitxml=docs/evidence/G-tim-kiem-lan1.xml` | Chạy và lưu file kết quả |
| `pytest --collect-only -q` | Chỉ liệt kê test, không chạy |

Chưa có file `cases/search.all.tsv` thì `pytest -m het` báo 1 test bị bỏ qua (skipped), không báo lỗi.

## Đọc kết quả

| Chữ | Nghĩa |
| --- | --- |
| `PASSED` | Đạt |
| `FAILED` | Đỏ. Chưa chắc Mealie sai, làm theo 4 bước ở mục 5.4 của file phân công |
| `XFAIL` | Đỏ nhưng là lỗi đã báo (có mã DEF trong `loi_da_bao.py`) |
| `XPASS` | Lỗi đã báo mà lần này lại đạt, phải xem lại (Mealie đã sửa hay lỗi chỉ xảy ra ngẫu nhiên) |
| `SKIPPED` | Bị bỏ qua vì thiếu file case |

Dòng cuối của pytest ghi số test đạt, đỏ và thời gian chạy. Hai con số này đưa vào báo cáo. Mỗi lần chạy chính thức hãy chạy hai lần liên tiếp, hai lần phải cho cùng kết quả.

## Test tìm kiếm kiểm tra gì

Mỗi test gửi `GET /api/recipes` với một tổ hợp tham số trong `cases/search.*.tsv`, rồi kiểm tra:

- Mã trạng thái phải là 200 (không lỗi 500).
- Thông tin phân trang đúng: `page`, `per_page`, `total`, `total_pages`, và số công thức ở trang 1 (I3).
- Công thức nào trả về cũng phải đúng bộ lọc category và tag, đúng với `requireAllCategories` và `requireAllTags` (I6).
- Từ khóa không có trong dữ liệu thì không có kết quả (I6).
- Duyệt hết mọi trang: không công thức nào xuất hiện hai lần, và gộp lại phải đúng bằng tập công thức tự lọc từ danh sách đầy đủ (I7). Từ khóa `ch` khớp theo tên, không phân biệt dấu.
- `orderBy` = `created_at` thì đúng thứ tự thời gian tạo trên mọi trang, tăng hoặc giảm theo `orderDirection`.
- `orderBy` = `name` thì đúng thứ tự mã Unicode trên mọi trang.
- `orderBy` = `random` thì gọi hai lần cùng `paginationSeed` phải ra cùng thứ tự.
- Riêng hai test `test_sap_xep_ten_theo_bang_chu_cai[asc]` và `[desc]`: sắp xếp theo tên phải theo bảng chữ cái (bỏ dấu). Mealie sắp theo mã Unicode nên "Cà phê sữa" đứng sau "Chè đậu"; hai test này đang để xfail, chờ nhóm xác nhận và cấp mã DEF.

Thông báo lỗi ghi rõ bất biến bị vi phạm (I1, I2, I3, I6, I7), có thể đưa thẳng vào phiếu lỗi.

## Ghi lỗi đã báo (xfail)

Khi có phiếu lỗi `DEF-xx`, thêm một dòng vào `tests/loi_da_bao.py`. Tên test lấy đúng như pytest in ra, kể cả phần trong ngoặc vuông:

```python
LOI_DA_BAO = {
    "test_tim_kiem_2wise[S12]": "DEF-01: perPage=1 kết hợp orderBy=random trả 500",
}
```

Hai test sắp xếp tên hiện được đánh dấu XFAIL tạm thời với mã `DEF-chua-cap-ma`. Đây là phát hiện chờ nhóm xác nhận, chưa phải lỗi đã được cấp mã DEF.

Chỉ Tuấn sửa `chung.py`, `conftest.py`, `pytest.ini`, `loi_da_bao.py`. Cần thêm gì thì nhắn Tuấn.

## CI (GitHub Actions)

File `.github/workflows/test.yml`: mỗi lần đẩy lên `main` hoặc mở Pull Request, GitHub tự dựng Mealie bằng Docker, nạp dữ liệu mẫu, chạy bộ mặc định và lưu `ket-qua.xml` ở mục Artifacts. 3-wise và thử hết không chạy trên CI.

## Lỗi thường gặp

| Hiện tượng | Nguyên nhân | Cách xử lý |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'requests'` | Chưa bật `.venv` hoặc chưa cài thư viện | `.venv\Scripts\activate` rồi `pip install -r requirements.txt` |
| `ConnectionError` hoặc `Connection refused` | Mealie chưa chạy | `docker compose up -d`, chờ một phút |
| `Dang nhap that bai: 401` | Sai tài khoản, hoặc Mealie vừa dựng lại nên chỉ có tài khoản mặc định | Đặt đúng `MEALIE_USER` và `MEALIE_PASS` (xem mục Biến môi trường) |
| `KeyError: 'Món chính'` ở fixture `nen` | Chưa nạp dữ liệu mẫu | `python scripts\chuan_bi_muc_c.py seed` |
| `collected 0 items` | Đứng sai thư mục | Chạy ở thư mục gốc của repo |
| `UnicodeDecodeError` khi đọc file case | File case bị ghi bằng bảng mã khác, thường do sinh bằng PowerShell | Sinh lại bằng `scripts\sinh_case.bat` trong Command Prompt |
