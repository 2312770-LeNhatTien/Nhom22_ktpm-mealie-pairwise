# So sánh Pairwise, 3-wise và thử hết

Nhóm kiểm thử Mealie v3.28.0 bằng các bộ ca sinh từ Microsoft PICT. Script
`scripts/kiem_tra_cap.py --all` xác nhận bốn bộ Pairwise phủ 100% cặp hợp lệ.
Bảng dùng kết quả đã đối chiếu với XML pytest. Cột thời gian là thời gian toàn
lượt chạy pytest, tính bằng giây. Các luồng được chạy trong những môi trường
khác nhau, nên so thời gian giữa các mức trong cùng một luồng.

| Luồng | Mức | Số ca thiết kế | Đạt | Không đạt | Lỗi mới có phiếu | Thời gian (giây) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Tìm kiếm | Pairwise | 19 | 19 | 0 | 0 | 1,715 / 1,099 |
| Tìm kiếm | 3-wise | 67 | 67 | 0 | 0 | 2,621 |
| Tìm kiếm | Thử hết | 5.832 | 5.832 | 0 | 0 | 130,172 |
| Công thức | Pairwise | 14 | 14 | 0 | 0 | 4,806 / 4,801 |
| Công thức | 3-wise | 50 | 50 | 0 | 0 | 15,435 / 18,718 |
| Công thức | Thử hết | 2.916 | 2.916 | 0 | 0 | 863,668 / 813,330 |
| Kế hoạch bữa ăn | Pairwise | 16 | 16 | 0 | 0 | 1,711 / 1,448 |
| Kế hoạch bữa ăn | 3-wise | 48 | 48 | 0 | 0 | 3,686 / 3,872 |
| Kế hoạch bữa ăn | Thử hết | 96 | 96 | 0 | 0 | 6,806 / 8,811 |
| Danh sách mua sắm | Pairwise | 9 | 9 | 0 | 0 | 2,014 / 2,037 |
| Danh sách mua sắm | 3-wise | 23 | 23 | 0 | 0 | 4,703 / 4,600 |
| Danh sách mua sắm | Thử hết | 144 | 144 | 0 | 0 | 26,854 / 32,489 |

## Nhận xét

- **Tìm kiếm.** Mức 3-wise và thử hết đều đạt, giống 19 ca Pairwise. Pairwise
  giảm 99,67% số ca so với 5.832 tổ hợp hợp lệ. Hai ca kiểm thử hồi quy
  sắp tên ngoài bộ PICT được đánh dấu XFAIL cho cùng một lỗi
  [DEF-01](loi/DEF-01.md). Chúng không tính vào 19 ca Pairwise trong bảng.
- **Công thức.** Cả ba mức đều đạt qua hai lượt. Thử thêm 3-wise và thử hết không phát hiện lỗi mới trong phạm vi model. Pairwise giảm 99,52% số ca so với 2.916 tổ hợp.
- **Kế hoạch bữa ăn.** Cả ba mức đều đạt trong hai lượt đối chiếu. Pairwise
  chạy 16 ca thay vì 96, giảm 83,33% số ca.
- **Danh sách mua sắm.** Pairwise chạy 9 ca thay vì 144, giảm 93,75% số
  ca. Cả ba mức đều đạt qua hai lượt. 3-wise và thử hết không phát hiện thêm lỗi trong phạm vi model.

Số lỗi mới trong bảng chỉ tính lỗi có phiếu được ghi nhận từ bộ ca tương ứng.
Kết quả áp dụng cho các giá trị và ràng buộc trong bốn model đã thiết kế.

## Nguồn số liệu

- Tìm kiếm lấy từ các XML `G-tim-kiem-*.xml` trong [docs/evidence](evidence/).
  Thời gian Pairwise gồm cả hai ca hồi quy chạy trong cùng lượt.
- Công thức lấy từ các XML `G-cong-thuc-*.xml`. Xem phương pháp chạy và từng
  lượt trong [báo cáo công thức](bao-cao/BaoCao_KetQua_CongThuc.md).
- Kế hoạch bữa ăn chạy lại bộ pytest đã gộp ở PR #57 trên Mealie v3.28.0.
  Bằng chứng nằm trong các XML `G-so-sanh-ke-hoach-*.xml`.
- Danh sách mua sắm chạy hai lượt cho từng mức trên Mealie v3.28.0 với
  dữ liệu mẫu. Bằng chứng nằm trong các XML `G-so-sanh-mua-sam-*.xml`.
  Đây là lượt chạy riêng để đối chiếu CK-16. GitHub Actions mặc định
  thu thập test trong `tests/`, còn script đối chiếu nằm trong `scripts/`.
  Sau khi dựng Mealie và nạp seed theo README, chạy các lệnh sau để đối chiếu.

  ```text
  python -m pytest -q scripts/doi_chieu_mua_sam.py
  python -m pytest -q scripts/doi_chieu_mua_sam.py -m o3
  python -m pytest -q scripts/doi_chieu_mua_sam.py -m het
  ```
