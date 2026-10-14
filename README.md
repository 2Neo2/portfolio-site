# Портфолио Ивана Доронина — Python Backend Developer

[![CI](https://github.com/2Neo2/portfolio-site/actions/workflows/ci.yml/badge.svg)](https://github.com/2Neo2/portfolio-site/actions/workflows/ci.yml)
![Python 3.14](https://img.shields.io/badge/python-3.14-3776AB)
![Coverage 100%](https://img.shields.io/badge/coverage-100%25-brightgreen)

Сайт-визитка на FastAPI: обо мне, стек, проекты, опыт и образование на русском и английском,
плюс публичный JSON API с тем же контентом.

## Стек

- **FastAPI**, Jinja2, Pydantic v2, pydantic-settings
- Контент — YAML (`content/ru.yaml`, `content/en.yaml`) с валидацией через Pydantic при старте
- **pytest** (100% покрытие), **ruff**, **mypy --strict**, pre-commit
- **Docker** (multi-stage, non-root, healthcheck), GitHub Actions

## Как устроено

```
app/
├── main.py          create_app(): lifespan загружает контент, роутеры, обработка 404
├── config.py        настройки из переменных окружения и .env
├── schemas.py       Pydantic-модели контента
├── content.py       загрузка и проверка YAML для всех языков
├── i18n.py          языки и подписи интерфейса
├── periods.py       периоды работы и стаж
├── templating.py    Jinja2, фильтры, версия статики для сброса кэша
├── routers/
│   ├── api.py       JSON API
│   └── pages.py     страницы на каждом языке: / и /en/
├── templates/       base, секции главной, страница проекта, схемы
└── static/          css, js, картинки
content/             тексты сайта — правятся без кода
tests/               pytest на отдельном тестовом контенте
```

Ошибка в YAML — опечатка в поле, неверная дата, проект есть только в одном языке —
не даёт приложению стартовать и показывает, что именно не так.

## Запуск

Нужен [uv](https://docs.astral.sh/uv/).

```bash
uv sync
make run          # http://127.0.0.1:8000
```

В Docker:

```bash
make docker-up    # http://localhost:8000, другой порт: PORT=8080 make docker-up
make docker-down
```

## Проверки

```bash
make check        # ruff + mypy --strict + pytest с покрытием
make hooks        # установить pre-commit
```

## API

Документация: `/docs`. Все ручки принимают `?lang=ru|en`.

| Метод | Путь | Что отдаёт |
|---|---|---|
| GET | `/api/profile` | профиль и контакты |
| GET | `/api/skills` | стек по группам |
| GET | `/api/projects` | проекты, фильтры `?featured=true` и `?stack=Docker` |
| GET | `/api/projects/{slug}` | один проект или 404 |
| GET | `/health` | проверка, что сервис жив |
