# Synthetic demonstration

Every model name, response, latency, token count, and price in this directory is
synthetic. These files show how a complete OhmJudge experiment fits together;
they are not evidence about any real model.

- `tasks.private.jsonl` contains the local answer keys.
- `prompts.public.jsonl` is the safe prompt-only form.
- `responses.synthetic.jsonl` contains generated fixture responses.
- `grades.synthetic.jsonl` is the deterministic grading output.
- `audit.synthetic.json` recomputes the bundle and verifies full coverage.
- `comparison.synthetic.json` demonstrates paired outcome statistics.
- `synthetic-pricing.json` contains fictional prices.
- `report.html` is the interactive analysis.
- `no-api-lab.html` is the copy/paste evaluation interface.
- `blind-collector.html` is the answer-free collector recommended for a
  blinded response-collection workflow.

Regenerate all files from source:

```bash
ohmjudge demo --output demo --count 50 --seed 2026
```

The generated HTML files are self-contained. Download and open any of them in a
browser; no server or network connection is required. The lab includes the
private answer key for local grading. The blind collector includes only public
prompts and the suite commitment.
