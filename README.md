# MSB SmartForm AI

> **One request. The right form. Ready to sign.**

Trợ lý AI lập hồ sơ & biểu mẫu khách hàng MSB. Khách mô tả nhu cầu bằng ngôn ngữ tự nhiên → Agent chọn đúng mẫu → điền → kiểm tra → sinh checklist → PDF → ký số → Zalo.

---

## 🌐 Links

| Resource | URL |
|---|---|
| **Live Demo** | https://endpoint-f1ef0f3c-da52-4977-8b6e-e096c3af9588.agentbase-runtime.aiplatform.vngcloud.vn |
| **Zalo Bot** | https://bot.zaloplatforms.com/groups/invite/bot.NZSPzvFP |

---

## 🚀 Quick Start

### Agent (Python)
```bash
cd apps/agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py          # http://127.0.0.1:8080
```

### Web (Next.js)
```bash
cd apps/web
npm install
npm run dev             # http://localhost:3000
```

### Docker
```bash
docker compose up --build   # agent :8080, web :3000
```

---

## 📁 Cấu trúc

```
apps/
  agent/   Python + LangGraph (port 8080)
  web/     Next.js 14 (chat UI, dashboard, forms, sign)
knowledge-base/  form-registry + 9 mẫu biểu mẫu
docker-compose.yml
```

---

## 👥 Contributor

| Tên | Vai trò |
|---|---|
| **Nguyen Quang Trung** | Product Owner |

---

> ⚠️ Dữ liệu khách hàng 100% giả lập. Agent chỉ chuẩn bị hồ sơ — không phê duyệt.
