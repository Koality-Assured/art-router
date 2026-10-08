# Artistic skills

Portable workflows for creating artwork and reviewing requests, representation routes, and declared evidence.

## Local constraints

- Keep these skills generic and portable; link to the governing standards and validator instead of copying them.
- Use repository-relative paths and preserve explicit human-review, hold, and non-claim boundaries.
- `evidence-validation`, `representation-routing`, and `request-contract` are read-only review workflows owned by `artistic-standards-reviewer`.
- `production-workflow` is the separate, write-capable artwork creation and packaging workflow owned by `artistic-production`.
- Production output still follows the applicable standards and human review gates.

## Next hop

- [`evidence-validation/`](./evidence-validation/) validates manifests, handoffs, and fixity.
- [`representation-routing/`](./representation-routing/) selects representation rows and cross-cutting controls.
- [`request-contract/`](./request-contract/) preserves request parameters, negotiates host capabilities, and checks execution drift.
- [`production-workflow/`](./production-workflow/) creates artwork and packages output under declared host capabilities.
