import hmac
import os
import time
from collections import defaultdict, deque

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.jwt import get_current_user_id

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

RATE_BUCKETS = defaultdict(deque)


def _check_rate_limit(scope: str, key: str, limit: int, period_seconds: int):
    now = time.time()
    bucket_key = scope + ":" + key
    bucket = RATE_BUCKETS[bucket_key]
    while bucket and (now - bucket[0]) > period_seconds:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests")
    bucket.append(now)


def rate_limit(scope: str, limit: int, period_seconds: int):
    def dependency(request: Request):
        client_host = "unknown"
        if request and request.client and request.client.host:
            client_host = request.client.host
        _check_rate_limit(scope, client_host, limit, period_seconds)

    return dependency


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


def check_admin_key(
    request: Request,
    x_admin_key: str = Header(None),
    _: None = Depends(rate_limit("admin", 30, 60)),
):
    admin_key = os.getenv("ADMIN_KEY", "")
    if not admin_key.strip():
        raise HTTPException(status_code=500, detail="ADMIN_KEY is not configured")
    if not x_admin_key or not hmac.compare_digest(x_admin_key, admin_key):
        raise HTTPException(status_code=401, detail="Unauthorized")


def auth_rate_limit(_: None = Depends(rate_limit("auth", 20, 60))):
    return True


def order_rate_limit(_: None = Depends(rate_limit("order", 15, 60))):
    return True
