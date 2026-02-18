import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException

import jwt

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "30"))


def verify_telegram_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Проверка подписи Telegram Login Widget.
    Алгоритм: core.telegram.org/widgets/login#checking-authorization
    """
    if not TG_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="TG_BOT_TOKEN not set")

    # hash приходит от Telegram
    received_hash = data.get("hash")
    if not received_hash:
        raise HTTPException(status_code=400, detail="Missing hash")

    # Собираем data-check-string: сортируем ключи, исключаем hash
    pairs = []
    for k in sorted(data.keys()):
        if k == "hash":
            continue
        v = data[k]
        if v is None:
            continue
        pairs.append(f"{k}={v}")
    data_check_string = "\n".join(pairs)

    # secret_key = sha256(bot_token)
    secret_key = hashlib.sha256(TG_BOT_TOKEN.encode("utf-8")).digest()

    # hmac_sha256(data_check_string, secret_key)
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if calculated_hash != received_hash:
        raise HTTPException(status_code=401, detail="Invalid Telegram hash")

    # anti-replay: можно проверять auth_date (например, не старше суток)
    auth_date = int(data.get("auth_date", "0"))
    if auth_date:
        now = int(datetime.now(tz=timezone.utc).timestamp())
        if now - auth_date > 86400:  # 24h
            raise HTTPException(status_code=401, detail="Auth data is too old")

    return data


def create_jwt(user_id: int) -> str:
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="JWT_SECRET not set")

    exp = datetime.now(tz=timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def get_current_user_id(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
