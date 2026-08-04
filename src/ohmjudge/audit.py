from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from .generate import suite_commitment
from .grade import grade_responses
from .io import canonical_json
from .models import GradeRecord, ModelResponse, Task
from .pricing import Price
from .units import finite_number, lookup_unit


def _response_key(response: ModelResponse) -> tuple[str, str, str]:
    return (response.provider, response.model, response.task_id)


def _grade_key(grade: GradeRecord) -> tuple[str, str, str]:
    return (grade.provider, grade.model, grade.task_id)


def audit_experiment(
    tasks: list[Task],
    *,
    responses: list[ModelResponse] | None = None,
    grades: list[GradeRecord] | None = None,
    prices: dict[tuple[str, str], Price] | None = None,
    require_complete: bool = False,
    require_protocol: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    task_ids: set[str] = set()
    templates: set[tuple[str, str]] = set()

    for task in tasks:
        if task.id in task_ids:
            errors.append(f"duplicate task id: {task.id}")
        task_ids.add(task.id)
        templates.add((task.pack, task.template))
        expected = finite_number(task.expected.get("value"))
        if expected is None:
            errors.append(f"{task.id}: expected value is not finite numeric data")
        expected_unit = str(task.expected.get("unit", ""))
        if lookup_unit(expected_unit) is None:
            errors.append(f"{task.id}: unknown expected unit {expected_unit!r}")
        relative = float(task.tolerance.get("relative", 0.0))
        absolute = float(task.tolerance.get("absolute", 0.0))
        if (
            not math.isfinite(relative)
            or not math.isfinite(absolute)
            or relative < 0
            or absolute < 0
        ):
            errors.append(f"{task.id}: tolerances must be finite and non-negative")

    response_rows = responses or []
    response_keys: set[tuple[str, str, str]] = set()
    response_models: dict[tuple[str, str], set[str]] = defaultdict(set)
    protocol_fields = (
        "captured_at",
        "surface",
        "settings",
        "tools",
        "retry_policy",
    )
    protocol_missing: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    protocol_complete = 0
    request_errors = 0
    for response in response_rows:
        key = _response_key(response)
        if key in response_keys:
            errors.append(
                "duplicate response: "
                f"{response.provider}/{response.model}/{response.task_id}"
            )
        response_keys.add(key)
        if response.task_id not in task_ids:
            errors.append(f"response references unknown task: {response.task_id}")
        response_models[(response.provider, response.model)].add(response.task_id)
        missing_fields = [
            field
            for field in protocol_fields
            if response.metadata.get(field) in (None, "")
        ]
        if missing_fields:
            for field in missing_fields:
                protocol_missing[(response.provider, response.model)][field] += 1
        else:
            protocol_complete += 1
        request_errors += response.error is not None

    coverage: list[dict[str, Any]] = []
    for (provider, model), answered in sorted(response_models.items()):
        missing = sorted(task_ids - answered)
        coverage.append(
            {
                "provider": provider,
                "model": model,
                "answered": len(answered),
                "expected": len(tasks),
                "complete": not missing,
                "missing_task_ids": missing,
            }
        )
        if missing:
            message = (
                f"{provider}/{model}: missing {len(missing)} of {len(tasks)} responses"
            )
            (errors if require_complete else warnings).append(message)

    protocol_coverage: list[dict[str, Any]] = []
    for (provider, model), missing in sorted(protocol_missing.items()):
        row = {
            "provider": provider,
            "model": model,
            "responses": len(response_models[(provider, model)]),
            "missing": dict(sorted(missing.items())),
        }
        protocol_coverage.append(row)
        missing_summary = ", ".join(
            f"{field} ({count})" for field, count in sorted(missing.items())
        )
        message = f"{provider}/{model}: incomplete capture protocol: {missing_summary}"
        (errors if require_protocol else warnings).append(message)

    supplied_grade_rows = grades or []
    grade_match: bool | None = None
    if supplied_grade_rows and not responses:
        errors.append(
            "grades were supplied without responses, so they cannot be audited"
        )
    elif responses is not None and grades is not None:
        recomputed = grade_responses(tasks, responses, prices=prices or {})
        recomputed_by_key = {_grade_key(item): item for item in recomputed}
        supplied_by_key: dict[tuple[str, str, str], GradeRecord] = {}
        for grade in supplied_grade_rows:
            key = _grade_key(grade)
            if key in supplied_by_key:
                errors.append(
                    f"duplicate grade: {grade.provider}/{grade.model}/{grade.task_id}"
                )
            supplied_by_key[key] = grade
        missing_grades = sorted(set(recomputed_by_key) - set(supplied_by_key))
        extra_grades = sorted(set(supplied_by_key) - set(recomputed_by_key))
        if missing_grades:
            errors.append(f"grade file is missing {len(missing_grades)} rows")
        if extra_grades:
            errors.append(f"grade file contains {len(extra_grades)} extra rows")
        mismatches = []
        for key in sorted(set(recomputed_by_key) & set(supplied_by_key)):
            expected_json = canonical_json(recomputed_by_key[key].to_dict())
            supplied_json = canonical_json(supplied_by_key[key].to_dict())
            if expected_json != supplied_json:
                mismatches.append("/".join(key))
        if mismatches:
            errors.append(
                f"{len(mismatches)} grade rows do not match deterministic recomputation"
            )
        grade_match = not missing_grades and not extra_grades and not mismatches

    return {
        "status": "pass" if not errors else "fail",
        "suite_commitment": suite_commitment(tasks),
        "tasks": len(tasks),
        "packs": sorted({task.pack for task in tasks}),
        "pack_count": len({task.pack for task in tasks}),
        "template_count": len(templates),
        "responses": len(response_rows),
        "models": len(response_models),
        "request_errors": request_errors,
        "coverage": coverage,
        "protocol_fields": list(protocol_fields),
        "responses_with_complete_protocol": protocol_complete,
        "protocol_coverage": protocol_coverage,
        "grades": len(supplied_grade_rows),
        "grades_match_recomputation": grade_match,
        "errors": errors,
        "warnings": warnings,
    }
