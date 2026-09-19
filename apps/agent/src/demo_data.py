"""5 demo customers (giả lập). Tuyệt đối không dùng dữ liệu thật."""
from __future__ import annotations

from .models import Customer

DEMO_CUSTOMERS: list[Customer] = [
    Customer(
        name="CÔNG TY CỔ PHẦN X",
        type="org",
        org_type="CP",
        tax_id="0101234567",
        account_no="123456789999",
        legal_rep="NGUYỄN VĂN X",
    ),
    Customer(
        name="CÔNG TY TNHH MỘT THÀNH VIÊN Y",
        type="org",
        org_type="TNHH1TV",
        tax_id="0102345678",
        account_no="234567899999",
        legal_rep="NGUYỄN VĂN Y",
    ),
    Customer(
        name="CÔNG TY TNHH HAI THÀNH VIÊN TRỞ LÊN Z",
        type="org",
        org_type="TNHH2TV",
        tax_id="0103456789",
        account_no="345678999999",
        legal_rep="NGUYỄN VĂN Z",
    ),
    Customer(
        name="DOANH NGHIỆP TƯ NHÂN A",
        type="org",
        org_type="DNTN",
        tax_id="0104567890",
        account_no="456789999999",
        legal_rep="NGUYỄN VĂN A",
    ),
    Customer(
        name="NGUYỄN VĂN A",
        type="individual",
        cccd="001234567890",
        account_no="567899999999",
    ),
    Customer(
        name="CÔNG TY TNHH FDI ALPHA VIỆT NAM",
        name_en="ALPHA VIETNAM FDI COMPANY LIMITED",
        type="org",
        org_type="FDI",
        is_fdi=True,
        tax_id="0109876543",
        account_no="987654321000",
        legal_rep="David Chen",
        legal_rep_nationality="Singapore",
        legal_rep_passport="S1234567A",
    ),
]


def match_demo_customer(text: str) -> Customer | None:
    """Match a demo customer by keyword/abbreviation in the user's text."""
    t = text.upper()
    # abbreviation aliases → demo index
    aliases = [
        (["CP X", "CỔ PHẦN X", "CONG TY CO PHAN X"], 0),
        (["TNHH 1TV Y", "TNHH MỘT THÀNH VIÊN Y", "1TV Y"], 1),
        (["TNHH 2TV", "TNHH HAI THÀNH VIÊN", "2TV Z"], 2),
        (["DNTN A", "DOANH NGHIỆP TƯ NHÂN A", "TƯ NHÂN A"], 3),
        (["CÁ NHÂN", "CÁ NHAN", "NGUYỄN VĂN A", "NGUYEN VAN A"], 4),
        (["FDI", "ALPHA", "FOREIGN", "DAVID CHEN", "DAVID"], 5),
    ]
    for keys, idx in aliases:
        if any(k in t for k in keys):
            return DEMO_CUSTOMERS[idx]
    # fallback: match distinctive tokens from full name
    for c in DEMO_CUSTOMERS:
        key = c.name.upper()
        tokens = [w for w in key.replace("CÔNG TY", "").replace("DOANH NGHIỆP", "").split() if len(w) > 1]
        if any(tok in t for tok in tokens):
            return c
    return None
