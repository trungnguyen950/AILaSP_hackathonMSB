# MSB-AC-05 — Thay đổi thông tin doanh nghiệp & người đại diện theo pháp luật (DEMO)

> Mẫu giả lập. Không dùng cho giao dịch thật.

## Metadata

| Cột | Giá trị |
|---|---|
| Mã mẫu | MSB-AC-05 |
| Tên mẫu | Thay đổi thông tin doanh nghiệp & người đại diện theo pháp luật |
| Nhóm nghiệp vụ | Tài khoản |
| KHCN/KHTC | KHTC |
| Loại hình DN | Tất cả |
| Trường hợp sử dụng | Thay đổi ĐDPL / chủ tài khoản / kế toán trưởng / người ủy quyền |
| Người lập | Chủ tài khoản |
| Người ký | Người đại diện theo pháp luật (mới & cũ) |
| Hồ sơ kèm | Giấy chứng nhận ĐKDN cập nhật; Quyết định bổ nhiệm; CCCD người mới |
| Phiên bản | 1.8 |
| Ngày hiệu lực | 01/04/2024 |
| File nguồn | forms/MSB-AC-05_v1.8.pdf |
| active | true |

## Trường biểu mẫu (fields)

| # | key | label | type | required | validate | ghi chú |
|---|---|---|---|---|---|---|
| 1 | company_name | Tên doanh nghiệp | text | yes | — | |
| 2 | tax_id | Mã số thuế | text | yes | mst_10digit | |
| 3 | account_no | Số tài khoản MSB | text | yes | msb_account | |
| 4 | change_type | Nội dung thay đổi | enum | yes | — | ĐDPL / chủ TK / kế toán trưởng / người ủy quyền |
| 5 | old_name | Họ tên (cũ) | text | yes | — | |
| 6 | new_name | Họ tên (mới) | text | yes | — | |
| 7 | new_position | Chức danh (mới) | text | yes | — | |
| 8 | new_cccd | CCCD (mới) | text | yes | cccd_12 | |
| 9 | appointment_doc_no | Số quyết định bổ nhiệm | text | yes | — | |
| 10 | appointment_date | Ngày quyết định | date | yes | — | |
| 11 | phone | Số điện thoại liên hệ | text | yes | phone_vn | |
| 12 | email | Email liên hệ | text | yes | email | |

## Người ký
| Người ký | Chức danh | Vị trí | Đóng dấu |
|---|---|---|---|
| Người đại diện theo pháp luật (cũ) | Đại diện PL (cũ) | ô ký 1 | Có |
| Người đại diện theo pháp luật (mới) | Đại diện PL (mới) | ô ký 2 | Có |

## Nội dung cố định (không sửa)
- Logo MSB, mã mẫu `MSB-AC-05`, footer, điều kiện pháp lý cố định.

## Reject list (không hỏi / không lưu)
PIN, OTP, password, private key, secret key, API key.
