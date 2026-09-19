# MSB-DS-04 — Đăng ký/thay đổi chữ ký số - chứng thư số (DEMO)

> Mẫu giả lập. Không dùng cho giao dịch thật.

## Metadata

| Cột | Giá trị |
|---|---|
| Mã mẫu | MSB-DS-04 |
| Tên mẫu | Đăng ký/thay đổi chữ ký số - chứng thư số |
| Nhóm nghiệp vụ | Chữ ký số |
| KHCN/KHTC | KHTC |
| Loại hình DN | Tất cả |
| Trường hợp sử dụng | Đăng ký mới / thay đổi / gia hạn / đổi chứng thư / đổi NCC / đổi serial / hủy |
| Người lập | Người đại diện theo pháp luật / Người được ủy quyền |
| Người ký | Người đại diện theo pháp luật |
| Hồ sơ kèm | Giấy chứng nhận ĐKDN; CCCD; Hồ sơ chứng thư số hiện tại (nếu thay đổi) |
| Phiên bản | 2.0 |
| Ngày hiệu lực | 01/06/2024 |
| File nguồn | forms/MSB-DS-04_v2.0.pdf |
| active | true |

## Phân nhánh nghiệp vụ
`đăng ký mới` · `thay đổi` · `gia hạn` · `thay đổi chứng thư số` · `thay đổi nhà cung cấp` · `thay đổi serial` · `hủy đăng ký`

## Trường biểu mẫu (fields)

| # | key | label | type | required | validate | ghi chú |
|---|---|---|---|---|---|---|
| 1 | company_name | Tên doanh nghiệp / Tên chủ chứng thư | text | yes | — | |
| 2 | tax_id_or_cccd | MST (tổ chức) / CCCD (cá nhân) | text | yes | mst_10digit OR cccd_12 | |
| 3 | action_type | Loại yêu cầu | enum | yes | — | mới / thay đổi / gia hạn / đổi chứng thư / đổi NCC / đổi serial / hủy |
| 4 | ds_provider | Nhà cung cấp chữ ký số | text | yes | — | |
| 5 | ds_serial | Serial chứng thư số | text | yes | — | không chứa private key |
| 6 | ds_valid_from | Ngày hiệu lực | date | yes | — | |
| 7 | ds_valid_to | Ngày hết hạn | date | yes | — | |
| 8 | legal_rep | Người đại diện theo pháp luật | text | yes | — | |
| 9 | phone | Số điện thoại | text | yes | phone_vn | |
| 10 | email | Email | text | yes | email | |
| 11 | old_serial | Serial chứng thư cũ | text | no | — | nếu thay đổi |

## Người ký
| Người ký | Chức danh | Vị trí | Đóng dấu |
|---|---|---|---|
| Người đại diện theo pháp luật | Đại diện PL | ô ký chính | Có (cong dấu doanh nghiệp) |

## Nội dung cố định (không sửa)
- Logo MSB, mã mẫu `MSB-DS-04`, footer, điều kiện pháp lý cố định.

## Reject list (không hỏi / không lưu)
**PRIVATE KEY, PIN, PASSWORD, OTP**, secret key, API key.
> Tuyệt đối không yêu cầu khách cung cấp các trường này; không lưu; không hiển thị.
