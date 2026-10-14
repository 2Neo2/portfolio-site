from dataclasses import dataclass
from datetime import date

import pytest

from app.periods import format_duration, format_period, months_worked, total_months

TODAY = date(2026, 10, 14)


@dataclass
class Job:
    start: str
    end: str | None = None


@pytest.mark.parametrize(
    ("job", "lang", "expected"),
    [
        (Job("2024-08"), "ru", "авг 2024 — н.в."),
        (Job("2024-08"), "en", "Aug 2024 — present"),
        (Job("2023-09", "2025-01"), "ru", "сен 2023 — янв 2025"),
        (Job("2023-09", "2025-01"), "en", "Sep 2023 — Jan 2025"),
    ],
)
def test_format_period(job: Job, lang: str, expected: str) -> None:
    assert format_period(job, lang) == expected  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("job", "expected"),
    [
        (Job("2023-09", "2025-01"), 17),  # как на hh.ru: 1 год 5 месяцев
        (Job("2024-08"), 27),  # по текущий месяц включительно
        (Job("2025-03", "2025-03"), 1),
    ],
)
def test_months_worked(job: Job, expected: int) -> None:
    assert months_worked(job, today=TODAY) == expected


def test_total_months_does_not_double_count_overlap() -> None:
    jobs = [Job("2024-08"), Job("2023-09", "2025-01")]

    # сен 2023 — окт 2026 без двойного счёта авг 2024 — янв 2025
    assert total_months(jobs, today=TODAY) == 38


def test_total_months_with_gap() -> None:
    jobs = [Job("2020-01", "2020-03"), Job("2021-01", "2021-02")]

    assert total_months(jobs, today=TODAY) == 5


@pytest.mark.parametrize(
    ("months", "ru", "en"),
    [
        (1, "1 мес.", "1 mo"),
        (5, "5 мес.", "5 mos"),
        (12, "1 год", "1 yr"),
        (17, "1 год 5 мес.", "1 yr 5 mos"),
        (27, "2 года 3 мес.", "2 yrs 3 mos"),
        (60, "5 лет", "5 yrs"),
        (132, "11 лет", "11 yrs"),
        (264, "22 года", "22 yrs"),
    ],
)
def test_format_duration(months: int, ru: str, en: str) -> None:
    assert format_duration(months, "ru") == ru
    assert format_duration(months, "en") == en
