"""Зависимость авторизации CRM: текущий админ из admin-cookie."""

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_security import ADMIN_COOKIE_NAME, decode_admin_token
from app.database.session import get_session
from app.models.admin import AdminUser


async def get_current_admin(
    admin_token: str | None = Cookie(default=None, alias=ADMIN_COOKIE_NAME),
    session: AsyncSession = Depends(get_session),
) -> AdminUser:
    if not admin_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not authenticated")
    admin_id = decode_admin_token(admin_token)
    if admin_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    admin = await session.get(AdminUser, admin_id)
    if admin is None or not admin.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "admin not found")
    return admin
