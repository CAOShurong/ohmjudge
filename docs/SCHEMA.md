# Data schemas

OhmJudge uses newline-delimited JSON for task, response, and grade records. Each
line is one complete object, so files can be streamed, diffed, concatenated, or
processed without loading an entire dataset.

## Private task

```json
{
  "id": "circuits.voltage_divider.012345abcdef",
  "pack": "circuits",
  "template": "voltage_divider",
  "seed": 2026,
  "prompt": "…",
  "expected": {"kind": "numeric", "value": 3.3, "unit": "V"},
  "tolerance": {"relative": 0.001, "absolute": 0.000001},
  "metadata": {
    "difficulty": "introductory",
    "parameters": {},
    "generator_version": 1
  }
}
```

The public form removes `expected`, `tolerance`, and generator parameters, then
adds the answer contract. A public record cannot be passed to `grade`.

## Model response

```json
{
  "task_id": "circuits.voltage_divider.012345abcdef",
  "provider": "manual-web",
  "model": "user-visible model label",
  "text": "{\"answer\": 3.3, \"unit\": \"V\"}",
  "latency_ms": null,
  "usage": {},
  "error": null,
  "metadata": {}
}
```

Provider errors are records, not dropped rows. `error` contains a sanitized
message; the response may then have empty `text`.

## Grade

```json
{
  "task_id": "circuits.voltage_divider.012345abcdef",
  "provider": "manual-web",
  "model": "user-visible model label",
  "pack": "circuits",
  "template": "voltage_divider",
  "correct": true,
  "error_type": "correct",
  "expected_value": 3.3,
  "expected_unit": "V",
  "observed_value": 3.3,
  "observed_unit": "V",
  "absolute_error": 0.0,
  "response_text": "{\"answer\": 3.3, \"unit\": \"V\"}",
  "prompt": "…",
  "latency_ms": null,
  "usage": {},
  "cost": null,
  "parse_mode": "json",
  "details": {}
}
```

## Pricing

Pricing is user-supplied JSON:

```json
{
  "notice": "Replace every placeholder with a current official source.",
  "models": [
    {
      "provider": "provider",
      "model": "model-id",
      "currency": "USD",
      "source": "provider pricing page URL",
      "verified_at": "YYYY-MM-DD",
    "input_per_million": 0.0,
    "output_per_million": 0.0
    }
  ]
}
```

The lookup key is `provider/model`. Missing or invalid prices produce a missing
cost, never zero cost.

## Compatibility policy

Fields may be added in minor releases. Readers should ignore unknown fields.
Removing or changing the meaning of an existing field requires a major release.
Generator behavior is separately identified by `generator_version`.

## Audit output

`ohmjudge audit` writes one JSON object containing the suite commitment, task,
pack, template, model, response, and grade counts; per-model coverage; a
recomputation verdict; warnings; and integrity errors. `status` is `pass` only
when the `errors` list is empty.

## Comparison output

`ohmjudge compare` writes one JSON object with the two exact provider/model
selectors, shared-task counts, the four paired correctness cells, observed
accuracy delta, exact two-sided McNemar p-value, per-pack breakdowns, and
warnings. Missing task IDs are excluded from the paired calculation and produce
a warning.
