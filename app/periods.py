"""Периоды работы: «авг 2024 — н.в.», длительность «2 года 3 мес.» и общий стаж.

Даты в контенте хранятся как «YYYY-MM», поэтому длительность и стаж
считаются автоматически и не устаревают.
"""

from collections.abc import Iterable
from datetime import date
from typing import Protocol

from app.i18n import Lang

MONTHS_SHORT: dict[Lang, tuple[str, ...]] = {
    "ru": (
        "янв",
        "фев",
        "мар",
        "апр",
        "май",
        "июн",
        "июл",
        "авг",
        "сен",
        "окт",
        "ноя",
        "дек",
    ),
    "en": (
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ),
}
PRESENT: dict[Lang, str] = {"ru": "н.в.", "en": "present"}


class HasPeriod(Protocol):
    @property
    def start(self) -> str: ...

    @property
    def end(self) -> str | None: ...


def month_index(year_month: str) -> int:
    """'2024-08' -> порядковый номер месяца, чтобы считать разницу простым вычитанием."""
    year, month = year_month.split("-")
    return int(year) * 12 + int(month) - 1


def current_month(today: date | None = None) -> str:
    today = today or date.today()
    return f"{today.year:04d}-{today.month:02d}"


def format_month(year_month: str, lang: Lang) -> str:
    year, month = year_month.split("-")
    return f"{MONTHS_SHORT[lang][int(month) - 1]} {year}"


def format_period(item: HasPeriod, lang: Lang) -> str:
    end = format_month(item.end, lang) if item.end else PRESENT[lang]
    return f"{format_month(item.start, lang)} — {end}"


def months_worked(item: HasPeriod, today: date | None = None) -> int:
    """Число месяцев включительно, как считает hh.ru: сен 2023 — янв 2025 = 17."""
    end = item.end or current_month(today)
    return month_index(end) - month_index(item.start) + 1


def total_months(items: Iterable[HasPeriod], today: date | None = None) -> int:
    """Общий стаж без двойного счёта месяцев, когда работы пересекаются."""
    months: set[int] = set()
    for item in items:
        end = item.end or current_month(today)
        months.update(range(month_index(item.start), month_index(end) + 1))
    return len(months)


def _ru_plural(number: int, one: str, few: str, many: str) -> str:
    if number % 10 == 1 and number % 100 != 11:
        return one
    if 2 <= number % 10 <= 4 and not 12 <= number % 100 <= 14:
        return few
    return many


def format_duration(months: int, lang: Lang) -> str:
    """26 -> «2 года 2 мес.» / «2 yrs 2 mos»."""
    years, rest = divmod(months, 12)
    parts: list[str] = []
    if lang == "ru":
        if years:
            parts.append(f"{years} {_ru_plural(years, 'год', 'года', 'лет')}")
        if rest:
            parts.append(f"{rest} мес.")
    else:
        if years:
            parts.append(f"{years} {'yr' if years == 1 else 'yrs'}")
        if rest:
            parts.append(f"{rest} {'mo' if rest == 1 else 'mos'}")
    return " ".join(parts)
