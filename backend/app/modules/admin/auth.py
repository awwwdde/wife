"""Вход в CRM: логин + пароль + 2FA (TOTP)."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_security import (
    clear_admin_cookie,
    create_admin_token,
    set_admin_cookie,
    verify_password,
    verify_totp,
)
from app.database.session import get_session
from app.models.admin import AdminUser
from app.modules.admin.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin-auth"])


class LoginRequest(BaseModel):
    email: str
    password: str
    totp_code: str


class AdminMe(BaseModel):
    email: str


@router.post("/login", response_model=AdminMe)
async def login(
    payload: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> AdminMe:
    result = await session.execute(
        select(AdminUser).where(AdminUser.email == payload.email.strip())
    )
    admin = result.scalar_one_or_none()
    # Одинаковая ошибка для всех случаев — не подсказываем, что именно неверно.
    invalid = HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    if admin is None or not admin.is_active:
        raise invalid
    if not verify_password(payload.password, admin.password_hash):
        raise invalid
    if not admin.totp_secret or not verify_totp(admin.totp_secret, payload.totp_code):
        raise invalid

    set_admin_cookie(response, create_admin_token(admin.id))
    return AdminMe(email=admin.email)


@router.get("/me", response_model=AdminMe)
async def me(admin: AdminUser = Depends(get_current_admin)) -> AdminMe:
    return AdminMe(email=admin.email)


@router.post("/logout")
async def logout(response: Response) -> dict[str, bool]:
    clear_admin_cookie(response)
    return {"ok": True}
