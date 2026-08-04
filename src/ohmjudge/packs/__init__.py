from __future__ import annotations

from collections.abc import Callable
from random import Random

from ..models import Task
from . import circuits, communications, control, signals

TaskGenerator = Callable[[Random, int], Task]

PACKS: dict[str, tuple[TaskGenerator, ...]] = {
    "circuits": circuits.GENERATORS,
    "signals": signals.GENERATORS,
    "control": control.GENERATORS,
    "communications": communications.GENERATORS,
}


def available_packs() -> tuple[str, ...]:
    return tuple(PACKS)
