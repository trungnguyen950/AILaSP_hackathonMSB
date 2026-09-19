"use client";
import { useEffect } from "react";
import type { FormTemplate } from "@/lib/api";

export function PreviewModal({
  form,
  onClose,
}: {
  form: FormTemplate | null;
  onClose: () => void;
}) {
  useEffect(() => {
    if (!form) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [form, onClose]);

  if (!form) return null;
  const { meta, fields, signatories } = form;

  return (
    <div
      className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`Preview ${meta.code}`}
    >
      <div
        className="flex max-h-[85vh] w-full max-w-2xl flex-col overflow-hidden rounded-card bg-white shadow-hover"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-ink-200 px-6 py-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-bold brand-text">{meta.code}</span>
              <span className="rounded-full bg-brand-50 px-2 py-0.5 text-[11px] font-semibold text-brand-700">
                v{meta.version}
              </span>
              <span className="rounded-full bg-status-readyBg px-2 py-0.5 text-[11px] font-semibold text-status-ready">
                active
              </span>
            </div>
            <h2 className="mt-1 text-lg font-bold text-ink-900">{meta.name}</h2>
          </div>
          <button
            onClick={onClose}
            className="rounded-btn p-2 text-ink-500 transition hover:bg-ink-50 hover:text-ink-900"
            aria-label="Close preview"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {/* Meta info */}
          <div className="grid grid-cols-2 gap-3 text-sm">
            <InfoRow label="Nhóm nghiệp vụ" value={meta.business_group} />
            <InfoRow label="Đối tượng" value={meta.segment} />
            <InfoRow label="Loại hình DN" value={meta.org_type} />
            <InfoRow label="Ngày hiệu lực" value={meta.effective_date} />
            <InfoRow label="Người lập" value={meta.preparer} />
            <InfoRow label="Người ký" value={meta.signer} />
          </div>

          {/* Use case */}
          <div className="mt-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-ink-500">Trường hợp sử dụng</div>
            <p className="mt-1 text-sm text-ink-700">{meta.use_case}</p>
          </div>

          {/* Fields */}
          {fields.length > 0 && (
            <div className="mt-4">
              <div className="text-xs font-semibold uppercase tracking-wide text-ink-500">
                Trường biểu mẫu ({fields.length})
              </div>
              <div className="mt-2 overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-ink-200 text-left text-xs text-ink-500">
                      <th className="py-2 pr-3 font-medium">Label</th>
                      <th className="py-2 pr-3 font-medium">Key</th>
                      <th className="py-2 pr-3 font-medium">Type</th>
                      <th className="py-2 font-medium">Required</th>
                    </tr>
                  </thead>
                  <tbody>
                    {fields.map((f) => (
                      <tr key={f.key} className="border-b border-ink-100">
                        <td className="py-2 pr-3 text-ink-900">{f.label}</td>
                        <td className="py-2 pr-3 font-mono text-xs text-ink-700">{f.key}</td>
                        <td className="py-2 pr-3 text-ink-700">{f.type}</td>
                        <td className="py-2">
                          {f.required ? (
                            <span className="rounded bg-brand-50 px-1.5 text-[10px] font-bold text-brand-700">*</span>
                          ) : (
                            <span className="text-ink-200">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Signatories */}
          {signatories.length > 0 && (
            <div className="mt-4">
              <div className="text-xs font-semibold uppercase tracking-wide text-ink-500">Người ký</div>
              <div className="mt-2 space-y-1">
                {signatories.map((s, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-ink-700">
                    <span className="font-medium text-ink-900">{s.who}</span>
                    <span>·</span>
                    <span>{s.position}</span>
                    <span>·</span>
                    <span>{s.position_to_sign}</span>
                    {s.stamp && s.stamp !== "Không" && (
                      <span className="rounded bg-ink-50 px-1.5 text-[10px] text-ink-700">đóng dấu</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Accompanying docs */}
          {meta.accompanying_docs.length > 0 && (
            <div className="mt-4">
              <div className="text-xs font-semibold uppercase tracking-wide text-ink-500">Hồ sơ kèm theo</div>
              <ul className="mt-2 space-y-1">
                {meta.accompanying_docs.map((d, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-ink-700">
                    <span className="text-ink-200">📎</span>
                    {d}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-ink-500">{label}</div>
      <div className="font-medium text-ink-900">{value}</div>
    </div>
  );
}
