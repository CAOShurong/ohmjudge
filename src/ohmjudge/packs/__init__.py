from __future__ import annotations

from collections.abc import Callable
from random import Random

from ..models import Task
from . import (
    circuits,
    communications,
    control,
    digital,
    electromagnetics,
    electronics,
    embedded,
    instrumentation,
    power,
    signals,
)

TaskGenerator = Callable[[Random, int], Task]

PACKS: dict[str, tuple[TaskGenerator, ...]] = {
    "circuits": circuits.GENERATORS,
    "signals": signals.GENERATORS,
    "control": control.GENERATORS,
    "communications": communications.GENERATORS,
    "electronics": electronics.GENERATORS,
    "power": power.GENERATORS,
    "electromagnetics": electromagnetics.GENERATORS,
    "digital": digital.GENERATORS,
    "embedded": embedded.GENERATORS,
    "instrumentation": instrumentation.GENERATORS,
}


def available_packs() -> tuple[str, ...]:
    return tuple(PACKS)
