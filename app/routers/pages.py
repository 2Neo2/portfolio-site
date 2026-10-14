from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from app.content import ContentDep
from app.schemas import SiteContent
from app.templating import STATIC_DIR, templates

router = APIRouter(include_in_schema=False)


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
    content: SiteContent,
    status_code: int = status.HTTP_200_OK,
    **context: Any,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        template,
        {
            "content": content,
            "has_resume": file_available(content.profile.resume_url),
            "has_photo": file_available(content.profile.photo_url),
            **context,
        },
        status_code=status_code,
    )


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, content: ContentDep) -> HTMLResponse:
    return render(request, "index.html", content)


@router.get("/projects/{slug}", response_class=HTMLResponse)
async def project_detail(
    slug: str, request: Request, content: ContentDep
) -> HTMLResponse:
    project = content.get_project(slug)
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    projects = content.projects
    position = projects.index(project)
    return render(
        request,
        "project.html",
        content,
        project=project,
        previous_project=projects[position - 1] if position > 0 else None,
        next_project=projects[position + 1] if position + 1 < len(projects) else None,
    )
