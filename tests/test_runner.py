from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ohmjudge.generate import generate_tasks
from ohmjudge.io import write_jsonl
from ohmjudge.models import ModelResponse
from ohmjudge.providers import ReplayProvider
from ohmjudge.runner import run_tasks


class RunnerTests(unittest.TestCase):
    def test_resume_rejects_a_different_model(self) -> None:
        task = generate_tasks(count=1, seed=3)[0]
        with tempfile.TemporaryDirectory() as directory:
            resume = Path(directory) / "resume.jsonl"
            replay = Path(directory) / "replay.jsonl"
            write_jsonl(
                resume,
                [
                    ModelResponse(
                        task_id=task.id,
                        provider="fixture",
                        model="old-model",
                        text='{"answer": 1, "unit": "V"}',
                    ).to_dict()
                ],
            )
            write_jsonl(replay, [])
            with self.assertRaises(ValueError):
                run_tasks(
                    [task],
                    provider=ReplayProvider(replay),
                    model="new-model",
                    resume_from=resume,
                )


if __name__ == "__main__":
    unittest.main()
