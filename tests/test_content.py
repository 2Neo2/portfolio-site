from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.config import BASE_DIR, Settings
from app.content import ContentError, load_content
from app.main import create_app
from tests.conftest import CONTENT_FIXTURE

WriteContent = Callable[[dict[str, Any]], Path]


def test_real_content_is_valid() -> None:
    """Настоящий content/content.yaml должен проходить валидацию — иначе сайт не стартует."""
    content = load_content(BASE_DIR / "content" / "content.yaml")

    assert content.profile.name
    assert content.projects


def test_fixture_content_is_loaded() -> None:
    content = load_content(CONTENT_FIXTURE)

    assert content.profile.name == "Тест Тестов"
    assert [project.slug for project in content.projects] == ["alpha", "beta", "gamma"]


def test_get_project() -> None:
    content = load_content(CONTENT_FIXTURE)

    project = content.get_project("beta")

    assert project is not None
    assert project.name == "Бета"
    assert content.get_project("unknown") is None


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ContentError, match="не найден"):
        load_content(tmp_path / "nope.yaml")


def test_broken_yaml_syntax(tmp_path: Path) -> None:
    path = tmp_path / "content.yaml"
    path.write_text("profile: [unclosed", encoding="utf-8")

    with pytest.raises(ContentError, match="синтаксиса YAML"):
        load_content(path)


@pytest.mark.parametrize(
    ("mutate", "error_part"),
    [
        pytest.param(
            lambda data: data["profile"].pop("name"),
            "profile.name",
            id="missing-required-field",
        ),
        pytest.param(
            lambda data: data["profile"].update(emial="typo@example.com"),
            "Extra inputs are not permitted",
            id="unknown-field",
        ),
        pytest.param(
            lambda data: data["profile"]["contacts"].update(email="not-an-email"),
            "contacts.email",
            id="invalid-email",
        ),
        pytest.param(
            lambda data: data["profile"]["contacts"].update(github="not a url"),
            "contacts.github",
            id="invalid-url",
        ),
        pytest.param(
            lambda data: data["projects"][0].update(slug="Bad Slug"),
            "projects.0.slug",
            id="invalid-slug",
        ),
        pytest.param(
            lambda data: data["projects"][1].update(slug="alpha"),
            "повторяющиеся slug проектов: alpha",
            id="duplicate-slug",
        ),
        pytest.param(
            lambda data: data["skills"][0].update(items=[]),
            "skills.0.items",
            id="empty-skill-group",
        ),
    ],
)
def test_invalid_content(
    raw_content: dict[str, Any],
    write_content: WriteContent,
    mutate: Callable[[dict[str, Any]], object],
    error_part: str,
) -> None:
    mutate(raw_content)
    path = write_content(raw_content)

    with pytest.raises(ContentError) as exc_info:
        load_content(path)

    assert error_part in str(exc_info.value)


def test_app_does_not_start_with_invalid_content(
    raw_content: dict[str, Any], write_content: WriteContent
) -> None:
    """Fail fast: с битым контентом приложение падает при старте, а не на первом запросе."""
    raw_content["profile"].pop("name")
    settings = Settings(_env_file=None, content_path=write_content(raw_content))  # type: ignore[call-arg]

    with pytest.raises(ContentError), TestClient(create_app(settings)):
        pass
