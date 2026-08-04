from __future__ import annotations

import hashlib
import json
from typing import Any

from .models import Task


ANSWER_INSTRUCTION = """
Return exactly one JSON object and no surrounding prose:
{"answer": <number>, "unit": "<unit requested in the question>"}
Use a decimal number, not an expression. Keep at least four significant digits.
""".strip()


def make_task(
    *,
    pack: str,
    template: str,
    seed: int,
    question: str,
    value: float | int | str,
    unit: str,
    difficulty: str,
    parameters: dict[str, Any],
    rel_tol: float = 1e-3,
    abs_tol: float = 1e-6,
) -> Task:
    identity = json.dumps(
        {
            "pack": pack,
            "template": template,
            "seed": seed,
            "parameters": parameters,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    short_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    return Task(
        id=f"{pack}.{template}.{short_hash}",
        pack=pack,
        template=template,
        seed=seed,
        prompt=f"{question.rstrip()}\n\n{ANSWER_INSTRUCTION}",
        expected={"kind": "numeric", "value": value, "unit": unit},
        tolerance={"relative": rel_tol, "absolute": abs_tol},
        metadata={
            "difficulty": difficulty,
            "parameters": parameters,
            "generator_version": 1,
        },
    )
