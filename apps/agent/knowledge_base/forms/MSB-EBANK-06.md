# MSB-EBANK-06 — Thay đổi hạn mức & phương thức phê duyệt eBank (DEMO)

> Mẫu giả lập. Không dùng cho giao dịch thật.

## Metadata

| Cột | Giá trị |
|---|---|
| Mã mẫu | MSB-EBANK-06 |
| Tên mẫu | Thay đổi hạn mức và phương thức phê duyệt giao dịch eBank |
| Nhóm nghiệp vụ | eBank |
| KHCN/KHTC | KHTC |
| Loại hình DN | Tất cả |
| Trường hợp sử dụng | Tăng/giảm hạn mức; đổi phương thức phê duyệt (1/2/3 người, N cấp) |
| Người lập | Chủ tài khoản / Người được ủy quyền |
| Người ký | Người đại diện theo pháp luật |
| Hồ sơ kèm | Giấy chứng nhận ĐKDN; Văn bản ủy quyền (nếu có) |
| Phiên bản | 1.2 |
| Ngày hiệu lực | 01/06/2024 |
| File nguồn | forms/MSB-EBANK-06_v1.2.pdf |
| active | true |

## Trường biểu mẫu (fields)

| # | key | label | type | required | validate | ghi chú |
|---|---|---|---|---|---|---|
| 1 | company_name | Tên doanh nghiệp | text | yes | — | |
| 2 | tax_id | Mã số thuế | text | yes | mst_10digit | |
| 3 | account_no | Số tài khoản MSB | text | yes | msb_account | |
| 4 | legal_rep | Người đại diện theo pháp luật | text | yes | — | |
| 5 | current_limit | Hạn mức hiện tại | number | yes | ≥ 0 | VND |
| 6 | new_limit | Hạn mức đề xuất | number | yes | > 0 | VND |
| 7 | approval_flow | Phương thức phê duyệt | enum | yes | — | 1 người / 2 người / 3 người / N cấp |
| 8 | approver_names | Danh sách người phê duyệt | text | yes | — | theo approval_flow |
| 9 | effective_date | Ngày hiệu lực đề xuất | date | yes | — | |

## Người ký
| Người ký | Chức danh | Vị trí | Đóng dấu |
|---|---|---|---|
| Người đại diện theo pháp luật | Đại diện PL | ô ký chính | Theo mẫu (optional) |

## Nội dung cố định (không sửa)
- Logo MSB, mã mẫu `MSB-EBANK-06`, footer, điều kiện pháp lý cố định.

## Reject list (không hỏi / không lưu)
PIN, OTP, password, private key, secret key, API key.
