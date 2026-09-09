from __future__ import annotations

import html
from pathlib import Path

from src.models.cv import GeneratedCV


def _esc(value: str) -> str:
    return html.escape(value.strip())


def _section(title: str, body: str) -> str:
    return f'<section class="section"><h2>{_esc(title)}</h2>{body}</section>'


def render_cv_html(generated: GeneratedCV, template_path: str | Path | None = None) -> str:
    data = generated.data
    personal = data.personal
    contact = "".join(f"<span>{_esc(item)}</span>" for item in (personal.phone,
                      personal.email, personal.location, personal.linkedin) if item.strip())
    body = f'<header class="cv-header"><div><h1>{_esc(personal.full_name) or "Your Name"}</h1><p class="role">{_esc(personal.target_job_title or data.profile.profession or "Professional")}</p></div><div class="contact">{contact}</div></header>'
    if generated.summary.strip():
        body += _section("Professional Summary",
                         f"<p>{_esc(generated.summary)}</p>")
    if generated.competencies:
        body += _section("Core Competencies",
                         f'<p class="competencies">{" &nbsp;·&nbsp; ".join(_esc(item) for item in generated.competencies)}</p>')
    jobs = []
    for job in generated.experience:
        dates = f'{_esc(job.start_year)}{(" — " if job.start_year else "")}{"Present" if job.current else _esc(job.end_year)}'
        bullets = "".join(
            f"<li>{_esc(item)}</li>" for item in [*job.responsibilities, *job.achievements])
        details = "".join(f"<p>{_esc(item)}</p>" for item in (job.processes,
                          job.team_management, job.software) if item.strip())
        jobs.append(
            f'<div class="job"><div class="job-top"><div><div class="job-title">{_esc(job.designation)}</div><div class="job-company">{_esc(job.company)}{(" · " + _esc(job.location)) if job.location else ""}</div></div><div class="job-date">{dates}</div></div>{f"<ul>{bullets}</ul>" if bullets else ""}{details}</div>')
    if jobs:
        body += _section("Professional Experience", "".join(jobs))
    education = []
    certifications = []
    for item in data.education:
        if item.qualification or item.institution:
            details = " · ".join(_esc(value) for value in (
                item.specialization, item.institution, item.year) if value)
            education.append(
                f'<div class="edu"><strong>{_esc(item.qualification)}</strong><span>{details}</span></div>')
        if item.certification:
            certifications.append(
                f'<p><strong>{_esc(item.certification)}</strong>{(" · " + _esc(item.institution)) if item.institution else ""}{(" · " + _esc(item.year)) if item.year else ""}</p>')
    if education:
        body += _section("Education & Qualifications", "".join(education))
    if data.skills.software.strip():
        body += _section("Technical Skills",
                         f"<p>{_esc(data.skills.software)}</p>")
    if certifications:
        body += _section("Certifications", "".join(certifications))
    additional = [("Languages", data.additional.languages), ("Awards", data.additional.awards), ("Professional memberships",
                                                                                                 data.additional.memberships), ("Training", data.additional.training), ("Availability", data.additional.availability)]
    additional_body = "".join(
        f"<p><strong>{_esc(label)}:</strong> {_esc(value)}</p>" for label, value in additional if value.strip())
    if additional_body:
        body += _section("Additional Information", additional_body)
    path = Path(template_path or Path(
        __file__).parents[2] / "templates" / "cv.html")
    return path.read_text(encoding="utf-8").replace("{{CV_BODY}}", body)
