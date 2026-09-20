type Trend = "up" | "down" | "neutral";

const colorHexMap: Record<string, string> = {
  navy: "#0B1F3A",
  brand: "#E30613",
  "status-ready": "#00A676",
  "status-missing": "#F59E0B",
  "status-review": "#1757A6",
  purple: "#7c3aed",
};

export function KpiCard({
  label,
  value,
  unit,
  trend,
  trendValue,
  icon,
  color = "navy",
  delta,
  deltaGood,
}: {
  label: string;
  value: string | number;
  unit?: string;
  trend?: Trend;
  trendValue?: string;
  icon: string;
  color?: "navy" | "brand" | "status-ready" | "status-missing" | "status-review" | "purple";
  delta?: string;
  deltaGood?: boolean;
}) {
  const colorMap: Record<string, string> = {
    navy: "text-navy-900",
    brand: "text-brand",
    "status-ready": "text-status-ready",
    "status-missing": "text-status-missing",
    "status-review": "text-status-review",
    purple: "text-purple",
  };
  const trendColor = trend === "up" ? "text-status-ready" : trend === "down" ? "text-status-danger" : "text-ink-500";
  const trendIcon = trend === "up" ? "↑" : trend === "down" ? "↓" : "→";
  const accent = colorHexMap[color] || "#0B1F3A";

  return (
    <div className="relative overflow-hidden rounded-card border border-ink-200 bg-white p-5 shadow-kpi transition-all duration-200 hover:-translate-y-0.5 hover:shadow-hover">
      <div className="absolute left-0 top-0 h-1 w-full" style={{ background: accent }} />
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
      {delta && (
        <div className={`mt-0.5 text-[11px] font-semibold ${deltaGood ? "text-status-ready" : "text-status-danger"}`}>
          {deltaGood ? "↑" : "↓"} {delta}
        </div>
      )}
    </div>
  );
}
