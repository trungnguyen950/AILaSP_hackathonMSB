"""MSB SmartForm AI Agent — LangGraph FSM 8 bước.

Core flow is deterministic (KB + RAG + Form Engine + QC).
LLM (optional) enhances: intent classification, field extraction, question phrasing.
Works without LLM (rule-based fallback) for local testing.
"""
from __future__ import annotations

import os
import re
from typing import Annotated, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from . import form_engine, qc, rag
from .demo_data import DEMO_CUSTOMERS, match_demo_customer
from .kb import KB
from .models import AgentState, Customer, FormTemplate
from .rag import INTENT_MAP, classify_keywords

# --- Optional LLM ---
_LLM = None
try:
    from langchain_openai import ChatOpenAI

    _model = os.environ.get("LLM_MODEL", "")
    _base = os.environ.get("LLM_BASE_URL", "")
    _key = os.environ.get("LLM_API_KEY", "")
    if _model and _base and _key:
        _LLM = ChatOpenAI(model=_model, base_url=_base, api_key=_key)
except Exception:
    _LLM = None


def llm_classify(text: str) -> list[str]:
    """Use LLM to classify intents; fall back to rule-based."""
    if not _LLM:
        return classify_keywords(text)
    intent_list = ", ".join(INTENT_MAP.keys())
    prompt = (
        f"Phân loại yêu cầu ngân hàng sau thành 1 hoặc nhiều nhãn từ danh sách:\n"
        f"{intent_list}\n\nYêu cầu: \"{text}\"\n\n"
        f"Trả về JSON: {{\"intents\": [\"...\"]}}. Chỉ trả JSON."
    )
    try:
        resp = _LLM.invoke(prompt)
        m = re.search(r"\{.*\}", resp.content, re.S)
        if m:
            import json

            data = json.loads(m.group(0))
            return data.get("intents", []) or classify_keywords(text)
    except Exception:
        pass
    return classify_keywords(text)


# --- Graph state (TypedDict for LangGraph) ---
class GraphState(TypedDict, total=False):
    message: str
    customer: Optional[Customer]
    intents: list[str]
    selected_code: Optional[str]
    not_found: bool
    collected: dict[str, str]
    missing: list[str]
    prev_missing: list[str]
    filled: dict[str, str]
    signatories: list[dict]
    checklist: list[dict]
    qc: Optional[dict]
    question: Optional[str]
    output: Optional[dict]
    violations: list[str]
    conversation_phase: str
    explanation: Optional[str]
    example: Optional[str]


def _template(code: Optional[str]) -> Optional[FormTemplate]:
    return KB.get(code) if code else None


# --- 8 nodes ---
def b1_identify(state: GraphState) -> dict:
    msg = state.get("message", "")
    customer = match_demo_customer(msg)
    if not customer:
        customer = state.get("customer") or DEMO_CUSTOMERS[0]
    return {"customer": customer}


def b2_classify(state: GraphState) -> dict:
    new_intents = llm_classify(state.get("message", ""))
    existing = state.get("intents", [])
    if new_intents == ["ACCOUNT"] and existing:
        return {"intents": existing}
    return {"intents": new_intents}


def b3_find_form(state: GraphState) -> dict:
    existing_code = state.get("selected_code")
    msg_lower = state.get("message", "").lower()
    other_code_mentioned = any(
        m.code.lower() in msg_lower for m in KB.list_active() if m.code != existing_code
    )
    if existing_code and KB.get(existing_code) and not other_code_mentioned:
        return {"not_found": False, "selected_code": existing_code}
    forms = rag.retrieve(KB, state.get("intents", []), state.get("customer"), state.get("message", ""))
    if not forms:
        return {"not_found": True, "selected_code": None}
    return {"not_found": False, "selected_code": forms[0].code}


# --- Guided flow: explain form fields ---
def _detect_language(state: GraphState) -> str:
    """Detect preferred language: 'vi' or 'en'."""
    msg = state.get("message", "").lower()
    customer = state.get("customer")
    english_markers = ["our company", "please", "bilingual", "forms", "i would like",
                       "accountant", "approver", "prepare", "foreign", "passport", "english"]
    en_count = sum(1 for m in english_markers if m in msg)
    if en_count >= 2:
        return "en"
    if customer and customer.is_fdi and customer.legal_rep_nationality and customer.legal_rep_nationality != "Vietnam":
        if en_count >= 1:
            return "en"
    return "vi"


def b3a_explain_form(state: GraphState) -> dict:
    """Explain the selected form: name, purpose, each field with guidance."""
    tpl = _template(state.get("selected_code"))
    if not tpl:
        return {"conversation_phase": "collecting"}
    meta = tpl.meta
    customer = state.get("customer")
    lang = _detect_language(state)

    lines = []
    if lang == "en":
        lines.append("Thank you for contacting MSB SmartForm AI.\n")
        bilingual_note = " (Bilingual VI-EN)" if meta.bilingual else ""
        lines.append(f"📋 **Recommended form:** {meta.code} — {meta.name}{bilingual_note}")
        lines.append(f"   Purpose: {meta.use_case}\n")
        if customer:
            ctype = "FDI Enterprise" if customer.is_fdi else ("Corporate" if customer.type == "org" else "Individual")
            lines.append(f"👤 Customer type: {ctype}")
        lines.append("")
        lines.append("📝 **Fields to complete:**")
        for i, f in enumerate(tpl.fields, 1):
            if form_engine.is_secret(f.key):
                continue
            label = f.label_en or f.label
            req = " *" if f.required else " (optional)"
            guidance = _field_guidance(f, "en")
            if guidance:
                lines.append(f"  {i}. {label}{req} — {guidance}")
            else:
                lines.append(f"  {i}. {label}{req}")
        lines.append(f"\n📄 Required documents: {', '.join(meta.accompanying_docs)}")
        lines.append(f"✍️ Signatory: {meta.signer}")
    else:
        lines.append("Cảm ơn Quý khách đã liên hệ MSB SmartForm AI.\n")
        bilingual_note = " (song ngữ VI-EN)" if meta.bilingual else ""
        lines.append(f"📋 **Mẫu biểu mẫu phù hợp:** {meta.code} — {meta.name}{bilingual_note}")
        lines.append(f"   Mục đích: {meta.use_case}\n")
        if customer:
            ctype = "Doanh nghiệp FDI" if customer.is_fdi else ("Doanh nghiệp" if customer.type == "org" else "Cá nhân")
            lines.append(f"👤 Loại khách hàng: {ctype}")
        lines.append("")
        lines.append("📝 **Các trường cần điền:**")
        for i, f in enumerate(tpl.fields, 1):
            if form_engine.is_secret(f.key):
                continue
            label = f.label
            if f.label_en and meta.bilingual:
                label = f"{f.label} / {f.label_en}"
            req = " *" if f.required else " (tự chọn)"
            guidance = _field_guidance(f, "vi")
            if guidance:
                lines.append(f"  {i}. {label}{req} — {guidance}")
            else:
                lines.append(f"  {i}. {label}{req}")
        lines.append(f"\n📄 Hồ sơ kèm theo: {', '.join(meta.accompanying_docs)}")
        lines.append(f"✍️ Người ký: {meta.signer}")

    explanation = "\n".join(lines)
    return {"conversation_phase": "explaining", "explanation": explanation}


def b3b_provide_example(state: GraphState) -> dict:
    """Generate a mock example with pre-filled data for the customer to see."""
    tpl = _template(state.get("selected_code"))
    if not tpl:
        return {"conversation_phase": "collecting"}
    customer = state.get("customer")
    meta = tpl.meta
    lang = _detect_language(state)

    # Build example values
    example_vals = {}
    if customer:
        if customer.name:
            example_vals["company_name"] = customer.name
            example_vals["customer_name"] = customer.name
        if customer.name_en:
            example_vals["company_name_en"] = customer.name_en
        if customer.tax_id:
            example_vals["tax_id"] = customer.tax_id
            example_vals["tax_id_or_cccd"] = customer.tax_id
        if customer.account_no:
            example_vals["account_no"] = customer.account_no
        if customer.legal_rep:
            example_vals["legal_rep"] = customer.legal_rep
        if customer.legal_rep_nationality:
            example_vals["legal_rep_nationality"] = customer.legal_rep_nationality
        if customer.legal_rep_passport:
            example_vals["legal_rep_passport"] = customer.legal_rep_passport
        if customer.cccd:
            example_vals["cccd"] = customer.cccd

    example_defaults = {
        "user_name": "Nguyễn Thị Lan",
        "cccd": "001098765432",
        "position": "Kế toán",
        "role": "Maker",
        "limit": "500000000",
        "new_limit": "1000000000",
        "auth_method": "OTP",
        "phone": "0901234567",
        "email": "lan@company.vn",
        "digital_sign_required": "Yes",
        "action_type": "thay đổi",
        "ds_provider": "Viettel-CA",
        "ds_serial": "VTCA-2024-001234",
        "ds_valid_to": "31/12/2026",
        "approval_flow": "2 người",
        "approver_names": "Nguyễn Văn X (Maker); David Chen (Approver)",
        "effective_date": "01/10/2026",
        "current_limit": "500000000",
    }
    for f in tpl.fields:
        if form_engine.is_secret(f.key):
            continue
        if f.key not in example_vals:
            if f.key in example_defaults:
                example_vals[f.key] = example_defaults[f.key]
            elif f.options:
                example_vals[f.key] = f.options[0]
            elif f.required:
                example_vals[f.key] = f"[ví dụ: {f.label}]"
            else:
                example_vals[f.key] = ""

    lines = []
    if lang == "en":
        lines.append("📋 **Mock example (DEMO):**\n")
        lines.append(f"Form: {meta.code} — {meta.name}")
        lines.append(f"Customer: {customer.name_en or customer.name if customer else 'Demo'}\n")
        lines.append("Filled information:")
        for f in tpl.fields:
            if form_engine.is_secret(f.key):
                continue
            val = example_vals.get(f.key, "")
            label = f.label_en or f.label
            lines.append(f"  {label}: {val}")
        lines.append("\n⚠️ This is a mock draft. Please fill in your real information and send it back.")
        lines.append("\n💡 You can enter values separated by | :")
        lines.append("  value1 | value2 | value3")
        lines.append("\nWhen ready, please provide your information or type 'ready' to begin.")
    else:
        lines.append("📋 **Mẫu giả lập (DEMO):**\n")
        lines.append(f"Mẫu: {meta.code} — {meta.name}")
        lines.append(f"Khách hàng: {customer.name if customer else 'Demo'}\n")
        lines.append("Thông tin điền:")
        for f in tpl.fields:
            if form_engine.is_secret(f.key):
                continue
            val = example_vals.get(f.key, "")
            label = f.label
            if f.label_en and meta.bilingual:
                label = f"{f.label} / {f.label_en}"
            lines.append(f"  {label}: {val}")
        lines.append("\n⚠️ Đây là bản nháp giả lập. Quý khách vui lòng điền thông tin thật rồi gửi lại cho tôi.")
        lines.append("\n💡 Quý khách có thể nhập theo dạng:")
        lines.append("  giátrị1 | giátrị2 | giátrị3  (phân tách bằng dấu |)")
        lines.append("\nKhi sẵn sàng, vui lòng cung cấp thông tin hoặc nhập \"sẵn sàng\" để bắt đầu.")

    example = "\n".join(lines)
    return {"conversation_phase": "example_shown", "example": example, "question": "\n\n".join([state.get("explanation", ""), example])}


def _field_guidance(f, lang: str = "vi") -> str:
    """Generate human-friendly 1-line guidance for a form field."""
    v = (f.validation or "").lower()
    if lang == "en":
        if "mst_10" in v:
            return "10 digits, e.g. 0101234567 — see Business Registration Certificate"
        if "cccd_12" in v:
            return "12 digits, e.g. 001098765432 — from ID card or passport"
        if "phone_vn" in v:
            return "Vietnamese phone, e.g. 0901234567"
        if "email" in v:
            return "Valid email, e.g. name@company.com"
        if "msb_account" in v:
            return "9–12 digits, e.g. 123456789999"
        if f.type == "enum" and f.options:
            return f"Choose: {', '.join(f.options)}"
        if f.type == "date":
            return "Format DD/MM/YYYY, e.g. 01/10/2026"
        if f.type == "number":
            return f"Number{' (' + f.note + ')' if f.note else ''}, e.g. 500000000"
        if f.type == "bool":
            return "Yes or No"
        if "company_name_en" in f.key:
            return "English company name from ERC/IRC"
        if "nationality" in f.key:
            return "Legal representative's nationality, e.g. Singapore"
        if "passport" in f.key:
            return "Passport number (for foreign nationals), e.g. S1234567A"
        if "role" in f.key:
            return "Maker (prepare) / Checker (review) / Approver (approve)"
        if "legal_rep" in f.key:
            return "From Business Registration Certificate"
        return ""
    # Vietnamese (có dấu)
    if "mst_10" in v:
        return "10 chữ số, ví dụ: 0101234567 — xem Giấy chứng nhận ĐKDN"
    if "cccd_12" in v:
        return "12 chữ số, ví dụ: 001098765432 — từ thẻ CCCD hoặc hộ chiếu"
    if "phone_vn" in v:
        return "Số điện thoại VN, ví dụ: 0901234567"
    if "email" in v:
        return "Email hợp lệ, ví dụ: name@company.com"
    if "msb_account" in v:
        return "9–12 chữ số, ví dụ: 123456789999"
    if f.type == "enum" and f.options:
        return f"Chọn: {', '.join(f.options)}"
    if f.type == "date":
        return "Định dạng DD/MM/YYYY, ví dụ: 01/10/2026"
    if f.type == "number":
        return f"Số{' (' + f.note + ')' if f.note else ''}, ví dụ: 500000000"
    if f.type == "bool":
        return "Yes hoặc No"
    if "company_name_en" in f.key:
        return "Tên doanh nghiệp bằng tiếng Anh, lấy từ ERC/IRC"
    if "nationality" in f.key:
        return "Quốc tịch người đại diện, ví dụ: Singapore"
    if "passport" in f.key:
        return "Số hộ chiếu (nếu người nước ngoài), ví dụ: S1234567A"
    if "role" in f.key:
        return "Maker (lập lệnh) / Checker (kiểm soát) / Approver (duyệt)"
    if "legal_rep" in f.key:
        return "Lấy từ Giấy phép ĐKKD"
    return ""


def b4_missing(state: GraphState) -> dict:
    tpl = _template(state.get("selected_code"))
    if not tpl:
        return {"missing": []}
    collected = state.get("collected", {})
    customer = state.get("customer")
    if customer:
        collected = _prefill_customer(customer, collected)
    prev_missing = state.get("prev_missing", [])
    collected = {**collected, **_extract_fields(tpl, state.get("message", ""), collected, prev_missing)}
    filled, missing = form_engine.fill(tpl, collected)
    question = None
    if missing:
        labels = [f.label for f in tpl.fields if f.key in missing]
        question = "Để hoàn thiện hồ sơ, vui lòng cung cấp:\n" + "\n".join(f"{i+1}. {l}" for i, l in enumerate(labels))
    return {"collected": collected, "missing": missing, "filled": filled, "question": question}


def b5_fill(state: GraphState) -> dict:
    tpl = _template(state.get("selected_code"))
    if not tpl:
        return {}
    filled, missing = form_engine.fill(tpl, state.get("collected", {}))
    return {"filled": filled, "missing": missing}


def b6_logic(state: GraphState) -> dict:
    tpl = _template(state.get("selected_code"))
    if not tpl:
        return {}
    violations = form_engine.validate(tpl, state.get("filled", {}))
    return {"violations": violations}


def b7_signatory(state: GraphState) -> dict:
    tpl = _template(state.get("selected_code"))
    if not tpl:
        return {}
    return {"signatories": [s.model_dump() for s in tpl.signatories]}


def b8_checklist(state: GraphState) -> dict:
    tpl = _template(state.get("selected_code"))
    if not tpl:
        return {}
    filled = state.get("filled", {})
    missing = state.get("missing", [])
    result = qc.run_checks(tpl, filled, missing, state.get("customer"))
    checklist = form_engine.build_checklist(tpl)
    output = _build_output(state, tpl, filled, result, checklist)
    return {"qc": result.model_dump(), "checklist": checklist, "output": output}


# --- helpers ---
def _extract_fields(tpl: FormTemplate, text: str, collected: dict[str, str] | None = None, question_fields: list[str] | None = None) -> dict[str, str]:
    """Heuristically extract field values from free-text.

    Supports: Label: value lines, pipe-separated, comma-separated, numbered list, and keyword-based.
    question_fields: ordered list of field keys that were asked in the previous question.
    """
    out: dict[str, str] = {}
    t = text.strip()
    prev = collected or {}

    # --- "Label: value" format (highest priority) ---
    label_matches = _parse_label_value_lines(t, tpl)
    for key, val in label_matches.items():
        if val and not form_engine.is_secret(key) and key not in {**prev, **out}:
            out[key] = val
    if label_matches:
        return out

    parts: list[str] | None = None
    if "|" in t:
        parts = [p.strip() for p in t.split("|") if p.strip()]
    elif re.search(r"^\s*1[\.\)]\s", t):
        parts = re.findall(r"\d+[\.\)]\s*(.+?)(?=\s*\d+[\.\)]|\Z)", t, re.S)
        parts = [p.strip().rstrip(",").strip() for p in parts if p.strip()]
    elif t.count(",") >= 2:
        parts = [p.strip() for p in t.split(",") if p.strip()]

    if parts:
        if question_fields:
            target_fields = [f for f in tpl.fields if f.key in question_fields]
        else:
            target_fields = [f for f in tpl.fields if f.required and not is_filled(tpl, f.key, {**prev, **out})]
        for f, val in zip(target_fields, parts):
            if val and not form_engine.is_secret(f.key):
                out[f.key] = val

    m = re.search(r"\b\d{12}\b", t)
    if m and "cccd" not in {**prev, **out}:
        _assign(tpl, out, "cccd", m.group(0))
    m = re.search(r"\b\d{10}\b", t)
    if m and "tax_id" not in {**prev, **out} and "cccd" not in out:
        _assign(tpl, out, "tax_id", m.group(0))
    m = re.search(r"\b0\d{9,10}\b", t)
    if m and "phone" not in {**prev, **out}:
        _assign(tpl, out, "phone", m.group(0))
        _assign(tpl, out, "change_phone", m.group(0))
    m = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", t)
    if m and "email" not in {**prev, **out}:
        _assign(tpl, out, "email", m.group(0))
        _assign(tpl, out, "change_email", m.group(0))
    m = re.search(r"(\d[\d,]*)\s*(tỷ|trieu|M|k|K)?", t, re.I)
    if m and "limit" not in {**prev, **out}:
        _assign(tpl, out, "limit", m.group(0).strip())
        _assign(tpl, out, "new_limit", m.group(0).strip())
    for role in ("Maker", "Checker", "Approver"):
        if role.lower() in t.lower() and "role" not in {**prev, **out}:
            _assign(tpl, out, "role", role)
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", t)
    if m and "ds_valid_to" not in {**prev, **out}:
        _assign(tpl, out, "ds_valid_to", m.group(0))
    return out


def is_filled(tpl: FormTemplate, key: str, out: dict) -> bool:
    return key in out


def _assign(tpl: FormTemplate, out: dict, key: str, val: str) -> None:
    if key not in out and any(f.key == key for f in tpl.fields) and not form_engine.is_secret(key):
        out[key] = val


def _normalize_label(s: str) -> str:
    """Normalize label for fuzzy matching: lowercase, remove diacritics, remove extra spaces."""
    import unicodedata
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    s = s.replace("(", " ").replace(")", " ").replace("/", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _parse_label_value_lines(text: str, tpl: FormTemplate) -> dict[str, str]:
    """Parse 'Label: value' lines and match to form fields by label.

    Handles:
      - Exact match: "Họ tên (mới)" → field with label "Họ tên (mới)"
      - Partial match: "CCCD" → field with label "CCCD (mới)" or "CCCD/Hộ chiếu"
      - Diacritics-insensitive: "Ho ten (moi)" matches "Họ tên (mới)"
    """
    result: dict[str, str] = {}
    lines = text.strip().splitlines()
    if len(lines) < 2:
        return result

    # Build field label index: (key, normalized_label)
    field_labels: list[tuple[str, str]] = []
    for f in tpl.fields:
        if form_engine.is_secret(f.key):
            continue
        field_labels.append((f.key, _normalize_label(f.label)))
        if f.label_en:
            field_labels.append((f.key, _normalize_label(f.label_en)))

    for line in lines:
        line = line.strip()
        if not line or ":" not in line:
            continue
        parts = line.split(":", 1)
        if len(parts) != 2:
            continue
        raw_label, value = parts[0].strip(), parts[1].strip()
        if not value:
            continue
        norm_label = _normalize_label(raw_label)

        best_key = None
        best_score = 0
        for key, norm_fl in field_labels:
            if norm_label == norm_fl:
                best_key = key
                best_score = 100
                break
            if norm_label in norm_fl or norm_fl in norm_label:
                score = min(len(norm_label), len(norm_fl)) / max(len(norm_label), len(norm_fl), 1) * 80
                if score > best_score:
                    best_score = score
                    best_key = key
            words_label = set(norm_label.split())
            words_field = set(norm_fl.split())
            overlap = words_label & words_field
            if overlap:
                score = len(overlap) / max(len(words_label), len(words_field), 1) * 70
                if score > best_score:
                    best_score = score
                    best_key = key

        if best_key and best_score >= 50:
            result[best_key] = value

    return result


def _build_output(state: GraphState, tpl: FormTemplate, filled: dict, result, checklist: list) -> dict:
    meta = tpl.meta
    customer = state.get("customer")
    output = {
        "A_nhu_cau": state.get("message", ""),
        "B_loai_kh": f"{customer.type} — {customer.name}" if customer else "",
        "C_nghiep_vu": ", ".join(state.get("intents", [])),
        "D_mau_bieu": f"{meta.code} (v{meta.version}, hiệu lực {meta.effective_date})",
        "E_da_co": {k: v for k, v in filled.items() if v and v != form_engine.MISSING},
        "F_con_thieu": state.get("missing", []),
        "G_bieu_mau_dien": filled,
        "H_nguoi_ky": state.get("signatories", []),
        "I_ho_so_kem": meta.accompanying_docs,
        "J_checklist": checklist,
        "K_canh_bao": state.get("violations", []),
        "status": result.status,
    }
    if customer and customer.is_fdi:
        output["B_loai_kh"] = f"FDI — {customer.name} / {customer.name_en or 'N/A'}"
        output["L_bilingual"] = {
            "is_fdi": True,
            "form_bilingual": meta.bilingual,
            "customer_name_en": customer.name_en,
            "legal_rep_nationality": customer.legal_rep_nationality,
            "legal_rep_passport": customer.legal_rep_passport,
            "note": "Bilingual VI-EN form selected. Passport and nationality required." if meta.bilingual else "Only Vietnamese form found. MSB confirmation needed for bilingual version.",
        }
    return output


def _prefill_customer(customer: Optional[Customer], collected: dict[str, str]) -> dict[str, str]:
    """Pre-fill form fields from identified demo customer data."""
    if not customer:
        return collected
    out = dict(collected)
    if customer.name:
        out.setdefault("company_name", customer.name)
        out.setdefault("customer_name", customer.name)
    if customer.name_en:
        out.setdefault("company_name_en", customer.name_en)
    if customer.tax_id:
        out.setdefault("tax_id", customer.tax_id)
        out.setdefault("tax_id_or_cccd", customer.tax_id)
    if customer.account_no:
        out.setdefault("account_no", customer.account_no)
    if customer.legal_rep:
        out.setdefault("legal_rep", customer.legal_rep)
    if customer.legal_rep_nationality:
        out.setdefault("legal_rep_nationality", customer.legal_rep_nationality)
    if customer.legal_rep_passport:
        out.setdefault("legal_rep_passport", customer.legal_rep_passport)
    if customer.cccd:
        out.setdefault("cccd", customer.cccd)
        out.setdefault("tax_id_or_cccd", customer.cccd)
    return out


def _generate_form_file(tpl: FormTemplate, filled: dict[str, str], customer: Optional[Customer]) -> dict:
    """Generate a downloadable form file (plain-text bản mềm). Returns {filename, content, mime}."""
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{tpl.meta.code}_{ts}.txt"
    lines = [
        f"{'=' * 60}",
        f"  MSB SmartForm AI — Bản mềm hồ sơ (giả lập)",
        f"{'=' * 60}",
        f"",
        f"Mã mẫu:          {tpl.meta.code}",
        f"Tên mẫu:         {tpl.meta.name}",
        f"Phiên bản:       {tpl.meta.version}",
        f"Ngày hiệu lực:   {tpl.meta.effective_date}",
        f"Nhóm nghiệp vụ:  {tpl.meta.business_group}",
        f"Đối tượng:       {tpl.meta.segment}",
        f"",
        f"{'─' * 60}",
        f"  THÔNG TIN ĐÃ ĐIỀN",
        f"{'─' * 60}",
        f"",
    ]
    for f in tpl.fields:
        if form_engine.is_secret(f.key):
            continue
        val = filled.get(f.key, "")
        required = "*" if f.required else " "
        lines.append(f"  {required} {f.label:<40s} : {val}")
    lines.extend([
        f"",
        f"{'─' * 60}",
        f"  NGƯỜY KÝ",
        f"{'─' * 60}",
        f"",
    ])
    for s in tpl.signatories:
        lines.append(f"  - {s.who} ({s.position}) — vị trí: {s.position_to_sign}")
    lines.extend([
        f"",
        f"{'─' * 60}",
        f"  HỒ SƠ KÈM THEO",
        f"{'─' * 60}",
        f"",
    ])
    for doc in tpl.meta.accompanying_docs:
        lines.append(f"  - {doc}")
    lines.extend([
        f"",
        f"{'=' * 60}",
        f"  File tạo lúc: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        f"  Lưu ý: Dữ liệu giả lập, không dùng cho giao dịch thật.",
        f"{'=' * 60}",
    ])
    return {"filename": filename, "content": "\n".join(lines), "mime": "text/plain"}


# --- Build graph ---
builder = StateGraph(GraphState)
builder.add_node("b1_identify", b1_identify)
builder.add_node("b2_classify", b2_classify)
builder.add_node("b3_find_form", b3_find_form)
builder.add_node("b3a_explain_form", b3a_explain_form)
builder.add_node("b3b_provide_example", b3b_provide_example)
builder.add_node("b4_missing", b4_missing)
builder.add_node("b5_fill", b5_fill)
builder.add_node("b6_logic", b6_logic)
builder.add_node("b7_signatory", b7_signatory)
builder.add_node("b8_checklist", b8_checklist)

builder.add_edge(START, "b1_identify")
builder.add_edge("b1_identify", "b2_classify")
builder.add_edge("b2_classify", "b3_find_form")
builder.add_conditional_edges(
    "b3_find_form",
    lambda s: END if s.get("not_found") else ("b3a_explain_form" if s.get("conversation_phase") != "collecting" else "b4_missing"),
)
builder.add_edge("b3a_explain_form", "b3b_provide_example")
builder.add_edge("b3b_provide_example", END)
builder.add_conditional_edges(
    "b4_missing",
    lambda s: END if s.get("missing") else "b5_fill",
)
builder.add_edge("b5_fill", "b6_logic")
builder.add_edge("b6_logic", "b7_signatory")
builder.add_edge("b7_signatory", "b8_checklist")
builder.add_edge("b8_checklist", END)

graph = builder.compile()


# --- Session store (in-memory; prod → AgentBase memory / DB) ---
_SESSIONS: dict[str, AgentState] = {}


def run(session_id: str, message: str) -> dict:
    """Process a user message through the guided FSM. Returns response dict."""
    state = _SESSIONS.get(session_id, AgentState(session_id=session_id))
    state.messages.append({"role": "user", "content": message})
    state.soan_ho_so = message.strip().upper() == "SOẠN HỒ SƠ" or message.strip().upper() == "SOAN HO SO"

    existing_code = state.selected_forms[0].code if state.selected_forms else None

    # Determine conversation phase routing
    msg_lower = message.strip().lower()
    is_ready = msg_lower in ("san sang", "sẵn sàng", "ready", "ok", "yes", "co", "có", "bat dau", "bắt đầu")
    is_providing_data = "|" in message or _looks_like_data(message)
    current_phase = state.conversation_phase

    # If customer is in example_shown phase and says ready or provides data → go to collecting
    if current_phase == "example_shown" and (is_ready or is_providing_data):
        conversation_phase = "collecting"
    elif current_phase == "example_shown":
        # Customer is asking a question, not providing data — re-explain with demo values
        tpl = KB.get(existing_code) if existing_code else None
        demo_hint = ""
        if tpl:
            demo_vals = []
            customer = state.customer
            for f in tpl.fields:
                if form_engine.is_secret(f.key) or not f.required:
                    continue
                val = state.collected.get(f.key, "")
                if not val and customer:
                    val = _prefill_customer(customer, {}).get(f.key, "")
                if not val:
                    defaults = {
                        "user_name": "Nguyễn Thị Lan", "cccd": "001098765432", "position": "Kế toán",
                        "role": "Maker", "auth_method": "OTP", "phone": "0901234567",
                        "email": "lan@company.vn", "limit": "500000000",
                    }
                    val = defaults.get(f.key, "")
                if val:
                    demo_vals.append(val)
            if demo_vals:
                demo_hint = "\n\n💡 Ví dụ điền nhanh:\n  " + " | ".join(demo_vals[:7])
        return {
            "status": "EXPLAINING",
            "question": f"Tôi hiểu Quý khách còn thắc mắc. Quý khách có thể xem lại hướng dẫn bên trên.{demo_hint}\n\nKhi sẵn sàng, vui lòng cung cấp thông tin theo dạng:\n  giátrị1 | giátrị2 | giátrị3  (phân tách bằng dấu |)\n\nHoặc nhập \"sẵn sàng\" để bắt đầu thu thập thông tin.",
            "selected_form": (KB.get(existing_code).meta.model_dump() if existing_code and KB.get(existing_code) else None),
            "session_id": session_id,
        }
    else:
        conversation_phase = current_phase if current_phase == "collecting" else "init"

    init: GraphState = {
        "message": message,
        "customer": state.customer,
        "collected": dict(state.collected),
        "selected_code": existing_code,
        "intents": list(state.intents),
        "prev_missing": list(state.missing),
        "conversation_phase": conversation_phase,
    }
    result = graph.invoke(init)

    # persist
    state.customer = result.get("customer", state.customer)
    state.intents = result.get("intents", [])
    state.collected = result.get("collected", state.collected)
    state.missing = result.get("missing", [])
    state.filled = result.get("filled", {})
    state.qc = None
    code = result.get("selected_code")
    if code:
        from .models import FormMeta

        state.selected_forms = [KB.get(code).meta] if KB.get(code) else []
    state.signatories = [type("S", (), d)() for d in result.get("signatories", [])]  # store raw
    state.checklist = result.get("checklist", [])
    state.last_question = result.get("question")
    state.output = result.get("output")
    state.not_found = result.get("not_found", False)
    state.conversation_phase = result.get("conversation_phase", conversation_phase)
    _SESSIONS[session_id] = state

    # response
    if state.not_found:
        return {
            "status": "NEED MSB REVIEW",
            "message": "Chưa xác định được mẫu biểu MSB tương ứng trong thư viện hiện có. Cần chuyên viên MSB xác nhận trước khi lập hồ sơ.",
            "session_id": session_id,
        }

    # Guided flow: explanation + example
    if state.conversation_phase == "example_shown" and result.get("question"):
        return {
            "status": "FORM EXPLAINED",
            "question": result["question"],
            "selected_form": (KB.get(code).meta.model_dump() if code and KB.get(code) else None),
            "explanation": result.get("explanation"),
            "example": result.get("example"),
            "session_id": session_id,
        }

    if state.last_question:
        return {
            "status": "MISSING INFORMATION",
            "question": state.last_question,
            "selected_form": (KB.get(code).meta.model_dump() if code and KB.get(code) else None),
            "session_id": session_id,
        }
    file_info = None
    tpl = KB.get(code) if code else None
    if tpl and state.filled and not state.missing:
        file_info = _generate_form_file(tpl, state.filled, state.customer)
    return {
        "status": (state.output or {}).get("status", "READY"),
        "output": state.output,
        "selected_form": (KB.get(code).meta.model_dump() if code and KB.get(code) else None),
        "filled": state.filled,
        "checklist": state.checklist,
        "file": file_info,
        "session_id": session_id,
    }


def _looks_like_data(text: str) -> bool:
    """Heuristic: does this message look like the user is providing form data?"""
    import re
    # Contains pipe-separated values
    if "|" in text:
        return True
    # Contains a 10-digit number (MST) or 12-digit (CCCD)
    if re.search(r"\b\d{10}\b", text) or re.search(r"\b\d{12}\b", text):
        return True
    # Contains email
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text):
        return True
    # Contains phone number
    if re.search(r"\b0\d{9,10}\b", text):
        return True
    return False


def get_state(session_id: str) -> AgentState | None:
    return _SESSIONS.get(session_id)


def reset_session(session_id: str) -> None:
    _SESSIONS.pop(session_id, None)
