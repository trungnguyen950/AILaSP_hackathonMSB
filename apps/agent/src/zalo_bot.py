"""Zalo Bot Platform integration — gửi tin nhắn + ảnh preview cho khách hàng.

Zalo Bot API (giống Telegram Bot API):
  Base URL: https://bot-api.zaloplatforms.com/bot<BOT_TOKEN>/<method>
  Token nằm trong URL path (KHÔNG phải header).

Các method sử dụng:
  - getMe          : kiểm tra token + lấy thông tin bot
  - sendMessage    : gửi tin nhắn text (hỗ trợ markdown/html)
  - sendPhoto      : gửi ảnh (multipart upload hoặc URL)
  - setWebhook     : đăng ký webhook URL để nhận event từ user
  - getWebhookInfo : xem trạng thái webhook
  - deleteWebhook  : xoá webhook (chuyển sang polling)
  - getUpdates     : long polling (dev/local)

Bot Token lấy từ:
  1. AgentBase outbound auth provider "zalo-bot-token" (runtime auto-inject)
  2. Env var ZALO_BOT_TOKEN (local dev fallback)

Lưu ý: Zalo Bot API KHÔNG có sendDocument — không gửi file PDF trực tiếp được.
Giải pháp: gửi text notification (markdown) + gửi ảnh preview (PNG) tạo bằng Pillow.
"""
from __future__ import annotations

import base64
import io
import json
import logging
import os
from datetime import datetime
from typing import Optional

import httpx

logger = logging.getLogger("zalo_bot")

ZALO_BOT_API_BASE = "https://bot-api.zaloplatforms.com/bot"
DEFAULT_TIMEOUT = 30.0

# In-memory store chat_id của khách hàng khi họ nhắn cho bot (mô phỏng)
_KNOWN_CHAT_IDS: dict[str, dict] = {}


def get_bot_token() -> Optional[str]:
    """Lấy Zalo Bot token.

    Thứ tự ưu tiên:
      1. AgentBase outbound auth provider "zalo-bot-token"
      2. Env var ZALO_BOT_TOKEN
    """
    # 1. AgentBase runtime
    try:
        agent_identity = os.environ.get("GREENNODE_AGENT_IDENTITY")
        if agent_identity:
            from greennode_agentbase import IdentityClient, IAMCredentials

            client = IdentityClient(iam_credentials=IAMCredentials())
            import asyncio

            result = asyncio.get_event_loop().run_until_complete(
                client.get_api_key_for_agent_identity_async(
                    provider_name="zalo-bot-token",
                    agent_identity_name=agent_identity,
                )
            )
            if result and getattr(result, "apikey", None):
                logger.info("Zalo bot token lấy từ AgentBase auth provider 'zalo-bot-token'.")
                return result.apikey
    except Exception as e:
        logger.debug("AgentBase auth lookup failed (local dev?): %s", e)

    # 2. Env var fallback
    token = os.environ.get("ZALO_BOT_TOKEN")
    if token:
        logger.info("Zalo bot token lấy từ env var ZALO_BOT_TOKEN.")
        return token

    return None


def _api_url(token: str, method: str) -> str:
    return f"{ZALO_BOT_API_BASE}{token}/{method}"


def api_call(token: str, method: str, params: dict | None = None, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """Generic Zalo Bot API call (POST JSON)."""
    url = _api_url(token, method)
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=params or {})
    data = resp.json()
    logger.info("Zalo API %s → status=%s body=%s", method, resp.status_code, data)
    return data


def get_me(token: str) -> dict:
    """Kiểm tra token + lấy thông tin bot."""
    return api_call(token, "getMe")


def send_message(
    token: str,
    chat_id: str,
    text: str,
    parse_mode: str | None = "markdown",
    timeout: float = DEFAULT_TIMEOUT,
) -> dict:
    """Gửi tin nhắn text. Hỗ trợ parse_mode = 'markdown' hoặc 'html'."""
    params: dict = {"chat_id": chat_id, "text": text}
    if parse_mode:
        params["parse_mode"] = parse_mode
    return api_call(token, "sendMessage", params, timeout=timeout)


def send_photo_file(
    token: str,
    chat_id: str,
    file_bytes: bytes,
    filename: str,
    caption: str | None = None,
    mime: str = "image/png",
    timeout: float = DEFAULT_TIMEOUT,
) -> dict:
    """Gửi ảnh (hoặc file) qua multipart upload.

    Zalo Bot API không có sendDocument nên dùng sendPhoto để gửi file
    (best effort — có thể bị reject nếu không phải ảnh).
    """
    url = _api_url(token, "sendPhoto")
    files = {"photo": (filename, file_bytes, mime)}
    data: dict = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, files=files, data=data)
    data_resp = resp.json()
    logger.info("Zalo sendPhoto (multipart) → filename=%s status=%s body=%s", filename, resp.status_code, data_resp)
    return data_resp


def send_photo_url(
    token: str,
    chat_id: str,
    photo_url: str,
    caption: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict:
    """Gửi ảnh qua URL."""
    params: dict = {"chat_id": chat_id, "photo": photo_url}
    if caption:
        params["caption"] = caption
    return api_call(token, "sendPhoto", params, timeout=timeout)


def set_webhook(token: str, url: str, secret_token: str) -> dict:
    """Đăng ký webhook URL để nhận event từ Zalo."""
    return api_call(token, "setWebhook", {"url": url, "secret_token": secret_token})


def get_webhook_info(token: str) -> dict:
    """Xem trạng thái webhook hiện tại."""
    return api_call(token, "getWebhookInfo")


def delete_webhook(token: str) -> dict:
    """Xoá webhook (chuyển sang getUpdates polling)."""
    return api_call(token, "deleteWebhook")


def get_updates(token: str, timeout: int = 30) -> dict:
    """Long polling để lấy update (chỉ dùng cho dev/local)."""
    return api_call(token, "getUpdates", {"timeout": timeout}, timeout=timeout + 10)


# --- Webhook event handling ---

def handle_webhook_event(body: dict) -> dict:
    """Xử lý event nhận được từ Zalo webhook.

    Zalo gửi payload ở 2 dạng:
      1. {event_name, message, ...}          — dạng THẬT (trực tiếp top-level)
      2. {ok: true, result: {event_name, ...}} — dạng docs (có wrapper result)
    Hàm này handle cả 2.

    Lưu chat_id của user vào memory + trả về context để handler gửi phản hồi.
    Returns: {"event_name": ..., "chat_id": ..., "text": ..., "from": ...}
    """
    result = body.get("result") or body
    event_name = result.get("event_name", "") or body.get("event_name", "")
    message = result.get("message", {}) or body.get("message", {})
    from_info = message.get("from", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id", "")
    text = message.get("text", "")
    display_name = from_info.get("display_name", "")

    parsed = {
        "event_name": event_name,
        "chat_id": chat_id,
        "chat_type": chat.get("chat_type", ""),
        "text": text,
        "from_id": from_info.get("id", ""),
        "from_name": display_name,
        "is_bot": from_info.get("is_bot", False),
    }

    # Lưu chat_id (để agent biết gửi notification cho ai)
    if chat_id and not from_info.get("is_bot"):
        _KNOWN_CHAT_IDS[chat_id] = {
            "display_name": display_name,
            "first_seen": datetime.now().isoformat(),
        }
        logger.info("Saved Zalo chat_id=%s (name=%s). Total known: %d", chat_id, display_name, len(_KNOWN_CHAT_IDS))

    return parsed


def get_known_chat_ids() -> dict:
    """Trả về danh sách chat_id đã biết (từ webhook)."""
    return dict(_KNOWN_CHAT_IDS)


def resolve_chat_id(payload_chat_id: Optional[str], context_user_id: Optional[str]) -> Optional[str]:
    """Xác định chat_id người nhận.

    Thứ tự: payload.chat_id → env ZALO_CHAT_ID → known chat_ids (lấy 1 cái) → context.
    """
    cid = payload_chat_id or os.environ.get("ZALO_CHAT_ID")
    if cid:
        return cid
    if _KNOWN_CHAT_IDS:
        return next(iter(_KNOWN_CHAT_IDS))
    if context_user_id:
        return context_user_id
    return None


# --- Notification ---

def build_notification_text(
    document_id: str,
    form_code: str,
    signed_hash: str,
    signed_by: str,
    filename: str,
) -> str:
    """Sinh nội dung text thông báo ký thành công (markdown rich text)."""
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    short_hash = signed_hash[:16] if signed_hash else "N/A"
    return (
        f"# MSB SmartForm AI — Ký số thành công\n\n"
        f"**Tài liệu:** `{filename}`\n"
        f"**Mã hồ sơ:** `{document_id or form_code}`\n"
        f"**Người ký:** {signed_by}\n"
        f"**Hash (SHA256):** `{short_hash}...`\n"
        f"**Thời gian:** {ts}\n\n"
        f"---\n"
        f"Bản mềm PDF đã ký sẵn sàng. Vui lòng tải về từ hệ thống MSB SmartForm AI.\n"
        f"Cảm ơn quý khách đã sử dụng dịch vụ!"
    )


def send_notification_to_customer(
    token: str,
    chat_id: str,
    notification_text: str,
    pdf_bytes: bytes | None = None,
    pdf_filename: str | None = None,
) -> dict:
    """Gửi thông báo + ảnh preview cho khách hàng qua Zalo Bot.

    Workflow:
      1. Gửi text notification (markdown) — luôn thực hiện
      2. Tạo ảnh preview PNG từ PDF (dùng Pillow) — gửi qua sendPhoto

    Returns: dict tổng hợp {success, steps, ...}.
    """
    result: dict = {
        "chat_id": chat_id,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "steps": {},
    }

    # 1. Text notification (markdown)
    try:
        text_res = send_message(token, chat_id, notification_text, parse_mode="markdown")
        result["steps"]["text"] = text_res
        if not text_res.get("ok"):
            result["error"] = f"sendMessage thất bại: {text_res.get('description') or text_res}"
            return result
        result["steps"]["text_message_id"] = text_res.get("result", {}).get("message_id")
    except Exception as e:
        logger.error("Zalo sendMessage failed: %s", e)
        result["error"] = f"sendMessage exception: {e}"
        return result

    # 2. Tạo ảnh preview PNG từ PDF + gửi qua sendPhoto
    if pdf_bytes:
        try:
            png_bytes = _pdf_to_preview_png(pdf_bytes, pdf_filename or "document.pdf")
            if png_bytes:
                photo_res = send_photo_file(
                    token, chat_id, png_bytes,
                    filename=f"{(pdf_filename or 'preview').rsplit('.', 1)[0]}.png",
                    caption=f"📄 {(pdf_filename or 'Bản mềm đã ký')} — preview",
                    mime="image/png",
                )
                result["steps"]["photo"] = photo_res
                if photo_res.get("ok"):
                    result["steps"]["photo_message_id"] = photo_res.get("result", {}).get("message_id")
                else:
                    result["steps"]["photo_note"] = f"sendPhoto failed: {photo_res.get('description', '')}"
            else:
                result["steps"]["photo_note"] = "Không tạo được ảnh preview từ PDF"
        except Exception as e:
            logger.warning("Zalo sendPhoto (preview) failed: %s", e)
            result["steps"]["photo_error"] = str(e)

    # Text đã gửi thành công → overall success
    result["success"] = True
    return result


def _pdf_to_preview_png(pdf_bytes: bytes, filename: str) -> bytes | None:
    """Tạo ảnh preview PNG từ PDF.

    Thử extract embedded image từ PDF bằng pypdf (pure Python).
    Nếu không có image, tạo text-based preview PNG bằng pure Python (zlib + struct).
    Không dùng Pillow — zero external dependency.
    """
    try:
        # Thử extract embedded image từ PDF bằng pypdf
        try:
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            if len(reader.pages) > 0:
                page = reader.pages[0]
                if "/XObject" in page.get("/Resources", {}):
                    x_objects = page["/Resources"]["/XObject"].get_object()
                    for obj_name in x_objects:
                        obj = x_objects[obj_name]
                        if obj.get("/Subtype") == "/Image":
                            width = int(obj.get("/Width", 800))
                            height = int(obj.get("/Height", 600))
                            data = obj.get_data()
                            cs = str(obj.get("/ColorSpace", "/DeviceRGB"))
                            bits = int(obj.get("/BitsPerComponent", 8))

                            mode = "RGB" if "RGB" in cs else ("L" if "Gray" in cs else "RGB")

                            # Convert to RGB raw bytes
                            if mode == "L":
                                rgb_data = bytearray()
                                for b in data[:width * height]:
                                    rgb_data.extend([b, b, b])
                                raw = bytes(rgb_data)
                            elif mode == "RGB":
                                raw = data[:width * height * 3]
                            else:
                                # CMYK or other → simple fallback
                                raw = data[:width * height * 3]
                                if len(raw) < width * height * 3:
                                    raw = raw + b'\xff' * (width * height * 3 - len(raw))

                            # Resize to max 1200px wide
                            if width > 1200:
                                new_w = 1200
                                new_h = int(height * (1200 / width))
                                raw = _resize_rgb(raw, width, height, new_w, new_h)
                                width, height = new_w, new_h

                            png = _encode_png_rgb(raw, width, height)
                            if png:
                                logger.info("PDF preview PNG from embedded image: %dx%d", width, height)
                                return png
        except Exception as e:
            logger.debug("PDF image extraction failed: %s", e)

        # Fallback: tạo text-based preview PNG (pure Python)
        return _create_text_preview_png(filename)

    except Exception as e:
        logger.error("PDF to PNG preview failed: %s", e)
        return None


def _encode_png_rgb(raw_rgb: bytes, width: int, height: int) -> bytes | None:
    """Encode raw RGB bytes into PNG using only stdlib (zlib + struct).

    Minimal PNG encoder — no Pillow, no external deps.
    """
    import zlib
    import struct

    if width <= 0 or height <= 0:
        return None
    if len(raw_rgb) < width * height * 3:
        raw_rgb = raw_rgb + b'\xff' * (width * height * 3 - len(raw_rgb))

    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk = chunk_type + data
        crc = zlib.crc32(chunk) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk + struct.pack(">I", crc)

    # PNG signature
    sig = b'\x89PNG\r\n\x1a\n'

    # IHDR: width, height, bit_depth=8, color_type=2 (RGB), compression=0, filter=0, interlace=0
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = make_chunk(b'IHDR', ihdr_data)

    # IDAT: raw image data with filter byte (0 = None) per scanline
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(0)  # filter type: None
        start = y * width * 3
        scanlines.extend(raw_rgb[start:start + width * 3])
    compressed = zlib.compress(bytes(scanlines), 9)
    idat = make_chunk(b'IDAT', compressed)

    # IEND
    iend = make_chunk(b'IEND', b'')

    return sig + ihdr + idat + iend


def _resize_rgb(raw: bytes, old_w: int, old_h: int, new_w: int, new_h: int) -> bytes:
    """Simple nearest-neighbor resize for RGB data."""
    out = bytearray(new_w * new_h * 3)
    for y in range(new_h):
        src_y = min(int(y * old_h / new_h), old_h - 1)
        for x in range(new_w):
            src_x = min(int(x * old_w / new_w), old_w - 1)
            src_idx = (src_y * old_w + src_x) * 3
            dst_idx = (y * new_w + x) * 3
            out[dst_idx:dst_idx + 3] = raw[src_idx:src_idx + 3]
    return bytes(out)


def _create_text_preview_png(filename: str) -> bytes:
    """Tạo ảnh preview text-based bằng pure Python PNG encoder.

    Vẽ: header MSB red, filename, timestamp, status, footer.
    Không dùng Pillow — chỉ dùng zlib + struct.
    """
    import zlib
    import struct

    width, height = 800, 500
    bg = (255, 255, 255)
    header_bg = (227, 6, 19)  # MSB red
    text_dark = (17, 24, 39)
    text_gray = (102, 112, 133)
    green = (0, 166, 118)
    line_gray = (229, 231, 235)

    # Create pixel buffer
    pixels = bytearray(width * height * 3)
    for i in range(width * height):
        pixels[i * 3:i * 3 + 3] = bytes(bg)

    def set_pixel(x: int, y: int, color: tuple):
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 3
            pixels[idx:idx + 3] = bytes(color)

    def fill_rect(x0: int, y0: int, x1: int, y1: int, color: tuple):
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                set_pixel(x, y, color)

    def draw_h_line(x0: int, y: int, x1: int, color: tuple, thickness: int = 1):
        for t in range(thickness):
            for x in range(x0, min(width, x1)):
                set_pixel(x, y + t, color)

    def draw_rect(x0: int, y0: int, x1: int, y1: int, color: tuple, thickness: int = 1):
        draw_h_line(x0, y0, x1, color, thickness)
        draw_h_line(x0, y1 - thickness, x1, color, thickness)
        for y in range(y0, y1):
            set_pixel(x0, y, color)
            set_pixel(x1 - 1, y, color)

    def draw_text(x: int, y: int, text: str, color: tuple, scale: int = 2):
        """Draw text using built-in 5x7 font bitmap."""
        _FONT = _get_font_bitmap()
        for i, ch in enumerate(text):
            if ch.upper() not in _FONT:
                ch = ' '
            bitmap = _FONT.get(ch.upper(), _FONT.get(' ', [[0] * 5] * 7))
            for row in range(7):
                for col in range(5):
                    if bitmap[row][col]:
                        for sy in range(scale):
                            for sx in range(scale):
                                px = x + (i * 6 + col) * scale + sx
                                py = y + row * scale + sy
                                set_pixel(px, py, color)

    # Header bar
    fill_rect(0, 0, width, 50, header_bg)
    draw_text(20, 14, "MSB SMARTFORM AI", (255, 255, 255), 2)

    # Title
    draw_text(20, 75, "BAN MEM DA KY SO", text_dark, 3)

    # File info
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    safe_name = filename[:40] + "..." if len(filename) > 40 else filename
    draw_text(20, 130, f"FILE: {safe_name}", text_gray, 2)
    draw_text(20, 155, f"TIME: {ts}", text_gray, 2)
    draw_text(20, 180, "STATUS: DA KY SO THANH CONG", green, 2)

    # Separator line
    draw_h_line(20, 220, width - 20, line_gray, 2)

    # Signature box
    draw_rect(20, 240, 350, 320, line_gray, 1)
    draw_text(30, 250, "CHU KY SO (MOCK)", text_gray, 1)
    draw_text(30, 275, "MOCK-DIGITAL-SIGNATURE", header_bg, 2)

    # Footer
    draw_h_line(20, 350, width - 20, line_gray, 1)
    draw_text(20, 365, "NGAN HANG TMCP HANG HAI VN - MSB", text_gray, 1)
    draw_text(20, 385, "DU LIEU GIA LAP - KHONG DUNG CHO GIAO DICH THAT", text_gray, 1)

    return _encode_png_rgb(bytes(pixels), width, height)


def _get_font_bitmap() -> dict:
    """5x7 bitmap font (uppercase A-Z, 0-9, space, dash, colon, dot, slash, paren)."""
    return {
        ' ': [[0]*5]*7,
        'A': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
        'B': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0]],
        'C': [[0,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,1],[0,1,1,1,0]],
        'D': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0]],
        'E': [[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
        'F': [[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],
        'G': [[0,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,0,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,1]],
        'H': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
        'I': [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1]],
        'J': [[0,0,1,1,1],[0,0,0,1,0],[0,0,0,1,0],[0,0,0,1,0],[1,0,0,1,0],[1,0,0,1,0],[0,1,1,0,0]],
        'K': [[1,0,0,0,1],[1,0,0,1,0],[1,0,1,0,0],[1,1,0,0,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],
        'L': [[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
        'M': [[1,0,0,0,1],[1,1,0,1,1],[1,0,1,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
        'N': [[1,0,0,0,1],[1,1,0,0,1],[1,0,1,0,1],[1,0,0,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
        'O': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        'P': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],
        'Q': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,0,0,1,0],[0,1,1,0,1]],
        'R': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],
        'S': [[0,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[0,1,1,1,0],[0,0,0,0,1],[0,0,0,0,1],[1,1,1,1,0]],
        'T': [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
        'U': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        'V': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0]],
        'W': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,0,1,0,1],[1,1,0,1,1],[1,0,0,0,1]],
        'X': [[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1],[1,0,0,0,1]],
        'Y': [[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
        'Z': [[1,1,1,1,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
        '0': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,1,1],[1,0,1,0,1],[1,1,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        '1': [[0,0,1,0,0],[0,1,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,1,0]],
        '2': [[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,1,1,1,1]],
        '3': [[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        '4': [[0,0,0,1,0],[0,0,1,1,0],[0,1,0,1,0],[1,0,0,1,0],[1,1,1,1,1],[0,0,0,1,0],[0,0,0,1,0]],
        '5': [[1,1,1,1,1],[1,0,0,0,0],[1,1,1,1,0],[0,0,0,0,1],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        '6': [[0,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        '7': [[1,1,1,1,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[0,1,0,0,0],[0,1,0,0,0]],
        '8': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        '9': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,1],[0,0,0,0,1],[0,0,0,0,1],[0,1,1,1,0]],
        '-': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        ':': [[0,0,0,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,0,0,0]],
        '.': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,1,0,0]],
        '/': [[0,0,0,0,1],[0,0,0,1,0],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[0,1,0,0,0],[1,0,0,0,0]],
        '(': [[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[0,1,0,0,0],[0,0,1,0,0]],
        ')': [[0,0,1,0,0],[0,0,0,1,0],[0,0,0,0,1],[0,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0]],
        '_': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1]],
    }
