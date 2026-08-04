from __future__ import annotations

import os
from typing import Any

from ..models import ModelResponse
from .base import BaseProvider, Transport, post_json
from .openai import SYSTEM_PROMPT


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(
        self,
        *,
        base_url: str = "https://api.anthropic.com/v1",
        api_key_env: str = "ANTHROPIC_API_KEY",
        anthropic_version: str = "2023-06-01",
        timeout: float = 120.0,
        max_tokens: int = 256,
        transport: Transport = post_json,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.anthropic_version = anthropic_version
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.transport = transport

    def request(self, *, task_id: str, prompt: str, model: str) -> ModelResponse:
        def operation() -> tuple[str, dict[str, int], dict[str, Any]]:
            api_key = os.environ.get(self.api_key_env)
            if not api_key:
                raise RuntimeError(
                    f"environment variable {self.api_key_env} is not set"
                )
            data = self.transport(
                f"{self.base_url}/messages",
                {
                    "x-api-key": api_key,
                    "anthropic-version": self.anthropic_version,
                },
                {
                    "model": model,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens": self.max_tokens,
                },
                self.timeout,
            )
            text_parts = [
                item["text"]
                for item in data.get("content", [])
                if isinstance(item, dict)
                and item.get("type") == "text"
                and isinstance(item.get("text"), str)
            ]
            if not text_parts:
                raise RuntimeError("response has no text content")
            raw_usage = data.get("usage", {})
            usage = {
                key: int(raw_usage.get(key, 0))
                for key in ("input_tokens", "output_tokens")
                if isinstance(raw_usage.get(key), (int, float))
            } if isinstance(raw_usage, dict) else {}
            usage["total_tokens"] = sum(usage.values())
            return "\n".join(text_parts), usage, {
                "response_id": data.get("id"),
                "stop_reason": data.get("stop_reason"),
            }

        return self._timed(
            operation,
            task_id=task_id,
            provider=self.name,
            model=model,
        )
