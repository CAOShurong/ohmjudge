from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from ..models import ModelResponse

Transport = Callable[
    [str, dict[str, str], dict[str, Any], float],
    dict[str, Any],
]


def post_json(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: float,
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read(2048).decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"network error: {exc.reason}") from exc
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("provider returned non-JSON data") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("provider returned a non-object JSON value")
    return parsed


class BaseProvider(ABC):
    name: str

    @abstractmethod
    def request(self, *, task_id: str, prompt: str, model: str) -> ModelResponse:
        raise NotImplementedError

    @staticmethod
    def _timed(
        operation: Callable[[], tuple[str, dict[str, int], dict[str, Any]]],
        *,
        task_id: str,
        provider: str,
        model: str,
    ) -> ModelResponse:
        started = time.perf_counter()
        try:
            text, usage, metadata = operation()
            error = None
        except Exception as exc:
            text = ""
            usage = {}
            metadata = {}
            error = str(exc)
        return ModelResponse(
            task_id=task_id,
            provider=provider,
            model=model,
            text=text,
            latency_ms=(time.perf_counter() - started) * 1000.0,
            usage=usage,
            error=error,
            metadata=metadata,
        )
