# MSB-AC-08 — Thay đổi thông tin liên hệ (số điện thoại/email/người nhận OTP) (DEMO)

> Mẫu giả lập. Không dùng cho giao dịch thật.

## Metadata

| Cột | Giá trị |
|---|---|
| Mã mẫu | MSB-AC-08 |
| Tên mẫu | Thay đổi số điện thoại, email, người nhận OTP và thông tin liên hệ |
| Nhóm nghiệp vụ | Tài khoản |
| KHCN/KHTC | KHCN/KHTC |
| Loại hình DN | Tất cả / Cá nhân |
| Trường hợp sử dụng | Đổi số ĐT, email, người nhận OTP; cập nhật thông tin liên hệ |
| Người lập | Chủ tài khoản / Khách hàng |
| Người ký | Khách hàng / Người đại diện theo pháp luật |
| Hồ sơ kèm | CCCD/Hộ chiếu; Giấy chứng nhận ĐKDN (nếu KHTC) |
| Phiên bản | 2.3 |
| Ngày hiệu lực | 15/05/2024 |
| File nguồn | forms/MSB-AC-08_v2.3.pdf |
| active | true |

## Trường biểu mẫu (fields)

| # | key | label | type | required | validate | ghi chú |
|---|---|---|---|---|---|---|
| 1 | customer_name | Họ tên / Tên doanh nghiệp | text | yes | — | |
| 2 | tax_id_or_cccd | MST (KHTC) / CCCD (KHCN) | text | yes | mst_10digit OR cccd_12 | |
| 3 | account_no | Số tài khoản MSB | text | yes | msb_account | |
| 4 | change_phone | Số điện thoại mới | text | no | phone_vn | nếu đổi ĐT |
| 5 | change_email | Email mới | text | no | email | nếu đổi email |
| 6 | otp_receiver | Người nhận OTP | enum | no | — | Chính khách / Người được ủy quyền |
| 7 | otp_receiver_name | Họ tên người nhận OTP | text | no | — | nếu otp_receiver = ủy quyền |
| 8 | otp_receiver_phone | Số ĐT người nhận OTP | text | no | phone_vn | |
| 9 | contact_address | Địa chỉ liên hệ mới | text | no | — | |

## Người ký
| Người ký | Chức danh | Vị trí | Đóng dấu |
|---|---|---|---|
| Khách hàng / Người đại diện theo pháp luật | — | ô ký khách hàng | KHTC: theo mẫu; KHCN: không |

## Nội dung cố định (không sửa)
- Logo MSB, mã mẫu `MSB-AC-08`, footer, điều kiện pháp lý cố định.

## Reject list (không hỏi / không lưu)
PIN, OTP, password, private key, secret key, API key.
