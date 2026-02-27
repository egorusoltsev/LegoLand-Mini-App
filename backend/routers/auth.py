import secrets
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from db import SessionLocal
from models import AuthSessionModel, UserModel, UserProfileModel
from auth.jwt import create_jwt
from auth.dependencies import get_user_id_from_token

router = APIRouter()


class ProfilePayload(BaseModel):
    full_name: str
    phone: str


def get_profile_dict(profile):
    if not profile:
        return {"full_name": "", "phone": ""}
    return {
        "full_name": profile.full_name or "",
        "phone": profile.phone or "",
    }


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
    print("[auth.init] code created", {"code_prefix": code[:6]})

    return {"code": code}


@router.get("/auth/telegram/check")
def check_telegram_auth(code: str):
    db = SessionLocal()
    try:
        print("[auth.check] incoming", {"code_prefix": code[:6]})
        session = db.query(AuthSessionModel).filter(AuthSessionModel.code == code).first()
        if not session:
            print("[auth.check] session not found", {"code_prefix": code[:6]})
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

        session.used = True
        db.commit()

        token = create_jwt(user.id)

        return {"status": "ok", "token": token}
    except Exception as exc:
        print("[auth.check] error", str(exc))
        raise
    finally:
        db.close()


@router.get("/me")
def get_me(user_id: int = Depends(get_user_id_from_token)):
    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == user_id).first()
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
            },
            "profile": get_profile_dict(profile),
        }
    finally:
        db.close()


@router.put("/me")
def update_me(payload: ProfilePayload, user_id: int = Depends(get_user_id_from_token)):
    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == user_id).first()
        if not profile:
            profile = UserProfileModel(user_id=user_id)
            db.add(profile)

        profile.full_name = payload.full_name.strip()
        profile.phone = payload.phone.strip()
        db.commit()
        db.refresh(profile)
        return {"status": "ok", "profile": get_profile_dict(profile)}
    finally:
        db.close()
