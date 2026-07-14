"""Валидация подписи Telegram — критично по SPEC §7.

Без проверки подписи нельзя доверять данным фронта. Реализованы оба пути:
- Mini App `initData` (HMAC-SHA256 с секретом на базе bot token и строки "WebAppData");
- Login Widget `hash` (секрет = SHA256(bot_token)).
"""

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl

from app.core.config import settings

# Максимальный возраст auth_date (сек). Защита от replay старых данных.
MAX_AUTH_AGE_SEC = 24 * 60 * 60


class TelegramAuthError(Exception):
    """Подпись невалидна или данные просрочены/битые."""


@dataclass
class TelegramUser:
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None


def _build_data_check_string(pairs: dict[str, str]) -> str:
    # Все пары кроме hash, отсортированы по ключу, "key=value" через \n.
    return "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs))


def _check_auth_date(pairs: dict[str, str]) -> None:
    auth_date = pairs.get("auth_date")
    if not auth_date:
        return
    try:
        age = time.time() - int(auth_date)
    except ValueError as exc:
        raise TelegramAuthError("bad auth_date") from exc
    if age > MAX_AUTH_AGE_SEC:
        raise TelegramAuthError("auth data expired")


def validate_init_data(init_data: str) -> TelegramUser:
    """Проверить `initData` строки Mini App и вернуть пользователя."""
    if not settings.BOT_TOKEN:
        raise TelegramAuthError("BOT_TOKEN is not configured")

    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise TelegramAuthError("hash is missing")

    data_check_string = _build_data_check_string(pairs)
    secret_key = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calc_hash, received_hash):
        raise TelegramAuthError("invalid initData signature")

    _check_auth_date(pairs)

    user_raw = pairs.get("user")
    if not user_raw:
        raise TelegramAuthError("user is missing in initData")
    user = json.loads(user_raw)
    return TelegramUser(
        id=int(user["id"]),
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        username=user.get("username"),
        photo_url=user.get("photo_url"),
    )


def validate_login_widget(data: dict[str, str]) -> TelegramUser:
    """Проверить payload Telegram Login Widget (браузер) и вернуть пользователя."""
    if not settings.BOT_TOKEN:
        raise TelegramAuthError("BOT_TOKEN is not configured")

    pairs = {k: str(v) for k, v in data.items() if v is not None}
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise TelegramAuthError("hash is missing")

    data_check_string = _build_data_check_string(pairs)
    secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calc_hash, received_hash):
        raise TelegramAuthError("invalid login widget signature")

    _check_auth_date(pairs)

    return TelegramUser(
        id=int(pairs["id"]),
        first_name=pairs.get("first_name"),
        last_name=pairs.get("last_name"),
        username=pairs.get("username"),
        photo_url=pairs.get("photo_url"),
    )
