# 04 — Data Model

> MSB SmartForm AI · ER + schema + Form Registry · v0.1

---

## 1. ER Diagram

```mermaid
erDiagram
  CUSTOMER ||--o{ SESSION : has
  SESSION ||--o{ MESSAGE : contains
  SESSION ||--o{ FORM_INSTANCE : produces
  FORM_TEMPLATE ||--o{ FORM_INSTANCE : instantiated_by
  FORM_TEMPLATE }o--|| FORM_REGISTRY : described_by
  CUSTOMER ||--o{ EBANK_USER : owns
  EBANK_USER ||--o{ EBANK_ROLE : has
  CUSTOMER ||--o{ DIGITAL_SIGNATURE : has
  CUSTOMER ||--o{ ETAX_ACCOUNT : has
  SESSION ||--|| AGENT_STATE : tracks
  FORM_INSTANCE ||--|| QC_RESULT : checked_by
  USER_AUTH ||--|| AUDIT_LOG : writes

  CUSTOMER {
    uuid id PK
    string name
    enum type "org|individual"
    enum org_type "CP|TNHH1TV|TNHH2TV|DNTN"
    string tax_id
    string account_no
    string legal_rep
    boolean is_demo
  }
  FORM_REGISTRY {
    string code PK
    string name
    string business_group
    enum segment "KHCN|KHTC"
    string org_type
    string use_case
    string preparer
    string signer
    string accompanying_docs
    string version
    date effective_date
    string source_file
    boolean active
  }
  FORM_TEMPLATE {
    uuid id PK
    string code FK
    string version
    json fields
    json signatories
    json fixed_content
    string layout_ref
  }
  FORM_INSTANCE {
    uuid id PK
    uuid session_id FK
    string code FK
    json field_values
    enum status "draft|filled|ready|missing|need_review"
    timestamp created_at
  }
  SESSION {
    uuid id PK
    uuid customer_id FK
    int current_step
    timestamp created_at
  }
  AGENT_STATE {
    uuid session_id PK
    json state
    string step
  }
  MESSAGE {
    uuid id PK
    uuid session_id FK
    string role
    text content
    timestamp ts
  }
  EBANK_USER {
    uuid id PK
    uuid customer_id FK
    string full_name
    string cccd
    string username
  }
  EBANK_ROLE {
    uuid id PK
    uuid user_id FK
    enum role "Maker|Checker|Approver"
    decimal limit
    string auth_method
  }
  DIGITAL_SIGNATURE {
    uuid id PK
    uuid customer_id FK
    string provider
    string serial
    date valid_from
    date valid_to
  }
  ETAX_ACCOUNT {
    uuid id PK
    uuid customer_id FK
    string tax_id
    string account_no
    string status
  }
  QC_RESULT {
    uuid form_instance_id PK
    json checks
    enum status "READY|MISSING|NEED_REVIEW"
  }
  AUDIT_LOG {
    bigint id PK
    uuid actor_id
    string action
    json detail
    timestamp ts
  }
```

---

## 2. Form Registry — schema & 5 bản ghi giả lập

Bảng chính (đúng cấu trúc yêu cầu):

| Cột | Kiểu | Ghi chú |
|---|---|---|
| Mã mẫu | string PK (code) | vd `MSB-EBANK-01` |
| Tên mẫu | string | |
| Nhóm nghiệp vụ | string | eBank / Thuế điện tử / Chữ ký số / Tài khoản |
| KHCN/KHTC | enum | `KHCN` (cá nhân) / `KHTC` (tổ chức) |
| Loại hình DN | string | Tất cả / CP / TNHH1TV / TNHH2TV / DNTN / Cá nhân |
| Trường hợp sử dụng | text | |
| Người lập | string | |
| Người ký | string | |
| Hồ sơ kèm | text | danh sách |
| Phiên bản | string | |
| Ngày hiệu lực | date | |
| File nguồn | string | path object storage |
| active | bool | đang hiệu lực |

> Dữ liệu 5 bản ghi nằm trong `knowledge-base/form-registry.md`.

---

## 3. Validation rules (DB-level + app-level)

| Trường | Rule |
|---|---|
| `tax_id` | 10 số, check digit MST VN |
| `account_no` | định dạng số TK MSB |
| `cccd` | 12 số |
| `phone` | định dạng ĐT VN (10–11 số, đầu 0) |
| `email` | RFC 5322 |
| `serial` (CTS) | chuỗi, không chứa private key |
| `version` | semver-ish (`2.1`) |
| `effective_date` | ≤ today để `active=true` |

---

## 4. Indexing

- `form_registry(business_group, segment, org_type, active)` — filter RAG.
- `form_registry(code, version DESC)` — chọn phiên bản mới nhất.
- `session(customer_id, created_at DESC)` — history.
- pgvector HNSW trên `form_template.embedding`.

---

## 5. Retention & privacy

- `MESSAGE`, `AGENT_STATE`: bảo lưu theo phiên, purge sau TTL (demo: 7 ngày).
- `AUDIT_LOG`: 12 tháng (mục tiêu).
- Không bảng nào lưu: PIN/OTP/private key/password/secret (reject ở API layer).
- `is_demo=true` cho mọi bản ghi v0.1.
