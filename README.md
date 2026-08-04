<div align="center">
  <img src="docs/assets/hero.svg" width="920" alt="OhmJudge — fresh, executable electrical-engineering benchmarks for frontier models">

  <p><strong>Fresh, executable electrical-engineering benchmarks for frontier models.</strong></p>

  <p>
    <a href="https://github.com/CAOShurong/ohmjudge/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/CAOShurong/ohmjudge/actions/workflows/ci.yml/badge.svg"></a>
    <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-5dd6c7"></a>
    <img alt="zero runtime dependencies" src="https://img.shields.io/badge/runtime%20dependencies-0-9cf">
    <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-3776ab">
  </p>
</div>

OhmJudge generates fresh numerical electrical-engineering problems, gives the same prompts to any model, and grades the answers locally with executable rules. Its default workflow needs **no API key**: copy a prompt into ChatGPT, Claude, Kimi, GLM, Qwen, or another web app, paste the answer back, and export a reproducible result.

> [!IMPORTANT]
> OhmJudge is an early research tool, not an authoritative model ranking. The included dashboard uses **clearly labelled synthetic responses** to demonstrate the reporting pipeline. It makes no claim about the named commercial models.

## Why this exists

Static benchmark questions eventually leak into training data. LLM-as-a-judge scores can also change when the judge model or prompt changes. OhmJudge takes a narrower route:

- **fresh tasks** — deterministic generators create a new suite from a recorded seed;
- **executable grading** — numeric answers, units, tolerances, and error categories are checked in Python;
- **model-agnostic use** — the no-API lab works with any browser-based model;
- **auditable artifacts** — tasks, responses, grades, prices, and suite commitments are plain JSONL/JSON;
- **useful diagnostics** — see domain accuracy, confidence intervals, cost, latency, error types, and the price–accuracy Pareto frontier.

It currently includes 20 task templates across circuits, signals, control, and communications.

<div align="center">
  <img src="docs/assets/workflow.svg" width="900" alt="OhmJudge reproducible evaluation workflow">
</div>

## Try it in two minutes — no API required

```bash
git clone https://github.com/CAOShurong/ohmjudge.git
cd ohmjudge
python -m pip install -e .

# Generate a private grading file plus a safe-to-share prompt file.
ohmjudge generate \
  --count 40 \
  --seed 2026 \
  --output tasks.private.jsonl \
  --public-output prompts.public.jsonl

# Build one self-contained HTML file. Open it in any browser.
ohmjudge lab --tasks tasks.private.jsonl --output ohmjudge-lab.html
```

In the lab:

1. enter a model label;
2. copy the current prompt into the model's normal web chat;
3. paste its answer back;
4. grade locally and export `responses.jsonl`.

The model is instructed to return:

```json
{"answer": 12.34, "unit": "kHz"}
```

OhmJudge tolerates surrounding prose and a numeric fallback, but records the parse mode so a strict analysis can exclude fallback parsing.

## Build a shareable report

```bash
ohmjudge grade \
  --tasks tasks.private.jsonl \
  --responses responses.jsonl \
  --output grades.jsonl

ohmjudge report \
  --tasks tasks.private.jsonl \
  --grades grades.jsonl \
  --title "My frontier-model EE study" \
  --note "Web apps, zero-shot, collected 2026-08-04" \
  --output report.html
```

The report is a self-contained interactive HTML file—no server, CDN, tracker, or JavaScript dependency. It includes:

- model-level accuracy with Wilson 95% confidence intervals;
- a domain heatmap;
- error taxonomy;
- latency and token summaries when available;
- user-supplied price estimates and a log-scaled price–accuracy Pareto frontier;
- filters and expandable per-task evidence.

Generate the bundled synthetic demo with:

```bash
ohmjudge demo --output demo
```

## What is tested

| Pack | Example templates | Deterministic checks |
|---|---|---|
| Circuits | voltage divider, RC cutoff, clipped op-amp, Thevenin resistance, series current | value, dimension, unit conversion, tolerance |
| Signals | RMS, Nyquist rate, alias frequency, sequence energy, convolution length | numeric or integer equality |
| Control | time constant, overshoot, settling time, pole radius, DC gain | formula-grounded numeric checks |
| Communications | Shannon capacity, free-space path loss, thermal noise, QPSK rate, link budget | logarithmic and linear-unit checks |

The generators target calculation discipline and unit handling. They do **not** yet cover schematic images, open-ended design, HDL, RF layout, semiconductor process design, or safety certification. See [Methodology](docs/METHODOLOGY.md) for the exact validity boundary.

## Optional API runners

The browser workflow is the default. If you later want repeatable batch experiments, adapters are included for:

- OpenAI Responses;
- OpenAI-compatible Chat Completions, including providers that expose compatible endpoints;
- Anthropic Messages;
- replay from an existing response file.

API access is separate from a normal web subscription. OhmJudge never prints credential values. See [Provider setup](docs/PROVIDERS.md) before running a paid endpoint.

```bash
ohmjudge doctor
ohmjudge run \
  --tasks tasks.private.jsonl \
  --provider openai-responses \
  --model YOUR_MODEL_ID \
  --output responses.jsonl
```

## Reproducibility contract

Every generated task has:

- a stable ID derived from its content;
- a pack, template, and generation seed;
- a prompt and private expected value;
- an accepted unit and absolute/relative tolerance;
- generator parameters for audit.

`generate` also prints a SHA-256 suite commitment. Publish the commitment and public prompts before collecting answers; release the private task file after the evaluation window if you want others to audit your result.

Read the [methodology](docs/METHODOLOGY.md), [data schemas](docs/SCHEMA.md), and [competitive landscape](docs/COMPETITIVE-LANDSCAPE.md) before reporting a serious comparison.

## Project map

```text
src/ohmjudge/
├── packs/          # seeded EE task generators
├── providers/      # optional remote runners
├── generate.py     # suites and commitments
├── grade.py        # deterministic validator
├── lab.py          # no-API browser workflow
├── report.py       # standalone interactive report
└── stats.py        # confidence intervals and Pareto frontier
```

## Contributing

The most valuable contribution is a new task pack with an independently checkable answer—not a longer prompt. Start with [Writing a pack](docs/WRITING_A_PACK.md), then read [CONTRIBUTING.md](CONTRIBUTING.md).

Please cite the repository with the metadata in [CITATION.cff](CITATION.cff). OhmJudge is released under the [MIT License](LICENSE).
