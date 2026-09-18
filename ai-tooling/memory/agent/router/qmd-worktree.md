---
Status: Active
Last updated: 2026-08-27
Scope: art-router qmd indexing
---

# QMD Worktree Indexing

- **Owner agent:** `router`
- **Status:** Active
- **Last updated:** 2026-08-27

- Running `scripts/qmd/refresh_qmd_index.py` from the art-router worktree used the existing qmd collection roots under `C:\Code\ai-router`, so the new worktree Markdown was not indexed there.

## Environment Quirks & Tooling Gotchas

- The refresh command completed successfully but reported the external collection root in its output. Verify collection roots before treating a refresh as proof that a new checkout or worktree is searchable.

## Learned Recovery Strategies

- Use the script's `--dry-run` first, inspect the resolved collection roots, then refresh with explicit user approval. Reconfigure or refresh the intended collection separately when a worktree must be searchable.

## Critical Success Factors

- Preserve qmd as the Markdown discovery path, but do not claim fresh retrieval coverage until the collection root matches the checkout being changed.
