export type ChecklistItem = { item: string; required: boolean; done: boolean };

export function Checklist({ items }: { items: ChecklistItem[] }) {
  if (!items?.length) return null;
  return (
    <div className="rounded-card border border-slate-200 bg-white p-4 shadow-card">
      <div className="mb-2 text-sm font-bold text-slate-900">J. Checklist trước khi nộp MSB</div>
      <ul className="space-y-1.5">
        {items.map((it, i) => (
          <li key={i} className="flex items-start gap-2 text-sm">
            <span
              className={`mt-0.5 inline-flex h-4 w-4 items-center justify-center rounded border text-[10px] ${
                it.done ? "border-status-ready bg-status-ready text-white" : "border-slate-300"
              }`}
            >
              {it.done ? "✓" : ""}
            </span>
            <span className={it.required ? "text-slate-900" : "text-slate-500"}>{it.item}</span>
            {it.required && (
              <span className="ml-1 rounded bg-brand-50 px-1.5 text-[10px] font-semibold text-brand-700">bắt buộc</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
