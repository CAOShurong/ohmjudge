from __future__ import annotations

from collections.abc import Iterable

from .models import GradeRecord, ModelResponse, Task
from .parse import parse_answer
from .pricing import Price, calculate_cost
from .units import convert_value, finite_number, lookup_unit


def grade_one(
    task: Task,
    response: ModelResponse,
    *,
    price: Price | None = None,
) -> GradeRecord:
    expected_value = task.expected.get("value")
    expected_unit = str(task.expected.get("unit", "unitless"))
    cost = calculate_cost(response.usage, price)

    common = {
        "task_id": task.id,
        "provider": response.provider,
        "model": response.model,
        "pack": task.pack,
        "template": task.template,
        "expected_value": expected_value,
        "expected_unit": expected_unit,
        "response_text": response.text,
        "prompt": task.prompt,
        "latency_ms": response.latency_ms,
        "usage": response.usage,
        "cost": cost,
    }
    if response.error:
        return GradeRecord(
            **common,
            correct=False,
            error_type="request_error",
            observed_value=None,
            observed_unit=None,
            absolute_error=None,
            parse_mode=None,
            details={"request_error": response.error},
        )

    if not response.text.strip():
        return GradeRecord(
            **common,
            correct=False,
            error_type="empty_response",
            observed_value=None,
            observed_unit=None,
            absolute_error=None,
            parse_mode="none",
            details={},
        )

    parsed = parse_answer(response.text)
    observed_number = finite_number(parsed.value)
    expected_number = finite_number(expected_value)
    if expected_number is None:
        raise ValueError(f"task {task.id} has a non-numeric expected value")
    if observed_number is None:
        return GradeRecord(
            **common,
            correct=False,
            error_type=(
                "parse_error" if parsed.value is None else "non_numeric_answer"
            ),
            observed_value=parsed.value,
            observed_unit=parsed.unit,
            absolute_error=None,
            parse_mode=parsed.mode,
            details={"parse_error": parsed.error},
        )

    if not parsed.unit:
        return GradeRecord(
            **common,
            correct=False,
            error_type="missing_unit",
            observed_value=observed_number,
            observed_unit=None,
            absolute_error=None,
            parse_mode=parsed.mode,
            details={},
        )

    observed_unit = parsed.unit
    observed_spec = lookup_unit(observed_unit)
    expected_spec = lookup_unit(expected_unit)
    if observed_spec is None:
        return GradeRecord(
            **common,
            correct=False,
            error_type="unknown_unit",
            observed_value=observed_number,
            observed_unit=observed_unit,
            absolute_error=None,
            parse_mode=parsed.mode,
            details={
                "expected_dimension": expected_spec.dimension if expected_spec else None
            },
        )
    if expected_spec is None:
        raise ValueError(f"task {task.id} has unknown expected unit {expected_unit!r}")
    if observed_spec.dimension != expected_spec.dimension:
        return GradeRecord(
            **common,
            correct=False,
            error_type="incompatible_unit",
            observed_value=observed_number,
            observed_unit=observed_unit,
            absolute_error=None,
            parse_mode=parsed.mode,
            details={
                "observed_dimension": observed_spec.dimension,
                "expected_dimension": expected_spec.dimension,
            },
        )

    converted = convert_value(observed_number, observed_unit, expected_unit)
    if converted is None:  # Defensive: both units were validated above.
        raise ValueError(f"cannot convert {observed_unit!r} to {expected_unit!r}")

    absolute_error = abs(converted - expected_number)
    allowed_error = max(
        float(task.tolerance.get("absolute", 0.0)),
        float(task.tolerance.get("relative", 0.0)) * abs(expected_number),
    )
    correct = absolute_error <= allowed_error + 1e-15
    return GradeRecord(
        **common,
        correct=correct,
        error_type="correct" if correct else "wrong_value",
        observed_value=converted,
        observed_unit=expected_unit,
        absolute_error=absolute_error,
        parse_mode=parsed.mode,
        details={"allowed_error": allowed_error, "raw_unit": parsed.unit},
    )


def grade_responses(
    tasks: Iterable[Task],
    responses: Iterable[ModelResponse],
    *,
    prices: dict[tuple[str, str], Price] | None = None,
) -> list[GradeRecord]:
    tasks_by_id = {task.id: task for task in tasks}
    price_table = prices or {}
    grades: list[GradeRecord] = []
    for response in responses:
        task = tasks_by_id.get(response.task_id)
        if task is None:
            raise ValueError(f"response references unknown task {response.task_id}")
        grades.append(
            grade_one(
                task,
                response,
                price=price_table.get((response.provider, response.model)),
            )
        )
    return grades
