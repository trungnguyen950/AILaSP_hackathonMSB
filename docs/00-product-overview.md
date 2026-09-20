# MSB SmartForm AI — Product Overview

> **Codename:** MSB SmartForm AI
> **Khách hàng:** Ngân hàng TMCP Hàng Hải Việt Nam — MSB
> **Tài liệu:** Tổng quan sản phẩm (mở đầu cho bộ SAD)
> **Phiên bản:** 1.0 (Hackathon baseline — đã deploy lên GreenNode AgentBase)

---

## 1. Tuyên ngôn sản phẩm

**One request. The right form. Ready to sign.**

Thay vì khách hàng phải tự tìm trong hàng chục mẫu biểu MSB, chỉ cần **mô tả nhu cầu bằng ngôn ngữ tự nhiên**, hệ thống tự:

`mô tả nhu cầu → phân tích & chọn form → giải thích từng trường → đưa ví dụ mẫu → thu thập dữ liệu → điền mẫu → kiểm tra logic → chỉ người ký → sinh checklist → xuất PDF → ký số → gửi Zalo`

## 2. Vấn đề đang giải

| Nỗi đau (Pain) | Hệ quả |
|---|---|
| Khách hàng/doanh nghiệp không biết mẫu nào phù hợp nhu cầu | Giao dịch bị trả hồ sơ nhiều lần |
| Mẫu biểu MSB nhiều, phân tán, nhiều phiên bản | Dễ dùng mẫu cũ/hết hiệu lực |
| Trường bắt buộc dễ bỏ sót | Hồ sơ thiếu, MSB phải yêu cầu bổ sung |
| Không rõ ai ký, ký ở đâu, có cần đóng dấu | Khách đến quầy mới bị hỏi lại |
| eBank: cấu trúc Maker/Checker/Approver phức tạp | Phân quyền sai, rủi ro giao dịch |
| Khách FDI cần biểu mẫu song ngữ VI-EN | Không có mẫu phù hợp, phải tự dịch |
| Khách đã điền form nhưng không biết ký số thế nào | Phải lên quầy ký thủ công |

## 3. Giá trị mang lại

- **Khách hàng:** giảm thời gian chuẩn bị hồ sơ, hiểu rõ từng trường, nộp đúng lần đầu.
- **Khách FDI:** biểu mẫu song ngữ VI-EN, hướng dẫn bằng tiếng Anh, quốc tế hóa.
- **MSB (chuyên viên):** giảm thao tác lặp, tập trung vào việc xác nhận & tư vấn.
- **Hackathon:** demo end-to-end hoàn chỉnh: chat → điền form → xuất PDF → ký số → gửi Zalo.

## 4. Personas (6 nhóm khách hàng demo)

| Persona | Mô tả | Ngôn ngữ | Nhu cầu demo |
|---|---|---|---|
| **CTCP X** | Công ty Cổ phần | Tiếng Việt | Thêm kế toán eBank (Maker + Approver) |
| **TNHH MTV Y** | TNHH 1 thành viên | Tiếng Việt | Thay đổi người đại diện pháp luật |
| **TNHH 2TV Z** | TNHH ≥2 thành viên | Tiếng Việt | Thuế điện tử + chữ ký số |
| **DNTN A** | Doanh nghiệp tư nhân | Tiếng Việt | Ủy quyền kế toán eBank |
| **FDI Alpha 🌐** | Doanh nghiệp FDI (vốn đầu tư nước ngoài) | Tiếng Anh (song ngữ VI/EN) | eBank + Maker/Approver, biểu mẫu song ngữ |
| **Cá nhân A** | Khách hàng cá nhân | Tiếng Việt | Đổi SĐT, email & eBank |

> Mỗi persona sử dụng **session độc lập** — chuyển persona tạo session mới, không dính dữ liệu cũ.

## 5. Phạm vi (Scope)

### In scope (v1.0 — Hackathon baseline)

**5 trang web:**
- **💬 Chat (`/`)** — Chat với AI Agent: chọn persona → giải thích form → ví dụ mẫu → thu thập dữ liệu → SOẠN HỒ SƠ → tải Text + PDF
- **📋 Mẫu Biểu Mẫu (`/forms/`)** — Thư viện 9 biểu mẫu: tìm kiếm, lọc, tải Text/PDF, xem trước, AI Fill
- **✍️ Ký Số (`/sign/`)** — Mô phỏng ký số: upload file → AI check → vẽ chữ ký → ký → tải file đã ký → gửi Zalo Bot
- **📊 Dashboard (`/dashboards/`)** — Realtime metrics: System & Performance + BU Impact + BA Analytics (signing funnel, form usage)
- **📖 Hướng dẫn (`/user-guide/`)** — 10 trang hướng dẫn với sidebar, FAQ, demo end-to-end

**Agent (Python + LangGraph):**
- Luồng hội thoại có hướng dẫn (guided flow): giải thích từng trường + ví dụ mẫu trước khi thu thập dữ liệu
- 9 biểu mẫu giả lập (8 tiếng Việt + 1 song ngữ VI-EN cho FDI)
- RAG chọn mẫu + điền trường + 9 quality checks (thêm BILINGUAL FIELD CHECK)
- Hỗ trợ song ngữ: tự phát hiện ngôn ngữ (tiếng Việt có dấu / tiếng Anh)
- 3 cách nhập dữ liệu: pipe-separated, Label: value, chat tự nhiên
- Xuất PDF vintage (thiết kế cổ điển, font tiếng Việt đầy đủ)
- Mock ký chữ ký số (fpdf2 + pypdf)
- AI kiểm tra file upload (authenticity check)
- Zalo Bot: gửi PDF đã ký + thông báo cho khách hàng

### Out of scope (v1.0)
- Gửi hồ sơ điện tử trực tiếp vào core banking MSB (chỉ chuẩn bị hồ sơ).
- Xác nhận/chấp thuận hồ sơ (quyền thuộc MSB).
- OCR tự động từ giấy tờ thật.
- Dữ liệu khách hàng thật (chỉ dữ liệu DEMO).

## 6. Nguyên tắc cốt lõi

1. **Knowledge Base là nguồn chân lý** — Agent không tự bịa mẫu/số hiệu/phiên bản.
2. **Chuẩn bị, không phê duyệt** — Agent chỉ hỗ trợ; quyết định thuộc MSB.
3. **Không lưu bí mật** — PIN/OTP/private key/password/secret không hiển thị, không lưu.
4. **Dữ liệu DEMO** — mọi số liệu khách hàng đều giả lập.
5. **Bảo toàn mẫu MSB** — không sửa logo/mã mẫu/footer/nội dung pháp lý cố định.
6. **Song ngữ** — FDI customers get English instructions; domestic customers get Vietnamese with full diacritics.

## 7. Cấu trúc dự án

```
apps/
  agent/   Python + LangGraph (AgentBase Custom Agent, port 8080, /health)
    src/
      agent.py         — LangGraph FSM: b1→b2→b3→b3a(explain)→b3b(example)→b4→b5-b8
      kb.py            — Knowledge Base loader (parses form-registry.md + form templates)
      rag.py           — Retriever (rule-based + keyword; FDI intent; English keywords)
      form_engine.py   — Fill + validate + render (bilingual labels)
      qc.py            — 9 quality checks (incl. BILINGUAL FIELD CHECK)
      sign_engine.py   — Mock digital signature (PDF + SHA256 + webhook)
      file_engine.py   — File upload validation + AI authenticity check + file signing
      vintage_pdf.py   — PDF vintage generator (classic design, Vietnamese fonts)
      zalo_bot.py      — Zalo Bot integration (send PDF + notification)
      demo_data.py     — 6 demo customers (incl. FDI)
      models.py        — Pydantic models (incl. label_en, is_fdi, bilingual)
    knowledge_base/    — 9 form templates + registry (bundled in container)
  web/     Next.js 14 (static export, 5 routes: / /forms/ /sign/ /dashboards/ /user-guide/)
    app/
      page.tsx              — Chat page (6 personas, guided flow, session isolation)
      forms/page.tsx        — Forms library (9 forms, search, filter, AI Fill)
      sign/page.tsx         — Sign page (upload, AI check, signature pad, Zalo)
      dashboards/page.tsx   — Dashboard (KPI cards, line/bar/donut/funnel charts, realtime)
      user-guide/           — 10-page user guide with sidebar
    components/
      Navbar.tsx            — Shared navbar (5 links: Chat · Forms · Sign · Dashboard · Guide)
      SignaturePad.tsx      — Custom canvas signature pad (no external dep)
      PreviewModal.tsx      — Form preview modal
      StatusBadge.tsx       — READY / MISSING / NEED REVIEW / FORM EXPLAINED
      dashboard/            — KpiCard, LineChart, BarChart, DonutChart, FunnelChart, HorizontalBarChart
      user-guide/           — Sidebar, BlockRenderer, BackToTop
    lib/
      api.ts                — API helpers (invoke, listForms, getForm, signFile, Zalo, etc.)
      useMetrics.ts         — Mock realtime metrics hook (system + BU + BA, updates every 3s)
      guide-content.ts      — User guide content (10 pages, typed blocks)
docs/      SAD đầy đủ (00–10) + user-guide
knowledge-base/  form-registry + 9 mẫu biểu giả lập
docker-compose.yml
```

## 8. Liên kết tài liệu

| # | Tài liệu | Mô tả |
|---|---|---|
| 00 | product-overview.md | (file này) |
| 01 | PRD.md | Yêu cầu chức năng + phi chức năng |
| 02 | architecture.md | SAD: HLA, sơ đồ, tech stack |
| 03 | LLD.md | Low-level design từng module |
| 04 | data-model.md | ER + schema + Form Registry |
| 05 | api-contract.md | REST API contract (/invocations actions) |
| 06 | security.md | Security architecture |
| 07 | deployment-ops.md | Triển khai, CI/CD, observability, DR |
| 08 | ADR.md | Architecture Decision Records |
| 09 | use-cases.md | Use case end-to-end + giá trị + outline pitch 7 phút |
| 10 | ui-ux-design.md | Design system + logo kim cương đỏ + wireframe & luồng |
| — | agent-prompt.md | System prompt của Agent |
| — | user-guide.md | Hướng dẫn khách hàng sử dụng 3 trang |
| — | knowledge-base/ | Form Registry + 9 biểu mẫu giả lập |
