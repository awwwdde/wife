"""FastAPI-зависимости авторизации: текущий клиент из httpOnly-cookie."""

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import COOKIE_NAME, decode_access_token
from app.database.session import get_session
from app.modules.client import repository as client_repo
from app.modules.client.models import Client


async def get_current_client(
    access_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    session: AsyncSession = Depends(get_session),
) -> Client:
    if not access_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not authenticated")
    client_id = decode_access_token(access_token)
    if client_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    client = await client_repo.get_by_id(session, client_id)
    if client is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "client not found")
    return client
