import shutil
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

FIXTURES_DIR = Path(__file__).parent / "fixtures"
CONTENT_FIXTURE = FIXTURES_DIR / "ru.yaml"
EN_CONTENT_FIXTURE = FIXTURES_DIR / "en.yaml"

WriteContent = Callable[[dict[str, Any]], Path]


def dump_yaml(path: Path, data: dict[str, Any]) -> Path:
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return path


def make_settings(content_dir: Path) -> Settings:
    # _env_file=None — тесты не должны зависеть от локального .env
    return Settings(_env_file=None, content_dir=content_dir)  # type: ignore[call-arg]


@pytest.fixture
def settings() -> Settings:
    return make_settings(FIXTURES_DIR)


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    # with запускает lifespan: контент загружается так же, как на проде
    with TestClient(create_app(settings)) as client:
        yield client


@pytest.fixture
def raw_content() -> dict[str, Any]:
    """Тестовый русский контент как словарь — удобно портить для негативных тестов."""
    data: dict[str, Any] = yaml.safe_load(CONTENT_FIXTURE.read_text(encoding="utf-8"))
    return data


@pytest.fixture
def write_content(tmp_path: Path) -> WriteContent:
    """Сохраняет словарь в отдельный YAML-файл и возвращает путь к нему."""

    def _write(data: dict[str, Any]) -> Path:
        return dump_yaml(tmp_path / "content.yaml", data)

    return _write


@pytest.fixture
def write_content_dir(tmp_path: Path) -> WriteContent:
    """Собирает папку контента: ru.yaml из словаря + тестовый en.yaml. Возвращает папку."""

    def _write(ru_data: dict[str, Any]) -> Path:
        content_dir = tmp_path / "content"
        content_dir.mkdir(exist_ok=True)
        dump_yaml(content_dir / "ru.yaml", ru_data)
        shutil.copy(EN_CONTENT_FIXTURE, content_dir / "en.yaml")
        return content_dir

    return _write
