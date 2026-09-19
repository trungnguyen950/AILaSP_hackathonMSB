# msb-smartform-agent

MSB SmartForm AI — Agent (Python + LangGraph). Deploy target: **GreenNode AgentBase Custom Agent runtime**.

## What it does
8-step FSM: nhận diện KH → phân loại nghiệp vụ → RAG chọn mẫu MSB → hỏi thông tin thiếu → điền mẫu → kiểm tra logic → người ký → checklist + QC. KB bundle 8 mẫu biểu giả lập trong container.

## Prerequisites
- Python 3.10+
- GreenNode IAM Service Account (for deploy) — https://iam.console.vngcloud.vn/service-accounts

## Setup (local)
```powershell
python -m venv venv; venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env   # set LLM_API_KEY/LLM_BASE_URL/LLM_MODEL (optional — works without via rule-based fallback)
```

## Run locally
```bash
python main.py    # http://127.0.0.1:8080
```

### Test
```bash
# health
curl http://127.0.0.1:8080/health

# chat
curl -X POST http://127.0.0.1:8080/invocations -H "Content-Type: application/json" \
  -d '{"action":"chat","message":"Công ty CP X muốn thêm kế toán vào eBank, kế toán lập lệnh, giám đốc duyệt"}'

# list forms
curl -X POST http://127.0.0.1:8080/invocations -H "Content-Type: application/json" -d '{"action":"list_forms"}'

# soạn hồ sơ
curl -X POST http://127.0.0.1:8080/invocations -H "Content-Type: application/json" -d '{"action":"soan_ho_so"}'
```

> Headers for session: `-H "X-GreenNode-AgentBase-Session-Id: s1" -H "X-GreenNode-AgentBase-User-Id: u1"`

## Deploy to AgentBase Runtime
Use `/agentbase-wizard` (LangGraph) then `/agentbase-deploy`:
1. `docker build --platform linux/amd64 -t {registryUrl}/{repoName}/msb-smartform-agent:{tag} .`
2. `bash .claude/skills/agentbase/scripts/cr.sh credentials docker-login`
3. `docker push {registryUrl}/{repoName}/msb-smartform-agent:{tag}`
4. `runtime.sh create --name msb-smartform-agent --image <img> --flavor 1x1-general --from-cr --env-file .env --poc true`

See `docs/07-deployment-ops.md` for full pipeline.

## Project structure
- `main.py` — entrypoint (dispatch by action) + /health
- `src/agent.py` — LangGraph FSM 8 bước
- `src/kb.py` — Knowledge Base loader (parses form-registry.md + form templates)
- `src/rag.py` — retriever (rule-based + keyword; prod → pgvector)
- `src/form_engine.py` — fill + validate + render
- `src/qc.py` — 8 quality checks
- `src/models.py` — Pydantic models + state
- `src/demo_data.py` — 5 khách hàng giả lập
- `knowledge_base/` — 8 form templates + registry (bundled)

## Notes
- Works **without LLM** (rule-based fallback) for local testing. Set LLM env vars for enhanced classification/phrasing.
- Never stores PIN/OTP/private key/password (reject list).
- Agent only prepares hồ sơ — never approves (quyền thuộc MSB).
