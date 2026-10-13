from functools import lru_cache
from pathlib import Path
from typing import Annotated

import yaml
from fastapi import Depends
from pydantic import ValidationError

from app.config import get_settings
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


@lru_cache
def get_content() -> SiteContent:
    return load_content(get_settings().content_path)


ContentDep = Annotated[SiteContent, Depends(get_content)]
