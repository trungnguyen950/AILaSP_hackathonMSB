"use client";
import { Navbar } from "@/components/Navbar";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { LineChart } from "@/components/dashboard/LineChart";
import { BarChart } from "@/components/dashboard/BarChart";
import { DonutChart } from "@/components/dashboard/DonutChart";
import { FunnelChart } from "@/components/dashboard/FunnelChart";
import { HorizontalBarChart } from "@/components/dashboard/HorizontalBarChart";
import { useMetrics } from "@/lib/useMetrics";

const vnd = (v: number) =>
  new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND", maximumFractionDigits: 0 }).format(v);

const vndShort = (v: number) => {
  if (v >= 1_000_000_000) return `${(v / 1_000_000_000).toFixed(1)} tỷ ₫`;
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)} triệu ₫`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(0)}K ₫`;
  return `${v} ₫`;
};

export default function DashboardPage() {
  const m = useMetrics(3000);

  const readyDelta = (m.readyRate - m.prevReadyRate).toFixed(1);
  const handlingDelta = (m.prevAvgHandlingTime - m.avgHandlingTime).toFixed(1);
  const returnDelta = (m.prevReturnRate - m.returnRate).toFixed(1);
  const npsDelta = (m.npsScore - m.prevNps).toFixed(0);
  const aevAnnual = Math.round((m.estimatedSavings / 1) * (365 / 14));

  return (
    <div className="flex min-h-screen flex-col bg-ink-50">
      <Navbar active="dashboard" />

      {/* Header */}
      <div className="border-b border-ink-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-extrabold text-ink-900">Dashboard Điều hành Hồ sơ</h1>
              <p className="mt-1 text-sm text-ink-700">
                SmartForm AI · Cập nhật realtime mỗi 3 giây
              </p>
            </div>
            <div className="flex items-center gap-4">
              <select className="rounded-btn border border-ink-200 bg-white px-3 py-1.5 text-xs font-medium text-ink-700">
                <option>Hôm nay</option>
                <option>7 ngày</option>
                <option>30 ngày</option>
              </select>
              <select className="rounded-btn border border-ink-200 bg-white px-3 py-1.5 text-xs font-medium text-ink-700">
                <option>Tất cả BU</option>
                <option>Doanh nghiệp</option>
                <option>Bán lẻ</option>
              </select>
              <div className="flex items-center gap-2">
                <span className="inline-flex h-2.5 w-2.5 animate-pulse rounded-full bg-status-ready" />
                <span className="text-xs font-semibold text-status-ready">LIVE</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto w-full max-w-7xl flex-1 p-6">
        {/* ═══ Section 1: KPI TỔNG QUAN ═══ */}
        <div className="mb-2 text-xs font-bold uppercase tracking-wide text-ink-500">KPI Tổng quan</div>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <KpiCard
            label="Tổng hồ sơ đã xử lý"
            value={m.totalDossiers.toLocaleString("vi-VN")}
            unit="hồ sơ"
            icon="📋"
            color="navy"
            trend="up"
            trendValue="Cộng dồn realtime"
          />
          <KpiCard
            label="Nộp đúng lần đầu"
            value={m.readyRate.toFixed(1)}
            unit="%"
            icon="✅"
            color="status-ready"
            trend="up"
            trendValue={`${m.readyCount} hồ sơ READY`}
            delta={`${readyDelta}% so kỳ trước`}
            deltaGood={m.readyRate >= m.prevReadyRate}
          />
          <KpiCard
            label="Thời gian xử lý TB"
            value={m.avgHandlingTime.toFixed(1)}
            unit="phút/hồ sơ"
            icon="⏱️"
            color="brand"
            trend="down"
            trendValue="Mục tiêu < 10 phút"
            delta={`${handlingDelta} phút so kỳ trước`}
            deltaGood={m.avgHandlingTime <= m.prevAvgHandlingTime}
          />
          <KpiCard
            label="Tỷ lệ hồ sơ trả lại"
            value={m.returnRate.toFixed(1)}
            unit="%"
            icon="⚠️"
            color="status-missing"
            trend="down"
            trendValue={`${m.missingCount} hồ sơ cần bổ sung`}
            delta={`${returnDelta}% so kỳ trước`}
            deltaGood={m.returnRate <= m.prevReturnRate}
          />
        </div>

        {/* ═══ Section 2: GIÁ TRỊ KINH DOANH ═══ */}
        <div className="mb-2 mt-8 text-xs font-bold uppercase tracking-wide text-ink-500">Giá trị kinh doanh (AEV)</div>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <KpiCard
            label="Tiết kiệm luỹ kế"
            value={vndShort(m.estimatedSavings)}
            icon="💰"
            color="status-ready"
            trend="up"
            trendValue="Cộng dồn từ pilot"
          />
          <KpiCard
            label="Tiết kiệm hôm nay"
            value={vndShort(m.savingsToday)}
            icon="📈"
            color="status-ready"
            trend="up"
            trendValue="Realtime"
          />
          <KpiCard
            label="Giờ RM tiết kiệm"
            value={m.rmTimeSaved}
            unit="giờ"
            icon="🕐"
            color="navy"
            trend="up"
            trendValue="Tổng cumul"
          />
          <div className="relative overflow-hidden rounded-card border border-navy-900 bg-navy-900 p-5 shadow-kpi">
            <div className="absolute left-0 top-0 h-1 w-full bg-brand" />
            <div className="text-[11px] font-semibold uppercase tracking-wide text-navy-100">AEV dự kiến / năm</div>
            <div className="mt-1 text-2xl font-extrabold text-white">
              {vndShort(aevAnnual)}
            </div>
            <div className="mt-1 text-xs font-medium text-status-ready">↑ Ước tính annualized</div>
          </div>
        </div>

        {/* ═══ Section 3: TRẠNG THÁI HỒ SƠ ═══ */}
        <div className="mb-2 mt-8 text-xs font-bold uppercase tracking-wide text-ink-500">Trạng thái hồ sơ</div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
            <h2 className="mb-3 text-sm font-bold text-ink-900">Phân bố trạng thái</h2>
            <DonutChart
              label="hồ sơ"
              segments={[
                { label: "READY", value: m.readyCount, color: "#00A676" },
                { label: "MISSING", value: m.missingCount, color: "#F59E0B" },
                { label: "NEED REVIEW", value: m.reviewCount, color: "#1757A6" },
              ]}
            />
          </div>
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card lg:col-span-2">
            <h2 className="mb-3 text-sm font-bold text-ink-900">Chi tiết theo trạng thái</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between rounded-btn bg-status-readyBg px-4 py-3">
                <span className="flex items-center gap-2 text-sm font-semibold text-ink-900">
                  <span className="inline-block h-3 w-3 rounded-full bg-status-ready" /> READY — Nộp đúng lần đầu
                </span>
                <span className="text-sm font-bold text-status-ready">
                  {m.readyCount.toLocaleString("vi-VN")} ({m.readyRate.toFixed(1)}%)
                </span>
              </div>
              <div className="flex items-center justify-between rounded-btn bg-status-missingBg px-4 py-3">
                <span className="flex items-center gap-2 text-sm font-semibold text-ink-900">
                  <span className="inline-block h-3 w-3 rounded-full bg-status-missing" /> MISSING — Cần bổ sung thông tin
                </span>
                <span className="text-sm font-bold text-status-missing">
                  {m.missingCount.toLocaleString("vi-VN")} ({((m.missingCount / m.totalDossiers) * 100).toFixed(1)}%)
                </span>
              </div>
              <div className="flex items-center justify-between rounded-btn bg-status-reviewBg px-4 py-3">
                <span className="flex items-center gap-2 text-sm font-semibold text-ink-900">
                  <span className="inline-block h-3 w-3 rounded-full bg-status-review" /> NEED REVIEW — Cần MSB xác nhận
                </span>
                <span className="text-sm font-bold text-status-review">
                  {m.reviewCount.toLocaleString("vi-VN")} ({((m.reviewCount / m.totalDossiers) * 100).toFixed(1)}%)
                </span>
              </div>
            </div>
            <div className="mt-4 rounded-btn bg-navy-50 p-3 text-xs text-navy-900/80">
              💡 <strong>{m.readyRate.toFixed(1)}%</strong> hồ sơ nộp đúng lần đầu — mục tiêu 90%. Cần cải thiện thêm{" "}
              {(90 - m.readyRate).toFixed(1)}%.
            </div>
          </div>
        </div>

        {/* ═══ Section 4: XU HƯỚNG REALTIME ═══ */}
        <div className="mb-2 mt-8 text-xs font-bold uppercase tracking-wide text-ink-500">Xu hướng realtime</div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card lg:col-span-2">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-bold text-ink-900">Phiên khách hàng đang hoạt động</h2>
              <span className="rounded-full bg-status-readyBg px-2 py-0.5 text-[10px] font-bold text-status-ready">
                {m.activeSessions} online now
              </span>
            </div>
            <LineChart data={m.activeSessionsHistory} color="#00A676" height={140} label="Phiên active" unit="" />
          </div>
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-bold text-ink-900">Thời gian xử lý TB</h2>
              <span className="rounded-full bg-navy-50 px-2 py-0.5 text-[10px] font-bold text-navy-900">
                {m.avgHandlingTime.toFixed(1)} phút
              </span>
            </div>
            <LineChart data={m.handlingTimeHistory} color="#1757A6" height={140} label="Phút/hồ sơ" unit="p" />
          </div>
        </div>

        {/* ═══ Section 5: PHÂN KHÚC KHÁCH HÀNG ═══ */}
        <div className="mb-2 mt-8 text-xs font-bold uppercase tracking-wide text-ink-500">Phân khúc khách hàng</div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
            <h2 className="mb-3 text-sm font-bold text-ink-900">Hồ sơ theo phân khúc</h2>
            <DonutChart
              label="hồ sơ"
              segments={m.segmentVolume.map((s) => ({ label: s.segment, value: s.count, color: s.color }))}
            />
          </div>
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card lg:col-span-2">
            <h2 className="mb-3 text-sm font-bold text-ink-900">Số lượng hồ sơ theo phân khúc</h2>
            <BarChart
              height={160}
              data={m.segmentVolume.map((s) => ({
                label: s.segment,
                value: s.count,
                color: s.color,
              }))}
            />
            <div className="mt-3 flex items-center gap-4 text-[11px]">
              <span className="flex items-center gap-1">
                <span className="inline-block h-2.5 w-2.5 rounded-full bg-navy-900" /> KH Doanh nghiệp
              </span>
              <span className="flex items-center gap-1">
                <span className="inline-block h-2.5 w-2.5 rounded-full bg-purple" /> KH FDI (song ngữ VI/EN)
              </span>
              <span className="flex items-center gap-1">
                <span className="inline-block h-2.5 w-2.5 rounded-full bg-brand" /> KH Cá nhân
              </span>
            </div>
          </div>
        </div>

        {/* ═══ Section 6: SIGNING FUNNEL + FORM SOURCE ═══ */}
        <div className="mb-2 mt-8 text-xs font-bold uppercase tracking-wide text-ink-500">Phễu ký & Nguồn form</div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card lg:col-span-2">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-bold text-ink-900">Phễu ký hồ sơ — Form → Signed</h2>
              <span className="rounded-full bg-status-readyBg px-2 py-0.5 text-[10px] font-bold text-status-ready">
                {m.signSuccessRate.toFixed(1)}% success
              </span>
            </div>
            <FunnelChart stages={m.signFunnel} height={200} />
          </div>
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
            <h2 className="mb-3 text-sm font-bold text-ink-900">Nguồn sử dụng form</h2>
            <DonutChart
              label="sessions"
              segments={m.formUsageBySource.map((s) => ({ label: s.source, value: s.count, color: s.color }))}
            />
          </div>
        </div>

        {/* ═══ Section 7: TOP FORMS + DAILY TREND ═══ */}
        <div className="mb-2 mt-8 text-xs font-bold uppercase tracking-wide text-ink-500">Form dùng nhiều & Xu hướng ký</div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-bold text-ink-900">Top 9 form dùng nhiều nhất</h2>
              <span className="text-[10px] text-ink-500">Chat + Forms page</span>
            </div>
            <HorizontalBarChart
              height={250}
              data={m.formUsage
                .slice()
                .sort((a, b) => b.count - a.count)
                .slice(0, 9)
                .map((f) => ({
                  label: f.code.replace("MSB-", ""),
                  value: f.count,
                  color: f.source === "Chat" ? "#E30613" : "#7c3aed",
                  sublabel: f.source,
                }))}
            />
            <div className="mt-2 flex items-center gap-4 text-[10px]">
              <span className="flex items-center gap-1">
                <span className="inline-block h-2.5 w-2.5 rounded-full bg-brand" /> Chat (persona)
              </span>
              <span className="flex items-center gap-1">
                <span className="inline-block h-2.5 w-2.5 rounded-full bg-purple" /> Forms (AI Fill)
              </span>
            </div>
          </div>
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-bold text-ink-900">Xu hướng ký theo ngày (14 ngày)</h2>
              <span className="rounded-full bg-navy-50 px-2 py-0.5 text-[10px] font-bold text-navy-900">
                {m.signTrend.reduce((sum, d) => sum + d.signed, 0)} tổng đã ký
              </span>
            </div>
            <BarChart
              height={180}
              data={m.signTrend.map((d, i) => ({ label: `D${i + 1}`, value: d.signed, color: "#00A676" }))}
            />
          </div>
        </div>

        {/* ═══ Section 8: RM PERFORMANCE ═══ */}
        <div className="mb-2 mt-8 text-xs font-bold uppercase tracking-wide text-ink-500">Hiệu suất chuyên viên RM</div>
        <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
          <h2 className="mb-3 text-sm font-bold text-ink-900">Top 5 RM — theo số hồ sơ xử lý</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-ink-200 text-left text-[11px] font-bold uppercase tracking-wide text-ink-500">
                  <th className="pb-2 pr-4">Chuyên viên RM</th>
                  <th className="pb-2 pr-4 text-right">Hồ sơ xử lý</th>
                  <th className="pb-2 pr-4 text-right">Tỷ lệ READY</th>
                  <th className="pb-2">Hiệu suất</th>
                </tr>
              </thead>
              <tbody>
                {m.rmPerformance
                  .slice()
                  .sort((a, b) => b.dossiers - a.dossiers)
                  .map((rm, i) => (
                    <tr key={i} className="border-b border-ink-100">
                      <td className="py-3 pr-4 font-semibold text-ink-900">{rm.name}</td>
                      <td className="py-3 pr-4 text-right font-bold text-ink-900">{rm.dossiers}</td>
                      <td className="py-3 pr-4 text-right font-semibold text-status-ready">{rm.readyRate.toFixed(0)}%</td>
                      <td className="py-3">
                        <div className="h-2 w-full max-w-xs overflow-hidden rounded-full bg-ink-50">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{ width: `${rm.readyRate}%`, background: rm.color }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* ═══ Section 9: KHÁCH HÀNG & FDI ═══ */}
        <div className="mb-2 mt-8 text-xs font-bold uppercase tracking-wide text-ink-500">Khách hàng & FDI</div>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <KpiCard
            label="NPS"
            value={m.npsScore.toFixed(0)}
            unit="điểm"
            icon="📊"
            color="navy"
            trend="up"
            trendValue="Net Promoter Score"
            delta={`${npsDelta} so kỳ trước`}
            deltaGood={m.npsScore >= m.prevNps}
          />
          <KpiCard
            label="CSAT"
            value={m.csatScore.toFixed(1)}
            unit="/ 5.0"
            icon="⭐"
            color="status-ready"
            trend="up"
            trendValue="Customer Satisfaction"
          />
          <KpiCard
            label="KH quay lại"
            value={m.returningCustomers}
            unit="KH"
            icon="🔄"
            color="status-review"
            trend="up"
            trendValue={`${m.returnCustomerRate.toFixed(1)}% tỷ lệ quay lại`}
          />
          <KpiCard
            label="FDI đã phục vụ"
            value={m.fdiServed}
            unit="KH"
            icon="🌐"
            color="purple"
            trend="up"
            trendValue={`${m.fdiBilingualForms} form song ngữ VI/EN`}
          />
        </div>

        {/* FDI detail card */}
        <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="rounded-card border border-purple-50 bg-purple-50 p-4 shadow-card">
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-purple px-2 py-0.5 text-[10px] font-bold text-white">VI/EN</span>
              <h2 className="text-sm font-bold text-ink-900">FDI — Segment chiến lược</h2>
            </div>
            <div className="mt-3 grid grid-cols-3 gap-3 text-center">
              <div>
                <div className="text-xl font-extrabold text-purple">{m.fdiServed}</div>
                <div className="text-[10px] text-ink-500">KH đã phục vụ</div>
              </div>
              <div>
                <div className="text-xl font-extrabold text-purple">{m.fdiBilingualForms}</div>
                <div className="text-[10px] text-ink-500">Form song ngữ</div>
              </div>
              <div>
                <div className="text-xl font-extrabold text-purple">{m.fdiSatisfaction.toFixed(1)}</div>
                <div className="text-[10px] text-ink-500">CSAT FDI / 5.0</div>
              </div>
            </div>
          </div>
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
            <h2 className="mb-2 text-sm font-bold text-ink-900">Giải thích chỉ số</h2>
            <ul className="space-y-1.5 text-xs text-ink-700">
              <li><strong className="text-status-ready">NPS</strong> — Net Promoter Score (−100 đến 100), đo lòng trung thành KH</li>
              <li><strong className="text-status-ready">CSAT</strong> — Customer Satisfaction Score (1.0–5.0), hài lòng sau mỗi hồ sơ</li>
              <li><strong className="text-status-review">Tỷ lệ quay lại</strong> — % KH dùng SmartForm lần 2+ (mức độ giữ chân)</li>
              <li><strong className="text-purple">FDI</strong> — Doanh nghiệp có vốn đầu tư nước ngoài, cần form song ngữ VI–EN</li>
            </ul>
          </div>
        </div>

        {/* Footer note */}
        <div className="mt-6 rounded-card border border-navy-100 bg-navy-50 p-4">
          <div className="flex items-start gap-2">
            <span className="text-lg">💡</span>
            <div className="text-xs text-navy-900/80">
              <strong>Dữ liệu realtime</strong> — cập nhật mỗi 3 giây. Hook{" "}
              <code className="rounded bg-white px-1 font-mono">useMetrics()</code> tách biệt phần data,
              dễ thay API thật (MSB data warehouse, Core Banking, CRM) mà không đổi UI.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
