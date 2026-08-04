from __future__ import annotations

import json
import random
from pathlib import Path

from .generate import generate_tasks, suite_commitment
from .grade import grade_responses
from .io import write_json, write_jsonl
from .lab import render_lab
from .models import ModelResponse
from .pricing import load_prices, price_metadata
from .report import render_report


_PROFILES = (
    ("synthetic", "CopperFox-4", 0.88, 1450.0, 820, 92),
    ("synthetic", "SiliconMist-2", 0.72, 620.0, 690, 68),
    ("synthetic", "NanoRelay-1", 0.54, 240.0, 540, 44),
)


def build_demo(directory: str | Path, *, seed: int = 2026, count: int = 40) -> dict[str, Path]:
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    tasks = generate_tasks(count=count, seed=seed)
    responses: list[ModelResponse] = []
    rng = random.Random(seed ^ 0x0A11CE)
    for provider, model, accuracy, latency, input_tokens, output_tokens in _PROFILES:
        for task in tasks:
            correct = rng.random() < accuracy
            expected = float(task.expected["value"])
            unit = str(task.expected["unit"])
            if correct:
                answer = expected * (1.0 + rng.uniform(-2e-5, 2e-5))
                text = json.dumps({"answer": answer, "unit": unit})
            elif rng.random() < 0.12:
                text = "I cannot determine the answer from the information given."
            elif rng.random() < 0.18:
                text = json.dumps({"answer": expected, "unit": "bananas"})
            else:
                text = json.dumps(
                    {"answer": expected * rng.choice([0.5, 0.8, 1.2, 2.0]), "unit": unit}
                )
            responses.append(
                ModelResponse(
                    task_id=task.id,
                    provider=provider,
                    model=model,
                    text=text,
                    latency_ms=max(40.0, rng.gauss(latency, latency * 0.12)),
                    usage={
                        "input_tokens": max(1, int(rng.gauss(input_tokens, 25))),
                        "output_tokens": max(1, int(rng.gauss(output_tokens, 9))),
                    },
                    metadata={"synthetic": True},
                )
            )

    pricing_path = root / "synthetic-pricing.json"
    write_json(
        pricing_path,
        {
            "notice": "Fictional prices for UI demonstration only.",
            "models": [
                {
                    "provider": "synthetic",
                    "model": "CopperFox-4",
                    "input_per_million": 5.0,
                    "output_per_million": 20.0,
                    "currency": "USD",
                    "source": "synthetic-demo",
                    "verified_at": "not-applicable",
                },
                {
                    "provider": "synthetic",
                    "model": "SiliconMist-2",
                    "input_per_million": 1.0,
                    "output_per_million": 4.0,
                    "currency": "USD",
                    "source": "synthetic-demo",
                    "verified_at": "not-applicable",
                },
                {
                    "provider": "synthetic",
                    "model": "NanoRelay-1",
                    "input_per_million": 0.2,
                    "output_per_million": 0.8,
                    "currency": "USD",
                    "source": "synthetic-demo",
                    "verified_at": "not-applicable",
                },
            ],
        },
    )
    prices = load_prices(str(pricing_path))
    grades = grade_responses(tasks, responses, prices=prices)
    tasks_path = root / "tasks.private.jsonl"
    prompts_path = root / "prompts.public.jsonl"
    responses_path = root / "responses.synthetic.jsonl"
    grades_path = root / "grades.synthetic.jsonl"
    report_path = root / "report.html"
    lab_path = root / "no-api-lab.html"
    write_jsonl(tasks_path, (task.to_dict() for task in tasks))
    write_jsonl(prompts_path, (task.to_dict(public=True) for task in tasks))
    write_jsonl(responses_path, (response.to_dict() for response in responses))
    write_jsonl(grades_path, (grade.to_dict() for grade in grades))
    render_report(
        grades,
        report_path,
        title="OhmJudge synthetic demonstration",
        note=(
            "All model names, responses, latencies, token counts, and prices in "
            "this demonstration are synthetic. They are UI fixtures, not claims "
            "about real frontier models."
        ),
        suite_commitment=suite_commitment(tasks),
        price_metadata=price_metadata(prices),
    )
    render_lab(tasks, lab_path)
    return {
        "tasks": tasks_path,
        "prompts": prompts_path,
        "responses": responses_path,
        "grades": grades_path,
        "report": report_path,
        "lab": lab_path,
        "pricing": pricing_path,
    }
