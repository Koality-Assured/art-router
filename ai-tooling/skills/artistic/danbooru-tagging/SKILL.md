---
schema_version: "2.0.0"
name: danbooru-tagging
description: >-
  Parse, normalize, and compile Danbooru tag-based prompts into the canonical
  8-slot sequence for visual diffusion models. Use when generating, optimizing,
  or translating illustration and anime prompts across model dialects (Illustrious,
  Pony, Animagine, Wan).
owner_agent: artistic-production
rank: high
isolation: mutate
on_failure: abort_and_rollback
prerequisites:
  - python
dependencies:
  required_skills:
    - isolate-work
  delegated_skills: []
  in_session_skills:
    - request-contract
    - representation-routing
    - evidence-validation
contracts:
  inputs:
    - Raw tag string or unstructured keyword list, target model dialect, optional negative tags
  outputs:
    - Canonical 8-slot compiled prompt, tailored negative prompt, estimated CLIP token budget, and dialect warnings
---

# Danbooru Tagging & Canonical Prompt Compilation

## When to use

Use when authoring, structuring, or translating tag-based illustration prompts for diffusion models trained on the Danbooru ontology (including Illustrious XL, Pony Diffusion V6, Animagine XL, NovelAI, and Wan 2.1/2.2). Common scenarios include:
- Normalizing raw user keywords into canonical Danbooru tags (resolving aliases, removing spaces).
- Sorting unstructured tags into the universal 8-slot canonical sequence to eliminate attribute bleeding.
- Translating prompts across conflicting model dialects (e.g. converting traditional `masterpiece` quality anchors into Pony `score_` chains or Animagine tail quality).
- Auditing prompt length against the 75-token CLIP attention chunk boundary.

## When not to use

Do not use for natural-language photographic prompt expansion (use general prompt engineering). Do not use for bypassing copyright, artist, or content safety boundaries. For non-tag artwork packaging, use [`production-workflow`](../production-workflow/SKILL.md).

## Criticality

High. In causal attention text encoders, token ordering dictates visual hierarchy and semantic binding. Unstructured tag sequences lead to color contamination, missing subjects, and dropped details.

## Source of truth

- [`docs/standards/danbooru-tag-ontology.md`](../../../../docs/standards/danbooru-tag-ontology.md) defines the native categories, tag groups, and relational DAGs.
- [`docs/standards/prompt-token-ordering.md`](../../../../docs/standards/prompt-token-ordering.md) defines the universal 8-slot architecture and dialect rules.
- [`references/prompt-engineering/catalogs/danbooru-tags/`](../../../../references/prompt-engineering/catalogs/danbooru-tags/) provides machine-readable schemas, group mappings, and model presets.
- [`scripts/tools/compile_prompt.py`](../../../../scripts/tools/compile_prompt.py) provides the canonical AST compiler engine and CLI.
- [`scripts/cli/harness.py`](../../../../scripts/cli/harness.py) exposes the CLI integration via `harness prompt compile`.

## Isolation

`mutate`. When compiling and generating asset prompts, manifests, or presets, execute within an isolated task worktree.

## How to use

1. Compile raw tags for Illustrious XL (default):
   ```powershell
   python scripts/cli/harness.py prompt compile -p "1girl, solo, twintails, blue_hair, school_uniform, standing, classroom, sunlight"
   ```

2. Compile and dialect-translate for Pony Diffusion V6 (applies score tokens, strips incompatible tags, sets CLIP Skip 2):
   ```powershell
   python scripts/cli/harness.py prompt compile -p "1girl, solo, twintails, blue_hair, school_uniform, standing" --model pony_v6_xl
   ```

3. Compile for Animagine XL v3 (places quality anchors at the tail):
   ```powershell
   python scripts/cli/harness.py prompt compile -p "1girl, solo, twintails, blue_hair, school_uniform, standing" --model animagine_xl_v3
   ```

4. Output machine-readable JSON for automated tool pipelines:
   ```powershell
   python scripts/cli/harness.py prompt compile -p "1girl, solo, twintails" --json
   ```

## Dry run

Validate the skill and test prompt compilation without modifying repository files:

```powershell
python scripts/ai-tooling/validate_skill.py --skill danbooru-tagging --dry-run
python scripts/cli/harness.py prompt compile -p "1girl, solo, blue_hair, school_uniform" --model illustrious_xl
```

## Security

Inherits Critical cost layers: qmd for discovery; ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root `AGENTS.md`.

- Model dialect translation strips unsupported or controversial tags per model guidelines.
- Preserves consent limits, safety thresholds, and avoids generating non-consensual depictions of real individuals. Follow [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

- Prompt tags successfully categorized into canonical 8 slots.
- Output prompt string adheres to target model dialect requirements.
- Unit test suite passes cleanly:
  ```powershell
  pytest scripts/tests/test_compile_prompt.py
  ```
