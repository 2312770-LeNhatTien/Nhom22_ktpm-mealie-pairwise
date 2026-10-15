# tests

Code test tự động của nhóm, viết bằng Python với `pytest` (chạy test) và `requests` (gọi API của Mealie).

| File | Làm gì |
| --- | --- |
| `conftest.py` | Phần dùng chung: địa chỉ Mealie, đăng nhập, đọc file case, tạo tên không trùng |
| `test_household.py` | Luồng cấu hình household: mỗi dòng của `cases/household.tsv` là một test (16 case) |

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

Kết quả mong đợi là 16 dòng `PASSED` và dòng cuối `16 passed`:

```text
tests/test_household.py::test_cong_thuc_moi_nhan_mac_dinh_cua_household[case01] PASSED
...
tests/test_household.py::test_cong_thuc_moi_nhan_mac_dinh_cua_household[case16] PASSED
============================== 16 passed ==============================
```

| Lệnh | Tác dụng |
| --- | --- |
| `pytest tests -v` | Chạy tất cả, mỗi case một dòng |
| `pytest tests -v -k case03` | Chỉ chạy case có tên chứa `case03` |
| `pytest tests -x` | Dừng ngay ở case hỏng đầu tiên |
| `pytest tests -v > ket-qua.txt` | Ghi kết quả ra file |

### Đổi cổng hoặc tài khoản

Máy nào Mealie chạy cổng khác thì đặt biến môi trường trước khi chạy, không sửa code:

```bat
set MEALIE_BASE_URL=http://localhost:9926
pytest tests -v
```

Hai biến còn lại là `MEALIE_USER` và `MEALIE_PASSWORD` (mặc định là tài khoản dùng chung của nhóm).

## Test này làm gì với Mealie

Mỗi test đi qua ba bước:

1. `PUT /api/households/preferences` lưu cấu hình theo đúng dòng case, rồi kiểm tra Mealie trả về đúng 9 giá trị.
2. `POST /api/recipes` tạo một công thức mới.
3. `GET /api/recipes/{slug}` đọc lại công thức, so 5 cài đặt (`public`, `showNutrition`, `showAssets`, `landscapeView`, `disableComments`) với 5 tùy chọn `recipe...` vừa lưu.

Công thức tạo ra được xóa ngay sau mỗi case. Cấu hình household được lưu lại trước khi chạy và trả về như cũ khi chạy xong, nên chạy trên máy sắp demo vẫn an toàn.

## Lỗi thường gặp

| Hiện tượng | Nguyên nhân | Cách xử lý |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'requests'` | Chưa bật `.venv` hoặc chưa cài thư viện | `.venv\Scripts\activate` rồi `pip install -r requirements.txt` |
| `ConnectionError` hoặc `Connection refused` | Mealie chưa chạy | `docker compose up -d`, chờ một phút |
| `Đăng nhập thất bại: 401` | Chưa thiết lập lần đầu, hoặc mật khẩu khác bảng dùng chung | Làm lại phần thiết lập lần đầu trong README gốc |
| `FileNotFoundError: ... household.tsv` | Thiếu file case | `git pull`; kiểm tra thư mục `cases/` |
| `collected 0 items` | Tên file không bắt đầu bằng `test_`, hoặc đứng sai thư mục | Đổi tên file; đứng ở thư mục gốc của repo |
| `UnicodeDecodeError` khi đọc file case | File case bị ghi bằng bảng mã khác, thường do sinh bằng PowerShell | Sinh lại bằng `scripts\sinh_case.bat` trong Command Prompt |

## Viết thêm test cho luồng khác

Hai luồng còn lại viết theo đúng khuôn của `test_household.py`: `test_search.py` đọc `cases/search.tsv`, `test_permissions.py` đọc `cases/permissions.tsv`. Phải đổi các nhãn trong file case (`none`, `one`, `two`, `match`) thành giá trị thật dựa trên dữ liệu mẫu. Cách gọi API của hai luồng này nằm trong `docs/api-3-luong.md`.
