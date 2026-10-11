# tests

Code test tự động của nhóm. Thư mục này chưa có code: nhóm chốt ngôn ngữ viết test (C# hoặc Python) rồi mới tạo project.

Dù viết bằng ngôn ngữ nào, code test làm cùng một việc:

1. Đọc file `.tsv` trong `cases/`: dòng đầu là tên tham số, mỗi dòng sau là một test case, các cột cách nhau bằng dấu tab.
2. Đăng nhập Mealie một lần qua `POST /api/auth/token`, giữ lại `access_token`.
3. Với mỗi dòng: gọi các API của luồng tương ứng.
4. So kết quả thực tế với kết quả mong đợi.
5. In mỗi case một dòng PASS hoặc FAIL kèm lý do, và ghi cùng nội dung vào file log.

Yêu cầu chung: chạy lại được bằng một lệnh, và lệnh đó được ghi vào file này.
