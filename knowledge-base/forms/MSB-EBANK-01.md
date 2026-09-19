# MSB-EBANK-01 — Đăng ký bổ sung người sử dụng eBank (DEMO)

> Mẫu giả lập. Không dùng cho giao dịch thật.

## Metadata

| Cột | Giá trị |
|---|---|
| Mã mẫu | MSB-EBANK-01 |
| Tên mẫu | Đăng ký bổ sung người sử dụng eBank |
| Nhóm nghiệp vụ | eBank |
| KHCN/KHTC | KHTC |
| Loại hình DN | Tất cả (CP / TNHH 1TV / TNHH 2TV+ / DNTN) |
| Trường hợp sử dụng | Bổ sung người dùng eBank (Maker/Checker/Approver), đặt hạn mức & xác thực |
| Người lập | Chủ tài khoản / Người được ủy quyền |
| Người ký | Người đại diện theo pháp luật |
| Hồ sơ kèm | CCCD/Hộ chiếu; Giấy chứng nhận ĐKDN; Văn bản ủy quyền (nếu có) |
| Phiên bản | 2.1 |
| Ngày hiệu lực | 01/06/2024 |
| File nguồn | forms/MSB-EBANK-01_v2.1.pdf |
| active | true |

## Trường biểu mẫu (fields)

| # | key | label | type | required | validate | ghi chú |
|---|---|---|---|---|---|---|
| 1 | company_name | Tên doanh nghiệp | text | yes | — | |
| 2 | tax_id | Mã số thuế | text | yes | mst_10digit | |
| 3 | account_no | Số tài khoản MSB | text | yes | msb_account | |
| 4 | legal_rep | Người đại diện theo pháp luật | text | yes | — | |
| 5 | user_name | Họ tên người dùng mới | text | yes | — | |
| 6 | cccd | CCCD/Hộ chiếu | text | yes | cccd_12 | |
| 7 | position | Chức danh | text | yes | — | |
| 8 | role | Vai trò | enum | yes | — | Maker / Checker / Approver |
| 9 | limit | Hạn mức giao dịch | number | no | > 0 | VND |
| 10 | auth_method | Phương thức xác thực | enum | yes | — | OTP / Token / SoftOTP |
| 11 | phone | Số điện thoại | text | yes | phone_vn | |
| 12 | email | Email | text | yes | email | |
| 13 | digital_sign_required | Yêu cầu chữ ký số | bool | no | — | nếu nghiệp vụ yêu cầu |

## Cấu trúc phê duyệt (eBank)
- 1 người: Maker + Approver (nếu SP cho phép)
- 2 người: Maker → Approver
- 3 người: Maker → Checker → Approver
- N cấp: Maker → Approver 1 → Approver 2 → ...

Bảng phân quyền sinh ra: `Người dùng | Chức danh | User | Vai trò | Hạn mức | Xác thực`.

## Người ký
| Người ký | Chức danh | Vị trí | Đóng dấu |
|---|---|---|---|
| Người đại diện theo pháp luật | Đại diện PL | ô ký chính | Theo mẫu (optional) |

## Nội dung cố định (không sửa)
- Logo MSB, mã mẫu `MSB-EBANK-01`, footer, điều kiện pháp lý cố định, cấu trúc phê duyệt.

## Reject list (không hỏi / không lưu)
PIN, OTP, password, private key, secret key, API key.
