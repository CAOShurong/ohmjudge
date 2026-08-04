# Contributing

OhmJudge welcomes focused, testable contributions. The best additions improve
what can be measured, not how impressive the benchmark sounds.

## Good first contributions

- Add unit aliases with conversion tests.
- Add an adversarial parser case.
- Improve keyboard or screen-reader behavior in the standalone lab.
- Add a task template whose answer can be calculated independently.
- Document a provider-compatible endpoint using its official documentation.

## Development

```bash
git clone https://github.com/CAOShurong/ohmjudge.git
cd ohmjudge
python -m pip install -e .
python -m unittest discover -s tests -v
ohmjudge demo --output build/demo
```

Runtime code must remain dependency-free. Development tooling may be proposed,
but CI must always retain a standard-library-only test path.

## Pull-request checklist

- Explain the measurement gap the change addresses.
- Add tests for success and failure cases.
- Keep generators deterministic for a fixed seed.
- Never include an API key, private benchmark answer file, or unlicensed dataset.
- Do not claim a model result without the underlying response and grade artifacts.
- Update the relevant documentation.

New generators must follow [Writing a pack](docs/WRITING_A_PACK.md).

## Research integrity

Synthetic, partial, cherry-picked, or manually corrected results must be labelled.
Do not submit marketing screenshots as benchmark evidence. If collection settings
differ between models, disclose the difference beside the comparison.

By participating, you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
