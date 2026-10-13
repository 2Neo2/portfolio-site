from fastapi import APIRouter, HTTPException, Query, status

from app.content import ContentDep
from app.schemas import Profile, Project, SkillGroup

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/profile", summary="Профиль и контакты")
async def get_profile(content: ContentDep) -> Profile:
    return content.profile


@router.get("/skills", summary="Стек по группам")
async def get_skills(content: ContentDep) -> list[SkillGroup]:
    return content.skills


@router.get("/projects", summary="Список проектов")
async def list_projects(
    content: ContentDep,
    featured: bool | None = Query(
        None, description="Только избранные (true) или остальные (false)"
    ),
    stack: str | None = Query(
        None, description="Технология из стека, без учёта регистра", examples=["Docker"]
    ),
) -> list[Project]:
    projects = content.projects
    if featured is not None:
        projects = [project for project in projects if project.featured == featured]
    if stack:
        technology = stack.casefold()
        projects = [
            project
            for project in projects
            if technology in (item.casefold() for item in project.stack)
        ]
    return projects


@router.get(
    "/projects/{slug}",
    summary="Проект по slug",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Проект не найден"}},
)
async def get_project(slug: str, content: ContentDep) -> Project:
    project = content.get_project(slug)
    if project is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"Проект '{slug}' не найден"
        )
    return project
