import json
import unittest
from unittest.mock import patch

from src.models.cv import CVData, cv_from_dict
from src.services.cv_generator import generate_cv
from src.services.cv_rewriter import generate_local_cv, rewrite_bullet
from src.services.storage import draft_json, load_draft_json
from src.utils.formatting import render_cv_html


def sample_data() -> CVData:
    return cv_from_dict({
        "personal": {"full_name": "Test Applicant", "target_job_title": "Accounts Manager"},
        "profile": {"years": "10", "profession": "Accounting professional", "industry": "Finance", "description": "Worked on accounts and prepared reports for management."},
        "experiences": [
            {"company": "Example Finance", "designation": "Accounts Manager", "start_year": "2018", "current": True,
                "responsibilities": ["worked on accounts"], "achievements": ["prepared reports for management"]},
            {"company": "Earlier Finance", "designation": "Accountant", "start_year": "2014",
                "end_year": "2018", "responsibilities": ["did reconciliation"], "achievements": []},
        ],
        "skills": {"functional": "Financial Accounting, Reporting"},
        "education": [{"qualification": "Bachelor of Commerce", "specialization": "Accounting", "institution": "Example University", "year": "2010"}],
    })


class CVServiceTests(unittest.TestCase):
    def test_rewriter_preserves_meaningful_text(self):
        self.assertEqual(rewrite_bullet(
            "worked on accounts"), "Managed accounts.")
        self.assertEqual(rewrite_bullet("I did reconciliation"),
                         "Performed reconciliation.")

    def test_sample_generates_local_cv(self):
        generated = generate_cv(sample_data())
        self.assertEqual(generated.status, "Local refinement used")
        self.assertEqual(len(generated.experience), 2)
        self.assertIn("Financial Accounting", generated.competencies)

    def test_draft_round_trip(self):
        data = sample_data()
        restored = load_draft_json(draft_json(data))
        self.assertEqual(restored.personal.full_name, "Test Applicant")
        self.assertEqual(len(restored.experiences), 2)

    def test_blank_cv_is_supported(self):
        self.assertIsInstance(cv_from_dict({}), CVData)
        self.assertEqual(len(cv_from_dict({}).experiences), 1)

    def test_ai_failure_falls_back_to_local(self):
        with patch.dict("os.environ", {}, clear=True):
            generated = generate_cv(sample_data(), use_ai=True)
        self.assertEqual(generated.status, "Local refinement used")

    def test_ai_success_uses_one_responses_call(self):
        data = sample_data()
        local = generate_local_cv(data)
        response = type("Response", (), {
            "output_text": json.dumps({
                "summary": "Refined summary",
                "experience": [
                    {
                        "id": job.id,
                        "responsibilities": job.responsibilities,
                        "achievements": job.achievements,
                    }
                    for job in local.experience
                ],
            })
        })()
        client = patch("src.services.ai_rewriter.OpenAI").start()
        self.addCleanup(patch.stopall)
        client.return_value.responses.create.return_value = response
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=True):
            generated = generate_cv(data, use_ai=True)
        self.assertEqual(generated.status, "AI refinement used")
        client.return_value.responses.create.assert_called_once()
        self.assertFalse(
            client.return_value.responses.create.call_args.kwargs["store"])

    def test_preview_contains_print_control_and_sections(self):
        html = render_cv_html(generate_cv(sample_data()))
        self.assertIn("Print / Save PDF", html)
        self.assertIn("Professional Experience", html)
        self.assertIn("Education &amp; Qualifications", html)
        self.assertIn("<title></title>", html)


if __name__ == "__main__":
    unittest.main()
