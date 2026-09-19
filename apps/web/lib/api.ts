const AGENT_URL = process.env.NEXT_PUBLIC_AGENT_URL || "";

export type FormMeta = {
  code: string;
  name: string;
  name_en: string | null;
  business_group: string;
  segment: string;
  org_type: string;
  use_case: string;
  preparer: string;
  signer: string;
  accompanying_docs: string[];
  version: string;
  effective_date: string;
  source_file: string;
  active: boolean;
  bilingual: boolean;
};

export type FormField = {
  key: string;
  label: string;
  type: string;
  required: boolean;
  validation: string | null;
  options: string[];
  note: string | null;
};

export type Signatory = {
  who: string;
  position: string;
  position_to_sign: string;
  stamp: string;
};

export type FormTemplate = {
  meta: FormMeta;
  fields: FormField[];
  signatories: Signatory[];
  fixed_content: string[];
  reject_list: string[];
  branches: string[];
};

export type AgentResponse = {
  status: string;
  message?: string;
  question?: string;
  selected_form?: any;
  filled?: Record<string, string>;
  checklist?: any[];
  output?: Record<string, any>;
  preview_html?: string;
  forms?: FormMeta[];
  form?: FormTemplate;
  session_id?: string;
  error?: string;
  file?: { filename: string; content: string; mime: string } | null;
};

export async function invoke(action: string, payload: Record<string, any> = {}): Promise<AgentResponse> {
  const res = await fetch(`${AGENT_URL}/invocations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-GreenNode-AgentBase-Session-Id": payload.session_id || "web-session",
      "X-GreenNode-AgentBase-User-Id": "web-user",
    },
    body: JSON.stringify({ action, ...payload }),
  });
  if (!res.ok) throw new Error(`Agent error ${res.status}`);
  return res.json();
}

export async function listForms(): Promise<FormMeta[]> {
  const res = await invoke("list_forms");
  return res.forms || [];
}

export async function getForm(code: string): Promise<FormTemplate> {
  const res = await invoke("get_form", { code });
  if (res.status === "error") throw new Error(res.message || "Form not found");
  return res.form!;
}

export type MockCert = {
  certId: string;
  subject: string;
  issuer: string;
  validFrom: string;
  validTo: string;
};

export type SignResult = {
  status: string;
  document_id: string;
  signed_hash: string;
  signed_pdf_base64: string;
  webhook: {
    event: string;
    documentId: string;
    formCode: string;
    signedHash: string;
    signedBy: string;
    certId: string;
    timestamp: string;
  };
  agent_ack: {
    acknowledged: boolean;
    message: string;
    nextStep: string;
    timestamp: string;
  };
  timestamp: string;
};

export async function mockSignDocument(
  documentId: string,
  signatureImage: string,
  mockCert: MockCert,
  code?: string
): Promise<SignResult> {
  const res = await invoke("mock_sign_document", {
    document_id: documentId,
    signature_image: signatureImage,
    mock_cert: mockCert,
    code,
  });
  if (res.status === "error") throw new Error(res.message || "Sign failed");
  return res as unknown as SignResult;
}

export type UploadCheckResult = {
  status: string;
  filename: string;
  file_type: string;
  file_size: number;
  authentic: boolean;
  score: number;
  checks: Array<{ check: string; pass: boolean; detail?: string }>;
  llm_verdict: { is_authentic: boolean; reason: string } | null;
  text_preview: string;
  timestamp: string;
  message?: string;
};

export type SignFileResult = {
  status: string;
  signed_filename: string;
  signed_hash: string;
  signed_file_base64: string;
  file_type: string;
  vintage_pdf_base64: string | null;
  vintage_pdf_filename: string | null;
  webhook: Record<string, any>;
  agent_ack: { acknowledged: boolean; message: string; nextStep: string; timestamp: string };
  timestamp: string;
  message?: string;
};

export type VintagePdfResult = {
  status: string;
  filename: string;
  pdf_base64: string;
  pdf_size: number;
  timestamp: string;
  message?: string;
};

export async function uploadAndCheck(
  filename: string,
  fileContent: string,
  code?: string
): Promise<UploadCheckResult> {
  const res = await invoke("upload_and_check", { filename, file_content: fileContent, code });
  if (res.status === "error") throw new Error(res.message || "Upload check failed");
  return res as unknown as UploadCheckResult;
}

export async function signUploadedFile(
  filename: string,
  fileContent: string,
  signatureImage: string,
  mockCert: MockCert,
  code?: string
): Promise<SignFileResult> {
  const res = await invoke("sign_uploaded_file", {
    filename,
    file_content: fileContent,
    signature_image: signatureImage,
    mock_cert: mockCert,
    code,
  });
  if (res.status === "error") throw new Error(res.message || "Sign file failed");
  return res as unknown as SignFileResult;
}

export async function exportVintagePdf(code: string): Promise<VintagePdfResult> {
  const res = await invoke("export_vintage_pdf", { code });
  if (res.status === "error") throw new Error(res.message || "Export PDF failed");
  return res as unknown as VintagePdfResult;
}

export async function exportFormPdf(code: string): Promise<VintagePdfResult> {
  const res = await invoke("export_form_pdf", { code });
  if (res.status === "error") throw new Error(res.message || "Export form PDF failed");
  return res as unknown as VintagePdfResult;
}
