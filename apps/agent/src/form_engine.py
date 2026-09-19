"""Form Engine: fill, validate, render."""
from __future__ import annotations

import re

from .models import FormTemplate

MISSING = "[CẦN KHÁCH HÀNG CUNG CẤP]"

# Reject list — never accept/store
SECRET_KEYS = {
    "pin",
    "password",
    "otp",
    "private_key",
    "privatekey",
    "secret_key",
    "secretkey",
    "api_key",
    "apikey",
}


def is_secret(key: str) -> bool:
    k = key.lower().replace("-", "_")
    return k in SECRET_KEYS


def fill(template: FormTemplate, values: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    """Fill template fields with values. Returns (filled, missing_required)."""
    filled: dict[str, str] = {}
    missing: list[str] = []
    for f in template.fields:
        if is_secret(f.key):
            continue  # never fill secrets
        val = values.get(f.key) or values.get(f.label)
        if val:
            filled[f.key] = val
        elif f.required:
            filled[f.key] = MISSING
            missing.append(f.key)
        else:
            filled[f.key] = ""
    return filled, missing


def validate(template: FormTemplate, filled: dict[str, str]) -> list[str]:
    """Run per-field validation. Returns list of violation messages."""
    violations: list[str] = []
    for f in template.fields:
        val = filled.get(f.key, "")
        if not val or val == MISSING:
            if f.required:
                violations.append(f"{f.label}: trường bắt buộc còn trống")
            continue
        v = (f.validation or "").lower()
        if "mst_10" in v and not re.match(r"^\d{10}$", val):
            violations.append(f"{f.label}: MST phải đúng 10 chữ số")
        if "cccd_12" in v and not re.match(r"^\d{12}$", val):
            violations.append(f"{f.label}: CCCD phải đúng 12 chữ số")
        if "phone_vn" in v and not re.match(r"^0\d{9,10}$", val):
            violations.append(f"{f.label}: số điện thoại không hợp lệ")
        if "email" in v and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", val):
            violations.append(f"{f.label}: email không hợp lệ")
        if "msb_account" in v and not re.match(r"^\d{9,12}$", val):
            violations.append(f"{f.label}: số tài khoản MSB không hợp lệ")
        if f.type == "enum" and f.options and val not in f.options:
            violations.append(f"{f.label}: phải là một trong {', '.join(f.options)}")
    return violations


def render_html(template: FormTemplate, filled: dict[str, str]) -> str:
    """Render a simple HTML preview of the filled form (demo). Supports bilingual labels."""
    rows = []
    for f in template.fields:
        val = filled.get(f.key, "")
        cls = "missing" if val == MISSING else ""
        label = f.label
        if f.label_en:
            label = f"{f.label} / {f.label_en}"
        rows.append(f'<tr><td>{label}</td><td class="{cls}">{val}</td></tr>')
    meta = template.meta
    title = f"{meta.code} — {meta.name}"
    if meta.name_en:
        title = f"{meta.code} — {meta.name} / {meta.name_en}"
    return (
        f"<div class='msb-form'><h3>{title}</h3>"
        f"<p>Phiên bản {meta.version} · Hiệu lực {meta.effective_date}</p>"
        f"<table>{''.join(rows)}</table></div>"
    )


def build_checklist(template: FormTemplate) -> list[dict]:
    """Build submission checklist from form + accompanying docs."""
    items: list[dict] = [{"item": f"Biểu mẫu {template.meta.code}", "required": True, "done": True}]
    for doc in template.meta.accompanying_docs:
        items.append({"item": doc, "required": True, "done": False})
    return items
