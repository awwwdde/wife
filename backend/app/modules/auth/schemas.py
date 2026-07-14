from pydantic import BaseModel


class MiniAppAuthRequest(BaseModel):
    """Тело запроса из Mini App — сырая строка initData от Telegram."""

    init_data: str


class WidgetAuthRequest(BaseModel):
    """Payload Telegram Login Widget (браузер). Поля приходят как есть от Telegram."""

    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str
