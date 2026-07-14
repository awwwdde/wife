"""JWT и httpOnly-cookie для клиентской авторизации (SPEC §7)."""

from datetime import UTC, datetime, timedelta

from fastapi import Response
from jose import JWTError, jwt

from app.core.config import settings

COOKIE_NAME = "access_token"


def create_access_token(client_id: int) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": str(client_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_TTL_MIN)).timestamp()),
    }
    return jwt.encode(claims, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Вернуть client_id из токена или None, если токен невалиден."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=settings.JWT_TTL_MIN * 60,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, path="/")
