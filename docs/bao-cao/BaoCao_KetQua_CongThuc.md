# Kết quả kiểm thử quản lý công thức

**Nhóm 22 · Bùi Ngọc Toàn (2312776) · CK-05, CK-11, CK-12, CK-18, CK-19**

Mỗi ca tạo một công thức có tên bắt đầu bằng `PW-`, cập nhật qua API, đọc
lại để đối chiếu và xóa công thức trong `finally`. Bộ kiểm thử kiểm tra lỗi
máy chủ (I1), mã HTTP (I2), nội dung đọc lại (I3) và việc đọc sau khi xóa
phải trả HTTP 404 (I5). Tám tham số trong model bao gồm mô tả, khẩu phần,
thời gian, nguyên liệu, hướng dẫn, danh mục, thẻ và chế độ công khai.

## Kết quả thực thi

Môi trường là Mealie v3.28.0 trên Docker Desktop, dữ liệu nền gồm 12 công
thức. Máy chạy Windows, Docker Engine 29.9.3, Python 3.12.14 và pytest 9.1.1.
Digest image là
`sha256:8b02290f4d1806f02acac6f25f6d48a3c965612fda1f8e914d5af533276f8688`.
Mỗi mức chạy hai lượt liên tiếp và thống kê riêng. Số ca kiểm thử được đối
chiếu với file TSV và thuộc tính `tests` trong JUnit XML.

| Mức | Số ca | Lượt 1 | Lượt 2 | XML |
| --- | ---: | --- | --- | --- |
| Pairwise | 14 | 14 đạt, 4,806 giây | 14 đạt, 4,801 giây | [Lượt 1](../evidence/G-cong-thuc-2wise-lan1.xml) · [Lượt 2](../evidence/G-cong-thuc-2wise-lan2.xml) |
| 3-wise | 50 | 50 đạt, 15,435 giây | 50 đạt, 18,718 giây | [Lượt 1](../evidence/G-cong-thuc-3wise-lan1.xml) · [Lượt 2](../evidence/G-cong-thuc-3wise-lan2.xml) |
| Thử hết | 2.916 | 2.916 đạt, 863,668 giây | 2.916 đạt, 813,330 giây | [Lượt 1](../evidence/G-cong-thuc-thu-het-lan1.xml) · [Lượt 2](../evidence/G-cong-thuc-thu-het-lan2.xml) |

Hai lượt cho cùng số ca đạt ở mỗi mức và không ghi nhận ca thất bại. Mức
3-wise và thử hết không phát hiện thêm lỗi trên các tổ hợp hợp lệ của model.

Bộ test âm của Quốc Tiến phát hiện hai lỗi nằm ngoài kết quả Pairwise ở trên:
tên công thức rỗng gây HTTP 500 và số khẩu phần âm vẫn được lưu.
[DEF-02](../loi/DEF-02.md) · [DEF-05](../loi/DEF-05.md)

## Lệnh chạy

```powershell
python -m pytest -q tests/test_cong_thuc.py
python -m pytest -q tests/test_cong_thuc.py -m o3
python -m pytest -q tests/test_cong_thuc.py -m het
```

Đặt `MEALIE_URL` theo địa chỉ máy kiểm thử và nạp dữ liệu mẫu theo README
trước khi chạy. Có thể dùng `--junitxml` để ghi kết quả cho từng lượt.
Xem [ảnh trích log pytest](../evidence/G-cong-thuc-ket-qua.png) để đối chiếu
lệnh và dòng tổng kết của từng lượt.
