from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator

WorkFormat = Literal["remote", "office", "hybrid"]


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Contacts(Schema):
    telegram: HttpUrl
    github: HttpUrl
    email: EmailStr
    hh: HttpUrl | None = None


class Profile(Schema):
    name: str = Field(min_length=1)
    title: str = Field(min_length=1)
    tagline: str
    location: str
    work_formats: list[WorkFormat] = []
    about: str
    motivation: str
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


class Project(Schema):
    slug: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    name: str = Field(min_length=1)
    summary: str
    problem: str
    solution: str
    results: list[str] = []
    stack: list[str] = []
    links: ProjectLinks = ProjectLinks()
    featured: bool = False


class Experience(Schema):
    company: str
    role: str
    period: str
    highlights: list[str] = []


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
