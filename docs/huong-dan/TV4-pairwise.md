# TV4 Kỹ thuật Pairwise: Bùi Ngọc Toàn

Sản phẩm của bạn là `docs/muc-d.md` và phần model, file case. Bạn là người trả lời các câu hỏi lý thuyết của thầy, nên phải tự tay chạy PICT chứ không chỉ đọc.

## Việc 1. Cài PICT và chạy ví dụ đầu tiên

1. Vào https://github.com/microsoft/pict/releases, tải `pict.exe` của bản mới nhất.
2. Đặt vào một thư mục, ví dụ `C:\tools\pict\`.
3. Thêm thư mục đó vào PATH: mở menu Start, gõ "environment variables", chọn **Edit the system environment variables → Environment Variables**, chọn dòng **Path** ở khung trên, bấm **Edit → New**, dán `C:\tools\pict`, bấm OK. Mở lại Command Prompt.
4. Gõ `pict`. Hiện ra phần hướng dẫn "Usage: pict model [options]" là đạt.

Dùng **Command Prompt**, không dùng PowerShell, cho các lệnh có dấu `>`. PowerShell bản cũ ghi file bằng bảng mã UTF-16, code test đọc vào sẽ lỗi ký tự.

Chạy ví dụ 3 tham số, ở thư mục gốc của repo:

```bat
pict models\demo.txt
pict models\demo.txt /s
```

Lệnh đầu in ra 9 test case. Lệnh thứ hai in thống kê: 21 cặp giá trị cần phủ, 9 test sinh ra. Tự kiểm tra bằng tay rằng cả 21 cặp đều có mặt trong 9 dòng. Làm được việc này là đã hiểu pairwise.

Cách đếm 21 cặp: `orderBy` có 3 giá trị, `orderDirection` có 2, `perPage` có 3. Số cặp là 3×2 + 3×3 + 2×3 = 21.

## Việc 2. Tự sinh lại file case và rà 3 model

```bat
scripts\sinh_case.bat
git status
```

Script sinh lại 4 file trong `cases/`. `git status` cho biết file nào khác với bản đang có trong repo. Số case có thể lệch 1–2 tùy phiên bản PICT, điều đó bình thường vì có nhiều bộ test cùng phủ đủ mọi cặp. Nếu lệch thì giữ bản do bạn sinh, và sửa số trong README cho khớp.

Rà từng model với mã nguồn Mealie `v3.28.0`:

| Model | Đối chiếu với | Cần kiểm tra |
| --- | --- | --- |
| `models/household.txt` | `mealie/schema/household/household_preferences.py` | Đủ 9 trường, đúng tên |
| `models/search.txt` | `mealie/schema/response/pagination.py` và hàm `get_all` trong `mealie/routes/recipe/recipe_crud_routes.py` | Tên tham số, và luật `orderBy=random` bắt buộc có `paginationSeed` |
| `models/permissions.txt` | `mealie/schema/user/user.py` | Đủ 5 cờ quyền |

Tên trong model viết kiểu `recipePublic`, trong code Python viết kiểu `recipe_public`. Hai cách viết là một: Mealie tự đổi sang kiểu chữ hoa giữa từ khi nhận và trả JSON.

Cú pháp model cần nắm để giải thích được:

```text
orderBy:        none, name, created_at, rating, random
paginationSeed: none, abc123

IF [orderBy] = "random" THEN [paginationSeed] = "abc123";
```

- Mỗi dòng là một tham số, sau dấu hai chấm là các giá trị.
- Dòng `IF ... THEN ...;` là ràng buộc: loại bỏ những tổ hợp vô nghĩa. Ở đây, sắp xếp ngẫu nhiên mà không có seed thì Mealie từ chối request, nên không đưa vào bộ test hợp lệ.
- Các giá trị như `none`, `one`, `two`, `match` là nhãn đại diện. Code test sẽ đổi chúng thành giá trị thật dựa trên dữ liệu mẫu.

## Việc 3. Bảng so sánh pairwise, 3-wise và exhaustive

Tùy chọn `/o:N` đặt bậc phủ: `/o:2` là pairwise (mặc định), `/o:3` là phủ mọi bộ ba, `/o:` bằng số tham số là thử hết.

```bat
pict models\household.txt /o:3 > cases\household_3wise.tsv
pict models\household.txt /o:9 > cases\household_exhaustive.tsv
pict models\search.txt /o:3
pict models\search.txt /o:9
pict models\permissions.txt /o:3
pict models\permissions.txt /o:6
```

Số liệu tham khảo, chạy bằng PICT build từ mã nguồn. Bạn chạy lại và ghi số của mình:

| Luồng | Số tham số | Số cặp cần phủ | Pairwise | 3-wise | Exhaustive |
| --- | --- | --- | --- | --- | --- |
| Cấu hình household | 9 | 224 | 16 | 53 | 1.792 |
| Tìm kiếm và lọc | 9, có 1 ràng buộc | 273 | 19 | 67 | 5.832 |
| Phân quyền | 6 | 100 | 14 | 41 | 192 |

Đếm số case trong một file: số dòng trừ đi 1 (dòng đầu là tên tham số). Trong Command Prompt:

```bat
find /c /v "" cases\household.tsv
```

Dưới bảng viết 3–4 câu nhận xét: pairwise giảm bao nhiêu phần trăm so với thử hết, 3-wise tốn thêm bao nhiêu case, và vì sao nhóm chọn chạy thêm exhaustive cho luồng household để đối chứng.

## Việc 4. Viết mục D

Mục D có 5 phần, mỗi phần khoảng nửa trang.

| Phần | Viết gì | Gợi ý |
| --- | --- | --- |
| D.1 Nguyên lý | Pairwise là gì, vì sao giảm được số case | Dùng ví dụ 18 tổ hợp còn 9 của `models/demo.txt`. Dẫn tài liệu gốc |
| D.2 Lý do chọn phạm vi | Vì sao 3 luồng này | Đều là nơi nhiều tham số độc lập gặp nhau; thử hết thì quá nhiều; kết quả mong đợi xác định được từ code |
| D.3 Giả định | Những điều nhóm coi là đúng | Lỗi chủ yếu do tương tác tối đa 2 tham số; mỗi giá trị được chọn đại diện cho cả một lớp tương đương; môi trường cố định là v3.28.0, SQLite, dữ liệu mẫu trong `docs/seed-data.md` |
| D.4 Rủi ro và giới hạn | Kỹ thuật này có thể bỏ sót gì | Lỗi cần 3 tham số trở lên; chọn sai giá trị đại diện; xác định sai kết quả mong đợi. Cách giảm: chạy thêm 3-wise và exhaustive cho luồng household |
| D.5 Tiêu chí pass/fail | Khi nào một case đạt, khi nào cả đợt test đạt | Xem bên dưới |

Tiêu chí pass/fail đề xuất:

- **Một case đạt** khi status code đúng như mong đợi và dữ liệu trả về thỏa mọi điều kiện đã ghi trước cho case đó.
- **Độ phủ đạt** khi 100% cặp giá trị hợp lệ của mỗi model được phủ, lấy số liệu từ `pict ... /s`.
- **Đợt test đạt** khi mọi case đều chạy được tự động, mọi case fail đều đã được phân loại là lỗi của Mealie, lỗi của test hay lỗi dữ liệu, và có phân tích nguyên nhân.
- **Đối chứng:** với luồng household, so kết quả 16 case pairwise với 1.792 case exhaustive. Nếu exhaustive tìm ra lỗi mà pairwise bỏ sót thì ghi nhận đó là giới hạn của kỹ thuật.

Tài liệu để dẫn:

- `doc/pict.md` trong repo PICT: cú pháp model, ràng buộc, test âm với dấu `~`, tùy chọn `/o`.
- Bài "Pairwise Testing in Real World" nằm trong thư mục `doc/` của repo PICT.
- Mọi con số phần trăm về tỷ lệ lỗi bắt được phải kèm tên bài báo và năm. Không tìm lại được nguồn thì bỏ con số đó đi.

## Việc 5. Kết quả mong đợi của từng luồng

Phần này dùng cho mục E và cho việc viết test sau giữa kỳ. Chi tiết từng API nằm ở [api-da-kiem-chung.md](api-da-kiem-chung.md).

| Luồng | Kết quả mong đợi |
| --- | --- |
| Cấu hình household | Lưu cấu hình trả về đúng 9 giá trị đã gửi. Công thức tạo sau đó có 5 cài đặt khớp với 5 tùy chọn `recipe...` của household |
| Tìm kiếm và lọc | Status 200; số công thức không vượt `perPage`; mọi công thức trả về thỏa bộ lọc; đúng thứ tự sắp xếp; cùng seed thì cùng thứ tự |
| Phân quyền | Hành động thành công khi user có cờ tương ứng hoặc là admin, ngược lại trả về 403 |

Ba điều cần biết khi viết kết quả mong đợi cho luồng tìm kiếm, quan sát được khi gọi thử Mealie `v3.28.0`:

- Tìm kiếm theo từ khóa là tìm gần đúng, không phân biệt dấu. Tìm `bò` ra cả "Phở bò" lẫn "Sinh tố bơ". Vì vậy nên kiểm tra "công thức mong đợi có trong kết quả", không so bằng tuyệt đối.
- Sắp xếp theo tên không theo thứ tự từ điển tiếng Việt. "Chè đậu" đứng trước "Cà phê sữa".
- Lọc theo một category không tồn tại thì Mealie trả về tất cả công thức chứ không trả về rỗng.

Hai điều sau là hành vi đáng đưa vào danh sách "hành vi bất thường" của mục G, sau khi test của nhóm tái hiện được.

## Câu hỏi nên chuẩn bị sẵn

- Pairwise khác exhaustive chỗ nào?
- Pairwise bỏ sót loại lỗi gì? Nhóm làm gì để bù?
- Vì sao chọn các giá trị này cho mỗi tham số?
- Làm sao nhóm biết kết quả mong đợi của từng case?
- Ràng buộc trong model tìm kiếm lấy từ đâu?
