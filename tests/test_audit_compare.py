from __future__ import annotations

import unittest

from ohmjudge.audit import audit_experiment
from ohmjudge.compare import compare_models
from ohmjudge.generate import generate_tasks
from ohmjudge.grade import grade_responses
from ohmjudge.models import GradeRecord, ModelResponse


def _record(
    task_id: str,
    model: str,
    correct: bool,
    *,
    pack: str = "circuits",
) -> GradeRecord:
    return GradeRecord(
        task_id=task_id,
        provider="fixture",
        model=model,
        pack=pack,
        template="template",
        correct=correct,
        error_type="correct" if correct else "wrong_value",
        expected_value=1.0,
        expected_unit="V",
        observed_value=1.0 if correct else 2.0,
        observed_unit="V",
        absolute_error=0.0 if correct else 1.0,
        response_text="",
        prompt="",
        latency_ms=None,
        usage={},
    )


class AuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tasks = generate_tasks(count=10, seed=42)
        self.responses = [
            ModelResponse(
                task_id=task.id,
                provider="manual-web",
                model="fixture",
                text=(
                    f'{{"answer": {task.expected["value"]}, '
                    f'"unit": "{task.expected["unit"]}"}}'
                ),
            )
            for task in self.tasks
        ]

    def test_complete_recomputed_experiment_passes(self) -> None:
        grades = grade_responses(self.tasks, self.responses)
        result = audit_experiment(
            self.tasks,
            responses=self.responses,
            grades=grades,
            require_complete=True,
        )
        self.assertEqual("pass", result["status"])
        self.assertTrue(result["grades_match_recomputation"])

    def test_tampered_grade_is_detected(self) -> None:
        grades = grade_responses(self.tasks, self.responses)
        grades[0].correct = False
        result = audit_experiment(
            self.tasks,
            responses=self.responses,
            grades=grades,
        )
        self.assertEqual("fail", result["status"])
        self.assertFalse(result["grades_match_recomputation"])

    def test_incomplete_coverage_can_be_strict(self) -> None:
        result = audit_experiment(
            self.tasks,
            responses=self.responses[:-1],
            require_complete=True,
        )
        self.assertEqual("fail", result["status"])

    def test_capture_protocol_can_be_strict(self) -> None:
        result = audit_experiment(
            self.tasks,
            responses=self.responses,
            require_protocol=True,
        )
        self.assertEqual("fail", result["status"])
        self.assertIn("surface", result["protocol_coverage"][0]["missing"])

        for response in self.responses:
            response.metadata = {
                "captured_at": "2026-08-05T00:00:00Z",
                "surface": "web",
                "settings": "default",
                "tools": "disabled",
                "retry_policy": "none",
            }
        result = audit_experiment(
            self.tasks,
            responses=self.responses,
            require_protocol=True,
        )
        self.assertEqual("pass", result["status"])
        self.assertEqual(len(self.responses), result["responses_with_complete_protocol"])


class CompareTests(unittest.TestCase):
    def test_paired_counts_and_direction(self) -> None:
        records = [
            _record("1", "base", True),
            _record("2", "base", True),
            _record("3", "base", False, pack="signals"),
            _record("4", "base", False, pack="signals"),
            _record("1", "new", True),
            _record("2", "new", False),
            _record("3", "new", True, pack="signals"),
            _record("4", "new", True, pack="signals"),
        ]
        result = compare_models(
            records,
            baseline_provider="fixture",
            baseline_model="base",
            challenger_provider="fixture",
            challenger_model="new",
        )
        self.assertEqual(4, result["overall"]["paired_tasks"])
        self.assertEqual(1, result["overall"]["baseline_only_correct"])
        self.assertEqual(2, result["overall"]["challenger_only_correct"])
        self.assertEqual("challenger", result["winner_by_observed_accuracy"])

    def test_missing_model_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "no grades found"):
            compare_models(
                [_record("1", "base", True)],
                baseline_provider="fixture",
                baseline_model="base",
                challenger_provider="fixture",
                challenger_model="missing",
            )


if __name__ == "__main__":
    unittest.main()
