# MSB-IB-02 — Đăng ký dịch vụ Internet Banking MSB (cá nhân) (DEMO)

> Mẫu giả lập. Không dùng cho giao dịch thật.

## Metadata

| Cột | Giá trị |
|---|---|
| Mã mẫu | MSB-IB-02 |
| Tên mẫu | Đăng ký dịch vụ Internet Banking MSB (cá nhân) |
| Nhóm nghiệp vụ | eBank |
| KHCN/KHTC | KHCN |
| Loại hình DN | Cá nhân |
| Trường hợp sử dụng | Đăng ký IB cá nhân, đặt hạn mức & phương thức xác thực |
| Người lập | Khách hàng cá nhân |
| Người ký | Khách hàng cá nhân |
| Hồ sơ kèm | CCCD/Hộ chiếu |
| Phiên bản | 3.0 |
| Ngày hiệu lực | 15/03/2024 |
| File nguồn | forms/MSB-IB-02_v3.0.pdf |
| active | true |

## Trường biểu mẫu (fields)

| # | key | label | type | required | validate | ghi chú |
|---|---|---|---|---|---|---|
| 1 | full_name | Họ và tên | text | yes | — | |
| 2 | cccd | CCCD/Hộ chiếu | text | yes | cccd_12 | |
| 3 | dob | Ngày sinh | date | yes | — | |
| 4 | phone | Số điện thoại | text | yes | phone_vn | |
| 5 | email | Email | text | yes | email | |
| 6 | account_no | Số tài khoản MSB | text | yes | msb_account | |
| 7 | service_level | Gói dịch vụ | enum | yes | — | Standard / Premium |
| 8 | limit | Hạn mức giao dịch/ngày | number | yes | > 0 | VND |
| 9 | auth_method | Phương thức xác thực | enum | yes | — | OTP / SoftOTP + SMS |
| 10 | otp_receiver | Người nhận OTP | enum | yes | — | Chính khách / Người được ủy quyền |

## Người ký
| Người ký | Chức danh | Vị trí | Đóng dấu |
|---|---|---|---|
| Khách hàng cá nhân | — | ô ký khách hàng | Không |

## Nội dung cố định (không sửa)
- Logo MSB, mã mẫu `MSB-IB-02`, footer, điều kiện pháp lý cố định.

## Reject list (không hỏi / không lưu)
PIN, OTP, password, private key, secret key, API key.
