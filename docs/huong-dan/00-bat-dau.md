# Bắt đầu: việc ai cũng phải làm

Đọc file này trước, rồi mới đọc hướng dẫn riêng của mình:

| Vai | Người | Hướng dẫn |
| --- | --- | --- |
| TV1 Nhóm trưởng | Lê Nhật Tiến | [TV1-nhom-truong.md](TV1-nhom-truong.md) |
| TV2 Môi trường và demo | Nguyễn Phú Quý | [TV2-moi-truong-demo.md](TV2-moi-truong-demo.md) |
| TV3 Phân tích hệ thống | Hồ Quốc Tiến | [TV3-phan-tich-he-thong.md](TV3-phan-tich-he-thong.md) |
| TV4 Kỹ thuật Pairwise | Bùi Ngọc Toàn | [TV4-pairwise.md](TV4-pairwise.md) |
| TV5 API và tự động hóa | Nguyễn Đình Tuấn | [TV5-api-tu-dong-hoa.md](TV5-api-tu-dong-hoa.md) |

Việc của từng người và hạn nằm trên bảng công việc (tab **Issues** và **Projects** của repo). Mỗi thẻ ghi rõ phải làm gì, nộp file nào, thế nào là xong. Không có thứ tự bắt buộc giữa các thành viên: ai xong thẻ nào thì mở Pull Request cho thẻ đó luôn, không cần chờ người khác.

Xem riêng việc của mình: mở tab **Issues**, bấm **Label**, chọn nhãn có tên mình, ví dụ `TV2 Quý`.

## 1. Cài công cụ

| Công cụ | Ai cần | Tải ở đâu | Kiểm tra |
| --- | --- | --- | --- |
| Git for Windows | Cả nhóm | https://git-scm.com/download/win | `git --version` |
| Docker Desktop | Cả nhóm | https://www.docker.com/products/docker-desktop/ | `docker --version` |
| Python 3.10 trở lên | Ai viết hoặc chạy test | https://www.python.org/downloads/ | `python --version` |
| PICT (`pict.exe`) | Toàn, và ai muốn tự sinh case | https://github.com/microsoft/pict/releases | `pict` |
| draw.io | Ai vẽ sơ đồ | https://app.diagrams.net (chạy trên trình duyệt) | không cần cài |

Lưu ý khi cài:

- Git: bấm **Next** đến hết, giữ nguyên mặc định.
- Docker Desktop: nếu trình cài đặt hỏi về WSL 2 thì đồng ý, khởi động lại máy khi được yêu cầu. Mở Docker Desktop và chờ nó báo engine đang chạy rồi mới gõ lệnh.
- Python: ở màn hình đầu của bộ cài nhớ tích **Add python.exe to PATH**.

Khai báo tên và email cho Git, làm một lần. Email phải là email đã đăng ký với GitHub, nếu không commit sẽ không được tính cho tài khoản của bạn:

```bat
git config --global user.name "Ho va ten"
git config --global user.email "email-da-dang-ky-github"
```

Kiểm tra sau lần push đầu tiên: mở tab **Commits** của nhánh mình trên GitHub. Tên đứng cạnh commit bấm vào được và dẫn tới trang cá nhân của bạn là đúng. Nếu tên chỉ là chữ thường không bấm được thì email trong Git chưa khớp với tài khoản, commit đó không được tính cho bạn trong biểu đồ đóng góp. Cách sửa nhanh nhất: vào GitHub **Settings → Emails**, thêm đúng email đang dùng trong Git và bấm xác nhận trong thư GitHub gửi về. Các commit cũ tự được tính lại, không phải commit lại.

## 2. Lấy repo về máy

1. Mở email mời vào repo và bấm chấp nhận. Chưa chấp nhận thì không đẩy code lên được.
2. Mở Command Prompt, chọn chỗ để chứa, ví dụ ổ D:

```bat
D:
git clone https://github.com/2312770-LeNhatTien/Nhom22_ktpm-mealie-pairwise.git
cd Nhom22_ktpm-mealie-pairwise
```

## 3. Chạy Mealie

Trong thư mục repo:

```bat
docker compose up -d
```

Lần đầu Docker tải image nên mất vài phút. Chờ khoảng một phút sau khi lệnh chạy xong rồi mở http://localhost:9925.

### Thiết lập lần đầu

Đăng nhập bằng tài khoản có sẵn `changeme@example.com` / `MyPassword`. Mealie mở trình thiết lập. Làm hết các bước, điền đúng bảng dưới đây để cả nhóm dùng chung một tài khoản:

| Bước | Điền |
| --- | --- |
| Account Details | Username `nhom22`, Full Name `Nhom 22`, Email `nhom22@example.com`, Password `Nhom22@Mealie` |
| Site Settings | Giữ nguyên mặc định |
| AI Providers | Bỏ qua |
| Summary | Kiểm tra lại rồi bấm hoàn tất |

Kiểm tra: đăng xuất, đăng nhập lại bằng `nhom22@example.com` / `Nhom22@Mealie`. Vào thẳng trang chính, không bị đẩy về trang thiết lập là đúng.

### Các lệnh Docker hay dùng

| Lệnh | Tác dụng |
| --- | --- |
| `docker compose up -d` | Chạy Mealie ở chế độ nền |
| `docker compose ps` | Xem container có đang chạy không |
| `docker compose logs -f mealie` | Xem log, bấm Ctrl+C để thoát |
| `docker compose stop` / `docker compose start` | Tạm dừng / chạy lại, giữ nguyên dữ liệu |
| `docker compose down -v` | Xóa container và toàn bộ dữ liệu. Chạy xong phải thiết lập lần đầu lại |

## 4. Các màn hình hay dùng trong Mealie

Đường dẫn dưới đây lấy từ mã nguồn giao diện của bản v3.28.0. Gõ thẳng vào thanh địa chỉ sau khi đăng nhập.

| Việc | Đường dẫn |
| --- | --- |
| Trang chủ, danh sách công thức | `http://localhost:9925/g/home` |
| Tạo công thức mới | `http://localhost:9925/g/home/r/create/new` |
| Tìm và lọc công thức | `http://localhost:9925/g/home/recipes/finder` |
| Quản lý category | `http://localhost:9925/group/data/categories` |
| Quản lý tag | `http://localhost:9925/group/data/tags` |
| Cài đặt household | `http://localhost:9925/household` |
| Thành viên và quyền trong household | `http://localhost:9925/household/members` |
| Admin: danh sách user | `http://localhost:9925/admin/manage/users` |
| Admin: tạo user | `http://localhost:9925/admin/manage/users/create` |
| Kế hoạch bữa ăn | `http://localhost:9925/household/mealplan/planner/view` |
| Danh sách mua sắm | `http://localhost:9925/shopping-lists` |
| Trang liệt kê API | `http://localhost:9925/docs` |

## 5. Quy trình làm một việc

Mỗi việc trên bảng công việc đi qua đúng các bước này.

**Bước 1. Nhận thẻ.** Mở thẻ của mình trên tab Issues, đọc phần "Việc cần làm" và "Xong khi". Trên bảng Projects, kéo thẻ từ cột **Todo** sang cột **In Progress**. Làm xong ý nào thì tích vào ô của ý đó ngay trên thẻ.

**Bước 2. Tạo nhánh.** Luôn bắt đầu từ `main` mới nhất:

```bat
git checkout main
git pull
git checkout -b tv2/muc-c
```

Tên nhánh theo mẫu `tvX/ten-viec`, không dấu, không khoảng trắng.

**Bước 3. Làm và commit.** Xong một ý là commit, không dồn cả việc vào một lần:

```bat
git status
git add .
git commit -m "[C] Thêm bảng lệnh Docker và phần lỗi thường gặp"
```

`git status` cho xem những file sắp được commit. Lời nhắn bắt đầu bằng mục báo cáo trong ngoặc vuông.

**Bước 4. Đẩy lên và mở Pull Request.**

```bat
git push -u origin tv2/muc-c
```

Mở trang repo trên GitHub, bấm nút **Compare & pull request** vừa hiện ra. Trong phần mô tả gõ `Closes #12` (thay 12 bằng số thẻ của mình) để khi gộp xong thẻ tự đóng. Ở cột bên phải, mục **Reviewers**, chọn một bạn và nhắn bạn đó vào xem.

Một Pull Request có thể đóng nhiều thẻ: gõ mỗi thẻ một dòng, `Closes #12` rồi `Closes #13`. Thẻ nào không có file để commit (ví dụ thẻ tập thuyết trình) thì khi xong bấm **Close issue** ở cuối thẻ.

**Bước 5. Sửa theo góp ý.** Sửa trên máy, commit, `git push`. Pull Request tự cập nhật, không cần mở cái mới.

**Bước 6. Gộp.** Khi có một người bấm **Approve**, bấm **Merge pull request**. Thẻ tự đóng và tự chuyển sang cột **Done**.

### Khi `main` đã thay đổi trong lúc mình đang làm

```bat
git checkout main
git pull
git checkout tv2/muc-c
git merge main
```

Nếu Git báo xung đột (conflict) ở một file, mở file đó, tìm các dòng `<<<<<<<`, `=======`, `>>>>>>>`, giữ lại phần đúng, xóa ba dòng đánh dấu, rồi `git add .` và `git commit`. Không chắc thì hỏi trong nhóm trước khi sửa.

## 6. Viết báo cáo ở đâu

- Mỗi mục báo cáo là một file Markdown trong `docs/`: `muc-a.md`, `muc-b.md`, `muc-c.md`, `muc-d.md`. Nhóm trưởng ghép các file này vào bản Word cuối.
- Sơ đồ để trong `docs/so-do/`, lưu cả file nguồn `.drawio` và ảnh `.png`.
- Ảnh chụp màn hình để trong `docs/evidence/`, tên bắt đầu bằng chữ cái của mục: `C-01-docker.png`.
- Chèn ảnh vào Markdown: `![Mô tả ảnh](evidence/C-01-docker.png)`.

Mục A có ba người viết chung một file `docs/muc-a.md`. Để không giẫm lên nhau, mỗi người chỉ sửa đúng đề mục của mình:

| Đề mục trong `muc-a.md` | Người viết |
| --- | --- |
| A.1 Mục tiêu hệ thống, A.2 Actor, A.3 Use case | Nhật Tiến |
| A.4 Cây thư mục và module, A.5 Dependency | Quốc Tiến |
| A.6 Luồng dữ liệu của 3 nghiệp vụ | Tuấn |

## 7. Lỗi thường gặp

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
| --- | --- | --- |
| `docker compose up` báo không kết nối được Docker | Docker Desktop chưa mở hoặc chưa khởi động xong | Mở Docker Desktop, chờ báo engine đang chạy rồi gõ lại |
| Báo cổng 9925 đã được dùng | Chương trình khác đang chiếm cổng | Trong `docker-compose.yml` đổi `"9925:9000"` thành `"9926:9000"` trên máy mình, mở `localhost:9926`. Không commit thay đổi này |
| Mở `localhost:9925` không lên | Mealie chưa khởi động xong | Chờ thêm một phút; xem `docker compose logs -f mealie` |
| Đăng nhập xong bị đẩy về trang thiết lập | Chưa làm thiết lập lần đầu | Làm hết các bước ở mục 3 |
| Quên mật khẩu hoặc lỡ điền khác bảng | | `docker compose down -v`, rồi `docker compose up -d` và thiết lập lại |
| `git push` báo lỗi 403 hoặc permission denied | Chưa chấp nhận lời mời, hoặc Git đang đăng nhập tài khoản khác | Chấp nhận lời mời trong email; kiểm tra tài khoản GitHub đang đăng nhập |
| `git push` bị từ chối, báo "fetch first" | Trên GitHub có commit mới hơn | `git pull` rồi push lại |
| `python` không chạy được | Lúc cài chưa tích Add to PATH | Cài lại Python và tích ô đó |
| `.venv\Scripts\activate` báo lỗi trong PowerShell | PowerShell chặn script | Dùng Command Prompt thay cho PowerShell |

Kẹt quá một tiếng thì chụp nguyên màn hình lỗi gửi vào nhóm, đừng tự mò cả buổi.
