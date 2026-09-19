# 01 — Product Requirements Document (PRD)

> MSB SmartForm AI · v0.1 Draft

---

## 1. Yêu cầu chức năng (FR)

### FR-1 Nhận diện khách hàng
- **FR-1.1** Hệ thống xác định khách hàng là cá nhân hay tổ chức, loại hình tổ chức (CP / TNHH 1TV / TNHH 2TV+ / DNTN).
- **FR-1.2** Hệ thống hỏi đã có tài khoản MSB chưa, đã dùng eBank chưa.
- **FR-1.3** Hệ thống lưu profile khách hàng DEMO theo phiên (session).

### FR-2 Nhận diện nhu cầu bằng ngôn ngữ tự nhiên
- **FR-2.1** Khách nhập yêu cầu free-text → Agent phân loại thành 1 hoặc nhiều nghiệp vụ thuộc tập: `ACCOUNT, EBANK, USER, AUTHORIZATION, MAKER, CHECKER, APPROVER, LIMIT, OTP, DIGITAL SIGNATURE, E-TAX, ACCOUNT CHANGE, LEGAL REP CHANGE, ACCOUNT HOLDER CHANGE, PHONE CHANGE, EMAIL CHANGE, SERVICE REGISTRATION, SERVICE TERMINATION`.
- **FR-2.2** Một câu có thể tách thành nhiều nghiệp vụ (vd: thêm người dùng + gán quyền + đặt hạn mức).

### FR-3 Form Registry & chọn mẫu
- **FR-3.1** Hệ thống duy trì Form Registry với các trường: `Mã mẫu, Tên mẫu, Nhóm nghiệp vụ, KHCN/KHTC, Loại hình DN, Trường hợp sử dụng, Người lập, Người ký, Hồ sơ kèm, Phiên bản, Ngày hiệu lực, File nguồn`.
- **FR-3.2** Agent tra Knowledge Base (RAG) để chọn mẫu phù hợp; ưu tiên mẫu đang hiệu lực, phiên bản mới nhất.
- **FR-3.3** Nếu nhiều mẫu phù hợp → liệt kê toàn bộ. Nếu không có → trả câu báo báo chuẩn `"Chưa xác định được mẫu biểu MSB..."`.
- **FR-3.4** Agent không tự đặt tên/số hiệu/phiên bản mẫu không tồn tại.

### FR-4 Thu thập thông tin còn thiếu
- **FR-4.1** Agent chỉ hỏi các trường bắt buộc còn thiếu, không hỏi lại thông tin đã có.
- **FR-4.2** Thông tin chưa có được đánh dấu `[CHƯA CÓ THÔNG TIN]` / `[CẦN KHÁCH HÀNG CUNG CẤP]`.

### FR-5 Điền & kiểm tra biểu mẫu
- **FR-5.1** Agent điền các trường có dữ liệu, giữ nguyên bố cục/logo/mã mẫu/footer/nội dung pháp lý cố định của MSB.
- **FR-5.2** Kiểm tra logic: tên DN, MST, số TK, họ tên, chức danh, ĐDPL, CCCD/HC, ĐT, email, chữ ký số, vai trò, quyền, hạn mức, phương thức phê duyệt, số lượng chữ ký, tính nhất quán giữa các mẫu.

### FR-6 Xác định người ký
- **FR-6.1** Chỉ rõ: người cần ký, chức danh, vị trí ký, có cần đóng dấu (Có/Không/Chưa xác định theo mẫu).
- **FR-6.2** Không tự kết luận yêu cầu đóng dấu nếu tài liệu MSB không quy định.

### FR-7 Checklist nộp hồ sơ
- **FR-7.1** Sinh checklist: biểu mẫu, hồ sơ pháp lý kèm, CCCD/HC, văn bản ủy quyền, thông tin eBank, hồ sơ chữ ký số, hồ sơ thuế điện tử, tài liệu khác.

### FR-8 Module eBank
- **FR-8.1** Hỗ trợ cấu trúc: 1 người (Maker+Approver nếu SP cho phép), 2 người (Maker→Approver), 3 người (Maker→Checker→Approver), nhiều cấp (Maker→Approver1→Approver2→...).
- **FR-8.2** Sinh bảng phân quyền: `Người dùng | Chức danh | User | Vai trò | Hạn mức | Xác thực`.

### FR-9 Module Thuế điện tử
- **FR-9.1** Phân biệt: đăng ký mới / thay đổi TK / bổ sung TK / hủy TK / thay đổi chữ ký số / thay đổi ĐDPL–người sử dụng.

### FR-10 Module Chữ ký số
- **FR-10.1** Hỗ trợ: đăng ký mới / thay đổi / gia hạn / thay đổi chứng thư / thay đổi nhà cung cấp / thay đổi serial / hủy.
- **FR-10.2** Kiểm tra: tên chủ chứng thư, MST/CCCD, nhà cung cấp, serial, ngày hiệu lực, ngày hết hạn, email, ĐT.
- **FR-10.3** Không yêu cầu/liên lạc với khách hàng về: PRIVATE KEY, PIN, PASSWORD, OTP. Không lưu/hiển thị các bí mật này.

### FR-11 Output chuẩn (11 mục)
Mỗi trả lời có cấu trúc: A. Nhu cầu · B. Loại KH · C. Nghiệp vụ MSB · D. Mẫu biểu · E. Thông tin đã có · F. Thông tin còn thiếu · G. Biểu mẫu đã điền · H. Người cần ký · I. Hồ sơ kèm · J. Checklist · K. Cảnh báo/điểm cần MSB xác nhận.

### FR-12 Chế độ "SOẠN HỒ SƠ"
- **FR-12.1** Khi người dùng nói `SOẠN HỒ SƠ`: chọn đúng mẫu → giữ bố cục → điền dữ liệu giả lập → đánh dấu trường thiếu → tạo bản xem trước → kiểm tra logic → xuất bản hoàn chỉnh.

### FR-13 Quality control
- **FR-13.1** Trước khi xuất hồ sơ, tự chạy 8 check: FORM, DATA, SIGNATURE, AUTHORITY, EBANK ROLE, LIMIT, MANDATORY FIELD, DOCUMENT CONSISTENCY.
- **FR-13.2** Trả `STATUS: READY | MISSING INFORMATION | NEED MSB REVIEW`.

### FR-14 Reverse / admin
- **FR-14.1** Admin upload/phiên bản/khoá mẫu biểu vào Form Registry.
- **FR-14.2** Agent hỗ trợ reverse-engineer (đọc cấu trúc mẫu → sinh lại metadata) — dành cho modernization.

### FR-15 Web app
- **FR-15.1** Chat UI + form preview + checklist view + history + role-based (KH / chuyên viên MSB / admin).

---

## 2. Yêu cầu phi chức năng (NFR)

| ID | Nhóm | Yêu cầu | Mục tiêu v0.1 |
|---|---|---|---|
| NFR-1 | Hiệu năng | Độ trễ phản hồi Agent | P95 < 6s / lượt (gồm RAG + LLM) |
| NFR-2 | Hiệu năng | Tra Form Registry | < 300ms |
| NFR-3 | Throughput | Số phiên đồng thời | 50 phiên (demo); scale-out |
| NFR-4 | Bảo mật | Mã hóa at-rest + in-transit | TLS 1.2+, AES-256 |
| NFR-5 | Bảo mật | Không lưu bí mật | PIN/OTP/key/password — reject ở đầu vào |
| NFR-6 | Bảo mật | RBAC | KH / MSB staff / admin |
| NFR-7 | Audit | L ghi mọi thao tác | Bảo lưu 12 tháng (mục tiêu) |
| NFR-8 | Khả dụng | Uptime | 99.5% (demo); 99.9% (prod) |
| NFR-9 | RPO/RTO | DR | RPO 15m, RTO 1h (mục tiêu prod) |
| NFR-10 | Khả mở rộng | Thêm mẫu mới | Via admin, không deploy lại agent |
| NFR-11 | i18n | Ngôn ngữ | Tiếng Việt (primary); UI label EN (mục tiêu) |
| NFR-12 | Compliance | OWASP Top 10, 12-factor | Pass checklist |
| NFR-13 | Dữ liệu | DEMO only | Không dữ liệu KH thật ở v0.1 |

---

## 3. Ràng buộc & giả định

- **Giả định:** Dữ liệu khách hàng trong v0.1 100% giả lập (CÔNG TY CP X, TNHH 1TV Y, TNHH 2TV+ Z, DNTN A, NGUYỄN VĂN A).
- **Ràng buộc:** Agent không bao giờ phê duyệt hồ sơ; không lưu bí mật; không sửa nội dung pháp lý cố định của mẫu.
- **Nguồn mẫu:** Knowledge Base do Admin nạp; Agent chỉ đọc.

---

## 4. Acceptance criteria (mốc demo)

1. Nhập *"Công ty tôi muốn đăng ký thêm kế toán vào eBank"* → Agent trả đúng nghiệp vụ + đúng mẫu `MSB-EBANK-01` + hỏi đủ trường + sinh checklist.
2. Nhập *"Tôi muốn đăng ký thuế điện tử"* → chọn `MSB-ETAX-03`, hỏi MST/TK/ĐDPL/chữ ký số.
3. Nhập *"Tôi đổi chữ ký số"* → chọn `MSB-DS-04`, hỏi nhà cung cấp/serial/hiệu lực, **không** hỏi PIN/private key.
4. `SOẠN HỒ SƠ` → sinh preview đã điền + đánh dấu trường thiếu + STATUS.
5. 8 quality check chạy và trả STATUS đúng.
