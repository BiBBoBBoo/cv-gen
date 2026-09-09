from __future__ import annotations

import re

from src.models.cv import CVData


def validate_cv(data: CVData) -> list[str]:
    warnings: list[str] = []
    if not data.personal.full_name.strip():
        warnings.append("Add a full name for the CV heading.")
    if data.personal.email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", data.personal.email):
        warnings.append("The email address does not look complete.")
    for index, job in enumerate(data.experiences, start=1):
        if job.start_year and job.end_year and not job.current and job.start_year.isdigit() and job.end_year.isdigit() and int(job.start_year) > int(job.end_year):
            warnings.append(
                f"Experience {index}: start year is after end year.")
    if not any(job.company.strip() or job.designation.strip() for job in data.experiences):
        warnings.append("Add at least one professional experience entry.")
    return warnings
