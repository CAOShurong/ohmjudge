from __future__ import annotations

import math
from typing import Any

from .models import GradeRecord


def model_selector(provider: str, model: str) -> str:
    return f"{provider}/{model}"


def _exact_mcnemar_p(baseline_only: int, challenger_only: int) -> float:
    discordant = baseline_only + challenger_only
    if discordant == 0:
        return 1.0
    tail = min(baseline_only, challenger_only)
    probability = sum(math.comb(discordant, index) for index in range(tail + 1)) / (
        2**discordant
    )
    return min(1.0, 2.0 * probability)


def _paired_counts(
    baseline: dict[str, GradeRecord],
    challenger: dict[str, GradeRecord],
) -> dict[str, Any]:
    shared = sorted(set(baseline) & set(challenger))
    both = sum(baseline[key].correct and challenger[key].correct for key in shared)
    baseline_only = sum(
        baseline[key].correct and not challenger[key].correct for key in shared
    )
    challenger_only = sum(
        challenger[key].correct and not baseline[key].correct for key in shared
    )
    neither = len(shared) - both - baseline_only - challenger_only
    baseline_accuracy = (both + baseline_only) / len(shared) if shared else 0.0
    challenger_accuracy = (both + challenger_only) / len(shared) if shared else 0.0
    return {
        "paired_tasks": len(shared),
        "both_correct": both,
        "baseline_only_correct": baseline_only,
        "challenger_only_correct": challenger_only,
        "neither_correct": neither,
        "baseline_accuracy": baseline_accuracy,
        "challenger_accuracy": challenger_accuracy,
        "accuracy_delta": challenger_accuracy - baseline_accuracy,
        "mcnemar_exact_p": _exact_mcnemar_p(baseline_only, challenger_only),
    }


def compare_models(
    records: list[GradeRecord],
    *,
    baseline_provider: str,
    baseline_model: str,
    challenger_provider: str,
    challenger_model: str,
) -> dict[str, Any]:
    def select(provider: str, model: str) -> dict[str, GradeRecord]:
        selected: dict[str, GradeRecord] = {}
        for record in records:
            if record.provider != provider or record.model != model:
                continue
            if record.task_id in selected:
                raise ValueError(
                    f"duplicate grade for {provider}/{model}/{record.task_id}"
                )
            selected[record.task_id] = record
        return selected

    baseline = select(baseline_provider, baseline_model)
    challenger = select(challenger_provider, challenger_model)
    if not baseline:
        raise ValueError(
            "no grades found for baseline "
            f"{model_selector(baseline_provider, baseline_model)}"
        )
    if not challenger:
        raise ValueError(
            "no grades found for challenger "
            f"{model_selector(challenger_provider, challenger_model)}"
        )

    overall = _paired_counts(baseline, challenger)
    shared = set(baseline) & set(challenger)
    packs = sorted(
        {baseline[key].pack for key in shared}
        | {challenger[key].pack for key in shared}
    )
    by_pack: dict[str, Any] = {}
    for pack in packs:
        baseline_pack = {
            key: record for key, record in baseline.items() if record.pack == pack
        }
        challenger_pack = {
            key: record for key, record in challenger.items() if record.pack == pack
        }
        by_pack[pack] = _paired_counts(baseline_pack, challenger_pack)

    warnings: list[str] = []
    if len(baseline) != len(challenger) or len(shared) != len(baseline):
        warnings.append(
            "The models do not have identical task coverage; only shared task IDs "
            "are compared."
        )
    discordant = overall["baseline_only_correct"] + overall["challenger_only_correct"]
    if discordant < 20:
        warnings.append(
            "Fewer than 20 discordant pairs make the exact test low-powered; "
            "treat the p-value cautiously."
        )

    delta = float(overall["accuracy_delta"])
    winner = "challenger" if delta > 0 else "baseline" if delta < 0 else "tie"
    return {
        "baseline": {
            "provider": baseline_provider,
            "model": baseline_model,
            "records": len(baseline),
        },
        "challenger": {
            "provider": challenger_provider,
            "model": challenger_model,
            "records": len(challenger),
        },
        "winner_by_observed_accuracy": winner,
        "statistically_clear_at_0_05": overall["mcnemar_exact_p"] < 0.05,
        "overall": overall,
        "by_pack": by_pack,
        "warnings": warnings,
    }
