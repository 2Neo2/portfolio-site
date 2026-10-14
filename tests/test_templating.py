import pytest

from app.templating import display_url, split_results


def test_split_results() -> None:
    metrics, notes = split_results(
        [
            "10+ интеграций",
            "1 000+ заявок в день",
            "4 источника",
            "24× быстрее выгрузка",
            "Покрытие тестами 85%+",
            "Lighthouse 90+",
        ]
    )

    assert metrics == [
        ("10+", "интеграций"),
        ("1 000+", "заявок в день"),
        ("4", "источника"),
        ("24×", "быстрее выгрузка"),
    ]
    assert notes == ["Покрытие тестами 85%+", "Lighthouse 90+"]


def test_split_results_empty() -> None:
    assert split_results([]) == ([], [])


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://github.com/2Neo2", "github.com/2Neo2"),
        ("http://example.com/", "example.com"),
        ("t.me/user", "t.me/user"),
    ],
)
def test_display_url(url: str, expected: str) -> None:
    assert display_url(url) == expected
