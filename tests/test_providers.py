from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from ohmjudge.providers.anthropic import AnthropicProvider
from ohmjudge.providers.openai import (
    OpenAICompatibleProvider,
    OpenAIResponsesProvider,
)


class ProviderTests(unittest.TestCase):
    def test_openai_compatible_payload_and_parse(self) -> None:
        seen = {}

        def transport(url, headers, payload, timeout):
            seen.update(url=url, headers=headers, payload=payload, timeout=timeout)
            return {
                "id": "abc",
                "choices": [{"message": {"content": '{"answer":1,"unit":"V"}'}}],
                "usage": {
                    "prompt_tokens": 12,
                    "completion_tokens": 8,
                    "total_tokens": 20,
                },
            }

        with patch.dict(os.environ, {"TEST_KEY": "secret"}):
            provider = OpenAICompatibleProvider(
                base_url="https://example.test/v1/",
                api_key_env="TEST_KEY",
                structured_output=True,
                transport=transport,
            )
            response = provider.request(task_id="t1", prompt="question", model="m1")
        self.assertIsNone(response.error)
        self.assertEqual("https://example.test/v1/chat/completions", seen["url"])
        self.assertEqual({"type": "json_object"}, seen["payload"]["response_format"])
        self.assertEqual(12, response.usage["input_tokens"])
        self.assertNotIn("secret", response.to_dict().__repr__())

    def test_responses_api_extracts_output_text(self) -> None:
        def transport(url, headers, payload, timeout):
            return {
                "id": "resp",
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": '{"answer":2,"unit":"A"}'}
                        ],
                    }
                ],
                "usage": {"input_tokens": 10, "output_tokens": 6, "total_tokens": 16},
            }

        with patch.dict(os.environ, {"OPENAI_API_KEY": "secret"}):
            provider = OpenAIResponsesProvider(transport=transport)
            response = provider.request(task_id="t2", prompt="question", model="m2")
        self.assertEqual('{"answer":2,"unit":"A"}', response.text)
        self.assertEqual("completed", response.metadata["status"])

    def test_anthropic_payload_and_usage(self) -> None:
        seen = {}

        def transport(url, headers, payload, timeout):
            seen["payload"] = payload
            return {
                "id": "msg",
                "content": [{"type": "text", "text": '{"answer":3,"unit":"Hz"}'}],
                "usage": {"input_tokens": 20, "output_tokens": 7},
                "stop_reason": "end_turn",
            }

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "secret"}):
            response = AnthropicProvider(transport=transport).request(
                task_id="t3", prompt="question", model="m3"
            )
        self.assertEqual(27, response.usage["total_tokens"])
        self.assertEqual(0, seen["payload"]["temperature"])

    def test_missing_key_becomes_record_error(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            response = OpenAICompatibleProvider(
                base_url="https://example.test",
                api_key_env="ABSENT",
            ).request(task_id="t4", prompt="question", model="m4")
        self.assertIn("ABSENT", response.error or "")


if __name__ == "__main__":
    unittest.main()
