from __future__ import annotations

from dataclasses import asdict, dataclass, field
from uuid import uuid4
from typing import Any


@dataclass
class PersonalInformation:
    full_name: str = ""
    phone: str = ""
    email: str = ""
    location: str = ""
    linkedin: str = ""
    target_job_title: str = ""
    employment_preference: str = "Full-time"


@dataclass
class ProfessionalProfile:
    years: str = ""
    profession: str = ""
    industry: str = ""
    specializations: str = ""
    description: str = ""
    target_roles: str = ""


@dataclass
class Experience:
    id: str = field(default_factory=lambda: str(uuid4()))
    company: str = ""
    designation: str = ""
    location: str = ""
    start_year: str = ""
    end_year: str = ""
    current: bool = False
    industry: str = ""
    responsibilities: list[str] = field(default_factory=lambda: [""])
    achievements: list[str] = field(default_factory=lambda: [""])
    processes: str = ""
    team_management: str = ""
    software: str = ""


@dataclass
class Skills:
    functional: str = ""
    industry: str = ""
    software: str = ""
    custom: str = ""


@dataclass
class Education:
    id: str = field(default_factory=lambda: str(uuid4()))
    qualification: str = ""
    specialization: str = ""
    institution: str = ""
    year: str = ""
    certification: str = ""


@dataclass
class AdditionalInformation:
    languages: str = ""
    awards: str = ""
    memberships: str = ""
    training: str = ""
    availability: str = ""


@dataclass
class CVData:
    personal: PersonalInformation = field(default_factory=PersonalInformation)
    profile: ProfessionalProfile = field(default_factory=ProfessionalProfile)
    experiences: list[Experience] = field(
        default_factory=lambda: [Experience()])
    skills: Skills = field(default_factory=Skills)
    education: list[Education] = field(default_factory=lambda: [Education()])
    additional: AdditionalInformation = field(
        default_factory=AdditionalInformation)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GeneratedCV:
    data: CVData
    summary: str
    competencies: list[str]
    experience: list[Experience]
    status: str = "Local refinement used"


def _clean_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return [""]
    return [str(item) for item in value] or [""]


def _make(cls: type, value: Any):
    return cls(**value) if isinstance(value, dict) else cls()


def cv_from_dict(raw: Any) -> CVData:
    if not isinstance(raw, dict):
        return CVData()
    personal = _make(PersonalInformation, raw.get("personal"))
    profile = _make(ProfessionalProfile, raw.get("profile"))
    skills = _make(Skills, raw.get("skills"))
    additional = _make(AdditionalInformation, raw.get("additional"))
    experiences = []
    for item in raw.get("experiences", []):
        if isinstance(item, dict):
            item = dict(item)
            item["responsibilities"] = _clean_list(
                item.get("responsibilities"))
            item["achievements"] = _clean_list(item.get("achievements"))
            experiences.append(_make(Experience, item))
    education = [_make(Education, item) for item in raw.get(
        "education", []) if isinstance(item, dict)]
    return CVData(personal, profile, experiences or [Experience()], skills, education or [Education()], additional)
