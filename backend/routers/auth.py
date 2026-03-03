import secrets
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.dependencies import auth_rate_limit, get_user_id_from_token
from auth.jwt import create_jwt
from db import get_db
from models import AuthSessionModel, UserModel, UserProfileModel

router = APIRouter()

SESSION_TTL_SECONDS = 60 * 60 * 24


def cleanup_expired_auth_sessions(db):
    now = int(time.time())
    threshold = now - SESSION_TTL_SECONDS
    db.query(AuthSessionModel).filter(AuthSessionModel.created_at < threshold).delete()


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
def init_telegram_auth(_=Depends(auth_rate_limit), db=Depends(get_db)):
    code = secrets.token_hex(16)
    cleanup_expired_auth_sessions(db)

    session = AuthSessionModel(
        code=code,
        telegram_id=None,
        created_at=int(time.time()),
        used=False,
    )
    db.add(session)
    db.commit()

    return {"code": code}


@router.get("/auth/telegram/check")
def check_telegram_auth(code: str, _=Depends(auth_rate_limit), db=Depends(get_db)):
    cleanup_expired_auth_sessions(db)
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

    session.used = True
    db.query(AuthSessionModel).filter(
        AuthSessionModel.telegram_id == telegram_id,
        AuthSessionModel.id != session.id,
    ).delete()
    db.commit()

    token = create_jwt(user.id)
    return {"status": "ok", "token": token}


@router.get("/me")
def get_me(user_id: int = Depends(get_user_id_from_token), db=Depends(get_db)):
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


@router.put("/me")
def update_me(payload: ProfilePayload, user_id: int = Depends(get_user_id_from_token), db=Depends(get_db)):
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
