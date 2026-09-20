# PROMPT — Redesign Dashboard cho Quản lý Ngân hàng

> **Role:** Senior Web Designer chuyên mảng Banking/FinTech
> **Target user:** Quản lý ngân hàng (Phó TGĐ, Trưởng BU, Giám đốc Khối KH Doanh nghiệp/Bán lẻ, Quản lý RM) — KHÔNG phải IT/DevOps
> **Product:** MSB SmartForm AI — trợ lý AI lập hồ sơ & biểu mẫu khách hàng

---

## 1. CONTEX & MỤC TIÊU

Dashboard hiện tại (`apps/web/app/dashboards/page.tsx`) đang trộn lẫn **chỉ số kỹ thuật IT** (API Response Time, Error Rate, Page Load Time, Success vs Errors donut, Response Time line chart) với **chỉ số business**. Quản lý ngân hàng không quan tâm "P95 latency 245ms" hay "Error rate 2.1%" — họ quan tâm: **bao nhiêu hồ sơ đã xử lý, bao nhiêu nộp đúng lần đầu, tiết kiệm được bao nhiêu tiền, khách hàng FDI phục vụ thế nào, RM nào hiệu quả nhất.**

**Mục tiêu:** Redesign toàn bộ Dashboard thành **Business KPI Dashboard** thuần — loại bỏ 100% chỉ số IT, giữ và mở rộng chỉ số business, thiết kế hiện đại đẹp mắt, dữ liệu realtime cập nhật mỗi 3 giây.

---

## 2. FILES CẦN SỬA

| File | Hành động |
|---|---|
| `apps/web/lib/useMetrics.ts` | **Rewrite** — xóa fields IT, thêm fields business mới, giữ cơ chế realtime 3s |
| `apps/web/app/dashboards/page.tsx` | **Rewrite** — xóa toàn bộ section IT, redesign layout business |
| `apps/web/components/dashboard/KpiCard.tsx` | **Enhance** — thêm prop `delta` (so với kỳ trước) và `sparkline` (mini trend) |
| `apps/web/components/dashboard/LineChart.tsx` | **Keep** — đã tốt, SVG thuần |
| `apps/web/components/dashboard/BarChart.tsx` | **Keep** |
| `apps/web/components/dashboard/DonutChart.tsx` | **Keep** |
| `apps/web/components/dashboard/FunnelChart.tsx` | **Keep** |
| `apps/web/components/dashboard/HorizontalBarChart.tsx` | **Keep** |
| `apps/web/tailwind.config.ts` | **Add tokens** — xem section 6 |

**KHÔNG** tạo file mới ngoài những file trên. **KHÔNG** thêm dependency npm — tất cả chart đã là SVG thuần, giữ nguyên.

---

## 3. DATA MODEL MỚI — `useMetrics.ts`

### 3.1 XÓA các fields IT (KHÔNG dùng cho quản lý NH):

```
- apiResponseTime          ❌
- errorRate                ❌
- pageLoadTime             ❌
- responseTimeHistory      ❌
- errorCount               ❌
- successCount             ❌
- tasksCompleted           ❌  (reframe thành business)
- tasksStarted             ❌
- avgEngagement            ❌  (seconds on page — IT/web analytics, không phải bank KPI)
- engagementByPage         ❌
```

### 3.2 GIỮ các fields business đã có (đã đúng hướng):

```
- signFunnel               ✅ giữ (Form Selected → Data Collected → QC Passed → Signed)
- signSuccessRate          ✅ giữ
- totalSigned              ✅ giữ
- formUsageBySource        ✅ giữ (Chat vs Forms vs Download)
- formUsage                ✅ giữ (top 9 forms)
- signTrend                ✅ giữ (14 days)
- conversionRate           ✅ giữ — REFRAME thành "Tỷ lệ nộp đúng lần đầu" (First-Time-Right)
- retentionRate            ✅ giữ — REFRAME thành "Tỷ lệ khách quay lại"
- activeUsers              ✅ giữ — REFRAME thành "Phiên KH đang hoạt động"
- activeUsersHistory       ✅ giữ — REFRAME thành "Phiên hoạt động realtime"
```

### 3.3 THÊM fields business mới:

```typescript
export type Metrics = {
  // ═══ KPI TỔNG QUAN (realtime) ═══
  totalDossiers: number;           // Tổng hồ sơ đã xử lý (cộng dồn, realtime)
  readyCount: number;              // Hồ sơ READY — nộp đúng lần đầu
  missingCount: number;            // Hồ sơ MISSING — cần bổ sung
  reviewCount: number;             // Hồ sơ NEED MSB REVIEW
  readyRate: number;               // % First-Time-Right = ready/total × 100

  // ═══ HIỆU QUẢ VẬN HÀNH ═══
  avgHandlingTime: number;         // Thời gian xử lý TB (phút/hồ sơ) — target ↓
  returnRate: number;              // Tỷ lệ hồ sơ trả lại (%) — target ↓
  handlingTimeHistory: number[];   // Time series 20 điểm cho line chart (phút)
  activeSessions: number;          // Phiên KH đang chat realtime
  activeSessionsHistory: number[]; // Time series 20 điểm

  // ═══ GIÁ TRỊ KINH DOANH (AEV) ═══
  estimatedSavings: number;        // Tiết kiệm luỹ kế (VND) — grows realtime
  savingsToday: number;            // Tiết kiệm hôm nay (VND)
  rmTimeSaved: number;             // Số giờ RM tiết kiệm (cumulative)

  // ═══ PHÂN KHÚC KHÁCH HÀNG ═══
  segmentVolume: { segment: string; count: number; color: string }[];
  // 3 segment: "KH Doanh nghiệp", "KH FDI", "KH Cá nhân"

  // ═══ TRẠNG THÁI HỒ SƠ (cho donut) ═══
  // derived: readyCount, missingCount, reviewCount

  // ═══ SIGNING FUNNEL (giữ nguyên) ═══
  signFunnel: { stage: string; count: number; color: string }[];
  signSuccessRate: number;
  totalSigned: number;

  // ═══ FORM USAGE (giữ nguyên) ═══
  formUsageBySource: { source: string; count: number; color: string }[];
  formUsage: { code: string; name: string; count: number; source: string }[];

  // ═══ DAILY SIGN TREND (giữ nguyên) ═══
  signTrend: { day: string; signed: number; failed: number }[];

  // ═══ RM PERFORMANCE (mới — quản lý quan tâm) ═══
  rmPerformance: { name: string; dossiers: number; readyRate: number; color: string }[];
  // Top 5 RM theo số hồ sơ xử lý

  // ═══ KHÁCH HÀNG (mới) ═══
  npsScore: number;                 // Net Promoter Score (-100 đến 100)
  csatScore: number;                // Customer Satisfaction (1.0–5.0)
  returningCustomers: number;       // Số KH quay lại dùng lần 2+
  returnRate: number;               // Tỷ lệ quay lại (%) — giữ retentionRate ý nghĩa

  // ═══ FDI STRATEGIC (mới — segment chiến lược) ═══
  fdiServed: number;                // Tổng FDI đã phục vụ
  fdiBilingualForms: number;        // Form song ngữ VI-EN đã dùng
  fdiSatisfaction: number;          // CSAT riêng FDI (1.0–5.0)

  // ═══ KỲ TRƯỚC (cho delta so sánh) ═══
  prevReadyRate: number;
  prevAvgHandlingTime: number;
  prevReturnRate: number;
  prevNps: number;
};
```

### 3.4 Giá trị INITIAL (business-realistic cho MSB):

```typescript
const INITIAL: Metrics = {
  totalDossiers: 1247,
  readyCount: 1083,
  missingCount: 112,
  reviewCount: 52,
  readyRate: 86.8,                  // 1083/1247
  avgHandlingTime: 12.5,            // phút/hồ sơ (target ↓ từ 45 phút)
  returnRate: 9.0,                  // % (target ↓ từ 30%)
  handlingTimeHistory: Array.from({length:20}, () => 10 + Math.random()*6),
  activeSessions: 14,
  activeSessionsHistory: Array.from({length:20}, () => 8 + Math.floor(Math.random()*12)),
  estimatedSavings: 174_580_000,    // ~174 triệu VND cumulative
  savingsToday: 12_600_000,         // ~12.6 triệu hôm nay
  rmTimeSaved: 682,                 // giờ RM tiết kiệm
  segmentVolume: [
    { segment: "KH Doanh nghiệp", count: 892, color: "#0B1F3A" },
    { segment: "KH FDI",          count: 156, color: "#7c3aed" },
    { segment: "KH Cá nhân",      count: 199, color: "#E30613" },
  ],
  signFunnel: [
    { stage: "Form Selected",  count: 320, color: "#1757A6" },
    { stage: "Data Collected", count: 285, color: "#7c3aed" },
    { stage: "QC Passed",      count: 251, color: "#F59E0B" },
    { stage: "Signed",         count: 218, color: "#00A676" },
  ],
  signSuccessRate: 68.1,
  totalSigned: 218,
  formUsageBySource: [
    { source: "Chat (persona)",    count: 198, color: "#E30613" },
    { source: "Forms (AI Fill)",   count: 87,  color: "#7c3aed" },
    { source: "Forms (download)",  count: 45,  color: "#1757A6" },
  ],
  formUsage: [ /* giữ nguyên 9 forms hiện tại */ ],
  signTrend: [ /* giữ nguyên 14 days */ ],
  rmPerformance: [
    { name: "Nguyễn Thị Lan",  dossiers: 87, readyRate: 91, color: "#00A676" },
    { name: "Trần Hoàng Nam",  dossiers: 72, readyRate: 88, color: "#1757A6" },
    { name: "Lê Minh Đức",     dossiers: 65, readyRate: 85, color: "#7c3aed" },
    { name: "Phạm Thu Hà",     dossiers: 58, readyRate: 89, color: "#E30613" },
    { name: "Võ Thanh Tùng",   dossiers: 51, readyRate: 83, color: "#F59E0B" },
  ],
  npsScore: 42,
  csatScore: 4.3,
  returningCustomers: 318,
  returnRate: 25.5,                  // % quay lại
  fdiServed: 156,
  fdiBilingualForms: 89,
  fdiSatisfaction: 4.6,
  prevReadyRate: 82.1,
  prevAvgHandlingTime: 14.8,
  prevReturnRate: 12.5,
  prevNps: 35,
};
```

### 3.5 `nextMetrics()` — jitter logic:

- `totalDossiers` tăng 0–2 mỗi tick (3s)
- `readyCount` tăng theo totalDossiers × readyRate
- `readyRate` jitter quanh 86 ± 3, clamp [75, 95]
- `avgHandlingTime` jitter quanh 12.5 ± 1.5, clamp [8, 20] — trend ↓ nhẹ
- `returnRate` jitter quanh 9 ± 1, clamp [5, 15] — trend ↓
- `estimatedSavings` tăng `savingsToday / 288` mỗi tick (288 ticks/ngày = 3s interval)
- `savingsToday` jitter nhẹ
- `activeSessions` jitter 14 ± 6, clamp [1, 50]
- `signFunnel`, `formUsage`, `formUsageBySource` — giữ logic growth hiện tại
- `signTrend` — giữ logic shift window hiện tại
- `npsScore` jitter 42 ± 3, clamp [20, 70]
- `csatScore` jitter 4.3 ± 0.2, clamp [3.5, 5.0]
- `fdiServed` tăng 0–1 mỗi tick
- `rmPerformance` — count tăng nhẹ random

---

## 4. LAYOUT MỚI — `dashboards/page.tsx`

### 4.1 Header (redesign):

```
┌──────────────────────────────────────────────────────────┐
│  [Logo MSB]  Dashboard Điều hành Hồ sơ                    │
│  SmartForm AI · Cập nhật realtime mỗi 3 giây   ● LIVE     │
│  [Kỳ: Hôm nay ▼]  [BU: Tất cả ▼]  [Phân khúc: Tất cả ▼]  │
└──────────────────────────────────────────────────────────┘
```

- Tiêu đề: **"Dashboard Điều hành Hồ sơ"** (không phải "📊 Dashboard")
- Subtitle: "SmartForm AI · Cập nhật realtime mỗi 3 giây"
- Thêm 3 filter dropdown (UI only, mock): Kỳ (Hôm nay / 7 ngày / 30 ngày), BU (Tất cả / Doanh nghiệp / Bán lẻ), Phân khúc (Tất cả / DN / FDI / Cá nhân)
- LIVE badge giữ (xanh, pulse)

### 4.2 Section 1 — KPI TỔNG QUAN (4 KpiCard lớn):

| Card | Value | Unit | Icon | Color | Delta |
|---|---|---|---|---|---|
| Tổng hồ sơ đã xử lý | `totalDossiers` | hồ sơ | 📋 | navy | ↑ vs hôm qua |
| Nộp đúng lần đầu | `readyRate` | % | ✅ | status-ready | ↑ `readyRate - prevReadyRate` |
| Thời gian xử lý TB | `avgHandlingTime` | phút/hồ sơ | ⏱️ | brand | ↓ `prev - current` |
| Tỷ lệ trả lại | `returnRate` | % | ⚠️ | status-missing | ↓ `prev - current` |

> **KpiCard enhance:** thêm prop `delta?: number` và `deltaLabel?: string` — hiển thị "↑ +4.7% so kỳ trước" (xanh nếu good, đỏ nếu bad). Thêm prop `sparkline?: number[]` — mini line chart 30px height trong card (nếu KpiCard có chỗ).

### 4.3 Section 2 — GIÁ TRỊ KINH DOANH (3 KpiCard + 1 highlight card):

| Card | Value | Format | Note |
|---|---|---|---|
| Tiết kiệm luỹ kế | `estimatedSavings` | VND format (174.5 triệu) | Icon 💰, color xanh, large number |
| Tiết kiệm hôm nay | `savingsToday` | VND format | Icon 📈 |
| Giờ RM tiết kiệm | `rmTimeSaved` | giờ | Icon 🕐 |
| **AEV dự kiến/năm** | `estimatedSavings / daysElapsed × 365` | **VND, bold, highlight card** | Card navy bg, số trắng lớn, label "AEV dự kiến (năm)" |

> **Format VND:** `new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(value)` — hiển thị "174.580.000 ₫"

### 4.4 Section 3 — TRẠNG THÁI HỒ SƠ (Donut + 3 mini stat):

```
┌─────────────────────┬──────────────────────────────────┐
│   Donut Chart       │  ✅ READY: 1.083 (86.8%)          │
│   3 segments:       │  ⚠️ MISSING: 112 (9.0%)           │
│   READY / MISSING   │  🔍 NEED REVIEW: 52 (4.2%)        │
│   / REVIEW          │                                   │
│   Center: total     │  → Insight: "86.8% hồ sơ nộp      │
│   "1.247 hồ sơ"     │    đúng lần đầu — mục tiêu 90%"   │
└─────────────────────┴──────────────────────────────────┘
```

- DonutChart: 3 segments (ready xanh, missing amber, review blue)
- Center label: tổng hồ sơ
- Bên phải: 3 dòng stat + 1 insight box (navy-50 bg)

### 4.5 Section 4 — XU HƯỚNG REALTIME (2 line charts):

| Chart | Data | Color | Span |
|---|---|---|---|
| Phiên KH đang hoạt động (realtime) | `activeSessionsHistory` | #00A676 (xanh) | 2 cols |
| Thời gian xử lý TB (phút/hồ sơ) | `handlingTimeHistory` | #1757A6 (navy) | 1 col |

- LineChart giữ nguyên component
- Header mỗi chart: title + badge "X online now" hoặc "avg X phút"

### 4.6 Section 5 — PHÂN KHÚC KHÁCH HÀNG (donut + bar):

```
┌─────────────────────┬──────────────────────────────────┐
│  Donut: 3 segment   │  Bar chart: số lượng mỗi segment  │
│  DN / FDI / Cá nhân │  + % tổng                         │
└─────────────────────┴──────────────────────────────────┘
```

- DonutChart: `segmentVolume` (DN navy, FDI tím, Cá nhân đỏ)
- BarChart: cùng data, show count + %
- FDI segment nổi bật (badge tím "VI/EN", strategic)

### 4.7 Section 6 — SIGNING FUNNEL + FORM SOURCE (giữ, refine):

| Chart | Data | Span |
|---|---|---|
| Signing Funnel — Form → Signed | `signFunnel` | 2 cols |
| Form Usage by Source | `formUsageBySource` donut | 1 col |

- FunnelChart giữ nguyên — đã tốt
- Thêm conversion % giữa các stage (đã có trong component)

### 4.8 Section 7 — TOP FORMS + DAILY TREND (giữ, refine):

| Chart | Data | Span |
|---|---|---|
| Top 9 Forms dùng nhiều nhất | `formUsage` HorizontalBarChart | 1 col |
| Daily Sign Trend (14 days) | `signTrend` BarChart | 1 col |

- Giữ nguyên — đã business-oriented

### 4.9 Section 8 — RM PERFORMANCE (mới — table/card):

```
┌──────────────────────────────────────────────────────────┐
│  Top 5 RM — Hiệu suất xử lý hồ sơ                         │
├──────────────────┬──────────┬──────────┬────────────────┤
│  RM              │ Hồ sơ    │ Ready %  │ Trend           │
├──────────────────┼──────────┼──────────┼────────────────┤
│  Nguyễn Thị Lan  │ 87       │ 91%      │ ████░ 91%       │
│  Trần Hoàng Nam  │ 72       │ 88%      │ ████░ 88%       │
│  ...             │          │          │                 │
└──────────────────┴──────────┴──────────┴────────────────┘
```

- Dùng HorizontalBarChart cho `rmPerformance` (label = tên RM, value = dossiers, sublabel = readyRate%)
- Hoặc table HTML thuần (đẹp hơn cho quản lý) — 4 cột: RM, Hồ sơ, Ready %, Progress bar

### 4.10 Section 9 — KHÁCH HÀNG & FDI (4 KpiCard):

| Card | Value | Unit | Icon | Color |
|---|---|---|---|---|
| NPS | `npsScore` | điểm | 📊 | navy |
| CSAT | `csatScore` | /5.0 | ⭐ | status-ready |
| KH quay lại | `returningCustomers` | KH | 🔄 | status-review |
| FDI đã phục vụ | `fdiServed` | KH | 🌐 | purple (#7c3aed) |

> FDI card có badge "VI/EN" tím — segment chiến lược.

### 4.11 Footer note (rewrite):

```
💡 Dữ liệu realtime — cập nhật mỗi 3 giây. Hook useMetrics() tách biệt phần data,
dễ thay API thật (MSB data warehouse, Core Banking, CRM) mà không đổi UI.
```

---

## 5. THIẾT KẾ VISUAL — Modern Banking Dashboard

### 5.1 Nguyên tắc:

- **Clean & spacious** — card padding 20px, gap 16px, section gap 32px
- **Data-forward** — số là focal point, font 28–32px bold cho KPI value
- **Color semantic** — xanh = good (READY, savings), đỏ = alert (return rate, MISSING), amber = warning, tím = FDI, navy = neutral/primary
- **Section divider** — mỗi section có label uppercase tracking-wide text-ink-500 (giữ style hiện tại) + optional icon
- **No emoji overload** — 1 emoji/card tối đa, style professional
- **Realtime feel** — LIVE badge pulse, số cập nhật mượt (transition), KpiCard có subtle animation khi value change

### 5.2 Color usage (dùng tokens hiện tại + thêm):

| Token | Hex | Dùng cho |
|---|---|---|
| `brand` | #E30613 | MSB red — alert, return rate, Cá nhân segment |
| `navy` | #0B1F3A | Primary — header, DN segment, neutral KPI |
| `status-ready` | #00A676 | Good — READY, savings, success |
| `status-missing` | #F59E0B | Warning — MISSING, return rate |
| `status-review` | #1757A6 | Info — NEED REVIEW |
| `purple-600` | #7c3aed | **FDI** — strategic segment, bilingual |
| `ink-50` | #F8FAFC | Page background |
| `ink-200` | #E5E7EB | Card border |

### 5.3 Typography:

- KPI value: `text-3xl font-extrabold` (30px) — focal point
- KPI label: `text-xs font-semibold uppercase tracking-wide text-ink-500`
- Section title: `text-sm font-bold text-ink-900`
- Chart title: `text-sm font-bold text-ink-900`
- Insight text: `text-xs text-navy-900/80`
- VND format: `font-mono` (JetBrains Mono) cho số tiền

### 5.4 Card style (enhance):

```tsx
// KpiCard — thêm subtle gradient + delta
<div className="rounded-card border border-ink-200 bg-white p-5 shadow-card transition-all hover:shadow-hover">
  {/* gradient accent bar top */}
  <div className="absolute top-0 left-0 h-1 w-full rounded-t-card" style={{ background: color }} />
  ...
</div>
```

- Thêm **accent bar** 4px trên cùng mỗi KpiCard (màu theo semantic)
- Hover: `shadow-hover` + `translateY(-2px)` (card-lift effect)
- Delta: "↑ +4.7% so kỳ trước" — xanh nếu metric good direction, đỏ nếu bad

### 5.5 Layout grid:

- Container: `max-w-7xl` (tăng từ max-w-6xl cho rộng hơn — dashboard cần space)
- KPI rows: `grid-cols-2 lg:grid-cols-4` (mobile 2, desktop 4)
- Chart rows: `grid-cols-1 lg:grid-cols-3` (mobile stack, desktop 3)
- Section gap: `mt-8` giữa sections
- Card gap: `gap-4`

---

## 6. TAILWIND CONFIG — tokens thêm

```typescript
// tailwind.config.ts — thêm vào extend:
colors: {
  // ... existing ...
  purple: {
    600: "#7c3aed",   // FDI strategic
    50:  "#F5F3FF",
  },
},
boxShadow: {
  // ... existing ...
  kpi: "0 2px 8px rgba(11,31,58,.06)",   // softer cho KPI card
},
```

---

## 7. LOẠI BỎ — CHECKLIST

**XÓA hoàn toàn khỏi `page.tsx` và `useMetrics.ts`:**

- [x] Section "System & Performance" (4 KPI: API Response Time, Error Rate, Page Load Time, Active Users as IT)
- [x] Chart "API Response Time (ms)" line chart
- [x] Chart "API Success vs Errors" donut
- [x] Chart "Task Completion" donut (reframe thành Trạng thái hồ sơ)
- [x] Chart "User Engagement by Page (seconds)" bar
- [x] Chart "BU Impact Metrics (%)" bar (reframe — không gộp technical)
- [x] Fields: `apiResponseTime`, `errorRate`, `pageLoadTime`, `responseTimeHistory`, `errorCount`, `successCount`, `tasksCompleted`, `tasksStarted`, `avgEngagement`, `engagementByPage`
- [x] Mọi text mentioning "API", "latency", "P95", "Core Web Vitals", "Error Rate", "Page Load"

---

## 8. GIỮ — CHECKLIST

- [x] Cơ chế realtime `useMetrics(intervalMs)` — setInterval 3s, giữ nguyên pattern
- [x] Tất cả 6 chart component (LineChart, BarChart, DonutChart, FunnelChart, HorizontalBarChart, KpiCard) — không xóa, chỉ enhance KpiCard
- [x] Signing Funnel (Form → Data → QC → Signed) — business, giữ
- [x] Form Usage by Source (Chat vs AI Fill vs Download) — business, giữ
- [x] Most Used Forms top 9 — business, giữ
- [x] Daily Sign Trend 14 days — business, giữ
- [x] LIVE badge + pulse animation
- [x] Footer note (rewrite text nhưng giữ concept)
- [x] Vietnamese language (có dấu)
- [x] Static export compatible (SSG) — "use client" chỉ ở useMetrics, page.tsx

---

## 9. ACCEPTANCE CRITERIA

1. **Zero IT metrics** — grep `apiResponse|errorRate|pageLoad|latency|P95|Core Web` trong `page.tsx` và `useMetrics.ts` → không match
2. **All business sections present** — 9 sections theo layout 4.2–4.11
3. **Realtime still works** — `useMetrics(3000)` cập nhật mỗi 3s, số thay đổi mượt
4. **VND format** — số tiền hiển thị "174.580.000 ₋" (Intl vi-VN)
5. **FDI nổi bật** — segment FDI có màu tím #7c3aed, badge "VI/EN"
6. **Delta so kỳ trước** — KpiCard hiển thị "↑ +X% so kỳ trước"
7. **Responsive** — mobile 2 cols, desktop 4 cols (KPI); mobile stack, desktop 3 cols (charts)
8. **No new dependency** — `package.json` không đổi
9. **Build pass** — `npm run build` trong `apps/web` thành công
10. **Vietnamese** — tất cả label/title bằng tiếng Việt có dấu

---

## 10. THỨ TỰ IMPLEMENT

1. Sửa `tailwind.config.ts` — thêm purple + shadow kpi
2. Rewrite `useMetrics.ts` — xóa IT fields, thêm business fields, giữ realtime logic
3. Enhance `KpiCard.tsx` — thêm delta + accent bar
4. Rewrite `dashboards/page.tsx` — 9 sections theo layout mới
5. `npm run build` verify
6. Review visual — đảm bảo modern, clean, professional banking aesthetic

---

> **Ghi chú:** Đây là dashboard cho **quản lý ngân hàng** — không phải tech dashboard. Mọi quyết định design ưu tiên: (1) số liệu business có ý nghĩa với C-level, (2) dễ đọc nhanh (glanceable), (3) đẹp hiện đại nhưng không flashy — banking cần trust & professionalism. Dữ liệu realtime là differentiator — giữ và nhấn mạnh.
