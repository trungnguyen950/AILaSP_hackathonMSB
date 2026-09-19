# 10 — UI/UX Design

> MSB SmartForm AI · Design system + wireframe + luồng · v1.0 (đã deploy)
> Logo: **kim cương đỏ** (giữ tinh chất hàng hải của MSB)

---

## 1. Nguyên tắc thiết kế

| Nguyên tắc | Áp dụng |
|---|---|
| **Conversation-first** | Chat là trung tâm; guided flow giải thích trước, thu thập sau |
| **Progressive disclosure** | Agent giải thích form → ví dụ → mới hỏi dữ liệu |
| **Trust & compliance** | Logo MSB, mã mẫu/phiên bản hiển thị rõ; Agent không phê duyệt |
| **Status luôn rõ** | FORM EXPLAINED / READY / MISSING / NEED REVIEW — màu hóa |
| **Vietnamese-first (có dấu)** | Tiếng Việt đầy đủ dấu; FDI → English |
| **Session isolation** | Mỗi persona = session riêng; nút reset |
| **Accessible** | WCAG AA, keyboard nav, ARIA labels |

---

## 2. Design System

### 2.1 Color (Tailwind config)

| Token | Hex | Dùng |
|---|---|---|
| `brand` (primary) | `#E30613` | MSB red — CTA, logo, brand |
| `brand-50` | `#FCE8EA` | Nền nhấn nhẹ |
| `brand-600` | `#C90510` | Hover |
| `navy` | `#0B1F3A` | Header, text chính |
| `navy-50` | `#EAF2FF` | Nền info |
| `ink-900` | `#111827` | Text chính |
| `ink-700` | `#667085` | Text phụ |
| `ink-200` | `#E5E7EB` | Border |
| `ink-50` | `#F8FAFC` | Nền trang |
| `status-ready` | `#00A676` | READY |
| `status-missing` | `#F59E0B` | MISSING INFORMATION |
| `status-review` | `#1757A6` | NEED MSB REVIEW |
| `status-danger` | `#E30613` | Lỗi |
| `purple-600` | — | FDI badge VI/EN |

### 2.2 Typography
- **Font:** Inter, Be Vietnam Pro, system-ui
- **Display/H1:** 800, 24–32px
- **H2:** 700, 18–22px
- **Body:** 400, 14–15px
- **Mono (mã mẫu, MST, CCCD):** JetBrains Mono
- **Chat Agent:** 14px, nền trắng, border-left 3px brand
- **Chat User:** 14px, nền brand, text trắng

### 2.3 Spacing & Radius
- Scale 4px: 4/8/12/16/24/32/48
- Radius: card 16px, button 10px, chip 999px
- Shadow: card `0 1px 3px rgba(11,31,58,.08)`, hover `0 8px 24px rgba(11,31,58,.12)`

### 2.4 Components

| Component | Mô tả |
|---|---|
| `Navbar` | Navy header, 4 links: 💬 Chat · 📋 Mẫu Biểu Mẫu · ✍️ Ký Số · 📖 Hướng dẫn |
| `Logo` / `Wordmark` | SVG kim cương đỏ + text "MSB SmartForm" |
| `StepBar` | 5 bước: Hiểu nhu cầu → Chọn mẫu → Điền → Kiểm tra → Ready |
| `PersonaCard` | 6 thẻ: CTCP X, TNHH MTV Y, TNHH 2TV Z, DNTN A, FDI Alpha 🌐, Cá nhân A |
| `ChatBubble` | Agent (trái, nền trắng, border-left đỏ) / User (phải, nền đỏ, text trắng) |
| `FormCard` | Mã mẫu (mono), tên, phiên bản chip, segment, active badge, bilingual badge |
| `StatusBadge` | READY (xanh) / MISSING (amber) / NEED_REVIEW (xanh dương) / FORM EXPLAINED (navy) |
| `Checklist` | Checkbox + label + required badge |
| `SignaturePad` | Custom canvas, mouse + touch, border dashed, clear button |
| `PreviewModal` | Full-screen modal: field table, signatories, accompanying docs |
| `FormsGrid` | Responsive grid (3/2/1 cols), search, filter, card with 4 buttons |
| `AIButton` | Gradient tím-xanh-lá, pulse animation |
| `SkeletonCard` | Shimmer loading placeholder |
| `Sidebar` (user-guide) | Navigation sidebar cho 9 trang hướng dẫn |
| `BlockRenderer` | Render typed blocks (h2, p, code, table, steps, callout, faq, nextSteps) |
| `BackToTop` | Floating button scroll to top |

### 2.5 Animations

| Class | Effect |
|---|---|
| `.animate-pop` | Scale 0.8→1 + opacity 0→1 (status badge) |
| `.dot-typing` | Blink 3 dots (chat loading) |
| `.ai-gradient` | Linear gradient tím→xanh→lá (AI Fill button) |
| `.ai-pulse` | Box-shadow pulse 2s infinite (AI button) |
| `.card-lift` | translateY(-4px) + shadow hover (form cards) |
| `.skeleton` | Shimmer 1.5s infinite (loading) |
| `.modal-backdrop` | Backdrop blur 4px (preview modal) |

---

## 3. Logo — Kim cương đỏ

**Concept:** giữ "tinh chất hàng hải" của logo MSB (mỏ neo) nhưng chuyển từ vòng tròn → hình kim cương, màu đỏ brand.

- SVG 200×200, scale bất kỳ
- Path: kim cương đỏ + inner border trắng + icon người (circle + line + arms + anchor)
- Used in: Navbar (40px), PersonaCard (16px), forms grid

---

## 4. Wireframe — 4 trang

### 4.1 Trang Chat (`/`)

```
┌──────────────────────────────────────────────────┐
│ NAVBAR: [MSB SmartForm]  💬Chat 📋Forms ✍️Sign 📖│
├──────────────────────────────────────────────────┤
│ STEP STRIP: 01 Hiểu → 02 Chọn → 03 Điền → 04 KT  │
├──────────────────────────────────────────────────┤
│ PERSONAS: [CTCP X] [TNHH MTV Y] [TNHH 2TV Z*]    │
│   [DNTN A] [FDI Alpha🌐 VI/EN] [Cá nhân A]        │
├────────────────────────┬─────────────────────────┤
│ CHAT                   │ SIDE PANEL              │
│                        │                         │
│ Agent: Chào bạn...     │ [Status: FORM EXPLAINED]│
│ User: CTCP X muốn...   │ [Mẫu đã chọn: MSB-...]  │
│ Agent: 📋 Mẫu phù hợp  │ [Hồ sơ đã điền]         │
│   1. Tên doanh nghiệp  │   company_name: CP X    │
│   2. Mã số thuế —...   │   tax_id: 0101234567    │
│   ...                  │ [Checklist]             │
│ User: sẵn sàng         │ [⬇ Tải Text] [⬇ Tải PDF]│
│ Agent: Để hoàn thiện..│ [SOẠN HỒ SƠ]            │
│   1. Họ tên...         │ [↻ Xoá thông tin cũ]    │
│ User: Nguyễn B | ...   │                         │
│ Agent: ✓ READY         │                         │
│                        │                         │
│ [Input box] [Gửi]      │                         │
└────────────────────────┴─────────────────────────┘
```

### 4.2 Trang Mẫu Biểu Mẫu (`/forms/`)

```
┌──────────────────────────────────────────────────┐
│ NAVBAR                                             │
├──────────────────────────────────────────────────┤
│ 📋 Thư Viện Biểu Mẫu                              │
│ [🔍 Search...]  [Category ▼]  9/9 mẫu             │
├──────────┬──────────┬──────────┐                 │
│ 🏦 eBank  │ 📋 Tài khoản│ 🔐 CKS │                 │
│ MSB-...01 │ MSB-AC-05 │ MSB-DS04│                 │
│ Đăng ký.. │ Thay đổi..│ Đăng ký.│                 │
│ [eBank]   │ [Tài khoản]│ [CKS]   │                 │
│ v2.1 active│ v1.8     │ v2.0    │                 │
│ [⬇Text][⬇PDF]│[⬇T][⬇P]│[⬇T][⬇P]│                 │
│ [👁 Xem Trước]      │[👁]      │[👁]              │
│ [🤖 AI Fill]        │[🤖]      │[🤖]              │
├──────────┼──────────┼──────────┤                 │
│ 🧾 Thuế   │ 🏦 eBank  │ 🏦 eBank │                 │
│ ...       │ ...       │ ...      │                 │
└──────────┴──────────┴──────────┘                 │
```

### 4.3 Trang Ký Số (`/sign/`)

```
┌──────────────────────────────────────────────────┐
│ NAVBAR                                             │
├──────────────────────────────────────────────────┤
│ ✍️ Ký Chữ Ký Số (Mô Phỏng)                        │
├──────────────────────┬───────────────────────────┤
│ 1. Chọn mẫu & cert   │ 3. Vẽ chữ ký              │
│ [Form dropdown ▼]    │ [┌──────────────────┐]    │
│ [Cert dropdown ▼]    │ [│  Signature Pad   │]    │
│                      │ [│  (canvas)        │]    │
│ 2. Upload file       │ [└──────────────────┘]    │
│ ┌──────────────────┐ │ [🗑 Xóa]                  │
│ │ 📁 Kéo thả hoặc  │ │                           │
│ │    click để chọn │ │ [🤖 AI Kiểm Tra File]    │
│ └──────────────────┘ │ [✍️ Ký File Đã Upload]   │
│ [🤖 AI Kiểm Tra]    │                           │
│ ✅ File hợp lệ 100/100│                          │
├──────────────────────┴───────────────────────────┤
│ RESULT: ✅ Ký số thành công!                      │
│ File: test_signed.txt | Hash: abc123...           │
│ Webhook → AI Agent (JSON)                         │
│ [⬇ Tải file] [💬 Gửi Zalo Bot]                   │
│ [Zalo chat_id input]                              │
└──────────────────────────────────────────────────┘
```

### 4.4 Trang Hướng dẫn (`/user-guide/`)

```
┌──────────────────────────────────────────────────┐
│ NAVBAR: [MSB SmartForm]  📖 Hướng dẫn  [Liên hệ]  │
├───────────┬──────────────────────────────────────┤
│ SIDEBAR   │ CONTENT                              │
│           │                                      │
│ Giới thiệu│ # Hướng dẫn sử dụng                  │
│  📖 Truy cập│                                  │
│           │ 3 trang: Chat / Forms / Sign         │
│ Trang Chat│                                      │
│  💬 Tổng quan│ [Card grid: 9 guide pages]        │
│  🔄 Luồng  │                                      │
│           │ 💡 Mẹo nhanh                         │
│ Mẫu Biểu Mẫu│                                    │
│  📋 Tổng quan│                                    │
│  🤖 AI Fill │                                    │
│           │                                      │
│ Ký Số     │                                      │
│  📤 Upload │                                      │
│  ✍️ Tạo sẵn│                                      │
│           │                                      │
│ Demo & FAQ│                                      │
│  🎯 Demo   │                                      │
│  ❓ FAQ    │                                      │
└───────────┴──────────────────────────────────────┘
```

---

## 5. Responsive

| Breakpoint | Layout |
|---|---|
| Mobile (<640px) | 1 cột, button full-width, sidebar ẩn |
| Tablet (640–1024px) | 2 cột (forms grid), chat + panel stack |
| Desktop (>1024px) | 3 cột (forms grid), chat (1fr) + panel (360px) |

---

## 6. Tham chiếu
- Product: `00-product-overview.md` · PRD: `01-PRD.md` · Architecture: `02-architecture.md` · Use cases: `09-use-cases.md`
