# MSB-EBANK-07 — Khóa/mở khóa dịch vụ ngân hàng điện tử (DEMO)

> Mẫu giả lập. Không dùng cho giao dịch thật.

## Metadata

| Cột | Giá trị |
|---|---|
| Mã mẫu | MSB-EBANK-07 |
| Tên mẫu | Khóa/mở khóa hoặc thay đổi dịch vụ ngân hàng điện tử |
| Nhóm nghiệp vụ | eBank |
| KHCN/KHTC | KHTC |
| Loại hình DN | Tất cả |
| Trường hợp sử dụng | Khóa / mở khóa / tạm ngưng / kích hoạt lại dịch vụ eBank, IB |
| Người lập | Chủ tài khoản / Người được ủy quyền |
| Người ký | Người đại diện theo pháp luật |
| Hồ sơ kèm | Giấy chứng nhận ĐKDN; Văn bản ủy quyền (nếu có) |
| Phiên bản | 1.0 |
| Ngày hiệu lực | 01/03/2024 |
| File nguồn | forms/MSB-EBANK-07_v1.0.pdf |
| active | true |

## Trường biểu mẫu (fields)

| # | key | label | type | required | validate | ghi chú |
|---|---|---|---|---|---|---|
| 1 | company_name | Tên doanh nghiệp | text | yes | — | |
| 2 | tax_id | Mã số thuế | text | yes | mst_10digit | |
| 3 | account_no | Số tài khoản MSB | text | yes | msb_account | |
| 4 | legal_rep | Người đại diện theo pháp luật | text | yes | — | |
| 5 | action_type | Loại yêu cầu | enum | yes | — | khóa / mở khóa / tạm ngưng / kích hoạt lại |
| 6 | service | Dịch vụ | enum | yes | — | eBank / Internet Banking / cụ thể |
| 7 | scope | Phạm vi | enum | yes | — | toàn bộ / theo user / theo chức năng |
| 8 | target_user | Người dùng bị ảnh hưởng | text | no | — | nếu scope = theo user |
| 9 | reason | Lý do | text | yes | — | |
| 10 | effective_date | Ngày hiệu lực | date | yes | — | |

## Người ký
| Người ký | Chức danh | Vị trí | Đóng dấu |
|---|---|---|---|
| Người đại diện theo pháp luật | Đại diện PL | ô ký chính | Theo mẫu (optional) |

## Nội dung cố định (không sửa)
- Logo MSB, mã mẫu `MSB-EBANK-07`, footer, điều kiện pháp lý cố định.

## Reject list (không hỏi / không lưu)
PIN, OTP, password, private key, secret key, API key.
