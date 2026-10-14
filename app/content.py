from pathlib import Path
from typing import Annotated

import yaml
from fastapi import Depends, Request
from pydantic import ValidationError

from app.schemas import SiteContent


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


def get_content(request: Request) -> SiteContent:
    """Контент загружается один раз при старте приложения (см. lifespan в main.py)."""
    content: SiteContent = request.app.state.content
    return content


ContentDep = Annotated[SiteContent, Depends(get_content)]
