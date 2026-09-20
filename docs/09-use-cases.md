# 09 — Use Cases & Giá trị sản phẩm (Pitch)

> MSB SmartForm AI · Use case end-to-end + giá trị nghiệp vụ + outline pitch 7 phút · v1.0

---

## 1. Use cases chính (end-to-end)

### UC-1 — "Thêm kế toán vào eBank" (tổ chức, guided flow)
**Input:** Nhấn thẻ **"CTCP X"** → Agent tự gửi: *"Công ty CP X muốn thêm kế toán vào eBank, kế toán lập lệnh, giám đốc duyệt"*
**Luồng:**
1. Agent chào hỏi, xác định: KHTC, Công ty CP X.
2. Chọn form: **MSB-EBANK-01** (v2.1, hiệu lực).
3. **Giải thích từng trường** (13 fields) kèm hướng dẫn: "Mã số thuế — 10 chữ số, ví dụ: 0101234567 — xem Giấy chứng nhận ĐKDN".
4. **Đưa mẫu giả lập** với data demo (CÔNG TY CỔ PHẦN X, 0101234567, Nguyễn Thị Lan...).
5. Khách gõ `sẵn sàng` → Agent hỏi 7 trường thiếu (tiếng Việt có dấu).
6. Khách nhập: `Nguyễn Văn B | 001098765432 | Kế toán | Maker | OTP | 0901234567 | b@congtyx.vn`
7. Agent điền + QC 9 checks → `READY`. Checklist: mẫu + CCCD + GGĐL.
8. Nhấn **SOẠN HỒ SƠ** → tải Text + PDF vintage.
**Giá trị:** khách hiểu rõ từng trường, nộp đúng lần đầu.

### UC-2 — FDI Enterprise (song ngữ VI-EN)
**Input:** Nhấn thẻ **"FDI Alpha 🌐"** → Agent gửi: *"Our company, Alpha Vietnam FDI Company Limited..."*
**Luồng:**
1. Agent detects English → responds in English.
2. Chọn form: **MSB-EBANK-01-FDI** (bilingual, 16 fields).
3. Explains each field in English: "Tax ID — 10 digits, e.g. 0101234567 — see Business Registration Certificate".
4. Mock example with Alpha Vietnam data (David Chen, Singapore, S1234567A).
5. Customer types `ready` → Agent asks 7 missing fields in English.
6. Customer provides: `Nguyen Thi Lan | 001098765432 | Ke toan | Maker | OTP | 0901234567 | lan@alphavietnam.vn`
7. Agent fills 15 fields, bilingual output (L_bilingual), QC 9 checks → `READY`.
**Giá trị:** international customer experience, bilingual forms, passport + nationality support.

### UC-3 — "Đổi chữ ký số" (an toàn bí mật)
**Input:** *"Tôi muốn đổi chữ ký số sang nhà cung cấp khác."*
**Luồng:** `DIGITAL SIGNATURE` → **MSB-DS-04** → hỏi NCC mới, serial mới, hiệu lực → **không hỏi** PIN/private key/OTP → điền → checklist.
**Giá trị:** an toàn bí mật; khách biết chính xác cần giấy gì.

### UC-4 — "Đổi giám đốc / người đại diện"
**Input:** *"Công ty đổi giám đốc, cần cập nhật với MSB."*
**Luồng:** `LEGAL REP CHANGE` → **MSB-AC-05** → Agent giải thích 12 trường → khách nhập theo format Label: value:
```
Nội dung thay đổi: Bổ nhiệm Giám đốc mới
Họ tên (cũ): Nguyễn Văn Minh
Họ tên (mới): Trần Hoàng Nam
CCCD (mới): 079200012345
...
```
→ Agent parse Label: value → điền 12 fields → READY.
**Giá trị:** khách có thể copy câu hỏi của Agent, điền value, gửi lại — Agent tự match.

### UC-5 — Upload file + Ký số + Gửi Zalo
**Input:** Vào trang **✍️ Ký Số** → chọn form MSB-DS-04 + chứng thư Viettel-CA.
**Luồng:**
1. Upload file .txt chứa nội dung form.
2. Nhấn **🤖 AI Kiểm Tra File** → Agent kiểm tra: form code, field structure, content → ✅ hợp lệ (score: 100/100).
3. Vẽ chữ ký trên canvas.
4. Nhấn **✍️ Ký File Đã Upload** → Agent chèn chữ ký, tạo SHA256 hash, webhook.
5. Tải file đã ký.
6. Nhấn **💬 Gửi Zalo Bot** → khách nhận PDF + thông báo qua Zalo.
**Giá trị:** end-to-end: upload → AI check → ký → gửi khách hàng.

### UC-6 — AI Fill từ thư viện biểu mẫu
**Input:** Vào trang **📋 Mẫu Biểu Mẫu** → nhấn **🤖 AI Fill** trên card MSB-EBANK-06.
**Luồng:**
1. Chuyển sang trang Chat → Agent gửi: "Tôi muốn điền mẫu MSB-EBANK-06..."
2. Agent giải thích form (không pre-fill demo data).
3. Khách gõ `sẵn sàng` → Agent hỏi **tất cả 11 trường bắt buộc**.
4. Khách cung cấp dữ liệu → READY → SOẠN HỒ SƠ.
**Giá trị:** khách tự chọn form từ thư viện, điền từ đầu.

---

## 2. Giá trị sản phẩm (Product Value)

| Đối tượng | Nỗi đau | Giá trị SmartForm AI |
|---|---|---|
| **Khách hàng DN** | Không biết mẫu nào, hay nộp thiếu | Nói nhu cầu → Agent giải thích + ví dụ → nộp đúng lần đầu |
| **Khách FDI** | Cần form song ngữ, không có mẫu phù hợp | Form VI-EN, hướng dẫn tiếng Anh, passport + nationality |
| **Kế toán/admin** | Phân quyền eBank phức tạp | Sinh bảng Maker/Checker/Approver + hạn mức tự động |
| **Khách cá nhân** | Đăng ký IB phải lên quầy | Soạn hồ sơ tại nhà, tải PDF, chỉ nộp 1 lần |
| **Chuyên viên MSB** | Tư vấn lặp, kiểm tra thủ công | Xem trước hồ sơ khách soạn, xác nhận nhanh |
| **MSB (org)** | Rủi ro dùng mẫu cũ/hết hiệu lực | Luôn ưu tiên phiên bản active mới nhất |
| **Bảo mật** | Rò rỉ bí mật | Reject PIN/OTP/private key; không lưu; PII mask |
| **Trải nghiệm ký** | Phải lên quầy ký thủ công | Ký số online → gửi Zalo Bot cho khách |

### Metrics định tính (mục tiêu demo)
- Giảm **số lần trả hồ sơ** do thiếu/sai mẫu: mục tiêu ↓ đáng kể.
- Giảm **thời gian chuẩn bị hồ sơ**: từ "tự tìm hàng chục mẫu" → "1 câu hỏi + hiểu rõ trường".
- **Tỷ lệ chọn đúng mẫu** (active + đúng phiên bản): mục tiêu cao.
- **FDI customer satisfaction**: bilingual forms, English instructions.

---

## 3. Demo flow (cho pitch 7 phút)

```
1. Mở web app → 6 persona cards
2. Nhấn "FDI Alpha 🌐" → Agent giải thích form bằng tiếng Anh (FORM EXPLAINED)
3. Gõ: ready → Agent hỏi 7 trường (English)
4. Nhập: Nguyen Thi Lan | 001098765432 | Ke toan | Maker | OTP | 0901234567 | lan@alphavietnam.vn
   → READY (15 fields, bilingual)
5. SOẠN HỒ SƠ → checklist + PDF vintage
6. Vào /sign/ → upload file → AI check → vẽ chữ ký → ký → tải file
7. Gửi Zalo Bot → khách nhận PDF
```

---

## 4. Outline pitch 7 phút

| Phút | Nội dung |
|---|---|
| 0:00–0:45 | **Vấn đề**: khách hàng MSB phải tự tìm hàng chục mẫu biểu, hay nộp sai/thiếu → trả hồ sơ nhiều lần. FDI cần song ngữ. |
| 0:45–1:30 | **Giải pháp**: MSB SmartForm AI — nói nhu cầu → Agent giải thích từng trường + ví dụ → thu thập → điền → checklist → PDF → ký số → Zalo. |
| 1:30–2:15 | **Kiến trúc**: 1 container AgentBase + LangGraph guided FSM + RAG + 9 forms + GreenNode LLM. |
| 2:15–4:30 | **Demo live**: UC-2 (FDI bilingual) + UC-5 (upload + ký + Zalo). |
| 4:30–5:30 | **Giá trị**: bảng nỗi đau → giải pháp; FDI bilingual; an toàn bí mật; 9 QC checks. |
| 5:30–6:15 | **Độ tin cậy**: 9 quality check, STATUS READY/MISSING/NEED_REVIEW, Agent không phê duyệt. |
| 6:15–7:00 | **Roadmap**: thêm mẫu PDF thật, memory cross-session, prod pgvector + DR, Zalo production. |

---

## 5. Phân biệt & rủi ro

**Phân biệt:** không phải chatbot trả lời chung chung — là trợ lý nghiệp vụ **chỉ dùng mẫu MSB thật trong KB**, không bịa mẫu, bảo toàn pháp lý, output có cấu trúc 11 mục + checklist. **Guided flow**: giải thích + ví dụ trước khi thu thập. **Bilingual**: FDI song ngữ VI-EN. **End-to-end**: chat → PDF → ký số → Zalo.

**Rủi ro & mitigate:**
- LLM chọn sai mẫu → RAG threshold + fallback "cần MSB xác nhận".
- Khách cung cấp bí mật → reject list ở API.
- Mẫu hết hiệu lực → filter `active=true` + version mới nhất.
- Session conflict → session isolation per persona.
- File upload độc hại → validate format + size + AI authenticity check.
