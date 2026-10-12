# docs

Nơi để báo cáo, hướng dẫn, sơ đồ và bằng chứng.

| Đường dẫn | Nội dung | Người phụ trách |
| --- | --- | --- |
| `huong-dan/` | Hướng dẫn làm việc cho từng thành viên, bắt đầu từ `00-bat-dau.md` | Nhật Tiến |
| `muc-a.md` | Mục A: mục tiêu, actor, use case, module, dependency, luồng dữ liệu | Nhật Tiến, Quốc Tiến, Tuấn |
| `muc-b.md` | Mục B: sơ đồ kiến trúc, giải thích module | Quốc Tiến |
| `muc-c.md` | Mục C: môi trường, cách chạy, bằng chứng | Quý |
| `muc-d.md` | Mục D: kế hoạch áp dụng Pairwise | Toàn |
| `api-3-luong.md` | Request và response của 3 luồng | Tuấn |
| `seed-data.md` | Dữ liệu mẫu dùng cho test | Quý |
| `demo-kich-ban.md` | Kịch bản demo | Quý |
| `so-do/` | Sơ đồ, lưu cả file `.drawio` và `.png` | Nhật Tiến, Quốc Tiến, Tuấn |
| `evidence/` | Ảnh chụp và video chứng minh hệ thống chạy được | Quý |
| `bao-cao/` | Bản báo cáo và slide nộp | Nhật Tiến |
| `meetings/` | Biên bản họp nhóm, mỗi buổi một file | Nhật Tiến |

Quy ước đặt tên ảnh trong `evidence/`: chữ cái của mục báo cáo, số thứ tự, mô tả ngắn. Ví dụ `C-01-docker-version.png`, `C-11-search-loc-category.png`.

Phần C hiện có [hướng dẫn môi trường và kết quả xác minh](muc-c.md), [bảng dữ liệu mẫu](seed-data.md) và [mô tả nguồn bằng chứng](evidence/README.md). Có thể nạp seed/chạy kiểm tra ba luồng bằng `python scripts/chuan_bi_muc_c.py seed` và `python scripts/chuan_bi_muc_c.py verify` từ thư mục gốc repo. Các phần onboarding còn cần bổ sung được ghi rõ trong mục C.
