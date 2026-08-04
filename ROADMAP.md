# Roadmap

The roadmap is organized by verifier depth, not by model marketing cycles.
Items move into a release only when their expected behavior can be tested
without asking another language model for the verdict.

## 0.2 — richer deterministic tasks

- Property-based generator sweeps for every pack.
- Template-balanced sampling when arbitrary pack subsets are selected.
- Symbolic equivalence for simple transfer functions and Boolean expressions.
- CSV and Markdown summary export.
- Experiment manifests with declared collection settings and immutable hashes.

## 0.3 — simulator-backed evaluation

- SPICE-backed DC operating-point and transient tasks.
- Verilog testbench packs with bounded runtime and explicit tool versions.
- Counterexample traces embedded in grade records.
- Container recipes for reproducible optional simulator environments.

## 0.4 — multimodal electrical engineering

- Schematic rendering from generated circuit graphs.
- Programmatic answer keys independent of the rendered image.
- OCR-robust labels and accessibility descriptions.
- Image perturbation tests that preserve circuit semantics.

## Research track

- English–Chinese prompt equivalence studies.
- Template-held-out transfer protocols.
- Repeated-run variance for routed web products.
- Hierarchical uncertainty estimates that account for shared templates.
- Calibration tasks where a model must abstain when the prompt is under-specified.

## Out of scope without a safety case

- Automatic control of physical laboratory equipment.
- Claims of professional certification or design safety.
- Uploading private chats or unpublished answer keys to third-party services.
- A live leaderboard that cannot expose its raw response evidence.

Proposals should start with the failure mode to measure, the executable
verifier, and the validity boundary. See [Writing a pack](docs/WRITING_A_PACK.md).
