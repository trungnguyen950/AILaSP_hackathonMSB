"use client";
import { useState } from "react";
import type { Block } from "@/lib/guide-content";

const calloutStyles = {
  info: { bg: "bg-navy-50", border: "border-navy-500", text: "text-navy-900", icon: "ℹ️", label: "Info" },
  warning: { bg: "bg-status-missingBg", border: "border-status-missing", text: "text-amber-900", icon: "⚠️", label: "Lưu ý" },
  tip: { bg: "bg-status-readyBg", border: "border-status-ready", text: "text-status-ready", icon: "💡", label: "Mẹo" },
  danger: { bg: "bg-status-dangerBg", border: "border-status-danger", text: "text-status-danger", icon: "🚫", label: "Quan trọng" },
};

function Callout({ variant, title, text }: { variant: "info" | "warning" | "tip" | "danger"; title?: string; text: string }) {
  const s = calloutStyles[variant];
  return (
    <div className={`my-4 rounded-card border-l-4 ${s.border} ${s.bg} p-4`}>
      <div className={`flex items-center gap-2 text-sm font-bold ${s.text}`}>
        <span>{s.icon}</span>
        <span>{title || s.label}</span>
      </div>
      <p className={`mt-1 text-sm ${s.text} opacity-90`}>{text}</p>
    </div>
  );
}

function StepList({ items }: { items: { title: string; desc: string }[] }) {
  return (
    <ol className="my-5 space-y-3">
      {items.map((step, i) => (
        <li key={i} className="flex gap-3">
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand text-sm font-bold text-white">
            {i + 1}
          </span>
          <div className="flex-1 rounded-btn border border-ink-200 bg-white p-3 shadow-card">
            <div className="text-sm font-semibold text-ink-900">{step.title}</div>
            <p className="mt-0.5 text-sm text-ink-700">{step.desc}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}

function CodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard?.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <div className="group relative my-4">
      <button
        onClick={copy}
        className="absolute right-2 top-2 rounded-btn border border-ink-200 bg-white px-2 py-1 text-xs text-ink-700 opacity-0 transition hover:text-ink-900 group-hover:opacity-100"
        aria-label="Copy code"
      >
        {copied ? "✓ Copied" : "Copy"}
      </button>
      <pre className="overflow-x-auto rounded-btn bg-navy-900 p-4 text-sm text-white/90">
        <code className="font-mono">{code}</code>
      </pre>
    </div>
  );
}

function DataTable({ headers, rows }: { headers: string[]; rows: string[][] }) {
  return (
    <div className="my-4 overflow-x-auto rounded-btn border border-ink-200">
      <table className="w-full text-sm">
        <thead className="bg-ink-50">
          <tr>
            {headers.map((h, i) => (
              <th key={i} className="px-3 py-2.5 text-left font-semibold text-ink-900">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-ink-200">
          {rows.map((row, i) => (
            <tr key={i} className="hover:bg-ink-50">
              {row.map((cell, j) => (
                <td key={j} className={`px-3 py-2 ${j === 0 ? "font-medium text-ink-900" : "text-ink-700"}`}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function FAQ({ items }: { items: { q: string; a: string }[] }) {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <div className="my-5 space-y-2">
      {items.map((item, i) => (
        <div key={i} className="rounded-btn border border-ink-200 bg-white">
          <button
            onClick={() => setOpen(open === i ? null : i)}
            className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-semibold text-ink-900"
            aria-expanded={open === i}
          >
            <span>{item.q}</span>
            <span className={`text-ink-500 transition ${open === i ? "rotate-180" : ""}`}>▾</span>
          </button>
          {open === i && (
            <div className="border-t border-ink-200 px-4 py-3 text-sm text-ink-700">{item.a}</div>
          )}
        </div>
      ))}
    </div>
  );
}

function NextSteps({ items }: { items: { label: string; href: string }[] }) {
  return (
    <div className="my-6 rounded-card border border-brand/30 bg-brand-50 p-4">
      <div className="mb-2 text-sm font-bold text-ink-900">Bước tiếp theo</div>
      <div className="flex flex-wrap gap-2">
        {items.map((item, i) => (
          <a
            key={i}
            href={item.href}
            className="inline-flex items-center gap-1 rounded-btn border border-brand bg-white px-3 py-1.5 text-sm font-semibold text-brand transition hover:bg-brand hover:text-white"
          >
            {item.label} →
          </a>
        ))}
      </div>
    </div>
  );
}

export function BlockRenderer({ blocks }: { blocks: Block[] }) {
  return (
    <div>
      {blocks.map((block, i) => {
        switch (block.type) {
          case "h2":
            return <h2 key={i} id={block.anchor} className="mt-8 mb-3 scroll-mt-20 text-xl font-extrabold text-ink-900">{block.text}</h2>;
          case "h3":
            return <h3 key={i} id={block.anchor} className="mt-6 mb-2 scroll-mt-20 text-lg font-bold text-ink-900">{block.text}</h3>;
          case "p":
            return <p key={i} className="my-3 text-sm leading-relaxed text-ink-700">{block.text}</p>;
          case "code":
            return <CodeBlock key={i} code={block.code} />;
          case "callout":
            return <Callout key={i} variant={block.variant} title={block.title} text={block.text} />;
          case "steps":
            return <StepList key={i} items={block.items} />;
          case "table":
            return <DataTable key={i} headers={block.headers} rows={block.rows} />;
          case "list":
            return block.ordered ? (
              <ol key={i} className="my-3 list-decimal space-y-1 pl-6 text-sm text-ink-700">
                {block.items.map((it, j) => <li key={j}>{it}</li>)}
              </ol>
            ) : (
              <ul key={i} className="my-3 list-disc space-y-1 pl-6 text-sm text-ink-700">
                {block.items.map((it, j) => <li key={j}>{it}</li>)}
              </ul>
            );
          case "faq":
            return <FAQ key={i} items={block.items} />;
          case "nextSteps":
            return <NextSteps key={i} items={block.items} />;
          default:
            return null;
        }
      })}
    </div>
  );
}
