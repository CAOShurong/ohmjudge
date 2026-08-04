from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Task:
    id: str
    pack: str
    template: str
    seed: int
    prompt: str
    expected: dict[str, Any]
    tolerance: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, *, public: bool = False) -> dict[str, Any]:
        data = asdict(self)
        if public:
            data.pop("expected", None)
            data.pop("tolerance", None)
            metadata = dict(data.get("metadata", {}))
            metadata.pop("parameters", None)
            data["metadata"] = metadata
            data["answer_contract"] = {
                "format": "json",
                "schema": {"answer": "number", "unit": "string"},
            }
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        return cls(
            id=str(data["id"]),
            pack=str(data["pack"]),
            template=str(data["template"]),
            seed=int(data["seed"]),
            prompt=str(data["prompt"]),
            expected=dict(data.get("expected", {})),
            tolerance={
                str(k): float(v) for k, v in dict(data.get("tolerance", {})).items()
            },
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(slots=True)
class ModelResponse:
    task_id: str
    provider: str
    model: str
    text: str = ""
    latency_ms: float | None = None
    usage: dict[str, int] = field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelResponse:
        return cls(
            task_id=str(data["task_id"]),
            provider=str(data["provider"]),
            model=str(data["model"]),
            text=str(data.get("text", "")),
            latency_ms=(
                float(data["latency_ms"])
                if data.get("latency_ms") is not None
                else None
            ),
            usage={str(k): int(v) for k, v in dict(data.get("usage", {})).items()},
            error=str(data["error"]) if data.get("error") else None,
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(slots=True)
class GradeRecord:
    task_id: str
    provider: str
    model: str
    pack: str
    template: str
    correct: bool
    error_type: str
    expected_value: float | str | None
    expected_unit: str
    observed_value: float | str | None
    observed_unit: str | None
    absolute_error: float | None
    response_text: str
    prompt: str
    latency_ms: float | None
    usage: dict[str, int]
    cost: float | None = None
    parse_mode: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GradeRecord:
        return cls(
            task_id=str(data["task_id"]),
            provider=str(data["provider"]),
            model=str(data["model"]),
            pack=str(data["pack"]),
            template=str(data["template"]),
            correct=bool(data["correct"]),
            error_type=str(data["error_type"]),
            expected_value=data.get("expected_value"),
            expected_unit=str(data.get("expected_unit", "")),
            observed_value=data.get("observed_value"),
            observed_unit=(
                str(data["observed_unit"])
                if data.get("observed_unit") is not None
                else None
            ),
            absolute_error=(
                float(data["absolute_error"])
                if data.get("absolute_error") is not None
                else None
            ),
            response_text=str(data.get("response_text", "")),
            prompt=str(data.get("prompt", "")),
            latency_ms=(
                float(data["latency_ms"])
                if data.get("latency_ms") is not None
                else None
            ),
            usage={str(k): int(v) for k, v in dict(data.get("usage", {})).items()},
            cost=float(data["cost"]) if data.get("cost") is not None else None,
            parse_mode=(
                str(data["parse_mode"]) if data.get("parse_mode") is not None else None
            ),
            details=dict(data.get("details", {})),
        )
