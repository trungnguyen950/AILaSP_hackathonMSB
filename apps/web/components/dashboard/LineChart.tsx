"use client";
import { useState, useCallback, useEffect } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceDot,
} from "recharts";

type ChartDatum = { idx: number; value: number };

function toData(data: number[]): ChartDatum[] {
  return data.map((v, i) => ({ idx: i, value: v }));
}

const colorId = (c: string) => c.replace("#", "").toLowerCase();

/* ── Custom Tooltip ── */
function ChartTooltip({ active, payload, unit, color }: any) {
  if (!active || !payload?.length) return null;
  const v = payload[0].value as number;
  return (
    <div
      className="rounded-btn border border-ink-200 bg-white/95 px-3 py-2 shadow-hover backdrop-blur"
      style={{ borderColor: color + "40" }}
    >
      <div className="text-xs font-bold" style={{ color }}>
        {typeof v === "number" ? v.toFixed(0) : v}{unit}
      </div>
      <div className="text-[10px] text-ink-500">
        Point {payload[0].payload.idx + 1}
      </div>
    </div>
  );
}

/* ── Inline (card) chart — compact, no axes ── */
export function LineChart({
  data,
  color = "#E30613",
  height = 120,
  label,
  unit = "",
}: {
  data: number[];
  color?: string;
  height?: number;
  label?: string;
  unit?: string;
}) {
  const [zoomOpen, setZoomOpen] = useState(false);
  const chartData = toData(data);
  const lastVal = data[data.length - 1] ?? 0;
  const gid = colorId(color);

  return (
    <>
      <div
        className="group w-full cursor-pointer"
        onClick={() => setZoomOpen(true)}
        title="Click để phóng to"
      >
        {label && (
          <div className="mb-1 flex items-center justify-between">
            <span className="text-xs font-semibold text-ink-700">{label}</span>
            <span className="text-xs font-bold" style={{ color }}>
              {lastVal.toFixed(0)}{unit}
              <span className="ml-1 text-[9px] text-ink-400 group-hover:text-ink-700">🔍</span>
            </span>
          </div>
        )}
        <ResponsiveContainer width="100%" height={height}>
          <AreaChart data={chartData} margin={{ top: 5, right: 5, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id={`grad-${gid}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.25} />
                <stop offset="100%" stopColor={color} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              fill={`url(#grad-${gid})`}
              isAnimationActive={true}
              animationDuration={400}
              dot={false}
              activeDot={{ r: 4, fill: color, stroke: "#fff", strokeWidth: 2 }}
            />
            <Tooltip
              content={<ChartTooltip unit={unit} color={color} />}
              cursor={{ stroke: color, strokeWidth: 1, strokeDasharray: "3 3" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {zoomOpen && (
        <ZoomModal
          data={chartData}
          color={color}
          label={label || "Chart"}
          unit={unit}
          onClose={() => setZoomOpen(false)}
        />
      )}
    </>
  );
}

/* ── Zoom Modal — full screen, glassmorphism backdrop ── */
function ZoomModal({
  data,
  color,
  label,
  unit,
  onClose,
}: {
  data: ChartDatum[];
  color: string;
  label: string;
  unit: string;
  onClose: () => void;
}) {
  const gid = colorId(color);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 transition-opacity duration-300"
      style={{ background: "rgba(11,31,58,0.25)", backdropFilter: "blur(8px)" }}
      onClick={onClose}
    >
      <div
        className="w-full max-w-3xl rounded-card border border-ink-200 bg-white p-6 shadow-hover transition-transform duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-ink-900">{label}</h3>
            <p className="text-xs text-ink-500">
              {data.length} data points · click outside or press ESC to close
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-btn p-2 text-ink-500 transition hover:bg-ink-50 hover:text-ink-900"
            aria-label="Close"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        {/* Stats */}
        <div className="mb-4 grid grid-cols-4 gap-3">
          {(() => {
            const vals = data.map((d) => d.value);
            const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
            return (
              <>
                <StatBox label="Current" value={`${vals[vals.length - 1].toFixed(0)}${unit}`} color={color} />
                <StatBox label="Average" value={`${avg.toFixed(0)}${unit}`} color="#1757A6" />
                <StatBox label="Min" value={`${Math.min(...vals).toFixed(0)}${unit}`} color="#F59E0B" />
                <StatBox label="Max" value={`${Math.max(...vals).toFixed(0)}${unit}`} color="#00A676" />
              </>
            );
          })()}
        </div>

        {/* Large chart with grid + axes */}
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
            <defs>
              <linearGradient id={`zoom-grad-${gid}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                <stop offset="100%" stopColor={color} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis
              dataKey="idx"
              tick={{ fontSize: 10, fill: "#667085" }}
              label={{ value: "Time", position: "insideBottom", offset: -5, style: { fontSize: 10, fill: "#98A2B3" } }}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "#667085" }}
              width={45}
            />
            <Tooltip
              content={<ChartTooltip unit={unit} color={color} />}
              cursor={{ stroke: color, strokeWidth: 1, strokeDasharray: "3 3" }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2.5}
              fill={`url(#zoom-grad-${gid})`}
              isAnimationActive={true}
              animationDuration={600}
              dot={{ r: 2, fill: color }}
              activeDot={{ r: 6, fill: color, stroke: "#fff", strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function StatBox({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="rounded-btn border border-ink-200 bg-ink-50 p-3 text-center">
      <div className="text-[10px] font-semibold uppercase tracking-wide text-ink-500">{label}</div>
      <div className="mt-0.5 text-sm font-extrabold" style={{ color }}>{value}</div>
    </div>
  );
}
