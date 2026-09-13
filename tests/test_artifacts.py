from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

from ohmjudge.cli import main
from ohmjudge.collector import render_collector
from ohmjudge.demo import build_demo
from ohmjudge.generate import generate_tasks, suite_commitment
from ohmjudge.io import read_jsonl, write_jsonl
from ohmjudge.lab import render_lab


class ArtifactTests(unittest.TestCase):
    def test_jsonl_reader_accepts_a_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.jsonl"
            path.write_bytes(b'\xef\xbb\xbf{"id":"t1","ok":true}\n')
            records = list(read_jsonl(path))
        self.assertEqual([{"id": "t1", "ok": True}], records)

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

    def test_blind_collector_contains_public_tasks_but_no_answer_key(self) -> None:
        tasks = generate_tasks(count=4, seed=13)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "collector.html"
            render_collector(tasks, output)
            html = output.read_text(encoding="utf-8")

        match = re.search(r"const TASKS=(.*?),COMMITMENT=", html)
        self.assertIsNotNone(match)
        embedded = json.loads(match.group(1))
        self.assertEqual(4, len(embedded))
        self.assertTrue(all("expected" not in task for task in embedded))
        self.assertTrue(all("tolerance" not in task for task in embedded))
        self.assertTrue(
            all("parameters" not in task.get("metadata", {}) for task in embedded)
        )
        self.assertIn(suite_commitment(tasks), html)
        self.assertIn("ANSWER-FREE - COLLECTION ONLY", html)
        self.assertIn("Import checkpoint", html)
        self.assertIn("suite_commitment:COMMITMENT", html)
        self.assertIn("function protocolFor(name)", html)
        self.assertIn("protocol=protocolFor(name)", html)
        self.assertNotIn("state.protocol.", html)
        self.assertNotIn("Reveal reference", html)
        self.assertNotIn("function assess", html)
        self.assertNotIn("fetch(", html)
        self.assertNotIn("XMLHttpRequest", html)
        self.assertNotIn("<script src=", html)

    def test_collect_command_builds_the_answer_free_artifact(self) -> None:
        tasks = generate_tasks(count=3, seed=19)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_file = root / "tasks.private.jsonl"
            output = root / "collector.html"
            write_jsonl(task_file, (task.to_dict() for task in tasks))

            code = main(
                [
                    "collect",
                    "--tasks",
                    str(task_file),
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(0, code)
            self.assertTrue(output.exists())
            self.assertNotIn('"expected":', output.read_text(encoding="utf-8"))

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
            self.assertIn("collector", outputs)


if __name__ == "__main__":
    unittest.main()
