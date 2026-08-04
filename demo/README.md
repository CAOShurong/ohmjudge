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

Regenerate all files from source:

```bash
ohmjudge demo --output demo --count 50 --seed 2026
```

The generated HTML files are self-contained. Download and open either file in a
browser; no server or network connection is required.
