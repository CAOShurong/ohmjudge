from __future__ import annotations

from pathlib import Path

from ..io import read_jsonl
from ..models import ModelResponse
from .base import BaseProvider


class ReplayProvider(BaseProvider):
    name = "replay"

    def __init__(self, path: str | Path) -> None:
        self.responses = {
            str(record["task_id"]): record for record in read_jsonl(path)
        }

    def request(self, *, task_id: str, prompt: str, model: str) -> ModelResponse:
        record = self.responses.get(task_id)
        if record is None:
            return ModelResponse(
                task_id=task_id,
                provider=self.name,
                model=model,
                error="no replay response for task",
            )
        return ModelResponse(
            task_id=task_id,
            provider=str(record.get("provider", self.name)),
            model=str(record.get("model", model)),
            text=str(record.get("text", "")),
            latency_ms=(
                float(record["latency_ms"])
                if record.get("latency_ms") is not None
                else None
            ),
            usage={
                str(key): int(value)
                for key, value in dict(record.get("usage", {})).items()
            },
            error=str(record["error"]) if record.get("error") else None,
            metadata=dict(record.get("metadata", {})),
        )
