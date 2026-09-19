"""PDF Font Manager — đăng ký font Unicode hỗ trợ tiếng Việt + sửa mojibake.

Giải quyết triệt để lỗi font tiếng Việt trong PDF:
  - Font core của PDF (Helvetica/Times/Courier) chỉ hỗ trợ Latin-1/WinAnsi,
    KHÔNG chứa glyph cho các ký tự tiếng Việt có dấu (ạ, ơ, ư, đ, Ặ, ...).
  - Trước đây, code dùng _ascii() (NFKD + encode ascii) để strip dấu → chữ bị vỡ.
  - Giải pháp: nạp font TTF Unicode (Be Vietnam Pro, Playfair Display, DejaVu)
    có glyph đầy đủ tiếng Việt vào fpdf2, rồi ghi text nguyên gốc (UTF-8).

Font được dùng (tất cả đã verify có glyph tiếng Việt):
  - Playfair Display  : serif cổ điển, sang trọng — cho tiêu đề
  - Be Vietnam Pro    : sans-serif thanh lịch, thiết kế riêng cho tiếng Việt — nội dung
  - DejaVu Serif/Sans : fallback an toàn (có sẵn trên hệ điều hành)

Sử dụng:
    from src.pdf_fonts import register_vintage_fonts, fix_vietnamese
    register_vintage_fonts(pdf)          # pdf là instance FPDF
    pdf.set_font("Playfair", "B", 18)    # dùng font Unicode
    pdf.cell(0, 8, text="Nguyễn Văn A — CỘNG HÒA XÃ HỘI")
"""
from __future__ import annotations

import logging
import os
import re
import unicodedata
from pathlib import Path

logger = logging.getLogger("pdf_fonts")

# ── Định vị thư mục fonts ──────────────────────────────────────────────
#  apps/agent/fonts/  (chạy local & Docker — COPY fonts/ vào image)
#  Fallback: font hệ thống (/usr/share/fonts/truetype/dejavu)
_FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
if not _FONT_DIR.exists():
    _FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def _font_path(name: str) -> str | None:
    p = _FONT_DIR / name
    return str(p) if p.exists() else None


# Bảng đăng ký font: (family_alias, regular, bold, italic)
_FONT_REGISTRY = [
    ("Playfair",  "PlayfairDisplay-Regular.ttf", "PlayfairDisplay-Bold.ttf",  "PlayfairDisplay-Regular.ttf"),
    ("BeVietnam", "BeVietnamPro-Regular.ttf",    "BeVietnamPro-Bold.ttf",     "BeVietnamPro-Medium.ttf"),
    ("DejaVuSerif", "DejaVuSerif.ttf",           "DejaVuSerif-Bold.ttf",      "DejaVuSerif-Italic.ttf"),
    ("DejaVuSans",  "DejaVuSans.ttf",            "DejaVuSans-Bold.ttf",       "DejaVuSans.ttf"),
]

# Alias mặc định cho các vai trò trong văn bản vintage
ROLE_DEFAULTS = {
    "title":   ("Playfair",    "B"),
    "heading": ("Playfair",    "B"),
    "body":    ("BeVietnam",   ""),
    "label":   ("BeVietnam",   "B"),
    "small":   ("BeVietnam",   ""),
    "mono":    ("DejaVuSans",  ""),
    "serif":   ("DejaVuSerif", ""),
}


def register_vintage_fonts(pdf) -> dict[str, str]:
    """Đăng ký tất cả font Unicode Việt vào instance FPDF.

    Trả về dict {role: family} để caller biết font nào đã sẵn sàng.
    Nếu không tìm thấy TTF nào, fallback về font core (Helvetica) —
    khi đó text sẽ được truyền qua fix_vietnamese() để ít vỡ nhất.
    """
    registered: dict[str, str] = {}
    for family, regular, bold, italic in _FONT_REGISTRY:
        rp, bp, ip = _font_path(regular), _font_path(bold), _font_path(italic)
        if not rp:
            logger.warning("Font %s không tìm thấy (%s) — skip", family, regular)
            continue
        try:
            pdf.add_font(family, style="", fname=rp)
            if bp:
                pdf.add_font(family, style="B", fname=bp)
            if ip:
                pdf.add_font(family, style="I", fname=ip)
            # B+I: dùng bold (đa số font vintage không có file riêng)
            if bp:
                pdf.add_font(family, style="BI", fname=bp)
            registered[family] = rp
            logger.info("Registered font %s (%s)", family, regular)
        except Exception as e:
            logger.warning("Lỗi đăng ký font %s: %s", family, e)
    return registered


def get_font(role: str, registered: dict[str, str]) -> tuple[str, str]:
    """Trả về (family, style) cho một vai trò, kèm fallback an toàn."""
    pref_family, default_style = ROLE_DEFAULTS.get(role, ("BeVietnam", ""))
    if pref_family in registered:
        return pref_family, default_style
    for fam in ("BeVietnam", "DejaVuSans", "DejaVuSerif", "Playfair"):
        if fam in registered:
            return fam, default_style
    return "Helvetica", default_style  # font core cuối cùng


# ── Sửa mojibake tiếng Việt ────────────────────────────────────────────
# Mojibake xảy ra khi text Unicode bị decode sai encoding. Ví dụ phổ biến:
#   "Nguyễn" encode utf-8 → decode latin-1 → "Nguyá»…n"  (UTF-8 as Latin-1)
#   "Nguyễn" encode utf-8 → decode cp1252 → "Nguyá»…n"
#   "ạ" → "áº¡"  /  "ơ" → "Æ¡"  /  "đ" → "Ä‘"
# Chiến lược: thử re-encode chuỗi về bytes theo các encoding sai phổ biến,
# rồi decode lại UTF-8. Nếu kết quả hợp lý (chứa ký tự Việt có dấu) thì dùng.

_MANGLED_ENCODINGS = ("latin-1", "cp1252", "iso-8859-1")

# Dấu hiệu text đã bị mojibake (UTF-8 bị decode sai)
_MOJIBAKE_HINTS = re.compile(r"[ÃÂÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞß][\u0080-\u00BF]|â‚¬|Â¦|á»|áº|Ã‚|â€")

# Tập ký tự Việt có dấu (precomposed) để kiểm tra kết quả sửa
_VIET_CHARS = set("àáâãäåèéêëìíîïòóôõöùúûüýỳỹỵàáảãạằẳẵặèẻẽẹềểễệìỉĩịòỏõọồổỗộờởỡợùủũụừửữựỳỷỹỵđĂăĐđÊêÔơƠƯư")
_VIET_CHARS |= set(c.upper() for c in _VIET_CHARS)


def _looks_mojibake(text: str) -> bool:
    if not text:
        return False
    return bool(_MOJIBAKE_HINTS.search(text))


def _try_repair(text: str) -> str | None:
    """Thử sửa mojibake bằng cách re-encode round-trip."""
    for enc in _MANGLED_ENCODINGS:
        try:
            repaired = text.encode(enc, errors="strict").decode("utf-8", errors="strict")
            return repaired
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    return None


def fix_vietnamese(text: str) -> str:
    """Phát hiện và sửa lỗi font/mojibake cho text tiếng Việt.

    Pipeline:
      1. Chuẩn hoá NFC (compose các dấu tổ hợp về dạng precomposed).
      2. Nếu phát hiện mojibake → thử re-encode round-trip.
      3. Thay thế một số ký tự hỏng phổ biến bằng mapping tĩnh.
      4. Bỏ các ký tự thay thế '\ufffd' (U+FFFD REPLACEMENT CHARACTER).

    Hàm idempotent: text sạch sẽ không bị thay đổi.
    """
    if not text:
        return ""

    # 1. NFC compose
    text = unicodedata.normalize("NFC", text)

    # 2. Sửa mojibake (đệ quy: có thể bị mojibake 2 lớp)
    for _ in range(3):
        if not _looks_mojibake(text):
            break
        repaired = _try_repair(text)
        if repaired and repaired != text:
            text = unicodedata.normalize("NFC", repaired)
        else:
            break

    # 3. Mapping tĩnh cho các trường hợp hỏng cụ thể (dấu gạch ngang, dấu ba chấm)
    static_map = {
        "\u0085": "…",        # ellipsis bị hỏng
        "\u0097": "—",        # em dash bị hỏng
        "\u0096": "–",        # en dash bị hỏng
        "â‚¬": "€",
        "Â¦": "¦",
        "â€™": "’",
        "â€œ": "“",
        "â€\u009d": "”",
        "â€”": "—",
        "â€“": "–",
        "â€¦": "…",
    }
    for bad, good in static_map.items():
        text = text.replace(bad, good)

    # 4. Xóa ký tự thay thế (xuất hiện khi decode lỗi với errors="replace")
    text = text.replace("\ufffd", "")

    return text


def safe_text(text: str, registered: dict | None = None) -> str:
    """Trả về text đã sửa, an toàn để ghi vào PDF Unicode.

    Nếu không có font Unicode (registered rỗng) → strip dấu về ASCII
    (fallback cuối cùng, chỉ khi không có TTF).
    """
    cleaned = fix_vietnamese(text)
    if registered is not None and not registered:
        # Không có font Unicode → strip dấu để tránh glyph rỗng (ô vuông)
        cleaned = unicodedata.normalize("NFKD", cleaned).encode("ascii", "replace").decode("ascii")
    return cleaned


def has_vietnamese(text: str) -> bool:
    """Kiểm tra text có chứa ký tự tiếng Việt có dấu hay không."""
    return any(ch in _VIET_CHARS for ch in text)


__all__ = [
    "register_vintage_fonts",
    "get_font",
    "fix_vietnamese",
    "safe_text",
    "has_vietnamese",
    "ROLE_DEFAULTS",
]
