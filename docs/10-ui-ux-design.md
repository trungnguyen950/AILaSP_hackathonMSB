# 10 — UI/UX Design

> MSB SmartForm AI · Design system + wireframe (PlantUML salt) + luồng (PlantUML) · v0.1
> Logo: **kim cương đỏ** (giữ tinh chất hàng hải của MSB) — xem `docs/assets/logo-diamond.svg`

---

## 1. Nguyên tắc thiết kế

| Nguyên tắc | Áp dụng |
|---|---|
| **Conversation-first** | Chat là trung tâm; mọi nghiệp vụ giải qua 1 luồng hội thoại |
| **Progressive disclosure** | Chỉ hỏi trường thiếu; 8 bước rút gọn thành 1 thanh tiến trình |
| **Trust & compliance** | Logo MSB, mã mẫu/phiên bản hiển thị rõ; Agent không phê duyệt |
| **Status luôn rõ** | QC STATUS (READY/MISSING/NEED_REVIEW) màu hóa mọi nơi |
| **Vietnamese-first** | Font Be Vietnam Pro; label tiếng Việt; số/CCCD/MST format VN |
| **Accessible** | WCAG AA, contrast ≥ 4.5:1, focus ring, keyboard nav, ARIA |

---

## 2. Design System

### 2.1 Color

| Token | Hex | Dùng |
|---|---|---|
| `--red-600` (primary) | `#E11D2A` | Diamond logo, CTA chính, brand |
| `--red-500` | `#FF3B3B` | Gradient đầu |
| `--red-700` | `#B0151F` | Gradient cuối, hover |
| `--red-50` | `#FFF1F2` | Nền nhấn nhẹ |
| `--gold-400` | `#FFB800` | Sparkle điểm nhấn diamond |
| `--slate-900` | `#0F172A` | Text chính |
| `--slate-700` | `#334155` | Text phụ |
| `--slate-500` | `#64748B` | Muted |
| `--slate-200` | `#E2E8F0` | Border |
| `--slate-100` | `#F1F5F9` | Nền card |
| `--slate-50` | `#F8FAFC` | Nền trang |
| `--white` | `#FFFFFF` | Surface |
| `--success` | `#16A34A` | READY |
| `--warning` | `#F59E0B` | MISSING INFORMATION |
| `--info` | `#2563EB` | NEED MSB REVIEW |
| `--danger` | `#DC2626` | Lỗi / bí mật bị reject |

Gradient brand: `linear-gradient(135deg, #FF3B3B 0%, #E11D2A 55%, #B0151F 100%)`.

### 2.2 Typography
- **Display/H1:** Be Vietnam Pro 800, 32–40px
- **H2:** 700, 22–26px
- **Body:** 400, 15–16px, line-height 1.6
- **Small/Label:** 500, 13px, uppercase, letter-spacing 0.04em
- **Mono (mã mẫu, MST, CCCD):** JetBrains Mono 500
- **Chat (Agent):** 15px, nền `--slate-50`, border-left 3px `--red-600`

### 2.3 Spacing & Radius
- Scale 4px: 4/8/12/16/24/32/48
- Radius: card 16px, button 10px, chip 999px, input 10px
- Shadow: card `0 1px 3px rgba(15,23,42,.08)`, hover `0 8px 24px rgba(15,23,42,.12)`

### 2.4 Components
| Component | Mô tả |
|---|---|
| `DiamondLogo` | SVG kim cương đỏ + anchor; size 24–120px |
| `StepBar` | 8 chấm; chấm hiện = đỏ gradient, chấm qua = xanh nhạt, chấm tới = xám |
| `ChatBubble` | Agent (trái, nền slate, border-left đỏ) / User (phải, nền đỏ gradient, text trắng) |
| `FormCard` | Thẻ mẫu: mã (mono), tên, phiên bản chip, ngày hiệu lực, badge active |
| `FieldRow` | label + input/enum; required = chấm đỏ; thiếu = nền `--warning` nhạt + `[CẦN CUNG CẤP]` |
| `StatusBadge` | READY (xanh) / MISSING (amber) / NEED_REVIEW (xanh dương) |
| `ChecklistItem` | checkbox + label + required badge + icon tài liệu |
| `SignatoryCard` | tên + chức danh + vị trí ký + đóng dấu (Có/Không/?) |
| `PermissionTable` | eBank: Người dùng \| Chức danh \| User \| Vai trò \| Hạn mức \| Xác thực |
| `PrimaryButton` | đỏ gradient, radius 10, hover darken, focus ring 2px red-300 |
| `Toast` | thông báo (success/info/error), auto-dismiss 5s |

---

## 3. Logo — Kim cương đỏ

**Concept:** giữ "tinh chất hàng hải" của logo tròn MSB (mỏ neo) nhưng chuyển từ **vòng tròn → hình kim cương (diamond/rhombus)**, màu đỏ brand, có sparkle vàng ở đỉnh.

- File mark: `docs/assets/logo-diamond.svg` (200×200, scale bất kỳ)
- File wordmark: `docs/assets/logo-diamond-wordmark.svg` (`MSB SmartForm` + tagline)
- Favicon: dùng mark ở 32×32.

```plantuml
@startuml
skinparam backgroundColor #F8FAFC
note as N1
  <b>Logo mark</b>
  — Kim cương đỏ (gradient #FF3B3B → #B0151F)
  — Mỏ neo trắng bên trong (tinh chất hàng hải MSB)
  — Sparkle vàng #FFB800 ở đỉnh
  — Inner diamond outline trắng tạo chiều sâu
  Xem: docs/assets/logo-diamond.svg
end note
@enduml
```

> Variant dự phòng: nếu muốn tối giản, thay mỏ neo bằng monogram "MSB" trắng in đậm giữa diamond.

---

## 4. Information Architecture (Sitemap)

```plantuml
@startuml
skinparam componentStyle rectangle
skinparam backgroundColor #FFFFFF
skinparam shadowing false

package "MSB SmartForm AI" {
  [Landing / Home] as L
  [Chat (luồng 8 bước)] as C
  [Form Preview] as FP
  [Checklist + Tải PDF] as CK
  [History (phiên)] as H
  [Admin: Form Registry] as A
  [Auth / Login] as AU
}

AU --> L : sau login
L --> C : "Bắt đầu"
C --> FP : chọn mẫu + điền
FP --> CK : SOẠN HỒ SƠ
C --> H : xem phiên
A --> A : CRUD mẫu (RBAC admin)
@enduml
```

---

## 5. Luồng người dùng (User Journey)

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam activity {
  BackgroundColor #FFFFFF
  BorderColor #E11D2A
  FontColor #0F172A
}

start
:User mở web app;
:Trang Landing (logo kim cương đỏ);
if (Đã đăng nhập?) then (có)
else (chưa)
  :Đăng nhập OIDC (RBAC);
endif
:Vào Chat — StepBar 8 bước;
:User mô tả nhu cầu (free-text);
:Agent B1 — nhận diện KH;
:Agent B2 — phân loại nghiệp vụ;
:Agent B3 — RAG chọn mẫu MSB;
if (Tìm thấy mẫu active?) then (có)
  if (Còn trường required thiếu?) then (có)
    :Agent B4 — hỏi bổ sung;
    :User cung cấp thông tin;
  else (không)
  endif
  :Agent B5 — điền mẫu;
  :Agent B6 — kiểm tra logic;
  :Agent B7 — xác định người ký;
  :Agent B8 — sinh checklist;
  :QC chạy 8 check;
  if (STATUS?) then (READY)
    :Hiện Form Preview + Checklist;
    if (User: SOẠN HỒ SƠ?) then (có)
      :Render PDF đã điền;
      :User tải PDF + checklist;
    else (chưa)
      :Tiếp tục chat;
    endif
  elseif (MISSING) then (MISSING)
    :Hiện trường thiếu (vàng);
    :Quay lại hỏi;
  else (NEED_REVIEW)
    :Flag "cần MSB xác nhận" (xanh dương);
  endif
else (không)
  :Thông báo "Chưa xác định được mẫu";
  :Gợi ý chuyên viên MSB;
endif
stop
@enduml
```

---

## 6. Luồng 8 bước (State Machine)

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam state {
  BackgroundColor #FFF1F2
  BorderColor #E11D2A
}

[*] --> B1 : mở chat
B1 : B1 — Nhận diện KH\n(cá nhân/tổ chức, loại hình)
B2 : B2 — Phân loại nhu cầu\n(intents[])
B3 : B3 — RAG tìm mẫu MSB
B4 : B4 — Hỏi thông tin thiếu
B5 : B5 — Điền mẫu
B6 : B6 — Kiểm tra logic
B7 : B7 — Xác định người ký
B8 : B8 — Checklist nộp hồ sơ

B1 --> B2
B2 --> B3
B3 --> B4 : tìm thấy
B3 --> [*] : không tìm thấy\n→ báo MSB
B4 --> B4 : khách trả lời / còn thiếu
B4 --> B5 : đủ required
B5 --> B6
B6 --> B7
B7 --> B8
B8 --> [*] : STATUS READY/MISSING/NEED_REVIEW

state "wait (hỏi khách)" as W
B4 --> W
W --> B4
@enduml
```

---

## 7. Luồng tương tác Chat (Sequence)

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam sequence {
  ArrowColor #334155
  LifeLineBorderColor #E11D2A
}

actor "Khách hàng" as U
participant "Frontend\n(Next.js)" as FE
participant "Backend\n(FastAPI)" as API
participant "Agent\n(LangGraph)" as AG
database "KB bundle\n(8 forms)" as KB
participant "LLM\n(GreenNode AIP)" as LLM

U -> FE : "Thêm kế toán vào eBank"
FE -> API : POST /chat (SSE)
API -> AG : run(state, msg)
AG -> AG : B1 nhận diện (session)
AG -> LLM : B2 classify intents
LLM --> AG : [EBANK,USER,MAKER,APPROVER]
AG -> KB : B3 RAG retrieve + filter
KB --> AG : MSB-EBANK-01 v2.1
AG --> FE : event: form_selected
FE --> U : thẻ mẫu (mã + phiên bản)
AG --> FE : event: question (thiếu CCCD, hạn mức...)
FE --> U : hỏi trong chat
U -> FE : cung cấp thông tin
FE -> API : POST /chat (answers)
API -> AG : resume(state, answers)
AG -> AG : B5 điền + B6 logic
AG -> AG : B7 người ký + B8 checklist
AG -> AG : QC 8 check
AG --> FE : event: qc (STATUS=READY)
AG --> FE : event: output (11 mục A..K)
FE --> U : preview + checklist
U -> FE : "SOẠN HỒ SƠ"
FE -> API : POST /forms/{code}/render
API --> FE : url PDF
FE --> U : tải PDF + checklist
@enduml
```

---

## 8. Wireframe — PlantUML Salt

### 8.1 Landing / Home

```plantuml
@startsalt
{
  {+ MSB SmartForm AI | [History] [Admin] | ( user ) }
  --
  {
    {
      { <b>MSB SmartForm AI</b> }
      { "Trợ lý AI lập hồ sơ & biểu mẫu MSB" }
      { "Nói nhu cầu — Agent chọn đúng mẫu, điền giúp, sinh checklist." }
      { [  Bắt đầu soạn hồ sơ  ] }
      { [  Xem hướng dẫn  ] }
    }
  |
    {
      { <b>3 bước</b> }
      { 1. Mô tả nhu cầu }
      { 2. Agent điền mẫu MSB }
      { 3. Tải hồ sơ + checklist }
    }
  }
  --
  { "Khách hàng:  CP X | TNHH 1TV Y | TNHH 2TV+ Z | DNTN A | Cá nhân" }
}
@endsalt
```

### 8.2 Chat (màn hình chính — luồng 8 bước)

```plantuml
@startsalt
{
  {+ MSB SmartForm AI | [History] [Admin] | ( user ) }
  --
  { Step: (1)●—(2)●—(3)●—(4)●—(5)○—(6)○—(7)○—(8)○  | Status: ^ READY ^ }
  --
  {
    { [Agent] | "Chào bạn, bạn là khách cá nhân hay doanh nghiệp?" }
    { [You]   | "Doanh nghiệp, công ty CP X" }
    { [Agent] | "Bạn muốn làm gì? (vd: thêm người dùng eBank...)" }
    { [You]   | "Thêm kế toán vào eBank, kế toán lập lệnh, GĐ duyệt" }
    { [Agent] | {^
        { <b>Mẫu đã chọn</b> }
        { Mã: MSB-EBANK-01 (v2.1 — hiệu lực 01/06/2024) }
        { Nhóm: eBank | KHTC | active }
      } }
    { [Agent] | "Cần bổ sung: họ tên kế toán, CCCD, ĐT, email, hạn mức, xác thực" }
    { [You]   | "Nguyễn Văn B | 001098765432 | 0901234567 | b@x.vn | 500M | OTP" }
    { [Agent] | {^
        { <b>Bảng phân quyền eBank</b> }
        { Người dùng | Chức danh | Vai trò | Hạn mức | Xác thực }
        { Nguyễn Văn B | Kế toán | Maker | 500,000,000 | OTP }
        { Nguyễn Văn X | GĐ | Approver | — | Token }
      } }
    { [Agent] | "✓ QC: 8/8 pass — STATUS: READY. Người ký: ĐDPL. Gõ 'SOẠN HỒ SƠ' để xuất." }
  }
  --
  { "Nhập yêu cầu..." | [Gửi] }
}
@endsalt
```

### 8.3 Form Preview + Checklist

```plantuml
@startsalt
{
  {+ Form Preview — MSB-EBANK-01 v2.1 | [Chat] [Tải PDF] }
  --
  {
    { <b>A. Nhu cầu</b> | Bổ sung người dùng eBank }
    { <b>B. Loại KH</b> | KHTC — Công ty CP X }
    { <b>C. Nghiệp vụ</b> | EBANK + USER + MAKER + APPROVER }
    { <b>D. Mẫu biểu</b> | MSB-EBANK-01 (v2.1, active) }
    { <b>E. Đã có</b> | Tên DN, MST, Số TK, ĐDPL }
    { <b>F. Còn thiếu</b> | (none) }
    { <b>G. Biểu mẫu đã điền</b> | {^
        { Tên DN: CÔNG TY CP X }
        { MST: 0101234567 }
        { Số TK: 123456789999 }
        { Người dùng: Nguyễn Văn B }
        { CCCD: 001098765432 }
        { Vai trò: Maker }
        { Hạn mức: 500,000,000 VND }
        { Xác thực: OTP }
      } }
    { <b>H. Người ký</b> | Nguyễn Văn X — ĐDPL — ô ký chính — đóng dấu: theo mẫu }
    { <b>I. Hồ sơ kèm</b> | CCCD, GGĐL, Văn bản ủy quyền (nếu có) }
    { <b>J. Checklist</b> | {^
        { (X) Biểu mẫu MSB-EBANK-01 }
        { ( ) CCCD/Hộ chiếu người dùng mới }
        { ( ) Giấy chứng nhận ĐKDN }
        { ( ) Văn bản ủy quyền (nếu có) }
      } }
    { <b>K. Cảnh báo</b> | (none) — STATUS: ^ READY ^ }
  }
}
@endsalt
```

### 8.4 History & Admin

```plantuml
@startsalt
{
  {+ History | [Chat] [Admin] }
  --
  { {^
    { Phiên | Khách hàng | Nghiệp vụ | Mẫu | STATUS | Thời gian }
    { #42 | CP X | eBank user | MSB-EBANK-01 | READY | 10:24 }
    { #41 | TNHH 1TV Y | Thuế điện tử | MSB-ETAX-03 | MISSING | 09:50 }
    { #40 | Cá nhân A | IB | MSB-IB-02 | READY | 09:12 }
  } }
}
@endsalt
```

```plantuml
@startsalt
{
  {+ Admin — Form Registry (RBAC: admin) | [Upload mẫu] }
  --
  { {^
    { Mã mẫu | Tên | Nhóm | KHCN/KHTC | Phiên bản | Hiệu lực | Active }
    { MSB-EBANK-01 | ĐK bổ sung user eBank | eBank | KHTC | 2.1 | 01/06/2024 | (X) }
    { MSB-IB-02 | ĐK IB cá nhân | eBank | KHCN | 3.0 | 15/03/2024 | (X) }
    { MSB-ETAX-03 | ĐK TK nộp thuế ETAX | Thuế | KHTC | 1.5 | 01/01/2024 | (X) }
    { MSB-DS-04 | ĐK/thay đổi CTS | Chữ ký số | KHTC | 2.0 | 01/06/2024 | (X) }
    { MSB-AC-05 | Thay đổi ĐDPL | Tài khoản | KHTC | 1.8 | 01/04/2024 | (X) }
    { ... | }
  } }
}
@endsalt
```

---

## 9. Luồng trạng thái STATUS (QC)

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
state "Draft" as D
state "Filled" as F
state "QC running" as Q
state "READY" as R
state "MISSING INFORMATION" as M
state "NEED MSB REVIEW" as N

[*] --> D
D --> F : B5 điền
F --> Q : QC 8 check
Q --> R : tất cả pass
Q --> M : thiếu required
Q --> N : check cần người
M --> F : khách bổ sung
R --> [*] : xuất PDF + checklist
N --> [*] : flag MSB staff
@enduml
```

---

## 10. Responsive & Accessibility

### Responsive
| Breakpoint | Layout |
|---|---|
| ≥ 1024px (desktop) | Chat 2 cột: hội thoại (trái 60%) + panel mẫu/checklist (phải 40%) |
| 768–1023 (tablet) | 1 cột; panel mẫu chuyển thành drawer phải |
| < 768 (mobile) | 1 cột; StepBar rút thành "Bước 4/8"; checklist collapse |

### Accessibility
- Contrast: text trên đỏ gradient = trắng (ratio ≥ 4.5:1); text chính slate-900 trên white (16:1).
- Focus ring 2px `--red-300` trên mọi interactive; tab order trái→phải, trên→dưới.
- Chat: `role="log" aria-live="polite"` cho stream Agent; mỗi bubble `aria-label`.
- StepBar: `role="progressbar"` + `aria-valuenow`.
- Form: label liên kết input; required `aria-required`; lỗi `aria-describedby` + `role="alert"`.
- StatusBadge: icon + text (không chỉ màu) → daltonism-safe.
- Keyboard: Enter gửi chat; Esc đóng drawer; ↑↓ history.

---

## 11. Microinteractions & UX detail

| Điểm | Hành vi |
|---|---|
| Logo | Diamond xoay nhẹ 1 lần khi app load; sparkle nhấp nháy 2s |
| Agent typing | 3 chấm đỏ nhảy trong bubble; stream token real-time (SSE) |
| Form selected | Thẻ mẫu slide-in từ phải + shimmer; mã mẫu mono |
| Field thiếu | Nền `--warning` nhạt + chip `[CẦN CUNG CẤP]` rung nhẹ 1 lần |
| QC pass | 8 check tick lần lượt (stagger 80ms); STATUS badge pop |
| SOẠN HỒ SƠ | Nút đỏ gradient; click → skeleton preview → PDF ready → confetti nhẹ |
| Bí mật reject | Toast danger "Không lưu PIN/OTP/private key" + rung input |
| Tải PDF | Progress ring → "Tải về" button; filename `MSB-EBANK-01_filled.pdf` |

---

## 12. Tham chiếu
- Luồng nghiệp vụ: `03-LLD.md` (FSM 8 bước) · Use case: `09-use-cases.md`
- Logo: `docs/assets/logo-diamond.svg`, `docs/assets/logo-diamond-wordmark.svg`
- Render PlantUML: paste block vào https://www.plantuml.com/plantuml/uml/ hoặc VS Code extension "PlantUML".
