import secrets
import time
from fastapi import APIRouter, Depends, HTTPException
from db import SessionLocal
from models import AuthSessionModel, UserModel
from auth.jwt import create_jwt
from auth.dependencies import get_user_id_from_token

router = APIRouter()


@router.post("/auth/telegram/init")
def init_telegram_auth():
    db = SessionLocal()
    code = secrets.token_hex(16)

    session = AuthSessionModel(
        code=code,
        telegram_id=None,
        created_at=int(time.time()),
        used=False,
    )

    db.add(session)
    db.commit()
    db.close()

    return {"code": code}


@router.get("/auth/telegram/check")
def check_telegram_auth(code: str):
    db = SessionLocal()
    try:
        session = db.query(AuthSessionModel).filter(AuthSessionModel.code == code).first()
        if not session:
            return {"status": "not_found"}

        if session.telegram_id is None:
            return {"status": "pending"}

        telegram_id = session.telegram_id

        user = db.query(UserModel).filter(UserModel.telegram_id == telegram_id).first()
        if not user:
            user = UserModel(telegram_id=telegram_id)
            db.add(user)
            db.commit()
            db.refresh(user)

        user_id = user.id

        session.used = True
        db.commit()

        token = create_jwt(user_id)

        return {"status": "ok", "token": token}
    finally:
        db.close()


@router.get("/me")
def get_me(user_id: int = Depends(get_user_id_from_token)):
    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "photo_url": user.photo_url,
            }
        }
    finally:
        db.close()
