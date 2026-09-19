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
    """Gửi thông báo + PDF (best effort) cho khách hàng qua Zalo Bot.

    Workflow:
      1. Gửi text notification (markdown) — luôn thực hiện
      2. (best effort) Gửi PDF qua sendPhoto multipart — có thể fail (không phải ảnh)

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

    # 2. Best effort: gửi PDF qua sendPhoto (multipart)
    if pdf_bytes and pdf_filename:
        try:
            photo_res = send_photo_file(
                token, chat_id, pdf_bytes, pdf_filename,
                caption=f"📄 {pdf_filename} — bản mềm đã ký",
            )
            result["steps"]["photo"] = photo_res
            if photo_res.get("ok"):
                result["steps"]["photo_message_id"] = photo_res.get("result", {}).get("message_id")
            else:
                # PDF không phải ảnh → ghi note nhưng vẫn success (text đã gửi)
                result["steps"]["photo_note"] = f"sendPhoto không chấp nhận PDF: {photo_res.get('description', '')}"
        except Exception as e:
            logger.warning("Zalo sendPhoto (PDF) failed (expected): %s", e)
            result["steps"]["photo_error"] = str(e)

    # Text đã gửi thành công → overall success
    result["success"] = True
    return result
