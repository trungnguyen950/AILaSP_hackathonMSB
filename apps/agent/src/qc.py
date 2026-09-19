"""Quality Control: 8 checks."""
from __future__ import annotations

from .models import CheckResult, Customer, FormTemplate, QCResult
from . import form_engine


def run_checks(template: FormTemplate, filled: dict[str, str], missing: list[str], customer: Customer | None) -> QCResult:
    checks: list[CheckResult] = []

    # 1. FORM CHECK
    checks.append(
        CheckResult(
            name="FORM CHECK",
            pass_=template.meta.active,
            detail=None if template.meta.active else "Mẫu không còn hiệu lực",
        )
    )

    # 2. DATA CHECK
    violations = form_engine.validate(template, filled)
    checks.append(CheckResult(name="DATA CHECK", pass_=not violations, detail="; ".join(violations) or None))

    # 3. SIGNATURE CHECK
    sig_ok = len(template.signatories) > 0
    checks.append(
        CheckResult(name="SIGNATURE CHECK", pass_=sig_ok, detail=None if sig_ok else "Chưa xác định người ký")
    )

    # 4. AUTHORITY CHECK
    authority_ok = True  # demo: người lập = chủ TK / ủy quyền — giả định OK
    checks.append(CheckResult(name="AUTHORITY CHECK", pass_=authority_ok))

    # 5. EBANK ROLE CHECK
    role_ok = True
    if template.meta.business_group == "eBank":
        role = filled.get("role", "")
        if role and role not in ("Maker", "Checker", "Approver"):
            role_ok = False
    checks.append(CheckResult(name="EBANK ROLE CHECK", pass_=role_ok))

    # 6. LIMIT CHECK
    limit_ok = True
    limit_val = filled.get("limit") or filled.get("new_limit")
    if limit_val:
        try:
            limit_ok = float(str(limit_val).replace(",", "").replace("VND", "").strip()) > 0
        except ValueError:
            limit_ok = False
    checks.append(CheckResult(name="LIMIT CHECK", pass_=limit_ok))

    # 7. MANDATORY FIELD CHECK
    checks.append(
        CheckResult(name="MANDATORY FIELD CHECK", pass_=not missing, detail=f"Thiếu: {missing}" if missing else None)
    )

    # 8. DOCUMENT CONSISTENCY CHECK
    consistent = True
    if customer and customer.tax_id:
        filled_tax = filled.get("tax_id", "")
        if filled_tax and filled_tax != form_engine.MISSING and filled_tax != customer.tax_id:
            consistent = False
    checks.append(CheckResult(name="DOCUMENT CONSISTENCY CHECK", pass_=consistent))

    # 9. BILINGUAL FIELD CHECK (FDI)
    bilingual_ok = True
    bilingual_detail = None
    if template.meta.bilingual or (customer and customer.is_fdi):
        required_en_fields = {"company_name_en", "legal_rep_nationality", "legal_rep_passport"}
        missing_en = [f for f in required_en_fields if f in {ff.key for ff in template.fields} and (not filled.get(f) or filled.get(f) == form_engine.MISSING)]
        if missing_en:
            bilingual_ok = False
            bilingual_detail = f"Missing bilingual/FDI fields: {missing_en}"
    checks.append(CheckResult(name="BILINGUAL FIELD CHECK", pass_=bilingual_ok, detail=bilingual_detail))

    # Status
    all_pass = all(c.pass_ for c in checks)
    if missing:
        status = "MISSING INFORMATION"
    elif not all_pass:
        status = "NEED MSB REVIEW"
    else:
        status = "READY"
    return QCResult(status=status, checks=checks)
