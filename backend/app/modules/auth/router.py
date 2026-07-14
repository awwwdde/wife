"""Эндпоинты авторизации через Telegram (Mini App + Login Widget)."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import clear_auth_cookie, set_auth_cookie
from app.core.telegram_auth import (
    TelegramAuthError,
    validate_init_data,
    validate_login_widget,
)
from app.database.session import get_session
from app.modules.auth import service
from app.modules.auth.dependencies import get_current_client
from app.modules.auth.schemas import MiniAppAuthRequest, WidgetAuthRequest
from app.modules.client.models import Client
from app.modules.client.schemas import ClientRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram/miniapp", response_model=ClientRead)
async def auth_miniapp(
    payload: MiniAppAuthRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> Client:
    try:
        tg = validate_init_data(payload.init_data)
    except TelegramAuthError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    client, token = await service.authenticate(session, tg)
    set_auth_cookie(response, token)
    return client


@router.post("/telegram/widget", response_model=ClientRead)
async def auth_widget(
    payload: WidgetAuthRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> Client:
    try:
        tg = validate_login_widget(payload.model_dump())
    except TelegramAuthError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    client, token = await service.authenticate(session, tg)
    set_auth_cookie(response, token)
    return client


@router.get("/me", response_model=ClientRead)
async def me(client: Client = Depends(get_current_client)) -> Client:
    return client


@router.post("/logout")
async def logout(response: Response) -> dict[str, bool]:
    clear_auth_cookie(response)
    return {"ok": True}
