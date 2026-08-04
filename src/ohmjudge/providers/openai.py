from __future__ import annotations

import os
from typing import Any

from ..models import ModelResponse
from .base import BaseProvider, Transport, post_json

SYSTEM_PROMPT = (
    "You are being evaluated on electrical-engineering calculation tasks. "
    "Follow the requested output contract exactly. Do not use markdown fences."
)


def _usage(payload: dict[str, Any]) -> dict[str, int]:
    raw = payload.get("usage")
    if not isinstance(raw, dict):
        return {}
    aliases = {
        "prompt_tokens": "input_tokens",
        "completion_tokens": "output_tokens",
        "input_tokens": "input_tokens",
        "output_tokens": "output_tokens",
        "total_tokens": "total_tokens",
    }
    result: dict[str, int] = {}
    for source, target in aliases.items():
        value = raw.get(source)
        if isinstance(value, (int, float)):
            result[target] = int(value)
    return result


class OpenAICompatibleProvider(BaseProvider):
    name = "openai-compatible"

    def __init__(
        self,
        *,
        base_url: str,
        api_key_env: str,
        timeout: float = 120.0,
        max_tokens: int = 256,
        structured_output: bool = False,
        transport: Transport = post_json,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.structured_output = structured_output
        self.transport = transport

    def request(self, *, task_id: str, prompt: str, model: str) -> ModelResponse:
        def operation() -> tuple[str, dict[str, int], dict[str, Any]]:
            api_key = os.environ.get(self.api_key_env)
            if not api_key:
                raise RuntimeError(
                    f"environment variable {self.api_key_env} is not set"
                )
            payload: dict[str, Any] = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                "max_tokens": self.max_tokens,
            }
            if self.structured_output:
                payload["response_format"] = {"type": "json_object"}
            data = self.transport(
                f"{self.base_url}/chat/completions",
                {"Authorization": f"Bearer {api_key}"},
                payload,
                self.timeout,
            )
            choices = data.get("choices")
            if not isinstance(choices, list) or not choices:
                raise RuntimeError("response has no choices")
            first = choices[0]
            if not isinstance(first, dict) or not isinstance(
                first.get("message"), dict
            ):
                raise RuntimeError("response choice has no message")
            content = first["message"].get("content")
            if not isinstance(content, str):
                raise RuntimeError("response message has no text content")
            return content, _usage(data), {"response_id": data.get("id")}

        return self._timed(
            operation,
            task_id=task_id,
            provider=self.name,
            model=model,
        )


class OpenAIResponsesProvider(BaseProvider):
    name = "openai-responses"

    def __init__(
        self,
        *,
        base_url: str = "https://api.openai.com/v1",
        api_key_env: str = "OPENAI_API_KEY",
        timeout: float = 120.0,
        max_output_tokens: int = 256,
        transport: Transport = post_json,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.timeout = timeout
        self.max_output_tokens = max_output_tokens
        self.transport = transport

    def request(self, *, task_id: str, prompt: str, model: str) -> ModelResponse:
        def operation() -> tuple[str, dict[str, int], dict[str, Any]]:
            api_key = os.environ.get(self.api_key_env)
            if not api_key:
                raise RuntimeError(
                    f"environment variable {self.api_key_env} is not set"
                )
            data = self.transport(
                f"{self.base_url}/responses",
                {"Authorization": f"Bearer {api_key}"},
                {
                    "model": model,
                    "instructions": SYSTEM_PROMPT,
                    "input": prompt,
                    "max_output_tokens": self.max_output_tokens,
                    "store": False,
                },
                self.timeout,
            )
            chunks: list[str] = []
            output = data.get("output")
            if isinstance(output, list):
                for item in output:
                    if not isinstance(item, dict) or item.get("type") != "message":
                        continue
                    content = item.get("content")
                    if not isinstance(content, list):
                        continue
                    for part in content:
                        if (
                            isinstance(part, dict)
                            and part.get("type") == "output_text"
                            and isinstance(part.get("text"), str)
                        ):
                            chunks.append(part["text"])
            if not chunks:
                raise RuntimeError("response has no output_text")
            return (
                "\n".join(chunks),
                _usage(data),
                {
                    "response_id": data.get("id"),
                    "status": data.get("status"),
                },
            )

        return self._timed(
            operation,
            task_id=task_id,
            provider=self.name,
            model=model,
        )
