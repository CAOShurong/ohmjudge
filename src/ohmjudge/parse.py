from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .units import finite_number


@dataclass(frozen=True, slots=True)
class ParsedAnswer:
    value: float | str | None
    unit: str | None
    mode: str
    error: str | None = None


def _json_objects(text: str) -> list[str]:
    objects: list[str] = []
    start: int | None = None
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                objects.append(text[start : index + 1])
                start = None
    return objects


def parse_answer(text: str) -> ParsedAnswer:
    for candidate in _json_objects(text):
        try:
            data: Any = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict) or "answer" not in data:
            continue
        number = finite_number(data["answer"])
        value: float | str | None = number
        if number is None and isinstance(data["answer"], str):
            value = data["answer"].strip()
        unit = data.get("unit")
        return ParsedAnswer(
            value=value,
            unit=str(unit).strip() if unit is not None else None,
            mode="json",
        )

    compact = " ".join(text.strip().split())
    match = re.search(
        r"(?:answer\s*[:=]\s*)?"
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"
        r"\s*([A-Za-z%Ωµμ/]+(?:/[A-Za-z]+)?)?",
        compact,
        flags=re.IGNORECASE,
    )
    if match:
        return ParsedAnswer(
            value=float(match.group(1)),
            unit=match.group(2),
            mode="numeric_fallback",
        )
    return ParsedAnswer(
        value=None,
        unit=None,
        mode="none",
        error="no JSON object or numeric answer found",
    )
