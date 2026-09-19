# MSB-EBANK-01-FDI — Bổ sung người sử dụng eBank (FDI / Bilingual VI-EN) (DEMO)

> Mẫu giả lập song ngữ Việt – Anh. Không dùng cho giao dịch thật.
> Áp dụng cho doanh nghiệp có vốn đầu tư nước ngoài (FDI).

## Metadata

| Cột | Giá trị |
|---|---|
| Mã mẫu | MSB-EBANK-01-FDI |
| Tên mẫu | Bổ sung người sử dụng eBank — Doanh nghiệp FDI (Song ngữ) |
| Nhóm nghiệp vụ | eBank |
| KHCN/KHTC | FDI |
| Loại hình DN | FDI (TNHH / CP) |
| Trường hợp sử dụng | Bổ sung người dùng eBank cho doanh nghiệp FDI; Maker/Checker/Approver; hạn mức; xác thực; biểu mẫu song ngữ VI-EN |
| Người lập | Chủ tài khoản / Người được ủy quyền |
| Người ký | Người đại diện theo pháp luật |
| Hồ sơ kèm | ERC (Giấy chứng nhận ĐKDN); IRC (Giấy chứng nhận ĐK đầu tư); CCCD/Hộ chiếu; Văn bản ủy quyền (nếu có) |
| Phiên bản | 1.0 |
| Ngày hiệu lực | 01/09/2024 |
| File nguồn | forms/MSB-EBANK-01-FDI_v1.0.pdf |
| active | true |

## Trường biểu mẫu (fields) — Bilingual VI / EN

| # | key | label | type | required | validate | ghi chú | label_en |
|---|---|---|---|---|---|---|---|
| 1 | company_name | Tên doanh nghiệp (VN) | text | yes | — | | Company name (VN) |
| 2 | company_name_en | Tên doanh nghiệp (EN) | text | yes | — | theo ERC/IRC | Company name (EN) |
| 3 | tax_id | Mã số thuế / Enterprise number | text | yes | mst_10digit | | Tax ID / Enterprise number |
| 4 | account_no | Số tài khoản MSB | text | yes | msb_account | | Account number |
| 5 | legal_rep | Người đại diện theo pháp luật | text | yes | — | | Legal representative |
| 6 | legal_rep_nationality | Quốc tịch người đại diện | text | yes | — | | Nationality |
| 7 | legal_rep_passport | Số hộ chiếu / Passport No. | text | yes | — | nếu nước ngoài | Passport number |
| 8 | user_name | Họ tên người dùng mới | text | yes | — | | New eBank user name |
| 9 | cccd | CCCD / Hộ chiếu (người dùng) | text | yes | cccd_12 | | ID / Passport (user) |
| 10 | position | Chức danh | text | yes | — | | Title |
| 11 | role | Vai trò | enum | yes | — | Maker / Checker / Approver | Role |
| 12 | limit | Hạn mức giao dịch | number | no | > 0 | VND | Transaction limit |
| 13 | auth_method | Phương thức xác thực | enum | yes | — | OTP / Token / SoftOTP | Authentication method |
| 14 | phone | Số điện thoại | text | yes | phone_vn | | Telephone |
| 15 | email | Email | text | yes | email | | Email |
| 16 | digital_sign_required | Yêu cầu chữ ký số | bool | no | — | | Digital signature required |

## Cấu trúc phê duyệt (eBank) — Approval Structure
- 1 người / 1 person: Maker + Approver (nếu SP cho phép)
- 2 người / 2 persons: Maker → Approver
- 3 người / 3 persons: Maker → Checker → Approver
- N cấp / N levels: Maker → Approver 1 → Approver 2 → ...

Bảng phân quyền / Authorization table: `Người dùng / User | Chức danh / Title | Vai trò / Role | Hạn mức / Limit | Xác thực / Auth`

## Người ký — Signatory
| Người ký / Signatory | Chức danh / Title | Vị trí / Position | Đóng dấu / Stamp |
|---|---|---|---|
| Người đại diện theo pháp luật / Legal Representative | Đại diện PL / Legal Rep | ô ký chính / main signature | Theo mẫu / As per form (optional) |

## Nội dung cố định (không sửa) — Fixed Content
- Logo MSB, mã mẫu `MSB-EBANK-01-FDI`, footer, điều kiện pháp lý cố định.
- Bilingual layout: Vietnamese left column, English right column.
- ERC and IRC references required for FDI customers.

## Reject list (không hỏi / không lưu) — Never Request or Store
PIN, OTP, password, private key, secret key, API key.
> Tuyệt đối không yêu cầu khách cung cấp các trường này; không lưu; không hiển thị.
