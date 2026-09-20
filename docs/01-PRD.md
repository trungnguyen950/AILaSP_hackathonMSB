# 01 — Product Requirements Document (PRD)

> MSB SmartForm AI · v1.0 (Hackathon baseline — đã deploy)

---

## 1. Yêu cầu chức năng (FR)

### FR-1 Nhận diện khách hàng
- **FR-1.1** Hệ thống xác định khách hàng là cá nhân hay tổ chức, loại hình tổ chức (CP / TNHH 1TV / TNHH 2TV+ / DNTN / FDI).
- **FR-1.2** Hệ thống lưu profile khách hàng DEMO theo phiên (session). Mỗi persona dùng session độc lập.
- **FR-1.3** FDI customer: tự phát hiện quốc tịch người đại diện → chuyển sang hướng dẫn tiếng Anh.

### FR-2 Nhận diện nhu cầu bằng ngôn ngữ tự nhiên
- **FR-2.1** Khách nhập yêu cầu free-text → Agent phân loại thành 1 hoặc nhiều nghiệp vụ. Thêm intent `FDI` với 14 từ khóa tiếng Anh (foreign, bilingual, passport, ERC, IRC, investment...).
- **FR-2.2** Một câu có thể tách thành nhiều nghiệp vụ (vd: thêm người dùng + gán quyền + đặt hạn mức).

### FR-3 Form Registry & chọn mẫu
- **FR-3.1** Hệ thống duy trì Form Registry với 9 biểu mẫu (8 tiếng Việt + 1 song ngữ VI-EN cho FDI).
- **FR-3.2** Agent tra Knowledge Base (RAG) để chọn mẫu phù hợp; ưu tiên mẫu đang hiệu lực, phiên bản mới nhất. FDI customers → ưu tiên form bilingual (+8 score).
- **FR-3.3** Agent không tự đặt tên/số hiệu/phiên bản mẫu không tồn tại.

### FR-4 Luồng hội thoại có hướng dẫn (Guided Flow)
- **FR-4.1** Agent giải thích form trước khi thu thập dữ liệu: tên mẫu, mục đích, từng trường kèm hướng dẫn (lấy ở đâu, định dạng, ví dụ).
- **FR-4.2** Agent đưa mẫu giả lập (DEMO) với dữ liệu demo điền sẵn, kèm gợi ý nhập.
- **FR-4.3** Chỉ khi khách hàng nói "sẵn sàng" (hoặc "ready", "ok") hoặc cung cấp dữ liệu, Agent mới chuyển sang thu thập.
- **FR-4.4** Nếu khách hỏi thêm → Agent re-explain với ví dụ điền nhanh (demo values từ session).

### FR-5 Thu thập thông tin còn thiếu
- **FR-5.1** Agent chỉ hỏi các trường bắt buộc còn thiếu, không hỏi lại thông tin đã có.
- **FR-5.2** Hỗ trợ 3 cách nhập:
  - **Pipe-separated:** `giátrị1 | giátrị2 | giátrị3`
  - **Label: value:** `Nhãn: giá trị` mỗi dòng (fuzzy match bằng normalized label)
  - **Chat tự nhiên:** regex extraction (CCCD 12 số, MST 10 số, phone, email, role, date)
- **FR-5.3** FDI customers: câu hỏi và nhãn trường bằng tiếng Anh.

### FR-6 Điền & kiểm tra biểu mẫu
- **FR-6.1** Agent điền các trường có dữ liệu, giữ nguyên bố cục/logo/mã mẫu/footer/nội dung pháp lý cố định.
- **FR-6.2** Kiểm tra logic: MST, CCCD, số TK, ĐT, email, vai trò, hạn mức, phương thức phê duyệt.

### FR-7 Xác định người ký
- **FR-7.1** Chỉ rõ: người cần ký, chức danh, vị trí ký, có cần đóng dấu.

### FR-8 Checklist nộp hồ sơ
- **FR-8.1** Sinh checklist: biểu mẫu, hồ sơ pháp lý kèm, CCCD/HC, văn bản ủy quyền.

### FR-9 Module eBank
- **FR-9.1** Hỗ trợ cấu trúc: 1 người, 2 người (Maker→Approver), 3 người (Maker→Checker→Approver), N cấp.
- **FR-9.2** Sinh bảng phân quyền: `Người dùng | Chức danh | User | Vai trò | Hạn mức | Xác thực`.

### FR-10 Module FDI (Song ngữ)
- **FR-10.1** Form MSB-EBANK-01-FDI: 16 trường song ngữ VI-EN (label + label_en).
- **FR-10.2** Trường FDI-specific: company_name_en, legal_rep_nationality, legal_rep_passport.
- **FR-10.3** Yêu cầu ERC (Giấy chứng nhận ĐKDN) + IRC (Giấy chứng nhận ĐK đầu tư).

### FR-11 Output chuẩn (11 mục + L_bilingual)
Mỗi trả lời có cấu trúc: A. Nhu cầu · B. Loại KH · C. Nghiệp vụ · D. Mẫu biểu · E. Thông tin đã có · F. Thông tin còn thiếu · G. Biểu mẫu đã điền · H. Người cần ký · I. Hồ sơ kèm · J. Checklist · K. Cảnh báo · **L. Bilingual info** (nếu FDI).

### FR-12 Chế độ "SOẠN HỒ SƠ"
- **FR-12.1** Khi người dùng nhấn nút SOẠN HỒ SƠ: đóng gói checklist + bản mềm (.txt) + PDF vintage.

### FR-13 Quality control (9 checks)
- **FR-13.1** 9 check: FORM, DATA, SIGNATURE, AUTHORITY, EBANK ROLE, LIMIT, MANDATORY FIELD, DOCUMENT CONSISTENCY, **BILINGUAL FIELD CHECK** (FDI).
- **FR-13.2** Trả `STATUS: READY | MISSING INFORMATION | NEED MSB REVIEW`.

### FR-14 Thư viện biểu mẫu (`/forms/`)
- **FR-14.1** Grid 3 cột responsive, search bar, filter by category.
- **FR-14.2** Mỗi form có 4 nút: Download Text, Download PDF, Xem Trước (modal), AI Fill.
- **FR-14.3** AI Fill: chuyển sang trang Chat, không pre-fill demo data, hỏi tất cả trường bắt buộc.

### FR-15 Ký chữ ký số (`/sign/`)
- **FR-15.1** Signature pad: custom canvas (mouse + touch), không dùng external library.
- **FR-15.2** Upload file (.txt/.pdf, max 5MB) → AI kiểm tra authenticity (score/100) → ký số.
- **FR-15.3** Ký PDF tạo sẵn từ form (không cần upload).
- **FR-15.4** Tạo SHA256 hash + webhook notification cho AI Agent.
- **FR-15.5** Xuất PDF vintage (thiết kế cổ điển, font tiếng Việt).

### FR-16 Zalo Bot
- **FR-16.1** Gửi PDF đã ký + thông báo cho khách hàng qua Zalo Bot.
- **FR-16.2** Webhook endpoint `/zalo-webhook` nhận message từ user, auto-respond với chat_id.
- **FR-16.3** Quản lý: getMe, setWebhook, getWebhookInfo, listChats, sendMessage.

### FR-17 Trang hướng dẫn (`/user-guide/`)
- **FR-17.1** 9 trang hướng dẫn với sidebar navigation, block renderer, back-to-top.
- **FR-17.2** Nội dung: giới thiệu, chat overview + flow, forms overview + AI Fill, sign upload + generated, dashboard overview, demo end-to-end, FAQ.

### FR-18 Session isolation
- **FR-18.1** Mỗi persona click → sinh session ID riêng (persona-{timestamp}).
- **FR-18.2** Nút "Xoá thông tin cũ, thực hiện lại" → reset session + clear UI.
- **FR-18.3** AI Fill từ /forms → session riêng, không pre-fill demo data (skip_customer_default flag).

### FR-19 Dashboard (`/dashboards/`)
- **FR-19.1** System & Performance Metrics: API Response Time, Error Rate, Page Load Time, Active Users (realtime).
- **FR-19.2** BU Impact Metrics: Conversion Rate, Avg Engagement, Task Success Rate, Retention Rate.
- **FR-19.3** BA Analytics: Signing Funnel (Form Selected → Data Collected → QC Passed → Signed), Form Usage by Source (Chat vs Forms page), Most Used Forms (top 9), Daily Sign Trend (14 days).
- **FR-19.4** Charts: Line chart (realtime), Bar chart (BU impact + daily trend), Donut chart (error/success + form source), Funnel chart (signing journey), Horizontal bar chart (form ranking).
- **FR-19.5** KPI Cards: 8 system/BU cards + 4 BA cards, color-coded with trend arrows.
- **FR-19.6** Mock realtime data: cập nhật mỗi 3 giây, cấu trúc hook `useMetrics()` tách biệt dễ thay API thật.
- **FR-19.7** Charts 100% SVG thuần — zero external dependency, tương thích static export.

### FR-20 Web app
- **FR-20.1** 5 routes: `/` (Chat), `/forms/` (Mẫu Biểu Mẫu), `/sign/` (Ký Số), `/dashboards/` (Dashboard), `/user-guide/` (Hướng dẫn).
- **FR-20.2** Navbar chung: 💬 Chat · 📋 Mẫu Biểu Mẫu · ✍️ Ký Số · 📊 Dashboard · 📖 Hướng dẫn.
- **FR-20.3** Static export (SSG), serve từ cùng container với agent.

---

## 2. Yêu cầu phi chức năng (NFR)

| ID | Nhóm | Yêu cầu | Mục tiêu v1.0 |
|---|---|---|---|
| NFR-1 | Hiệu năng | Độ trễ phản hồi Agent | P95 < 6s / lượt |
| NFR-2 | Hiệu năng | Tra Form Registry | < 1ms (in-memory) |
| NFR-3 | Throughput | Số phiên đồng thời | 50 phiên (demo) |
| NFR-4 | Bảo mật | Không lưu bí mật | PIN/OTP/key/password — reject ở đầu vào |
| NFR-5 | i18n | Ngôn ngữ | Tiếng Việt (có dấu) + Tiếng Anh (FDI) |
| NFR-6 | Dữ liệu | DEMO only | Không dữ liệu KH thật |
| NFR-7 | Khả mở rộng | Thêm mẫu mới | Via admin, không deploy lại agent |
| NFR-8 | Deploy | GreenNode AgentBase | 1 container, port 8080, /health |

---

## 3. Acceptance criteria (mốc demo)

1. Nhấn "CTCP X" → Agent giải thích MSB-EBANK-01 bằng tiếng Việt có dấu → "sẵn sàng" → điền → READY.
2. Nhấn "FDI Alpha 🌐" → Agent giải thích MSB-EBANK-01-FDI bằng tiếng Anh → "ready" → điền → READY (bilingual output).
3. Nhấn persona khác → session mới, không dính form cũ.
4. `/forms/` → 9 forms, nhấn AI Fill → chuyển sang Chat, hỏi tất cả trường (no pre-fill).
5. `/sign/` → upload .txt → AI check ✅ → vẽ chữ ký → ký → tải file đã ký.
6. SOẠN HỒ SƠ → checklist + bản mềm .txt + PDF vintage.
7. 9 quality check chạy và trả STATUS đúng.
8. Nút "Xoá thông tin cũ" → reset session + clear UI.
9. Gửi Zalo Bot → khách hàng nhận PDF + thông báo.
10. `/user-guide/` → 9 trang hướng dẫn đầy đủ.
