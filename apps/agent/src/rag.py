"""RAG retriever: rule-based + keyword scoring over Form Registry.

Demo: 8 forms with rich metadata → deterministic retrieval, no embedding model needed.
Prod path: swap for pgvector HNSW (see ADR-3).
"""
from __future__ import annotations

from .kb import KnowledgeBase
from .models import Customer, FormMeta

# Intent → (business_group hints, segment hints, keyword hints)
INTENT_MAP: dict[str, dict] = {
    "ACCOUNT": {"group": ["Tài khoản"], "kw": ["tài khoản", "mở tài khoản", "thay đổi tài khoản", "account"]},
    "ACCOUNT CHANGE": {"group": ["Tài khoản"], "kw": ["thay đổi", "thông tin", "change"]},
    "ACCOUNT HOLDER CHANGE": {"group": ["Tài khoản"], "kw": ["chủ tài khoản", "holder"]},
    "LEGAL REP CHANGE": {"group": ["Tài khoản"], "kw": ["đại diện", "giám đốc", "đổi giám đốc", "representative"]},
    "EBANK": {"group": ["eBank"], "kw": ["ebank", "internet banking", "ib", "ngân hàng điện tử", "online banking"]},
    "USER": {"group": ["eBank"], "kw": ["người dùng", "người sử dụng", "kế toán", "user", "accountant"]},
    "AUTHORIZATION": {"group": ["eBank"], "kw": ["phân quyền", "ủy quyền", "authorization", "authority"]},
    "MAKER": {"group": ["eBank"], "kw": ["lập lệnh", "maker", "prepare", "payment"]},
    "CHECKER": {"group": ["eBank"], "kw": ["kiểm soát", "checker", "control"]},
    "APPROVER": {"group": ["eBank"], "kw": ["duyệt", "phê duyệt", "approver", "approval", "approve"]},
    "LIMIT": {"group": ["eBank"], "kw": ["hạn mức", "tăng hạn mức", "giảm hạn mức", "limit"]},
    "OTP": {"group": ["eBank", "Tài khoản"], "kw": ["otp", "người nhận otp", "authentication"]},
    "DIGITAL SIGNATURE": {"group": ["Chữ ký số"], "kw": ["chữ ký số", "chứng thư", "token", "cts", "digital signature"]},
    "E-TAX": {"group": ["Thuế điện tử"], "kw": ["thuế điện tử", "nộp thuế", "etax", "liên kết thuế", "e-tax"]},
    "PHONE CHANGE": {"group": ["Tài khoản"], "kw": ["số điện thoại", "đổi điện thoại", "đt", "sđt", "sdt", "đổi sđt", "đổi sdt", "phone"]},
    "EMAIL CHANGE": {"group": ["Tài khoản"], "kw": ["email", "đổi email"]},
    "SERVICE REGISTRATION": {"group": ["eBank"], "kw": ["đăng ký", "kích hoạt", "register", "registration"]},
    "SERVICE TERMINATION": {"group": ["eBank"], "kw": ["khóa", "mở khóa", "tạm ngưng", "hủy", "terminate", "lock"]},
    "FDI": {"group": ["eBank"], "kw": ["fdi", "foreign", "nước ngoài", "bilingual", "song ngữ", "vi-en", "english", "passport", "quốc tịch", "nationality", "erc", "irc", "investment"]},
}


def classify_keywords(text: str) -> list[str]:
    """Rule-based intent classification from free-text (fallback / primary for demo)."""
    t = text.lower()
    intents: list[str] = []
    for intent, hints in INTENT_MAP.items():
        if any(k in t for k in hints["kw"]):
            intents.append(intent)
    # normalize: EBANK sub-intents imply EBANK context
    if any(i in intents for i in ["USER", "MAKER", "CHECKER", "APPROVER", "LIMIT"]) and "EBANK" not in intents:
        intents.append("EBANK")
    return intents or ["ACCOUNT"]


def retrieve(kb: KnowledgeBase, intents: list[str], customer: Customer | None, text: str = "") -> list[FormMeta]:
    """Score active forms by intent + customer segment + keyword overlap. Return ranked list."""
    candidates = kb.list_active()
    t = text.lower()
    scored: list[tuple[float, FormMeta]] = []
    for m in candidates:
        score = 0.0
        # intent → business_group match
        for intent in intents:
            hints = INTENT_MAP.get(intent, {})
            if m.business_group in hints.get("group", []):
                score += 3.0
            for kw in hints.get("kw", []):
                if kw in m.use_case.lower() or kw in m.name.lower():
                    score += 1.0
        # customer segment
        if customer:
            if customer.type == "individual" and "KHCN" in m.segment:
                score += 2.0
            if customer.type == "org" and "KHTC" in m.segment:
                score += 2.0
            # FDI customer → strongly prefer FDI/bilingual forms
            if customer.is_fdi:
                if "FDI" in m.segment or m.bilingual:
                    score += 8.0
                else:
                    score -= 2.0  # penalize non-FDI forms for FDI customers
        # FDI intent → prefer FDI forms
        if "FDI" in intents and ("FDI" in m.segment or m.bilingual):
            score += 5.0
        # direct keyword overlap with use_case/name
        for word in re_split_words(t):
            if len(word) < 3:
                continue
            if word in m.use_case.lower() or word in m.name.lower():
                score += 0.5
        # prefer newer version handled by active filter; small bonus for explicit code mention
        if m.code.lower() in t:
            score += 5.0
        scored.append((score, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    # return top forms with score > 0
    return [m for s, m in scored if s > 0]


def re_split_words(text: str) -> list[str]:
    import re

    return re.findall(r"[a-z0-9à-ỹ]+", text.lower())
