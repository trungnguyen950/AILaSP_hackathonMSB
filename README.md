# MSB SmartForm AI

Trợ lý AI lập hồ sơ & biểu mẫu khách hàng MSB. Khách mô tả nhu cầu → Agent chọn đúng mẫu MSB → hỏi thông tin thiếu → điền mẫu → kiểm tra → sinh checklist ký/nộp.

## Quick start (local)

### Agent (Python)
```powershell
cd apps\agent
python -m venv venv; venv\Scripts\Activate.ps1
pip install -r requirements.txt
# (optional) cp .env.example .env  và set LLM_API_KEY/LLM_BASE_URL/LLM_MODEL
python main.py          # http://127.0.0.1:8080
```
> Agent chạy được **không cần LLM** (rule-based fallback). Set LLM env để tăng chất lượng phân loại/phrasing.

### Web (Next.js)
```powershell
cd apps\web
npm install
npm run dev             # http://localhost:3000
```

### Docker Compose
```bash
docker compose up --build   # agent :8080, web :3000
```

## Demo flow
1. Mở http://localhost:3000 → chat UI
2. Gõ: `Công ty CP X muốn thêm kế toán vào eBank, kế toán lập lệnh, giám đốc duyệt`
3. Agent hỏi bổ sung → cung cấp: `Nguyễn Văn B | 001098765432 | 0901234567 | b@x.vn | 500000000 | OTP`
4. Agent chọn MSB-EBANK-01, điền, QC → STATUS READY
5. Bấm `SOẠN HỒ SƠ` → checklist + preview

## Deploy (GreenNode AgentBase)
Agent deploy qua skill `/agentbase-wizard` (LangGraph) → `/agentbase-deploy` (build → push CR → runtime). Xem `docs/07-deployment-ops.md`.

## Cấu trúc
```
apps/
  agent/   Python + LangGraph (AgentBase Custom Agent, port 8080, /health)
  web/     Next.js (chat UI, design system, logo kim cương đỏ)
docs/      SAD đầy đủ (00–10) + agent-prompt + assets/logo
knowledge-base/  form-registry + 8 mẫu biểu giả lập (source of truth)
docker-compose.yml
```

## Tài liệu
- Tổng quan: `docs/00-product-overview.md`
- Kiến trúc: `docs/02-architecture.md`
- Use case + pitch: `docs/09-use-cases.md`
- UI/UX + PlantUML: `docs/10-ui-ux-design.md`
- Deploy: `docs/07-deployment-ops.md`

> Dữ liệu khách hàng 100% giả lập. Agent chỉ chuẩn bị hồ sơ — không phê duyệt (quyền thuộc MSB). Không lưu PIN/OTP/private key.
