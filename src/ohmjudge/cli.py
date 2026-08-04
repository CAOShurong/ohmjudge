from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .audit import audit_experiment
from .compare import compare_models
from .demo import build_demo
from .generate import generate_tasks, suite_commitment
from .grade import grade_responses
from .io import read_jsonl, write_json, write_jsonl
from .lab import render_lab
from .models import GradeRecord, ModelResponse, Task
from .packs import PACKS
from .pricing import load_prices, price_metadata
from .providers import (
    AnthropicProvider,
    OpenAICompatibleProvider,
    OpenAIResponsesProvider,
    ReplayProvider,
)
from .report import render_report
from .runner import run_and_save


def _tasks(path: str) -> list[Task]:
    values = [Task.from_dict(record) for record in read_jsonl(path)]
    if not values:
        raise ValueError(f"{path}: no tasks")
    if any(not task.expected for task in values):
        raise ValueError(
            f"{path}: public prompt records cannot be graded; use the private task file"
        )
    return values


def _responses(path: str) -> list[ModelResponse]:
    return [ModelResponse.from_dict(record) for record in read_jsonl(path)]


def _grades(path: str) -> list[GradeRecord]:
    return [GradeRecord.from_dict(record) for record in read_jsonl(path)]


def _build_provider(args: argparse.Namespace):
    if args.provider == "openai-compatible":
        return OpenAICompatibleProvider(
            base_url=args.base_url,
            api_key_env=args.api_key_env,
            timeout=args.timeout,
            max_tokens=args.max_tokens,
            structured_output=args.structured_output,
        )
    if args.provider == "openai-responses":
        return OpenAIResponsesProvider(
            base_url=args.base_url,
            api_key_env=args.api_key_env,
            timeout=args.timeout,
            max_output_tokens=args.max_tokens,
        )
    if args.provider == "anthropic":
        return AnthropicProvider(
            base_url=args.base_url,
            api_key_env=args.api_key_env,
            timeout=args.timeout,
            max_tokens=args.max_tokens,
        )
    if args.provider == "replay":
        if not args.replay:
            raise ValueError("--replay is required for the replay provider")
        return ReplayProvider(args.replay)
    raise ValueError(f"unsupported provider {args.provider}")


def _cmd_generate(args: argparse.Namespace) -> int:
    tasks = generate_tasks(pack_names=args.pack, count=args.count, seed=args.seed)
    write_jsonl(args.output, (task.to_dict() for task in tasks))
    if args.public_output:
        write_jsonl(args.public_output, (task.to_dict(public=True) for task in tasks))
    print(
        json.dumps(
            {
                "tasks": len(tasks),
                "packs": sorted({task.pack for task in tasks}),
                "output": str(Path(args.output).resolve()),
                "public_output": (
                    str(Path(args.public_output).resolve())
                    if args.public_output
                    else None
                ),
                "commitment": suite_commitment(tasks),
            },
            indent=2,
        )
    )
    return 0


def _cmd_lab(args: argparse.Namespace) -> int:
    tasks = _tasks(args.tasks)
    path = render_lab(tasks, args.output)
    print(path.resolve())
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    tasks = _tasks(args.tasks)
    provider = _build_provider(args)
    responses = run_and_save(
        tasks,
        provider=provider,
        model=args.model,
        output=args.output,
        concurrency=args.concurrency,
        resume=not args.no_resume,
    )
    errors = sum(response.error is not None for response in responses)
    print(
        json.dumps(
            {
                "responses": len(responses),
                "errors": errors,
                "provider": provider.name,
                "model": args.model,
                "output": str(Path(args.output).resolve()),
            },
            indent=2,
        )
    )
    return 1 if errors == len(responses) and responses else 0


def _cmd_grade(args: argparse.Namespace) -> int:
    tasks = _tasks(args.tasks)
    responses = _responses(args.responses)
    prices = load_prices(args.pricing)
    grades = grade_responses(tasks, responses, prices=prices)
    write_jsonl(args.output, (grade.to_dict() for grade in grades))
    print(
        json.dumps(
            {
                "graded": len(grades),
                "correct": sum(grade.correct for grade in grades),
                "output": str(Path(args.output).resolve()),
            },
            indent=2,
        )
    )
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    grades = _grades(args.grades)
    prices = load_prices(args.pricing)
    tasks = _tasks(args.tasks) if args.tasks else []
    path = render_report(
        grades,
        args.output,
        title=args.title,
        note=args.note,
        suite_commitment=suite_commitment(tasks) if tasks else "",
        price_metadata=price_metadata(prices),
    )
    print(path.resolve())
    return 0


def _cmd_audit(args: argparse.Namespace) -> int:
    tasks = _tasks(args.tasks)
    responses = _responses(args.responses) if args.responses else None
    grades = _grades(args.grades) if args.grades else None
    prices = load_prices(args.pricing)
    result = audit_experiment(
        tasks,
        responses=responses,
        grades=grades,
        prices=prices,
        require_complete=args.require_complete,
        require_protocol=args.require_protocol,
    )
    if args.output:
        write_json(args.output, result)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


def _cmd_compare(args: argparse.Namespace) -> int:
    result = compare_models(
        _grades(args.grades),
        baseline_provider=args.baseline_provider,
        baseline_model=args.baseline_model,
        challenger_provider=args.challenger_provider,
        challenger_model=args.challenger_model,
    )
    if args.output:
        write_json(args.output, result)
    print(json.dumps(result, indent=2))
    return 0


def _cmd_demo(args: argparse.Namespace) -> int:
    outputs = build_demo(args.output, seed=args.seed, count=args.count)
    print(
        json.dumps(
            {name: str(path.resolve()) for name, path in outputs.items()},
            indent=2,
        )
    )
    return 0


def _cmd_list_packs(args: argparse.Namespace) -> int:
    payload: dict[str, Any] = {
        pack: [generator.__name__ for generator in generators]
        for pack, generators in PACKS.items()
    }
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    env_names = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "ZHIPU_API_KEY",
        "KIMI_API_KEY",
        "DASHSCOPE_API_KEY",
    ]
    payload = {
        "ohmjudge": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "no_api_workflow_ready": sys.version_info >= (3, 11),
        "optional_api_credentials": {
            name: "set" if os.environ.get(name) else "not set" for name in env_names
        },
        "note": "Credential values are never printed.",
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["no_api_workflow_ready"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ohmjudge",
        description=(
            "Fresh, executable electrical-engineering benchmarks for frontier models."
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="generate a fresh task suite")
    generate.add_argument("--pack", action="append", choices=tuple(PACKS))
    generate.add_argument("--count", type=int, default=50)
    generate.add_argument("--seed", type=int, default=2026)
    generate.add_argument("--output", default="tasks.private.jsonl")
    generate.add_argument("--public-output")
    generate.set_defaults(func=_cmd_generate)

    lab = commands.add_parser(
        "lab", help="build a self-contained no-API paste-and-grade lab"
    )
    lab.add_argument("--tasks", required=True)
    lab.add_argument("--output", default="ohmjudge-lab.html")
    lab.set_defaults(func=_cmd_lab)

    run = commands.add_parser("run", help="run tasks through an optional model API")
    run.add_argument("--tasks", required=True)
    run.add_argument(
        "--provider",
        required=True,
        choices=("openai-compatible", "openai-responses", "anthropic", "replay"),
    )
    run.add_argument("--model", required=True)
    run.add_argument("--base-url", default="https://api.openai.com/v1")
    run.add_argument("--api-key-env", default="OPENAI_API_KEY")
    run.add_argument("--replay")
    run.add_argument("--output", default="responses.jsonl")
    run.add_argument("--timeout", type=float, default=120.0)
    run.add_argument("--max-tokens", type=int, default=256)
    run.add_argument("--concurrency", type=int, default=1)
    run.add_argument("--structured-output", action="store_true")
    run.add_argument("--no-resume", action="store_true")
    run.set_defaults(func=_cmd_run)

    grade = commands.add_parser("grade", help="grade response JSONL deterministically")
    grade.add_argument("--tasks", required=True)
    grade.add_argument("--responses", required=True)
    grade.add_argument("--pricing")
    grade.add_argument("--output", default="grades.jsonl")
    grade.set_defaults(func=_cmd_grade)

    report = commands.add_parser("report", help="build an interactive HTML report")
    report.add_argument("--grades", required=True)
    report.add_argument("--tasks")
    report.add_argument("--pricing")
    report.add_argument("--title", default="OhmJudge benchmark report")
    report.add_argument("--note", default="")
    report.add_argument("--output", default="ohmjudge-report.html")
    report.set_defaults(func=_cmd_report)

    audit = commands.add_parser(
        "audit", help="verify the integrity and coverage of experiment artifacts"
    )
    audit.add_argument("--tasks", required=True)
    audit.add_argument("--responses")
    audit.add_argument("--grades")
    audit.add_argument("--pricing")
    audit.add_argument("--require-complete", action="store_true")
    audit.add_argument(
        "--require-protocol",
        action="store_true",
        help=(
            "require captured_at, surface, settings, tools, and retry_policy "
            "metadata on every response"
        ),
    )
    audit.add_argument("--output")
    audit.set_defaults(func=_cmd_audit)

    compare = commands.add_parser(
        "compare", help="run a paired deterministic comparison of two models"
    )
    compare.add_argument("--grades", required=True)
    compare.add_argument("--baseline-provider", required=True)
    compare.add_argument("--baseline-model", required=True)
    compare.add_argument("--challenger-provider", required=True)
    compare.add_argument("--challenger-model", required=True)
    compare.add_argument("--output")
    compare.set_defaults(func=_cmd_compare)

    demo = commands.add_parser("demo", help="build synthetic report and no-API lab")
    demo.add_argument("--output", default="demo")
    demo.add_argument("--seed", type=int, default=2026)
    demo.add_argument("--count", type=int, default=50)
    demo.set_defaults(func=_cmd_demo)

    packs = commands.add_parser("list-packs", help="list task packs and templates")
    packs.set_defaults(func=_cmd_list_packs)

    doctor = commands.add_parser(
        "doctor", help="check local readiness without revealing credentials"
    )
    doctor.set_defaults(func=_cmd_doctor)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"ohmjudge: {exc}\n")
    return 2
