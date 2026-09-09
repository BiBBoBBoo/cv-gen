from __future__ import annotations

from src.models.cv import CVData, GeneratedCV
from src.services.ai_rewriter import AIRefinementError, refine_cv_with_ai
from src.services.ats_optimizer import optimize_for_ats
from src.services.cv_rewriter import generate_local_cv


def generate_cv(data: CVData, use_ai: bool = False) -> GeneratedCV:
    generated = generate_local_cv(data)
    if use_ai:
        try:
            generated = refine_cv_with_ai(generated)
        except AIRefinementError:
            generated.status = "Local refinement used"
    return optimize_for_ats(generated)
