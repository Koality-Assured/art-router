---
doc_kind: research
canonical_id: art-router-representation-gaps
purpose: [research, validation]
rank: high
status: complete
date: 2026-08-27
topics: [art, representation, accessibility, safety, cultural-respect, authorship, delivery]
rag_keywords: [literary-art, performance, dance, theatre, music, sculpture, ceramics, textiles, comics, games, cartography, generative-art, provenance, synthetic-media, community-authority, withdrawal, fixity, captions, audio-description]
---

# Art-router representation and control gaps

## Bottom line

The art-router standards already cover 17 representation rows, a general intent and critique contract, and universal release gates. The missing work is concentrated in seven explicit representation families and in cross-cutting controls for generative workflows, human likeness, participant data, community authority, accessibility evidence, and delivery integrity. The standards writer should add scoped rows and a small cross-cutting annex. The generic `ai-harness-core` machinery should remain generic; the evidence reviewed here shows no reason to move art-domain rules into that upstream template.

This is a research note, not a proposed normative standard. The criteria below are candidates for fixture-based validation. None should be called validated until a real generation or reproducible fixture exercises it.

## Scope and method

I compared the current files [`artistic-practice.md`](../../docs/standards/artistic-practice.md) and [`artistic-representations.md`](../../docs/standards/artistic-representations.md) with the next-steps prompt, then checked the gaps against primary sources from W3C, NIST, C2PA, IPTC, UNESCO, the United Nations, WIPO, WHO, the Library of Congress, and the U.S. Copyright Office. The Library of Congress Recommended Formats Statement is useful as a coverage check because it names textual works, still and moving images, audio, musical scores, datasets, GIS/cartographic work, design/3D, software/video games, and web archives as distinct preservation concerns ([Library of Congress Recommended Formats Statement](https://www.loc.gov/preservation/resources/rfs/)).

The repository's indexed upstream comparison note, `qmd://docs/standards/wiki-harness-template.md`, says that `ai-harness-core` keeps the folder layout, routing, cost layers, generic skills, scripts, and portable supporting notes, while fed instances keep domain corpus, research, and memory. That note is not git-tracked in this worktree. The tracked [`gh-workflow-notes.md`](../../supporting/github/gh-workflow-notes.md) states the same boundary. I therefore treat the indexed note as comparison evidence and the tracked note as the local corroboration, not as a file to recreate here.

## Additional representation families

Leave the current matrix intact. These additions address distinct production risks rather than renaming existing media.

### Literary, textual, and poetic work

Text is absent as a primary artistic representation even though it is often the canonical source for poetry, prose, scripts, artist books, and text-based installations. A row should cover reading order, lineation, language and script, translation, versioning, typography, text alternatives for visual text, and preservation of the source text. It should distinguish an expressive visual treatment of text from the accessible text that carries the work's words.

Candidate handoff evidence: an author-approved plain-text or structured-text master, a rendered presentation, language and direction metadata, translation status, font and license record, and a description of any meaning carried only by layout.

### Performance, theatre, and dance

The current installation and participatory rows do not capture the rehearsal, casting, embodiment, live timing, audience proximity, or recording rights of performance. A row should cover performer consent, role and credit choices, rehearsal and accessibility plans, audience warnings, venue access, live captioning or interpretation where needed, recording and reuse permissions, and an emergency or stop procedure.

This family also exposes a gap in the current accessibility language. W3C's media guidance treats accessibility as a planning concern and identifies captions, descriptive transcripts, audio description, sign language, and an accessible player as separate deliverables ([W3C: Making Audio and Video Media Accessible](https://www.w3.org/WAI/media/av/)). Those controls apply to a recorded performance, but a live work needs a live delivery plan as well.

### Music, composition, and live sound

The audio row covers files and multisensory cues, but it does not distinguish composition, performance, lyrics, improvisation, live amplification, or audience exposure. A row should include score or session lineage, performer and neighboring rights, stems or notation where relevant, loudness and dynamics, lyrics or spoken-content alternatives, playback and monitoring, hearing protection, quiet space, and an opt-out path.

For amplified public events, WHO's standard provides concrete safety features: a maximum average sound level of 100 dB LAeq,15 min, calibrated live monitoring and recording, audience hearing protection, quiet zones, and staff information ([WHO global standard for safe listening venues and events](https://www.who.int/publications/i/item/9789240043114)). These are venue-specific controls, not a universal artistic limit.

### Sculpture, ceramics, textiles, and material fabrication

Installation is a site and audience-flow category; it does not replace a material-object row. Sculpture, ceramics, textiles, wearable objects, and fabricated props add hazards and failure modes around dust, solvents, glazes, dyes, sharp edges, load, heat, fragility, skin contact, cleaning, and aging. A row should require a material and hazard inventory, fabrication and handling limits, structural or electrical review when applicable, tactile-access decisions, conservation limits, and a maintenance or disposal plan.

The standards writer should keep material and body safety jurisdictional. The existing tattoo and installation rows already point to FDA, OSHA, ADA, and local authorities; the new row should connect to those existing boundaries rather than make a design file sound like a safety approval.

### Comics, sequential art, storyboards, and illustrated narrative

Collage and illustration do not cover the semantic dependency between panels, captions, speech, sound effects, gutters, and reading order. A row should specify canonical sequence, alternate reading order if it changes meaning, text extraction, descriptive transcript, localization constraints, and how motion or interactive panels degrade to a static version.

### Games and software-based artworks

The website and creative UI row covers browser interaction, but not installed games, executable artworks, game state, controller diversity, save data, patching, privacy, or end-of-life behavior. The Library of Congress lists software and video games as a separate format concern ([Library of Congress Recommended Formats Statement](https://www.loc.gov/preservation/resources/rfs/)). A row should record runtime and platform, input map, onboarding and exit, save-state behavior, accessible control alternatives, offline mode, dependency versions, privacy/data flows, content warnings, and a playable preservation build or screen-recorded fallback.

### Cartographic and geospatial art

Data visualization covers encoding and uncertainty, but maps add projection, coordinate reference system, geographic scale, place-name authority, spatial resolution, location privacy, and the possibility that a map's persuasive design hides uncertainty. The Library of Congress treats GIS, geospatial, and non-GIS cartographic work as a distinct preservation category. A row should require datum/projection, source date, spatial precision, update owner, uncertainty statement, accessible text or tabular equivalent, and a review of whether exact locations create safety or privacy risk.

### Generative and AI-native work

This should be a workflow overlay that can attach to any medium, not a claim that a new medium exists. It should require the model or tool identity and version, input assets, prompts or procedural rules, seed and generation parameters when available, edits and selections, rejected or unsafe branches when retaining them is appropriate, disclosure language, and known limits of reproducibility. NIST's Generative AI Profile identifies provenance data such as creator or developer, date/time, modifications, and sources, and says it can apply to text, images, video, audio, and datasets ([NIST AI RMF: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)).

## Cross-cutting gaps

### Technical and reproducibility controls

The current standards ask for provenance and technical metadata, but they do not require a reproducible generation record or a clear fallback when exact reproduction is impossible. The next version should add:

- A machine-readable work manifest linking the canonical asset, source assets, versions, transformations, dependencies, and delivery derivatives.
- A generation record for AI-assisted work: provider or local tool, model/version, prompt or procedure, input references, seed and settings when exposed, human selections, edits, and tool limitations.
- A delivery-condition test record covering target size, duration, distance, device, substrate, venue, body location, or runtime. Record the degraded mode tested and the accepted limitation.
- Fixity for the handoff package, with a digest or equivalent integrity record and a re-verification step after transfer. Do not treat a digest as proof of authorship or legal ownership.
- A receiving-environment check that opens or renders the package, reports missing fonts/dependencies, and records any deviation from the approved master.

NIST recommends documenting provenance limitations, monitoring capabilities through testing, and collecting feedback about provenance mechanisms. C2PA provides a technical standard for certifying source and history of media content ([C2PA specifications](https://spec.c2pa.org/specifications/)). C2PA is useful when the format and toolchain support it, but an absent or stripped manifest must remain an explicit limitation rather than a silent pass.

### Accessibility beyond a web checklist

The existing standard correctly points to WCAG 2.2 for web and ICT. WCAG itself describes web content and says it does not address every user need ([WCAG 2.2](https://www.w3.org/TR/WCAG22/)). The gap is an evidence model for non-web and live work, not another universal conformance claim.

The standards writer should require the maker to identify the information or experience that must be preserved, then choose equivalent modes for the actual audience. Depending on the work, that can include structured text, long description, captions, descriptive transcript, audio description, sign language, tactile or physical alternative, keyboard or switch access, seated and standing modes, reduced motion, quiet space, or non-immersive fallback. Accessibility assets should ship with the work and be tested in the receiving player or venue.

W3C's WCAG 2.2 gives testable requirements for non-text alternatives, captions, audio description, live captions, sign language, color-independent meaning, and pause/stop behavior. Its media guidance also says to plan accessibility before production. The candidate control should therefore measure both presence and delivery: a caption file existing beside a video is not evidence that it is synchronized, legible, selectable, or available in the intended player.

### Safety, privacy, and incident response

The current matrix covers material hazards, seizure-risk flashes, sound, tattoo hygiene, venue safety, and some privacy considerations. It lacks a shared screening and escalation layer for generated or manipulated content, especially when a work includes a recognizable person, sensitive personal data, sexual or violent content, or a vulnerable participant.

NIST's profile identifies privacy, harmful bias and homogenization, dangerous or hateful content, intellectual property, and information integrity as generative-AI risks. It recommends structured human feedback, red-teaming with relevant expertise, content provenance, withdrawal or revocation options for human subjects, and content filters for inappropriate, harmful, false, illegal, or violent content ([NIST AI RMF: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)). The art-router control should translate those ideas into a release record:

- Identify content and subject risks before generation or capture, including likeness, location, private data, and vulnerable people.
- Define who may approve, hold, restrict, withdraw, or request takedown.
- Record consent scope separately for capture, editing, publication, model training, derivatives, and archival retention.
- Use human review for high-risk cases; record the trigger, reviewer role, decision, and unresolved limitation.
- Provide an incident, correction, and withdrawal path after release, with an owner and response target.

For a recognizable person's digital replica, the U.S. Copyright Office describes the risk as realistic but false depictions in video, image, or audio and recommends stronger protection for unauthorized distribution ([U.S. Copyright Office: Part 1, Digital Replicas](https://www.copyright.gov/newsnet/2024/1048.html)). This is a U.S.-specific legal source, not a global rule. The portable control is permission and disclosure tracking, with local legal review when the jurisdiction or use requires it.

### Cultural responsibility and community authority

The current standards already ask about living heritage, Indigenous knowledge, sacred imagery, consultation, consent, benefit, and withdrawal. The missing detail is who has decision authority, which uses are restricted, whether documentation itself is permitted, and how a restriction survives handoff.

UNESCO's 2003 Convention says communities, groups, and individuals who create, maintain, and transmit intangible heritage should participate in its management. UNESCO's ethical principles say communities should have the primary role and that interaction should be contingent on free, prior, sustained, and informed consent ([UNESCO: 2003 Convention](https://ich.unesco.org/en/convention), [UNESCO: Ethical Principles for Safeguarding Intangible Cultural Heritage](https://ich.unesco.org/en/ethics-and-ich-00866)). UNDRIP Article 31 recognizes Indigenous peoples' rights to maintain, control, protect, and develop cultural heritage, traditional knowledge, and traditional cultural expressions ([United Nations: UNDRIP Article 31](https://www.un.org/esa/socdev/unpfii/documents/UNDG_guidelines_EN.pdf)). WIPO advises assessing risks and potential benefits before documenting traditional knowledge or traditional cultural expressions ([WIPO: Documentation of TK and TCEs](https://www.wipo.int/en/web/traditional-knowledge/resources/tk-and-tces)).

The candidate control is therefore authority-based, not a box marked “consulted”: identify the community or representative institution where appropriate; ask what may be shown, transformed, named, stored, or commercialized; record terms, attribution, benefit sharing, confidentiality, and withdrawal; and refuse release when the required authority or permission is absent. A community-approved description should travel with the work, while restricted source details should not be copied into a public manifest.

### Authorship, rights, and synthetic-media disclosure

The current practice standard records human decisions, collaborators, tools, licenses, and C2PA provenance. It should make the contribution record more granular and separate four questions that are easy to collapse: who made expressive decisions, who owns or licenses source material, how the asset was produced, and what an audience is told about synthetic or manipulated content.

The U.S. Copyright Office concludes that AI assistance does not bar protection of human-authored expression, but that purely AI-generated material or material without sufficient human control is not protected under current U.S. law; it also says prompts alone are not sufficient control ([U.S. Copyright Office: Part 2, Copyrightability](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf)). The standards writer should not turn that jurisdictional conclusion into a universal authorship rule. The portable record is a contribution ledger with human selection, arrangement, modification, collaboration, source permissions, model/tool use, and audience disclosure. Legal status remains a jurisdictional review item.

For photography, IPTC provides a practical metadata model that separates image creator, copyright owner, licensor, descriptive information, and accessibility alt text; it also warns that rights metadata can be affected by law and contract ([IPTC Photo Metadata Standard 2024.1](https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata-2024.1.html)). The same separation should guide other media even when IPTC is not the right schema.

### Delivery, preservation, and withdrawal

The current handoff fields are strong on file names, formats, profiles, dimensions, and owners. They are weaker on package integrity, preservation intent, accessibility assets as first-class files, and post-release change. The Library of Congress RFS frames format choice as a survival and continued-access problem and distinguishes preferred and acceptable characteristics; it also warns that DRM or encryption can prevent use of a digital work. The standards writer should add a preservation intent field, an archival master versus delivery derivative distinction, fixity, dependency/runtime notes, accessibility assets, and a change or withdrawal contact.

For web, interactive, game, and XR work, the package should include a tested build or an explicitly bounded substitute such as a screen recording, interaction map, or static export. For physical and live work, it should include installation, maintenance, access, safety, and removal instructions. For restricted cultural or participant material, the package should carry the restriction and contact without exposing the protected content.

## Candidate measurable criteria

These are proposed acceptance criteria for the standards writer and validation specialist. They are not yet repository controls.

- **Representation coverage:** Each fixture names one primary representation family, any cross-media families, delivery modes, audience, and risk owner. The fixture set includes at least one item from every newly proposed family before the matrix is called exercised.
- **Generation reproducibility:** A second operator can recreate the approved output or produce a documented bounded-difference result from the manifest. The record names every unavailable parameter and explains why exact reproduction was not possible.
- **Accessibility evidence:** Every applicable alternative is linked in the handoff and passes a delivery-condition check. For web or ICT, record the claimed WCAG level and manual keyboard/focus/media checks; for live, physical, and immersive work, record the chosen equivalent, venue/device test, and accepted limitation.
- **Participant and likeness control:** Every recognizable participant has a recorded permission scope for capture, edit, publication, training, derivatives, archival retention, and withdrawal. A fixture must exercise at least one refusal or withdrawal path without exposing private data.
- **Cultural authority:** A fixture involving community-held or restricted material records the decision authority, permitted use, attribution, benefit terms, confidentiality, and withdrawal route. A negative fixture must hold release when authority or permission is missing.
- **Synthetic-media disclosure:** An independent reviewer can identify whether AI generation, manipulation, or digital replica work occurred from the public disclosure and the private provenance record. Missing provenance must be reported as missing, not treated as evidence that no synthetic process occurred.
- **Source and rights completeness:** Every source asset has a rights state of licensed, permitted, public-domain, creator-owned, restricted, or unknown, with an owner for unresolved items. Unknown or restricted items trigger hold or explicit scope limitation.
- **Safety escalation:** High-risk content, flashing, sound, material, body, venue, or privacy cases produce a named reviewer, decision, mitigation, and incident/withdrawal contact. For amplified public audio, measure against the applicable local rule and, where the WHO standard is adopted, record calibrated LAeq,15 min monitoring.
- **Package integrity:** The receiving environment opens or renders the approved package; the manifest, fixity record, source files, accessibility assets, and dependency/runtime notes are present; and a post-transfer recheck records any mismatch.
- **Post-release accountability:** A human can report a correction, accessibility defect, cultural concern, rights issue, or safety incident and reach the responsible owner. The validation fixture records the response path and the allowed change or withdrawal action.

The first validation pass should exercise a text/poetry piece, live performance or music case, material-object case, sequential-art case, game or cartographic case, and an AI-assisted visual or time-based work. This extends the next-steps prompt's existing 2D, motion, 3D, web, tattoo, photography, and icon/favicon cases without claiming that any criterion is proven by documentation alone.

## Recommendations for the standards writer

1. Add the seven representation rows above, keeping generative/AI-native work as an overlay that attaches to any medium.
2. Add a cross-cutting “evidence and accountability” annex covering the manifest, reproducibility record, delivery-condition test, rights state, consent scope, community authority, synthetic disclosure, incident path, and withdrawal contact.
3. Strengthen the universal release gates so that accessibility alternatives, provenance limits, and delivery integrity are evidenced in the handoff, not merely planned in the brief.
4. Add a small jurisdiction and authority note: WCAG, WHO, FDA, OSHA, ADA, copyright, venue codes, and community protocols have different scopes. The standard should require the applicable authority or specialist review without presenting any one source as a universal law of art.
5. Validate the candidate criteria with the six-fixture set before promoting any item into `docs/standards/`. Record failures and accepted limitations in a later research or validation note.
6. Preserve upstream parity by leaving generic `ai-harness-core` machinery unchanged. Domain-specific categories, cultural controls, and art safety evidence belong in this fed instance's standards and research areas; generic routing, isolation, qmd, ast-grep, Headroom, and script improvements remain eligible for upstream synchronization.

## Source ledger

### Repository sources

- [`artistic-practice.md`](../../docs/standards/artistic-practice.md), current intent, cultural, authorship, provenance, critique, and release contract.
- [`artistic-representations.md`](../../docs/standards/artistic-representations.md), current medium matrix and universal release gates.
- [`art-router-next-steps.md`](../../projects/project-prompts/art-router-next-steps.md), human scope and suggested validation fixtures.
- [`gh-workflow-notes.md`](../../supporting/github/gh-workflow-notes.md), tracked description of `ai-harness-core` as the generic, non-domain-fed template.
- `qmd://docs/standards/wiki-harness-template.md`, indexed upstream comparison note; not present as a git-tracked file in this worktree.

### Primary external sources

- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [W3C media accessibility guidance](https://www.w3.org/WAI/media/av/).
- [NIST AI RMF: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf).
- [C2PA specifications](https://spec.c2pa.org/specifications/).
- [IPTC Photo Metadata Standard 2024.1](https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata-2024.1.html).
- [UNESCO 2003 Convention](https://ich.unesco.org/en/convention) and [UNESCO Ethical Principles for Safeguarding Intangible Cultural Heritage](https://ich.unesco.org/en/ethics-and-ich-00866).
- [United Nations Declaration on the Rights of Indigenous Peoples, Article 31](https://www.un.org/development/desa/indigenouspeoples/wp-content/uploads/sites/19/2018/11/UNDRIP_E_web.pdf).
- [WIPO: Documentation of Traditional Knowledge and Traditional Cultural Expressions](https://www.wipo.int/en/web/traditional-knowledge/resources/tk-and-tces).
- [WHO global standard for safe listening venues and events](https://www.who.int/publications/i/item/9789240043114).
- [Library of Congress Recommended Formats Statement](https://www.loc.gov/preservation/resources/rfs/).
- [U.S. Copyright Office, Part 1: Digital Replicas](https://www.copyright.gov/newsnet/2024/1048.html) and [Part 2: Copyrightability](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf).

## Open questions

- Which jurisdictional profiles should the standards writer support first for venue, tattoo, public-space, and labeling controls?
- Should the work manifest be a small art-router schema, or should the router adopt existing C2PA/IPTC/format-specific metadata and add only a cross-medium index?
- Which community review and compensation records can be represented publicly, and which must remain private or community-controlled?
- What level of exact reproducibility is realistic for each local or hosted generation tool, and which bounded-difference tests will be accepted?
