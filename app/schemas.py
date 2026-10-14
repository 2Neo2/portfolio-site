from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

WorkFormat = Literal["remote", "office", "hybrid"]
# Месяц в формате «2024-08»
YearMonth = Annotated[str, Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Contacts(Schema):
    telegram: HttpUrl
    github: HttpUrl
    email: EmailStr
    hh: HttpUrl | None = None


class SpokenLanguage(Schema):
    name: str = Field(min_length=1)
    level: str = Field(min_length=1)


class Profile(Schema):
    name: str = Field(min_length=1)
    title: str = Field(min_length=1)
    tagline: str
    location: str
    work_formats: list[WorkFormat] = []
    about: str
    motivation: str
    languages: list[SpokenLanguage] = []
    contacts: Contacts
    resume_url: str | None = None
    photo_url: str | None = None
    open_to_work: bool = False


class SkillGroup(Schema):
    group: str = Field(min_length=1)
    items: list[str] = Field(min_length=1)


class ProjectLinks(Schema):
    repo: HttpUrl | None = None
    demo: HttpUrl | None = None


class Screenshot(Schema):
    src: str = Field(min_length=1)  # /static/img/projects/<slug>/<file>.jpg
    alt: str = Field(min_length=1)  # подпись: что на экране


class Project(Schema):
    slug: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    name: str = Field(min_length=1)
    summary: str
    problem: str
    solution: str | None = None
    results: list[str] = []
    stack: list[str] = []
    links: ProjectLinks = ProjectLinks()
    screenshots: list[Screenshot] = []
    featured: bool = False
    in_progress: bool = False


class Experience(Schema):
    company: str = Field(min_length=1)
    role: str = Field(min_length=1)
    location: str | None = None
    start: YearMonth
    end: YearMonth | None = None  # None — работаю по настоящее время
    achievements: list[str] = []
    responsibilities: list[str] = []
    stack: list[str] = []

    @model_validator(mode="after")
    def check_dates_order(self) -> Self:
        # «YYYY-MM» сравнивается как строка в правильном порядке
        if self.end is not None and self.end < self.start:
            raise ValueError(f"end ({self.end}) раньше start ({self.start})")
        return self


class Education(Schema):
    title: str = Field(min_length=1)  # программа: «Программная инженерия»
    degree: str | None = None  # уровень: «Бакалавриат», «Магистратура»
    org: str = Field(min_length=1)  # вуз или школа
    faculty: str | None = None
    description: str | None = None  # пояснение к курсу
    period: str = Field(min_length=1)  # «2020 — 2024», «2026 — н.в.»
    url: HttpUrl | None = None


class SiteContent(Schema):
    profile: Profile
    skills: list[SkillGroup]
    projects: list[Project]
    experience: list[Experience] = []
    education: list[Education] = []
    additional_education: list[Education] = []

    @field_validator("projects")
    @classmethod
    def check_unique_slugs(cls, projects: list[Project]) -> list[Project]:
        slugs = [project.slug for project in projects]
        duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
        if duplicates:
            raise ValueError(f"повторяющиеся slug проектов: {', '.join(duplicates)}")
        return projects

    def get_project(self, slug: str) -> Project | None:
        return next(
            (project for project in self.projects if project.slug == slug), None
        )
