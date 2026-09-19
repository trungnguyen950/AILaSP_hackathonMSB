"use client";

export function HorizontalBarChart({
  data,
  height = 220,
  label,
}: {
  data: { label: string; value: number; color?: string; sublabel?: string }[];
  height?: number;
  label?: string;
}) {
  const max = Math.max(...data.map((d) => d.value), 1);

  return (
    <div className="w-full">
      {label && <div className="mb-2 text-xs font-semibold text-ink-700">{label}</div>}
      <div className="space-y-2" style={{ minHeight: height }}>
        {data.map((d, i) => {
          const widthPct = (d.value / max) * 100;
          return (
            <div key={i} className="flex items-center gap-2">
              <div className="w-32 shrink-0 text-right text-[11px] font-medium text-ink-700">
                <div className="font-mono font-bold text-ink-900">{d.label}</div>
                {d.sublabel && <div className="text-[9px] text-ink-500">{d.sublabel}</div>}
              </div>
              <div className="h-6 flex-1 overflow-hidden rounded-btn bg-ink-50">
                <div
                  className="flex h-full items-center justify-end rounded-btn pr-2 text-[10px] font-bold text-white transition-all duration-500"
                  style={{ width: `${widthPct}%`, background: d.color || "#E30613", minWidth: "24px" }}
                >
                  {d.value}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
