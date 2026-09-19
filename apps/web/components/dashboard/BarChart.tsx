"use client";

export function BarChart({
  data,
  height = 140,
  label,
  unit = "",
}: {
  data: { label: string; value: number; color?: string }[];
  height?: number;
  label?: string;
  unit?: string;
}) {
  const max = Math.max(...data.map((d) => d.value), 1);

  return (
    <div className="w-full">
      {label && <div className="mb-2 text-xs font-semibold text-ink-700">{label}</div>}
      <div className="flex items-end gap-3" style={{ height }}>
        {data.map((d, i) => {
          const barHeight = (d.value / max) * (height - 30);
          return (
            <div key={i} className="flex flex-1 flex-col items-center">
              <div className="text-[10px] font-bold text-ink-900">{d.value.toFixed(0)}{unit}</div>
              <div
                className="mt-1 w-full rounded-t-btn transition-all duration-500"
                style={{
                  height: `${barHeight}px`,
                  background: d.color || "#E30613",
                  minHeight: "4px",
                }}
              />
              <div className="mt-1 text-[10px] font-medium text-ink-700">{d.label}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
