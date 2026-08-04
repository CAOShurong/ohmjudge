from __future__ import annotations

import unittest

from ohmjudge.generate import generate_tasks
from ohmjudge.grade import grade_one
from ohmjudge.models import ModelResponse
from ohmjudge.parse import parse_answer


class ParseTests(unittest.TestCase):
    def test_json_inside_markdown_is_found(self) -> None:
        parsed = parse_answer('Result:\n```json\n{"answer": 3.5, "unit": "V"}\n```')
        self.assertEqual(3.5, parsed.value)
        self.assertEqual("V", parsed.unit)
        self.assertEqual("json", parsed.mode)

    def test_numeric_fallback(self) -> None:
        parsed = parse_answer("Answer: 1.25 kHz")
        self.assertEqual(1.25, parsed.value)
        self.assertEqual("kHz", parsed.unit)
        self.assertEqual("numeric_fallback", parsed.mode)

    def test_unparseable(self) -> None:
        parsed = parse_answer("This cannot be determined.")
        self.assertIsNotNone(parsed.error)


class GradeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = generate_tasks(pack_names=["circuits"], count=1, seed=18)[0]

    def response(self, text: str, error: str | None = None) -> ModelResponse:
        return ModelResponse(
            task_id=self.task.id,
            provider="test",
            model="fixture",
            text=text,
            error=error,
        )

    def test_exact_answer_passes(self) -> None:
        expected = self.task.expected
        grade = grade_one(
            self.task,
            self.response(
                f'{{"answer": {expected["value"]}, "unit": "{expected["unit"]}"}}'
            ),
        )
        self.assertTrue(grade.correct)
        self.assertEqual("correct", grade.error_type)

    def test_convertible_unit_passes(self) -> None:
        task = next(
            task
            for task in generate_tasks(pack_names=["communications"], count=20, seed=9)
            if task.expected["unit"] == "Mbit/s"
        )
        expected = float(task.expected["value"])
        response = ModelResponse(
            task_id=task.id,
            provider="test",
            model="fixture",
            text=f'{{"answer": {expected * 1e6}, "unit": "bit/s"}}',
        )
        self.assertTrue(grade_one(task, response).correct)

    def test_unknown_unit_is_separate_error(self) -> None:
        grade = grade_one(
            self.task,
            self.response('{"answer": 1, "unit": "bananas"}'),
        )
        self.assertFalse(grade.correct)
        self.assertEqual("unknown_unit", grade.error_type)

    def test_incompatible_unit_is_separate_error(self) -> None:
        grade = grade_one(
            self.task,
            self.response('{"answer": 1, "unit": "s"}'),
        )
        self.assertFalse(grade.correct)
        self.assertEqual("incompatible_unit", grade.error_type)

    def test_missing_unit_fails_contract(self) -> None:
        grade = grade_one(
            self.task,
            self.response('{"answer": 1}'),
        )
        self.assertFalse(grade.correct)
        self.assertEqual("missing_unit", grade.error_type)

    def test_empty_response_is_separate_error(self) -> None:
        grade = grade_one(self.task, self.response("  "))
        self.assertEqual("empty_response", grade.error_type)

    def test_text_without_number_is_parse_error(self) -> None:
        grade = grade_one(
            self.task,
            self.response("This cannot be determined."),
        )
        self.assertEqual("parse_error", grade.error_type)

    def test_request_error_is_preserved(self) -> None:
        grade = grade_one(
            self.task,
            self.response("", error="HTTP 429"),
        )
        self.assertEqual("request_error", grade.error_type)
        self.assertEqual("HTTP 429", grade.details["request_error"])

    def test_wrong_value_reports_absolute_error(self) -> None:
        unit = self.task.expected["unit"]
        grade = grade_one(
            self.task,
            self.response(f'{{"answer": 999999, "unit": "{unit}"}}'),
        )
        self.assertEqual("wrong_value", grade.error_type)
        self.assertGreater(grade.absolute_error or 0, 0)


if __name__ == "__main__":
    unittest.main()
