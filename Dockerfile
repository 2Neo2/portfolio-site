# syntax=docker/dockerfile:1

# ---------- Стадия 1: зависимости через uv ----------
FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Сначала только файлы зависимостей — этот слой кешируется, пока не поменялся uv.lock
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project


# ---------- Стадия 2: только то, что нужно для запуска ----------
FROM python:3.14-slim

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home --uid 1000 app

WORKDIR /app

COPY --from=builder /app/.venv ./.venv
COPY app ./app
COPY content ./content

# Приложение работает не от root
USER app

EXPOSE 8000

# В slim-образе нет curl — проверяем /health стандартной библиотекой Python
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
