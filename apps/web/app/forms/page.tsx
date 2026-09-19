"use client";
import { useState, useEffect, useMemo, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { PreviewModal } from "@/components/PreviewModal";
import { listForms, getForm, exportFormPdf, type FormMeta, type FormTemplate } from "@/lib/api";

const GROUP_ICON: Record<string, string> = {
  eBank: "🏦",
  "Tài khoản": "📋",
  "Chữ ký số": "🔐",
  "Thuế điện tử": "🧾",
};

const GROUP_COLOR: Record<string, string> = {
  eBank: "bg-blue-50 text-blue-700",
  "Tài khoản": "bg-amber-50 text-amber-700",
  "Chữ ký số": "bg-purple-50 text-purple-700",
  "Thuế điện tử": "bg-emerald-50 text-emerald-700",
};

function iconFor(group: string) {
  return GROUP_ICON[group] || "📄";
}
function colorFor(group: string) {
  return GROUP_COLOR[group] || "bg-ink-100 text-ink-700";
}

function downloadFormText(tpl: FormTemplate) {
  const lines = [
    "=".repeat(60),
    `  MSB SmartForm AI — Template: ${tpl.meta.code}`,
    "=".repeat(60),
    "",
    `Mã mẫu:          ${tpl.meta.code}`,
    `Tên mẫu:         ${tpl.meta.name}`,
    `Nhóm nghiệp vụ:  ${tpl.meta.business_group}`,
    `Đối tượng:       ${tpl.meta.segment}`,
    `Phiên bản:       ${tpl.meta.version}`,
    `Ngày hiệu lực:  ${tpl.meta.effective_date}`,
    `Trường hợp:      ${tpl.meta.use_case}`,
    `Người lập:       ${tpl.meta.preparer}`,
    `Người ký:        ${tpl.meta.signer}`,
    "",
    "─".repeat(60),
    "  TRƯỜNG BIỂU MẪU",
    "─".repeat(60),
    "",
  ];
  tpl.fields.forEach((f, i) => {
    const req = f.required ? "*" : " ";
    lines.push(`  ${req} ${f.label} (${f.key}) — type: ${f.type}${f.required ? " [bắt buộc]" : ""}`);
  });
  if (tpl.signatories.length) {
    lines.push("", "─".repeat(60), "  NGƯỜI KÝ", "─".repeat(60), "");
    tpl.signatories.forEach((s) => {
      lines.push(`  - ${s.who} — ${s.position} — ${s.position_to_sign}`);
    });
  }
  if (tpl.meta.accompanying_docs.length) {
    lines.push("", "─".repeat(60), "  HỒ SƠ KÈM THEO", "─".repeat(60), "");
    tpl.meta.accompanying_docs.forEach((d) => lines.push(`  - ${d}`));
  }
  lines.push("", "=".repeat(60), "  Dữ liệu giả lập — không dùng cho giao dịch thật.", "=".repeat(60));

  const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${tpl.meta.code}_template.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function FormsPage() {
  const router = useRouter();
  const [forms, setForms] = useState<FormMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [groupFilter, setGroupFilter] = useState("all");
  const [previewForm, setPreviewForm] = useState<FormTemplate | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [downloadingCode, setDownloadingCode] = useState<string | null>(null);
  const [downloadingPdfCode, setDownloadingPdfCode] = useState<string | null>(null);

  useEffect(() => {
    listForms()
      .then((data) => {
        setForms(data);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message || "Không thể tải danh sách biểu mẫu.");
        setLoading(false);
      });
  }, []);

  const groups = useMemo(() => {
    const set = new Set(forms.map((f) => f.business_group));
    return ["all", ...Array.from(set)];
  }, [forms]);

  const filtered = useMemo(() => {
    return forms.filter((f) => {
      if (groupFilter !== "all" && f.business_group !== groupFilter) return false;
      if (search) {
        const q = search.toLowerCase();
        return (
          f.name.toLowerCase().includes(q) ||
          f.code.toLowerCase().includes(q) ||
          f.use_case.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [forms, search, groupFilter]);

  const handlePreview = useCallback(async (code: string) => {
    setPreviewLoading(true);
    try {
      const tpl = await getForm(code);
      setPreviewForm(tpl);
    } catch (e: any) {
      setError(e.message || "Không thể tải chi tiết mẫu.");
    } finally {
      setPreviewLoading(false);
    }
  }, []);

  const handleDownload = useCallback(async (code: string) => {
    setDownloadingCode(code);
    try {
      const tpl = await getForm(code);
      downloadFormText(tpl);
    } catch (e: any) {
      setError(e.message || "Không thể tải file.");
    } finally {
      setDownloadingCode(null);
    }
  }, []);

  const handleDownloadPdf = useCallback(async (code: string) => {
    setDownloadingPdfCode(code);
    try {
      const res = await exportFormPdf(code);
      const link = document.createElement("a");
      link.href = res.pdf_base64;
      link.download = res.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e: any) {
      setError(e.message || "Không thể tải PDF.");
    } finally {
      setDownloadingPdfCode(null);
    }
  }, []);

  const handleAIFill = useCallback(
    (code: string) => {
      router.push(`/?form=${encodeURIComponent(code)}`);
    },
    [router]
  );

  return (
    <div className="flex min-h-screen flex-col bg-ink-50">
      <Navbar active="forms" />

      {/* Page header */}
      <div className="border-b border-ink-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-8">
          <h1 className="text-2xl font-extrabold text-ink-900">📋 Thư Viện Biểu Mẫu</h1>
          <p className="mt-1 text-sm text-ink-700">
            Tổng hợp các form và template sẵn có — tải xuống, xem trước, hoặc yêu cầu AI điền giúp.
          </p>
        </div>
      </div>

      {/* Search + filter */}
      <div className="border-b border-ink-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-3 px-6 py-3">
          <div className="relative flex-1 min-w-[200px]">
            <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-500">🔍</span>
            <input
              type="text"
              placeholder="Tìm theo tên, mã, mô tả..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-btn border border-ink-200 py-2 pl-9 pr-4 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/30"
            />
          </div>
          <select
            value={groupFilter}
            onChange={(e) => setGroupFilter(e.target.value)}
            className="rounded-btn border border-ink-200 px-3 py-2 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/30"
            aria-label="Filter by category"
          >
            {groups.map((g) => (
              <option key={g} value={g}>
                {g === "all" ? "Tất cả nhóm" : g}
              </option>
            ))}
          </select>
          <span className="text-xs text-ink-500">
            {filtered.length} / {forms.length} mẫu
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="mx-auto w-full max-w-6xl flex-1 p-6">
        {error && (
          <div className="mb-4 rounded-btn bg-status-dangerBg px-4 py-3 text-sm text-status-danger">
            {error}
          </div>
        )}

        {/* Loading skeleton */}
        {loading && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-card border border-ink-200 bg-white p-5">
                <div className="skeleton h-8 w-8 rounded-lg" />
                <div className="skeleton mt-4 h-5 w-3/4 rounded" />
                <div className="skeleton mt-2 h-3 w-full rounded" />
                <div className="skeleton mt-1 h-3 w-2/3 rounded" />
                <div className="skeleton mt-4 h-6 w-20 rounded-full" />
                <div className="mt-4 space-y-2">
                  <div className="skeleton h-8 rounded-btn" />
                  <div className="skeleton h-8 rounded-btn" />
                  <div className="skeleton h-8 rounded-btn" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && filtered.length === 0 && !error && (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="text-6xl opacity-50">📂</div>
            <p className="mt-4 text-lg font-semibold text-ink-900">Chưa có biểu mẫu nào</p>
            <p className="mt-1 text-sm text-ink-700">
              {search || groupFilter !== "all"
                ? "Thử bỏ bộ lọc hoặc từ khóa tìm kiếm khác."
                : "Kiểm tra kết nối đến Agent."}
            </p>
          </div>
        )}

        {/* Forms grid */}
        {!loading && filtered.length > 0 && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((form) => (
              <div
                key={form.code}
                className="card-lift flex flex-col rounded-card border border-ink-200 bg-white p-5 shadow-card"
              >
                {/* Icon + version */}
                <div className="flex items-start justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-ink-50 text-xl">
                    {iconFor(form.business_group)}
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="rounded-full bg-brand-50 px-2 py-0.5 text-[11px] font-semibold text-brand-700">
                      v{form.version}
                    </span>
                    {form.active && (
                      <span className="rounded-full bg-status-readyBg px-2 py-0.5 text-[11px] font-semibold text-status-ready">
                        active
                      </span>
                    )}
                  </div>
                </div>

                {/* Title */}
                <h3 className="mt-3 text-sm font-bold text-ink-900" title={form.name}>
                  <span className="font-mono brand-text">{form.code}</span>
                  <span className="mx-1 text-ink-200">·</span>
                  <span className="line-clamp-2">{form.name}</span>
                </h3>

                {/* Description */}
                <p className="mt-1.5 line-clamp-2 text-xs text-ink-700">{form.use_case}</p>

                {/* Category badge + segment */}
                <div className="mt-3 flex flex-wrap items-center gap-1.5">
                  <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${colorFor(form.business_group)}`}>
                    {form.business_group}
                  </span>
                  <span className="rounded-full bg-ink-50 px-2 py-0.5 text-[10px] font-medium text-ink-700">
                    {form.segment}
                  </span>
                  <span className="rounded-full bg-ink-50 px-2 py-0.5 text-[10px] font-medium text-ink-700">
                    HL: {form.effective_date}
                  </span>
                </div>

                {/* Action buttons */}
                <div className="mt-4 space-y-2 border-t border-ink-100 pt-4">
                  {/* Download TXT + PDF (2 cột) */}
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => handleDownload(form.code)}
                      disabled={downloadingCode === form.code}
                      className="flex w-full items-center justify-center gap-1 rounded-btn border border-ink-200 px-2 py-2 text-xs font-semibold text-ink-700 transition hover:border-ink-500 hover:bg-ink-50 disabled:opacity-50"
                      aria-label={`Download ${form.code} text`}
                    >
                      {downloadingCode === form.code ? "⏳" : "⬇"} Text
                    </button>
                    <button
                      onClick={() => handleDownloadPdf(form.code)}
                      disabled={downloadingPdfCode === form.code}
                      className="flex w-full items-center justify-center gap-1 rounded-btn border border-brand bg-brand-50 px-2 py-2 text-xs font-semibold text-brand transition hover:bg-brand-100 disabled:opacity-50"
                      aria-label={`Download ${form.code} PDF`}
                    >
                      {downloadingPdfCode === form.code ? "⏳" : "⬇"} PDF
                    </button>
                  </div>

                  {/* Preview */}
                  <button
                    onClick={() => handlePreview(form.code)}
                    disabled={previewLoading}
                    className="flex w-full items-center justify-center gap-2 rounded-btn px-3 py-2 text-xs font-semibold text-ink-700 transition hover:bg-ink-50 disabled:opacity-50"
                    aria-label={`Preview ${form.code}`}
                  >
                    {previewLoading ? "⏳ Đang mở..." : "👁 Xem Trước"}
                  </button>

                  {/* AI Fill */}
                  <button
                    onClick={() => handleAIFill(form.code)}
                    className="ai-gradient ai-pulse flex w-full items-center justify-center gap-2 rounded-btn px-3 py-2 text-xs font-bold text-white transition"
                    aria-label={`AI Fill ${form.code}`}
                  >
                    🤖 AI Fill
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <PreviewModal form={previewForm} onClose={() => setPreviewForm(null)} />
    </div>
  );
}
