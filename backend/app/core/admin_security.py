"""Безопасность админки: пароль (bcrypt), 2FA (TOTP), admin-JWT в отдельной cookie."""

from datetime import UTC, datetime, timedelta

import bcrypt
import pyotp
from fastapi import Response
from jose import JWTError, jwt

from app.core.config import settings

ADMIN_COOKIE_NAME = "admin_token"


# --- Пароль ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


# --- TOTP (2FA) ---
def generate_totp_secret() -> str:
    return pyotp.random_base32()


def totp_provisioning_uri(secret: str, email: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name="askbrows CRM")


def verify_totp(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=1)


# --- Admin JWT ---
def create_admin_token(admin_id: int) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": str(admin_id),
        "role": "admin",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_TTL_MIN)).timestamp()),
    }
    return jwt.encode(claims, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_admin_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("role") != "admin":
            return None
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None


def set_admin_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=token,
        max_age=settings.JWT_TTL_MIN * 60,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        path="/",
    )


def clear_admin_cookie(response: Response) -> None:
    response.delete_cookie(key=ADMIN_COOKIE_NAME, path="/")
