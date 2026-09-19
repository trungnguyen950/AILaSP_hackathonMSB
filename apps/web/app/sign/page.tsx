"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import { Navbar } from "@/components/Navbar";
import { SignaturePad, type SignaturePadRef } from "@/components/SignaturePad";
import {
  listForms,
  mockSignDocument,
  uploadAndCheck,
  signUploadedFile,
  sendZaloNotification,
  type FormMeta,
  type MockCert,
  type SignResult,
  type UploadCheckResult,
  type SignFileResult,
  type ZaloNotificationResult,
} from "@/lib/api";

const MOCK_CERTS: MockCert[] = [
  { certId: "MOCK-CERT-001", subject: "CN=Nguyễn Văn X, O=Công ty CP X, C=VN", issuer: "Viettel-CA", validFrom: "2024-01-01", validTo: "2026-12-31" },
  { certId: "FPT-CA", subject: "CN=Nguyễn Văn A, O=Cá nhân, C=VN", issuer: "FPT-CA", validFrom: "2024-03-15", validTo: "2025-03-15" },
];

const MAX_FILE_SIZE = 5 * 1024 * 1024;

type Phase = "idle" | "uploading" | "ai_checking" | "signing" | "done" | "error";

export default function SignPage() {
  const [forms, setForms] = useState<FormMeta[]>([]);
  const [selectedCode, setSelectedCode] = useState("");
  const [selectedCert, setSelectedCert] = useState(0);
  const [phase, setPhase] = useState<Phase>("idle");
  const [error, setError] = useState("");
  const [result, setResult] = useState<SignResult | null>(null);
  const [fileResult, setFileResult] = useState<SignFileResult | null>(null);
  const [checkResult, setCheckResult] = useState<UploadCheckResult | null>(null);

  // Zalo notification state
  const [zaloResult, setZaloResult] = useState<ZaloNotificationResult | null>(null);
  const [zaloSending, setZaloSending] = useState(false);
  const [zaloError, setZaloError] = useState("");

  // File upload state
  const [file, setFile] = useState<File | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const sigRef = useRef<SignaturePadRef>(null);

  useEffect(() => {
    listForms().then((data) => {
      setForms(data);
      if (data.length > 0) setSelectedCode(data[0].code);
    }).catch((e) => setError(e.message || "Không thể tải danh sách mẫu."));
  }, []);

  const selectedForm = forms.find((f) => f.code === selectedCode);

  // --- File handling ---
  const handleFileSelect = useCallback((f: File) => {
    setError("");
    setCheckResult(null);
    setFileResult(null);
    setPhase("idle");

    const ext = f.name.split(".").pop()?.toLowerCase();
    if (!ext || !["txt", "pdf"].includes(ext)) {
      setError("Định dạng không hỗ trợ. Chỉ chấp nhận .txt hoặc .pdf");
      return;
    }
    if (f.size > MAX_FILE_SIZE) {
      setError(`File quá lớn (${(f.size / 1024 / 1024).toFixed(1)}MB). Tối đa 5MB.`);
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setFile(f);
      setFileContent(reader.result as string);
    };
    reader.readAsDataURL(f);
  }, []);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files[0]) handleFileSelect(e.dataTransfer.files[0]);
  };

  // --- AI Check ---
  const handleAICheck = async () => {
    if (!file || !fileContent || !selectedCode) return;
    setPhase("ai_checking");
    setError("");
    try {
      const res = await uploadAndCheck(file.name, fileContent, selectedCode);
      setCheckResult(res);
      if (!res.authentic) {
        setPhase("error");
        setError(`AI check: File không hợp lệ (score: ${res.score}/100). ${res.llm_verdict?.reason || ""}`);
      } else {
        setPhase("idle");
      }
    } catch (e: any) {
      setPhase("error");
      setError(e.message || "Lỗi AI check.");
    }
  };

  // --- Sign uploaded file ---
  const handleSignUploaded = async () => {
    if (!file || !fileContent || !selectedCode) return;
    if (sigRef.current?.isEmpty()) {
      setError("Vui lòng vẽ chữ ký.");
      return;
    }
    setPhase("signing");
    setError("");
    try {
      const sig = sigRef.current!.toDataURL();
      const res = await signUploadedFile(file.name, fileContent, sig, MOCK_CERTS[selectedCert], selectedCode);
      setFileResult(res);
      setPhase("done");
    } catch (e: any) {
      setPhase("error");
      setError(e.message || "Lỗi khi ký file.");
    }
  };

  // --- Sign generated PDF (existing flow) ---
  const handleSignGenerated = async () => {
    if (sigRef.current?.isEmpty()) {
      setError("Vui lòng vẽ chữ ký.");
      return;
    }
    if (!selectedCode) return;
    setPhase("signing");
    setError("");
    try {
      const sig = sigRef.current!.toDataURL();
      const docId = `DOC-${selectedCode}-${Date.now().toString(36).toUpperCase()}`;
      const res = await mockSignDocument(docId, sig, MOCK_CERTS[selectedCert], selectedCode);
      setResult(res);
      setPhase("done");
    } catch (e: any) {
      setPhase("error");
      setError(e.message || "Lỗi khi ký.");
    } finally {
      if (phase !== "done") setPhase("idle");
    }
  };

  const downloadSignedFile = () => {
    if (!fileResult) return;
    const link = document.createElement("a");
    link.href = fileResult.signed_file_base64;
    link.download = fileResult.signed_filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadSignedPdf = () => {
    if (!fileResult?.vintage_pdf_base64) return;
    const link = document.createElement("a");
    link.href = fileResult.vintage_pdf_base64;
    link.download = fileResult.vintage_pdf_filename || "signed_vintage.pdf";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadGeneratedPdf = () => {
    if (!result) return;
    const link = document.createElement("a");
    link.href = result.signed_pdf_base64;
    link.download = `${result.document_id}_signed.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // --- Send Zalo notification + signed PDF to customer ---
  const handleSendZalo = async () => {
    setZaloError("");
    setZaloResult(null);
    setZaloSending(true);
    try {
      let pdfBase64 = "";
      let filename = "signed.pdf";
      let documentId = "";
      let formCode = selectedCode;
      let signedHash = "";
      let signedBy = "";

      if (fileResult) {
        pdfBase64 = fileResult.vintage_pdf_base64 || fileResult.signed_file_base64;
        filename = fileResult.vintage_pdf_filename || fileResult.signed_filename;
        signedHash = fileResult.signed_hash;
        signedBy = MOCK_CERTS[selectedCert].subject;
        documentId = (fileResult.webhook as any)?.documentId || "";
        formCode = (fileResult.webhook as any)?.formCode || selectedCode;
      } else if (result) {
        pdfBase64 = result.signed_pdf_base64;
        filename = `${result.document_id}_signed.pdf`;
        documentId = result.document_id;
        signedHash = result.signed_hash;
        signedBy = result.webhook?.signedBy || MOCK_CERTS[selectedCert].subject;
        formCode = result.webhook?.formCode || selectedCode;
      }

      if (!pdfBase64) {
        throw new Error("Không có PDF đã ký để gửi.");
      }

      const res = await sendZaloNotification({
        pdf_base64: pdfBase64,
        filename,
        document_id: documentId,
        form_code: formCode,
        signed_hash: signedHash,
        signed_by: signedBy,
      });
      setZaloResult(res);
      if (res.status === "error") {
        setZaloError(res.message || res.error || "Gửi Zalo thất bại.");
      }
    } catch (e: any) {
      setZaloError(e.message || "Lỗi khi gửi thông báo Zalo.");
    } finally {
      setZaloSending(false);
    }
  };

  const reset = () => {
    setPhase("idle");
    setError("");
    setResult(null);
    setFileResult(null);
    setCheckResult(null);
    setFile(null);
    setFileContent("");
    setZaloResult(null);
    setZaloError("");
    setZaloSending(false);
    sigRef.current?.clear();
  };

  return (
    <div className="flex min-h-screen flex-col bg-ink-50">
      <Navbar active="sign" />

      <div className="border-b border-ink-200 bg-white">
        <div className="mx-auto max-w-4xl px-6 py-8">
          <h1 className="text-2xl font-extrabold text-ink-900">✍️ Ký Chữ Ký Số (Mô Phỏng)</h1>
          <p className="mt-1 text-sm text-ink-700">
            Upload file biểu mẫu → AI kiểm tra → Ký số → Tải file đã ký. Hoặc ký PDF tạo sẵn từ form.
          </p>
        </div>
      </div>

      <div className="mx-auto w-full max-w-4xl flex-1 p-6">
        {error && (
          <div className="mb-4 rounded-btn bg-status-dangerBg px-4 py-3 text-sm text-status-danger">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Left column */}
          <div className="space-y-4">
            {/* Form + cert selection */}
            <div className="rounded-card border border-ink-200 bg-white p-5 shadow-card">
              <h2 className="text-sm font-bold text-ink-900">1. Chọn biểu mẫu & chứng thư số</h2>
              <select
                value={selectedCode}
                onChange={(e) => setSelectedCode(e.target.value)}
                className="mt-3 w-full rounded-btn border border-ink-200 px-3 py-2 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/30"
              >
                {forms.map((f) => (
                  <option key={f.code} value={f.code}>{f.code} — {f.name}</option>
                ))}
              </select>
              <select
                value={selectedCert}
                onChange={(e) => setSelectedCert(Number(e.target.value))}
                className="mt-2 w-full rounded-btn border border-ink-200 px-3 py-2 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/30"
              >
                {MOCK_CERTS.map((c, i) => (
                  <option key={c.certId} value={i}>{c.certId} — {c.issuer}</option>
                ))}
              </select>
              {selectedForm && (
                <div className="mt-2 text-xs text-ink-700">
                  {selectedForm.business_group} · v{selectedForm.version} · {selectedForm.segment}
                  {selectedForm.bilingual && <span className="ml-1 rounded bg-purple-100 px-1.5 text-purple-700">VI/EN</span>}
                </div>
              )}
            </div>

            {/* File upload */}
            <div className="rounded-card border border-ink-200 bg-white p-5 shadow-card">
              <h2 className="text-sm font-bold text-ink-900">2. Upload file biểu mẫu</h2>
              <p className="mt-1 text-xs text-ink-700">Hỗ trợ .txt và .pdf (tối đa 5MB)</p>

              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`mt-3 cursor-pointer rounded-btn border-2 border-dashed p-6 text-center transition ${
                  dragOver ? "border-brand bg-brand-50" : "border-ink-200 hover:border-ink-500"
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt,.pdf"
                  className="hidden"
                  onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                />
                {file ? (
                  <div>
                    <div className="text-2xl">{file.name.endsWith(".pdf") ? "📄" : "📝"}</div>
                    <div className="mt-1 text-sm font-medium text-ink-900">{file.name}</div>
                    <div className="text-xs text-ink-500">{(file.size / 1024).toFixed(1)} KB</div>
                  </div>
                ) : (
                  <div>
                    <div className="text-2xl opacity-50">📁</div>
                    <div className="mt-1 text-sm text-ink-700">Kéo thả file hoặc click để chọn</div>
                    <div className="text-xs text-ink-500">.txt hoặc .pdf</div>
                  </div>
                )}
              </div>

              {file && (
                <button
                  onClick={() => { setFile(null); setFileContent(""); setCheckResult(null); setFileResult(null); }}
                  className="mt-2 text-xs text-ink-500 hover:text-status-danger"
                >
                  🗎 Xóa file
                </button>
              )}

              {/* AI Check button + result */}
              {file && !checkResult && (
                <button
                  onClick={handleAICheck}
                  disabled={phase === "ai_checking"}
                  className="mt-3 flex w-full items-center justify-center gap-2 rounded-btn border border-navy-100 bg-navy-50 px-3 py-2 text-xs font-bold text-navy-900 transition hover:bg-navy-100 disabled:opacity-50"
                >
                  {phase === "ai_checking" ? (
                    <><span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-navy-900 border-t-transparent" /> AI đang kiểm tra...</>
                  ) : (
                    <>🤖 AI Kiểm Tra File</>
                  )}
                </button>
              )}

              {checkResult && (
                <div className={`mt-3 rounded-btn p-3 text-xs ${checkResult.authentic ? "bg-status-readyBg text-status-ready" : "bg-status-dangerBg text-status-danger"}`}>
                  <div className="font-bold">
                    {checkResult.authentic ? "✅ File hợp lệ" : "❌ File không hợp lệ"} (score: {checkResult.score}/100)
                  </div>
                  <div className="mt-1 space-y-0.5">
                    {checkResult.checks.map((c, i) => (
                      <div key={i} className="flex items-center gap-1">
                        <span>{c.pass ? "✓" : "✗"}</span>
                        <span className="text-ink-700">{c.check}</span>
                      </div>
                    ))}
                  </div>
                  {checkResult.llm_verdict && (
                    <div className="mt-1 italic text-ink-700">AI: {checkResult.llm_verdict.reason}</div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Right column: signature + actions */}
          <div className="space-y-4">
            <div className="rounded-card border border-ink-200 bg-white p-5 shadow-card">
              <h2 className="text-sm font-bold text-ink-900">3. Vẽ chữ ký</h2>
              <p className="mt-1 text-xs text-ink-700">Dùng chuột hoặc ngón tay để ký</p>
              <div className="mt-3">
                <SignaturePad ref={sigRef} />
              </div>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-[11px] text-ink-500">{sigRef.current?.isEmpty() !== false ? "Chưa ký" : "Đã ký"}</span>
                <button
                  onClick={() => sigRef.current?.clear()}
                  className="rounded-btn border border-ink-200 px-3 py-1.5 text-xs font-semibold text-ink-700 transition hover:bg-ink-50"
                >
                  🗑 Xóa
                </button>
              </div>
            </div>

            {/* Action buttons */}
            <div className="space-y-2">
              {/* Sign uploaded file */}
              {file && checkResult?.authentic && (
                <button
                  onClick={handleSignUploaded}
                  disabled={phase === "signing"}
                  className="ai-gradient ai-pulse flex w-full items-center justify-center gap-2 rounded-card px-4 py-4 text-base font-bold text-white transition disabled:opacity-50"
                >
                  {phase === "signing" ? (
                    <><span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" /> Đang ký file...</>
                  ) : (
                    <>✍️ Ký File Đã Upload</>
                  )}
                </button>
              )}

              {/* Sign generated PDF (no upload needed) */}
              {!file && (
                <button
                  onClick={handleSignGenerated}
                  disabled={phase === "signing"}
                  className="ai-gradient ai-pulse flex w-full items-center justify-center gap-2 rounded-card px-4 py-4 text-base font-bold text-white transition disabled:opacity-50"
                >
                  {phase === "signing" ? (
                    <><span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" /> Đang ký...</>
                  ) : (
                    <>✍️ Ký PDF Tạo Sẵn (từ form)</>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Results */}
        {(result || fileResult) && phase === "done" && (
          <div className="mt-6 animate-pop rounded-card border border-status-ready bg-status-readyBg p-6 shadow-card">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl">✅</span>
                <h2 className="text-lg font-bold text-status-ready">Ký số thành công!</h2>
              </div>
              <button onClick={reset} className="rounded-btn border border-ink-200 px-3 py-1.5 text-xs text-ink-700 hover:bg-white">
                ↻ Ký file khác
              </button>
            </div>

            {fileResult && (
              <>
                <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div className="rounded-btn bg-white p-4">
                    <div className="text-xs font-semibold uppercase tracking-wide text-ink-500">File đã ký</div>
                    <div className="mt-1 font-mono text-sm text-ink-900">{fileResult.signed_filename}</div>
                  </div>
                  <div className="rounded-btn bg-white p-4">
                    <div className="text-xs font-semibold uppercase tracking-wide text-ink-500">SHA256 Hash</div>
                    <div className="mt-1 break-all font-mono text-xs text-ink-900">{fileResult.signed_hash}</div>
                  </div>
                </div>
                <div className="mt-4 rounded-btn bg-white p-4">
                  <div className="text-xs font-semibold uppercase tracking-wide text-ink-500">Webhook → AI Agent</div>
                  <pre className="mt-2 overflow-x-auto rounded-btn bg-ink-50 p-3 text-xs text-ink-700">
{JSON.stringify(fileResult.webhook, null, 2)}
                  </pre>
                </div>
                <div className="mt-4 rounded-btn border border-navy-100 bg-navy-50 p-4">
                  <div className="flex items-start gap-2">
                    <span className="text-status-ready">✓</span>
                    <div className="text-sm text-ink-900">
                      <div className="font-medium">{fileResult.agent_ack.message}</div>
                      <div className="mt-1 text-xs text-ink-700">Next: {fileResult.agent_ack.nextStep}</div>
                    </div>
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
                  <button
                    onClick={downloadSignedFile}
                    className="flex w-full items-center justify-center gap-2 rounded-btn border border-status-ready bg-white px-4 py-3 text-sm font-bold text-status-ready transition hover:bg-status-readyBg"
                  >
                    ⬇ Tải file gốc ({fileResult.file_type})
                  </button>
                  <button
                    onClick={handleSendZalo}
                    disabled={zaloSending}
                    className="flex w-full items-center justify-center gap-2 rounded-btn border border-brand bg-brand-50 px-4 py-3 text-sm font-bold text-brand transition hover:bg-brand-100 disabled:opacity-50"
                  >
                    {zaloSending ? (
                      <><span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-brand border-t-transparent" /> Đang gửi Zalo...</>
                    ) : zaloResult?.status === "success" ? (
                      <>✅ Đã gửi Zalo</>
                    ) : (
                      <>💬 Gửi Zalo Bot</>
                    )}
                  </button>
                </div>
                {(zaloError || zaloResult) && (
                  <div className={`mt-3 rounded-btn p-3 text-xs ${zaloResult?.status === "success" ? "bg-status-readyBg text-status-ready" : "bg-status-dangerBg text-status-danger"}`}>
                    {zaloError && <div className="font-bold">❌ {zaloError}</div>}
                    {zaloResult?.status === "success" && (
                      <div>
                        <div className="font-bold">✅ Đã gửi thông báo qua Zalo Bot thành công</div>
                        <div className="mt-1 text-ink-700">
                          Chat ID: {zaloResult.zalo.chat_id}
                          {zaloResult.zalo.steps?.text_message_id && ` · MsgID: ${zaloResult.zalo.steps.text_message_id}`}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}

            {result && !fileResult && (
              <>
                <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div className="rounded-btn bg-white p-4">
                    <div className="text-xs font-semibold uppercase tracking-wide text-ink-500">Document ID</div>
                    <div className="mt-1 font-mono text-sm text-ink-900">{result.document_id}</div>
                  </div>
                  <div className="rounded-btn bg-white p-4">
                    <div className="text-xs font-semibold uppercase tracking-wide text-ink-500">SHA256 Hash</div>
                    <div className="mt-1 break-all font-mono text-xs text-ink-900">{result.signed_hash}</div>
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
                  <button
                    onClick={downloadGeneratedPdf}
                    className="flex w-full items-center justify-center gap-2 rounded-btn border border-status-ready bg-white px-4 py-3 text-sm font-bold text-status-ready transition hover:bg-status-readyBg"
                  >
                    ⬇ Tải xuống PDF đã ký
                  </button>
                  <button
                    onClick={handleSendZalo}
                    disabled={zaloSending}
                    className="flex w-full items-center justify-center gap-2 rounded-btn border border-brand bg-brand-50 px-4 py-3 text-sm font-bold text-brand transition hover:bg-brand-100 disabled:opacity-50"
                  >
                    {zaloSending ? (
                      <><span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-brand border-t-transparent" /> Đang gửi Zalo...</>
                    ) : zaloResult?.status === "success" ? (
                      <>✅ Đã gửi Zalo</>
                    ) : (
                      <>💬 Gửi Zalo Bot</>
                    )}
                  </button>
                </div>
                {(zaloError || zaloResult) && (
                  <div className={`mt-3 rounded-btn p-3 text-xs ${zaloResult?.status === "success" ? "bg-status-readyBg text-status-ready" : "bg-status-dangerBg text-status-danger"}`}>
                    {zaloError && <div className="font-bold">❌ {zaloError}</div>}
                    {zaloResult?.status === "success" && (
                      <div>
                        <div className="font-bold">✅ Đã gửi thông báo qua Zalo Bot thành công</div>
                        <div className="mt-1 text-ink-700">
                          Chat ID: {zaloResult.zalo.chat_id}
                          {zaloResult.zalo.steps?.text_message_id && ` · MsgID: ${zaloResult.zalo.steps.text_message_id}`}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
