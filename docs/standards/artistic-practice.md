---
doc_kind: requirement
canonical_id: artistic-practice
purpose: [requirement, reinforcement]
rank: high
topics: [art, creative-practice, cultural-respect, authorship, provenance, critique]
rag_keywords: [intent, audience, context, meaning, composition, originality, cultural-respect, authorship, provenance, generation-manifest, synthetic-media, likeness, participant-consent, community-authority, withdrawal, accessibility-evidence, safety-escalation, fixity, preservation, ambiguity, critique, release-gates]
---

# Artistic practice standard

## Scope and operating model

For this standard, art is the practice of making intentional perceptual, material, and symbolic choices for an audience in a context. This is an operational model for planning and review, not a universal definition of art or a claim that every work must explain itself.

Use the four-part cycle of creating, presenting, responding, and connecting as a review spine. The National Core Arts Standards describe these processes and ask makers to refine work, convey meaning, interpret intent, apply criteria, and relate work to social, cultural, and historical context ([NCAS anchor standards](https://www.nationalartsstandards.org/content/national-core-arts-standards-anchor-standards)). For critique, separate observation, description, interpretation, and connection; that sequence is supported by MoMA’s visual-thinking foundations ([MoMA: Foundations for Engagement with Art](https://www.moma.org/visit/accessibility/meetme/practice/foundations.html)).

## Decision contract

Before release, the maker or team MUST be able to answer these questions in plain language:

- **Intent:** What should the work make possible, prompt, question, or change? Name the primary effect and any deliberate counter-effect.
- **Audience and context:** Who encounters it, where, under what conditions, and with what prior knowledge, access needs, power differences, or risk of misreading?
- **Meaning:** What does the work signify, evoke, withhold, or leave unresolved? Distinguish maker intent from audience interpretation.
- **Composition:** Which perceptual choices carry the work: scale, sequence, framing, rhythm, contrast, space, material, sound, interaction, or absence? State what is deliberately subordinate.
- **Originality and reference:** Which source works, conventions, datasets, prompts, models, or cultural forms informed it? Identify what is transformed, quoted, licensed, or still uncertain. Do not treat “original” as a legal conclusion.
- **Cultural respect:** If the work uses living heritage, Indigenous knowledge, sacred imagery, community symbols, language, or traditional cultural expressions, identify the people and context concerned, the decision authority where appropriate, the permission or consultation path, permitted and restricted uses, who benefits, and how withdrawal or correction is handled. UNESCO treats intangible heritage as living practices recognized by communities, while its 2005 Convention emphasizes mutual respect, cultural diversity, and the role of artists and communities ([UNESCO 2003 Convention](https://www.unesco.org/en/legal-affairs/convention-safeguarding-intangible-cultural-heritage), [UNESCO 2005 Convention](https://www.unesco.org/en/legal-affairs/convention-protection-and-promotion-diversity-cultural-expressions)). For Indigenous cultural heritage, traditional knowledge, and cultural expressions, apply a higher review threshold and do not assume outsider permission; UNDRIP Article 31 recognizes Indigenous peoples’ rights to maintain, control, protect, and develop them ([UNDRIP, Article 31](https://www.un.org/development/desa/indigenouspeoples/wp-content/uploads/sites/19/2018/11/UNDRIP_E_web.pdf)).
- **Authorship and provenance:** Record human decisions, collaborators, source assets, licenses, model or tool use, edits, and approvals. C2PA provides a technical way to carry origin and edit history as content provenance ([C2PA specification](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html)). **U.S.-specific legal note:** the U.S. Copyright Office says AI-assisted output may be protected where a human determines sufficient expressive elements, while a prompt alone is not enough; obtain U.S. legal review for a registration, dispute, or rights warranty ([U.S. Copyright Office, AI and Copyrightability, Part 2](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf)).
- **Production record and disclosure:** When a work is generated or materially manipulated, record the tool or model and version, input assets, prompts or procedures, exposed settings, human selections and edits, known reproducibility limits, and audience-facing disclosure. Treat missing or stripped provenance as a recorded limitation, not evidence that no synthetic process occurred ([NIST AI RMF: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf), [C2PA specifications](https://spec.c2pa.org/specifications/)).
- **People and likeness:** For recognizable participants or a person's likeness, record consent or permission scope separately for capture, editing, publication, model training, derivatives, archival retention, and withdrawal. Define who may approve, hold, restrict, correct, or request removal; escalate high-risk cases for appropriate human review. This is a production control, not a statement of universal legal rights ([NIST AI RMF: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf), [U.S. Copyright Office: Digital Replicas](https://www.copyright.gov/newsnet/2024/1048.html)).
- **Ambiguity:** Which readings, gaps, or contradictions are intentional? What must remain open, and what must be clarified for safety, access, or informed consent?
- **Critique:** Which criteria will be used, who can challenge the work, what evidence will settle a disagreement, and what change would cause a hold? Critique should identify observations before inferences and should not require a single interpretation.

## Prompt template

Use this brief before generating, commissioning, or revising a work:

```text
Make: [work, medium, version, and intended use]
Intent: [primary effect; deliberate counter-effect]
Audience/context: [people, place, time, access needs, prior knowledge, risks]
Meaning: [what is suggested, stated, quoted, withheld, or unresolved]
Perceptual/material choices: [scale, color, sound, texture, sequence, interaction]
Composition: [hierarchy, pacing, focal points, constraints, what stays quiet]
References and originality: [sources, transformations, licenses, unknowns]
Cultural respect: [communities/forms involved; consultation, consent, limits, benefit]
Authorship/provenance: [human contributions, collaborators, tools, source assets, record]
Production/disclosure: [tool/model/version, inputs, settings, human edits, reproducibility limits, public disclosure]
People/authority: [participants or likeness; consent scope; community authority, restrictions, benefit, withdrawal]
Ambiguity: [intended openings; required clarifications]
Critique: [reviewers, criteria, tests, hold conditions]
Release: [target formats, environments, accessibility equivalents, owner, date]
```

## Evidence and exception record

Use one record for each released work or version. Link evidence rather than copying protected participant or community material into a public package.

```text
Work/version: [canonical asset; version; owner]
Representation and delivery condition: [family; size, duration, device, venue, substrate, body location, or runtime]
Risks and escalation: [content, privacy, likeness, participant, cultural, material, venue, or safety risk; reviewer; decision]
Accessibility evidence: [equivalent modes; delivery-condition test; accepted limitation]
Provenance and generation: [sources; tools/models; inputs; settings; human decisions; synthetic-media status and disclosure]
People and authority: [consent scope; decision authority; permitted/restricted uses; benefit; withdrawal contact]
Preservation and fixity: [master/derivatives; dependencies; accessibility assets; integrity record; recheck result]
Status: [pass | hold | exception]
Exception and expiry: [unmet control; rationale; mitigation; owner; review date]
Incident, correction, or withdrawal path: [contact; allowed action; response target]
```

## Release gates

Release is blocked until the owner records evidence for each applicable gate:

1. Intent, audience, context, and desired experience are named; the work can be judged against them.
2. The composition and material choices are deliberate at the target scale, duration, distance, and sensory mode.
3. Meaning, ambiguity, and critique criteria are documented without claiming that audience interpretation is controllable.
4. References, permissions, licenses, collaborators, tool use, and human contributions are recorded. For generated or materially manipulated work, the production record and audience-facing disclosure identify the method and known provenance or reproducibility limits.
5. Cultural-risk review is complete. Living, sacred, Indigenous, or community-held forms have an appropriate authority or consultation path, permitted and restricted uses, attribution, benefit, and withdrawal path; hold release when required authority or permission is absent.
6. Accessibility and safety equivalents are selected, shipped, and tested for the actual audience and venue. For non-web, live, physical, or immersive work, record the chosen equivalent and delivery-condition result; high-risk use has a named reviewer and escalation path.
7. A second person has reviewed the work at the delivery condition and logged findings, decisions, and unresolved limitations.
8. Handoff metadata identifies the canonical asset, version, owner, source files, dependencies, rights, color/time/space assumptions, accessibility assets, preservation intent, package fixity and recheck, and rollback or withdrawal contact.

## What this standard does not claim

The contract makes production decisions legible. It does not turn taste into a formula, replace community authority, guarantee legal rights, or make a medium accessible merely because a checklist was completed. Treat heuristics as context-dependent choices; treat jurisdiction-specific law, safety codes, and venue rules as requirements only where they apply, with local professional review when needed.
