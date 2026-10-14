from typing import Final, Literal

Lang = Literal["ru", "en"]

LANGUAGES: Final[tuple[Lang, ...]] = ("ru", "en")
DEFAULT_LANG: Final[Lang] = "ru"


def home_url(lang: Lang) -> str:
    """Основной язык живёт в корне сайта, остальные — под префиксом: /en/."""
    return "/" if lang == DEFAULT_LANG else f"/{lang}/"


def lang_from_path(path: str) -> Lang:
    for lang in LANGUAGES:
        if lang != DEFAULT_LANG and (
            path == f"/{lang}" or path.startswith(f"/{lang}/")
        ):
            return lang
    return DEFAULT_LANG


# Подписи интерфейса. Тексты о себе и проектах — в content/<lang>.yaml.
UI: Final[dict[Lang, dict[str, str]]] = {
    "ru": {
        "og_locale": "ru_RU",
        "skip_to_content": "К содержимому",
        "nav_label": "Разделы",
        "nav_about": "Обо мне",
        "nav_stack": "Стек",
        "nav_projects": "Проекты",
        "nav_experience": "Опыт",
        "nav_contacts": "Контакты",
        "language_label": "Язык",
        "theme_toggle": "Переключить тему",
        "open_to_work": "Открыт к предложениям",
        "work_format_label": "Формат работы",
        "work_format_remote": "Удалёнка",
        "work_format_office": "Офис",
        "work_format_hybrid": "Гибрид",
        "contacts_label": "Контакты",
        "write_telegram": "Написать в Telegram",
        "download_resume": "Скачать резюме",
        "api_example": "Пример ответа API этого сайта",
        "open_swagger": "Открыть API в Swagger",
        "about_title": "Обо мне",
        "motivation_title": "Почему бэкенд",
        "stack_title": "Стек",
        "projects_title": "Проекты",
        "more": "Подробнее",
        "other_projects": "Другие проекты",
        "experience_title": "Опыт",
        "education_title": "Обучение",
        "learning_now": "Изучаю сейчас",
        "contacts_text": "Если у вас есть вакансия или проект — буду рад присоединиться к команде и работать вместе. Напишите, обсудим задачи и формат работы.",
        "hh_value": "Резюме на hh.ru",
        "resume": "Резюме",
        "resume_value": "Скачать PDF",
        "made_with": "Сделано на FastAPI",
        "all_projects": "Все проекты",
        "project": "Проект",
        "open_demo": "Открыть демо",
        "source_code": "Исходный код",
        "closed_source": "Коммерческий проект — код закрыт",
        "problem": "Задача",
        "solution": "Решение",
        "results": "Результаты",
        "previous": "Предыдущий",
        "next": "Следующий",
        "not_found_title": "Страница не найдена",
        "not_found_text": "Возможно, ссылка устарела или в адресе опечатка.",
        "to_home": "На главную",
    },
    "en": {
        "og_locale": "en_US",
        "skip_to_content": "Skip to content",
        "nav_label": "Sections",
        "nav_about": "About",
        "nav_stack": "Stack",
        "nav_projects": "Projects",
        "nav_experience": "Experience",
        "nav_contacts": "Contact",
        "language_label": "Language",
        "theme_toggle": "Toggle theme",
        "open_to_work": "Open to work",
        "work_format_label": "Work format",
        "work_format_remote": "Remote",
        "work_format_office": "Office",
        "work_format_hybrid": "Hybrid",
        "contacts_label": "Contacts",
        "write_telegram": "Message on Telegram",
        "download_resume": "Download CV",
        "api_example": "Sample API response of this site",
        "open_swagger": "Open API in Swagger",
        "about_title": "About",
        "motivation_title": "Why backend",
        "stack_title": "Stack",
        "projects_title": "Projects",
        "more": "Read more",
        "other_projects": "Other projects",
        "experience_title": "Experience",
        "education_title": "Education",
        "learning_now": "Currently learning",
        "contacts_text": "Have a job opening or a project in mind? I'd be glad to join your team and work together. Drop me a line and let's discuss the details.",
        "hh_value": "CV on hh.ru",
        "resume": "CV",
        "resume_value": "Download PDF",
        "made_with": "Built with FastAPI",
        "all_projects": "All projects",
        "project": "Project",
        "open_demo": "Open demo",
        "source_code": "Source code",
        "closed_source": "Commercial project — closed source",
        "problem": "Problem",
        "solution": "Solution",
        "results": "Results",
        "previous": "Previous",
        "next": "Next",
        "not_found_title": "Page not found",
        "not_found_text": "The link may be outdated or there is a typo in the address.",
        "to_home": "Back to home",
    },
}
