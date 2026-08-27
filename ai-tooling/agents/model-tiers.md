---
doc_kind: process
canonical_id: agent-model-tiers
purpose: [process]
rank: high
topics: [agents]
rag_keywords: [model_tier, fast, standard, high, max, platform-native, host]
---

# Agent model tiers

Orchestrators pick a reasoning tier and a **platform-native** model when spawning specialists. Default is **standard** unless the human specified another tier.

## Tiers

| Tier | Reasoning | Host examples |
| --- | --- | --- |
| `fast` | low | cheapest fastest model on that host |
| `standard` | mid | GPT Luna; Cursor Grok 4.5; Gemini 3.7 Flash |
| `high` | high | GPT Terra; Cursor Grok 4.6; Gemini 3.7 Flash |
| `max` | max | GPT Sol; Cursor Grok 4.6; Gemini 3.1 Pro |

## Platform-native selection

The orchestrator selects the column for the **current host** and never defaults to another vendor's model on a host that has first-party models. Cursor → Cursor models (never default GPT/Claude on Cursor). ChatGPT/Codex → GPT models. Antigravity → Gemini models.

Product names in the table are the human-facing map. Host picker IDs change and are host-local operational data; do not persist them in cross-host canonical contracts.

New agents get `model_tier: standard` unless the human specifies otherwise.

## Secondary model quotas and pacing

When using secondary or quota-metered models, down-tier research and inspection workers to the configured research tier. Keep expensive models for orchestration and synthesis. The runtime profiles in [`../../config/harness.config.json`](../../config/harness.config.json) define concurrency, pacing, and 429 recovery policy; the reusable parsing and batching helpers live in [`../../scripts/_lib/pacing.py`](../../scripts/_lib/pacing.py).

Under `metered_secondary`, limit active subagents to the configured profile maximum and honor reset windows instead of retrying aggressively. Enterprise or explicitly unmetered hosts may use the `unmetered` profile.

## Related

| Doc | Role |
| --- | --- |
| [`AGENTS.md`](./AGENTS.md) | Agent authoring rules |
| [`../a2a/agent-cards/README.md`](../a2a/agent-cards/README.md) | Host cards (`type: host`; migration note only) |
| [`../skills/meta/isolate-work/SKILL.md`](../skills/meta/isolate-work/SKILL.md) | Isolate then spawn |
