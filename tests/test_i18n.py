import pytest

from app.i18n import DEFAULT_LANG, LANGUAGES, UI, Lang, home_url, lang_from_path


def test_default_language_is_russian() -> None:
    assert DEFAULT_LANG == "ru"
    assert LANGUAGES[0] == DEFAULT_LANG


def test_all_languages_have_same_ui_keys() -> None:
    """Забытый перевод упадёт здесь, а не на проде."""
    reference = set(UI[DEFAULT_LANG])
    for lang in LANGUAGES:
        assert set(UI[lang]) == reference, lang


def test_no_empty_translations() -> None:
    for lang in LANGUAGES:
        empty = [key for key, value in UI[lang].items() if not value.strip()]
        assert not empty, f"{lang}: {empty}"


@pytest.mark.parametrize(("lang", "expected"), [("ru", "/"), ("en", "/en/")])
def test_home_url(lang: Lang, expected: str) -> None:
    assert home_url(lang) == expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/", "ru"),
        ("/projects/alpha", "ru"),
        ("/en", "en"),
        ("/en/", "en"),
        ("/en/projects/unknown", "en"),
        ("/english", "ru"),  # не путаем префикс с началом слова
    ],
)
def test_lang_from_path(path: str, expected: str) -> None:
    assert lang_from_path(path) == expected
