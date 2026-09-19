# 08 — Architecture Decision Records (ADR)

> MSB SmartForm AI · v0.1

Format: **Context · Decision · Alternatives · Trade-off · Status**

---

## ADR-1 — Monorepo, 3 service tách biệt

- **Context:** Web + API + Agent cùng repo nhưng deploy độc lập.
- **Decision:** Monorepo với `apps/web`, `apps/api`, `apps/agent`; shared `packages/` (types, schema).
- **Alternatives:** Polyrepo (khó đồng bộ schema); Monolith (khó scale Agent riêng).
- **Trade-off:** Đơn giản dev vs cần CI per service.
- **Status:** Proposed

## ADR-2 — Agent dùng LangGraph state machine

- **Context:** Luồng 8 bước có trạng thái, có wait (hỏi khách), có rẽ nhánh.
- **Decision:** LangGraph FSM, state lưu PostgreSQL.
- **Alternatives:** LangChain chain tuyến tính (khó wait/branch); raw LLM loop (khó kiểm soát).
- **Trade-off:** Phụ thuộc LangGraph vs kiểm soát luồng rõ ràng.
- **Status:** Proposed

## ADR-3 — Vector store: in-memory (demo) → pgvector (prod)

- **Context:** Cần RAG. AgentBase runtime = 1 container; demo chỉ 8 mẫu.
- **Decision:** Demo dùng vector store **in-memory** (FAISS/Chroma) build lúc boot từ KB bundle trong container → không cần DB bên ngoài. Prod path → pgvector trên managed PostgreSQL.
- **Alternatives:** pgvector ngay từ đầu (thêm 1 managed DB + kết nối VPC, phức tạp demo); Qdrant managed (thêm service + egress).
- **Trade-off:** In-memory reindex mỗi boot (8 mẫu < 1s, OK) vs không persist vector (chấp nhận demo). Prod cần pgvector để persist + scale.
- **Status:** Accepted (demo) · Proposed (prod path)

## ADR-4 — Deployment: GreenNode AgentBase Custom Agent runtime (1 container)

- **Context:** Ràng buộc dùng skill GreenNode để deploy. AgentBase Custom Agent = 1 container Python (port 8080, `/health`).
- **Decision:** Gộp Backend + Agent + Form Engine + RAG + QC + KB bundle vào **1 Docker image**, deploy qua `/agentbase-wizard` → `/agentbase-deploy` (build → push managed CR → `runtime.sh create --from-cr`). Frontend = Next.js static export host riêng (hoặc serve từ cùng container).
- **Alternatives:** K8s multi-service (phức tạp, không cần cho demo); OpenClaw (template chatbot Telegram/Zalo — không phải web app tùy biến); VNG Cloud vServer tay.
- **Trade-off:** 1 container đơn giản, đúng model AgentBase vs phải bundle mọi thứ (OK vì demo nhỏ). Prod có thể tách DB ra managed.
- **Status:** Accepted

## ADR-5 — LLM: GreenNode AI Platform (MaaS), OpenAI-compatible

- **Context:** Skill AgentBase khuyến nghị GreenNode AIP; OpenAI-compatible, tích hợp platform, unified billing.
- **Decision:** Dùng GreenNode AIP endpoint `https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1`; API key qua `/agentbase-llm`; model chọn từ `models list` (`modelStatus=ENABLED`). Env `LLM_API_KEY/LLM_BASE_URL/LLM_MODEL`.
- **Alternatives:** OpenAI/Gemini trực tiếp (cần account riêng, egress); OSS self-host (chi phí compute).
- **Trade-off:** Tích hợp chặt + POC credits vs phụ thuộc 1 provider (chấp nhận).
- **Status:** Accepted

## ADR-6 — Form template = JSON schema + layout PDF reference

- **Context:** Cần điền trường + render giữ bố cục MSB.
- **Decision:** Template JSON (fields, signatories, fixed_content) + `layout_ref` trỏ PDF/template trong object storage; render map field→vị trí.
- **Alternatives:** Pure PDF form (AcroForm) — phụ thuộc tool, khó version; HTML-only — mất bố cục MSB.
- **Trade-off:** Cần mapping vị trí vs bảo toàn bố cục gốc.
- **Status:** Proposed — **cần xác nhận có PDF gốc thật hay chỉ mock.**

## ADR-7 — Không lưu bí mật, reject ở API layer

- **Context:** NFR-5 + nguyên tắc an toàn.
- **Decision:** Middleware quét reject list trước khi vào Agent; PII mask trong log.
- **Alternatives:** Encrypt & store (rủi ro + không cần thiết cho demo).
- **Trade-off:** Mất khả năng "tiếp tục" nếu khách cung cấp bí mật (đúng theo thiết kế).
- **Status:** Accepted

## ADR-8 — Agent không phê duyệt hồ sơ

- **Context:** Quyết định chấp nhận thuộc MSB.
- **Decision:** Output luôn có mục K "điểm cần MSB xác nhận"; STATUS tối đa `READY` (sẵn sàng nộp), không `APPROVED`.
- **Alternatives:** Auto-approve (rủi ro pháp lý + sai scope).
- **Trade-off:** Khách vẫn phải qua MSB (đúng quy trình).
- **Status:** Accepted

## ADR-9 — i18n: Tiếng Việt primary

- **Context:** Khách hàng MSB dùng tiếng Việt.
- **Decision:** UI + Agent output tiếng Việt; label EN optional (mục tiêu).
- **Alternatives:** Song ngữ ngay (tăng scope).
- **Trade-off:** Tập trung demo vs chuẩn hóa i18n sau.
- **Status:** Proposed

## ADR-10 — Knowledge Base bundle trong container (demo)

- **Context:** 8 form template nhỏ; AgentBase = 1 container; tránh DB bên ngoài cho demo.
- **Decision:** Bundle `knowledge-base/` (form-registry + 8 template JSON/MD) vào image; nạp + index in-memory lúc startup. Session = SQLite file (ephemeral).
- **Alternatives:** Managed PG ngay (phức tạp deploy demo); gọi API form service riêng (thêm service).
- **Trade-off:** Update mẫu = rebuild image (OK demo, admin upload là prod path) vs deploy cực đơn giản.
- **Status:** Accepted (demo) · Prod: tách sang Form Registry service + managed PG.

## ADR-11 — Frontend: Next.js static export, host riêng

- **Context:** AgentBase runtime chạy backend Python; frontend cần host riêng hoặc serve static.
- **Decision:** Next.js static export (SSG) host trên static host (Vercel/Netlify) gọi endpoint runtime. Fallback: serve static từ chính FastAPI container (1 deploy).
- **Alternatives:** Next.js SSR (cần Node runtime riêng); SPA thuần (mất SEO, không cần cho demo).
- **Trade-off:** 2 host vs tách rõ FE/BE; fallback 1 host cho demo tối giản.
- **Status:** Accepted

## ADR-12 — Memory: optional qua `/agentbase-memory`

- **Context:** Agent có luồng 8 bước + có thể cần nhớ phiên trước.
- **Context:** AgentBase hỗ trợ memory (short-term checkpointer + long-term semantic) qua `/agentbase-memory`; LangGraph tích hợp `AgentBaseMemoryEvents` làm checkpointer.
- **Decision:** v0.1 dùng session SQLite (đủ demo). Bật `/agentbase-memory` khi cần tiếp tục hồ sơ dở dang qua phiên.
- **Trade-off:** Đơn giản demo vs memory platform khi cần persistence cross-session.
- **Status:** Proposed (bật khi cần)
