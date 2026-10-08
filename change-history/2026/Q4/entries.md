# Change history — 2026 Q4

Entries newest first. Append via `python scripts/change-history/append_change_history.py` only.

## Entries





### 2026-10-08 — Summarize art bundle routes in text output

- **Requesting user:** Robbie
- **AI agent:** Codex
- **User request:** Fix the schema 1.3 art-router text report so bundle cases show their routes.
- **Summary:**
  - Derive a stable route summary from 1.3 components while preserving legacy case.medium labels.
  - Add regression coverage for 1.3 summaries and 1.0–1.2 formatting.

### 2026-10-08 — Align art manifest 1.3 component shape

- **Requesting user:** Robbie
- **AI agent:** Codex
- **User request:** Correct schema 1.3 art request and bundle fields to match the normative component shape.
- **Summary:**
  - Use route, nested asset.type, and primary/supporting roles; reject old 1.3 field names and adjacent role.
  - Add a prose-conforming mixed-media fixture and keep 1.0–1.2 manifests compatible.

### 2026-10-08 — Expand art router representations

- **Requesting user:** Robbie
- **AI agent:** Codex
- **User request:** Expand the art router with validated representation coverage, production guidance, official references, and sample gallery entries.
- **Summary:**
  - Add registry-driven routing and schema 1.3 mixed-media validation while preserving manifest 1.0–1.2.
  - Add a write-capable production workflow, focused standards captures, and package-validated sample metadata.

### 2026-10-07 — Allow factual employer-mark identification

- **Requesting user:** portfolio owner
- **AI agent:** Cursor agent
- **User request:** Represent résumé-style employer marks as factual identifiers without asserting a separate per-logo written license.
- **Summary:**
  - Added a factual-identification source status for organization marks with identification-only scope. Kept publisher cinematics gated on permission evidence and clarified that source context is not a license or legal opinion.

### 2026-10-07 — Third-party mark and publisher embed contract

- **Requesting user:** Portfolio owner
- **AI agent:** Codex
- **User request:** Extend the Art router for company marks and cinematic embeds.
- **Summary:**
  - Added schema 1.2 with per-source usage evidence, kind-specific scopes, and constrained YouTube embed controls.
  - Added a synthetic fixture, pass/hold tests, routing guidance, and source-grounded policy notes.

