from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.jwt import get_current_user_id

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_user_id_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return get_current_user_id(credentials)


def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(optional_security),
):
    if not credentials:
        return None
    return get_current_user_id(credentials)


def check_admin_key(x_admin_key: str = Header(None)):
    # ADMIN_KEY читаем внутри, чтобы env точно был доступен
    import os
    admin_key = os.getenv("ADMIN_KEY")
    if x_admin_key != admin_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
