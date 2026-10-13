# Карта разработки: сайт-визитка Python Backend Developer

**Стек:** Python 3.12 · FastAPI · Jinja2 · Pydantic v2 · pytest · ruff · mypy · Docker · GitHub Actions
**Идея:** сайт — это одновременно визитка и демонстрация бэкенд-навыков. Код в публичном репозитории должен выглядеть как production-код: структура, типы, тесты, CI, Docker.

Отмечай `[x]` по мере выполнения. В каждом этапе есть критерий «Готово, когда…» — не переходи дальше, пока он не выполнен.

---

## Итоговая структура проекта

```
portfolio-site/
├── app/
│   ├── __init__.py
│   ├── main.py            # создание FastAPI-приложения, подключение роутеров и статики
│   ├── config.py          # настройки через pydantic-settings (.env)
│   ├── content.py         # загрузка и валидация content.yaml
│   ├── schemas.py         # Pydantic-модели: Profile, Project, SkillGroup, Education...
│   ├── routers/
│   │   ├── pages.py       # HTML-страницы (Jinja2)
│   │   └── api.py         # JSON API: /api/...
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── project.html
│   │   └── partials/      # hero.html, stack.html, projects.html, ...
│   └── static/
│       ├── css/style.css
│       ├── img/
│       └── resume.pdf
├── content/
│   └── content.yaml       # ВСЕ тексты сайта — здесь, не в шаблонах
├── tests/
│   ├── conftest.py
│   ├── test_pages.py
│   ├── test_api.py
│   └── test_content.py
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── Makefile
└── README.md
```

---

## Этап 0. Подготовка окружения (~30 мин)

- [ ] Установить [uv](https://docs.astral.sh/uv/) (`brew install uv`) — менеджер зависимостей (можно poetry, но uv быстрее и сейчас в тренде)
- [ ] `uv init` в папке, Python 3.12+
- [ ] `git init`, создать `.gitignore` (venv, `__pycache__`, `.env`, `.mypy_cache`, `.pytest_cache`)
- [ ] Создать **публичный** репозиторий на GitHub, первый коммит, push
- [ ] Зависимости:
  - основные: `fastapi`, `uvicorn[standard]`, `jinja2`, `pydantic-settings`, `pyyaml`
  - dev: `pytest`, `httpx`, `pytest-cov`, `ruff`, `mypy`, `types-PyYAML`, `pre-commit`

**Готово, когда:** `uv run python -c "import fastapi"` работает, репозиторий на GitHub.

---

## Этап 1. Контент (~1–2 часа) — самое важное

Сначала тексты, потом код. Заполни `content/content.yaml`:

```yaml
profile:
  name: Иван Доронин
  title: Python Backend Developer
  tagline: Строю надёжные бэкенды и Telegram-ботов для бизнеса
  location: ...
  about: |
    2–3 предложения: кто ты и что умеешь.
  motivation: |
    3–4 предложения: почему бэкенд, что нравится, куда растёшь.
  contacts:
    telegram: https://t.me/...
    github: https://github.com/...
    email: ...
    hh: https://hh.ru/resume/...
  resume_url: /static/resume.pdf

skills:
  - group: Языки и фреймворки
    items: [Python, FastAPI, Django, aiogram]
  - group: Базы данных и кеш
    items: [PostgreSQL, Redis, SQLAlchemy, Alembic]
  - group: Асинхронность и очереди
    items: [asyncio, Celery, RabbitMQ]
  - group: Инфраструктура
    items: [Docker, Linux, Nginx, GitHub Actions]

projects:
  - slug: business-telegram-bot
    name: Telegram-бот для бизнеса
    summary: Одна строка — что это
    problem: Какую задачу бизнеса решал
    solution: Что сделал ты (архитектура, ключевые решения)
    results:            # ЦИФРЫ: пользователи, заказы/день, время ответа, сэкономленные часы
      - ...
    stack: [Python, aiogram, PostgreSQL, Redis, Docker]
    links:
      repo: null        # коммерческий — без ссылки, это нормально
      demo: null
    featured: true
  - slug: jobradar
    name: JobRadar
    ...

experience:
  - company: ...
    role: Python Backend Developer
    period: 2024 — н.в.
    highlights: [..., ...]

education:
  - title: ...
    org: ...
    year: ...
    url: ...

learning_now: [...]   # что изучаешь сейчас — показывает рост
```

Чек-лист по контенту:
- [ ] У каждого проекта есть **problem → solution → results**, а не просто «сделал бота»
- [ ] В results хотя бы у 2 проектов есть цифры
- [ ] Мотивация — без «люблю учиться новому», конкретно
- [ ] Резюме в PDF положено в `app/static/resume.pdf`

**Готово, когда:** YAML заполнен, прочитан вслух, лишняя вода вырезана.

---

## Этап 2. Каркас FastAPI (~1 час)

- [ ] `app/config.py`: класс `Settings(BaseSettings)` — `app_name`, `debug`, `content_path`, `site_url`; читается из `.env`
- [ ] `.env.example` с примерами переменных (сам `.env` — в `.gitignore`)
- [ ] `app/main.py`: функция `create_app() -> FastAPI` (фабрика — удобно для тестов)
- [ ] Подключить `StaticFiles` на `/static`
- [ ] Эндпоинт `GET /health` → `{"status": "ok"}`
- [ ] `Makefile`: `make run` (`uvicorn app.main:app --reload`), `make test`, `make lint`

**Готово, когда:** `make run` → `http://localhost:8000/health` отвечает, `/docs` открывается.

---

## Этап 3. Модели и загрузка контента (~1–2 часа)

- [ ] `app/schemas.py`: Pydantic-модели под каждую секцию YAML (`Profile`, `Contacts`, `SkillGroup`, `Project`, `ProjectLinks`, `Experience`, `Education`, `SiteContent`)
  - используй `HttpUrl`, `EmailStr` (нужен `pydantic[email]`), `Field(min_length=...)`
- [ ] `app/content.py`: функция `load_content(path) -> SiteContent`
  - читает YAML, валидирует через `SiteContent.model_validate(...)`
  - кешируется (`functools.lru_cache`) — файл читается один раз
- [ ] Dependency `get_content()` для роутеров (`Depends`) — так в тестах можно подменить контент через `app.dependency_overrides`
- [ ] Если YAML невалиден — приложение **падает при старте** с понятной ошибкой (fail fast)

**Готово, когда:** опечатка в YAML (например, удалённое `name` у проекта) даёт понятную ошибку валидации при запуске.

---

## Этап 4. JSON API (~1 час)

Изюминка для бэкенд-ревьюера: тот же контент доступен через API.

- [ ] `GET /api/profile` → профиль + контакты
- [ ] `GET /api/skills`
- [ ] `GET /api/projects` → список, query-параметры `?featured=true`, `?stack=Redis`
- [ ] `GET /api/projects/{slug}` → 404 с нормальным JSON, если нет
- [ ] `response_model` у каждого эндпоинта, `tags=["api"]`, описания (`summary`, `description`) — Swagger должен выглядеть аккуратно
- [ ] Роутер с `prefix="/api"`

**Готово, когда:** `/docs` выглядит как документация нормального сервиса, все ручки работают.

---

## Этап 5. HTML-страницы (~3–4 часа)

- [ ] `Jinja2Templates`, роутер `pages.py`
- [ ] `base.html`: `<head>` (meta, title, description, og-теги), шапка с навигацией по якорям, футер
- [ ] `GET /` → `index.html`, секции через `{% include "partials/..." %}`:
  1. Hero: имя, должность, tagline, кнопки (Telegram, GitHub, Резюме)
  2. Обо мне + мотивация
  3. Стек (группы-карточки с тегами)
  4. Проекты (карточки; `featured` — крупнее)
  5. Опыт (таймлайн)
  6. Обучение + «изучаю сейчас»
  7. Контакты
- [ ] `GET /projects/{slug}` → детальная страница проекта (problem / solution / results / stack); 404 — своя страница `404.html`
- [ ] Ни одного текста, захардкоженного в шаблоне, — всё из `content.yaml`

**Готово, когда:** вся информация из YAML видна на сайте, ссылки работают.

---

## Этап 6. Дизайн и вёрстка (~3–5 часов)

- [ ] Чистый CSS (CSS-переменные для цветов) или лёгкий фреймворк ([Pico CSS](https://picocss.com) — минимум усилий, выглядит прилично)
- [ ] Адаптив: проверить на 375px (телефон) — рекрутеры часто смотрят с телефона
- [ ] Тёмная тема через `prefers-color-scheme`
- [ ] Шрифт: Inter / JetBrains Mono для акцентов (Google Fonts)
- [ ] Фото или аватар (необязательно, но повышает доверие)
- [ ] Favicon
- [ ] Без тяжёлого JS — сайт должен грузиться мгновенно

**Готово, когда:** Lighthouse (Chrome DevTools) ≥ 90 по Performance, Accessibility, SEO.

---

## Этап 7. Тесты (~2 часа)

- [ ] `conftest.py`: фикстура `client` (`TestClient(create_app())`), фикстура с тестовым контентом через `dependency_overrides`
- [ ] `test_content.py`: реальный `content.yaml` валиден; битый YAML → ошибка
- [ ] `test_api.py`: все ручки 200, фильтры работают, несуществующий slug → 404
- [ ] `test_pages.py`: `/` → 200 и содержит имя; `/projects/{slug}` → 200; неизвестная страница → 404; `/health` → ok
- [ ] Покрытие: `pytest --cov=app` ≥ 85%

**Готово, когда:** `make test` зелёный, покрытие ≥ 85%.

---

## Этап 8. Качество кода (~1 час)

- [ ] `ruff` (линтер + форматтер) — настройки в `pyproject.toml`, включить правила `E, F, I, B, UP, SIM`
- [ ] `mypy --strict` по папке `app/` (или хотя бы `disallow_untyped_defs = true`)
- [ ] `pre-commit`: ruff, ruff-format, mypy, trailing-whitespace
- [ ] Type hints везде

**Готово, когда:** `make lint` проходит без ошибок.

---

## Этап 9. Docker (~1–2 часа)

- [ ] `Dockerfile` multi-stage:
  - stage 1: установка зависимостей через uv
  - stage 2: `python:3.12-slim`, копируем venv и код
  - запуск от **не-root** пользователя
  - `HEALTHCHECK` на `/health`
  - `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]`
- [ ] `.dockerignore` (tests, .git, .venv, кеши)
- [ ] `docker-compose.yml` для локального запуска
- [ ] Размер образа < 200 МБ (`docker images`)

**Готово, когда:** `docker compose up` → сайт открывается на localhost:8000.

---

## Этап 10. CI — GitHub Actions (~1 час)

`.github/workflows/ci.yml`, запуск на push и pull request:
- [ ] job `lint`: ruff check + ruff format --check + mypy
- [ ] job `test`: pytest с покрытием
- [ ] job `docker`: сборка образа (проверка, что собирается)
- [ ] Бейдж CI в README

**Готово, когда:** на GitHub зелёная галочка у последнего коммита.

---

## Этап 11. Деплой (~1–3 часа)

Выбери один вариант:

**A. Render / Fly.io (проще)**
- [ ] Подключить репозиторий, деплой из Dockerfile
- [ ] Автодеплой при push в `main`
- [ ] Минус бесплатного Render: «засыпает» и первый запрос идёт ~30 сек

**B. VPS (лучше для резюме — показывает DevOps-навыки)**
- [ ] VPS (Timeweb / Selectel / Aeza, ~300–500 ₽/мес), Ubuntu
- [ ] SSH по ключу, отключить вход по паролю, `ufw`
- [ ] Docker + Docker Compose на сервере
- [ ] Caddy как reverse proxy (HTTPS автоматически через Let's Encrypt) — проще, чем nginx + certbot
- [ ] CD: GitHub Actions → сборка образа → push в GHCR → `ssh` на сервер → `docker compose pull && up -d`

**Общее:**
- [ ] Домен (`ivan-doronin.dev` или `.ru`), A-запись на сервер
- [ ] HTTPS работает, http редиректит на https

**Готово, когда:** сайт открывается по домену с замочком, push в main автоматически обновляет сайт.

---

## Этап 12. Полировка и SEO (~1–2 часа)

- [ ] `GET /robots.txt` и `GET /sitemap.xml` — генерировать роутами FastAPI (ещё плюс к бэкенду)
- [ ] Open Graph-картинка (превью при отправке ссылки в Telegram)
- [ ] `<title>` и `meta description` на каждой странице
- [ ] Middleware: заголовки безопасности (`X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`)
- [ ] Кеширование статики (`Cache-Control`)
- [ ] Проверить превью ссылки в Telegram

---

## Этап 13. README репозитория (~1 час)

README — вторая визитка, его тоже читают:
- [ ] Ссылка на живой сайт + скриншот
- [ ] Стек и архитектура (короткая схема)
- [ ] Как запустить: локально, через Docker, тесты
- [ ] Бейджи: CI, coverage, Python version
- [ ] Описание API-эндпоинтов

---

## Бонусы (после запуска, по желанию)

Выбирай то, что хочешь показать работодателю:

- [ ] **Форма обратной связи → Telegram-бот.** POST `/api/contact` → валидация → отправка сообщения тебе в Telegram (Bot API через `httpx.AsyncClient`) + rate limit (`slowapi`) и honeypot от спама. Отлично ложится на твой опыт с ботами
- [ ] **Счётчик просмотров / аналитика:** middleware пишет хиты в SQLite/PostgreSQL (SQLAlchemy 2.0 async + Alembic), `/api/stats` за токеном
- [ ] **GitHub-интеграция:** подтягивать последние репозитории/звёзды через GitHub API с кешированием в Redis (TTL 1 час)
- [ ] **Мультиязычность** RU/EN: `content.ru.yaml` / `content.en.yaml`, переключение `/en/`
- [ ] **Структурированные логи** (`structlog`) + request-id middleware
- [ ] **Мониторинг:** `/metrics` для Prometheus или просто UptimeRobot на `/health`

---

## Примерный план по времени

| Неделя | Этапы | Результат |
|---|---|---|
| 1 | 0–3 | Контент готов, каркас и модели работают |
| 2 | 4–6 | API + полноценные страницы с дизайном |
| 3 | 7–10 | Тесты, линтеры, Docker, CI |
| 4 | 11–13 | Сайт в интернете на своём домене, README |
| дальше | Бонусы | 1–2 фичи на выбор |

При 1–2 часах в день — около месяца. Если вечеров больше — 1,5–2 недели.

---

## Советы по процессу

- Делай **маленькие коммиты** с нормальными сообщениями (`feat: add projects API`, `test: cover 404 for unknown slug`) — ревьюеры смотрят историю
- Работай через ветки и PR даже в одиночку — CI будет проверять каждый PR
- Застрял больше чем на 30 минут — спрашивай, разберём
- После каждого этапа можно прислать код на ревью
