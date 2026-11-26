# docs

Nơi để báo cáo, hướng dẫn, sơ đồ và bằng chứng.

| Đường dẫn | Nội dung |
| --- | --- |
| `bao-cao/` | Báo cáo giữa kỳ (`Nhom22_BaoCaoGiuaKy.docx` và `.pdf`) và slide |
| `TestCase_GiuaKy.xlsx` | 76 test case (58 Pairwise và 18 dữ liệu sai), mỗi luồng một sheet |
| `so-do/` | Sơ đồ use case, kiến trúc, luồng dữ liệu của 4 luồng và quy trình test (`.png`, `.svg`) |
| `muc-c.md` | Môi trường, cách chạy, bằng chứng hệ thống chạy |
| `seed-data.md` | Dữ liệu mẫu dùng cho test |
| `evidence/` | Ảnh chụp và file kết quả chứng minh hệ thống chạy được |
| `huong-dan/` | Cài công cụ và quy trình làm việc nhóm, bắt đầu từ `00-bat-dau.md` |
| `meetings/` | Biên bản họp nhóm, mỗi buổi một file |

Quy ước đặt tên ảnh trong `evidence/`: chữ cái của mục, số thứ tự, mô tả ngắn. Ví dụ `C-01-docker-version.png`, `C-11-search-loc-category.png`.

Phần môi trường có [hướng dẫn môi trường và kết quả kiểm tra](muc-c.md), [bảng dữ liệu mẫu](seed-data.md) và [danh sách bằng chứng](evidence/README.md). Nạp dữ liệu bằng `python scripts/chuan_bi_muc_c.py seed` từ thư mục gốc repo.
## Báo cáo kiểm thử cuối kỳ

[Báo cáo kết quả kiểm thử chức năng tìm kiếm](bao-cao/BaoCao_TongKet_KiemThuTimKiem.docx) ghi lại kết quả 2-wise, 3-wise, vét cạn, môi trường Docker và các giới hạn của bộ dữ liệu mẫu.
