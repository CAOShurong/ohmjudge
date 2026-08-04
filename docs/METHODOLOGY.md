# Methodology

OhmJudge measures whether a model can solve freshly parameterized,
self-contained electrical-engineering calculations and obey a compact answer
contract. It does not measure general intelligence or professional engineering
competence.

## Evaluation unit

A task contains:

- a natural-language question;
- a requested output unit;
- a private expected value;
- an absolute and relative tolerance;
- generator metadata and a deterministic seed.

The model receives only the prompt. Grading is a pure local computation: parse
the response, normalize a recognized unit, compare the numeric value, and assign
an error category.

## Suite generation

`ohmjudge generate --seed S --count N` chooses task templates and parameters
from Python's seeded pseudorandom generator. A task ID is the first 12
hexadecimal characters of SHA-256 over its pack, template, seed, and parameters.
A suite commitment is SHA-256 over the canonical private task records.

This gives repeatability, not secrecy. Anyone who knows the seed and generator
version can reconstruct the answers. For a contamination-sensitive study:

1. choose an unpublished random seed;
2. generate private tasks and public prompts;
3. publish the suite commitment before collecting responses;
4. keep the private task file local;
5. release the private file after collection and publish every response.

## Parsing and grading

The preferred response is:

```json
{"answer": 123.4, "unit": "kHz"}
```

The parser first looks for a JSON object. If none can be decoded, it attempts a
conservative numeric fallback. The grade records `parse_mode` so analyses can
separate strict contract compliance from mathematical correctness.

Recognized compatible units are converted to the expected base dimension.
Correctness is:

```text
absolute_error <= max(absolute_tolerance,
                      relative_tolerance * abs(expected_value))
```

The current taxonomy distinguishes correct responses, provider errors, empty
responses, parse errors, non-numeric answers, missing units, unknown units,
incompatible dimensions, and numeric errors.

## Statistics

The report shows observed accuracy and a 95% Wilson score interval. Wilson
intervals behave more sensibly than a normal approximation for small samples or
rates near zero and one. They quantify sampling uncertainty from the chosen
task suite; they do not account for prompt sensitivity, provider drift,
contamination, or correlated task templates.

The price–accuracy chart uses only prices supplied by the experimenter and token
counts reported by a provider. Its horizontal spacing is logarithmic so both
small and large cost differences remain visible. A point is Pareto-efficient if
no observed model is both at least as accurate and no more expensive, with one
strict advantage. Missing or partial costs stay missing rather than being
treated as free.

## Threats to validity

### Construct validity

Current tasks emphasize scalar calculations and unit discipline. A high score
does not establish the ability to read a schematic, debug a lab setup, design a
safe power system, select parts under supply constraints, write HDL, or make
trade-offs under ambiguous requirements.

### Contamination

Procedural parameters reduce exact question memorization, but the governing
formulas and template phrasing can still be familiar. A public seed is not a
private test. Generator diversity and withheld template families matter more
than simply increasing `count`.

### Independence

Tasks produced by the same template are correlated. Treating all generated
instances as independent can make confidence intervals look narrower than the
underlying template diversity warrants. Report per-template results and the
number of distinct templates.

### Repeated sampling

Web products may silently change models, system prompts, routing, and tool use.
Record the visible product/model label, date, settings, and collection method.
A single run is a snapshot, not a permanent model property.

### API versus web products

An API model ID and a web-app label are not interchangeable evidence. Web
products may add retrieval, reasoning controls, memory, or routing. Compare them
only when the difference is explicit in the report.

### Data handling

The standalone lab embeds private expected answers so it can grade locally.
Do not publish that HTML before collection if answer secrecy matters.

## Reporting checklist

A credible result should disclose:

- repository version or commit;
- suite commitment, seed policy, task count, and template count;
- exact model/product labels and collection dates;
- API parameters or web-app settings;
- whether tools, browsing, files, or retries were allowed;
- raw responses and unedited grades;
- pricing source and effective date, if cost is reported;
- exclusions, failures, and manual interventions.

Synthetic data must remain labelled synthetic. OhmJudge's bundled demo exists
to exercise the pipeline and must never be cited as a model comparison.
