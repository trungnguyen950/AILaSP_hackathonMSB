"""Mock Digital Signature Engine — generate signed PDF + SHA256 hash + webhook notification.

This simulates a real digital signature flow:
1. Embed signature image into a PDF document
2. Compute SHA256 hash of the signed PDF
3. Return base64-encoded PDF + hash for download
4. Webhook payload for AI Agent notification

PDF đầu ra dùng phong cách vintage lịch lãm (vintage_pdf) với font Unicode
hỗ trợ đầy đủ tiếng Việt — không còn strip dấu như trước.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import logging
from datetime import datetime
from typing import Optional

from fpdf import FPDF

from .pdf_fonts import register_vintage_fonts, fix_vietnamese, safe_text, get_font
from .vintage_pdf import generate_vintage_pdf, generate_signed_vintage_pdf

logger = logging.getLogger("sign_engine")

MAX_SIG_DIM = 400


def _ascii(text: str) -> str:
    """DEPRECATED — chỉ giữ lại cho backward-compat.

    Ưu tiên dùng fix_vietnamese() + font Unicode để giữ dấu tiếng Việt.
    """
    if not text:
        return ""
    import unicodedata
    text = text.replace("\u2014", "-").replace("\u2013", "-").replace("\u2026", "...")
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "replace").decode("ascii")


def _b64_to_bytes(data_url: str) -> bytes:
    """Convert a base64 data URL (data:image/png;base64,...) to raw bytes."""
    if "," in data_url:
        data_url = data_url.split(",", 1)[1]
    return base64.b64decode(data_url)


def _build_vintage_doc(
    document_id: str,
    form_code: str,
    form_name: str,
    filled: dict[str, str],
    signatories: list[dict],
) -> dict:
    """Xây dict văn bản cho vintage_pdf từ dữ liệu form."""
    # Chuyển filled (key→value) thành dict label→value với label dễ đọc
    fields: dict[str, str] = {}
    for key, val in filled.items():
        if not val or val == "[CẦN KHÁCH HÀNG CUNG CẤP]":
            continue
        label = key.replace("_", " ")
        # Viết hoa chữ cái đầu
        label = label[0].upper() + label[1:] if label else label
        fields[label] = val

    return {
        "title": fix_vietnamese(form_name or "BIỂU MẪU HỒ SƠ"),
        "subtitle": f"Mã hồ sơ: {document_id}",
        "form_code": form_code,
        "form_name": form_name,
        "org_name": "NGÂN HÀNG TMCP HÀNG HẢI VIỆT NAM — MSB",
        "fields": fields,
        "signatories": signatories,
        "notes": [
            "Dữ liệu giả lập — không dùng cho giao dịch thật.",
            "Chữ ký số mô phỏng (mock digital signature).",
        ],
        "document_id": document_id,
        "footer_code": f"{form_code} · {document_id}",
        "watermark": "MSB",
    }


def generate_signed_pdf(
    document_id: str,
    form_code: str,
    form_name: str,
    filled: dict[str, str],
    signatories: list[dict],
    signature_image_b64: str,
    mock_cert: dict,
) -> tuple[bytes, str, dict]:
    """Generate a signed PDF (vintage style) with embedded signature image.

    Returns (pdf_bytes, sha256_hash, webhook_payload).
    """
    doc = _build_vintage_doc(document_id, form_code, form_name, filled, signatories)
    pdf_bytes, signed_hash = generate_signed_vintage_pdf(
        doc,
        signature_image_b64=signature_image_b64,
        mock_cert=mock_cert,
    )

    # --- Webhook payload ---
    webhook_payload = {
        "event": "DOCUMENT_SIGNED",
        "documentId": document_id,
        "formCode": form_code,
        "signedHash": signed_hash,
        "signedBy": mock_cert.get("subject", "unknown"),
        "certId": mock_cert.get("certId", ""),
        "timestamp": datetime.now().isoformat(),
    }

    return pdf_bytes, signed_hash, webhook_payload


def pdf_to_base64(pdf_bytes: bytes) -> str:
    """Convert PDF bytes to base64 data URL."""
    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    return f"data:application/pdf;base64,{b64}"


def notify_ai_agent(webhook_payload: dict, session_id: str) -> dict:
    """Mock webhook notification to AI Agent.

    In production, this would POST to an external AI Agent webhook URL.
    Here, we log it and return an acknowledgement — the agent processes it
    internally since the sign engine runs inside the same agent container.
    """
    logger.info("=" * 60)
    logger.info("WEBHOOK → AI Agent: DOCUMENT_SIGNED")
    logger.info("Payload: %s", json.dumps(webhook_payload, ensure_ascii=False, indent=2))
    logger.info("Session: %s", session_id)
    logger.info("=" * 60)

    doc_ref = webhook_payload.get("documentId") or webhook_payload.get("filename") or webhook_payload.get("formCode") or "hồ sơ"
    return {
        "acknowledged": True,
        "message": f"Đã ký số thành công cho {doc_ref}.",
        "nextStep": "Trạng thái hồ sơ đã cập nhật: SIGNED",
        "timestamp": datetime.now().isoformat(),
    }
