export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { bg: string; text: string; label: string }> = {
    READY: { bg: "bg-status-readyBg", text: "text-status-ready", label: "READY" },
    "MISSING INFORMATION": { bg: "bg-status-missingBg", text: "text-status-missing", label: "MISSING INFORMATION" },
    "NEED MSB REVIEW": { bg: "bg-status-reviewBg", text: "text-status-review", label: "NEED MSB REVIEW" },
  };
  const s = map[status] || { bg: "bg-ink-100", text: "text-ink-700", label: status };
  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-bold ${s.bg} ${s.text} animate-pop`}>
      {s.label}
    </span>
  );
}
