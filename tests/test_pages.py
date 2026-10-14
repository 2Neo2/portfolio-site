from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.routers import pages


def test_index(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    html = response.text
    assert "<title>Тест Тестов — Python Backend Developer</title>" in html
    assert "Открыт к предложениям" in html
    for name in ("Альфа", "Бета", "Гамма"):
        assert name in html


def test_index_shows_metrics(client: TestClient) -> None:
    html = client.get("/").text

    assert '<dt class="metric-value">10+</dt>' in html
    assert '<dt class="metric-value">1 000+</dt>' in html


def test_index_splits_featured_and_other_projects(client: TestClient) -> None:
    html = client.get("/").text

    featured_block, others_block = html.split("Другие проекты")
    assert 'href="/projects/alpha"' in featured_block
    assert 'href="/projects/gamma"' in others_block


def test_project_page(client: TestClient) -> None:
    response = client.get("/projects/beta")

    assert response.status_code == 200
    html = response.text
    assert "<title>Бета — Тест Тестов</title>" in html
    assert "Задача беты" in html
    assert "Решение беты" in html
    assert "https://github.com/test-user/beta" in html
    # соседние проекты
    assert 'href="/projects/alpha"' in html
    assert 'href="/projects/gamma"' in html


def test_project_without_links_is_marked_closed(client: TestClient) -> None:
    html = client.get("/projects/alpha").text

    assert "код закрыт" in html


def test_first_project_has_no_previous_link(client: TestClient) -> None:
    html = client.get("/projects/alpha").text

    assert "pager-prev" not in html
    assert "pager-next" in html


@pytest.mark.parametrize("url", ["/projects/unknown", "/no-such-page"])
def test_html_404(client: TestClient, url: str) -> None:
    response = client.get(url)

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("text/html")
    assert "Страница не найдена" in response.text


def test_static_files(client: TestClient) -> None:
    response = client.get("/static/css/style.css")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")


def test_resume_button_hidden_without_file(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pages, "STATIC_DIR", tmp_path)

    html = client.get("/").text

    assert 'href="/static/resume.pdf"' not in html


def test_resume_button_shown_with_file(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "resume.pdf").write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(pages, "STATIC_DIR", tmp_path)

    html = client.get("/").text

    assert 'href="/static/resume.pdf"' in html


@pytest.mark.parametrize(
    ("resume_url", "expected"),
    [
        (None, False),
        ("https://example.com/resume.pdf", True),
    ],
)
def test_resume_available_without_static_file(
    resume_url: str | None, expected: bool
) -> None:
    assert pages.resume_available(resume_url) is expected
