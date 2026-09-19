"use client";
import { useState, useRef, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { Logo } from "@/components/Logo";
import { StatusBadge } from "@/components/StatusBadge";
import { FormCard, type FormMeta } from "@/components/FormCard";
import { Checklist, type ChecklistItem } from "@/components/Checklist";
import { invoke, exportVintagePdf, type AgentResponse } from "@/lib/api";

type Msg = { role: "agent" | "user"; content: string };

const STEPS = [
  { n: "01", t: "Hiểu nhu cầu", d: "Natural language" },
  { n: "02", t: "Chọn mẫu MSB", d: "Form Registry" },
  { n: "03", t: "Điền hồ sơ", d: "Drafting Engine" },
  { n: "04", t: "Kiểm tra", d: "Validation" },
  { n: "05", t: "Ready / Missing / Review", d: "Checklist" },
];

const PERSONAS = [
  { tag: "CTCP X", d: "Thêm kế toán · Maker + Approver", prompt: "Công ty CP X muốn thêm kế toán vào eBank, kế toán lập lệnh, giám đốc duyệt" },
  { tag: "TNHH MTV Y", d: "Thay Giám đốc & người đại diện", prompt: "Công ty TNHH một thành viên Y muốn thay đổi người đại diện theo pháp luật và cập nhật thông tin tài khoản" },
  { tag: "TNHH 2TV Z", d: "Thuế điện tử + chữ ký số", prompt: "Công ty TNHH hai thành viên trở lên Z muốn đăng ký tài khoản MSB để nộp thuế điện tử và đăng ký chữ ký số Viettel-CA", main: true },
  { tag: "DNTN A", d: "Ủy quyền kế toán eBank", prompt: "DNTN A muốn ủy quyền cho kế toán sử dụng eBank để lập lệnh thanh toán" },
  { tag: "FDI Alpha 🌐", d: "Bilingual VI/EN · eBank + Maker/Approver", prompt: "Our company, Alpha Vietnam FDI Company Limited, has just opened an account with MSB. I would like our Vietnamese accountant to prepare payments, while I remain the final approver. Please prepare the required bilingual forms.", fdi: true },
  { tag: "Cá nhân A", d: "Đổi SĐT, email & eBank", prompt: "Cá nhân A muốn đổi số điện thoại và email đăng ký tài khoản MSB" },
];

const FDI_PROMPT =
  "Our company, Alpha Vietnam FDI Company Limited, has just opened an account with MSB. I would like our Vietnamese accountant to prepare payments, while I remain the final approver. Please prepare the required bilingual forms.";

export default function Page() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center bg-ink-50"><Navbar active="home" /></div>}>
      <PageContent />
    </Suspense>
  );
}

function PageContent() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: "agent", content: "Chào bạn! Tôi là MSB SmartForm AI — trợ lý lập hồ sơ & biểu mẫu. Hãy mô tả nhu cầu, hoặc bấm nút demo bên dưới." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState<FormMeta | null>(null);
  const [status, setStatus] = useState<string>("");
  const [checklist, setChecklist] = useState<ChecklistItem[]>([]);
  const [output, setOutput] = useState<Record<string, any> | null>(null);
  const [error, setError] = useState("");
  const [fileInfo, setFileInfo] = useState<{ filename: string; content: string; mime: string } | null>(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [sessionId, setSessionId] = useState(`web-${Date.now()}`);
  const endRef = useRef<HTMLDivElement>(null);
  const taRef = useRef<HTMLTextAreaElement>(null);
  const searchParams = useSearchParams();
  const aiFillHandled = useRef(false);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  useEffect(() => {
    const formCode = searchParams.get("form");
    if (formCode && !aiFillHandled.current && !loading) {
      aiFillHandled.current = true;
      const prompt = `Tôi muốn điền mẫu ${formCode}. Hãy giúp tôi hoàn thiện hồ sơ này.`;
      send(prompt);
    }
  }, [searchParams, loading]);

  async function send(text?: string, sid?: string) {
    const msg = (text ?? input).trim();
    if (!msg || loading) return;
    const useSid = sid || sessionId;
    setInput(""); setError("");
    setMessages((m) => [...m, { role: "user", content: msg }]);
    setLoading(true);
    try {
      const res = await invoke("chat", { message: msg, session_id: useSid });
      handle(res);
    } catch (e: any) {
      setError(e.message || "Lỗi kết nối Agent.");
    } finally {
      setLoading(false);
    }
  }

  function handle(res: AgentResponse) {
    if (res.selected_form) setForm(res.selected_form);
    if (res.status) setStatus(res.status);
    if (res.checklist) setChecklist(res.checklist);
    if (res.output) setOutput(res.output);
    if (res.file) setFileInfo(res.file);
    else if (res.status && res.status !== "READY") setFileInfo(null);
    let content: string;
    if (res.message) content = res.message;
    else if (res.question) content = res.question;
    else if (res.output) content = formatOutput(res.output);
    else content = "Đã xử lý.";
    if (res.file) content += "\n\n📎 Bản mềm đã sẵn sàng — bấm tải xuống bên cạnh.";
    setMessages((m) => [...m, { role: "agent", content }]);
  }

  function formatOutput(o: Record<string, any>): string {
    return [
      `✓ Mẫu: ${o.D_mau_bieu || ""}`,
      `✓ Nghiệp vụ: ${o.C_nghiep_vu || ""}`,
      `✓ Người ký: ${(o.H_nguoi_ky || []).map((s: any) => `${s.who} — ${s.position}`).join("; ")}`,
      `✓ STATUS: ${o.status || ""}`,
      `Gõ "SOẠN HỒ SƠ" để xuất bản xem trước + checklist.`,
    ].join("\n");
  }

  async function soanHoSo() {
    setLoading(true); setError("");
    setMessages((m) => [...m, { role: "user", content: "SOẠN HỒ SƠ" }]);
    try {
      const res = await invoke("soan_ho_so", { session_id: sessionId });
      if (res.checklist) setChecklist(res.checklist);
      if (res.status) setStatus(res.status);
      if (res.file) setFileInfo(res.file);
      let content = `Đã soạn hồ sơ. STATUS: ${res.status}. Xem checklist bên phải.`;
      if (res.file) content += "\n\n📎 Bản mềm đã sẵn sàng — bấm tải xuống bên cạnh.";
      setMessages((m) => [...m, { role: "agent", content }]);
    } catch (e: any) { setError(e.message || "Lỗi khi soạn hồ sơ."); }
    finally { setLoading(false); }
  }

  function downloadFile() {
    if (!fileInfo) return;
    const blob = new Blob([fileInfo.content], { type: fileInfo.mime || "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileInfo.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  async function downloadPdf() {
    if (!form) return;
    setPdfLoading(true);
    try {
      const res = await exportVintagePdf(form.code, sessionId);
      const link = document.createElement("a");
      link.href = res.pdf_base64;
      link.download = res.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e: any) {
      setError(e.message || "Lỗi khi xuất PDF.");
    } finally {
      setPdfLoading(false);
    }
  }

  function resetAll() {
    invoke("reset_session", { session_id: sessionId }).catch(() => {});
    const newSid = `web-${Date.now()}`;
    setSessionId(newSid);
    setMessages([
      { role: "agent", content: "Chào bạn! Tôi là MSB SmartForm AI — trợ lý lập hồ sơ & biểu mẫu. Hãy mô tả nhu cầu, hoặc bấm nút demo bên dưới." },
    ]);
    setForm(null);
    setStatus("");
    setChecklist([]);
    setOutput(null);
    setFileInfo(null);
    setError("");
    setInput("");
  }

  function startPersona(prompt: string) {
    const newSid = `persona-${Date.now()}`;
    setSessionId(newSid);
    setMessages([
      { role: "agent", content: "Chào bạn! Tôi là MSB SmartForm AI — trợ lý lập hồ sơ & biểu mẫu. Hãy mô tả nhu cầu, hoặc bấm nút demo bên dưới." },
    ]);
    setForm(null);
    setStatus("");
    setChecklist([]);
    setOutput(null);
    setFileInfo(null);
    setError("");
    send(prompt, newSid);
  }

  return (
    <div className="flex min-h-screen flex-col bg-ink-50">
      <Navbar active="home" />

      {/* 5-step solution strip (PPT slide 3) */}
      <div className="border-b border-ink-200 bg-white">
        <div className="mx-auto grid max-w-6xl grid-cols-2 gap-2 px-6 py-3 sm:grid-cols-3 lg:grid-cols-5">
          {STEPS.map((s) => (
            <div key={s.n} className="flex items-start gap-2">
              <span className="step-num brand-text text-lg font-extrabold">{s.n}</span>
              <div className="leading-tight">
                <div className="text-xs font-semibold text-ink-900">{s.t}</div>
                <div className="text-[10px] text-ink-500">{s.d}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Persona cards (PPT slide 4) */}
      <div className="border-b border-ink-200 bg-white">
        <div className="mx-auto flex max-w-6xl gap-2 overflow-x-auto px-6 py-2">
          {PERSONAS.map((p) => (
            <button
              key={p.tag}
              onClick={() => p.prompt && startPersona(p.prompt)}
              className={`flex shrink-0 items-center gap-2 rounded-btn border px-3 py-1.5 text-left text-xs transition ${
                p.main ? "border-brand bg-brand-50 hover:bg-brand-100"
                : p.fdi ? "border-purple-300 bg-purple-50 hover:bg-purple-100"
                : "border-ink-200 hover:border-ink-500"
              }`}
            >
              <Logo size={16} />
              <div className="leading-tight">
                <div className="font-bold text-ink-900">{p.tag}</div>
                <div className="text-[10px] text-ink-700">{p.d}</div>
              </div>
              {p.main && <span className="ml-1 rounded bg-brand px-1.5 py-0.5 text-[9px] font-bold text-white">DEMO</span>}
              {p.fdi && <span className="ml-1 rounded bg-purple-600 px-1.5 py-0.5 text-[9px] font-bold text-white">VI/EN</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Main: chat + side panel */}
      <div className="mx-auto grid w-full max-w-6xl flex-1 grid-cols-1 gap-4 p-4 lg:grid-cols-[1fr_360px]">
        {/* Chat */}
        <div className="flex flex-col rounded-card border border-ink-200 bg-white shadow-card">
          <div className="flex-1 space-y-3 overflow-y-auto p-4" style={{ maxHeight: "calc(100vh - 320px)" }}>
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm ${m.role === "user" ? "chat-user" : "chat-agent"}`}>
                  {m.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="chat-agent dot-typing rounded-2xl px-4 py-3">
                  <span className="mr-1 inline-block h-2 w-2 rounded-full bg-brand"> </span>
                  <span className="mr-1 inline-block h-2 w-2 rounded-full bg-brand"> </span>
                  <span className="inline-block h-2 w-2 rounded-full bg-brand"> </span>
                </div>
              </div>
            )}
            {error && <div className="rounded-btn bg-status-dangerBg px-4 py-2 text-sm text-status-danger">{error}</div>}
            <div ref={endRef} />
          </div>
          <div className="flex gap-2 border-t border-ink-200 p-3">
            <textarea
              ref={taRef}
              className="flex-1 resize-none rounded-btn border border-ink-200 px-4 py-2.5 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/30"
              placeholder="Nhập yêu cầu... (Enter để gửi, Shift+Enter để xuống dòng)"
              rows={1}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                const ta = e.target;
                ta.style.height = "auto";
                ta.style.height = Math.min(ta.scrollHeight, 120) + "px";
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                  if (taRef.current) taRef.current.style.height = "auto";
                }
              }}
              disabled={loading}
            />
            <button
              className="brand-bg rounded-btn px-5 py-2.5 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
              onClick={() => send()} disabled={loading || !input}
            >Gửi</button>
          </div>
        </div>

        {/* Side panel */}
        <aside className="space-y-3">
          {status && (
            <div className="rounded-card border border-ink-200 bg-white p-4 shadow-card">
              <div className="mb-2 text-sm font-bold text-ink-900">Trạng thái</div>
              <StatusBadge status={status} />
            </div>
          )}
          {form && (
            <div>
              <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-ink-500">Mẫu đã chọn</div>
              <FormCard form={form} />
            </div>
          )}
          {output && (
            <div className="rounded-card border border-ink-200 bg-white p-4 text-sm shadow-card">
              <div className="mb-2 font-bold text-ink-900">Hồ sơ đã điền</div>
              <dl className="space-y-1">
                {Object.entries(output.G_bieu_mau_dien || {}).map(([k, v]: any) => (
                  <div key={k} className="flex justify-between gap-2">
                    <dt className="text-ink-700">{k}</dt>
                    <dd className={`font-medium ${v === "[CẦN KHÁCH HÀNG CUNG CẤP]" ? "missing-field rounded px-1" : "text-ink-900"}`}>{String(v)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
          <Checklist items={checklist} />
          {fileInfo && (
            <div className="rounded-card border border-brand bg-brand-50 p-4 shadow-card">
              <div className="mb-2 text-sm font-bold text-ink-900">Bản mềm hồ sơ</div>
              <div className="mb-3 truncate text-xs text-ink-700">{fileInfo.filename}</div>
              <div className="grid grid-cols-2 gap-2">
                <button
                  className="brand-bg rounded-btn px-3 py-2.5 text-sm font-semibold text-white hover:bg-brand-600"
                  onClick={downloadFile}
                >⬇ Tải Text</button>
                <button
                  className="flex items-center justify-center gap-1 rounded-btn border border-brand bg-white px-3 py-2.5 text-sm font-semibold text-brand hover:bg-brand-50 disabled:opacity-50"
                  onClick={downloadPdf}
                  disabled={pdfLoading || !form}
                >
                  {pdfLoading ? (
                    <><span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-brand border-t-transparent" /> Đang xuất...</>
                  ) : (
                    <>⬇ Tải PDF</>
                  )}
                </button>
              </div>
              <p className="mt-2 text-[10px] text-ink-500">PDF vintage — font tiếng Việt đầy đủ, thiết kế cổ điển.</p>
            </div>
          )}
          {form && (
            <div className="space-y-2">
              <button
                className="brand-bg w-full rounded-btn px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
                onClick={soanHoSo} disabled={loading}
              >SOẠN HỒ SƠ</button>
              <button
                className="w-full rounded-btn border border-status-danger bg-white px-4 py-2.5 text-sm font-semibold text-status-danger transition hover:bg-status-dangerBg disabled:opacity-50"
                onClick={resetAll} disabled={loading}
              >↻ Xoá thông tin cũ, thực hiện lại</button>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
