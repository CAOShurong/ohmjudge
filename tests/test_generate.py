from __future__ import annotations

import unittest

from ohmjudge.generate import generate_tasks, suite_commitment
from ohmjudge.packs import PACKS


class GenerateTests(unittest.TestCase):
    def test_same_seed_is_byte_stable(self) -> None:
        first = generate_tasks(count=50, seed=99)
        second = generate_tasks(count=50, seed=99)
        self.assertEqual(
            [task.to_dict() for task in first],
            [task.to_dict() for task in second],
        )
        self.assertEqual(suite_commitment(first), suite_commitment(second))

    def test_different_seed_changes_commitment(self) -> None:
        first = generate_tasks(count=20, seed=1)
        second = generate_tasks(count=20, seed=2)
        self.assertNotEqual(suite_commitment(first), suite_commitment(second))

    def test_all_templates_are_reached(self) -> None:
        template_count = sum(len(generators) for generators in PACKS.values())
        tasks = generate_tasks(count=template_count, seed=7)
        reached = {(task.pack, task.template) for task in tasks}
        expected = {
            (pack, generator.__name__)
            for pack, generators in PACKS.items()
            for generator in generators
        }
        self.assertEqual(expected, reached)

    def test_ids_are_unique(self) -> None:
        tasks = generate_tasks(count=200, seed=2026)
        self.assertEqual(len(tasks), len({task.id for task in tasks}))

    def test_public_record_hides_answer_and_parameters(self) -> None:
        task = generate_tasks(count=1, seed=4)[0]
        public = task.to_dict(public=True)
        self.assertNotIn("expected", public)
        self.assertNotIn("tolerance", public)
        self.assertNotIn("parameters", public["metadata"])
        self.assertIn("answer_contract", public)

    def test_rejects_unknown_pack(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown packs"):
            generate_tasks(pack_names=["not-a-pack"])


if __name__ == "__main__":
    unittest.main()
