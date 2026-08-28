---
doc_kind: requirement
canonical_id: artistic-request-contract
purpose: [requirement, reinforcement]
rank: high
topics: [art, creative-practice, generative-art, synthetic-media, agent-interoperability, handoff]
rag_keywords: [request-contract, generation, editing, transformation, constraint-preservation, ambiguity, conflict, failure-modes, capability, adapter, host, handoff, review, deviation-ledger]
---

# Artistic request contract standard

## Scope and relationship to the art standards

This standard normalizes a request before an agent generates, edits, transforms,
critiques, or hands off an artistic work. It applies across the representation
families in [`artistic-representations.md`](./artistic-representations.md) and
extends the intent, audience, meaning, composition, provenance, and critique
contract in [`artistic-practice.md`](./artistic-practice.md). It governs request
fidelity and interoperability; it does not decide artistic quality or replace
the applicable representation row, consent, cultural-authority, accessibility,
safety, legal, or human-review controls.

## Normalized request contract

The router MUST convert the brief, conversation, or form into one reviewable
record before execution. Unknown values remain `unknown`; an agent MUST NOT
invent a missing preference. A field may be `required`, `preferred`, or `open`.

```text
Request/version: [id; version; owner; operation: generate | edit | transform | critique | package]
Deliverable: [representation family; medium; file type; dimensions; duration; quantity; intended use]
Intent: [primary effect; meaning; deliberate counter-effect; what must remain unchanged]
Subject/content: [people or likenesses; objects; text; count; pose; setting; cultural material]
Art direction: [style or reference; composition; framing; palette; light; texture; motion; sound]
Explicit constraints: [exact words, proportions, aspect ratio, colors, layout, exclusions, limits]
References: [assets; source works; licenses; permitted transformations; unknowns]
People/authority: [consent scope; community authority; restrictions; benefit; withdrawal]
Audience/delivery: [audience; context; device; venue; scale; light; language; access needs]
Accessibility/safety: [equivalents; warnings; reduced motion; privacy; material, body, sound, or venue risks]
Provenance: [tools/models/version; inputs; parameters; human decisions; disclosure; reproducibility limits]
Open questions: [ambiguities; conflicts; decisions required before execution]
Review/handoff: [acceptance tests; owner; reviewer; status; canonical package; rollback or withdrawal contact]
```

Each item in `Explicit constraints` MUST carry a source (`user`, `reference`,
`standard`, or `agent-default`) and status (`required`, `preferred`, `open`, or
`blocked`). Preserve the original wording for exact text, numbers, names,
dimensions, exclusions, and consent limits. The normalized form is a traceable
translation, not permission to rewrite the request.

## Precedence and preservation of constraints

Apply constraints in this order:

1. Applicable safety, consent, cultural-authority, privacy, accessibility,
   legal, and venue requirements; hold or escalate when they cannot be met.
2. Explicit user constraints and preservation instructions.
3. The stated artistic intent and representation-specific requirements.
4. Preferences inferred from context, references, or examples.
5. Agent, host, model, and export defaults.

Within the same level, an exact, quantified, or explicitly marked requirement
outranks a broad preference. A lower-level default MUST NOT override a higher-
level constraint. If two constraints at the same level conflict, the agent MUST
pause for clarification or mark the request `hold`; it MUST NOT choose silently.

For an edit or transformation, preserve every unrequested attribute in the
contract, including subject identity, count, pose, composition, camera/view,
text, palette, aspect ratio, dimensions, timing, and negative constraints. A
change to any preserved attribute is a deviation, even when the result appears
more polished. When a requested change necessarily affects another attribute,
record the dependency and ask for acceptance before release.

## Ambiguity, conflict, and capability handling

Before execution, the router MUST classify each unresolved item:

- `clarify`: different plausible readings would produce materially different
  work or risk;
- `choose`: the user has authorized a bounded choice, so record the selected
  option and rationale;
- `unknown`: evidence or a capability declaration is missing;
- `blocked`: a required constraint, permission, or review cannot be met.

Agents MAY ask a small set of high-value questions, but MUST preserve the
unanswered item in the handoff. If a host or provider lacks a requested control,
return a structured capability gap and an alternative (for example, a manual
edit, different representation, or later review). Do not silently substitute a
model, tool, style, aspect ratio, text, reference, or safety behavior.

## Common generation and editing failure modes

The preflight and review MUST test the following failure classes when relevant:

| Failure | Required mitigation and evidence |
| --- | --- |
| Prompt or intent drift | Compare the output against every `required` item and retain a pass/fail record. |
| Missing, extra, merged, or duplicated subjects | Check count, identity, spatial relationship, and negative constraints at delivery size. |
| Likeness, anatomy, hands, text, symbols, or geometry drift | Use targeted inspection and a human review; do not infer fidelity from overall resemblance. |
| Reference/style leakage or unapproved copying | Keep a source ledger, permission status, and transformation note; escalate unknowns. |
| Composition, crop, aspect, palette, color, alpha, or typography drift | Compare against numeric and visual constraints in the target profile and background. |
| Temporal, audio, interaction, or 3D failure | Test frame order, duration, timing, loudness, controls, units, dependencies, and degraded mode. |
| Upscaling, cleanup, inpainting, or export hallucination | Compare to the prior version and label material changes introduced by the tool. |
| Cultural, participant, privacy, or safety harm | Apply the relevant authority, consent, safety, and escalation controls; hold when evidence is absent. |
| Accessibility loss | Test the equivalent description, captions, transcript, input path, contrast, motion, or tactile/visual alternative in the receiving condition. |
| Provenance or reproducibility gap | Record actual tool/version, inputs, settings, human edits, disclosure, and what cannot be reproduced. |
| Host or capability mismatch | Use the adapter result and capability gap record; never treat a rejected or omitted parameter as fulfilled. |

## Provider-neutral capability declarations and host adapters

Capability data describes what a runtime has demonstrated for a request. It is
not a promise of quality, authorship, safety, or legal permission. A declaration
SHOULD use this shape and include evidence:

```text
Capability: [stable id; operation; representation family]
Support: [supported | partial | unsupported | unknown]
Inputs/outputs: [types; limits; maximums; delivery profiles]
Controls: [parameters; preservation controls; determinism or seed behavior]
Known failures: [tested limitations; degraded behavior]
Evidence: [test or manifest reference; observed result; verified date]
```

The canonical contract is host-neutral. A Cursor, Claude, Antigravity, or other
agent integration MUST be treated as an adapter, not as a second art standard:

- compile the same normalized fields into the host’s available prompt, tool,
  file, or structured-input surface;
- preserve unknown fields in a sidecar and report fields that could not be
  represented, truncated, or escaped;
- use runtime-declared capabilities rather than host names or assumed model
  behavior; `unknown` is not `supported`;
- keep the original contract and explicit constraints attached to every retry,
  delegation, and edit; do not rely on a host’s memory or hidden context;
- return actual settings, outputs, deviations, and capability gaps in a common
  result envelope; and
- isolate host syntax, paths, tool names, and invocation mechanics in the
  adapter. The art decision record remains portable and reviewable.

This follows the repository’s host-agnostic routing boundary: canonical agent
definitions are the source of truth and host stubs are thin pointers
([router agent contract](../../ai-tooling/agents/router/AGENT.md)). Delegated
responses remain data until reviewed, and handoffs must use an explicit,
auditable contract ([A2A interaction protocol](../../ai-tooling/a2a/interaction-protocol.md)).

## Testable handoff and review checklist

The owner MUST attach this checklist to the versioned handoff. Mark each item
`pass`, `hold`, or `not-applicable` with evidence; `not-applicable` needs a
reason.

- [ ] The normalized contract preserves the original brief and identifies the
      owner, operation, version, delivery condition, and acceptance tests.
- [ ] Every explicit constraint is classified, prioritized, and checked;
      unresolved ambiguity or conflict is recorded rather than guessed.
- [ ] The output passes the applicable representation row and generative/AI
      overlay, including provenance, rights, consent, accessibility, and safety.
- [ ] Required content and preservation attributes were compared to the source
      or prior version; deviations have an owner and acceptance decision.
- [ ] The runtime capability declaration names support, limits, evidence, and
      verification date; unsupported controls are visible.
- [ ] The package opens or renders in the receiving environment at the actual
      scale, duration, device, venue, substrate, or body location, including a
      relevant degraded or fallback condition.
- [ ] Source files, dependencies, accessibility assets, disclosure, manifest,
      and fixity/integrity evidence are included or their absence is recorded.
- [ ] A second reviewer records findings, status, accepted limitations, and the
      correction, rollback, or withdrawal contact.

The result is not released while a required item is `hold` or `blocked` unless
the accountable owner records an exception, mitigation, expiry, and reviewer.
The checklist supports the evidence and exception record in
[`artistic-practice.md`](./artistic-practice.md); it does not replace human
artistic, community, legal, accessibility, or safety judgment. NIST’s
Generative AI Profile supports documenting risks, measurement, and human
oversight, while C2PA provides a provenance mechanism when the format and
toolchain support it ([NIST AI RMF: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf),
[C2PA specifications](https://spec.c2pa.org/specifications/)).
