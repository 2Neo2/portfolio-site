from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import Settings, get_settings
from app.content import load_contents
from app.i18n import lang_from_path
from app.routers import api, pages
from app.templating import STATIC_DIR


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # fail fast: битый контент не даст приложению стартовать
    app.state.contents = load_contents(app.state.settings.content_dir)
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> Response:
        """Для страниц сайта — своя 404, для API и прочих ошибок — стандартный JSON."""
        if exc.status_code != status.HTTP_404_NOT_FOUND or request.url.path.startswith("/api"):
            return await http_exception_handler(request, exc)
        return pages.render(
            request,
            "404.html",
            lang_from_path(request.url.path),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @app.get("/health", tags=["service"], summary="Проверка работоспособности")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api.router)
    for router in pages.routers:
        app.include_router(router)

    return app


app = create_app()
