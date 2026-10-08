# Artistic standards

`docs/standards/` contains reusable requirements for artwork, delivery, review, and preservation.

## Local constraints

- **Content ownership:** This folder owns normative art standards and their machine-readable contracts.
- **Placement:** Keep standards in tagged Markdown; place structured schemas and registries beside the standard they support.
- **Lifecycle:** Update the owning standard when requirements change, and state compatibility when a schema version advances.
- **Relationships:** Link retrieval aids in `supporting/`; they may route to a standard but must not restate its requirements.
- **Source of truth:** `artistic-representations.md` defines production controls; `artistic-representation-registry.json` defines canonical representation IDs and routing metadata.
- **Validation:** Run `python scripts/docs/validate_router_structure.py` for documentation metadata and the applicable art-router validator for structured contracts.
- **Escalation:** Check primary sources and hold for unresolved safety, legal, accessibility, consent, or cultural-authority requirements.
- **Local exceptions:** Record exceptions in the governing standard with an owner and review conditions.

## Next hop

- [Representation controls](./artistic-representations.md)
- [Request contract](./artistic-request-contract.md)
- [Representation registry](./artistic-representation-registry.json)
