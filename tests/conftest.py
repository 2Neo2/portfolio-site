from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

FIXTURES_DIR = Path(__file__).parent / "fixtures"
CONTENT_FIXTURE = FIXTURES_DIR / "content.yaml"


@pytest.fixture
def settings() -> Settings:
    # _env_file=None — тесты не должны зависеть от локального .env
    return Settings(_env_file=None, content_path=CONTENT_FIXTURE)  # type: ignore[call-arg]


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    # with запускает lifespan: контент загружается так же, как на проде
    with TestClient(create_app(settings)) as client:
        yield client


@pytest.fixture
def raw_content() -> dict[str, Any]:
    """Тестовый контент как словарь — удобно портить для негативных тестов."""
    data: dict[str, Any] = yaml.safe_load(CONTENT_FIXTURE.read_text(encoding="utf-8"))
    return data


@pytest.fixture
def write_content(tmp_path: Path):  # type: ignore[no-untyped-def]
    """Сохраняет словарь в YAML во временную папку и возвращает путь."""

    def _write(data: dict[str, Any]) -> Path:
        path = tmp_path / "content.yaml"
        path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        return path

    return _write
