from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ohmjudge.pricing import Price, calculate_cost, load_prices


class PricingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.price = Price(
            provider="fixture",
            model="model",
            input_per_million=2.0,
            output_per_million=8.0,
        )

    def test_missing_usage_does_not_look_free(self) -> None:
        self.assertIsNone(calculate_cost({}, self.price))

    def test_cost_uses_reported_tokens(self) -> None:
        cost = calculate_cost(
            {"input_tokens": 1_000_000, "output_tokens": 500_000},
            self.price,
        )
        self.assertEqual(6.0, cost)

    def test_negative_price_is_rejected(self) -> None:
        payload = {
            "models": [
                {
                    "provider": "fixture",
                    "model": "model",
                    "input_per_million": -1,
                    "output_per_million": 2,
                }
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pricing.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_prices(str(path))


if __name__ == "__main__":
    unittest.main()
