export function StepBar({ step }: { step: number }) {
  const total = 8;
  return (
    <div className="flex items-center gap-1.5" role="progressbar" aria-valuenow={step} aria-valuemax={total}>
      {Array.from({ length: total }, (_, i) => {
        const n = i + 1;
        const done = n < step;
        const current = n === step;
        return (
          <div key={n} className="flex items-center gap-1.5">
            <span
              className={`inline-flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-bold ${
                current
                  ? "brand-gradient text-white"
                  : done
                  ? "bg-status-ready text-white"
                  : "bg-slate-200 text-slate-500"
              }`}
            >
              {n}
            </span>
            {i < total - 1 && <span className={`h-0.5 w-3 ${done ? "bg-status-ready" : "bg-slate-200"}`} />}
          </div>
        );
      })}
      <span className="ml-2 text-xs font-medium text-slate-500">Bước {step}/{total}</span>
    </div>
  );
}
