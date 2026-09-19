# 05 — API Contract

> MSB SmartForm AI · REST + SSE · v0.1
> Base URL: `/api/v1` · Auth: `Authorization: Bearer <JWT>` (OIDC)

---

## 1. Auth

| Method | Path | Mô tả |
|---|---|---|
| POST | `/auth/login` | OIDC redirect / exchange token |
| GET | `/auth/me` | Profile + role |
| POST | `/auth/logout` | Hủy session |

Roles: `customer` · `msb_staff` · `admin`.

---

## 2. Chat & Session

### `POST /sessions`
Tạo phiên mới.
```json
// req
{ "customer_id": "uuid (demo)" }
// resp 201
{ "session_id": "uuid", "current_step": 1 }
```

### `POST /chat`  (Server-Sent Events)
Gửi tin nhắn, stream phản hồi Agent.
```json
// req
{ "session_id": "uuid", "message": "Tôi muốn thêm kế toán vào eBank" }
```
SSE events:
```
event: question     // Agent hỏi bổ sung
data: {"fields":["tax_id","account_no","cccd","role"]}

event: form_selected
data: {"code":"MSB-EBANK-01","version":"2.1","name":"..."}

event: filled
data: {"form_instance_id":"uuid","preview":{...}}

event: qc
data: {"status":"READY","checks":[...]}

event: output
data: { /* 11 mục: A..K */ }

event: done
```

### `GET /sessions/{id}`
Trả state + history.

### `GET /sessions/{id}/messages`
Lịch sử tin nhắn.

---

## 3. Form Registry

| Method | Path | Role | Mô tả |
|---|---|---|---|
| GET | `/forms` | any | List + filter `?segment=&org_type=&group=&active=true` |
| GET | `/forms/{code}` | any | Chi tiết mẫu (phiên bản mới nhất) |
| GET | `/forms/{code}/versions` | any | Lịch sử phiên bản |
| POST | `/admin/forms` | admin | Upload mẫu mới (metadata + template JSON + PDF) |
| PUT | `/admin/forms/{code}` | admin | Cập nhật metadata / `active` |
| POST | `/admin/forms/{code}/versions` | admin | Thêm phiên bản |

`GET /forms` resp:
```json
{
  "items": [
    {
      "code": "MSB-EBANK-01",
      "name": "Đăng ký bổ sung người sử dụng eBank",
      "business_group": "eBank",
      "segment": "KHTC",
      "org_type": "Tất cả",
      "use_case": "Bổ sung người dùng eBank (Maker/Checker/Approver)",
      "preparer": "Chủ tài khoản / Người được ủy quyền",
      "signer": "Người đại diện theo pháp luật",
      "accompanying_docs": ["CCCD","GGĐL","Văn bản ủy quyền"],
      "version": "2.1",
      "effective_date": "2024-06-01",
      "source_file": "s3://forms/MSB-EBANK-01_v2.1.pdf",
      "active": true
    }
  ]
}
```

---

## 4. Form fill / validate / render

### `POST /forms/{code}/fill`
```json
// req
{ "session_id": "uuid", "values": { "company_name":"CÔNG TY CP X", "tax_id":"0101234567" } }
// resp
{ "form_instance_id":"uuid", "filled": { }, "missing": ["account_no","cccd"], "status":"MISSING_INFORMATION" }
```

### `POST /forms/{code}/validate`
```json
// req
{ "form_instance_id":"uuid" }
// resp
{ "violations": [ {"field":"tax_id","msg":"MST phải 10 số"} ], "valid": false }
```

### `POST /forms/{code}/render`
```json
// req
{ "form_instance_id":"uuid", "format":"pdf" }
// resp
{ "url": "https://.../MSB-EBANK-01_filled.pdf", "expires_in": 600 }
```

### `GET /forms/{code}/checklist`
```json
{ "checklist": [
  {"item":"Biểu mẫu MSB-EBANK-01","required":true,"done":true},
  {"item":"CCCD/Hộ chiếu","required":true,"done":false},
  {"item":"Văn bản ủy quyền","required":false,"done":false}
]}
```

---

## 5. Quality check

### `POST /qc/run`
```json
// req
{ "form_instance_id":"uuid" }
// resp
{ "status":"READY",
  "checks": [
    {"name":"FORM CHECK","pass":true},
    {"name":"DATA CHECK","pass":true},
    {"name":"SIGNATURE CHECK","pass":true},
    {"name":"AUTHORITY CHECK","pass":true},
    {"name":"EBANK ROLE CHECK","pass":true},
    {"name":"LIMIT CHECK","pass":true},
    {"name":"MANDATORY FIELD CHECK","pass":false,"detail":["account_no trống"]},
    {"name":"DOCUMENT CONSISTENCY CHECK","pass":true}
  ]}
```

---

## 6. eBank / eTax / Digital Signature (domain helpers)

| Method | Path | Mô tả |
|---|---|---|
| GET | `/customers/{id}/ebank-users` | Danh sách user eBank + role + limit |
| POST | `/customers/{id}/ebank-users` | Thêm user (sinh bảng phân quyền) |
| GET | `/customers/{id}/etax` | Tài khoản thuế điện tử |
| GET | `/customers/{id}/digital-signatures` | Chứng thư số (không trả bí mật) |

---

## 7. Audit

| Method | Path | Role | Mô tả |
|---|---|---|---|
| GET | `/audit?actor=&from=&to=` | admin | Audit log (phân trang) |

---

## 8. Error format
```json
{ "error": { "code": "FORM_NOT_FOUND", "message": "Chưa xác định được mẫu biểu MSB..." } }
```

Mã lỗi: `FORM_NOT_FOUND` · `VALIDATION_FAILED` · `MISSING_REQUIRED` · `UNAUTHORIZED` · `FORBIDDEN` · `SECRET_REJECTED` · `LLM_TIMEOUT`.

---

## 9. OpenAPI
FastAPI tự sinh `/api/v1/openapi.json` + Swagger UI tại `/docs`. File spec sẽ được xuất tại build time (`openapi.yaml`).
