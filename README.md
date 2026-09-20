# MSB SmartForm AI

> **One request. The right form. Ready to sign.**

Trợ lý AI lập hồ sơ & biểu mẫu khách hàng MSB. Khách mô tả nhu cầu bằng ngôn ngữ tự nhiên → Agent chọn đúng mẫu MSB → giải thích từng trường + ví dụ → hỏi thông tin thiếu → điền mẫu → kiểm tra 9 bước → sinh checklist → xuất PDF → ký số → gửi Zalo Bot.

---

## 🌐 Links

| Resource | URL |
|---|---|
| **GreenNode AgentBase Endpoint** | https://endpoint-f1ef0f3c-da52-4977-8b6e-e096c3af9588.agentbase-runtime.aiplatform.vngcloud.vn |
| **Health check** | `GET /health` → 200 ✅ |
| **Zalo Bot (mời & lấy chat_id)** | https://bot.zaloplatforms.com/groups/invite/bot.NZSPzvFP |
| **Web UI (sau deploy)** | serve từ cùng container AgentBase, route `/` |
| **API contract** | `POST /invocations` (xem `docs/05-api-contract.md`) |

> **Zalo Bot:** Nhấn link invite → bot tham gia Zalo → nhắn bất kỳ → bot phản hồi kèm `chat_id` → dán `chat_id` vào trang Ký Số để gửi PDF đã ký cho khách hàng.

---

## 🚀 Quick start (local)

### Agent (Python)
```bash
cd apps/agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# (optional) cp .env.example .env  và set LLM_API_KEY/LLM_BASE_URL/LLM_MODEL
python main.py          # http://127.0.0.1:8080
```
> Agent chạy được **không cần LLM** (rule-based fallback). Set LLM env để tăng chất lượng phân loại/phrasing.

### Web (Next.js)
```bash
cd apps/web
npm install
npm run dev             # http://localhost:3000
```

### Docker Compose
```bash
docker compose up --build   # agent :8080, web :3000
```

---

## 🎯 Demo flow

1. Mở http://localhost:3000 → chat UI (6 persona)
2. Nhấn thẻ **"CTCP X"** → Agent tự gửi prompt
3. Gõ: `sẵn sàng` → Agent hỏi 7 trường thiếu
4. Nhập: `Nguyễn Văn B | 001098765432 | 0901234567 | b@x.vn | 500000000 | OTP`
5. Agent chọn MSB-EBANK-01, điền, 9 QC checks → STATUS READY
6. Bấm `SOẠN HỒ SƠ` → checklist + PDF vintage
7. Trang **Ký Số** → upload file → AI check → vẽ chữ ký → ký → gửi Zalo Bot

---

## 📊 Dashboard Điều hành Hồ sơ

Dashboard business KPI realtime cho **quản lý ngân hàng** (Phó TGĐ, Trưởng BU, Quản lý RM) — cập nhật mỗi 3 giây.

**9 nhóm chỉ số:**
1. KPI Tổng quan (tổng hồ sơ, % nộp đúng lần đầu, thời gian xử lý TB, tỷ lệ trả lại)
2. Giá trị kinh doanh AEV (tiết kiệm luỹ kế, AEV dự kiến/năm)
3. Trạng thái hồ sơ (READY / MISSING / NEED REVIEW)
4. Xu hướng realtime (phiên active, thời gian xử lý)
5. Phân khúc khách hàng (Doanh nghiệp / FDI / Cá nhân)
6. Phễu ký & Nguồn form (Form Selected → Signed)
7. Top 9 form dùng nhiều + Daily Sign Trend 14 ngày
8. Hiệu suất chuyên viên RM (top 5)
9. Khách hàng & FDI (NPS, CSAT, KH quay lại, FDI đã phục vụ)

> Charts 100% SVG thuần — zero external dependency. Dễ thay mock data bằng API thật (MSB data warehouse, Core Banking, CRM).

---

## ☁️ Deploy (GreenNode AgentBase)

Agent deploy qua skill `/agentbase-wizard` (LangGraph) → `/agentbase-deploy` (build → push CR → runtime). Xem `docs/07-deployment-ops.md`.

**Runtime hiện tại:**
- Name: `msb-smartform-agent`
- Status: `ACTIVE`
- Flavor: `1x1-general`
- Endpoint: xem bảng Links phía trên
- LLM: GreenNode AI Platform (MaaS) — `z-ai/glm-5.2-hackathon`

---

## 📁 Cấu trúc

```
apps/
  agent/   Python + LangGraph (AgentBase Custom Agent, port 8080, /health)
    src/         agent.py, kb.py, rag.py, form_engine.py, qc.py, sign_engine.py,
                 file_engine.py, vintage_pdf.py, zalo_bot.py, demo_data.py
    knowledge_base/  9 form templates + registry (bundled in container)
  web/     Next.js 14 (static export, 5 routes, design system, logo kim cương đỏ)
    app/         page.tsx (Chat), forms/, sign/, dashboards/, user-guide/
    components/  Navbar, SignaturePad, dashboard/ (6 SVG charts), user-guide/
    lib/         api.ts, useMetrics.ts, guide-content.ts
docs/      SAD đầy đủ (00–11) + agent-prompt + user-guide + assets/logo
knowledge-base/  form-registry + 9 mẫu biểu giả lập (source of truth)
docker-compose.yml
```

---

## 📖 Tài liệu

| # | File | Mô tả |
|---|---|---|
| 00 | `docs/00-product-overview.md` | Tổng quan sản phẩm |
| 01 | `docs/01-PRD.md` | Yêu cầu chức năng + phi chức năng |
| 02 | `docs/02-architecture.md` | SAD: HLA, sơ đồ, tech stack |
| 07 | `docs/07-deployment-ops.md` | Triển khai, CI/CD, observability |
| 09 | `docs/09-use-cases.md` | Use case end-to-end + pitch 7 phút |
| 10 | `docs/10-ui-ux-design.md` | Design system + wireframe |
| 11 | `docs/11-pitch-slides-bonus.marp.md` | 4 slide pitch bổ sung (Marp) |
| — | `docs/PROMPT-redesign-dashboard.md` | Prompt redesign dashboard business |
| — | `docs/SUMMARY-for-Deputy-GM.md` | Tóm tắt cho Phó TGĐ (≤300 từ) |

---

## 👥 Contributors

| Tên | Vai trò | Liên hệ |
|---|---|---|
| **Nguyen Quang Trung** | Product Owner (PO) | MSB SmartForm AI — Hackathon AI 2026 |

**Links:**
- 🌐 GreenNode AgentBase Endpoint: https://endpoint-f1ef0f3c-da52-4977-8b6e-e096c3af9588.agentbase-runtime.aiplatform.vngcloud.vn
- 💬 Zalo Bot (invite & lấy chat_id): https://bot.zaloplatforms.com/groups/invite/bot.NZSPzvFP

---

> ⚠️ Dữ liệu khách hàng 100% giả lập. Agent chỉ chuẩn bị hồ sơ — không phê duyệt (quyền thuộc MSB). Không lưu PIN/OTP/private key.
