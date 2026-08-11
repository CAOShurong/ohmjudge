from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ohmjudge.generate import generate_tasks, suite_commitment
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

    def test_runner_binds_every_response_to_the_task_suite(self) -> None:
        tasks = generate_tasks(count=2, seed=8)
        with tempfile.TemporaryDirectory() as directory:
            replay = Path(directory) / "replay.jsonl"
            write_jsonl(
                replay,
                [
                    ModelResponse(
                        task_id=task.id,
                        provider="fixture",
                        model="model",
                        text="response",
                    ).to_dict()
                    for task in tasks
                ],
            )

            responses = run_tasks(
                tasks,
                provider=ReplayProvider(replay),
                model="model",
            )

        commitment = suite_commitment(tasks)
        self.assertTrue(responses)
        self.assertTrue(
            all(
                response.metadata["suite_commitment"] == commitment
                for response in responses
            )
        )

    def test_runner_rejects_replay_from_a_different_suite(self) -> None:
        task = generate_tasks(count=1, seed=11)[0]
        wrong_commitment = suite_commitment(generate_tasks(count=1, seed=12))
        with tempfile.TemporaryDirectory() as directory:
            replay = Path(directory) / "replay.jsonl"
            write_jsonl(
                replay,
                [
                    ModelResponse(
                        task_id=task.id,
                        provider="fixture",
                        model="model",
                        text="response",
                        metadata={"suite_commitment": wrong_commitment},
                    ).to_dict()
                ],
            )

            with self.assertRaisesRegex(ValueError, "different task suite"):
                run_tasks(
                    [task],
                    provider=ReplayProvider(replay),
                    model="model",
                )


if __name__ == "__main__":
    unittest.main()
