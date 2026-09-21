# PROMPT — Tạo Pitch Deck Marp cho MSB SmartForm AI

> Copy toàn bộ nội dung dưới đây (từ `---PROMPT START---` đến `---PROMPT END---`) và dán vào Claude.

---PROMPT START---

Bạn là chuyên gia thiết kế Pitch Deck. Hãy tạo **Pitch Deck Marp** cho **MSB SmartForm AI** — MSB AI Hackathon 2026, track AI for Customers.

**Ràng buộc thời gian: 5 phút thuyết trình + 2 phút demo video = 7 phút tổng.** Tối đa **8 slide**, mỗi slide 1 thông điệp, số liệu cụ thể, tiếng Việt có dấu. Tập trung trục **vấn đề → giải pháp → giá trị**.

Xuat raw markdown Marp, không giải thích.

## Frontmatter (dùng chính xác)

```yaml
---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MSB SmartForm AI · AI for Customers · MSB AI Hackathon 2026'
footer: 'Team AI (SP) · 5 phút pitch + 2 phút demo'
style: |
  section { background:#F8FAFC; color:#111827; font-family:'Be Vietnam Pro',Inter,system-ui,sans-serif; padding:48px 56px; }
  h1 { color:#0B1F3A; font-size:30px; margin-bottom:4px; }
  h2 { color:#E30613; font-size:18px; font-weight:700; margin-top:0; }
  h3 { color:#0B1F3A; font-size:16px; }
  table { font-size:13px; width:100%; border-collapse:collapse; }
  th { background:#0B1F3A; color:white; padding:6px 10px; text-align:left; }
  td { padding:6px 10px; border-bottom:1px solid #E5E7EB; }
  .takeaway { background:#E30613; color:white; padding:14px 20px; border-radius:10px; font-size:15px; font-weight:700; margin-top:18px; }
  .kpi { background:#0B1F3A; color:white; border-radius:12px; padding:14px; text-align:center; }
  .kpi .num { font-size:28px; font-weight:800; color:#E30613; }
  .col2 { display:flex; gap:20px; }
  .col2 > div { flex:1; }
  .col3 { display:flex; gap:16px; }
  .col3 > div { flex:1; }
  .card { background:white; border:1px solid #E5E7EB; border-radius:12px; padding:14px; box-shadow:0 1px 3px rgba(11,31,58,.08); }
---
```

## 8 slide (mỗi slide tách bằng `---`, bắt đầu bằng `<!-- SLIDE N -->`)

### SLIDE 1 — Tiêu đề + Đội (30s)
- 💎 **MSB SmartForm AI** — *"One request. The right form. Ready to sign."*
- Mô tả 1 câu: Trợ lý AI lập hồ sơ & biểu mẫu MSB — khách mô tả nhu cầu → Agent tự chọn mẫu, điền form, kiểm tra, xuất PDF, ký số, gửi Zalo.
- **Team AI (SP):**
  - **Trung Nguyễn** — Khối Công nghệ — Full-stack Owner: thiết kế, lập trình, deploy, demo, presenter.
  - **Thanh Tâm** — Khối Ngân hàng Doanh nghiệp — Banking SME: ý tưởng, định hướng nghiệp vụ, đánh giá sản phẩm.

### SLIDE 2 — Vấn đề (45s)
- Khách hàng MSB phải tự tìm **hàng chục mẫu biểu** → nộp sai/thiếu → **trả lại nhiều vòng (~30%)**. RM tốn **45 phút/lượt**. **~850 khách chờ/ngày**.
- Table 2 cột (Pain → Hệ quả), 4 dòng chính:
  - Không biết mẫu nào → trả hồ sơ nhiều lần
  - Mẫu cũ/hết hiệu lực → rủi ro tuân thủ
  - Không rõ ai ký, ký ở đâu → đến quầy mới hỏi lại
  - **FDI cần song ngữ VI-EN → không có mẫu phù hợp**
- `.takeaway`: Mỗi ngày 850 khách đang chờ — vấn đề cấp bách, không nhỏ.

### SLIDE 3 — Giải pháp (60s, dẫn vào demo)
- Pipeline 1 dòng: `mô tả nhu cầu → AI chọn form → giải thích + ví dụ → thu thập → điền → 9 QC checks → checklist → PDF vintage → ký số → Zalo`
- 3 `.card` col3:
  - **Guided FSM 8 bước** — LangGraph: giải thích từng trường + ví dụ trước khi hỏi
  - **KB MSB thật** — RAG chọn mẫu, không hallucinate, luôn dùng mẫu active
  - **End-to-end** — chat → PDF vintage → ký số → Zalo Bot (độc nhất)
- `.takeaway`: Không phải chatbot chung — là Banking Form Copilot.

### SLIDE 4 — Demo (2 phút, slide placeholder)
- Tiêu đề: **🎬 Demo — 2 phút**
- Ghi chú: *[Phát video demo 2 phút: nhấn persona FDI Alpha → Agent giải thích tiếng Anh → điền form → READY → SOẠN HỒ SƠ → tải PDF vintage → trang Ký Số → upload + AI check + vẽ chữ ký → ký → gửi Zalo]*
- 6 persona: CTCP X · TNHH MTV Y · TNHH 2TV Z · DNTN A · FDI Alpha 🌐 · Cá nhân A

### SLIDE 5 — Tác động & Thị trường (45s)
- 3 `.kpi` col3: **28–43 tỷ VND/năm** (AEV) · **310.000 lượt/năm** (quy mô) · **30%→3%** (tỷ lệ trả lại)
- Table gọn:
  | | Hiện tại | Với AI |
  |---|---|---|
  | Thời gian RM/lượt | 45 phút | 10 phút |
  | Tỷ lệ trả lại | ~30% | ~3% |
  | Tiết kiệm/lượt | — | ~140.000 VND |
- 3 segment: 🏞 150K KH doanh nghiệp · 🌐 3K FDI (pain point cao nhất) · 👤 5M cá nhân
- `.takeaway`: AEV kép — giảm chi phí & tăng doanh thu, reach cấp triệu khách.

### SLIDE 6 — Điểm khác biệt (30s)
- Table 2 cột (Chatbot chung vs **SmartForm AI**), 4 dòng:
  - Nguồn mẫu: LLM tự sinh → hallucinate | **KB MSB thật — không bịa**
  - Luồng: Hỏi đáp 1 lần | **Guided FSM 8 bước + 9 QC checks**
  - Song ngữ: Không | **VI-EN cho FDI (duy nhất)**
  - End-to-end: Chat thôi | **Chat → PDF → Ký số → Zalo**
- **Why now:** LLM maturity · AgentBase platform · MSB đẩy số hóa + thu hút FDI
- **Bằng chứng:** 9 mẫu thật · 6 persona · đã deploy · rule-based fallback

### SLIDE 7 — Roadmap (30s)
- 3 `.card` col3:
  - **Phase 1 (0–3T):** Pilot 30 mẫu, 1 BU Doanh nghiệp, 1 container. KPI: ↓50% thời gian.
  - **Phase 2 (3–9T):** 100+ mẫu, memory pgvector, Zalo production. KPI: 200K lượt/năm.
  - **Phase 3 (9–18T):** OCR pre-fill, multi-tenant, API core banking. KPI: AEV full 28–43 tỷ.

### SLIDE 8 — Tổng kết & ASK (15s)
- 3 `.kpi`: **28–43 tỷ VND/năm** · **310K lượt/năm** · **1 câu → hồ sơ ready to sign**
- `.takeaway` (ASK): **Cho phép pilot 3 tháng, 30 mẫu, Khối Doanh nghiệp. Đo AEV thực tế → scale bằng số.**
- Team AI (SP) · MSB AI Hackathon 2026

## Nguyên tắc
1. Mỗi slide = 1 thông điệp. Không nhồi. Dùng table/card/KPI, không list dài.
2. Số liệu cụ thể: 45 phút, 30%, 140K VND, 28 tỷ, 310K, 150K, 9 mẫu, 6 persona.
3. Tiếng Việt có dấu. Brand MSB: #E30613 / #0B1F3A. Font Be Vietnam Pro.
4. Slide 4 là placeholder demo — nội dung ghi chú trong `[...]`, không dày.

---PROMPT END---
