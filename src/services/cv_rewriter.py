from __future__ import annotations

import re
from copy import deepcopy

from src.data.action_verbs import ACTION_VERBS
from src.models.cv import CVData, Experience, GeneratedCV


def rewrite_bullet(value: str) -> str:
    text = re.sub(r"^(I|we)\s+", "", value.strip(), flags=re.IGNORECASE)
    for phrase, replacement in sorted(ACTION_VERBS.items(), key=lambda pair: len(pair[0]), reverse=True):
        text = re.sub(rf"\b{re.escape(phrase)}\b",
                      replacement, text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).rstrip(".!?")
    return f"{text[:1].upper()}{text[1:]}." if text else ""


def _split_values(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[,\n]", value) if item.strip()]


def rewrite_experience(experience: Experience) -> Experience:
    result = deepcopy(experience)
    result.responsibilities = [item for item in (rewrite_bullet(
        value) for value in experience.responsibilities) if item]
    result.achievements = [item for item in (rewrite_bullet(
        value) for value in experience.achievements) if item]
    return result


def generate_local_cv(data: CVData) -> GeneratedCV:
    rewritten_experience = [
        rewrite_experience(job)
        for job in data.experiences
        if job.company.strip() or job.designation.strip()
    ]
    competencies = (
        _split_values(data.skills.functional)
        + _split_values(data.skills.industry)
        + _split_values(data.profile.specializations)
    )[:16]
    if data.profile.description.strip():
        summary = rewrite_bullet(data.profile.description).rstrip(".")
    else:
        summary = " ".join(
            value for value in (
                f"{data.profile.years} years of experience" if data.profile.years else "",
                data.profile.profession,
                f"with expertise in {data.profile.industry}" if data.profile.industry else "",
            ) if value
        )
    generated_data = deepcopy(data)
    generated_data.experiences = rewritten_experience
    return GeneratedCV(generated_data, summary, competencies, rewritten_experience)
