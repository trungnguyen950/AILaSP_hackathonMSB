"use client";
import { Navbar } from "@/components/Navbar";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { LineChart } from "@/components/dashboard/LineChart";
import { BarChart } from "@/components/dashboard/BarChart";
import { DonutChart } from "@/components/dashboard/DonutChart";
import { useMetrics } from "@/lib/useMetrics";

export default function DashboardPage() {
  const m = useMetrics(3000);

  return (
    <div className="flex min-h-screen flex-col bg-ink-50">
      <Navbar active="dashboard" />

      {/* Header */}
      <div className="border-b border-ink-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-extrabold text-ink-900">📊 Dashboard</h1>
              <p className="mt-1 text-sm text-ink-700">
                System performance & business impact — realtime metrics (cập nhật mỗi 3 giây)
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="inline-flex h-2.5 w-2.5 animate-pulse rounded-full bg-status-ready" />
              <span className="text-xs font-semibold text-status-ready">LIVE</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto w-full max-w-6xl flex-1 p-6">
        {/* KPI Cards — Row 1: System & Performance */}
        <div className="mb-2 text-xs font-bold uppercase tracking-wide text-ink-500">System & Performance</div>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          <KpiCard
            label="API Response Time"
            value={m.apiResponseTime}
            unit="ms"
            icon="⚡"
            color="navy"
            trend={m.apiResponseTime < 300 ? "up" : "down"}
            trendValue={`P95: ${Math.round(m.apiResponseTime * 1.8)}ms`}
          />
          <KpiCard
            label="Error Rate"
            value={m.errorRate.toFixed(1)}
            unit="%"
            icon="⚠️"
            color={m.errorRate < 5 ? "status-ready" : "brand"}
            trend={m.errorRate < 5 ? "up" : "down"}
            trendValue={`${m.errorCount} errors / ${m.successCount} reqs`}
          />
          <KpiCard
            label="Page Load Time"
            value={m.pageLoadTime}
            unit="ms"
            icon="📄"
            color="navy"
            trend={m.pageLoadTime < 1000 ? "up" : "down"}
            trendValue="Core Web Vitals"
          />
          <KpiCard
            label="Active Users"
            value={m.activeUsers}
            unit="online"
            icon="👥"
            color="status-ready"
            trend="up"
            trendValue="Realtime"
          />
        </div>

        {/* KPI Cards — Row 2: BU Impact */}
        <div className="mb-2 mt-6 text-xs font-bold uppercase tracking-wide text-ink-500">BU Impact</div>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          <KpiCard
            label="Conversion Rate"
            value={m.conversionRate.toFixed(1)}
            unit="%"
            icon="🎯"
            color="brand"
            trend="up"
            trendValue="Form → READY"
          />
          <KpiCard
            label="Avg Engagement"
            value={m.avgEngagement}
            unit="s"
            icon="⏱️"
            color="navy"
            trend="up"
            trendValue="Time on page"
          />
          <KpiCard
            label="Task Success Rate"
            value={m.taskSuccessRate.toFixed(1)}
            unit="%"
            icon="✅"
            color="status-ready"
            trend="up"
            trendValue={`${m.tasksCompleted}/${m.tasksStarted} tasks`}
          />
          <KpiCard
            label="Retention Rate"
            value={m.retentionRate.toFixed(1)}
            unit="%"
            icon="🔄"
            color="status-review"
            trend="up"
            trendValue="Return visitors"
          />
        </div>

        {/* Charts — Row 1 */}
        <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
          {/* Active Users — Line chart */}
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card lg:col-span-2">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-bold text-ink-900">Active Users (Realtime)</h2>
              <span className="rounded-full bg-status-readyBg px-2 py-0.5 text-[10px] font-bold text-status-ready">
                {m.activeUsers} online now
              </span>
            </div>
            <LineChart data={m.activeUsersHistory} color="#00A676" height={140} label="Users" unit="" />
          </div>

          {/* Error vs Success — Donut chart */}
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
            <h2 className="mb-3 text-sm font-bold text-ink-900">API Success vs Errors</h2>
            <DonutChart
              label="requests"
              segments={[
                { label: "Success", value: m.successCount, color: "#00A676" },
                { label: "Errors", value: m.errorCount, color: "#E30613" },
              ]}
            />
          </div>
        </div>

        {/* Charts — Row 2 */}
        <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
          {/* Response Time — Line chart */}
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card lg:col-span-2">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-bold text-ink-900">API Response Time (ms)</h2>
              <span className="rounded-full bg-navy-50 px-2 py-0.5 text-[10px] font-bold text-navy-900">
                avg {m.apiResponseTime}ms
              </span>
            </div>
            <LineChart data={m.responseTimeHistory} color="#1757A6" height={140} label="Latency" unit="ms" />
          </div>

          {/* Task Success — Donut */}
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
            <h2 className="mb-3 text-sm font-bold text-ink-900">Task Completion</h2>
            <DonutChart
              label="tasks"
              segments={[
                { label: "Completed", value: m.tasksCompleted, color: "#00A676" },
                { label: "In Progress", value: m.tasksStarted - m.tasksCompleted, color: "#F59E0B" },
              ]}
            />
          </div>
        </div>

        {/* Charts — Row 3 */}
        <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
          {/* Engagement by Page — Bar chart */}
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
            <h2 className="mb-3 text-sm font-bold text-ink-900">User Engagement by Page (seconds)</h2>
            <BarChart
              height={150}
              unit="s"
              data={m.engagementByPage.map((e, i) => ({
                label: e.page,
                value: e.seconds,
                color: ["#E30613", "#1757A6", "#7c3aed", "#059669"][i % 4],
              }))}
            />
          </div>

          {/* BU Impact Summary — Bar chart */}
          <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
            <h2 className="mb-3 text-sm font-bold text-ink-900">BU Impact Metrics (%)</h2>
            <BarChart
              height={150}
              unit="%"
              data={[
                { label: "Conversion", value: m.conversionRate, color: "#E30613" },
                { label: "Task Success", value: m.taskSuccessRate, color: "#00A676" },
                { label: "Retention", value: m.retentionRate, color: "#1757A6" },
                { label: "Engagement", value: Math.min(m.avgEngagement / 4, 100), color: "#7c3aed" },
              ]}
            />
          </div>
        </div>

        {/* Footer note */}
        <div className="mt-6 rounded-card border border-navy-100 bg-navy-50 p-4">
          <div className="flex items-start gap-2">
            <span className="text-lg">💡</span>
            <div className="text-xs text-navy-900/80">
              <strong>Dữ liệu mock realtime</strong> — cập nhật mỗi 3 giây. Cấu trúc hook <code className="rounded bg-white px-1 font-mono">useMetrics()</code> tách biệt phần fetch data,
              dễ thay thế bằng API thật (Prometheus, Grafana, custom backend) mà không đổi UI.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
