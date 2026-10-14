import hashlib
import re
from collections.abc import Iterable
from datetime import date
from functools import lru_cache

from fastapi.templating import Jinja2Templates
from jinja2 import StrictUndefined

from app.config import BASE_DIR
from app.i18n import Lang
from app.periods import (
    HasPeriod,
    format_duration,
    format_period,
    months_worked,
    total_months,
)

APP_DIR = BASE_DIR / "app"
STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = APP_DIR / "templates"

METRIC_RE = re.compile(r"^(?P<value>\d[\d\s.,]*[+%×]*)\s+(?P<label>.+)$")

Metric = tuple[str, str]


def split_results(results: Iterable[str]) -> tuple[list[Metric], list[str]]:
    """Делит результаты на метрики с числом впереди и обычные пункты.

    '1 000+ заявок в день' -> ('1 000+', 'заявок в день')
    'Lighthouse 90+'       -> обычный пункт
    """
    metrics: list[Metric] = []
    notes: list[str] = []
    for result in results:
        match = METRIC_RE.match(result)
        if match is None:
            notes.append(result)
        else:
            metrics.append((match["value"].strip(), match["label"]))
    return metrics, notes


def static_url(path: str) -> str:
    """URL статики с версией по содержимому файла: style.css?v=1a2b3c4d.

    Файл поменялся — поменялась ссылка, и браузер не покажет старую закэшированную версию.
    """
    return f"/static/{path}?v={_file_hash(path)}"


@lru_cache
def _file_hash(path: str) -> str:
    return hashlib.md5((STATIC_DIR / path).read_bytes(), usedforsecurity=False).hexdigest()[:8]


def display_url(url: object) -> str:
    """https://github.com/2Neo2 -> github.com/2Neo2"""
    return str(url).removeprefix("https://").removeprefix("http://").rstrip("/")


templates = Jinja2Templates(directory=TEMPLATES_DIR)
# Опечатка в имени переменной или ключе перевода — ошибка, а не пустая строка на сайте
templates.env.undefined = StrictUndefined
templates.env.filters["split_results"] = split_results
templates.env.filters["display_url"] = display_url
templates.env.globals["current_year"] = date.today().year
templates.env.globals["static_url"] = static_url
templates.env.globals["job_period"] = format_period


def job_duration(item: HasPeriod, lang: Lang) -> str:
    return format_duration(months_worked(item), lang)


def experience_total(items: list[HasPeriod], lang: Lang) -> str:
    return format_duration(total_months(items), lang)


templates.env.globals["job_duration"] = job_duration
templates.env.globals["experience_total"] = experience_total
