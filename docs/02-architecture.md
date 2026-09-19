# 02 — Solution Architecture Document (SAD)

> MSB SmartForm AI · HLA + sơ đồ · v0.1

---

## 1. Tổng quan kiến trúc

MSB SmartForm AI là web app 3 lớp: **Frontend (Next.js)** → **Backend API (FastAPI)** → **Agent (LangGraph)** + **Knowledge Base (RAG)** + **Form Engine**. Agent điều phối luồng 8 bước, dùng RAG chọn mẫu từ Form Registry, điền mẫu, chạy quality check, sinh checklist.

```mermaid
flowchart LR
  subgraph Client["Client"]
    U["Khách hàng / MSB staff<br/>(Browser)"]
  end

  subgraph Edge["Edge / API Gateway"]
    GW["API Gateway + Auth (OIDC)"]
  end

  subgraph App["Application Layer"]
    FE["Web Frontend<br/>Next.js"]
    API["Backend API<br/>FastAPI (BFF)"]
  end

  subgraph AgentLayer["Agent Layer"]
    AG["Agent Orchestrator<br/>LangGraph state machine (8 bước)"]
    QC["Quality Check Service<br/>(8 checks)"]
    FE2["Form Engine<br/>fill + validate + render PDF"]
  end

  subgraph KB["Knowledge Base"]
    REG[("Form Registry<br/>PostgreSQL")]
    VEC[("Vector Store<br/>pgvector")]
    DOC[("Object Storage<br/>source PDFs/templates")]
  end

  subgraph State["State"]
    SES[("Session/History<br/>PostgreSQL")]
    AUD[("Audit Log")]
  end

  U --> FE --> GW --> API
  API --> AG --> VEC
  AG --> REG
  AG --> FE2 --> DOC
  AG --> QC
  API --> SES
  AG --> SES
  API --> AUD
  AG --> AUD
```

## 2. Component Diagram

```mermaid
graph TB
  FE["Web Frontend<br/>Chat · Form Preview · Checklist · Admin"]
  API["Backend API (BFF)<br/>REST + SSE/WebSocket"]
  AG["Agent Orchestrator<br/>LangGraph · 8-step FSM"]
  RAG["RAG Retriever<br/>semantic + metadata filter"]
  QC["Quality Check<br/>8 checks"]
  FORM["Form Engine<br/>template fill · validate · PDF"]
  REG["Form Registry CRUD"]
  VEC["Embeddings / Vector"]
  SES["Session Manager"]
  AUTH["AuthN/AuthZ (OIDC, RBAC)"]
  AUD["Audit Logger"]
  LLM["LLM Provider"]

  FE --> API
  API --> AUTH
  API --> SES
  API --> AG
  AG --> LLM
  AG --> RAG
  AG --> FORM
  AG --> QC
  AG --> SES
  RAG --> VEC
  RAG --> REG
  FORM --> REG
  API --> AUD
  AG --> AUD
```

## 3. Tech Stack

| Lớp | Công nghệ | Lý do |
|---|---|---|
| Frontend | Next.js (React) + TypeScript + Tailwind, **static export (SSG)** | Chat UX, host riêng hoặc serve từ container |
| Backend + Agent | FastAPI + **greennode-agentbase SDK** + LangGraph (FSM 8 bước) | 1 container, đúng AgentBase Custom Agent model |
| LLM | **GreenNode AI Platform (MaaS)** OpenAI-compatible | Tích hợp platform, POC credits (ADR-5) |
| Form Registry (demo) | JSON/MD bundle trong container | 8 mẫu nhỏ, không cần DB bên ngoài (ADR-10) |
| Vector Store (demo) | FAISS/Chroma **in-memory** (build lúc boot) | Không cần PG bên ngoài (ADR-3) |
| Session (demo) | SQLite file (ephemeral) | Đủ demo |
| Form Registry (prod) | PostgreSQL + pgvector | Persist, scale (ADR-3/10 prod path) |
| Object Storage (prod) | S3-compatible | Lưu source PDF khi có mẫu thật |
| PDF | WeasyPrint / pdf-lib | Render form đã điền (template JSON → PDF) |
| Auth | OIDC (Keycloak demo) + JWT | RBAC 3 vai trò |
| Container/Deploy | **GreenNode AgentBase runtime** (1 container, port 8080, `/health`) | ADR-4, qua `/agentbase-wizard` + `/agentbase-deploy` |
| Memory | `/agentbase-memory` (optional) | ADR-12 |
| Observability | `/agentbase-monitor` + OpenTelemetry/Prometheus/Grafana (prod) | |
| CI/CD | GitHub Actions | |

## 4. Sequence Diagram — Luồng chính

```mermaid
sequenceDiagram
  autonumber
  actor U as Khách hàng
  participant FE as Frontend
  participant API as Backend API
  participant AG as Agent (LangGraph)
  participant RAG as RAG
  participant FORM as Form Engine
  participant QC as Quality Check
  participant DB as DB/Vector

  U->>FE: "Tôi muốn thêm kế toán vào eBank"
  FE->>API: POST /chat {message, sessionId}
  API->>AG: run(state, message)
  AG->>AG: B1 nhận diện KH (từ session/profile)
  AG->>AG: B2 phân loại nghiệp vụ → EBANK+USER+AUTHORIZATION
  AG->>RAG: retrieve(ngữ nghĩa + filter KHTC)
  RAG->>DB: vector search + metadata
  DB-->>RAG: MSB-EBANK-01 (v2.1, hiệu lực)
  RAG-->>AG: mẫu + metadata
  AG->>AG: B4 xác định trường thiếu
  AG-->>API: hỏi bổ sung (SSE)
  API-->>FE: "cần MST, TK, họ tên, CCCD, vai trò..."
  FE-->>U: hiển thị câu hỏi
  U->>FE: cung cấp thông tin
  FE->>API: POST /chat {answers}
  API->>AG: resume(state, answers)
  AG->>FORM: fill(MSB-EBANK-01, values)
  FORM-->>AG: form đã điền + [CHƯA CÓ...]
  AG->>QC: run 8 checks
  QC-->>AG: STATUS=READY/MISSING/NEED_REVIEW
  AG->>AG: B7 người ký · B8 checklist
  AG-->>API: output chuẩn 11 mục
  API-->>FE: render preview + checklist
  FE-->>U: xem trước + tải PDF + checklist
```

## 5. Data Flow Diagram (DFD)

```mermaid
flowchart LR
  REQ["Yêu cầu KH<br/>(free-text)"] --> AG
  AG["Agent"] -->|query| VEC["Vector Store"]
  VEC -->|top-k mẫu| AG
  AG -->|filter| REG["Form Registry"]
  REG -->|metadata + fields| AG
  AG -->|values| FORM["Form Engine"]
  FORM -->|filled form| AG
  AG --> QC["Quality Check"]
  QC -->|status| AG
  AG -->|output 11 mục| OUT["Hồ sơ + Checklist + PDF"]
  DOC["Object Storage"] -->|template/PDF| FORM
  FORM -->|rendered PDF| OUT
```

## 6. Deployment Diagram

```mermaid
flowchart TB
  subgraph Browser["Browser"]
    FE["Next.js Static Export<br/>(host riêng hoặc trong container)"]
  end

  subgraph AgentBase["GreenNode AgentBase Runtime (1 container, port 8080)"]
    APP["FastAPI + greennode-agentbase SDK<br/>GET /health"]
    AG["LangGraph Agent (8 bước)"]
    RAG["RAG in-memory"]
    KB["KB bundle (8 forms + registry)"]
    FORM["Form Engine"]
    QC["Quality Check"]
    SES["SQLite session"]
  end

  subgraph Ext["External"]
    LLM["GreenNode AI Platform (MaaS)"]
    MEM["/agentbase-memory (optional)"]
  end

  FE --> APP
  APP --> AG
  AG --> RAG --> KB
  AG --> FORM --> KB
  AG --> QC
  APP --> SES
  AG --> LLM
  AG -.-> MEM
```

## 7. Network Topology (logical)

```mermaid
flowchart LR
  Internet(("Internet")) --> WAF["WAF"]
  WAF --> LB["Load Balancer / Ingress"]
  LB --> FE["Frontend (public)"]
  LB --> API["API (private)"]
  API --> AG["Agent (private)"]
  AG --> DB[("DB (private)")]
  AG --> OBJ[("Object Storage (private)")]
  AG --> LLM["LLM (egress, allowlist)"]
  API --> OIDC["IdP"]
```

## 8. Scalability strategy

- API & Agent **stateless** → scale ngang theo số pod (AgentBase autoscale min/max replicas).
- Demo: KB bundle in-container, vector in-memory, SQLite session → **không có DB round-trip**, RAG trên 8 mẫu < 1ms.
- Bottleneck duy nhất = **LLM latency** → streaming (SSE) + small model cho phân loại nhẹ.
- Prod: pgvector HNSW + cache embedding; Form Registry index; session chuyển Redis/PG.

> **Về thắc mắc latency PostgreSQL:** ở demo không dùng PG (KB in-memory), nên query gần như tức thì. Khi lên prod với pgvector + vài trăm mẫu, HNSW index vẫn < 10ms. Độ trễ người dùng cảm nhận chủ yếu từ LLM (đã stream), không từ DB.

## 9. Single point of failure & mitigations

| SPOF risk | Mitigation |
|---|---|
| LLM provider down | Fallback model + graceful degrade (chỉ tra mẫu, không điền) |
| DB down | Replica read + HA primary (prod) |
| Vector index slow | HNSW + cache; reindex offline |

## 10. Tham chiếu
- PRD: `01-PRD.md` · LLD: `03-LLD.md` · Data: `04-data-model.md` · API: `05-api-contract.md` · Security: `06-security.md` · Ops: `07-deployment-ops.md` · ADR: `08-ADR.md`
