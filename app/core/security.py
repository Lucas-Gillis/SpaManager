from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
import jwt

from .config import get_settings

def create_access_token(subject: str, *, data: dict[str, Any]) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(settings.jwt_expiration_minutes))
    to_encode = {"sub": subject, "exp": expire, **data}
    return jwt.encode(payload=to_encode, key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return payload
