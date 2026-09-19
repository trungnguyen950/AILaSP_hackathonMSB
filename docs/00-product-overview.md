# MSB SmartForm AI — Product Overview

> **Codename:** MSB SmartForm AI
> **Khách hàng:** Ngân hàng TMCP Hàng Hải Việt Nam — MSB
> **Tài liệu:** Tổng quan sản phẩm (mở đầu cho bộ SAD)
> **Phiên bản:** 0.1 (Draft — phục vụ Hackathon + baseline production)

---

## 1. Tuyên ngôn sản phẩm

Thay vì khách hàng phải tự tìm trong hàng chục mẫu biểu MSB, chỉ cần **mô tả nhu cầu bằng ngôn ngữ tự nhiên**, hệ thống tự:

`mô tả nhu cầu → xác định nghiệp vụ → chọn đúng mẫu MSB → hỏi thông tin còn thiếu → điền mẫu → kiểm tra logic → chỉ người ký → sinh checklist nộp hồ sơ`

## 2. Vấn đề đang giải

| Nỗi đau (Pain) | Hệ quả |
|---|---|
| Khách hàng/doanh nghiệp không biết mẫu nào phù hợp nhu cầu | Giao dịch bị trả hồ sơ nhiều lần |
| Mẫu biểu MSB nhiều, phân tán, nhiều phiên bản | Dễ dùng mẫu cũ/hết hiệu lực |
| Trường bắt buộc dễ bỏ sót | Hồ sơ thiếu, MSB phải yêu cầu bổ sung |
| Không rõ ai ký, ký ở đâu, có cần đóng dấu | Khách đến quầy mới bị hỏi lại |
| eBank: cấu trúc Maker/Checker/Approver phức tạp | Phân quyền sai, rủi ro giao dịch |

## 3. Giá trị mang lại

- **Khách hàng:** giảm thời gian chuẩn bị hồ sơ, giảm sai sót, nộp đúng lần đầu.
- **MSB (chuyên viên):** giảm thao tác lặp, tập trung vào việc xác nhận & tư vấn.
- **Hackathon:** demo end-to-end khả thi trong thời gian ngắn với dữ liệu giả lập.

## 4. Personas

| Persona | Mô tả | Mục tiêu với sản phẩm |
|---|---|---|
| **Khách hàng tổ chức** | Kế toán / nhân viên admin công ty (CP, TNHH 1TV, TNHH 2TV+, DNTN) | Soạn hồ sơ eBank, thuế điện tử, chữ ký số, thay đổi thông tin DN |
| **Khách hàng cá nhân** | Cá nhân dùng MSB | Đăng ký IB, thay đổi thông tin, dịch vụ |
| **Chuyên viên MSB** | Cán bộ CSKH doanh nghiệp | Xem trước hồ sơ khách soạn, xác nhận, tư vấn bổ sung |
| **Admin MSB** | Quản trị Form Registry | Upload/phiên bản/khoá mẫu biểu |

## 5. Phạm vi (Scope)

### In scope (v0.1 — Hackathon baseline)
- Chat UI soạn hồ sơ theo luồng 8 bước.
- Form Registry + 5 biểu mẫu giả lập trong Knowledge Base.
- RAG chọn mẫu theo ngữ nghĩa + điền trường + checklist.
- Module eBank (Maker/Checker/Approver), Thuế điện tử, Chữ ký số.
- 5 nhóm khách hàng giả lập (CP X, TNHH 1TV Y, TNHH 2TV+ Z, DNTN A, Cá nhân).
- Xuất hồ sơ đã điền (preview + PDF) + checklist.
- Quality check tự động (8 loại check).
- Web app đầy đủ (frontend + backend + agent + KB).

### Out of scope (v0.1)
- Gửi hồ sơ điện tử trực tiếp vào core banking MSB (chỉ chuẩn bị hồ sơ).
- Xác nhận/chấp thuận hồ sơ (quyền thuộc MSB).
- OCR tự động từ giấy tờ thật.
- Tích hợp SMS/OTP gateway thật.
- Dữ liệu khách hàng thật (chỉ dữ liệu DEMO).

## 6. Nguyên tắc cốt lõi

1. **Knowledge Base là nguồn chân lý** — Agent không tự bịa mẫu/số hiệu/phiên bản.
2. **Chuẩn bị, không phê duyệt** — Agent chỉ hỗ trợ; quyết định thuộc MSB.
3. **Không lưu bí mật** — PIN/OTP/private key/password/secret không hiển thị, không lưu.
4. **Dữ liệu DEMO** — mọi số liệu khách hàng đều giả lập.
5. **Bảo toàn mẫu MSB** — không sửa logo/mã mẫu/footer/nội dung pháp lý cố định.

## 7. Liên kết tài liệu

| # | Tài liệu | Mô tả |
|---|---|---|
| 00 | product-overview.md | (file này) |
| 01 | PRD.md | Yêu cầu chức năng + phi chức năng |
| 02 | architecture.md | SAD: HLA, sơ đồ, tech stack |
| 03 | LLD.md | Low-level design từng module |
| 04 | data-model.md | ER + schema + Form Registry |
| 05 | api-contract.md | REST API contract |
| 06 | security.md | Security architecture |
| 07 | deployment-ops.md | Triển khai, CI/CD, observability, DR |
| 08 | ADR.md | Architecture Decision Records |
| 09 | use-cases.md | Use case end-to-end + giá trị + outline pitch 7 phút |
| 10 | ui-ux-design.md | Design system + logo kim cương đỏ + wireframe & luồng PlantUML |
| — | agent-prompt.md | System prompt của Agent (rewrite + flag) |
| — | knowledge-base/ | Form Registry + 5 biểu mẫu giả lập |
