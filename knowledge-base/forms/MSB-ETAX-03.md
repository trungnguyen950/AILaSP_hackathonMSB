# MSB-ETAX-03 — Đăng ký tài khoản nộp thuế điện tử (DEMO)

> Mẫu giả lập. Không dùng cho giao dịch thật.

## Metadata

| Cột | Giá trị |
|---|---|
| Mã mẫu | MSB-ETAX-03 |
| Tên mẫu | Đăng ký tài khoản nộp thuế điện tử |
| Nhóm nghiệp vụ | Thuế điện tử |
| KHCN/KHTC | KHTC |
| Loại hình DN | Tất cả |
| Trường hợp sử dụng | Đăng ký mới / thay đổi / bổ sung / hủy TK nộp thuế ETAX; liên kết hệ thống thuế |
| Người lập | Người đại diện theo pháp luật / Người được ủy quyền |
| Người ký | Người đại diện theo pháp luật |
| Hồ sơ kèm | Giấy chứng nhận ĐKDN; Văn bản ủy quyền; Hồ sơ chữ ký số |
| Phiên bản | 1.5 |
| Ngày hiệu lực | 01/01/2024 |
| File nguồn | forms/MSB-ETAX-03_v1.5.pdf |
| active | true |

## Phân nhánh nghiệp vụ
`đăng ký mới` · `thay đổi tài khoản` · `bổ sung tài khoản` · `hủy tài khoản` · `thay đổi chữ ký số` · `thay đổi ĐDPL / người sử dụng`

## Trường biểu mẫu (fields)

| # | key | label | type | required | validate | ghi chú |
|---|---|---|---|---|---|---|
| 1 | company_name | Tên doanh nghiệp | text | yes | — | |
| 2 | tax_id | Mã số thuế | text | yes | mst_10digit | |
| 3 | account_no | Số tài khoản MSB (nộp thuế) | text | yes | msb_account | |
| 4 | legal_rep | Người đại diện theo pháp luật | text | yes | — | |
| 5 | branch | Cơ quan thuế quản lý | text | yes | — | |
| 6 | action_type | Loại yêu cầu | enum | yes | — | mới / thay đổi / bổ sung / hủy |
| 7 | ds_provider | Nhà cung cấp chữ ký số | text | yes | — | |
| 8 | ds_serial | Serial chứng thư số | text | yes | — | không chứa private key |
| 9 | ds_valid_to | Hiệu lực chứng thư đến | date | yes | — | |
| 10 | phone | Số điện thoại | text | yes | phone_vn | |
| 11 | email | Email | text | yes | email | |
| 12 | authorized_person | Người được ủy quyền | text | no | — | nếu có |

## Người ký
| Người ký | Chức danh | Vị trí | Đóng dấu |
|---|---|---|---|
| Người đại diện theo pháp luật | Đại diện PL | ô ký chính | Có (cong dấu doanh nghiệp) |

## Nội dung cố định (không sửa)
- Logo MSB, mã mẫu `MSB-ETAX-03`, footer, điều kiện pháp lý cố định.

## Reject list (không hỏi / không lưu)
PIN, OTP, password, private key, secret key, API key.
