type Trend = "up" | "down" | "neutral";

export function KpiCard({
  label,
  value,
  unit,
  trend,
  trendValue,
  icon,
  color = "navy",
}: {
  label: string;
  value: string | number;
  unit?: string;
  trend?: Trend;
  trendValue?: string;
  icon: string;
  color?: "navy" | "brand" | "status-ready" | "status-missing" | "status-review";
}) {
  const colorMap: Record<string, string> = {
    navy: "text-navy-900",
    brand: "text-brand",
    "status-ready": "text-status-ready",
    "status-missing": "text-status-missing",
    "status-review": "text-status-review",
  };
  const trendColor = trend === "up" ? "text-status-ready" : trend === "down" ? "text-status-danger" : "text-ink-500";
  const trendIcon = trend === "up" ? "↑" : trend === "down" ? "↓" : "→";

  return (
    <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-ink-500">{label}</div>
          <div className={`mt-1 text-2xl font-extrabold ${colorMap[color]}`}>
            {value}
            {unit && <span className="ml-0.5 text-sm font-medium text-ink-700">{unit}</span>}
          </div>
        </div>
        <div className="text-2xl">{icon}</div>
      </div>
      {trendValue && (
        <div className={`mt-1 text-xs font-medium ${trendColor}`}>
          {trendIcon} {trendValue}
        </div>
      )}
    </div>
  );
}
