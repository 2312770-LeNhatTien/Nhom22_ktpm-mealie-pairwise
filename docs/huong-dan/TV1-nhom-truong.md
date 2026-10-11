# TV1 Nhóm trưởng: Lê Nhật Tiến

Việc của nhóm trưởng gồm ba nhóm: giữ cho bốn bạn còn lại không bị kẹt, viết phần mở đầu của mục A, và ghép sản phẩm của cả nhóm thành báo cáo và slide.

## 1. Theo dõi tiến độ

### Tạo bảng công việc (làm một lần)

Danh sách thẻ nằm trong `scripts/cong-viec.json`. Script `scripts/tao_bang_cong_viec.py` đọc file đó và tạo nhãn, mốc **Giữa kỳ** (hạn 18/10) cùng toàn bộ thẻ trên GitHub. Mỗi thẻ được gắn nhãn tên người làm, ví dụ `TV2 Quý`, và ghi họ tên ở dòng đầu.

1. Cài GitHub CLI và đăng nhập. Khi được hỏi, chọn **GitHub.com**, **HTTPS**, **Login with a web browser**:

```bat
winget install --id GitHub.cli
gh auth login
```

   Cài xong phải đóng Command Prompt và mở lại thì lệnh `gh` mới chạy.

2. Ở thư mục gốc của repo:

```bat
python scripts\tao_bang_cong_viec.py --thu
python scripts\tao_bang_cong_viec.py
```

   Lệnh đầu chỉ in ra những gì sẽ tạo. Lệnh sau tạo thật. Chạy lại bao nhiêu lần cũng không tạo trùng.

3. Tạo bảng kéo thả ở tab Projects:

```bat
gh auth refresh -s project
python scripts\tao_bang_cong_viec.py --bang
```

   Script tạo bảng **Nhóm 22 - Giữa kỳ**, đưa các thẻ vào và xếp cột: thẻ đã xong vào **Done**, thẻ đang có Pull Request vào **In Progress**, còn lại vào **Todo**. Nếu bảng hiện dạng danh sách thì bấm mũi tên cạnh tên View, chọn **Layout → Board**. Nếu bước này báo lỗi, script in ra cách tạo bảng bằng tay.

4. Mở bảng, bấm dấu ba chấm ở góc trên bên phải, chọn **Settings**:
   - **Manage access**: thêm 4 bạn với quyền **Write** để các bạn kéo được thẻ.
   - Kéo xuống **Danger zone**, đổi **Visibility** thành **Public** để thầy mở xem được bảng.

5. Thử một lần: đóng một thẻ đã xong, xem thẻ có tự nhảy sang cột **Done** không. Nếu không, bấm dấu ba chấm → **Workflows**, bật **Item closed** và **Pull request merged**.

Thêm một việc mới sau này: tạo thẻ trực tiếp ở tab **Issues → New issue**, gắn nhãn tên người làm và mốc **Giữa kỳ**.

Sau khi tạo xong, nhắn nhóm một câu kèm link tab Issues, vì GitHub không tự gửi thông báo cho từng bạn.

### Hằng ngày

- Mỗi tối xem bảng công việc. Thẻ nào nằm ở cột **In Progress** quá hai ngày thì hỏi riêng bạn đó đang vướng gì.
- Hạn chung của các phần là 18/10, nhưng báo cáo và slide phải nộp ngày 19/10. Nếu mọi phần đều về đúng tối 18/10 thì chỉ còn một ngày để ghép. Nhắc các bạn mở Pull Request ngay khi xong từng thẻ, và ghép dần vào báo cáo mỗi khi có một phần được gộp.
- Mỗi Pull Request cần ít nhất một người khác bấm **Approve** rồi mới gộp. Pull Request nằm quá một ngày chưa ai xem thì nhắc người đọc chéo.
- Ghi biên bản mỗi buổi họp vào `docs/meetings/`, mỗi buổi một file: ai có mặt, quyết định gì, ai làm gì tiếp.

Cách xem và gộp một Pull Request:

1. Mở tab **Pull requests**, bấm vào Pull Request cần xem.
2. Mở tab **Files changed** để đọc nội dung thay đổi.
3. Muốn góp ý vào một dòng: rê chuột vào dòng đó, bấm dấu **+**, gõ góp ý.
4. Bấm **Review changes**, chọn **Approve** nếu ổn hoặc **Request changes** nếu cần sửa.
5. Khi đã ổn, quay lại tab **Conversation**, bấm **Merge pull request**.

## 2. Viết phần mở đầu của mục A

Sản phẩm: ba đề mục đầu trong `docs/muc-a.md` và một sơ đồ use case.

### Bước 1. Dùng thử Mealie khoảng 30 phút

Lần lượt làm từng việc dưới đây và ghi lại: ai làm được việc này, cần quyền gì.

| Thử việc gì | Ở đâu |
| --- | --- |
| Tạo một công thức bằng tay, thêm nguyên liệu và các bước | `/g/home/r/create/new` |
| Tạo category, tag rồi gắn vào công thức | `/group/data/categories`, `/group/data/tags` |
| Tìm và lọc công thức | `/g/home/recipes/finder` |
| Lập kế hoạch bữa ăn cho một ngày | `/household/mealplan/planner/view` |
| Tạo danh sách mua sắm | `/shopping-lists` |
| Xem và đổi cài đặt household | `/household` |
| Tạo thêm một user, cấp và bỏ quyền | `/admin/manage/users/create`, `/household/members` |
| Đăng xuất, mở thử một công thức khi chưa đăng nhập | trang công thức bất kỳ |

### Bước 2. Viết ba đề mục

**A.1 Mục tiêu hệ thống** (khoảng 5–7 câu). Trả lời: Mealie là gì, giải quyết việc gì, cho ai, chạy ở đâu. Thông tin nền từ README của Mealie: đây là trình quản lý công thức nấu ăn tự cài trên máy mình, có lập kế hoạch bữa ăn và danh sách mua sắm, backend cung cấp REST API, giao diện viết bằng Vue. Các tính năng chính: nhập công thức từ URL hoặc nhập tay, kế hoạch bữa ăn, danh sách mua sắm, sổ công thức (cookbook).

Giải thích thêm hai khái niệm riêng của Mealie vì cả ba luồng kiểm thử đều dùng tới:

- **Group:** một nhóm lớn dùng chung dữ liệu công thức.
- **Household:** hộ gia đình nằm trong group. Mỗi user thuộc một household. Cài đặt của household quyết định mặc định cho công thức mới.

**A.2 Actor.** Lập bảng:

| Actor | Làm được gì |
| --- | --- |
| Khách (chưa đăng nhập) | Xem công thức công khai của household công khai |
| Người dùng thường | Tạo, sửa, tìm công thức; lập kế hoạch bữa ăn; danh sách mua sắm |
| Người dùng có quyền riêng | Tùy quyền: quản lý category và tag, quản lý household, quản lý thành viên, mời người mới |
| Admin | Mọi việc ở trên, cộng với quản lý user, group, household và cài đặt hệ thống |
| Ứng dụng bên thứ ba | Gọi REST API thay cho người dùng. Script test của nhóm thuộc loại này |

Điền lại bảng theo những gì bạn thấy khi dùng thử, đừng chép nguyên.

**A.3 Use case.** Vẽ một sơ đồ use case bằng draw.io:

1. Mở https://app.diagrams.net, chọn lưu file về máy.
2. Ở khung bên trái, mở nhóm hình **UML**. Kéo hình người (Actor) ra cho từng actor, kéo hình bầu dục (Use Case) cho từng use case.
3. Vẽ 6–8 use case, ví dụ: Đăng nhập, Tạo công thức, Tìm kiếm và lọc công thức, Lập kế hoạch bữa ăn, Quản lý danh sách mua sắm, Cấu hình household, Quản lý quyền thành viên, Quản lý user.
4. Tô màu khác cho 3 use case nhóm kiểm thử: **Tìm kiếm và lọc công thức**, **Cấu hình household**, **Quản lý quyền thành viên**.
5. Nối actor với use case bằng đường thẳng.
6. **File → Save** thành `docs/so-do/use-case.drawio`, rồi **File → Export as → PNG** thành `docs/so-do/use-case.png`.

Dưới hình viết 2–3 câu: ba use case tô màu là phạm vi kiểm thử của nhóm, và vì sao chọn chúng (đều có nhiều tham số độc lập kết hợp với nhau).

## 3. Dựng khung báo cáo và ghép bản nộp

Tạo `docs/bao-cao/Nhom22_BaoCaoGiuaKy.docx` với cấu trúc:

| Phần | Nội dung | Lấy từ |
| --- | --- | --- |
| Trang bìa | Tên môn, tên đề tài, tổ hợp R02 Mealie + K06 Pairwise, giảng viên, 5 thành viên kèm MSSV | README |
| Bảng phân công | Ai phụ trách mục nào | README |
| A | Mục tiêu, actor, use case, module, dependency, luồng dữ liệu | `docs/muc-a.md` |
| B | Sơ đồ kiến trúc, giải thích 5 module | `docs/muc-b.md` |
| C | Môi trường, lệnh chạy, dữ liệu mẫu, bằng chứng | `docs/muc-c.md` |
| D | Nguyên lý Pairwise, phạm vi, giả định, rủi ro, tiêu chí pass/fail | `docs/muc-d.md` |
| E, F, G | Ghi ngắn những gì đã có: 3 model PICT, file case, script mẫu chạy 16 case household. Phần còn lại làm ở giai đoạn sau | `models/`, `cases/`, `tests/` |
| H | Tag và SHA đã chốt, link repo, cách chạy lại | README |
| Phụ lục | Ảnh bảng công việc, ảnh lịch sử commit | GitHub |

Khi ghép:

- Chép chữ từ file Markdown sang Word, định dạng lại đề mục cho thống nhất một kiểu.
- Hình chèn từ file PNG trong `docs/so-do/` và `docs/evidence/`. Mỗi hình có số và tên: "Hình 1. Sơ đồ kiến trúc".
- Đọc lại từ đầu đến cuối một lượt để giọng văn và cách gọi tên thống nhất, ví dụ chỗ nào cũng gọi là "luồng cấu hình household".
- Xuất PDF, mở lại bản PDF kiểm tra hình và bảng không bị vỡ trang.

## 4. Làm slide

Thời lượng ước khoảng 10 phút, chưa có con số chính thức. Dàn ý 9 slide:

| Slide | Nội dung | Người nói | Thời gian |
| --- | --- | --- | --- |
| 1 | Tên đề tài, thành viên, phiên bản đã chốt (tag, SHA) | Nhật Tiến | 0:30 |
| 2 | Mealie là gì, actor, use case | Nhật Tiến | 1:00 |
| 3 | Sơ đồ kiến trúc và 5 module liên quan | Quốc Tiến | 1:30 |
| 4 | Luồng dữ liệu của 3 nghiệp vụ | Tuấn | 1:00 |
| 5 | Môi trường, cách cài; demo trực tiếp luồng household | Quý | 2:00 |
| 6 | Pairwise là gì, ví dụ 18 tổ hợp còn 9 | Toàn | 1:00 |
| 7 | Phạm vi 3 luồng, số case exhaustive và pairwise, tiêu chí pass/fail | Toàn | 1:30 |
| 8 | Script mẫu đã chạy được gì | Tuấn | 0:45 |
| 9 | Kế hoạch đến cuối kỳ, bảng công việc, lịch sử commit | Nhật Tiến | 0:45 |

Nguyên tắc: mỗi slide một ý, chữ ít, hình to. Số liệu nên đưa lên slide 7: household 1.792 tổ hợp còn 16 case, tìm kiếm 5.832 còn 19, phân quyền 192 còn 14.

Nếu thầy cho ít thời gian hơn thì bỏ slide 4 và slide 8 trước. Nếu được nhiều hơn thì Quý demo trực tiếp thêm hai luồng còn lại.

Ảnh cho slide 9:

- Bảng công việc: mở tab **Projects**, chụp màn hình bảng. Chụp thêm tab **Issues → Milestones → Giữa kỳ** để thấy tỷ lệ thẻ đã đóng.
- Lịch sử commit: mở tab **Insights → Contributors**, chụp biểu đồ đóng góp của từng người.

## 5. Kiểm tra tài liệu cài đặt của Quý

Khi Quý mở Pull Request cho mục C:

1. Chạy `docker compose down -v` để xóa sạch Mealie trên máy mình.
2. Mở `docs/muc-c.md` trên nhánh của Quý, làm theo đúng từng dòng, không hỏi miệng.
3. Chỗ nào phải đoán hoặc phải hỏi mới làm được thì chỗ đó tài liệu còn thiếu. Ghi góp ý vào đúng dòng đó trong Pull Request.

Đây là cách thử đúng tiêu chí của thầy: hướng dẫn cài đặt đủ rõ để giảng viên dựng lại được.

## 6. Nộp bài và đánh dấu bản giữa kỳ

Danh sách kiểm tra trước khi nộp:

- [ ] Mealie v3.28.0 chạy được trên máy demo và một máy dự phòng
- [ ] Có video demo dự phòng
- [ ] Mục A đủ 6 đề mục, mục B có sơ đồ và 5 module, mục C đã được người khác làm theo thành công, mục D có tiêu chí pass/fail
- [ ] Ba file model trong `models/`, file case trong `cases/`
- [ ] Script mẫu chạy được 16 case household, có ảnh kết quả
- [ ] README, báo cáo và slide đều ghi tag `v3.28.0` và SHA
- [ ] Cả 5 thành viên đều có commit trên repo
- [ ] Bảng công việc đúng với thực tế
- [ ] Đã tập có bấm giờ, cả bài vừa trong 10 phút

Nộp báo cáo và slide theo cách thầy yêu cầu, chụp màn hình xác nhận đã nộp. Sau đó gắn tag để sau này chỉ ra được chính xác bản đã nộp:

```bat
git checkout main
git pull
git tag midterm
git push origin midterm
```
