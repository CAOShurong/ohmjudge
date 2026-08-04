from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ohmjudge.demo import build_demo
from ohmjudge.generate import generate_tasks
from ohmjudge.lab import render_lab


class ArtifactTests(unittest.TestCase):
    def test_lab_is_self_contained_and_no_api(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "lab.html"
            render_lab(generate_tasks(count=4, seed=3), output)
            html = output.read_text(encoding="utf-8")
        self.assertIn("No-API frontier-model bench", html)
        self.assertIn("localStorage", html)
        self.assertIn("capture protocol", html.lower())
        self.assertIn("retry_policy", html)
        self.assertNotIn("https://api.", html)
        self.assertNotIn("<script src=", html)

    def test_demo_labels_everything_synthetic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs = build_demo(directory, count=20, seed=4)
            report = outputs["report"].read_text(encoding="utf-8")
            pricing = json.loads(outputs["pricing"].read_text(encoding="utf-8"))
        self.assertIn("All model names", report)
        self.assertIn("synthetic", report.lower())
        self.assertIn("Fictional prices", pricing["notice"])

    def test_demo_produces_all_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs = build_demo(directory, count=8, seed=5)
            for path in outputs.values():
                self.assertTrue(path.exists(), path)
                self.assertGreater(path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
