# tests

Code test tự động của nhóm, viết bằng Python với `pytest` (chạy test) và `requests` (gọi API của Mealie). Thư mục này chưa có file test nào.

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

Mealie phải đang chạy (`docker compose up -d`). Rồi:

```bat
pytest tests -v
```

Khi chưa có file test nào, pytest báo `no tests ran`, như vậy là cài đặt đã đúng.

## Code test phải làm gì

1. Đọc file `.tsv` trong `cases/`: dòng đầu là tên tham số, mỗi dòng sau là một test case, các cột cách nhau bằng dấu tab.
2. Đăng nhập Mealie một lần qua `POST /api/auth/token`, giữ lại `access_token`.
3. Với mỗi dòng: gọi các API của luồng tương ứng.
4. So kết quả thực tế với kết quả mong đợi bằng `assert`.

Mỗi dòng trong file case thành một test riêng nhờ `@pytest.mark.parametrize`, nên pytest tự in PASS hoặc FAIL cho từng case. Tên file test bắt đầu bằng `test_`, ví dụ `test_household.py`.
