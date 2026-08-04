from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .io import read_jsonl, write_jsonl
from .models import ModelResponse, Task
from .providers import BaseProvider


def run_tasks(
    tasks: list[Task],
    *,
    provider: BaseProvider,
    model: str,
    concurrency: int = 1,
    resume_from: str | Path | None = None,
) -> list[ModelResponse]:
    if concurrency < 1:
        raise ValueError("concurrency must be at least 1")
    completed: dict[str, ModelResponse] = {}
    if resume_from and Path(resume_from).exists():
        for record in read_jsonl(resume_from):
            response = ModelResponse.from_dict(record)
            if response.model != model:
                raise ValueError(
                    "resume file contains model "
                    f"{response.model!r}, expected {model!r}"
                )
            if response.task_id in completed:
                raise ValueError(
                    f"resume file repeats task {response.task_id}"
                )
            completed[response.task_id] = response
    pending = [task for task in tasks if task.id not in completed]

    def call(task: Task) -> ModelResponse:
        return provider.request(task_id=task.id, prompt=task.prompt, model=model)

    if concurrency == 1:
        for task in pending:
            completed[task.id] = call(task)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {executor.submit(call, task): task for task in pending}
            for future in as_completed(futures):
                task = futures[future]
                try:
                    completed[task.id] = future.result()
                except Exception as exc:
                    completed[task.id] = ModelResponse(
                        task_id=task.id,
                        provider=provider.name,
                        model=model,
                        error=f"runner error: {exc}",
                    )
    return [completed[task.id] for task in tasks if task.id in completed]


def run_and_save(
    tasks: list[Task],
    *,
    provider: BaseProvider,
    model: str,
    output: str | Path,
    concurrency: int = 1,
    resume: bool = True,
) -> list[ModelResponse]:
    responses = run_tasks(
        tasks,
        provider=provider,
        model=model,
        concurrency=concurrency,
        resume_from=output if resume else None,
    )
    write_jsonl(output, (response.to_dict() for response in responses))
    return responses
