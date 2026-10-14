import pytest
from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_profile(client: TestClient) -> None:
    response = client.get("/api/profile")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Тест Тестов"
    assert data["contacts"]["email"] == "test@example.com"
    assert data["open_to_work"] is True


def test_skills(client: TestClient) -> None:
    response = client.get("/api/skills")

    assert response.status_code == 200
    assert response.json() == [
        {"group": "Языки", "items": ["Python", "SQL"]},
        {"group": "Инфраструктура", "items": ["Docker", "Linux"]},
    ]


def slugs(response_json: list[dict[str, object]]) -> list[object]:
    return [project["slug"] for project in response_json]


def test_list_projects(client: TestClient) -> None:
    response = client.get("/api/projects")

    assert response.status_code == 200
    assert slugs(response.json()) == ["alpha", "beta", "gamma"]


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("featured=true", ["alpha", "beta"]),
        ("featured=false", ["gamma"]),
        ("stack=Docker", ["alpha"]),
        ("stack=python", ["alpha", "beta"]),  # без учёта регистра
        ("stack=Rust", []),
        ("featured=true&stack=FastAPI", ["beta"]),
    ],
)
def test_filter_projects(client: TestClient, query: str, expected: list[str]) -> None:
    response = client.get(f"/api/projects?{query}")

    assert response.status_code == 200
    assert slugs(response.json()) == expected


def test_invalid_filter_value(client: TestClient) -> None:
    response = client.get("/api/projects?featured=maybe")

    assert response.status_code == 422


def test_get_project(client: TestClient) -> None:
    response = client.get("/api/projects/beta")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Бета"
    assert data["links"]["repo"] == "https://github.com/test-user/beta"


def test_get_unknown_project_returns_json_404(client: TestClient) -> None:
    response = client.get("/api/projects/unknown")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"detail": "Проект 'unknown' не найден"}


def test_unknown_api_route_returns_json_404(client: TestClient) -> None:
    response = client.get("/api/unknown")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"


def test_openapi_schema(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert set(paths) == {
        "/health",
        "/api/profile",
        "/api/skills",
        "/api/projects",
        "/api/projects/{slug}",
    }
