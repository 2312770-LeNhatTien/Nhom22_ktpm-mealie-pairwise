# Nhom22_ktpm-mealie-pairwise

Đề tài môn Kiểm thử phần mềm của Nhóm 22: kiểm thử hệ thống **Mealie** (R02) bằng kỹ thuật **Combinatorial / Pairwise** (K06) với công cụ Microsoft PICT.

## Thành viên

| MSSV | Họ tên | Vai trò | Phụ trách trong báo cáo |
| --- | --- | --- | --- |
| 2312770 | Lê Nhật Tiến | Nhóm trưởng, quản lý dự án | Mục A (mục tiêu, actor, use case), mục H, tổng hợp báo cáo, slide |
| 2312731 | Nguyễn Phú Quý | Môi trường và demo | Mục C |
| 2312769 | Hồ Quốc Tiến | Phân tích hệ thống | Mục A (module, dependency), mục B |
| 2312776 | Bùi Ngọc Toàn | Kỹ thuật Pairwise | Mục D, mục E |
| 2312792 | Nguyễn Đình Tuấn | API và tự động hóa | Mục A (luồng dữ liệu), mục F |

## Bảng công việc và hướng dẫn

Việc của từng người nằm ở tab **Issues** (lọc theo nhãn tên mình) và bảng kéo thả ở tab **Projects**. Mỗi thẻ ghi việc cần làm, file phải nộp, điều kiện để coi là xong và hạn. Ai xong thẻ nào thì mở Pull Request cho thẻ đó luôn, không cần chờ người khác.

Hướng dẫn làm từng việc nằm trong `docs/huong-dan/`:

| Đọc | Dành cho |
| --- | --- |
| [00-bat-dau.md](docs/huong-dan/00-bat-dau.md) | Cả nhóm: cài công cụ, chạy Mealie, quy trình nhánh, commit, Pull Request |
| [TV1-nhom-truong.md](docs/huong-dan/TV1-nhom-truong.md) | Lê Nhật Tiến |
| [TV2-moi-truong-demo.md](docs/huong-dan/TV2-moi-truong-demo.md) | Nguyễn Phú Quý |
| [TV3-phan-tich-he-thong.md](docs/huong-dan/TV3-phan-tich-he-thong.md) | Hồ Quốc Tiến |
| [TV4-pairwise.md](docs/huong-dan/TV4-pairwise.md) | Bùi Ngọc Toàn |
| [TV5-api-tu-dong-hoa.md](docs/huong-dan/TV5-api-tu-dong-hoa.md) | Nguyễn Đình Tuấn |
| [api-da-kiem-chung.md](docs/huong-dan/api-da-kiem-chung.md) | Ai cần biết API của 3 luồng nhận gì, trả gì |

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

Lần đầu đăng nhập bằng tài khoản có sẵn của Mealie là `changeme@example.com` / `MyPassword`. Mealie sẽ mở trình thiết lập. Làm hết các bước chứ không bỏ qua, vì chừng nào admin còn dùng email có sẵn thì mỗi lần đăng nhập Mealie lại đẩy về trang này. Cả nhóm điền cùng một bộ giá trị để code test chạy được trên mọi máy:

| Bước | Điền |
| --- | --- |
| Account Details | Username `nhom22`, Full Name `Nhom 22`, Email `nhom22@example.com`, Password `Nhom22@Mealie` |
| Site Settings | Tắt Enable Advanced Content, tắt Enable Public Access, bật Use Seed Data |
| AI Providers | Bỏ qua |
| Summary | Kiểm tra lại rồi bấm hoàn tất |

Từ đó về sau đăng nhập bằng `nhom22@example.com` / `Nhom22@Mealie`. Trang liệt kê API nằm ở http://localhost:9925/docs.

Nếu chạy `docker compose down -v` thì dữ liệu bị xóa hết và phải thiết lập lại từ đầu.

| Lệnh | Tác dụng |
| --- | --- |
| `docker compose up -d` | Tải image (lần đầu) và chạy Mealie ở chế độ nền |
| `docker compose ps` | Xem container có đang chạy không |
| `docker compose logs -f mealie` | Xem log, bấm Ctrl+C để thoát |
| `docker compose stop` / `docker compose start` | Tạm dừng / chạy lại, giữ nguyên dữ liệu |
| `docker compose down -v` | Xóa container và toàn bộ dữ liệu, quay về trạng thái mới cài |

## Phạm vi kiểm thử

Nhóm kiểm thử 3 luồng qua API của Mealie, không bấm giao diện.

| Luồng | Model | Số tham số | Exhaustive | Pairwise |
| --- | --- | --- | --- | --- |
| Cấu hình household | `models/household.txt` | 9 | 1.792 | 16 |
| Tìm kiếm và lọc công thức | `models/search.txt` | 9, có 1 ràng buộc | 5.832 | 19 |
| Phân quyền người dùng | `models/permissions.txt` | 6 | 192 | 14 |

`models/demo.txt` là ví dụ 3 tham số để làm quen với PICT (18 tổ hợp, pairwise còn 9).

## Cấu trúc thư mục

```text
README.md            phiên bản đã chốt, cách chạy, ai làm gì
docker-compose.yml   file chạy Mealie
requirements.txt     thư viện Python cho code test
docs/                các mục báo cáo (muc-a.md ... muc-d.md)
docs/huong-dan/      hướng dẫn làm việc cho từng thành viên
docs/so-do/          sơ đồ (.drawio và .png)
docs/bao-cao/        bản báo cáo và slide nộp
docs/evidence/       ảnh chụp và video bằng chứng
docs/meetings/       biên bản họp nhóm
docs/seed-data.md    dữ liệu mẫu dùng cho test
models/              file model PICT (.txt)
cases/               file test case do PICT sinh ra (.tsv)
tests/               code test tự động
scripts/             script sinh case, tạo bảng công việc
```

## Sinh lại test case

Tải `pict.exe` từ https://github.com/microsoft/pict/releases và thêm vào PATH. Mở **Command Prompt** (không dùng PowerShell cho lệnh có dấu `>`) ở thư mục gốc của repo:

```bat
scripts\sinh_case.bat
```

Hoặc chạy tay cho từng model:

```bat
pict models\household.txt > cases\household.tsv
pict models\household.txt /s
```

Lệnh thứ hai in thống kê số cặp giá trị cần phủ và số test sinh ra. Số case có thể lệch 1–2 so với file trong `cases/` tùy phiên bản PICT, vì có nhiều bộ test cùng phủ đủ mọi cặp.

## Chạy test

Code test viết bằng Python với `pytest` và `requests`. Cách cài đặt và lệnh chạy nằm trong `tests/README.md`.

## Quy ước làm việc

- Mỗi người làm trên nhánh riêng tên `tvX/ten-viec`, ví dụ `tv4/model-household`, rồi gộp vào `main` qua Pull Request có ít nhất một người khác xem.
- Lời nhắn commit bắt đầu bằng mục báo cáo trong ngoặc vuông, ví dụ `[D] Thêm tiêu chí pass/fail`.
- Phần của ai người đó tự commit bằng tài khoản của mình.
- Không đưa mật khẩu thật lên repo. Tài khoản trong README là tài khoản dùng chung của nhóm cho bản Mealie chạy trên máy cá nhân.
- Mỗi Pull Request ghi `Closes #số-thẻ` trong phần mô tả để thẻ tự đóng khi gộp.
