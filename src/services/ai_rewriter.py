from __future__ import annotations

import json
import os

from openai import OpenAI
import streamlit as st

from src.models.cv import GeneratedCV


class AIRefinementError(RuntimeError):
    pass


def refine_cv_with_ai(generated: GeneratedCV) -> GeneratedCV:
    api_key = st.secrets.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise AIRefinementError("OPENAI_API_KEY is not configured")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    source = {
        "summary": generated.summary,
        "experience": [
            {
                "id": job.id,
                "responsibilities": job.responsibilities,
                "achievements": job.achievements,
            }
            for job in generated.experience
        ],
    }
    instructions = (
        "Refine only the wording of this CV. Preserve every fact exactly. Never invent or "
        "remove achievements, metrics, skills, qualifications, technologies, responsibilities, "
        "dates, companies, job titles, or bullet points. Return JSON with exactly two keys: "
        "summary (string) and experience (array of objects with id, responsibilities, and "
        "achievements arrays). Keep every id and preserve each source array length.\n\n"
        f"SOURCE CV:\n{json.dumps(source, ensure_ascii=True)}"
    )
    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            input=instructions,
            store=False,
        )
        refined = json.loads(response.output_text)
    except Exception as exc:
        raise AIRefinementError("AI request failed") from exc

    try:
        summary = str(refined["summary"])
        by_id = {item["id"]: item for item in refined["experience"]}
        for job in generated.experience:
            item = by_id[job.id]
            if len(item["responsibilities"]) != len(job.responsibilities) or len(item["achievements"]) != len(job.achievements):
                raise ValueError("AI changed the source bullet count")
            job.responsibilities = [str(value)
                                    for value in item["responsibilities"]]
            job.achievements = [str(value) for value in item["achievements"]]
        generated.summary = summary
        generated.status = "AI refinement used"
        return generated
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AIRefinementError("AI returned an unusable refinement") from exc
