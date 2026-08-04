from __future__ import annotations

import unittest

from ohmjudge.models import GradeRecord
from ohmjudge.stats import pareto_frontier, summarize, wilson_interval


def record(
    model: str, correct: bool, cost: float, pack: str = "circuits"
) -> GradeRecord:
    return GradeRecord(
        task_id=f"{model}-{correct}-{cost}",
        provider="fixture",
        model=model,
        pack=pack,
        template="sample",
        correct=correct,
        error_type="correct" if correct else "wrong_value",
        expected_value=1.0,
        expected_unit="V",
        observed_value=1.0 if correct else 2.0,
        observed_unit="V",
        absolute_error=0.0 if correct else 1.0,
        response_text="",
        prompt="",
        latency_ms=100.0,
        usage={"input_tokens": 10, "output_tokens": 5},
        cost=cost,
    )


class StatsTests(unittest.TestCase):
    def test_wilson_interval_contains_rate(self) -> None:
        low, high = wilson_interval(7, 10)
        self.assertLess(low, 0.7)
        self.assertGreater(high, 0.7)

    def test_summary_groups_models_and_packs(self) -> None:
        result = summarize(
            [
                record("a", True, 0.2),
                record("a", False, 0.2, "signals"),
                record("b", True, 0.1),
            ]
        )
        self.assertEqual(2, result["model_count"])
        self.assertEqual(["circuits", "signals"], result["packs"])

    def test_pareto_removes_dominated_model(self) -> None:
        models = [
            {
                "provider": "p",
                "model": "cheap-good",
                "accuracy": 0.8,
                "total_cost": 1.0,
            },
            {"provider": "p", "model": "bad-deal", "accuracy": 0.7, "total_cost": 2.0},
            {
                "provider": "p",
                "model": "expensive-best",
                "accuracy": 0.9,
                "total_cost": 3.0,
            },
        ]
        names = {item["model"] for item in pareto_frontier(models)}
        self.assertEqual({"cheap-good", "expensive-best"}, names)

    def test_partial_cost_is_not_reported_as_total(self) -> None:
        priced = record("a", True, 0.2)
        missing = record("a", False, 0.0)
        missing.cost = None
        model = summarize([priced, missing])["models"][0]
        self.assertIsNone(model["total_cost"])
        self.assertFalse(model["cost_complete"])


if __name__ == "__main__":
    unittest.main()
