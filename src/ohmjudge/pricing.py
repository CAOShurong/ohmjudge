from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .io import read_json


@dataclass(frozen=True, slots=True)
class Price:
    provider: str
    model: str
    input_per_million: float
    output_per_million: float
    currency: str = "USD"
    source: str | None = None
    verified_at: str | None = None


def load_prices(path: str | None) -> dict[tuple[str, str], Price]:
    if not path:
        return {}
    payload = read_json(Path(path))
    entries = payload.get("models", [])
    if not isinstance(entries, list):
        raise ValueError("pricing file field 'models' must be a list")
    prices: dict[tuple[str, str], Price] = {}
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("each pricing entry must be an object")
        price = Price(
            provider=str(item["provider"]),
            model=str(item["model"]),
            input_per_million=float(item["input_per_million"]),
            output_per_million=float(item["output_per_million"]),
            currency=str(item.get("currency", "USD")),
            source=str(item["source"]) if item.get("source") else None,
            verified_at=(
                str(item["verified_at"]) if item.get("verified_at") else None
            ),
        )
        if price.input_per_million < 0 or price.output_per_million < 0:
            raise ValueError("pricing values must be non-negative")
        prices[(price.provider, price.model)] = price
    return prices


def calculate_cost(
    usage: dict[str, int], price: Price | None
) -> float | None:
    if price is None:
        return None
    has_input = "input_tokens" in usage or "prompt_tokens" in usage
    has_output = "output_tokens" in usage or "completion_tokens" in usage
    if not has_input and not has_output:
        return None
    input_tokens = usage.get("input_tokens", usage.get("prompt_tokens", 0))
    output_tokens = usage.get("output_tokens", usage.get("completion_tokens", 0))
    return (
        input_tokens * price.input_per_million
        + output_tokens * price.output_per_million
    ) / 1_000_000.0


def price_metadata(prices: dict[tuple[str, str], Price]) -> list[dict[str, Any]]:
    return [
        {
            "provider": price.provider,
            "model": price.model,
            "currency": price.currency,
            "input_per_million": price.input_per_million,
            "output_per_million": price.output_per_million,
            "source": price.source,
            "verified_at": price.verified_at,
        }
        for price in prices.values()
    ]
