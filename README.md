# Nhom22_ktpm-mealie-pairwise

Đề tài môn Kiểm thử phần mềm của Nhóm 22: kiểm thử hệ thống **Mealie** (R02) bằng kỹ thuật **Combinatorial / Pairwise** (K06) với công cụ Microsoft PICT.

## Thành viên

| MSSV | Họ tên | Vai trò | Phụ trách trong báo cáo giữa kỳ |
| --- | --- | --- | --- |
| 2312770 | Lê Nhật Tiến | Nhóm trưởng, quản lý dự án | Kế hoạch kiểm thử (mục 1.1–1.5, 3.3.1–3.3.3, 3.3.8–3.3.10, 3.4), ghép báo cáo, slide |
| 2312731 | Nguyễn Phú Quý | Môi trường và demo | Môi trường, bằng chứng chạy (mục 4.2) |
| 2312769 | Hồ Quốc Tiến | Phân tích hệ thống | Sơ đồ use case, kiến trúc, module (mục 3.2) |
| 2312776 | Bùi Ngọc Toàn | Kỹ thuật Pairwise | Model PICT, test case, dữ liệu test (mục 2.1, 2.2, 3.3.6, 3.3.7) |
| 2312792 | Nguyễn Đình Tuấn | API và tự động hóa | Luồng dữ liệu, bất biến, script chạy thử (mục 3.2.4, 3.3.5, 3.4.3) |

## Phiên bản hệ thống được kiểm thử

| Hạng mục | Giá trị |
| --- | --- |
| Repo | https://github.com/mealie-recipes/mealie |
| Tag | `v3.28.0` |
| Commit SHA | `0552eaa4a80031b8572849cca0ed95d07f1be001` |
| Docker image | `ghcr.io/mealie-recipes/mealie:v3.28.0` |
| Cơ sở dữ liệu | SQLite (mặc định của Mealie) |

Nhóm chỉ làm việc trên đúng phiên bản này. Mã nguồn Mealie không nằm trong repo; ai cần đọc code thì clone riêng:

```bat
git clone --branch v3.28.0 --depth 1 https://github.com/mealie-recipes/mealie.git
cd mealie
git rev-parse HEAD
```

Lệnh cuối phải in ra đúng SHA ở bảng trên.

## Chạy Mealie

Cần cài Docker Desktop trước. Sau đó mở terminal ở thư mục gốc của repo:

```bat
docker compose up -d
```

Chờ khoảng một phút rồi mở http://localhost:9925.

### Thiết lập lần đầu

Lần đầu đăng nhập bằng tài khoản có sẵn của Mealie là `changeme@example.com` / `MyPassword`. Mealie sẽ mở trình thiết lập. Làm hết các bước chứ không bỏ qua, vì chừng nào admin còn dùng email có sẵn thì mỗi lần đăng nhập Mealie lại đẩy về trang này. Cả nhóm điền cùng một bộ giá trị để script test chạy được trên mọi máy:

| Bước | Điền |
| --- | --- |
| Account Details | Username `nhom22`, Full Name `Nhom 22`, Email `nhom22@example.com`, Password `Nhom22@Mealie` |
| Site Settings | Tắt Enable Advanced Content, tắt Enable Public Access, bật Use Seed Data |
| AI Providers | Bỏ qua |
| Summary | Kiểm tra lại rồi bấm hoàn tất |

Từ đó về sau đăng nhập bằng `nhom22@example.com` / `Nhom22@Mealie`. Trang liệt kê API nằm ở http://localhost:9925/docs.

Nếu chạy `docker compose down -v` thì dữ liệu bị xóa hết và phải thiết lập lại từ đầu.

### Dựng lại Mealie sạch bằng một lệnh

Bật Docker Desktop, rồi ở thư mục gốc của repo chạy:

```bat
scripts\dung_lai.bat
```

Script xóa dữ liệu, dựng lại Mealie, nạp 12 công thức mẫu rồi mở một cửa sổ đã đặt sẵn biến môi trường để chạy `pytest` (mất khoảng 40 giây). **Cẩn thận:** script chạy `docker compose down -v` nên mất luôn tài khoản `nhom22` đã thiết lập. Sau khi dựng lại chỉ còn tài khoản mặc định `changeme@example.com` / `MyPassword`, và script dùng đúng tài khoản này.

| Lệnh | Tác dụng |
| --- | --- |
| `docker compose up -d` | Tải image (lần đầu) và chạy Mealie ở chế độ nền |
| `docker compose ps` | Xem container có đang chạy không |
| `docker compose logs -f mealie` | Xem log, bấm Ctrl+C để thoát |
| `docker compose stop` / `docker compose start` | Tạm dừng / chạy lại, giữ nguyên dữ liệu |
| `docker compose down -v` | Xóa container và toàn bộ dữ liệu, quay về trạng thái mới cài |

### Nạp dữ liệu mẫu

Sau khi thiết lập xong, nạp dữ liệu mẫu (3 category, 3 tag, 12 công thức; chạy lại không tạo trùng):

```bat
python scripts\chuan_bi_muc_c.py seed
```

Bảng dữ liệu mẫu nằm ở [docs/seed-data.md](docs/seed-data.md).

## Phạm vi kiểm thử

Nhóm kiểm thử 4 luồng qua API của Mealie, không bấm giao diện. Luồng tìm kiếm và lọc là trọng tâm.

| Luồng | Model | Số tham số | Thử hết | 3-wise | Pairwise |
| --- | --- | --- | --- | --- | --- |
| Tìm kiếm và lọc (trọng tâm) | `models/search.txt` | 9, có 1 ràng buộc | 5.832 | 67 | 19 |
| Quản lý công thức | `models/recipe.txt` | 8 | 2.916 | 50 | 14 |
| Kế hoạch bữa ăn | `models/mealplan.txt` | 4 | 96 | 48 | 16 |
| Danh sách mua sắm | `models/shopping.txt` | 6 | 144 | 23 | 9 |
| Tổng | 4 model | | 8.988 | 188 | 58 |

Ngoài 58 test Pairwise còn 18 test dữ liệu sai và giá trị biên, tổng cộng 76 test case. Chi tiết từng test case (dữ liệu vào, các bước, kết quả mong đợi) nằm trong [docs/TestCase_GiuaKy.xlsx](docs/TestCase_GiuaKy.xlsx).

## Cấu trúc thư mục

```text
README.md            phiên bản đã chốt, cách chạy, ai làm gì
docker-compose.yml   file chạy Mealie
requirements.txt     thư viện Python cho code test
models/              4 model PICT (recipe, search, mealplan, shopping)
cases/               test case do PICT sinh: *.o2.tsv (2-wise), *.o3.tsv (3-wise)
scripts/             sinh case, kiểm tra độ phủ cặp, chạy thử 4 luồng, nạp dữ liệu mẫu, dựng lại Mealie (dung_lai.bat)
tests/               bộ pytest (làm ở cuối kỳ)
docs/bao-cao/        báo cáo giữa kỳ (.docx, .pdf) và slide
docs/TestCase_GiuaKy.xlsx   76 test case, mỗi luồng một sheet
docs/so-do/          sơ đồ use case, kiến trúc, luồng dữ liệu, quy trình test
docs/evidence/       ảnh chụp bằng chứng hệ thống chạy
docs/huong-dan/      hướng dẫn cài công cụ và quy trình làm việc nhóm
docs/seed-data.md    dữ liệu mẫu dùng cho test
```

## Sinh lại test case

Repo kèm PICT 3.7.4 tại `tools\pict.exe`; `scripts\sinh_case.bat` tự thêm thư mục này vào PATH trong cửa sổ Command Prompt hiện tại. Nếu tải PICT riêng, lấy từ https://github.com/microsoft/pict/releases. Mở **Command Prompt** (không dùng PowerShell cho lệnh có dấu `>`) ở thư mục gốc repo:

```bat
scripts\sinh_case.bat
```

Hoặc chạy tay cho từng model (`/o:2` phủ mọi cặp, `/o:3` phủ mọi bộ ba, `/r:22` cố định hạt giống để ai chạy cũng ra đúng bộ case):

```bat
tools\pict.exe models\search.txt /o:2 /r:22 > cases\search.o2.tsv
tools\pict.exe models\search.txt /o:2 /r:22 /s
```

Lệnh thứ hai in thống kê số cặp giá trị cần phủ và số test sinh ra. Số case có thể lệch 1–2 so với file trong `cases/` tùy phiên bản PICT, vì có nhiều bộ test cùng phủ đủ mọi cặp.

Kiểm tra độc lập độ phủ cặp của cả 4 model (không tin hoàn toàn vào PICT):

```bat
python scripts\kiem_tra_cap.py --all
```

## Chạy thử 4 luồng

Cần Python 3.10 trở lên và `pip install -r requirements.txt`. Mealie phải đang chạy và đã nạp dữ liệu mẫu. Địa chỉ và tài khoản đặt bằng biến môi trường (có sẵn giá trị mặc định đúng với bảng thiết lập ở trên):

```bat
set MEALIE_URL=http://localhost:9925
set MEALIE_USER=nhom22@example.com
set MEALIE_PASS=Nhom22@Mealie
python scripts\chay_thu_4_luong.py
python scripts\chay_ca_am_tinh.py
```

`chay_thu_4_luong.py` chạy 58 test Pairwise của 4 luồng, `chay_ca_am_tinh.py` chạy 18 test dữ liệu sai và giá trị biên. Mỗi test tự tạo dữ liệu có tiền tố `PW-` và xóa sau khi chạy. Kết quả ghi ra file `ket_qua*.json` trong `scripts/` (file này không đưa lên Git).

Đây là bản chạy thử ở giữa kỳ. Ở cuối kỳ nhóm chuyển thành bộ pytest trong `tests/`, thêm CI trên GitHub Actions và chạy chính thức trên Docker image đã ghim.

## Quy ước làm việc

- Mỗi người làm trên nhánh riêng tên `tvX/ten-viec`, ví dụ `tv4/model-recipe`, rồi gộp vào `main` qua Pull Request có ít nhất một người khác xem.
- Lời nhắn commit bắt đầu bằng mục việc trong ngoặc vuông, ví dụ `[D] Thêm tiêu chí pass/fail`.
- Phần của ai người đó tự commit bằng tài khoản của mình.
- Không đưa mật khẩu thật lên repo. Tài khoản trong README là tài khoản dùng chung của nhóm cho bản Mealie chạy trên máy cá nhân.
- Mỗi Pull Request ghi `Closes #số-thẻ` trong phần mô tả để thẻ tự đóng khi gộp.
- Hướng dẫn cài công cụ, quy trình nhánh, commit và Pull Request: [docs/huong-dan/00-bat-dau.md](docs/huong-dan/00-bat-dau.md).
