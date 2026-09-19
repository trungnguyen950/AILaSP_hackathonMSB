# 09 — Use Cases & Giá trị sản phẩm (Pitch)

> MSB SmartForm AI · Use case end-to-end + giá trị nghiệp vụ + outline pitch 7 phút

---

## 1. Use cases chính (end-to-end)

### UC-1 — "Thêm kế toán vào eBank" (tổ chức)
**Input:** *"Công ty tôi (CP X) muốn đăng ký thêm kế toán vào eBank, kế toán lập lệnh, giám đốc duyệt."*
**Luồng:**
1. Agent nhận diện: KHTC, Công ty CP X (MST 0101234567, TK 123456789999).
2. Phân loại: `EBANK + USER + MAKER + APPROVER` + thiết lập luồng 2 người.
3. RAG chọn → **MSB-EBANK-01** (v2.1, hiệu lực).
4. Hỏi thiếu: họ tên kế toán, CCCD, ĐT, email, hạn mức, phương thức xác thực.
5. Điền mẫu + sinh bảng phân quyền `Kế toán | Maker | <user> | Lập lệnh | 500M | OTP` và `Giám đốc | Approver | <user> | Duyệt | — | Token`.
6. QC 8 check → `READY`. Người ký: ĐDPL. Checklist: mẫu + CCCD + GGĐL.
**Giá trị:** khách không cần biết mã mẫu; hồ sơ đúng lần đầu.

### UC-2 — "Đăng ký thuế điện tử" (tổ chức)
**Input:** *"Tôi muốn đăng ký tài khoản nộp thuế điện tử cho công ty."*
**Luồng:** nhận diện KHTC → `E-TAX` → **MSB-ETAX-03** → hỏi MST, TK nộp thuế, cơ quan thuế, chữ ký số (NCC, serial, hiệu lực), ĐDPL → điền → checklist (GGĐL, ủy quyền, hồ sơ CTS).
**Giá trị:** gom đủ hồ sơ pháp lý + CTS cùng lúc, tránh nộp thiếu.

### UC-3 — "Đổi chữ ký số" (tổ chức)
**Input:** *"Tôi muốn đổi chữ ký số sang nhà cung cấp khác."*
**Luồng:** `DIGITAL SIGNATURE` (thay đổi NCC) → **MSB-DS-04** → hỏi NCC mới, serial mới, hiệu lực → **không hỏi** PIN/private key/OTP → điền → checklist.
**Giá trị:** an toàn bí mật; khách biết chính xác cần giấy gì.

### UC-4 — "Đổi giám đốc / người đại diện" (tổ chức)
**Input:** *"Công ty đổi giám đốc, cần cập nhật với MSB."*
**Luồng:** `LEGAL REP CHANGE` → **MSB-AC-05** → hỏi tên mới, CCCD mới, số quyết định bổ nhiệm, ngày → chỉ 2 người ký (ĐDPL cũ + mới) + đóng dấu → checklist (GGĐL cập nhật, quyết định, CCCD).
**Giá trị:** chỉ đúng người ký, đúng dấu — giảm trả hồ sơ.

### UC-5 — "Tăng hạn mức eBank" (tổ chức)
**Input:** *"Tôi muốn tăng hạn mức eBank lên 2 tỷ/ngày."*
**Luồng:** `LIMIT` → **MSB-EBANK-06** → hỏi hạn mức hiện tại, phương thức phê duyệt → điền → ký ĐDPL.
**Giá trị:** thao tác 1 mẫu thay vì nhiều lần lên quầy.

### UC-6 — "Đăng ký Internet Banking cá nhân"
**Input:** *"Tôi là cá nhân, muốn đăng ký Internet Banking MSB."*
**Luồng:** nhận diện KHCN → `EBANK + SERVICE REGISTRATION` → **MSB-IB-02** → hỏi CCCD, ĐT, email, gói dịch vụ, hạn mức, người nhận OTP → điền → ký khách hàng (không đóng dấu).
**Giá trị:** tự soạn hồ sơ tại nhà, chỉ mang tới quầy nộp.

### UC-7 — "Khóa tạm thời eBank" / "Đổi số điện thoại nhận OTP"
- Khóa: `SERVICE TERMINATION` → **MSB-EBANK-07**.
- Đổi ĐT/OTP: `PHONE CHANGE` → **MSB-AC-08**.
**Giá trị:** xử lý nhanh các thay đổi nhỏ vốn dễ sai mẫu.

### UC-8 — `SOẠN HỒ SƠ` (chế độ soạn)
**Input:** sau khi Agent đã chọn mẫu + đủ thông tin, khách nói *"SOẠN HỒ SƠ"*.
**Luồng:** giữ bố cục MSB → điền dữ liệu DEMO → đánh dấu `[CẦN CUNG CẤP]` → preview → QC → xuất PDF + checklist.
**Giá trị:** bản xem trước trực quan, tải về nộp ngay.

---

## 2. Giá trị sản phẩm (Product Value)

| Đối tượng | Nỗi đau | Giá trị SmartForm AI |
|---|---|---|
| **Khách hàng DN** | Không biết mẫu nào, hay nộp thiếu | Nói nhu cầu → ra đúng mẫu + checklist → nộp đúng lần đầu |
| **Kế toán/admin** | Phân quyền eBank phức tạp | Sinh bảng Maker/Checker/Approver + hạn mức tự động |
| **Khách cá nhân** | Đăng ký IB phải lên quầy | Soạn hồ sơ tại nhà, tải PDF, chỉ nộp 1 lần |
| **Chuyên viên MSB** | Tư vấn lặp, kiểm tra thủ công | Xem trước hồ sơ khách soạn, xác nhận nhanh |
| **MSB (org)** | Rủi ro dùng mẫu cũ/hết hiệu lực | Luôn ưu tiên phiên bản active mới nhất |
| **Bảo mật** | Rò rỉ bí mật | Reject PIN/OTP/private key; không lưu; PII mask |

### Metrics định tính (mục tiêu demo)
- Giảm **số lần trả hồ sơ** do thiếu/sai mẫu: mục tiêu ↓ đáng kể.
- Giảm **thời gian chuẩn bị hồ sơ**: từ "tự tìm hàng chục mẫu" → "1 câu hỏi".
- **Tỷ lệ chọn đúng mẫu** (active + đúng phiên bản): mục tiêu cao.

---

## 3. Demo flow (cho pitch)

```
1. Mở web app → chat UI
2. Gõ: "Công ty CP X muốn thêm kế toán vào eBank, kế toán lập lệnh, giám đốc duyệt"
   → Agent hỏi bổ sung (họ tên, CCCD, hạn mức...)
3. Cung cấp thông tin → Agent chọn MSB-EBANK-01, điền, sinh bảng phân quyền
4. SOẠN HỒ SƠ → preview + QC STATUS: READY + checklist
5. Tải PDF + checklist
6. (Bonus) "Tôi muốn đổi chữ ký số" → MSB-DS-04, KHÔNG hỏi PIN → an toàn
```

---

## 4. Outline pitch 7 phút

| Phút | Nội dung |
|---|---|
| 0:00–0:45 | **Vấn đề**: khách hàng MSB phải tự tìm hàng chục mẫu biểu, hay nộp sai/thiếu → trả hồ sơ nhiều lần. |
| 0:45–1:30 | **Giải pháp**: MSB SmartForm AI — nói nhu cầu → Agent chọn đúng mẫu MSB → hỏi đủ thông tin → điền → checklist. |
| 1:30–2:15 | **Kiến trúc** (1 slide): 1 container AgentBase + LangGraph 8 bước + RAG trên Form Registry + GreenNode LLM. Nhấn mạnh: deploy qua skill GreenNode, KB bundle, không cần DB bên ngoài. |
| 2:15–4:30 | **Demo live**: UC-1 (thêm kế toán eBank) + UC-3 (đổi chữ ký số, không hỏi PIN). |
| 4:30–5:30 | **Giá trị**: bảng nỗi đau → giải pháp; an toàn bí mật; luôn dùng mẫu active. |
| 5:30–6:15 | **Độ tin cậy**: 8 quality check, STATUS READY/MISSING/NEED_REVIEW, Agent không phê duyệt (quyền MSB). |
| 6:15–7:00 | **Roadmap**: 13 nhóm nghiệp vụ, mẫu PDF thật, memory cross-session, prod pgvector + DR. |

---

## 5. Phân biệt & rủi ro

**Phân biệt:** không phải chatbot trả lời chung chung — là trợ lý nghiệp vụ **chỉ dùng mẫu MSB thật trong KB**, không bịa mẫu, bảo toàn pháp lý, output có cấu trúc 11 mục + checklist.

**Rủi ro & mitigate:**
- LLM chọn sai mẫu → RAG threshold + fallback "cần MSB xác nhận".
- Khách cung cấp bí mật → reject list ở API.
- Mẫu hết hiệu lực → filter `active=true` + version mới nhất.
