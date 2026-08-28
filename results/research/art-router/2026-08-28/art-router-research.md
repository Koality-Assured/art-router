---
doc_kind: research
canonical_id: art-router-research-2026-08-28
title: Art router expansion research
topic: art-router
date: 2026-08-28
status: complete
research_mode: deep-research
source_scope: in-repo corpus audit plus authoritative external sources
tags: [art-router, generative-art, constraint-preservation, drift-detection, agent-compatibility, safety, rights]
---

# Art router expansion research

This dossier answers three questions:

1. Does the router cover the common shapes of AI-assisted artistic work?
2. How should it preserve the initial brief, detect drift, and stop on ambiguity or rights-sensitive risk?
3. What should it assume, and not assume, when the work is executed through Cursor-style, Claude-style, or Google Antigravity-style agents?

The research is date-stamped 2026-08-28. Product behavior is volatile; the agent comparison records only capabilities described in official documentation available on that date. This is a design and routing report, not a legal opinion, safety certification, accessibility conformance statement, or release approval.

## Executive findings

The existing representation-routing skill is unusually broad. It already names rows for painting and illustration, photography, raster/vector/sprites, logos, typography/color, CGI/3D/VFX, animation/video/projection, audio and haptic work, literary work, comics, software artworks, XR, data visualization, cartographic art, installations, tattoos, merchandise, and physical fabrication. The named media in the research brief are therefore covered at the level of representation.

The material gap is a second axis that the current row list does not make explicit: what the user is asking the system to do to an asset. Generation, edit, inpaint, outpaint, remove, composite, restyle, vectorize, animate, extend, translate, remix, fabricate, map, and deploy have different inputs, evidence, and failure modes. Editing/inpainting is the clearest example: the current skill treats generation and manipulation through a generative overlay, but a router should preserve the untouched region, mask semantics, and edit locality as first-class constraints.

The router should become a two-axis system:

- Representation: what the work is and where it will be used.
- Operation: what transformation is requested and what must remain invariant.

Every route should also carry a constraint ledger. The ledger distinguishes hard requirements, preferences, unknowns, inferred defaults, and prohibited assumptions. It is compared with the output evidence before the system reports success. A clean manifest or checksum must remain evidence about declared metadata and package integrity only; it must never be treated as proof of quality, authorship, ownership, consent, safety, accessibility, or release readiness.

The cross-host strategy should be portable at the contract layer and adaptive at the execution layer. Cursor documents a file/search/web/browser/shell/image-generation agent with project rules and MCP; Claude Code documents a terminal-centered agent with `CLAUDE.md`, permission modes, CLI controls, and MCP; Antigravity documents an agent-first IDE/CLI/SDK with editor, terminal, browser, asynchronous agents, artifacts, workspace rules, permissions, and a terminal sandbox. These are useful affordances, not a common behavioral guarantee. The router must send a self-contained request contract and require artifact evidence regardless of host.

## Method and corpus audit

### In-repo corpus first

The worktree was checked with QMD before external research:

- Three targeted `qmd search` calls for artistic categories, constraint drift, and cross-agent behavior returned empty result sets.
- `qmd status` reported zero indexed documents and zero vectors in all ten collections.
- `qmd ls docs`, `qmd ls research`, and `qmd ls results` reported no indexed files.

The checked-in router material was therefore inspected by targeted path after the QMD index proved empty. The most relevant existing sources were `ai-tooling/skills/artistic/representation-routing/SKILL.md`, `ai-tooling/skills/artistic/evidence-validation/SKILL.md`, `ai-tooling/agents/router/AGENT.md`, and `ai-tooling/agents/artistic-standards-reviewer/AGENT.md`. This report should be treated as an external-evidence expansion of the current skills, not as proof that the whole repository corpus was indexed.

The prescribed `scripts/results/new_run_dir.py` helper is not present in this worktree. The required results path was created directly as `results/research/art-router/2026-08-28/`; no source, skill, script, routing, or unrelated file was changed.

### Evidence boundary

The category list below is an operational taxonomy, not a prevalence ranking. The available sources document media capabilities, format requirements, safety risks, or standards; they do not establish how often users request each type. Where a recommendation is an inference from those sources, it is labeled as such.

## Coverage review: request families and failure modes

For each family, the router should capture: subject or content, operation, representation, delivery condition, exact constraints, references and rights, human review owner, and evidence needed to accept the result.

### Still image: illustration, photography, raster, and sprites

Common requests include text-to-image illustration, product or editorial imagery, portraits, concept art, texture sheets, transparent cutouts, sprite sheets, fixed aspect ratios, and multiple variations.

Frequent failure modes are subject count or identity drift, incorrect composition, unwanted background changes, broken hands or small details, unreadable embedded text, inconsistent characters across variations, wrong crop or aspect ratio, and a deliverable that looks right but is not in the requested color space, resolution, transparency mode, or file format. These are general failure hypotheses for acceptance testing, not claims that every provider exhibits every failure.

The router should preserve exact canvas dimensions, aspect ratio, alpha requirement, color-space requirement, focal subject, subject count, negative constraints, reference-image roles, and variation count. It should distinguish a style reference from a structure or content reference. Adobe’s Firefly documentation explicitly treats style references as a control separate from the text prompt and exposes a strength parameter; the same separation is useful in the router even when a chosen provider uses different parameter names. [S04]

Acceptance checks should inspect image metadata, alpha, dimensions, crop, text legibility, subject count, and reference-role evidence. Human review remains necessary for likeness, cultural representation, quality, and rights.

### Editing, inpainting, outpainting, removal, and compositing

Common requests include removing an object, changing a background, replacing a garment or product color, repairing a damaged area, extending a canvas, relighting, compositing a supplied object into a scene, or making a local change while keeping everything else unchanged.

The characteristic failure is locality drift: the requested region changes, but so do the face, hands, product geometry, text, lighting, or unmasked background. Other failures include mask inversion, feathering too wide or too narrow, seams, halos, scale mismatch, perspective mismatch, and an edit that silently changes the source image rather than preserving a reversible layer or original.

The operation contract must include the source asset hash, mask semantics, editable region, protected region, allowed spill or blend margin, edit prompt, and a requirement to retain the original. Adobe documents black mask areas as protected and white areas as exposed for Firefly image manipulation, and its inpainting guide describes filling masked holes while returning a generated result. [S03] [S05] The router should normalize provider-specific polarity into one internal convention and verify the result against the protected region with an image-diff or perceptual-diff check. A material protected-region change is a hold, not a quality preference.

### Vector, logo, icon, and typography work

Common requests include a logo or wordmark, favicon, app icon, brand mark, packaging mark, editable SVG, icon family, lettering study, typographic lockup, and a scalable color system.

The failure modes are especially consequential: generated raster art is mislabeled as editable vector; paths are self-intersecting or excessively complex; text is misspelled, outlined when live text was required, or rendered with an unavailable font; the mark is not legible at intended sizes; color contrast fails; a logo resembles a conflicting mark; or a user asks for a living artist’s signature style or a protected brand identity without clarifying rights.

SVG is not just a picture format. W3C’s SVG guidance distinguishes paths, images, and text, recommends text equivalents and semantic structure for accessible graphics, and explains that character data can remain searchable and selectable. [S06] [S07] The router should ask whether text must remain live or may be outlined, whether fonts may be embedded, which SVG feature subset is allowed, and which target renderers must be tested. For logos, it should route trademark clearance as a human-owned hold: USPTO guidance recommends searching for confusingly similar word and design marks before filing or commercial use. [S08] [S09]

Do not conflate trademark clearance with copyrightability. The U.S. Copyright Office says typeface and mere variations of typographic ornamentation or lettering are generally not copyrightable, while a sufficiently original graphic combination may be. [S10] The router should report this distinction and require a qualified reviewer where the user asks for ownership, clearance, registration, or infringement conclusions.

### 3D, CGI, game assets, and VFX

Common requests include a concept render, turntable, game-ready mesh, prop, character, environment, material or texture set, rigged asset, camera move, VFX plate, or a model prepared for a web or engine runtime.

Failures include a pretty render with no usable mesh, non-manifold or self-intersecting geometry, inverted normals, missing UVs or textures, broken rig weights, wrong units or scale, excessive polygon or texture budgets, missing animation clips, unsupported extensions, and a file that loads in the authoring tool but not in the target runtime. The required artifact may be an authoring file, a runtime package, a render, or all three; these are not interchangeable.

Khronos describes glTF as an API-neutral runtime delivery format, not an authoring format, and lists scene hierarchy, meshes, materials, cameras, textures, and animations as distinct parts of a complete scene. [S11] The router should capture target engine, coordinate system, units, triangle and texture budgets, material model, required animations, license of embedded assets, and whether source authoring data is required. It should validate the actual target runtime or a designated reference loader, not only file existence.

### Animation, video, motion graphics, and projection

Common requests include a short text-to-video shot, image-to-video motion, loop, title sequence, explainer, projection piece, animated logo, scene extension, first-to-last-frame interpolation, or multi-shot edit.

Failures include temporal identity drift, object morphing, camera or lighting discontinuity, dialogue and lip-sync mismatch, inconsistent text, broken loops, wrong duration or frame rate, unwanted audio, unsafe flashes, and a result that satisfies one shot but not the requested sequence. Long narrative requests often conflict with provider-specific clip limits and must be decomposed into shots with continuity evidence.

Google’s current Gemini video documentation illustrates why the router needs explicit provider capability checks: the documented Veo 3.1 workflow supports short generated clips, image direction, first and last frames, extension, aspect-ratio choices, and native audio, with model-specific input and output limits. [S12] The same page states that safety filters may block prompts or uploaded photos. These are provider facts, not universal model facts; the router must query a capability manifest and never promise a duration, resolution, audio mode, or extension path without checking the selected provider.

Web delivery adds accessibility constraints. WCAG 2.2 includes pause/stop/hide requirements for moving or auto-updating content and animation-from-interaction guidance. [S13] For web animation, acceptance should include pause/stop behavior, reduced-motion behavior where applicable, flash review, captions or transcripts for speech, and keyboard or non-pointer control where the experience is interactive.

### Audio, music, voice, vibration, and haptics

Common requests include a music bed, song sketch, sound effect, ambience, podcast voice, narration, character voice, voice conversion, sound installation, vibration cue, or audio-reactive visual.

Failure modes include unwanted melodic or timbral similarity, clipped or noisy audio, timing drift, incorrect duration or sample rate, missing stems, voice identity drift, pronunciation errors, language or accent mismatch, unconsented likeness, and a mix that cannot be separated or edited later. A generated song also has separate composition and recording concerns.

The U.S. Copyright Office distinguishes a musical work from a sound recording and notes that they may be separately owned and licensed. [S14] Its AI report says that copyrightability of an AI-assisted output depends on human authorship and that prompts alone do not establish human authorship of expressive elements. [S01] [S02] The router should therefore record source samples, licenses, model/provider, human edits, stems, and disclosure; it should not promise ownership from generation alone.

Voice requests require an explicit identity and consent gate. ElevenLabs documents voice verification, restrictions on professional cloning of another person’s voice, and a prohibition on intentional replication without consent or legal right. [S15] [S16] The router should treat “sound like [living person]”, “make this person say”, and “use this private recording” as rights-sensitive identity requests, not ordinary style modifiers. Public-figure impersonation, fraud, or deceptive attribution should be held or refused according to the applicable safety policy.

### Text, poetry, scripts, comics, storyboards, and illustrated narrative

Common requests include a poem, artist statement, screenplay, children’s book, comic script, storyboard, captions, dialogue, character bible, page layout, or a sequence of image panels with recurring characters and exact lettering.

Failures include invented facts, continuity breaks, character or costume drift, missing panels, wrong reading order, text overflow, duplicate or omitted dialogue, tone drift, unsupported cultural claims, and visual text that cannot be corrected because it was baked into a raster image. NIST defines confabulation to include output that is false, internally inconsistent, or divergent from the prompt or earlier context. [S17] That definition maps directly to continuity and parameter drift in narrative art.

The router should separate story truth from fictional invention, preserve a character and continuity ledger, and keep dialogue, captions, and labels as structured text until final layout. For comics, it should capture page size, panel count and order, bleed, reading direction, language, balloon placement, accessibility transcript, and whether lettering must remain editable. For factual or documentary narratives, source verification is a separate hard gate.

### Code-native, interactive, game, and XR work

Common requests include a generative canvas, shader sketch, interactive installation, game prototype, creative UI, data-driven animation, browser artwork, WebXR scene, AR filter, or executable visual instrument.

Failures include a static mockup presented as an interactive artifact, missing controls, broken state transitions, inaccessible keyboard flow, unbounded animation or GPU work, unsafe browser or shell actions, cross-origin failures, unsupported device features, and a visually impressive demo that has no reproducible build or test path.

W3C’s WebXR specification requires user intent and transient activation for immersive session requests, models feature availability as device- and user-agent-dependent, and calls out precision, latency, and security concerns. [S18] WebGPU also imposes origin-clean restrictions on image sources because shaders can expose cross-origin data. [S19] The router should capture target browsers and devices, permission prompts, input modes, latency budget, fallback mode, asset origins, privacy boundaries, and exit behavior. Acceptance should run the artifact in a real target browser or a documented emulation path, with a non-XR fallback when requested.

### Data visualization and cartography

Common requests include an explanatory chart, dashboard visual, map illustration, GIS layer style, animated map, terrain view, location-aware installation, or an evidentiary visual derived from supplied data.

Failure modes include fabricated or stale data, wrong coordinate reference system, missing source attribution, misleading classification or scale, label collisions, omitted uncertainty, bad generalization, inaccessible color encoding, and decorative geography that looks plausible but is not spatially true. A map-like image made from a text prompt is not equivalent to a data-backed map.

OGC API - Maps defines maps as visual portrayals created by applying a style to geospatial resources and includes extent, styles, output encodings, and coordinate reference systems in its standards context. [S20] USGS describes cartographic representation as displaying information on a map and notes that features must be shown at a level of detail appropriate to the map extent, requiring cartographic generalization. [S21] The router should require data provenance, dataset version and date, CRS, extent, classification method, label policy, scale, legend, uncertainty treatment, and accessibility alternative. A cartographic request with invented locations or unverified facts is a hold.

### Physical, installation, tattoo, merchandise, and packaging

Common requests include a poster, garment, label, package, print-ready file, fabricated object, sculpture, public installation, signage, tattoo stencil, temporary tattoo, or 3D-printed product.

Failures arise when a screen image is treated as physically realizable: wrong scale, bleed, dieline, substrate, ink behavior, color profile, seam, repeat, material thickness, fastener, load, heat, egress, weather, accessibility, or installation method. Tattoos add permanence, skin placement, aging, line-weight, and health risks. Merchandise adds trademark, labeling, consumer-safety, and production constraints.

FDA materials state that tattoos are permanent, that inks can cause infection or allergic reaction, and that no color additives are approved for injection into skin; local authorities generally regulate tattoo practice. [S22] This makes “tattoo-ready” a professional and health-sensitive deliverable, not just a black-and-white image conversion. CPSC identifies hazards in both 3D-printing processes and printed products. [S23] FTC guidance requires many textile products to identify fiber content, country of origin, and responsible business. [S24]

The router should ask for substrate, dimensions, production process, tolerances, color system, safety owner, venue or jurisdiction, audience, maintenance, and whether the output is a concept, a production file, or an installation plan. It should route tattoo designs to a qualified tattoo professional and physical installations to venue, structural, electrical, fire, and accessibility review as applicable. It must not imply that a generated design is safe to manufacture or apply.

## Constraint preservation and drift control

### The request contract

Before routing, normalize the initial request into a durable contract while retaining the original wording for audit. The contract should contain:

- `intent`: one or more operations such as generate, edit, inpaint, outpaint, vectorize, animate, extend, compose, write, map, fabricate, or deploy.
- `representation`: primary row plus every adjacent row carrying a separate risk.
- `inputs`: asset identifiers or hashes, reference roles, data sources, source licenses, and permitted transformations.
- `hard_constraints`: exact values and prohibitions. Examples include dimensions, duration, aspect ratio, file format, text string, language, subject count, protected region, CRS, target runtime, or body location.
- `soft_constraints`: preferences such as mood, palette, visual direction, or degree of abstraction.
- `unknowns`: missing details that block reliable routing or require an explicit default.
- `delivery`: audience, channel, target device, venue, substrate, production method, package structure, and deadline.
- `rights_and_people`: likeness, voice, private data, source materials, cultural authority, trademark, licensing, and consent state.
- `safety_and_accessibility`: age audience, permanence, physical hazards, sensitive content, captions, transcripts, pause/stop behavior, reduced-motion needs, and alternative representations.
- `acceptance_tests`: observable checks and the owner who can judge them.
- `non_claims`: what the system will not infer, such as ownership, clearance, consent validity, or professional safety.

Do not silently turn a preference into a hard constraint or a missing value into a fact. If a provider cannot support a hard constraint, surface the conflict and offer a revised route or a human decision.

### The constraint ledger

Keep a machine-readable ledger through the run. Each entry should have:

- a stable identifier;
- source location: original prompt, user follow-up, reference asset, system default, or provider capability;
- normalized value and original wording;
- class: hard, soft, unknown, inferred, or prohibited;
- dependencies and conflicts;
- evidence expected;
- status: preserved, verified, changed with approval, unverified, violated, or not applicable;
- reviewer or decision owner.

The ledger prevents a common agent failure: a later, more detailed instruction or tool result displacing an earlier requirement without an explicit decision. NIST’s definition of confabulation includes divergence from the prompt and contradiction with earlier context, so prompt-to-output comparison is a reliability control, not only a style preference. [S17]

### Hidden-conflict detection

Run a preflight conflict pass before selecting a provider or tool. Useful deterministic checks include:

- exact text plus a raster-only generator;
- editable vector plus a request that only names a PNG or JPEG output;
- “change only the background” plus no protected mask;
- a real person’s likeness or voice plus absent consent or a deceptive use;
- “in the style of” a living artist plus a commercial or attribution-sensitive use;
- a short provider clip limit plus a long continuous narrative;
- a physically permanent tattoo plus unreadably small text or untested line detail;
- a factual map plus missing dataset, date, CRS, or source attribution;
- “safe for children” plus graphic, sexual, hateful, or dangerous content;
- a browser/XR artifact plus no target device, permission, fallback, or user-activation path;
- a public installation plus no venue, load, power, egress, weather, or accessibility owner.

Conflicts should be represented as `needs_user_decision`, `provider_mismatch`, `rights_hold`, `safety_hold`, or `evidence_hold`. The router should not resolve a material conflict by rewriting the brief.

### Drift detection after generation or editing

Use the cheapest reliable check first, then escalate:

1. Compare exact metadata: dimensions, aspect ratio, duration, frame rate, sample rate, channel count, file type, transparency, CRS, units, and declared model/provider settings.
2. Compare exact structured fields: text strings, panel counts, layer names, SVG text, map labels, asset names, and required animation clips.
3. Compare protected content: source-image masks, non-edit regions, unchanged layers, reference geometry, or fixed first/last frames.
4. Compare semantic requirements: subject count, identity, placement, palette, accessibility controls, target runtime behavior, or physical production notes.
5. Inspect provenance and package evidence: source hashes, C2PA manifest where supported, generation parameters, tool versions, human decisions, and fixity records.
6. Re-run only the failed operation with a narrowed scope; never regenerate the whole asset when the user asked for a local correction unless the user approves the tradeoff.

The result status should be `pass`, `revise`, `hold`, or `exception`, with `exception` requiring a named accountable owner, rationale, mitigation, expiry, and permitted scope. A validator pass is not a release decision.

### Rights, identity, and unsafe request screening

At intake, detect requests involving real people, private images or recordings, living artists, brands, copyrighted source assets, public-figure impersonation, non-consensual sexual imagery, child sexual abuse material, fraud, misleading documentary content, or dangerous physical application. NIST identifies intellectual-property, likeness/voice, privacy, abusive-content, and indirect prompt-injection risks in its Generative AI Profile. [S17] OWASP’s 2025 LLM Top 10 separately identifies prompt injection, sensitive-information disclosure, improper output handling, excessive agency, misinformation, and unbounded consumption. [S25]

Reference images, metadata, web pages, captions, and imported files must be treated as data, not as instructions. The router should isolate them from the instruction contract, sanitize or ignore embedded commands, and preserve source attribution without adopting source text as policy. This matters more when a host can browse, run shell commands, actuate a browser, invoke MCP, or delegate to parallel agents.

For a rights-sensitive or unsafe request, the route should explain the boundary and offer a safe transformation where possible: an original non-identifying character, a licensed or user-owned reference, a generic vocal quality rather than a named person, a fictional map clearly labeled as fictional, or a non-permanent tattoo mockup. Do not provide a false claim of clearance, consent, or professional safety.

## Cross-host expectations and mitigation

“Cursor-style,” “Claude-style,” and “Antigravity-style” are families of environments, not stable protocols. The concrete evidence below uses official documentation for Cursor Agent, Claude Code, and Google Antigravity. Exact models, plans, permissions, tool names, and defaults may change.

### Cursor-style coding agents

Cursor’s official Agent overview describes an agent composed of instructions, tools, and a selected model. It documents file and folder search, web search, file reading including image formats, file edits, shell commands, browser control, image generation, and question asking. [S26] Cursor’s rules documentation describes project rules in `.cursor/rules`, user and team rules, `AGENTS.md`, and relevance or glob-based application. [S27] Cursor also documents MCP integrations and approval behavior for tools. [S28]

Practical expectation: Cursor may be strong at repository-local visual implementation and browser verification when those tools are enabled. It may also have more than one instruction layer, so the router should not assume that a project rule, user rule, team rule, or `AGENTS.md` is present or applied in another host.

Mitigation:

- send the request contract and constraint ledger in the task itself;
- require the agent to state which files, browser, image, and MCP tools it actually used;
- keep generated assets in an explicit output directory and retain source and diff evidence;
- require a browser screenshot or recording only when visual behavior is part of acceptance;
- treat MCP outputs and repository files as untrusted data;
- do not grant broad shell or MCP permissions merely because a visual task may need one tool.

### Claude-style agents

Claude Code’s official CLI documentation describes interactive and print modes, session continuation, MCP configuration, allowed and disallowed tools, permission modes, maximum turns, and a cautionary bypass-permissions option. [S29] Anthropic’s memory documentation describes recursive discovery of `CLAUDE.md` files from the working directory and nested discovery when subtrees are read. [S30] Anthropic’s tool-use documentation describes client-side tools and server-side tools as distinct execution surfaces. [S31]

Practical expectation: a Claude-style terminal agent may be effective for structured planning, file edits, shell-based generation pipelines, and explicit tool contracts, but the documentation used here does not establish native image generation, browser actuation, or a particular media tool. Those must be supplied and verified as capabilities rather than inferred from the model name.

Mitigation:

- run a capability probe before routing: can it read the required asset, invoke the selected generator, render the output, and inspect the result?
- pin or quote the project-local contract; do not depend on recursive `CLAUDE.md` discovery for correctness;
- set explicit tool allow/deny rules and use plan mode for high-impact work;
- cap turns and preserve intermediate manifests so a long terminal run cannot silently broaden scope;
- require the agent to report unavailable capabilities instead of substituting a text description for an artifact.

### Google Antigravity-style agentic environments

Google’s official Antigravity documentation describes an agentic IDE with editor and browser surfaces, asynchronous local agents, parallel agents across codebases, and artifacts such as plans, code diffs, architecture diagrams, images, and browser recordings. [S32] Antigravity’s CLI and SDK documentation describes fine-grained permissions, deny/ask/allow lists, a native terminal sandbox, and policy hooks. [S33] [S34] Workspace rules are documented under `.agents/rules`, with global rules in `~/.gemini/GEMINI.md`; the docs note backward support for `.agent/rules`. [S35]

Practical expectation: Antigravity may make end-to-end browser verification, asynchronous decomposition, artifact review, and multi-agent execution especially visible. That visibility does not make the output correct. Headless mode can soft-deny tools that require approval, and the docs distinguish workspace access, shell permission, browser permission, and sandbox escape. [S36]

Mitigation:

- make the router’s acceptance tests explicit because an artifact or recording proves what was observed, not that every constraint was met;
- configure least-privilege allow/ask/deny rules for shell, browser, MCP, and non-workspace access;
- do not rely on asynchronous agents sharing the same working state unless the host documents the synchronization behavior;
- require each subagent to return a scoped evidence bundle and merge only through a parent ledger;
- treat headless soft-denials as failed evidence, not successful completion;
- record host, version, model, permission mode, sandbox state, and artifact identifiers in the run manifest.

### Portable contract

The common denominator should be a host-neutral envelope:

```yaml
task:
  request_id: fake-art-2026-08-28-001
  original_request: "verbatim user request"
  operation: edit
  primary_representation: photography
  adjacent_representations: [graphic-design]
constraints:
  hard: [{id: c1, name: protected_region, value: "subject face and product"}]
  soft: [{id: c2, name: mood, value: "warm late-afternoon light"}]
  unknown: [{id: c3, name: output_format}]
delivery: {channel: web, dimensions: "1200x800", format: png}
evidence_required: [metadata, protected-region-diff, visual-review]
holds: [rights, safety, accessibility, provider-mismatch]
non_claims: [ownership, clearance, consent-validity, release-readiness]
```

The example is intentionally fake and contains no real personal data. A host adapter can map this envelope to Cursor rules, Claude Code permissions and memory, or Antigravity rules and policy hooks. The acceptance semantics must not change with the host.

## Recommendations for the art router

### P0: Add operation-aware routing

Keep the current representation rows. Add an operation taxonomy and require one or more operations before selecting a provider. At minimum: `generate`, `edit`, `inpaint`, `outpaint`, `remove`, `composite`, `restyle`, `vectorize`, `animate`, `extend`, `translate`, `remix`, `write`, `map`, `fabricate`, and `deploy`.

The operation determines the invariant set. An inpaint route protects the unmasked region; a vector route protects text and editability; a video extension route protects the prior clip and continuity; a map route protects data and CRS; a fabrication route protects scale and material constraints.

### P0: Make the constraint ledger a required handoff

Add the ledger to every art manifest and agent handoff. Require a before/after status for each hard constraint. Keep user language and normalized values side by side. A missing or unverified hard constraint produces `hold` or `revise`, never a green summary.

### P0: Add provider capability manifests

Provider entries should declare supported input and output media, parameter ranges, reference-image roles, edit locality guarantees, duration and resolution limits, audio or voice support, safety-filter behavior, export formats, provenance support, cost or rate-limit considerations, and known verification paths. Treat every entry as versioned and date-stamped. If a capability is undocumented, mark it unknown and require a proof-of-capability test.

### P0: Add safe preflight and hold triggers

Implement deterministic checks for identity and consent, rights-sensitive styles or source material, unsafe sexual or deceptive content, prompt injection in references, exact text versus raster-only generation, physical permanence, map factuality, and missing delivery conditions. Keep legal, cultural, venue, medical, and professional safety decisions with named human reviewers.

### P1: Add modality-specific acceptance probes

Use small, repeatable checks before expensive generation: image metadata and masks; SVG parse, text, and accessibility fields; glTF load and scene inventory; video duration and frame-rate inspection; audio duration, sample rate, clipping, and stems; comic panel and text extraction; browser interaction and accessibility smoke tests; map CRS and data-source checks; and manufacturing dimensions or dieline checks.

### P1: Add provenance and disclosure hooks

C2PA describes cryptographically verifiable provenance, ingredient history, actions, AI-ML output declarations, prompts as possible inputs, and rights-related assertions. [S37] Use provenance where supported, but preserve privacy controls and explain that valid provenance does not prove that the underlying claims are true. Record model, tool, input, prompt, human edit, and export history in a separate internal manifest when C2PA is unavailable.

### P1: Add host adapters with a common evidence schema

Create adapters for the three documented host families, but keep the contract and evidence schema host-neutral. A host adapter should declare available read, transform, render, browser, shell, MCP, and delegation capabilities; permission state; sandbox state; and whether a human approval is available. Never infer capability from brand or model name.

### P2: Add a correction loop that preserves locality

When a result fails one constraint, generate a minimal repair plan and rerun only the affected operation. Require a new diff against the original ledger. This is most important for inpainting, text correction, logo cleanup, character continuity, audio repair, and map label changes.

### P2: Add human review roles to the route

The route should name the needed reviewer without pretending to perform that review: rights or trademark reviewer, likeness/consent owner, cultural authority, accessibility reviewer, tattoo professional, venue or structural professional, audio rights owner, or accountable release owner. The existing reviewer skill’s non-claims should remain intact.

## Test strategy and proof of work

This research run did not alter router code, so the implementation recommendations were not represented as completed code. The evidence was tested by source retrieval, current-router inspection, and report validation. The following test suite is the smallest useful proof plan for implementing the recommendations.

### Contract and drift fixtures

Create synthetic, non-identifying fixtures with expected outcomes:

- `image-edit-locality`: change only a masked sky; a changed face or protected foreground is `hold`.
- `logo-live-text`: exact wordmark text plus live SVG text; a PNG-only provider is `provider-mismatch`.
- `video-duration`: request 8 seconds with first and last frames; a provider capability manifest that cannot satisfy either frame is `revise`.
- `voice-consent`: user-owned voice with consent evidence passes the identity preflight; a named public figure without rights is `rights_hold`.
- `map-factuality`: supplied dataset, CRS, date, legend, and source pass metadata checks; an invented location is `hold`.
- `xr-permission`: browser artwork includes explicit user activation and a non-XR fallback; missing fallback or permission path is `evidence_hold`.
- `tattoo-permanence`: stencil request records placement, line-weight review, and professional handoff; absent professional review remains `hold`.
- `agent-injection`: a reference image or imported page contains an instruction-shaped string; the string must remain data and cannot alter the ledger.

### Acceptance criteria

An implementation is ready for adversarial review when it can:

- preserve the original request verbatim and produce stable normalized constraint IDs;
- distinguish hard, soft, unknown, inferred, and prohibited values;
- report provider mismatch before generation when a hard constraint is unsupported;
- detect protected-region drift and exact metadata drift;
- retain source and output hashes without claiming that hashes prove rights or quality;
- emit an explicit hold for unresolved rights, consent, safety, cultural, accessibility, factuality, or delivery questions;
- produce the same route and acceptance semantics under Cursor, Claude Code, and Antigravity adapters when given the same envelope;
- record host-specific capabilities and permissions without changing the user’s constraints;
- fail loudly when a headless or sandboxed host denies required evidence;
- keep all external text, reference assets, MCP output, and agent responses in the data plane rather than the instruction plane.

### Validation performed for this report

- QMD corpus audit completed; index was empty and this limitation is recorded above.
- Required repository and specialist instructions were read before drafting.
- Official primary sources were gathered for NIST, the U.S. Copyright Office, W3C, Khronos, OGC, USGS, USPTO, FDA, CPSC, FTC, Adobe, ElevenLabs, Cursor, Anthropic, Google Antigravity, OWASP, and C2PA.
- Report frontmatter, required sections, source identifiers, and changed-file scope were checked locally after writing.
- `git diff --check` was run to detect whitespace errors.

## Open questions and uncertainty

- The worktree’s QMD index is empty, so corpus coverage and prior decisions could not be measured through retrieval. Re-indexing is a separate maintenance action and was intentionally not performed because the user restricted changes to the research/results scope.
- No source reviewed here establishes a universal ranking of artistic request frequency or a universal failure rate for any provider. The taxonomy is coverage-oriented.
- Provider limits, model names, safety filters, permission defaults, and plan availability can change. Store retrieval date, URL, provider version, and observed capability in the router’s capability registry.
- Legal treatment of AI-assisted work, likeness, voice, trademarks, training data, and physical products varies by jurisdiction and fact pattern. The router can identify a review need; it cannot clear rights.
- C2PA provenance is opt-in and does not make the underlying claims true. It is a tamper-evident provenance mechanism, not a truth oracle.
- WebXR and WebGPU specifications evolve. A target browser and device test remains necessary even when a feature appears in a standard.

## Sources

All sources below were accessed or checked on 2026-08-28. Product and standards status claims should be rechecked before implementation or release.

- **[S01]** [U.S. Copyright Office: Copyright and Artificial Intelligence, Part 2, Copyrightability](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf) — human authorship, prompting, arrangement, and modification.
- **[S02]** [U.S. Copyright Office: Copyright and Artificial Intelligence overview](https://www.copyright.gov/ai/) — report parts and current status.
- **[S03]** [Adobe Firefly: Using masks for image manipulation](https://developer.adobe.com/firefly-services/docs/firefly-api/guides/concepts/masking/) — protected and exposed mask regions.
- **[S04]** [Adobe Firefly: Style image references](https://developer.adobe.com/firefly-services/docs/firefly-api/guides/concepts/style-image-reference/) — style references and strength.
- **[S05]** [Adobe Photoshop API: Inpainting with fill mask](https://developer.adobe.com/firefly-services/docs/photoshop/guides/using-fill-mask/) — masked-area inpainting workflow.
- **[S06]** [W3C SVG 2: Text](https://www.w3.org/TR/SVG/text.html) — live SVG text, searchability, and semantic labeling.
- **[S07]** [W3C SVG 1.1: Accessibility support](https://www.w3.org/TR/SVG11/access.html) — text equivalents, structure, color, and dynamic content.
- **[S08]** [USPTO: Federal trademark searching](https://www.uspto.gov/trademarks/search/federal-trademark-searching) — clearance-search guidance.
- **[S09]** [USPTO: Design search codes](https://www.uspto.gov/trademarks/search/design-search-codes) — searching similar design elements.
- **[S10]** [U.S. Copyright Office Compendium: Typeface and lettering](https://www.copyright.gov/comp3/2017version/docs/compendium.pdf) — limits for typeface and lettering claims.
- **[S11]** [Khronos glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) — runtime delivery versus authoring format and scene components.
- **[S12]** [Google AI for Developers: Video generation in the Gemini API](https://ai.google.dev/gemini-api/docs/video) — documented video inputs, outputs, reference images, frames, extension, and limits.
- **[S13]** [W3C WCAG 2.2: Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) — moving and auto-updating content controls.
- **[S14]** [U.S. Copyright Office: What musicians should know about copyright](https://www.copyright.gov/engage/musicians/) — separate musical-work and sound-recording rights.
- **[S15]** [ElevenLabs: Voice cloning overview](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning) — verification and professional-cloning restrictions.
- **[S16]** [ElevenLabs: Prohibited Use Policy](https://elevenlabs.io/use-policy) — consent or legal-right boundary for intentional voice replication.
- **[S17]** [NIST AI 600-1: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) — confabulation, prompt injection, IP, privacy, and abusive-content risks.
- **[S18]** [W3C WebXR Device API](https://www.w3.org/TR/webxr/) — user intent, feature availability, tracking, latency, and security.
- **[S19]** [W3C WebGPU](https://www.w3.org/TR/webgpu/) — origin restrictions for image sources.
- **[S20]** [OGC API - Maps](https://www.ogc.org/standards/ogcapi-maps/) — styled geospatial portrayals, extents, CRS, and outputs.
- **[S21]** [USGS: Cartographic representation](https://www.usgs.gov/centers/cegis/science/science-topics/cartographic-representation) — extent-dependent detail and generalization.
- **[S22]** [FDA: Tattoos and permanent makeup](https://www.fda.gov/cosmetics/cosmetic-products/tattoos-temporary-tattoos-and-permanent-makeup) — permanence, inks, and health risks.
- **[S23]** [CPSC: Additive manufacturing and 3D printing](https://www.cpsc.gov/Regulations-Laws--Standards/Voluntary-Standards/Additive-Manufacturing-3D-Printing) — process and product safety standards work.
- **[S24]** [FTC: Apparel and labeling](https://www.ftc.gov/news-events/topics/tools-consumers/apparel-labeling) — textile labeling requirements.
- **[S25]** [OWASP GenAI: Top 10 risks for LLMs and GenAI applications, 2025](https://genai.owasp.org/llm-top-10/) — prompt injection, improper output handling, excessive agency, misinformation, and related risks.
- **[S26]** [Cursor: Agent overview](https://cursor.com/docs/agent/overview) — documented agent tools and image-generation capability.
- **[S27]** [Cursor: Rules](https://prod.cursor.com/docs/rules) — project, user, team, and `AGENTS.md` instruction surfaces.
- **[S28]** [Cursor: MCP integrations](https://prod.cursor.com/help/customization/mcp) — MCP discovery and approval behavior.
- **[S29]** [Anthropic: Claude Code CLI reference](https://docs.anthropic.com/en/docs/claude-code/cli-usage) — CLI modes, permissions, tools, MCP, and turn limits.
- **[S30]** [Anthropic: Claude Code memory](https://docs.anthropic.com/en/docs/claude-code/memory) — `CLAUDE.md` discovery and imports.
- **[S31]** [Anthropic: Tool use overview](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview) — client-side and server-side tools.
- **[S32]** [Google Antigravity: IDE overview](https://antigravity.google/docs/ide/overview/) — editor, terminal, browser, parallel agents, and artifacts.
- **[S33]** [Google Antigravity: CLI permissions](https://antigravity.google/docs/cli/permissions/) — fine-grained allow, ask, and deny rules.
- **[S34]** [Google Antigravity: SDK safety policies](https://www.antigravity.google/docs/sdk/policies/) — declarative policies and human approval hooks.
- **[S35]** [Google Antigravity: Rules](https://www.antigravity.google/docs/ide/rules/) — global and workspace rule locations and activation modes.
- **[S36]** [Google Antigravity: Headless mode](https://antigravity.google/docs/cli/headless/) — soft-denied approvals and scoped allow rules.
- **[S37]** [C2PA Specifications 2.4](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html) — provenance, AI disclosure, privacy, and integrity boundaries.

## Changed files

- Added [art-router-research.md](art-router-research.md).

No other files were changed.
