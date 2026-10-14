from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from app.content import Contents, get_contents
from app.i18n import DEFAULT_LANG, LANGUAGES, UI, Lang, home_url
from app.templating import STATIC_DIR, templates

ContentsDep = Annotated[Contents, Depends(get_contents)]


def file_available(url: str | None) -> bool:
    """Резюме и фото показываем, только если файл действительно лежит в static.

    Внешние ссылки (https://...) считаем доступными без проверки.
    """
    if url is None:
        return False
    if url.startswith("/static/"):
        return (STATIC_DIR / url.removeprefix("/static/")).is_file()
    return True


def render(
    request: Request,
    template: str,
    lang: Lang,
    *,
    page_path: str = "",
    status_code: int = status.HTTP_200_OK,
    **context: Any,
) -> HTMLResponse:
    """Рендерит страницу на нужном языке.

    page_path — путь страницы без языкового префикса ("projects/jobradar"),
    из него строятся ссылки на эту же страницу на других языках.
    """
    content = get_contents(request)[lang]
    return templates.TemplateResponse(
        request,
        template,
        {
            "content": content,
            "lang": lang,
            "languages": LANGUAGES,
            "default_lang": DEFAULT_LANG,
            "t": UI[lang],
            "home_url": home_url(lang),
            "alternate_urls": {code: home_url(code) + page_path for code in LANGUAGES},
            "site_url": request.app.state.settings.site_url.rstrip("/"),
            "has_resume": file_available(content.profile.resume_url),
            "has_photo": file_available(content.profile.photo_url),
            **context,
        },
        status_code=status_code,
    )


def build_router(lang: Lang) -> APIRouter:
    """Одинаковый набор страниц для каждого языка: / и /projects/... или /en/ и /en/projects/..."""
    prefix = "" if lang == DEFAULT_LANG else f"/{lang}"
    router = APIRouter(prefix=prefix, include_in_schema=False)

    @router.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return render(request, "index.html", lang)

    @router.get("/projects/{slug}", response_class=HTMLResponse)
    async def project_detail(
        slug: str, request: Request, contents: ContentsDep
    ) -> HTMLResponse:
        content = contents[lang]
        project = content.get_project(slug)
        if project is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        projects = content.projects
        position = projects.index(project)
        return render(
            request,
            "project.html",
            lang,
            page_path=f"projects/{slug}",
            project=project,
            previous_project=projects[position - 1] if position > 0 else None,
            next_project=projects[position + 1]
            if position + 1 < len(projects)
            else None,
        )

    return router


routers = [build_router(lang) for lang in LANGUAGES]
