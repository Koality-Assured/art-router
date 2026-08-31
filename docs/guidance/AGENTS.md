# Guidance AGENTS

`docs/guidance/` owns repeatable operational playbooks that implement or explain repository standards. It is distinct from `docs/standards/`, which owns normative requirements.

## Local ownership

- **Content ownership:** `documentation-ops` owns durable playbooks here; subject-matter reviewers own factual review for their domain.
- **Placement:** Use kebab-case Markdown pages directly under this folder. Keep provider-specific workflows scoped to their provider and link universal controls in `docs/standards/`.
- **Lifecycle:** Promote validated operational guidance from research or project work only with explicit authorization. Revise in place when provider behavior changes; retire stale pages by an explicit replacement or archive decision.
- **Relationships:** Guidance may link to standards, research, supporting notes, and vendor primary sources. It must not redefine standards, copy research archives wholesale, or make `scratch/` a source.
- **Source of truth:** This folder is the source of truth for operational sequencing and checklists. Standards remain authoritative for MUST controls; vendor pages remain authoritative for current provider capabilities.
- **Validation:** Durable pages require YAML frontmatter, kebab-case names, `python scripts/docs/validate_router_structure.py`, `python scripts/docs/run_markdownlint.py`, and `python scripts/qmd/refresh_qmd_index.py` after indexed Markdown changes.
- **Escalation:** Use the Ambiguity Gate for conflicting requirements, unsupported provider capabilities, rights or likeness uncertainty, cultural-authority questions, and material changes to the standards boundary. Request fresh research when vendor documentation or model IDs have changed.
- **Local exceptions:** `README.md` is a human-only folder index and has no durable-page frontmatter. All other playbooks are durable Markdown and must retain the repository security rules, provenance limits, and explicit non-claims.
