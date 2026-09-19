export type FormMeta = {
  code: string;
  name: string;
  business_group: string;
  segment: string;
  version: string;
  effective_date: string;
  active: boolean;
};

export function FormCard({ form }: { form: FormMeta }) {
  if (!form) return null;
  return (
    <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
      <div className="flex items-center justify-between">
        <span className="font-mono text-sm font-bold brand-text">{form.code}</span>
        <span className="rounded-full bg-brand-50 px-2 py-0.5 text-[11px] font-semibold text-brand-700">
          v{form.version}
        </span>
      </div>
      <div className="mt-1 text-sm font-semibold text-ink-900">{form.name}</div>
      <div className="mt-1 flex flex-wrap gap-2 text-[11px] text-ink-700">
        <span>{form.business_group}</span>
        <span>·</span>
        <span>{form.segment}</span>
        <span>·</span>
        <span>HL: {form.effective_date}</span>
        {form.active && (
          <span className="rounded bg-status-readyBg px-1.5 font-semibold text-status-ready">active</span>
        )}
      </div>
    </div>
  );
}
