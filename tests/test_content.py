from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.config import BASE_DIR
from app.content import ContentError, load_content, load_contents
from app.i18n import LANGUAGES
from app.main import create_app
from tests.conftest import CONTENT_FIXTURE, FIXTURES_DIR, WriteContent, make_settings


def test_real_content_is_valid() -> None:
    """Настоящие content/<lang>.yaml должны проходить валидацию — иначе сайт не стартует."""
    contents = load_contents(BASE_DIR / "content")

    assert set(contents) == set(LANGUAGES)
    for content in contents.values():
        assert content.profile.name
        assert content.projects


def test_fixture_contents_are_loaded() -> None:
    contents = load_contents(FIXTURES_DIR)

    assert contents["ru"].profile.name == "Тест Тестов"
    assert contents["en"].profile.name == "Test Testov"
    assert [project.slug for project in contents["en"].projects] == [
        "alpha",
        "beta",
        "gamma",
    ]


def test_get_project() -> None:
    content = load_content(CONTENT_FIXTURE)

    project = content.get_project("beta")

    assert project is not None
    assert project.name == "Бета"
    assert content.get_project("unknown") is None


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ContentError, match="не найден"):
        load_content(tmp_path / "nope.yaml")


def test_missing_language_file(
    raw_content: dict[str, Any], write_content_dir: WriteContent
) -> None:
    content_dir = write_content_dir(raw_content)
    (content_dir / "en.yaml").unlink()

    with pytest.raises(ContentError, match="en.yaml"):
        load_contents(content_dir)


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
            lambda data: data["profile"].update(work_formats=["freelance"]),
            "profile.work_formats.0",
            id="unknown-work-format",
        ),
        pytest.param(
            lambda data: data["experience"][0].update(start="08.2024"),
            "experience.0.start",
            id="invalid-month-format",
        ),
        pytest.param(
            lambda data: data["experience"][1].update(start="2025-02", end="2025-01"),
            "раньше start",
            id="end-before-start",
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


def test_projects_must_match_between_languages(
    raw_content: dict[str, Any], write_content_dir: WriteContent
) -> None:
    """Иначе переключатель языка на странице проекта вёл бы на 404."""
    raw_content["projects"][2]["slug"] = "delta"

    with pytest.raises(ContentError) as exc_info:
        load_contents(write_content_dir(raw_content))

    message = str(exc_info.value)
    assert "не хватает [delta]" in message
    assert "лишние [gamma]" in message


def test_app_does_not_start_with_invalid_content(
    raw_content: dict[str, Any], write_content_dir: WriteContent
) -> None:
    """Fail fast: с битым контентом приложение падает при старте, а не на первом запросе."""
    raw_content["profile"].pop("name")
    settings = make_settings(write_content_dir(raw_content))

    with pytest.raises(ContentError), TestClient(create_app(settings)):
        pass


def test_real_content_images_exist() -> None:
    """Каждый скриншот и фото из content/<lang>.yaml лежит в static — иначе на сайте будет битая картинка."""
    static_dir = BASE_DIR / "app" / "static"
    for lang, content in load_contents(BASE_DIR / "content").items():
        paths = [
            shot.src for project in content.projects for shot in project.screenshots
        ]
        for path in paths:
            assert path.startswith("/static/"), f"{lang}: {path}"
            assert (static_dir / path.removeprefix("/static/")).is_file(), (
                f"{lang}: нет файла {path}"
            )
