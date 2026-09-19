"""Vintage PDF Generator — sinh PDF phong cách cổ điển, lịch lãm cho MSB SmartForm AI.

Thiết kế vintage:
  - Bảng màu trầm ấm: sepia, burgundy, kem giấy cũ, nâu đất, xanh rêu, vàng nghệ.
  - Font serif cổ điển (Playfair Display) cho tiêu đề; sans-serif (Be Vietnam Pro)
    cho nội dung — tất cả hỗ trợ đầy đủ tiếng Việt (Unicode).
  - Khung viền kép trang nhã, góc filigree bo cong, watermark hoa văn mờ.
  - Cấu trúc: quốc hiệu → tên tổ chức → tiêu đề trang trọng → nội dung →
    khu vực chữ ký & con dấu → footer (ngày, mã văn bản, số trang).
  - Khổ A4, margin cân đối, tối ưu in ấn.

API chính:
    generate_vintage_pdf(document) -> bytes
    generate_signed_vintage_pdf(document, signature_image_b64, mock_cert) -> bytes

    document: dict với các trường:
        title, subtitle, form_code, form_name, org_name,
        fields: dict[label, value],
        signatories: list[dict(who, position)],
        accompanying_docs: list[str],
        notes: list[str],
        document_id, footer_code
"""
from __future__ import annotations

import base64
import hashlib
import io
import logging
from datetime import datetime
from typing import Optional

from fpdf import FPDF

from .pdf_fonts import register_vintage_fonts, get_font, fix_vietnamese, safe_text

logger = logging.getLogger("vintage_pdf")


# ── Bảng màu vintage (tông trầm ấm) ────────────────────────────────────
#         R    G    B    — vai trò
PALETTE = {
    "sepia":      (112,  66,  20),   # nâu sepia đậm — viền, tiêu đề
    "burgundy":   (122,  36,  50),   # đỏ burgundy — điểm nhấn, quốc hiệu
    "ink":        ( 54,  37,  22),   # nâu ink — nội dung chính
    "cream":      (244, 236, 216),   # kem giấy cũ — nền
    "parchment":  (237, 228, 204),   # giấy cổ — nền vùng nội dung
    "olive":      ( 85, 107,  47),   # xanh rêu — nhãn phụ
    "gold":       (184, 134,  11),   # vàng nghệ — filigree, divider
    "gold_light": (212, 175,  55),   # vàng nhạt — watermark
    "muted":      (120, 100,  72),   # nâu xám — footer, ghi chú
    "border":     (160, 120,  60),   # nâu viền
    "shadow":     (200, 180, 140),   # shadow nhạt
}


def _c(name: str) -> tuple[int, int, int]:
    return PALETTE[name]


# ── Lớp FPDF vintage ───────────────────────────────────────────────────
class VintagePDF(FPDF):
    """FPDF tuỳ biến với helper vẽ vintage: viền kép, filigree, watermark."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=22)
        self.registered = register_vintage_fonts(self)
        self._watermark: str | None = None
        self._footer_code: str = ""
        self._page_total = 0

    # -- helper chọn font theo vai trò --
    def use_font(self, role: str, size: float, style: str | None = None):
        family, default_style = get_font(role, self.registered)
        st = style if style is not None else default_style
        self.set_font(family, st, size)

    def _txt(self, s: str) -> str:
        return safe_text(s, self.registered)

    # -- watermark (vẽ trên mỗi trang qua header) --
    def set_watermark(self, text: str):
        self._watermark = text

    def header(self):
        # Watermark hoa văn mờ — chữ lớn xoay chéo giữa trang
        if self._watermark:
            wm = self._txt(self._watermark)
            self.use_font("title", 52, "B")
            w = self.get_string_width(wm)
            # Dùng màu rất nhạt (giả lập độ mờ — fpdf2 core không có alpha)
            cx, cy = self.w / 2, self.h / 2
            with self.local_context(text_color=(218, 200, 165)):
                self.rotate(35, cx, cy)
                self.text(cx - w / 2, cy, wm)
                self.rotate(0, cx, cy)

    def footer(self):
        # Footer: đường kẻ vàng nghệ + dòng ghi ngày & mã văn bản + số trang
        self.set_y(-18)
        self.set_draw_color(*_c("gold"))
        self.set_line_width(0.3)
        self.line(20, self.get_y(), self.w - 20, self.get_y())
        self.ln(2)
        self.use_font("small", 7.5, "")
        self.set_text_color(*_c("muted"))
        ts = self._txt(datetime.now().strftime("Ngày %d tháng %m năm %Y"))
        left = f"{ts}  ·  MSB SmartForm AI"
        right = self._txt(self._footer_code or "")
        pg = f"Trang {self.page_no()}/{{nb}}"
        self.cell(0, 5, text=self._txt(left), align="L")
        # right side: mã văn bản + số trang
        self.set_y(-13)
        self.set_x(self.w - 20 - self.get_string_width(self._txt(right + "  ·  " + pg)))
        self.cell(0, 5, text=self._txt(right + "  ·  " + pg), align="R")

    # -- Khung viền kép + góc filigree --
    def draw_border_frame(self):
        x0, y0 = 12, 16
        x1, y1 = self.w - 12, self.h - 16
        # Viền ngoài (đậm)
        self.set_draw_color(*_c("sepia"))
        self.set_line_width(0.8)
        self.rect(x0, y0, x1 - x0, y1 - y0)
        # Viền trong (mảnh, cách 3mm) — tạo hiệu ứng viền kép
        self.set_draw_color(*_c("gold"))
        self.set_line_width(0.3)
        self.rect(x0 + 3, y0 + 3, x1 - x0 - 6, y1 - y0 - 6)
        # Góc filigree (4 góc) — hoa văn bo cong tinh tế
        self._draw_corners(x0, y0, x1, y1)

    def _draw_corners(self, x0, y0, x1, y1):
        self.set_draw_color(*_c("gold"))
        self.set_line_width(0.4)
        r = 6  # bán kính góc bo
        for cx, cy, sx, sy in [
            (x0 + 3, y0 + 3, 1, 1),       # góc trên-trái
            (x1 - 3, y0 + 3, -1, 1),      # góc trên-phải
            (x0 + 3, y1 - 3, 1, -1),      # góc dưới-trái
            (x1 - 3, y1 - 3, -1, -1),     # góc dưới-phải
        ]:
            # Đường cong bo góc (arc 90°)
            self.set_xy(cx, cy)
            self.set_draw_color(*_c("gold"))
            # Vẽ 2 đường thẳng ngắn tạo góc + chấm tròn (signet mini)
            self.line(cx, cy, cx + sx * r, cy)
            self.line(cx, cy, cx, cy + sy * r)
            # Chấm tròn nhỏ ở góc — dấu triện mini
            self.set_fill_color(*_c("burgundy"))
            self.circle(cx + sx * 1.2, cy + sy * 1.2, 0.8, style="F")

    # -- Dòng kẻ đôi (double rule) --
    def double_rule(self, x0, x1, y, gap=1.2):
        self.set_draw_color(*_c("sepia"))
        self.set_line_width(0.5)
        self.line(x0, y, x1, y)
        self.set_draw_color(*_c("gold"))
        self.set_line_width(0.3)
        self.line(x0, y + gap, x1, y + gap)

    # -- Dấu triện / signet cách điệu cuối trang --
    def draw_signet(self, x, y, r=8):
        self.set_draw_color(*_c("burgundy"))
        self.set_line_width(0.6)
        self.circle(x, y, r, style="D")
        self.set_draw_color(*_c("gold"))
        self.set_line_width(0.3)
        self.circle(x, y, r - 1.5, style="D")
        # Chữ S (SmartForm) ở giữa
        self.use_font("title", 9, "B")
        self.set_text_color(*_c("burgundy"))
        self.set_xy(x - 3, y - 3)
        self.cell(6, 6, text="MSB", align="C")

    # -- Nhãn vùng (section heading) --
    def section_heading(self, text: str, y: float | None = None):
        if y is not None:
            self.set_y(y)
        self.ln(2)
        self.use_font("heading", 11, "B")
        self.set_text_color(*_c("burgundy"))
        self.cell(0, 7, text=self._txt(text), new_x="LMARGIN", new_y="NEXT")
        # Dòng kẻ ngang nhạt dưới tiêu đề mục
        self.set_draw_color(*_c("shadow"))
        self.set_line_width(0.2)
        self.line(20, self.get_y(), self.w - 20, self.get_y())
        self.ln(3)


# ── Hàm sinh PDF chính ────────────────────────────────────────────────
def _new_pdf(footer_code: str = "", watermark: str = "MSB") -> VintagePDF:
    pdf = VintagePDF()
    pdf.set_watermark(watermark)
    pdf._footer_code = footer_code
    return pdf


def _draw_header_block(pdf: VintagePDF, doc: dict):
    """Header: quốc hiệu + tên tổ chức + tiêu đề trang trọng."""
    # Quốc hiệu (CỘNG HÒA XÃ HỘI...) — burgundy, serif, căn giữa
    pdf.set_y(22)
    pdf.use_font("title", 10, "B")
    pdf.set_text_color(*_c("burgundy"))
    org = doc.get("org_name", "NGÂN HÀNG TMCP HÀNG HẢI VIỆT NAM — MSB")
    pdf.cell(0, 5, text=pdf._txt("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.use_font("small", 8, "I")
    pdf.set_text_color(*_c("muted"))
    pdf.cell(0, 4, text=pdf._txt("Độc lập — Tự do — Hạnh phúc"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    # Dòng kẻ đôi quốc hiệu
    pdf.double_rule(60, pdf.w - 60, pdf.get_y())
    pdf.ln(5)

    # Tên tổ chức (logo MSB) — serif đậm, sepia
    pdf.use_font("title", 15, "B")
    pdf.set_text_color(*_c("sepia"))
    pdf.cell(0, 7, text=pdf._txt(org), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.use_font("small", 8, "")
    pdf.set_text_color(*_c("muted"))
    pdf.cell(0, 4, text=pdf._txt("SmartForm AI — Trợ lý lập hồ sơ & biểu mẫu"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Tiêu đề văn bản — Playfair Display lớn, burgundy, căn giữa
    title = doc.get("title", doc.get("form_name", "BIỂU MẪU HỒ SƠ"))
    pdf.use_font("title", 18, "B")
    pdf.set_text_color(*_c("burgundy"))
    pdf.multi_cell(0, 8, text=pdf._txt(title), align="C")
    pdf.ln(1)

    # Phụ đề / mã mẫu
    subtitle = doc.get("subtitle", "")
    form_code = doc.get("form_code", "")
    sub_parts = []
    if form_code:
        sub_parts.append(f"Mã mẫu: {form_code}")
    if subtitle:
        sub_parts.append(subtitle)
    if sub_parts:
        pdf.use_font("label", 9, "")
        pdf.set_text_color(*_c("olive"))
        pdf.cell(0, 5, text=pdf._txt("  ·  ".join(sub_parts)), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    # Dòng kẻ đôi phân cách header / nội dung
    pdf.double_rule(20, pdf.w - 20, pdf.get_y())
    pdf.ln(4)


def _draw_fields(pdf: VintagePDF, fields: dict, signatories: list, accompanying: list, notes: list):
    """Nội dung chính: bảng thông tin đã điền + người ký + hồ sơ kèm theo."""
    # ── Thông tin đã điền ──
    if fields:
        pdf.section_heading("THÔNG TIN ĐÃ ĐIỀN")
        # Bảng 2 cột: nhãn (serif italic, olive) | giá trị (sans, ink)
        col_x = 22
        label_w = 70
        val_x = col_x + label_w
        val_w = pdf.w - 20 - val_x
        for label, value in fields.items():
            if value is None or value == "" or value == "[CẦN KHÁCH HÀNG CUNG CẤP]":
                continue
            # Kiểm tra còn đủ chỗ không, nếu không → trang mới
            if pdf.get_y() > pdf.h - 40:
                pdf.add_page()
                pdf.draw_border_frame()
            y = pdf.get_y()
            # Nhãn
            pdf.set_xy(col_x, y)
            pdf.use_font("body", 9.5, "I")
            pdf.set_text_color(*_c("olive"))
            pdf.multi_cell(label_w, 5.5, text=pdf._txt(str(label)) + ":", align="L")
            # Giá trị
            pdf.set_xy(val_x, y)
            pdf.use_font("body", 10, "")
            pdf.set_text_color(*_c("ink"))
            pdf.multi_cell(val_w, 5.5, text=pdf._txt(str(value)), align="L")
            # Xác định y lớn nhất giữa nhãn & giá trị
            new_y = max(pdf.get_y(), y + 6)
            pdf.set_y(new_y)
            # Dòng kẻ ngang nhạt giữa các dòng
            pdf.set_draw_color(*_c("shadow"))
            self_line = pdf
            self_line.set_line_width(0.15)
            pdf.line(col_x, pdf.get_y(), pdf.w - 20, pdf.get_y())
            pdf.ln(1.5)
        pdf.ln(2)

    # ── Người ký ──
    if signatories:
        if pdf.get_y() > pdf.h - 50:
            pdf.add_page()
            pdf.draw_border_frame()
        pdf.section_heading("NGƯỜI KÝ")
        for s in signatories:
            who = s.get("who", "") if isinstance(s, dict) else str(s)
            pos = s.get("position", "") if isinstance(s, dict) else ""
            pos_sign = s.get("position_to_sign", "") if isinstance(s, dict) else ""
            pdf.use_font("label", 10, "B")
            pdf.set_text_color(*_c("sepia"))
            pdf.cell(0, 6, text=pdf._txt(f"  •  {who}"), new_x="LMARGIN", new_y="NEXT")
            pdf.use_font("small", 8.5, "I")
            pdf.set_text_color(*_c("muted"))
            detail = f"      Chức vụ: {pos}" + (f"  ·  Ký cho vị trí: {pos_sign}" if pos_sign else "")
            pdf.cell(0, 5, text=pdf._txt(detail), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        pdf.ln(2)

    # ── Hồ sơ kèm theo ──
    if accompanying:
        if pdf.get_y() > pdf.h - 45:
            pdf.add_page()
            pdf.draw_border_frame()
        pdf.section_heading("HỒ SƠ KÈM THEO")
        for d in accompanying:
            pdf.use_font("body", 9.5, "")
            pdf.set_text_color(*_c("ink"))
            pdf.cell(0, 5.5, text=pdf._txt(f"  [ ]  {d}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    # ── Ghi chú ──
    if notes:
        if pdf.get_y() > pdf.h - 35:
            pdf.add_page()
            pdf.draw_border_frame()
        pdf.section_heading("GHI CHÚ")
        for n in notes:
            pdf.use_font("small", 8.5, "I")
            pdf.set_text_color(*_c("muted"))
            pdf.multi_cell(0, 5, text=pdf._txt(f"  •  {n}"))
            pdf.ln(0.5)


def _draw_signature_area(pdf: VintagePDF, signature_image_b64: str | None = None, mock_cert: dict | None = None):
    """Khu vực chữ ký & con dấu — cuối văn bản."""
    if pdf.get_y() > pdf.h - 65:
        pdf.add_page()
        pdf.draw_border_frame()
    pdf.ln(4)
    pdf.section_heading("CHỮ KÝ & CON DẤU")

    # Tạo 2 cột: trái = khách hàng, phải = đại diện MSB
    col_top = pdf.get_y()
    left_x, right_x = 25, pdf.w / 2 + 5
    col_w = pdf.w / 2 - 30

    # Cột trái — chữ ký khách hàng (embed image nếu có)
    pdf.set_xy(left_x, col_top)
    pdf.use_font("label", 9, "B")
    pdf.set_text_color(*_c("sepia"))
    pdf.cell(col_w, 6, text=pdf._txt("Khách hàng / Người lập"), new_x="LMARGIN", new_y="NEXT")

    if signature_image_b64:
        try:
            raw = signature_image_b64.split(",", 1)[-1] if "," in signature_image_b64 else signature_image_b64
            sig_bytes = base64.b64decode(raw)
            img_h = 28
            pdf.image(io.BytesIO(sig_bytes), x=left_x + 5, y=pdf.get_y() + 2, w=60, h=img_h)
            pdf.set_y(pdf.get_y() + img_h + 4)
        except Exception as e:
            pdf.use_font("small", 8, "I")
            pdf.set_text_color(*_c("muted"))
            pdf.cell(col_w, 5, text=pdf._txt(f"[Chữ ký: {e}]"), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(20)
    else:
        # Khung chữ ký rỗng (dấu chấm X)
        pdf.ln(22)

    # Đường kẻ chữ ký
    pdf.set_x(left_x)
    pdf.set_draw_color(*_c("ink"))
    pdf.set_line_width(0.4)
    pdf.line(left_x, pdf.get_y(), left_x + col_w - 5, pdf.get_y())
    pdf.ln(1.5)
    pdf.use_font("small", 8, "I")
    pdf.set_text_color(*_c("muted"))
    pdf.set_x(left_x)
    pdf.cell(col_w, 4, text=pdf._txt("(Ký, ghi rõ họ tên và đóng dấu)"), new_x="LMARGIN", new_y="NEXT")

    # Cột phải — đại diện MSB
    pdf.set_xy(right_x, col_top)
    pdf.use_font("label", 9, "B")
    pdf.set_text_color(*_c("sepia"))
    pdf.cell(col_w, 6, text=pdf._txt("Đại diện MSB"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(24)
    pdf.set_x(right_x)
    pdf.set_draw_color(*_c("ink"))
    pdf.set_line_width(0.4)
    pdf.line(right_x, pdf.get_y(), right_x + col_w - 5, pdf.get_y())
    pdf.ln(1.5)
    pdf.use_font("small", 8, "I")
    pdf.set_text_color(*_c("muted"))
    pdf.set_x(right_x)
    pdf.cell(col_w, 4, text=pdf._txt("(Ký, ghi rõ họ tên)"), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # Thông tin chứng thư số (nếu có)
    if mock_cert:
        pdf.use_font("small", 8, "")
        pdf.set_text_color(*_c("muted"))
        cert_id = mock_cert.get("certId", "N/A")
        subject = mock_cert.get("subject", "N/A")
        issuer = mock_cert.get("issuer", "N/A")
        valid = f"{mock_cert.get('validFrom', '')} ÷ {mock_cert.get('validTo', '')}"
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        info_lines = [
            f"Chứng thư số: {cert_id}  ·  Cấp bởi: {issuer}",
            f"Chủ sở hữu: {subject}",
            f"Hiệu lực: {valid}  ·  Thời gian ký: {ts}",
        ]
        for line in info_lines:
            pdf.cell(0, 4.5, text=pdf._txt(line), new_x="LMARGIN", new_y="NEXT")

    # Dấu triện / signet cách điệu ở góc phải
    pdf.draw_signet(pdf.w - 28, pdf.get_y() + 4, r=7)


def _finalize(pdf: VintagePDF) -> bytes:
    pdf._page_total = pdf.page_no()
    out = pdf.output()
    if isinstance(out, str):
        out = out.encode("latin-1")
    return bytes(out)


def generate_vintage_pdf(doc: dict) -> bytes:
    """Sinh PDF vintage từ dict văn bản. Trả về bytes PDF.

    doc keys (tất cả optional):
        title, subtitle, form_code, form_name, org_name,
        fields (dict), signatories (list[dict]),
        accompanying_docs (list[str]), notes (list[str]),
        document_id, footer_code, watermark
    """
    pdf = _new_pdf(
        footer_code=doc.get("footer_code") or doc.get("form_code") or "",
        watermark=doc.get("watermark") or "MSB",
    )
    pdf.add_page()
    pdf.draw_border_frame()
    _draw_header_block(pdf, doc)
    _draw_fields(
        pdf,
        fields=doc.get("fields") or {},
        signatories=doc.get("signatories") or [],
        accompanying=doc.get("accompanying_docs") or [],
        notes=doc.get("notes") or [],
    )
    _draw_signature_area(
        pdf,
        signature_image_b64=doc.get("signature_image"),
        mock_cert=doc.get("mock_cert"),
    )
    return _finalize(pdf)


def generate_signed_vintage_pdf(
    doc: dict,
    signature_image_b64: str,
    mock_cert: dict,
) -> tuple[bytes, str]:
    """Sinh PDF vintage đã ký (embed chữ ký + thông tin chứng thư).

    Trả về (pdf_bytes, sha256_hash).
    """
    doc = dict(doc)
    doc["signature_image"] = signature_image_b64
    doc["mock_cert"] = mock_cert
    pdf_bytes = generate_vintage_pdf(doc)
    signed_hash = hashlib.sha256(pdf_bytes).hexdigest()
    return pdf_bytes, signed_hash


def text_to_vintage_pdf(text: str, title: str = "VĂN BẢN", form_code: str = "") -> bytes:
    """Chuyển text thô (đã sửa font) thành PDF vintage.

    Phân tích text theo dòng: header → đoạn → chữ ký.
    Dùng cho 'bản mềm' .txt tải về từ chat/forms page.
    """
    lines = [fix_vietnamese(l).rstrip() for l in text.splitlines()]
    fields: dict[str, str] = {}
    notes: list[str] = []
    signatories: list[str] = []
    section = "fields"

    for line in lines:
        s = line.strip()
        if not s:
            continue
        up = s.upper()
        # Phát hiện tiêu đề mục
        if "THÔNG TIN" in up and ("ĐIỀN" in up or "DA DIEN" in up):
            section = "fields"; continue
        if "NGƯỜY KÝ" in up or "NGUOI KY" in up:
            section = "sign"; continue
        if "HỒ SƠ KÈM" in up or "HO SO KEM" in up:
            section = "notes"; continue
        if "GHI CHÚ" in up or "GHI CHU" in up or "LƯU Ý" in up or "LUU Y" in up:
            section = "notes"; continue
        if s.startswith("=" * 10) or s.startswith("─" * 10):
            continue

        if section == "fields":
            # Dòng dạng "  * Nhãn : giá trị" hoặc "  Nhãn: giá trị"
            if ":" in s or " :" in s:
                parts = s.lstrip("* ").split(":", 1)
                if len(parts) == 2 and parts[0].strip():
                    fields[parts[0].strip()] = parts[1].strip()
                    continue
        if section == "sign":
            signatories.append(s.lstrip("-•* "))
            continue
        if section == "notes":
            notes.append(s.lstrip("-•* "))
            continue
        # Dòng không thuộc mục nào → ghi chú
        if s:
            notes.append(s)

    doc = {
        "title": fix_vietnamese(title),
        "form_code": form_code,
        "fields": fields,
        "signatories": [{"who": sig, "position": "", "position_to_sign": ""} for sig in signatories],
        "notes": notes,
        "footer_code": form_code,
    }
    return generate_vintage_pdf(doc)
