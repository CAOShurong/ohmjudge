# Provider setup

You do not need an API to use OhmJudge. The recommended starting point is:

```bash
ohmjudge generate --count 40 --seed 2026 --output tasks.private.jsonl
ohmjudge lab --tasks tasks.private.jsonl --output ohmjudge-lab.html
```

Open the HTML file, copy prompts to the model's ordinary website, paste answers
back, and export the response file.

## Important distinction

A paid ChatGPT, Claude, Kimi, GLM, or Qwen web subscription does not necessarily
include API usage. API billing, credentials, model IDs, quotas, and data policies
are provider-specific. Check the provider's current official documentation
before a paid batch run.

OhmJudge reads keys from environment variables and never prints their values.
Use `ohmjudge doctor` to check whether variables are present.

## OpenAI Responses

Official reference: [Create a model response](https://platform.openai.com/docs/api-reference/responses/create).

PowerShell:

```powershell
$env:OPENAI_API_KEY = "your-key"
ohmjudge run `
  --tasks tasks.private.jsonl `
  --provider openai-responses `
  --model YOUR_MODEL_ID `
  --base-url https://api.openai.com/v1 `
  --output responses.openai.jsonl
```

The adapter sends `store: false`, records returned usage, and extracts
`output_text` message parts.

## Anthropic Messages

Official reference: [Create a Message](https://platform.claude.com/docs/en/api/messages/create).

```powershell
$env:ANTHROPIC_API_KEY = "your-key"
ohmjudge run `
  --tasks tasks.private.jsonl `
  --provider anthropic `
  --model YOUR_MODEL_ID `
  --base-url https://api.anthropic.com/v1 `
  --api-key-env ANTHROPIC_API_KEY `
  --output responses.anthropic.jsonl
```

## OpenAI-compatible endpoints

The compatible adapter posts to `<base-url>/chat/completions`. The following
providers document compatible interfaces, but endpoints and model IDs may
change:

- [Kimi API overview](https://platform.kimi.ai/docs/api/overview)
- [GLM API introduction](https://docs.bigmodel.cn/cn/guide/start/introduction)
- [Qwen Model Studio API guide](https://help.aliyun.com/en/model-studio/first-api-call-to-qwen)

Generic command:

```powershell
$env:PROVIDER_API_KEY = "your-key"
ohmjudge run `
  --tasks tasks.private.jsonl `
  --provider openai-compatible `
  --model YOUR_MODEL_ID `
  --base-url PROVIDER_BASE_URL `
  --api-key-env PROVIDER_API_KEY `
  --output responses.provider.jsonl
```

Add `--structured-output` only when the provider documents
`response_format: {"type": "json_object"}` support.

## Replay

Replay is useful for testing the runner without any network call:

```bash
ohmjudge run \
  --tasks tasks.private.jsonl \
  --provider replay \
  --model imported-model \
  --replay responses.existing.jsonl \
  --output responses.replayed.jsonl
```

## Cost and rate-limit safety

- Start with two or three tasks.
- Keep concurrency at one until the endpoint behavior is confirmed.
- Record the exact model ID and date.
- Supply pricing yourself; do not assume bundled demo prices are current.
- Preserve provider errors rather than silently retrying until a preferred answer appears.
- Never commit `.env`, keys, or a pre-publication private task file.
