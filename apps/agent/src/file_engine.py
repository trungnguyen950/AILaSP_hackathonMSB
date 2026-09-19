"""File Engine — upload validation, AI authenticity check, and file signing.

Supports:
- .txt files: append signature block at end (text) OR convert to vintage PDF
- .pdf files: merge original with a signature overlay page (via pypdf + fpdf2)

AI authenticity check uses LLM if available, falls back to rule-based validation.

Font: dùng Unicode TTF (Be Vietnam Pro, DejaVu) — hỗ trợ đầy đủ tiếng Việt.
"""
from __future__ import annotations

import base64
import hashlib
import io
import logging
import re
from datetime import datetime
from typing import Optional

from fpdf import FPDF

from .pdf_fonts import register_vintage_fonts, fix_vietnamese, safe_text, get_font
from .vintage_pdf import text_to_vintage_pdf, generate_vintage_pdf

logger = logging.getLogger("file_engine")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".txt", ".pdf"}
PDF_MAGIC = b"%PDF"


def _ascii(text: str) -> str:
    """DEPRECATED — chỉ dùng khi không có font Unicode.

    Ưu tiên fix_vietnamese() + font Unicode để giữ dấu tiếng Việt.
    """
    if not text:
        return ""
    text = text.replace("\u2014", "-").replace("\u2013", "-").replace("\u2026", "...")
    import unicodedata
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "replace").decode("ascii")


def validate_file(filename: str, content: bytes) -> tuple[bool, str, str]:
    """Validate uploaded file. Returns (is_valid, file_type, error_message)."""
    if not filename:
        return False, "", "Tên file trống."
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, "", f"Định dạng không hỗ trợ. Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}"
    if len(content) > MAX_FILE_SIZE:
        return False, "", f"File quá lớn ({len(content) // 1024}KB). Tối đa {MAX_FILE_SIZE // 1024 // 1024}MB."
    if ext == ".pdf" and not content[:5].startswith(PDF_MAGIC):
        return False, "", "File PDF không hợp lệ (sai magic bytes)."
    return True, ext, ""


def check_authenticity(
    filename: str,
    content: bytes,
    form_code: str,
    form_name: str,
    llm=None,
) -> dict:
    """Check file authenticity. Returns {is_authentic, score, details, extracted_text}.

    Uses LLM if available, falls back to rule-based validation.
    """
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    text_content = ""

    if ext == ".txt":
        try:
            text_content = content.decode("utf-8", errors="replace")[:4000]
        except Exception:
            text_content = ""
    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            for page in reader.pages[:3]:
                text_content += page.extract_text() or ""
            text_content = text_content[:4000]
        except Exception:
            text_content = ""

    # --- Rule-based checks ---
    checks = []
    score = 0

    # Check 1: Form code present
    if form_code and form_code in text_content:
        checks.append({"check": "form_code_found", "pass": True})
        score += 30
    else:
        checks.append({"check": "form_code_found", "pass": False, "detail": f"Không tìm thấy mã mẫu {form_code} trong file"})
        score += 5

    # Check 2: Form name or keywords present
    if form_name:
        name_words = [w.lower() for w in form_name.split() if len(w) > 3]
        found_words = [w for w in name_words if w in text_content.lower()]
        if found_words:
            checks.append({"check": "form_name_keywords", "pass": True, "detail": f"Found: {found_words}"})
            score += 20
        else:
            checks.append({"check": "form_name_keywords", "pass": False})
            score += 5

    # Check 3: Content not empty
    if len(text_content.strip()) > 50:
        checks.append({"check": "content_not_empty", "pass": True})
        score += 20
    else:
        checks.append({"check": "content_not_empty", "pass": False, "detail": "Nội dung quá ngắn hoặc trống"})
        score += 0

    # Check 4: Looks like a form (has field-like structure)
    field_indicators = ["@", "số", "tên", "mã", "email", "phone", "cccd", "mst", "account"]
    found_indicators = [ind for ind in field_indicators if ind in text_content.lower()]
    if len(found_indicators) >= 2:
        checks.append({"check": "form_structure", "pass": True, "detail": f"Indicators: {found_indicators}"})
        score += 15
    else:
        checks.append({"check": "form_structure", "pass": False})
        score += 5

    # Check 5: File format valid
    checks.append({"check": "file_format_valid", "pass": True})
    score += 15

    # --- LLM enhancement (optional) ---
    llm_verdict = None
    if llm and text_content:
        try:
            prompt = (
                f"Kiểm tra file biểu mẫu ngân hàng. Mẫu mong đợi: {form_code} — {form_name}.\n"
                f"Nội dung file (tóm tắt):\n{text_content[:1500]}\n\n"
                f"Trả về JSON: {{\"is_authentic\": true/false, \"reason\": \"...\"}}. Chỉ trả JSON."
            )
            resp = llm.invoke(prompt)
            m = re.search(r"\{.*\}", resp.content, re.S)
            if m:
                import json
                data = json.loads(m.group(0))
                llm_verdict = data
                if data.get("is_authentic"):
                    score = max(score, 75)
                else:
                    score = min(score, 40)
        except Exception as e:
            logger.warning("LLM check failed: %s", e)

    is_authentic = score >= 50
    return {
        "is_authentic": is_authentic,
        "score": score,
        "checks": checks,
        "llm_verdict": llm_verdict,
        "extracted_text_preview": text_content[:500],
    }


def sign_file(
    filename: str,
    content: bytes,
    signature_image_b64: str,
    mock_cert: dict,
    form_code: str = "",
) -> tuple[bytes, str, dict]:
    """Sign an uploaded file. Returns (signed_bytes, sha256_hash, webhook_payload).

    - .txt: append signature block at end (text) — giữ nguyên UTF-8 tiếng Việt
    - .pdf: merge original with a signature overlay page (Unicode font)
    """
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cert_id = mock_cert.get("certId", "UNKNOWN")
    subject = mock_cert.get("subject", "UNKNOWN")

    if ext == ".txt":
        sig_block = (
            f"\n\n{'=' * 60}\n"
            f"  DIGITAL SIGNATURE (MOCK)\n"
            f"{'=' * 60}\n"
            f"  Timestamp:     {ts}\n"
            f"  Certificate:   {cert_id}\n"
            f"  Subject:       {subject}\n"
            f"  Form:          {form_code}\n"
            f"  Signature:     [Embedded PNG signature image]\n"
            f"{'=' * 60}\n"
        )
        signed_bytes = content + sig_block.encode("utf-8")

    elif ext == ".pdf":
        # Create signature overlay page — dùng Unicode font (Be Vietnam Pro)
        overlay_pdf = FPDF(orientation="P", unit="mm", format="A4")
        registered = register_vintage_fonts(overlay_pdf)
        overlay_pdf.add_page()

        fam_title, _ = get_font("title", registered)
        fam_body, _ = get_font("body", registered)

        overlay_pdf.set_font(fam_title, "B", 14)
        overlay_pdf.set_text_color(122, 36, 50)  # burgundy
        overlay_pdf.cell(0, 10, text=safe_text("MSB SmartForm AI — Trang chữ ký số (mô phỏng)", registered), new_x="LMARGIN", new_y="NEXT")
        overlay_pdf.ln(5)
        overlay_pdf.set_font(fam_body, "", 10)
        overlay_pdf.set_text_color(54, 37, 22)  # ink
        overlay_pdf.cell(0, 6, text=safe_text(f"Thời gian ký: {ts}", registered), new_x="LMARGIN", new_y="NEXT")
        overlay_pdf.cell(0, 6, text=safe_text(f"Chứng thư số: {cert_id}", registered), new_x="LMARGIN", new_y="NEXT")
        overlay_pdf.cell(0, 6, text=safe_text(f"Chủ sở hữu: {subject}", registered), new_x="LMARGIN", new_y="NEXT")
        overlay_pdf.cell(0, 6, text=safe_text(f"Mẫu: {form_code}", registered), new_x="LMARGIN", new_y="NEXT")
        overlay_pdf.ln(8)

        # Embed signature image
        try:
            sig_data = signature_image_b64.split(",", 1)[-1] if "," in signature_image_b64 else signature_image_b64
            sig_bytes = base64.b64decode(sig_data)
            overlay_pdf.image(io.BytesIO(sig_bytes), x=30, y=overlay_pdf.get_y(), w=80, h=40)
        except Exception as e:
            overlay_pdf.cell(0, 10, text=safe_text(f"[Lỗi nhập ảnh chữ ký: {e}]", registered), new_x="LMARGIN", new_y="NEXT")

        overlay_pdf.ln(45)
        overlay_pdf.set_draw_color(112, 66, 20)  # sepia
        overlay_pdf.line(30, overlay_pdf.get_y(), 110, overlay_pdf.get_y())
        overlay_pdf.set_font(fam_body, "", 9)
        overlay_pdf.cell(0, 5, text=safe_text("Chữ ký khách hàng (mô phỏng)", registered), new_x="LMARGIN", new_y="NEXT")

        overlay_bytes = overlay_pdf.output()
        if isinstance(overlay_bytes, str):
            overlay_bytes = overlay_bytes.encode("latin-1")

        # Merge original PDF + overlay
        from pypdf import PdfReader, PdfWriter
        writer = PdfWriter()
        reader_orig = PdfReader(io.BytesIO(content))
        for page in reader_orig.pages:
            writer.add_page(page)
        reader_overlay = PdfReader(io.BytesIO(overlay_bytes))
        for page in reader_overlay.pages:
            writer.add_page(page)
        out_buf = io.BytesIO()
        writer.write(out_buf)
        signed_bytes = out_buf.getvalue()

    else:
        signed_bytes = content

    signed_hash = hashlib.sha256(signed_bytes).hexdigest()
    webhook_payload = {
        "event": "FILE_SIGNED",
        "filename": filename,
        "formCode": form_code,
        "signedHash": signed_hash,
        "signedBy": subject,
        "certId": cert_id,
        "timestamp": datetime.now().isoformat(),
    }

    return signed_bytes, signed_hash, webhook_payload


def txt_to_vintage_pdf_bytes(content: bytes, form_code: str = "", title: str = "VĂN BẢN") -> bytes:
    """Chuyển nội dung text (bytes, UTF-8) thành PDF vintage lịch lãm.

    Áp dụng fix_vietnamese để sửa mojibake trước khi sinh PDF.
    """
    text = content.decode("utf-8", errors="replace")
    text = fix_vietnamese(text)
    return text_to_vintage_pdf(text, title=title, form_code=form_code)


def file_to_base64(data: bytes, mime: str = "application/octet-stream") -> str:
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"
