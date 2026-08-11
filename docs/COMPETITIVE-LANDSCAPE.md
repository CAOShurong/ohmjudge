# Competitive landscape

OhmJudge is intentionally narrower than a general leaderboard. Its contribution
is the combination of fresh procedural EE calculations, deterministic local
grading, a no-API browser workflow, and portable evidence artifacts.

## Relevant prior work

| Project | Scope | Evaluation mechanism | What OhmJudge adds |
|---|---|---|---|
| [EEE-Bench](https://arxiv.org/abs/2411.01492) | 2,860 multimodal questions across ten electrical and electronic engineering disciplines | curated benchmark answers | reproducible seeded scalar tasks and a local copy/paste workflow |
| [CIRCUIT](https://arxiv.org/abs/2502.07980) | 510 analog-circuit reasoning questions | final-answer and unit-test evaluation | user-generated fresh suites, unit normalization, and auditable JSONL artifacts |
| [PCB-Bench](https://github.com/digailab/PCB-Bench) | multimodal PCB placement and routing over real design artifacts | artifact and design-rule evaluation | a lightweight scalar-calculation workflow that needs no EDA installation |
| [HWE-Bench](https://arxiv.org/abs/2603.18102) | board-level schematic-design tasks with datasheets | static and simulator-based evaluation | a much lighter workflow that students can run without EDA infrastructure |
| [Frontier-Eng](https://arxiv.org/abs/2604.12290) | executable generative-optimization tasks across engineering domains | task-specific verifiers | specialized introductory-to-intermediate EE calculations and no-API collection |
| [Inspect AI](https://inspect.aisi.org.uk/scoring-workflow.html) | general model-evaluation framework with deferred scoring workflows | configurable collection, logs, scorers, and metrics | a single-file answer-free collector for manual web products and EE-specific deterministic grading |
| [models.dev](https://github.com/anomalyco/models.dev) | model capability, limit, and pricing metadata | registry rather than capability benchmark | actual task generation, response evidence, grading, and experiment reports |
| [Open Responses](https://www.openresponses.org/) | interoperable language-model response API specification | protocol conformance | provider-independent research evaluation, including use without an API |

The table does not claim that OhmJudge replaces these projects. EEE-Bench and
CIRCUIT provide broader curated knowledge; PCB-Bench and HWE-Bench reach realistic
schematic design; Frontier-Eng tests open-ended engineering optimization.
OhmJudge's present tasks are smaller and easier to audit.

Inspect AI demonstrates the established value of collecting outputs before
applying a scorer. OhmJudge does not claim to invent deferred scoring. Its
narrow addition is an answer-free, dependency-free HTML collector that can be
handed to someone using an ordinary web product, with every response bound to
the committed EE suite and grading deferred to the private task file.

## Gap being tested

The working hypothesis is that individual researchers need an evaluation loop
between a static academic benchmark and a full benchmark infrastructure stack:

1. create a fresh, committed suite;
2. test any web product without buying API access;
3. grade with code instead of another language model;
4. inspect failures at task level;
5. publish enough artifacts for another person to audit the claim.

This is a product and methodology hypothesis, not evidence of unique novelty.
Manual-input support also exists in general evaluation frameworks; OhmJudge's
claim is the integrated EE-specific chain, not the invention of copy/paste
collection. Adoption, external task-pack contributions, and independently
reproduced experiments are the tests that matter.

## Deliberate non-goals

- A universal model intelligence score.
- A live scraped leaderboard.
- A claim that procedurally generated questions are contamination-proof.
- A replacement for SPICE, MATLAB, EDA suites, or laboratory validation.
- A price database that silently goes stale.
- Model rankings derived from undisclosed or synthetic responses.

## Directions with the strongest research value

- Symbolic and property-based validators for families of equivalent answers.
- Schematic-image packs with programmatic circuit extraction.
- SPICE-backed analog tasks and counterexample traces.
- HDL packs graded by simulation and formal properties.
- Bilingual terminology studies across English and Chinese prompts.
- Template-held-out evaluation to distinguish formula recognition from transfer.

Each direction should be added only with a reproducible verifier and a clear
account of what the score can and cannot establish.
