from __future__ import annotations

from src.models.cv import GeneratedCV


def optimize_for_ats(generated: GeneratedCV) -> GeneratedCV:
    """Keep supplied keywords visible without adding unsupported terms."""
    generated.competencies = list(dict.fromkeys(
        item.strip() for item in generated.competencies if item.strip()))[:16]
    return generated
