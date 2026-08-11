# Changelog

All notable changes are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-08-11

### Added

- An answer-free, self-contained `collect` workflow for manual web-product
  experiments, with browser-local resume and JSONL checkpoint export/import.
- Suite-commitment binding on collector, lab, replay, and API-runner response
  records.
- Cross-platform Python CI, CodeQL analysis, and pinned GitHub Actions
  dependencies.

### Changed

- Audits now report matched, missing, and mismatched response commitments.
- A present mismatched commitment is always an integrity error; strict protocol
  mode also requires the commitment field.
- The public demo and project site lead with blind collection while retaining
  the answer-bearing lab for personal practice.
- Release automation now tests before publishing, verifies tag/version parity,
  builds distributions once, writes checksums, and creates attestations.

## [0.2.0] - 2026-08-04

### Added

- Capture-protocol fields in the no-API lab for surface, visible settings,
  tools, and retry policy.
- Strict `audit --require-protocol` validation with per-model metadata coverage.
- Versioned wheel installation instructions and release checksum policy.

### Changed

- Rebuilt the README figures, project site, no-API lab, and report in a
  restrained, print-inspired academic visual system.
- Clarified the project's narrow decision boundary and competitive position.
- Upgraded GitHub Actions and added build-and-install package verification.

## [0.1.0] - 2026-08-04

### Added

- Fifty seeded task templates across ten electrical-engineering domains.
- Deterministic grading with unit conversion, tolerances, and error taxonomy.
- A self-contained no-API copy/paste evaluation lab.
- Optional OpenAI Responses, OpenAI-compatible, Anthropic, and replay providers.
- Resume-safe response collection.
- Interactive standalone reports with confidence intervals and a price–accuracy Pareto frontier.
- Cross-artifact integrity audits and exact paired McNemar comparisons.
- A responsive project site with a generated no-API lab and synthetic report.
- Synthetic demo artifacts, schemas, methodology, and contribution guides.

[Unreleased]: https://github.com/CAOShurong/ohmjudge/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/CAOShurong/ohmjudge/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/CAOShurong/ohmjudge/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/CAOShurong/ohmjudge/releases/tag/v0.1.0
