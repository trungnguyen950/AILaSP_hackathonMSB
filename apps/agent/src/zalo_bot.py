"""Zalo Bot Platform integration — gửi tin nhắn + ảnh/preview PDF cho khách hàng.

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
Giải pháp: gửi text notification (markdown) + thử sendPhoto với PDF bytes (best effort).
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
      2. Chuyển PDF → ảnh PNG (Pillow) → gửi qua sendPhoto

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

    # 2. Convert PDF → PNG → send via sendPhoto
    if pdf_bytes:
        try:
            png_bytes = _pdf_first_page_to_png(pdf_bytes)
            if not png_bytes:
                # Fallback: tạo preview image từ text
                png_bytes = _create_preview_image(pdf_filename or "document.pdf")

            if png_bytes:
                base_name = (pdf_filename or "preview").rsplit(".", 1)[0]
                photo_res = send_photo_file(
                    token, chat_id, png_bytes,
                    filename=f"{base_name}.png",
                    caption=f"📄 {pdf_filename or 'Bản mềm đã ký'} — preview",
                    mime="image/png",
                )
                result["steps"]["photo"] = photo_res
                if photo_res.get("ok"):
                    result["steps"]["photo_message_id"] = photo_res.get("result", {}).get("message_id")
                else:
                    result["steps"]["photo_note"] = f"sendPhoto failed: {photo_res.get('description', '')}"
            else:
                result["steps"]["photo_note"] = "Không tạo được ảnh preview"
        except Exception as e:
            logger.warning("Zalo sendPhoto failed: %s", e)
            result["steps"]["photo_error"] = str(e)

    # Text đã gửi thành công → overall success
    result["success"] = True
    return result


def _pdf_first_page_to_png(pdf_bytes: bytes) -> bytes | None:
    """Extract first page of PDF as PNG using pypdf + pure Python PNG encoder.

    No Pillow, no external image library — only stdlib (zlib + struct).
    Tries to extract embedded images from the first page.
    Returns PNG bytes or None if no images found.
    """
    try:
        import pypdf

        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        if not reader.pages:
            return None

        page = reader.pages[0]
        resources = page.get("/Resources", {})
        if "/XObject" not in resources:
            return None

        x_objects = resources["/XObject"].get_object()
        for obj_name in x_objects:
            obj = x_objects[obj_name]
            if obj.get("/Subtype") != "/Image":
                continue

            width = int(obj.get("/Width", 800))
            height = int(obj.get("/Height", 600))
            data = obj.get_data()
            cs = str(obj.get("/ColorSpace", "/DeviceRGB"))

            # Convert to RGB bytes
            if "Gray" in cs:
                rgb = bytearray()
                for b in data[:width * height]:
                    rgb.extend([b, b, b])
                raw = bytes(rgb)
            elif "RGB" in cs:
                raw = data[:width * height * 3]
            else:
                raw = data[:width * height * 3]
                if len(raw) < width * height * 3:
                    raw = raw + b'\xff' * (width * height * 3 - len(raw))

            # Resize to max 1200px wide (nearest-neighbor)
            if width > 1200:
                new_w = 1200
                new_h = int(height * (1200 / width))
                raw = _resize_nn(raw, width, height, new_w, new_h)
                width, height = new_w, new_h

            png = _encode_png(raw, width, height)
            if png:
                logger.info("PDF → PNG (pypdf extract): %dx%d", width, height)
                return png

    except Exception as e:
        logger.debug("PDF image extraction failed: %s", e)

    return None


def _encode_png(raw_rgb: bytes, width: int, height: int) -> bytes | None:
    """Pure Python PNG encoder — stdlib only (zlib + struct). No Pillow."""
    import zlib
    import struct

    if width <= 0 or height <= 0:
        return None
    if len(raw_rgb) < width * height * 3:
        raw_rgb = raw_rgb + b'\xff' * (width * height * 3 - len(raw_rgb))

    def chunk(ctype: bytes, data: bytes) -> bytes:
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))

    # Add filter byte (0=None) per scanline
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(0)
        scanlines.extend(raw_rgb[y * width * 3:(y + 1) * width * 3])
    idat = chunk(b'IDAT', zlib.compress(bytes(scanlines), 9))
    iend = chunk(b'IEND', b'')

    return sig + ihdr + idat + iend


def _resize_nn(raw: bytes, ow: int, oh: int, nw: int, nh: int) -> bytes:
    """Nearest-neighbor resize for RGB data."""
    out = bytearray(nw * nh * 3)
    for y in range(nh):
        sy = min(int(y * oh / nh), oh - 1)
        for x in range(nw):
            sx = min(int(x * ow / nw), ow - 1)
            si = (sy * ow + sx) * 3
            di = (y * nw + x) * 3
            out[di:di + 3] = raw[si:si + 3]
    return bytes(out)


# --- 5x7 bitmap font for text preview ---
_FONT_5x7: dict[str, list] = {
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
    '-': [[0]*5,[0]*5,[0]*5,[1,1,1,1,1],[0]*5,[0]*5,[0]*5],
    ':': [[0]*5,[0,0,1,0,0],[0,0,1,0,0],[0]*5,[0,0,1,0,0],[0,0,1,0,0],[0]*5],
    '.': [[0]*5,[0]*5,[0]*5,[0]*5,[0]*5,[0,0,1,0,0],[0,0,1,0,0]],
    '/': [[0,0,0,0,1],[0,0,0,1,0],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[0,1,0,0,0],[1,0,0,0,0]],
    '(': [[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[0,1,0,0,0],[0,0,1,0,0]],
    ')': [[0,0,1,0,0],[0,0,0,1,0],[0,0,0,0,1],[0,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0]],
    '_': [[0]*5,[0]*5,[0]*5,[0]*5,[0]*5,[0]*5,[1,1,1,1,1]],
}


def _create_preview_image(filename: str) -> bytes:
    """Create text-based PNG preview using pure Python (zlib+struct). No Pillow."""
    width, height = 800, 480
    bg = (255, 255, 255)
    red = (227, 6, 19)
    dark = (17, 24, 39)
    gray = (102, 112, 133)
    green = (0, 166, 118)
    lgray = (229, 231, 235)

    px = bytearray(width * height * 3)
    for i in range(width * height):
        px[i * 3:i * 3 + 3] = bytes(bg)

    def setp(x: int, y: int, c: tuple):
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 3
            px[idx:idx + 3] = bytes(c)

    def fill(x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                setp(x, y, c)

    def hline(x0, y, x1, c, t=1):
        for ty in range(t):
            for x in range(x0, min(width, x1)):
                setp(x, y + ty, c)

    def rect(x0, y0, x1, y1, c, t=1):
        hline(x0, y0, x1, c, t)
        hline(x0, y1 - t, x1, c, t)
        for y in range(y0, y1):
            setp(x0, y, c)
            setp(x1 - 1, y, c)

    def text(x, y, s, c, scale=2):
        for i, ch in enumerate(s):
            bm = _FONT_5x7.get(ch.upper(), _FONT_5x7.get(' '))
            for r in range(7):
                for col in range(5):
                    if bm[r][col]:
                        for sy in range(scale):
                            for sx in range(scale):
                                setp(x + (i * 6 + col) * scale + sx, y + r * scale + sy, c)

    # Draw
    fill(0, 0, width, 45, red)
    text(20, 12, "MSB SMARTFORM AI", (255, 255, 255), 2)

    text(20, 65, "BAN MEM DA KY SO", dark, 3)
    safe = filename[:40] + "..." if len(filename) > 40 else filename
    text(20, 115, f"FILE: {safe}", gray, 2)
    text(20, 140, f"TIME: {datetime.now().strftime('%d/%m/%Y %H:%M')}", gray, 2)
    text(20, 165, "STATUS: DA KY SO THANH CONG", green, 2)

    hline(20, 205, width - 20, lgray, 2)

    rect(20, 225, 350, 295, lgray, 1)
    text(30, 235, "CHU KY SO (MOCK)", gray, 1)
    text(30, 258, "MOCK-DIGITAL-SIGNATURE", red, 2)

    hline(20, 325, width - 20, lgray, 1)
    text(20, 340, "NGAN HANG TMCP HANG HAI VN - MSB", gray, 1)
    text(20, 360, "DU LIEU GIA LAP - KHONG DUNG CHO GIAO DICH THAT", gray, 1)

    return _encode_png(bytes(px), width, height)
