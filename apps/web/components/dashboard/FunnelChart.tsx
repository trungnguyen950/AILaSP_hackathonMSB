"use client";

export function FunnelChart({
  stages,
  height = 200,
}: {
  stages: { stage: string; count: number; color: string }[];
  height?: number;
}) {
  const max = Math.max(...stages.map((s) => s.count), 1);
  const total = stages[0]?.count || 1;

  return (
    <div className="w-full" style={{ minHeight: height }}>
      {stages.map((s, i) => {
        const widthPct = (s.count / max) * 100;
        const convPct = i === 0 ? 100 : (s.count / total) * 100;
        const dropoff = i > 0 ? ((stages[i - 1].count - s.count) / stages[i - 1].count) * 100 : 0;
        return (
          <div key={i} className="mb-2">
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="font-semibold text-ink-900">{s.stage}</span>
              <span className="text-ink-700">
                {s.count} <span className="text-ink-500">({convPct.toFixed(0)}%)</span>
                {i > 0 && dropoff > 0 && (
                  <span className="ml-1 text-status-danger">↓{dropoff.toFixed(0)}%</span>
                )}
              </span>
            </div>
            <div className="h-7 w-full overflow-hidden rounded-btn bg-ink-50">
              <div
                className="flex h-full items-center justify-end rounded-btn pr-2 text-[10px] font-bold text-white transition-all duration-500"
                style={{ width: `${widthPct}%`, background: s.color, minWidth: "30px" }}
              >
                {s.count}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
