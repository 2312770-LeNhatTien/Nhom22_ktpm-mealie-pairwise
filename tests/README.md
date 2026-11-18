# tests

Code test tự động của nhóm, viết bằng Python với `pytest` (chạy test) và `requests` (gọi API của Mealie).

Ở giữa kỳ nhóm mới có bản chạy thử trong `scripts/` (`chay_thu_4_luong.py` và `chay_ca_am_tinh.py`, cách chạy xem README gốc). Bộ pytest của 4 luồng (mỗi dòng trong `cases/*.o2.tsv` là một test) làm ở cuối kỳ. Trong thư mục này hiện có:

| File | Làm gì |
| --- | --- |
| `conftest.py` | Phần dùng chung: địa chỉ Mealie, đăng nhập, đọc file case, tạo tên không trùng |

File test của luồng household (phạm vi cũ) nằm ở `docs/cu-3-luong/tests/test_household.py`.

## Cài đặt (làm một lần trên mỗi máy)

Cài Python 3.10 trở lên từ https://www.python.org/downloads/, lúc cài nhớ tích **Add python.exe to PATH**. Sau đó mở Command Prompt ở thư mục gốc của repo:

```bat
python --version
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Lệnh thứ hai tạo môi trường riêng cho repo, lệnh thứ ba bật nó lên (dấu nhắc lệnh có thêm chữ `(.venv)`). Mỗi lần mở Command Prompt mới phải chạy lại lệnh thứ ba.

## Chạy test

Mealie phải đang chạy (`docker compose up -d`) và đã làm xong phần thiết lập lần đầu trong README gốc, vì test đăng nhập bằng `nhom22@example.com`. Rồi:

```bat
pytest tests -v
```

Khi chưa có file `test_*.py` nào, pytest báo `no tests ran`, như vậy là cài đặt đã đúng.

### Đổi cổng hoặc tài khoản

Máy nào Mealie chạy cổng khác thì đặt biến môi trường trước khi chạy, không sửa code:

```bat
set MEALIE_BASE_URL=http://localhost:9926
pytest tests -v
```

Hai biến còn lại là `MEALIE_USER` và `MEALIE_PASSWORD` (mặc định là tài khoản dùng chung của nhóm).

## Code test phải làm gì

1. Đọc file `.tsv` trong `cases/`: dòng đầu là tên tham số, mỗi dòng sau là một test case, các cột cách nhau bằng dấu tab.
2. Đăng nhập Mealie một lần qua `POST /api/auth/token`, giữ lại `access_token`.
3. Với mỗi dòng: gọi các API của luồng tương ứng, rồi đọc lại dữ liệu.
4. So kết quả thực tế với kết quả mong đợi (các bất biến I1 đến I6 trong báo cáo giữa kỳ) bằng `assert`.

Tên file test bắt đầu bằng `test_`, ví dụ `test_search.py`. Mỗi dòng case thành một test riêng nhờ `@pytest.mark.parametrize`, nên pytest in PASS hoặc FAIL cho từng case.

## Lỗi thường gặp

| Hiện tượng | Nguyên nhân | Cách xử lý |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'requests'` | Chưa bật `.venv` hoặc chưa cài thư viện | `.venv\Scripts\activate` rồi `pip install -r requirements.txt` |
| `ConnectionError` hoặc `Connection refused` | Mealie chưa chạy | `docker compose up -d`, chờ một phút |
| `Đăng nhập thất bại: 401` | Chưa thiết lập lần đầu, hoặc mật khẩu khác bảng dùng chung | Làm lại phần thiết lập lần đầu trong README gốc |
| `collected 0 items` | Tên file không bắt đầu bằng `test_`, hoặc đứng sai thư mục | Đổi tên file; đứng ở thư mục gốc của repo |
| `UnicodeDecodeError` khi đọc file case | File case bị ghi bằng bảng mã khác, thường do sinh bằng PowerShell | Sinh lại bằng `scripts\sinh_case.bat` trong Command Prompt |
