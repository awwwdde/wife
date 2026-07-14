# askbrows backend: общий образ для API, бота и воркера (разные command в compose).
FROM python:3.12-slim

# uv для установки зависимостей.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Слой зависимостей (кэшируется отдельно от кода).
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-install-project --no-dev || uv pip install --system -e .

COPY . .
RUN uv pip install --system -e . || true

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
