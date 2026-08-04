# Running a defensible experiment

This guide separates a quick personal comparison from a result suitable for
public discussion.

## 1. Define the protocol before looking at scores

Record the question, exact model or product labels, web or API mode, visible
reasoning and tool settings, allowed manual intervention, seed policy, included
packs, collection date, and failure rules. Do not change these rules after
seeing which model wins without labelling the new run exploratory.

## 2. Generate and commit the suite

```bash
ohmjudge generate \
  --count 100 \
  --seed YOUR_PRIVATE_SEED \
  --output tasks.private.jsonl \
  --public-output prompts.public.jsonl
```

Save the printed SHA-256 commitment somewhere timestamped before collection.
The default 50-task suite covers every current template once. Larger suites
repeat template families with new parameters; they do not create new independent
capabilities.

## 3. Collect without API access

```bash
ohmjudge lab --tasks tasks.private.jsonl --output lab.html
```

Use one model label per visible product configuration. Do not silently merge
answers from two modes under one label. Export the response JSONL and preserve it
unchanged.

## 4. Grade and audit

```bash
ohmjudge grade \
  --tasks tasks.private.jsonl \
  --responses responses.jsonl \
  --output grades.jsonl

ohmjudge audit \
  --tasks tasks.private.jsonl \
  --responses responses.jsonl \
  --grades grades.jsonl \
  --require-complete \
  --output audit.json
```

The audit checks duplicate and unknown references, expected-value finiteness,
units, tolerances, per-model coverage, and deterministic recomputation of every
supplied grade.

## 5. Compare paired outcomes

Accuracy differences on the same tasks are paired data. OhmJudge reports the
four correctness cells and an exact two-sided McNemar test:

```bash
ohmjudge compare \
  --grades grades.jsonl \
  --baseline-provider manual-web \
  --baseline-model "Model A" \
  --challenger-provider manual-web \
  --challenger-model "Model B" \
  --output comparison.json
```

The p-value asks whether the two discordant cells are balanced under an equal
error-rate null. It does not measure practical importance, correct for many
comparisons, or remove template correlation. The command warns when fewer than
20 pairs disagree.

## 6. Build and publish the evidence

```bash
ohmjudge report \
  --tasks tasks.private.jsonl \
  --grades grades.jsonl \
  --title "Fresh EE benchmark — protocol name" \
  --note "Collection date, product mode, and disclosed deviations" \
  --output report.html
```

A reproducible release should contain protocol notes, public prompts, the
pre-collection commitment, raw responses, grades, audit output, comparisons,
the report, the repository commit, and the private task file after the secrecy
window closes. Remove credentials and unrelated personal chat content, but keep
provider errors and inconvenient negative results.
