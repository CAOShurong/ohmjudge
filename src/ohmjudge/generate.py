from __future__ import annotations

import hashlib
import random
from collections.abc import Iterable

from .io import content_hash
from .models import Task
from .packs import PACKS, available_packs


def _derived_seed(master_seed: int, index: int, pack: str, template: str) -> int:
    material = f"ohmjudge:v1:{master_seed}:{index}:{pack}:{template}".encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def generate_tasks(
    *,
    pack_names: Iterable[str] | None = None,
    count: int = 40,
    seed: int = 2026,
) -> list[Task]:
    if count < 1:
        raise ValueError("count must be at least 1")
    selected = tuple(pack_names or available_packs())
    if not selected:
        raise ValueError("select at least one pack")
    unknown = [name for name in selected if name not in PACKS]
    if unknown:
        raise ValueError(f"unknown packs: {', '.join(unknown)}")

    tasks: list[Task] = []
    for index in range(count):
        pack = selected[index % len(selected)]
        generators = PACKS[pack]
        cycle = index // len(selected)
        generator = generators[cycle % len(generators)]
        task_seed = _derived_seed(seed, index, pack, generator.__name__)
        tasks.append(generator(random.Random(task_seed), task_seed))

    ids = {task.id for task in tasks}
    if len(ids) != len(tasks):
        raise RuntimeError("generator produced duplicate task IDs")
    return tasks


def suite_commitment(tasks: Iterable[Task]) -> str:
    return content_hash(task.to_dict() for task in tasks)
