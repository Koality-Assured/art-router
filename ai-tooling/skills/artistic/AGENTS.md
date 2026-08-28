# Artistic skills

Shared, read-only workflows for routing art representations, normalizing artistic requests, and checking declared evidence.

## Local constraints

- Keep these skills generic and portable; link to the governing standards and validator instead of copying them.
- Use repository-relative paths and preserve explicit human-review, hold, and non-claim boundaries.
- The three skills are sibling workflows owned by `artistic-standards-reviewer`.

## Next hop

- [`evidence-validation/`](./evidence-validation/) validates manifests, handoffs, and fixity.
- [`representation-routing/`](./representation-routing/) selects representation rows and cross-cutting controls.
- [`request-contract/`](./request-contract/) preserves request parameters, negotiates host capabilities, and checks execution drift.
