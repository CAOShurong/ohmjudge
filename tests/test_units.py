from __future__ import annotations

import unittest

from ohmjudge.generate import generate_tasks
from ohmjudge.grade import grade_one
from ohmjudge.models import ModelResponse
from ohmjudge.units import convert_value, lookup_unit


class UnitTests(unittest.TestCase):
    def test_every_generated_expected_unit_is_registered(self) -> None:
        tasks = generate_tasks(count=500, seed=9127)
        unknown = {
            str(task.expected["unit"])
            for task in tasks
            if lookup_unit(str(task.expected["unit"])) is None
        }
        self.assertEqual(set(), unknown)
        for task in tasks:
            response = ModelResponse(
                task_id=task.id,
                provider="fixture",
                model="exact",
                text=(
                    f'{{"answer": {task.expected["value"]}, '
                    f'"unit": "{task.expected["unit"]}"}}'
                ),
            )
            self.assertTrue(grade_one(task, response).correct, task.id)

    def test_milli_and_mega_ohm_keep_case_sensitive_prefixes(self) -> None:
        self.assertEqual(1e-3, convert_value(1.0, "mΩ", "ohm"))
        self.assertEqual(1e6, convert_value(1.0, "MΩ", "ohm"))
        self.assertEqual(1e-3, convert_value(1.0, "mohm", "ohm"))
        self.assertEqual(1e6, convert_value(1.0, "Mohm", "ohm"))
        self.assertEqual(1e6, convert_value(1.0, "MOhm", "ohm"))
        self.assertEqual(1e6, convert_value(1.0, "MOHM", "ohm"))
        self.assertEqual(1e-3, convert_value(1.0, "mOhm", "ohm"))

    def test_extended_units_convert(self) -> None:
        self.assertEqual(1000.0, convert_value(1.0, "kW", "W"))
        self.assertAlmostEqual(1000.0, convert_value(1.0, "mH", "uH") or 0.0)
        self.assertEqual(3600.0, convert_value(1.0, "hours", "s"))


if __name__ == "__main__":
    unittest.main()
