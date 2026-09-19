# Form Registry — Thư viện biểu mẫu MSB (DEMO)

> Dữ liệu giả lập phục vụ demo/test. Không sử dụng cho giao dịch thật.
> Cấu trúc cột đúng theo yêu cầu: `Mã mẫu | Tên mẫu | Nhóm nghiệp vụ | KHCN/KHTC | Loại hình DN | Trường hợp sử dụng | Người lập | Người ký | Hồ sơ kèm | Phiên bản | Ngày hiệu lực | File nguồn`

---

## Bảng Registry

| Mã mẫu | Tên mẫu | Nhóm nghiệp vụ | KHCN/KHTC | Loại hình DN | Trường hợp sử dụng | Người lập | Người ký | Hồ sơ kèm | Phiên bản | Ngày hiệu lực | File nguồn |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MSB-EBANK-01 | Đăng ký bổ sung người sử dụng eBank | eBank | KHTC | Tất cả | Bổ sung người dùng eBank (Maker/Checker/Approver), đặt hạn mức & xác thực | Chủ tài khoản / Người được ủy quyền | Người đại diện theo pháp luật | CCCD/Hộ chiếu; Giấy chứng nhận ĐKDN; Văn bản ủy quyền (nếu có) | 2.1 | 01/06/2024 | forms/MSB-EBANK-01_v2.1.pdf |
| MSB-IB-02 | Đăng ký dịch vụ Internet Banking MSB (cá nhân) | eBank | KHCN | Cá nhân | Đăng ký IB cá nhân, đặt hạn mức & phương thức xác thực | Khách hàng cá nhân | Khách hàng cá nhân | CCCD/Hộ chiếu | 3.0 | 15/03/2024 | forms/MSB-IB-02_v3.0.pdf |
| MSB-ETAX-03 | Đăng ký tài khoản nộp thuế điện tử | Thuế điện tử | KHTC | Tất cả | Đăng ký mới / thay đổi / bổ sung / hủy TK nộp thuế ETAX; liên kết với hệ thống thuế | Người đại diện theo pháp luật / Người được ủy quyền | Người đại diện theo pháp luật | Giấy chứng nhận ĐKDN; Văn bản ủy quyền; Hồ sơ chữ ký số | 1.5 | 01/01/2024 | forms/MSB-ETAX-03_v1.5.pdf |
| MSB-DS-04 | Đăng ký/thay đổi chữ ký số - chứng thư số | Chữ ký số | KHTC | Tất cả | Đăng ký mới / thay đổi / gia hạn / đổi chứng thư / đổi NCC / đổi serial / hủy | Người đại diện theo pháp luật / Người được ủy quyền | Người đại diện theo pháp luật | Giấy chứng nhận ĐKDN; CCCD; Hồ sơ chứng thư số hiện tại (nếu thay đổi) | 2.0 | 01/06/2024 | forms/MSB-DS-04_v2.0.pdf |
| MSB-AC-05 | Thay đổi thông tin doanh nghiệp & người đại diện theo pháp luật | Tài khoản | KHTC | Tất cả | Thay đổi ĐDPL / chủ tài khoản / kế toán trưởng / người ủy quyền | Chủ tài khoản | Người đại diện theo pháp luật (mới & cũ) | Giấy chứng nhận ĐKDN cập nhật; Quyết định bổ nhiệm; CCCD người mới | 1.8 | 01/04/2024 | forms/MSB-AC-05_v1.8.pdf |
| MSB-EBANK-06 | Thay đổi hạn mức & phương thức phê duyệt eBank | eBank | KHTC | Tất cả | Tăng/giảm hạn mức; đổi phương thức phê duyệt (1/2/3 người, N cấp) | Chủ tài khoản / Người được ủy quyền | Người đại diện theo pháp luật | Giấy chứng nhận ĐKDN; Văn bản ủy quyền (nếu có) | 1.2 | 01/06/2024 | forms/MSB-EBANK-06_v1.2.pdf |
| MSB-EBANK-07 | Khóa/mở khóa dịch vụ ngân hàng điện tử | eBank | KHTC | Tất cả | Khóa / mở khóa / tạm ngưng / kích hoạt lại eBank, IB | Chủ tài khoản / Người được ủy quyền | Người đại diện theo pháp luật | Giấy chứng nhận ĐKDN; Văn bản ủy quyền (nếu có) | 1.0 | 01/03/2024 | forms/MSB-EBANK-07_v1.0.pdf |
| MSB-AC-08 | Thay đổi thông tin liên hệ (ĐT/email/người nhận OTP) | Tài khoản | KHCN/KHTC | Tất cả / Cá nhân | Đổi số ĐT, email, người nhận OTP; cập nhật liên hệ | Chủ tài khoản / Khách hàng | Khách hàng / Người đại diện theo pháp luật | CCCD/Hộ chiếu; Giấy chứng nhận ĐKDN (nếu KHTC) | 2.3 | 15/05/2024 | forms/MSB-AC-08_v2.3.pdf |

---

## Ghi chú

- Tất cả bản ghi `active = true`, đang trong thời hạn hiệu lực.
- `File nguồn` trỏ tới object storage (`s3://forms/...`); file template JSON chi tiết nằm tại `knowledge-base/forms/<code>.md`.
- Khi có phiên bản mới hơn, phiên bản cũ set `active = false`; Agent luôn ưu tiên `active = true` + `version` cao nhất.
- `Loại hình DN = "Tất cả"` nghĩa là áp dụng cho CP / TNHH 1TV / TNHH 2TV+ / DNTN.
