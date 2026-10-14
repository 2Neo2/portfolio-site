from pathlib import Path
from typing import Annotated

import yaml
from fastapi import Depends, Query, Request
from pydantic import ValidationError

from app.i18n import DEFAULT_LANG, LANGUAGES, Lang
from app.schemas import SiteContent

Contents = dict[Lang, SiteContent]


class ContentError(Exception):
    """Файл контента не найден или содержит ошибки."""


def load_content(path: Path) -> SiteContent:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContentError(f"Файл контента не найден: {path}") from exc
    except yaml.YAMLError as exc:
        raise ContentError(f"Ошибка синтаксиса YAML в {path}:\n{exc}") from exc

    try:
        return SiteContent.model_validate(raw)
    except ValidationError as exc:
        raise ContentError(f"Ошибка в содержимом {path}:\n{exc}") from exc


def load_contents(content_dir: Path) -> Contents:
    """Загружает content/<lang>.yaml для каждого языка.

    Набор проектов во всех языках должен совпадать — иначе переключатель
    языка на странице проекта поведёт на 404.
    """
    contents: Contents = {
        lang: load_content(content_dir / f"{lang}.yaml") for lang in LANGUAGES
    }

    expected = {project.slug for project in contents[DEFAULT_LANG].projects}
    for lang, content in contents.items():
        slugs = {project.slug for project in content.projects}
        if slugs != expected:
            missing = ", ".join(sorted(expected - slugs)) or "—"
            extra = ", ".join(sorted(slugs - expected)) or "—"
            raise ContentError(
                f"Проекты в {lang}.yaml не совпадают с {DEFAULT_LANG}.yaml: "
                f"не хватает [{missing}], лишние [{extra}]"
            )
    return contents


def get_contents(request: Request) -> Contents:
    """Контент загружается один раз при старте приложения (см. lifespan в main.py)."""
    contents: Contents = request.app.state.contents
    return contents


def get_content(
    request: Request,
    lang: Annotated[Lang, Query(description="Язык контента")] = DEFAULT_LANG,
) -> SiteContent:
    return get_contents(request)[lang]


ContentDep = Annotated[SiteContent, Depends(get_content)]
