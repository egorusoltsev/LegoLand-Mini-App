from fastapi import APIRouter, Depends, Request
from db import get_db
from models import AuthSessionModel
from utils.telegram import send_telegram_reply

router = APIRouter()


def attach_telegram_to_session(code: str, telegram_id: int, db) -> bool:
    session = (
        db.query(AuthSessionModel)
        .filter(AuthSessionModel.code == code, AuthSessionModel.used == False)
        .first()
    )

    if not session:
        return False

    session.telegram_id = telegram_id
    db.commit()
    return True


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request, db=Depends(get_db)):
    data = await request.json()
    print("[telegram.webhook] update received", {"keys": list(data.keys())})

    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    text = message.get("text", "")
    chat_id = message["chat"].get("id")
    print("[telegram.webhook] message", {"chat_id": chat_id, "text": text[:80]})

    if text.startswith("/start web_"):
        code = text.replace("/start web_", "").strip()
        success = attach_telegram_to_session(code, chat_id, db)

        try:
            if success:
                send_telegram_reply(chat_id, "✅ Вы успешно авторизованы. Вернитесь на сайт.")
            else:
                send_telegram_reply(chat_id, "❌ Сессия устарела.")
        except Exception as exc:
            print("[telegram.webhook] telegram api error", str(exc))

    return {"ok": True}
