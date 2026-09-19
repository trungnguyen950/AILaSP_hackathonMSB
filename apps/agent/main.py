"""MSB SmartForm AI — Agent entrypoint (GreenNode AgentBase Custom Agent).

Deploy target: GreenNode AgentBase Runtime (1 container, port 8080, GET /health).
The /invocations endpoint dispatches by `action` (many logical REST paths):
  - chat           : send a message through the 8-step FSM
  - list_forms     : list active Form Registry
  - get_form       : get a form template by code
  - fill_form      : fill a form with provided values
  - validate_form  : validate a filled form
  - render_form    : render filled form (HTML preview)
  - run_qc         : run 8 quality checks on a filled form
  - soan_ho_so     : trigger "SOẠN HỒ SƠ" (render filled form)
  - list_personas  : list 5 demo customers
  - get_session    : get session state
  - reset_session  : reset session
"""
from __future__ import annotations

import base64
import os
from datetime import datetime

from dotenv import load_dotenv

from greennode_agentbase import GreenNodeAgentBaseApp, PingStatus, RequestContext

from src import agent, form_engine, qc, sign_engine, file_engine
from src.demo_data import DEMO_CUSTOMERS
from src.kb import KB

load_dotenv()

app = GreenNodeAgentBaseApp()


@app.entrypoint
def handler(payload: dict, context: RequestContext) -> dict:
    """Main agent entrypoint — dispatch by action (many logical paths)."""
    action = payload.get("action", "chat")
    session_id = context.session_id or payload.get("session_id", "default")
    ts = datetime.now().isoformat()

    # --- Form Registry paths ---
    if action == "list_forms":
        return {"status": "success", "forms": [m.model_dump() for m in KB.list_active()], "timestamp": ts}

    if action == "get_form":
        code = payload.get("code", "")
        tpl = KB.get(code)
        if not tpl:
            return {"status": "error", "error": "FORM_NOT_FOUND", "message": f"Không tìm thấy mẫu {code}"}
        return {"status": "success", "form": tpl.model_dump(), "timestamp": ts}

    # --- Form engine paths ---
    if action == "fill_form":
        code = payload.get("code", "")
        tpl = KB.get(code)
        if not tpl:
            return {"status": "error", "error": "FORM_NOT_FOUND"}
        values = payload.get("values", {})
        filled, missing = form_engine.fill(tpl, values)
        return {"status": "success", "filled": filled, "missing": missing, "timestamp": ts}

    if action == "validate_form":
        code = payload.get("code", "")
        tpl = KB.get(code)
        if not tpl:
            return {"status": "error", "error": "FORM_NOT_FOUND"}
        filled = payload.get("filled", {})
        violations = form_engine.validate(tpl, filled)
        return {"status": "success", "valid": not violations, "violations": violations, "timestamp": ts}

    if action == "render_form":
        code = payload.get("code", "")
        tpl = KB.get(code)
        if not tpl:
            return {"status": "error", "error": "FORM_NOT_FOUND"}
        filled = payload.get("filled", {})
        return {"status": "success", "html": form_engine.render_html(tpl, filled), "timestamp": ts}

    if action == "run_qc":
        code = payload.get("code", "")
        tpl = KB.get(code)
        if not tpl:
            return {"status": "error", "error": "FORM_NOT_FOUND"}
        filled = payload.get("filled", {})
        missing = payload.get("missing", [])
        result = qc.run_checks(tpl, filled, missing, None)
        return {"status": "success", "qc": result.model_dump(), "timestamp": ts}

    # --- Persona paths ---
    if action == "list_personas":
        return {"status": "success", "personas": [c.model_dump() for c in DEMO_CUSTOMERS], "timestamp": ts}

    # --- Session paths ---
    if action == "get_session":
        state = agent.get_state(session_id)
        return {"status": "success", "session_id": session_id, "state": state.model_dump() if state else None, "timestamp": ts}

    if action == "reset_session":
        agent.reset_session(session_id)
        return {"status": "success", "message": "Session reset", "session_id": session_id, "timestamp": ts}

    # --- Soạn hồ sơ ---
    if action == "soan_ho_so":
        result = agent.run(session_id, "SOẠN HỒ SƠ")
        code = (result.get("selected_form") or {}).get("code")
        if code and KB.get(code) and result.get("filled"):
            result["preview_html"] = form_engine.render_html(KB.get(code), result["filled"])
        return result

    # --- Export Vintage PDF (từ form đã điền trong session) ---
    if action == "export_vintage_pdf":
        code = payload.get("code", "")
        tpl = KB.get(code) if code else None
        if not tpl:
            return {"status": "error", "error": "FORM_NOT_FOUND", "message": f"Không tìm thấy mẫu {code}"}

        state = agent.get_state(session_id)
        filled = state.filled if state else payload.get("filled", {})
        signatories = [s.model_dump() for s in tpl.signatories]

        if not filled:
            return {"status": "error", "error": "NO_DATA", "message": "Chưa có dữ liệu đã điền. Hãy soạn hồ sơ trước."}

        # Sửa font tiếng Việt cho tất cả giá trị
        from src.pdf_fonts import fix_vietnamese
        clean_filled = {k: fix_vietnamese(str(v)) for k, v in filled.items()}

        doc = {
            "title": fix_vietnamese(tpl.meta.name),
            "subtitle": f"Nhóm: {tpl.meta.business_group} · Phiên bản: {tpl.meta.version}",
            "form_code": tpl.meta.code,
            "form_name": tpl.meta.name,
            "org_name": "NGÂN HÀNG TMCP HÀNG HẢI VIỆT NAM — MSB",
            "fields": {f.label: clean_filled.get(f.key, "") for f in tpl.fields
                       if not form_engine.is_secret(f.key) and clean_filled.get(f.key, "")
                       and clean_filled.get(f.key, "") != form_engine.MISSING},
            "signatories": signatories,
            "accompanying_docs": tpl.meta.accompanying_docs,
            "notes": [
                "Dữ liệu giả lập — không dùng cho giao dịch thật.",
                f"Hồ sơ lập bởi MSB SmartForm AI · {datetime.now().strftime('%d/%m/%Y %H:%M')}.",
            ],
            "footer_code": f"{tpl.meta.code} · v{tpl.meta.version}",
            "watermark": "MSB",
        }

        from src.vintage_pdf import generate_vintage_pdf
        pdf_bytes = generate_vintage_pdf(doc)
        pdf_b64 = sign_engine.pdf_to_base64(pdf_bytes)

        return {
            "status": "success",
            "filename": f"{tpl.meta.code}_vintage.pdf",
            "pdf_base64": pdf_b64,
            "pdf_size": len(pdf_bytes),
            "timestamp": ts,
        }

    # --- Export Vintage PDF cho template rỗng (từ trang danh sách biểu mẫu) ---
    if action == "export_form_pdf":
        code = payload.get("code", "")
        tpl = KB.get(code) if code else None
        if not tpl:
            return {"status": "error", "error": "FORM_NOT_FOUND", "message": f"Không tìm thấy mẫu {code}"}

        from src.pdf_fonts import fix_vietnamese
        signatories = [s.model_dump() for s in tpl.signatories]

        doc = {
            "title": fix_vietnamese(tpl.meta.name),
            "subtitle": f"Nhóm: {tpl.meta.business_group} · Phiên bản: {tpl.meta.version} · Hiệu lực: {tpl.meta.effective_date}",
            "form_code": tpl.meta.code,
            "form_name": tpl.meta.name,
            "org_name": "NGÂN HÀNG TMCP HÀNG HẢI VIỆT NAM — MSB",
            "fields": {f.label: ("[bắt buộc]" if f.required else "[tùy chọn]") for f in tpl.fields
                       if not form_engine.is_secret(f.key)},
            "signatories": signatories,
            "accompanying_docs": tpl.meta.accompanying_docs,
            "notes": [
                "Đây là mẫu biểu mẫu trống (template). Dùng AI Fill để điền tự động.",
                "Dữ liệu giả lập — không dùng cho giao dịch thật.",
            ],
            "footer_code": f"{tpl.meta.code} · v{tpl.meta.version}",
            "watermark": "MSB",
        }

        from src.vintage_pdf import generate_vintage_pdf
        pdf_bytes = generate_vintage_pdf(doc)
        pdf_b64 = sign_engine.pdf_to_base64(pdf_bytes)

        return {
            "status": "success",
            "filename": f"{tpl.meta.code}_template.pdf",
            "pdf_base64": pdf_b64,
            "pdf_size": len(pdf_bytes),
            "timestamp": ts,
        }

    # --- Mock Digital Signature ---
    if action == "mock_sign_document":
        import uuid as _uuid

        document_id = payload.get("document_id", f"DOC-{_uuid.uuid4().hex[:8]}")
        signature_image = payload.get("signature_image", "")
        mock_cert = payload.get("mock_cert", {})
        code = payload.get("code", "")
        tpl = KB.get(code) if code else None

        form_code = tpl.meta.code if tpl else (code or "UNKNOWN")
        form_name = tpl.meta.name if tpl else "Untitled Form"

        state = agent.get_state(session_id)
        filled = state.filled if state else (payload.get("filled", {}))
        signatories = [s.model_dump() for s in tpl.signatories] if tpl else []

        if not signature_image:
            return {"status": "error", "error": "NO_SIGNATURE", "message": "Vui lòng vẽ chữ ký."}

        pdf_bytes, signed_hash, webhook_payload = sign_engine.generate_signed_pdf(
            document_id=document_id,
            form_code=form_code,
            form_name=form_name,
            filled=filled,
            signatories=signatories,
            signature_image_b64=signature_image,
            mock_cert=mock_cert,
        )
        pdf_b64 = sign_engine.pdf_to_base64(pdf_bytes)
        ack = sign_engine.notify_ai_agent(webhook_payload, session_id)

        return {
            "status": "success",
            "document_id": document_id,
            "signed_hash": signed_hash,
            "signed_pdf_base64": pdf_b64,
            "webhook": webhook_payload,
            "agent_ack": ack,
            "timestamp": ts,
        }

    if action == "sign_notification":
        webhook_payload = payload.get("webhook_payload", {})
        ack = sign_engine.notify_ai_agent(webhook_payload, session_id)
        return {"status": "success", "ack": ack, "timestamp": ts}

    # --- File Upload + AI Check ---
    if action == "upload_and_check":
        filename = payload.get("filename", "")
        file_content_b64 = payload.get("file_content", "")
        code = payload.get("code", "")
        tpl = KB.get(code) if code else None

        if not file_content_b64:
            return {"status": "error", "error": "NO_FILE", "message": "Vui lòng upload file."}

        raw_b64 = file_content_b64.split(",", 1)[-1] if "," in file_content_b64 else file_content_b64
        try:
            content = base64.b64decode(raw_b64)
        except Exception:
            return {"status": "error", "error": "INVALID_BASE64", "message": "File content không hợp lệ."}

        is_valid, file_type, val_msg = file_engine.validate_file(filename, content)
        if not is_valid:
            return {"status": "error", "error": "INVALID_FILE", "message": val_msg}

        form_code = tpl.meta.code if tpl else code
        form_name = tpl.meta.name if tpl else "Unknown"

        from src.agent import _LLM
        check_result = file_engine.check_authenticity(filename, content, form_code, form_name, _LLM)

        return {
            "status": "success",
            "filename": filename,
            "file_type": file_type,
            "file_size": len(content),
            "authentic": check_result["is_authentic"],
            "score": check_result["score"],
            "checks": check_result["checks"],
            "llm_verdict": check_result.get("llm_verdict"),
            "text_preview": check_result["extracted_text_preview"],
            "timestamp": ts,
        }

    # --- Sign Uploaded File ---
    if action == "sign_uploaded_file":
        import uuid as _uuid

        filename = payload.get("filename", "")
        file_content_b64 = payload.get("file_content", "")
        signature_image = payload.get("signature_image", "")
        mock_cert = payload.get("mock_cert", {})
        code = payload.get("code", "")
        tpl = KB.get(code) if code else None
        form_code = tpl.meta.code if tpl else (code or "UNKNOWN")

        if not file_content_b64 or not signature_image:
            return {"status": "error", "error": "MISSING_DATA", "message": "Thiếu file hoặc chữ ký."}

        raw_b64 = file_content_b64.split(",", 1)[-1] if "," in file_content_b64 else file_content_b64
        try:
            content = base64.b64decode(raw_b64)
        except Exception:
            return {"status": "error", "error": "INVALID_BASE64", "message": "File content không hợp lệ."}

        is_valid, file_type, val_msg = file_engine.validate_file(filename, content)
        if not is_valid:
            return {"status": "error", "error": "INVALID_FILE", "message": val_msg}

        signed_bytes, signed_hash, webhook_payload = file_engine.sign_file(
            filename=filename,
            content=content,
            signature_image_b64=signature_image,
            mock_cert=mock_cert,
            form_code=form_code,
        )

        ext = file_type.lstrip(".")
        mime = "text/plain" if ext == "txt" else "application/pdf"
        signed_b64 = file_engine.file_to_base64(signed_bytes, mime)
        ack = sign_engine.notify_ai_agent(webhook_payload, session_id)

        base_name = filename.rsplit(".", 1)[0]
        signed_filename = f"{base_name}_signed.{ext}"

        # Sinh thêm bản PDF vintage (cho phép tải PDF bên cạnh bản text/pdf gốc)
        vintage_pdf_b64 = None
        vintage_pdf_filename = None
        try:
            if ext == "txt":
                pdf_bytes = file_engine.txt_to_vintage_pdf_bytes(
                    signed_bytes, form_code=form_code,
                    title=form_code or "Văn bản đã ký",
                )
            else:
                # .pdf đã ký → dùng luôn signed_bytes
                pdf_bytes = signed_bytes
            vintage_pdf_b64 = file_engine.file_to_base64(pdf_bytes, "application/pdf")
            vintage_pdf_filename = f"{base_name}_signed.pdf"
        except Exception as e:
            import logging as _logging
            _logging.getLogger("main").warning("vintage PDF fallback failed: %s", e)

        return {
            "status": "success",
            "signed_filename": signed_filename,
            "signed_hash": signed_hash,
            "signed_file_base64": signed_b64,
            "file_type": file_type,
            "vintage_pdf_base64": vintage_pdf_b64,
            "vintage_pdf_filename": vintage_pdf_filename,
            "webhook": webhook_payload,
            "agent_ack": ack,
            "timestamp": ts,
        }

    # --- Zalo Bot: getMe (kiểm tra token) ---
    if action == "zalo_get_me":
        from src.zalo_bot import get_bot_token, get_me
        token = get_bot_token()
        if not token:
            return {"status": "error", "error": "NO_ZALO_TOKEN", "message": "Thiếu ZALO_BOT_TOKEN env var hoặc AgentBase auth provider 'zalo-bot-token'."}
        return {"status": "success", "bot": get_me(token), "timestamp": ts}

    # --- Zalo Bot: setWebhook ---
    if action == "zalo_set_webhook":
        from src.zalo_bot import get_bot_token, set_webhook
        token = get_bot_token()
        if not token:
            return {"status": "error", "error": "NO_ZALO_TOKEN", "message": "Thiếu ZALO_BOT_TOKEN."}
        webhook_url = payload.get("url", "")
        secret = payload.get("secret_token") or os.environ.get("ZALO_WEBHOOK_SECRET", "")
        if not webhook_url:
            return {"status": "error", "error": "NO_URL", "message": "Truyền url webhook (HTTPS, public)."}
        if not secret:
            return {"status": "error", "error": "NO_SECRET", "message": "Truyền secret_token hoặc cấu hình ZALO_WEBHOOK_SECRET."}
        return {"status": "success", "result": set_webhook(token, webhook_url, secret), "timestamp": ts}

    # --- Zalo Bot: getWebhookInfo ---
    if action == "zalo_get_webhook_info":
        from src.zalo_bot import get_bot_token, get_webhook_info
        token = get_bot_token()
        if not token:
            return {"status": "error", "error": "NO_ZALO_TOKEN", "message": "Thiếu ZALO_BOT_TOKEN."}
        return {"status": "success", "result": get_webhook_info(token), "timestamp": ts}

    # --- Zalo Bot: sendMessage (gửi text tuỳ ý) ---
    if action == "zalo_send_message":
        from src.zalo_bot import get_bot_token, send_message, resolve_chat_id
        token = get_bot_token()
        if not token:
            return {"status": "error", "error": "NO_ZALO_TOKEN", "message": "Thiếu ZALO_BOT_TOKEN."}
        chat_id = resolve_chat_id(payload.get("chat_id"), getattr(context, "user_id", None))
        if not chat_id:
            return {"status": "error", "error": "NO_CHAT_ID", "message": "Truyền chat_id hoặc cấu hình ZALO_CHAT_ID."}
        text = payload.get("text", "")
        if not text:
            return {"status": "error", "error": "NO_TEXT", "message": "Thiếu nội dung text."}
        return {"status": "success", "result": send_message(token, chat_id, text, parse_mode=payload.get("parse_mode", "markdown")), "timestamp": ts}

    # --- Zalo Bot: list known chat_ids (từ webhook) ---
    if action == "zalo_list_chats":
        from src.zalo_bot import get_known_chat_ids
        return {"status": "success", "chats": get_known_chat_ids(), "timestamp": ts}

    # --- Zalo Bot: gửi thông báo + PDF đã ký cho khách hàng ---
    if action == "send_zalo_notification":
        from src.zalo_bot import (
            get_bot_token, resolve_chat_id, send_notification_to_customer, build_notification_text,
        )

        # Ưu tiên PDF vintage (bản PDF đẹp), fallback về signed_file_base64 gốc
        pdf_b64 = payload.get("pdf_base64") or payload.get("vintage_pdf_base64") or ""
        filename = payload.get("filename") or payload.get("vintage_pdf_filename") or "signed.pdf"
        document_id = payload.get("document_id", "")
        form_code = payload.get("form_code", "")
        signed_hash = payload.get("signed_hash", "")
        signed_by = payload.get("signed_by", "")
        chat_id_override = payload.get("chat_id") or payload.get("zalo_user_id")

        if not pdf_b64:
            return {"status": "error", "error": "NO_PDF", "message": "Thiếu PDF base64 để gửi."}

        # Decode base64 (hỗ trợ data URL)
        raw_b64 = pdf_b64.split(",", 1)[-1] if "," in pdf_b64 else pdf_b64
        try:
            pdf_bytes = base64.b64decode(raw_b64)
        except Exception:
            return {"status": "error", "error": "INVALID_BASE64", "message": "PDF content không hợp lệ."}

        # Lấy bot token
        token = get_bot_token()
        if not token:
            return {
                "status": "error",
                "error": "NO_ZALO_TOKEN",
                "message": "Thiếu Zalo Bot token. Cấu hình ZALO_BOT_TOKEN env var hoặc AgentBase auth provider 'zalo-bot-token'.",
            }

        # Xác định chat_id người nhận
        chat_id = resolve_chat_id(chat_id_override, getattr(context, "user_id", None))
        if not chat_id:
            return {
                "status": "error",
                "error": "NO_CHAT_ID",
                "message": "Không tìm thấy Zalo chat_id. Truyền chat_id, cấu hình ZALO_CHAT_ID, hoặc nhắn cho bot trước để agent lưu chat_id.",
            }

        notification_text = build_notification_text(document_id, form_code, signed_hash, signed_by, filename)
        zalo_result = send_notification_to_customer(token, chat_id, notification_text, pdf_bytes, filename)

        return {
            "status": "success" if zalo_result.get("success") else "error",
            "zalo": zalo_result,
            "message": "Đã gửi thông báo qua Zalo Bot thành công." if zalo_result.get("success") else (zalo_result.get("error") or "Gửi Zalo thất bại."),
            "timestamp": ts,
        }

    # --- Chat (default) ---
    message = payload.get("message", "")
    if not message:
        return {"status": "error", "error": "EMPTY_MESSAGE", "message": "Vui lòng nhập yêu cầu."}
    return agent.run(session_id, message)


@app.ping
def health_check() -> PingStatus:
    """GET /health — AgentBase contract."""
    return PingStatus.HEALTHY


# --- Serve the bundled frontend (static export) at "/" ---
# Mounted AFTER /health, /invocations, and /zalo-webhook so those API routes take priority.
from pathlib import Path

# --- Zalo Bot Webhook endpoint ---
# Zalo gửi POST tới URL này khi có user nhắn cho bot.
# Header X-Bot-Api-Secret-Token dùng để xác thực.
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse as StarletteJSONResponse
from starlette.routing import Route as StarletteRoute

ZALO_WEBHOOK_SECRET = os.environ.get("ZALO_WEBHOOK_SECRET", "")


async def _zalo_webhook_handler(request: StarletteRequest):
    """Receive Zalo Bot webhook events and auto-respond to user messages."""
    import logging as _lg

    _log = _lg.getLogger("zalo_webhook")

    # 1. Validate secret token
    secret = request.headers.get("x-bot-api-secret-token", "")
    if ZALO_WEBHOOK_SECRET and secret != ZALO_WEBHOOK_SECRET:
        _log.warning("Zalo webhook: secret token mismatch. Got=%s Expected=%s", secret[:8], ZALO_WEBHOOK_SECRET[:8])
        return StarletteJSONResponse({"ok": False, "error": "unauthorized"}, status_code=403)

    # 2. Parse event
    try:
        body = await request.json()
    except Exception as e:
        _log.warning("Zalo webhook: invalid JSON: %s", e)
        return StarletteJSONResponse({"ok": False, "error": "invalid_json"}, status_code=400)

    from src.zalo_bot import handle_webhook_event, get_bot_token, send_message

    parsed = handle_webhook_event(body)
    _log.info("Zalo webhook event: %s", parsed)

    respond_result = None

    # 3. Auto-respond to text messages
    if parsed.get("event_name") == "message.text.received" and parsed.get("chat_id"):
        chat_id = parsed["chat_id"]
        text = (parsed.get("text") or "").strip().lower()
        from_name = parsed.get("from_name", "quý khách")

        if text in ("/start", "start", "hi", "hello", "chào", "chao", ""):
            reply = (
                f"# Chào {from_name}! 👋\n\n"
                f"Đây là **Bot AI SmartForm** — trợ lý ký số MSB.\n\n"
                f"**Chat ID của bạn:**\n`{chat_id}`\n\n"
                f"**Hướng dẫn:**\n"
                f"1. Copy chat ID ở trên\n"
                f"2. Ký PDF trên web MSB SmartForm AI\n"
                f"3. Dán chat ID vào ô \"Zalo chat_id\" → bấm **Gửi Zalo Bot**\n"
                f"4. Bot sẽ gửi thông báo ký thành công tại đây\n\n"
                f"Gõ `status` để kiểm tra trạng thái hồ sơ."
            )
        elif text == "status":
            reply = (
                f"**Trạng thái:** Chưa có hồ sơ nào được ký.\n\n"
                f"Chat ID của bạn: `{chat_id}`\n"
                f"Ký PDF trên web → dán chat ID vào ô Zalo → bấm Gửi."
            )
        else:
            reply = (
                f"Đã nhận: \"{parsed.get('text', '')}\"\n\n"
                f"**Chat ID của bạn:** `{chat_id}`\n\n"
                f"Gõ `/start` để xem hướng dẫn."
            )

        # Gửi phản hồi + ghi kết quả
        try:
            token = get_bot_token()
            if token:
                respond_result = send_message(token, chat_id, reply, parse_mode="markdown")
                _log.info("Zalo auto-respond → chat_id=%s result=%s", chat_id, respond_result)
            else:
                respond_result = {"ok": False, "error": "NO_BOT_TOKEN"}
                _log.error("Zalo webhook: no bot token available for auto-respond.")
        except Exception as e:
            respond_result = {"ok": False, "error": str(e)}
            _log.error("Zalo webhook: auto-respond failed: %s", e)

    return StarletteJSONResponse({"ok": True, "parsed": parsed, "respond": respond_result})


# Insert webhook route BEFORE static mount so it takes priority
app.router.routes.insert(0, StarletteRoute("/zalo-webhook", _zalo_webhook_handler, methods=["POST"]))


_static_dir = Path(os.environ.get("STATIC_DIR", "static"))
if _static_dir.exists():
    from starlette.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="static")


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
