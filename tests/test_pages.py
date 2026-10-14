import re
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


def test_photo_placeholder_without_file(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pages, "STATIC_DIR", tmp_path)

    html = client.get("/").text

    assert 'src="/static/img/photo.jpg"' not in html
    assert (
        '<span class="avatar avatar-placeholder" aria-hidden="true">ТТ</span>' in html
    )


def test_photo_shown_with_file(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "img").mkdir()
    (tmp_path / "img" / "photo.jpg").write_bytes(b"\xff\xd8\xff")
    monkeypatch.setattr(pages, "STATIC_DIR", tmp_path)

    html = client.get("/").text

    assert 'src="/static/img/photo.jpg" alt="Тест Тестов"' in html
    assert "avatar-placeholder" not in html


def test_hero_contacts(client: TestClient) -> None:
    html = client.get("/").text

    hero = html.split('class="hero-contacts"')[1].split("</ul>")[0]
    assert "t.me/test_user" in hero
    assert 'href="mailto:test@example.com"' in hero
    assert "github.com/test-user" in hero
    assert "hh.ru" not in hero  # hh не указан в тестовом контенте


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (None, False),
        ("https://example.com/resume.pdf", True),
    ],
)
def test_file_available_without_static_file(url: str | None, expected: bool) -> None:
    assert pages.file_available(url) is expected


def test_russian_is_default(client: TestClient) -> None:
    html = client.get("/").text

    assert '<html lang="ru">' in html
    assert "Обо мне" in html


def test_english_index(client: TestClient) -> None:
    response = client.get("/en/")

    assert response.status_code == 200
    html = response.text
    assert '<html lang="en">' in html
    assert "<title>Test Testov — Python Backend Developer</title>" in html
    assert "Open to work" in html
    assert "About" in html
    assert 'href="/en/projects/alpha"' in html
    assert "Обо мне" not in html


def test_english_index_without_trailing_slash_redirects(client: TestClient) -> None:
    response = client.get("/en", follow_redirects=False)

    assert response.status_code in (307, 308)
    assert response.headers["location"].endswith("/en/")


def test_english_project_page(client: TestClient) -> None:
    response = client.get("/en/projects/beta")

    assert response.status_code == 200
    html = response.text
    assert "Beta problem" in html
    assert 'href="/en/projects/alpha"' in html


@pytest.mark.parametrize(
    ("url", "switch_to"),
    [
        ("/", 'href="/en/" hreflang="en"'),
        ("/en/", 'href="/" hreflang="ru"'),
        ("/projects/beta", 'href="/en/projects/beta" hreflang="en"'),
        ("/en/projects/beta", 'href="/projects/beta" hreflang="ru"'),
    ],
)
def test_language_switch_keeps_page(
    client: TestClient, url: str, switch_to: str
) -> None:
    html = client.get(url).text

    assert switch_to in html


def test_hreflang_alternates(client: TestClient) -> None:
    html = client.get("/projects/beta").text

    assert (
        '<link rel="alternate" hreflang="ru" href="http://localhost:8000/projects/beta">'
        in html
    )
    assert (
        '<link rel="alternate" hreflang="en" href="http://localhost:8000/en/projects/beta">'
        in html
    )
    assert 'hreflang="x-default" href="http://localhost:8000/projects/beta"' in html


@pytest.mark.parametrize(
    ("url", "expected"),
    [("/", ["Удалёнка", "Гибрид"]), ("/en/", ["Remote", "Hybrid"])],
)
def test_work_formats(client: TestClient, url: str, expected: list[str]) -> None:
    html = client.get(url).text

    block = html.split('class="work-formats"')[1].split("</ul>")[0]
    labels = [
        item.split("</svg>")[1].split("</li>")[0]
        for item in block.split('class="work-format"')[1:]
    ]
    assert labels == expected


def test_static_assets_have_version(client: TestClient) -> None:
    """У CSS/JS в ссылке есть хэш содержимого — браузер не покажет старую версию."""
    html = client.get("/").text

    assert re.search(r'href="/static/css/style\.css\?v=[0-9a-f]{8}"', html)
    assert re.search(r'src="/static/js/theme\.js\?v=[0-9a-f]{8}"', html)


def test_english_404(client: TestClient) -> None:
    response = client.get("/en/projects/unknown")

    assert response.status_code == 404
    assert '<html lang="en">' in response.text
    assert "Page not found" in response.text


@pytest.mark.parametrize(
    ("url", "link"),
    [
        ("/", '<a href="/#education">Образование</a>'),
        ("/en/", '<a href="/en/#education">Education</a>'),
    ],
)
def test_nav_has_education_link(client: TestClient, url: str, link: str) -> None:
    nav = client.get(url).text.split('<nav class="nav"')[1].split("</nav>")[0]

    assert link in nav


def test_education_section(client: TestClient) -> None:
    html = client.get("/").text
    section = html.split('id="education"')[1].split("</section>")[0]

    assert '<span class="edu-period">2020 — 2024</span>' in section
    assert '<p class="edu-degree">Бакалавриат</p>' in section
    assert "Тестовая программа" in section
    assert '<p class="edu-faculty">Тестовый факультет</p>' in section
    # дополнительное образование — отдельным блоком, без уровня
    additional = section.split("Дополнительное образование")[1]
    assert "Тестовый курс" in additional
    assert "edu-degree" not in additional


def test_english_education_section(client: TestClient) -> None:
    section = client.get("/en/").text.split('id="education"')[1].split("</section>")[0]

    assert "Bachelor&#39;s degree" in section
    assert "Additional education" in section


def test_education_description(client: TestClient) -> None:
    html = client.get("/").text

    assert '<p class="edu-description">Тестовое пояснение</p>' in html


def test_experience_section(client: TestClient) -> None:
    section = client.get("/").text.split('id="experience"')[1].split("</section>")[0]

    assert "авг 2024 — н.в." in section
    assert "сен 2023 — янв 2025" in section
    assert (
        "1 год 5 мес." in section
    )  # длительность закрытой работы не зависит от сегодняшней даты
    assert "Тестовая компания" in section
    assert '<span class="timeline-location"> · Тестоград</span>' in section
    assert "Тестовое достижение" in section
    assert "<summary>Обязанности</summary>" in section
    assert '<li class="tag">FastAPI</li>' in section


def test_english_experience_section(client: TestClient) -> None:
    section = client.get("/en/").text.split('id="experience"')[1].split("</section>")[0]

    assert "Aug 2024 — present" in section
    assert "1 yr 5 mos" in section
    assert "Key achievements" in section


def test_spoken_languages(client: TestClient) -> None:
    html = client.get("/").text

    assert '<span class="spoken-language-name">Английский</span> B2' in html


def test_closed_source_note_is_neutral(client: TestClient) -> None:
    html = client.get("/projects/alpha").text

    assert "Код проекта закрыт" in html


def test_in_progress_badge(client: TestClient) -> None:
    assert (
        '<span class="badge-progress">В разработке</span>'
        in client.get("/projects/gamma").text
    )
    assert "badge-progress" not in client.get("/projects/beta").text
    assert (
        '<span class="badge-progress">In progress</span>'
        in client.get("/en/projects/gamma").text
    )


def test_project_screenshots(client: TestClient) -> None:
    html = client.get("/projects/gamma").text

    assert (
        '<img src="/static/img/projects/gamma/main.jpg" alt="Главный экран гаммы"'
        in html
    )
    assert "<figcaption>Главный экран гаммы</figcaption>" in html


def test_project_without_solution_hides_section(client: TestClient) -> None:
    assert "<h2>Решение</h2>" not in client.get("/projects/gamma").text
    assert "<h2>Решение</h2>" in client.get("/projects/beta").text


def test_screenshots_only_on_project_page(client: TestClient) -> None:
    """На главной картинок проектов нет, даже если у проекта есть скриншоты."""
    assert "/static/img/projects/alpha/main.jpg" not in client.get("/").text
    assert "/static/img/projects/alpha/main.jpg" in client.get("/projects/alpha").text
