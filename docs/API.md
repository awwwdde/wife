# API — справочник эндпоинтов

Актуально для Фаз 1–2. Все пути под префиксом `/api` (кроме `/healthz`).
Интерактивная схема — `/docs` (Swagger) на запущенном бэке. Времена — UTC (ISO 8601).

## Система
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/healthz` | Healthcheck панели (200 когда готово). |
| GET | `/api/health` | Статус + текущее окружение. |
| POST | `/api/bot/webhook` | Приём Telegram-обновлений (webhook бота; проверка `X-Telegram-Bot-Api-Secret-Token`). |

## Услуги
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/services` | Список активных услуг (витрина). |

## Авторизация (Telegram)
| Метод | Путь | Тело / примечание |
|---|---|---|
| POST | `/api/auth/telegram/miniapp` | `{ "init_data": "<tg.initData>" }`. Валидирует подпись, создаёт/находит клиента, ставит httpOnly-cookie. |
| POST | `/api/auth/telegram/widget` | Payload Telegram Login Widget (`id, first_name, …, auth_date, hash`). |
| GET | `/api/auth/me` | Текущий клиент по cookie (401 если нет). |
| POST | `/api/auth/logout` | Сброс cookie. |

## Запись
| Метод | Путь | Примечание |
|---|---|---|
| GET | `/api/slots?date=YYYY-MM-DD&service_ids=1&service_ids=2` | Свободные слоты (UTC) с учётом графика, буфера, шага, таймзоны. |
| POST | `/api/appointments` | `{ service_ids[], start_at, comment?, consent, source? }`. Требует авторизацию. Согласие ПДн обязательно. **409** если слот занят (EXCLUDE-констрейнт). |
| GET | `/api/appointments/my` | Записи текущего клиента. |
| POST | `/api/appointments/{id}/cancel` | Отмена (не позднее `CANCELLATION_HOURS` до визита, иначе 400). |
| POST | `/api/appointments/{id}/reschedule` | `{ start_at }`. Перенос с тем же правилом и защитой от конфликта. |

## CRM (админка) — всё под `/api/admin`, требует admin-cookie
| Метод | Путь | Назначение |
|---|---|---|
| POST | `/api/admin/login` | `{email, password, totp_code}` → admin-cookie. Пароль (bcrypt) + 2FA (TOTP). |
| GET / POST | `/api/admin/me` · `/api/admin/logout` | Текущий админ / выход. |
| GET POST PATCH DELETE | `/api/admin/services[/{id}]` | CRUD услуг (DELETE — мягкое, `is_active=false`). |
| GET / PUT | `/api/admin/schedule` | Недельный график (7 дней). |
| GET POST DELETE | `/api/admin/timeoff[/{id}]` | Отпуска/перерывы. |
| GET / PATCH | `/api/admin/settings` | Настройки мастера (приватный адрес, шаг слота, часы отмены). |
| GET | `/api/admin/clients[?q=]` · `/api/admin/clients/{id}` | База клиентов; карточка с историей, визитами и суммой. |
| GET | `/api/admin/appointments?from=&to=` | Записи за период (календарь). |
| POST | `/api/admin/appointments` | Ручная запись (существующий клиент или новый: имя+телефон). 409 при конфликте слота. |
| PATCH | `/api/admin/appointments/{id}/status` | Исход: `completed` / `cancelled` / `no_show` / `confirmed`. |

## Авторизация и безопасность
- Валидация подписи Telegram обязательна: `initData` — HMAC-SHA256 (секрет на базе
  bot token и строки `WebAppData`); Login Widget — `hash` (секрет `SHA256(bot_token)`).
  Проверяется свежесть `auth_date`.
- Сессия — JWT в **httpOnly**-cookie (`Secure` в production, `SameSite=Lax`).
- Защита от двойного бронирования — на уровне БД: Postgres `EXCLUDE USING gist`
  (`btree_gist` + `tstzrange`) по активным записям мастера.
