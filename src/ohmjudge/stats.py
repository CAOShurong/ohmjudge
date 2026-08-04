from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable
from statistics import median
from typing import Any

from .models import GradeRecord


def wilson_interval(successes: int, total: int, z: float = 1.959964) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 0.0)
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    margin = (
        z
        * math.sqrt(
            proportion * (1.0 - proportion) / total
            + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return (max(0.0, center - margin), min(1.0, center + margin))


def _aggregate(records: list[GradeRecord]) -> dict[str, Any]:
    total = len(records)
    correct = sum(record.correct for record in records)
    low, high = wilson_interval(correct, total)
    latencies = [
        record.latency_ms for record in records if record.latency_ms is not None
    ]
    costs = [record.cost for record in records if record.cost is not None]
    input_tokens = sum(
        record.usage.get("input_tokens", record.usage.get("prompt_tokens", 0))
        for record in records
    )
    output_tokens = sum(
        record.usage.get("output_tokens", record.usage.get("completion_tokens", 0))
        for record in records
    )
    complete_cost = total > 0 and len(costs) == total
    total_cost = sum(costs) if complete_cost else None
    error_counts: dict[str, int] = defaultdict(int)
    for record in records:
        error_counts[record.error_type] += 1
    return {
        "total": total,
        "correct": correct,
        "accuracy": correct / total if total else 0.0,
        "ci95_low": low,
        "ci95_high": high,
        "median_latency_ms": median(latencies) if latencies else None,
        "total_cost": total_cost,
        "cost_complete": complete_cost,
        "cost_per_correct": (
            total_cost / correct
            if total_cost is not None and correct
            else None
        ),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "errors": dict(sorted(error_counts.items())),
    }


def summarize(records: Iterable[GradeRecord]) -> dict[str, Any]:
    materialized = list(records)
    by_model: dict[tuple[str, str], list[GradeRecord]] = defaultdict(list)
    by_model_pack: dict[tuple[str, str, str], list[GradeRecord]] = defaultdict(list)
    for record in materialized:
        by_model[(record.provider, record.model)].append(record)
        by_model_pack[(record.provider, record.model, record.pack)].append(record)

    models = []
    for (provider, model), group in sorted(by_model.items()):
        row = {"provider": provider, "model": model, **_aggregate(group)}
        row["packs"] = {
            pack: _aggregate(by_model_pack[(provider, model, pack)])
            for pack in sorted({record.pack for record in group})
        }
        models.append(row)

    return {
        "models": models,
        "record_count": len(materialized),
        "model_count": len(models),
        "packs": sorted({record.pack for record in materialized}),
        "pareto": pareto_frontier(models),
    }


def pareto_frontier(models: list[dict[str, Any]]) -> list[dict[str, str]]:
    eligible = [
        model
        for model in models
        if model.get("total_cost") is not None
    ]
    frontier: list[dict[str, str]] = []
    for candidate in eligible:
        dominated = any(
            other is not candidate
            and other["total_cost"] <= candidate["total_cost"]
            and other["accuracy"] >= candidate["accuracy"]
            and (
                other["total_cost"] < candidate["total_cost"]
                or other["accuracy"] > candidate["accuracy"]
            )
            for other in eligible
        )
        if not dominated:
            frontier.append(
                {
                    "provider": str(candidate["provider"]),
                    "model": str(candidate["model"]),
                }
            )
    return sorted(frontier, key=lambda item: (item["provider"], item["model"]))
