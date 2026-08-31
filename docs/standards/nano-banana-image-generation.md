---
doc_kind: requirement
canonical_id: nano-banana-image-generation
purpose: [requirement, reinforcement]
rank: high
topics: [generative-ai, image-generation, image-editing, gemini, nano-banana, provenance, safety, evaluation]
rag_keywords: [nano-banana, nano-banana-2, nano-banana-pro, gemini-3.1-flash-image, gemini-3.1-flash-lite-image, gemini-3-pro-image, gemini-2.5-flash-image, prompt-contract, reference-images, grounding, SynthID, C2PA, safety, likeness, cultural-review, accessibility, reproducibility]
---

# Nano Banana image-generation standard

## Scope and authority

This annex governs repository workflows that generate or edit images through Google’s Gemini image models marketed as Nano Banana. It is a provider-specific control layer. The repository’s universal intent, authorship, provenance, cultural, accessibility, safety, critique, and release controls remain in [`artistic-practice.md`](./artistic-practice.md); representation-specific delivery gates remain in [`artistic-representations.md`](./artistic-representations.md); and request normalization remains in [`artistic-request-contract.md`](./artistic-request-contract.md).

“Google documents” identifies a vendor capability, requirement, limitation, or recommendation. “Repository control” identifies a MUST or SHOULD imposed by this annex. A vendor recommendation is not evidence of guaranteed behavior.

The governing vendor references are Google’s [image-generation guide](https://ai.google.dev/gemini-api/docs/image-generation), [API models page](https://ai.google.dev/gemini-api/docs/models), [Gemini 3.1 Flash Image model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-image), [Gemini 3.1 Flash-Lite Image model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite-image), [Gemini 3 Pro Image model page](https://ai.google.dev/gemini-api/docs/models/gemini-3-pro-image), [Gemini 2.5 Flash Image model page](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-image), [API safety guidance](https://ai.google.dev/gemini-api/docs/safety-guidance), [safety settings](https://ai.google.dev/gemini-api/docs/safety-settings), [API errors](https://ai.google.dev/gemini-api/docs/api-errors), and [SynthID documentation](https://deepmind.google/models/synthid/).

## Model and version selection

The exact model ID MUST be recorded for every generation. “Nano Banana” is a product-family label, not an endpoint alias.

Use the following current model map as a routing baseline, then verify live availability and capabilities before implementation:

- **Nano Banana 2:** `gemini-3.1-flash-image`. Google documents it as the general-purpose current model with image input, conversational editing, thinking, Search grounding, Image Search grounding, and 0.5K/1K/2K/4K output.
- **Nano Banana 2 Lite:** `gemini-3.1-flash-lite-image`. Google documents it as the efficiency choice with 1K-only output and no Google Search grounding. The guide says it is not optimized for multiple reference inputs or multi-turn sequential editing.
- **Nano Banana Pro:** `gemini-3-pro-image`. Google documents it for complex professional assets, text-heavy layouts, factual visualizations, Search grounding, thinking, and 1K/2K/4K output.
- **Legacy Nano Banana:** `gemini-2.5-flash-image`. Google documents conversational generation and editing at 1K, without thinking or Search grounding. New work SHOULD test migration to a current model.

The implementation MUST use the stable model-page ID or a live capability declaration. It MUST NOT silently substitute a preview ID, a different model, or Imagen. Google’s guide and models page identify Imagen 4 as deprecated; any exception requires a fresh availability and migration check.

## Prompt contract

Before execution, the owner MUST normalize the request with [`artistic-request-contract.md`](./artistic-request-contract.md), preserving exact text, dimensions, names, exclusions, references, consent limits, unknowns, and edit invariants. The image-specific prompt MAY compile these fields into the following brief:

```text
Intent and deliverable: [purpose, audience, medium, aspect ratio, what must read]
Subject inventory: [subjects, count, identity, action, materials, reference-image roles]
Scene and composition: [setting, foreground/background, focal point, placement, negative space, reading order]
Style and medium: [photo, illustration, render, poster, diagram, texture, palette, surface]
Light and camera: [time, direction, softness, contrast, shot, angle, lens, depth of field, motion]
Text and layout: [exact strings, language, hierarchy, placement, font character, unchanged text on edits]
Requested delta: [for edits, change only this]
Preserve: [framing, identity, count, pose, palette, text, aspect ratio, and other invariants]
Output controls: [model ID, aspect ratio, image size, tools, thinking configuration]
Acceptance checks: [content, placement, text, facts, safety, rights, provenance, delivery]
```

Google’s documented prompting recommendations include detailed subject, setting, intent, photographic or cinematic terms where useful, stepwise descriptions for complex scenes, semantic description of an intended state, and small conversational edits. These are working instructions to test, not validated performance claims. Text, fine detail, spatial relationships, and character consistency MUST be checked in the result.

## Reference-image handling

The caller MUST maintain a reference ledger that identifies each input by role, order, source, permission status, transformation scope, and whether it is an object, character, or style reference. Rights to upload an image MUST be established separately from consent to depict or modify a recognizable person, permission to use a trademark or property, and permission to publish a derivative.

Google documents a family-level workflow limit of up to 14 images with model-specific allocations: Lite up to 14 object references; Flash Image up to 10 object and up to 4 character references; and Pro up to 6 object, up to 5 character, and up to 3 style references. These are documented input limits, not a promise that every reference will be preserved or represented correctly. The workflow MUST hold or escalate when a requested reference cannot be represented, when order or role is ambiguous, or when the provider rejects an input.

For edits, the prompt MUST identify the source image and requested delta and state what remains invariant. The reviewer MUST check for copy/paste leakage, left/right or spatial confusion, unintended blending, persistent mask or doodle marks, and changes outside the requested region.

## API and configuration controls

The workflow MUST record the provider surface, exact model ID, date, prompt, reference assets and order, response format, aspect ratio, image size, tools, thinking configuration where exposed, interaction lineage, response status, and output hash. AI Studio, the Gemini app, and APIs may expose different wrappers and defaults; documentation for one surface MUST NOT be treated as proof of parity with another.

When delivery geometry matters, the API request SHOULD set `response_format` with an image type, `aspect_ratio`, and `image_size`. Google documents 1K as the current Gemini 3 default; Flash Image also documents 0.5K, 2K, and 4K, Pro documents 1K, 2K, and 4K, and Lite documents 1K only. The requested resolution MUST match the chosen model’s live capability declaration. Higher resolution is not a correction for wrong content, spelling, or composition.

For conversational API edits, `previous_interaction_id` MAY carry prior interaction context where the selected surface supports it. Batch API MAY be used for independent queued variants when a turnaround of up to 24 hours is acceptable; it is not an interactive correction loop.

Clients handling interleaved responses MUST inspect response steps when text and image blocks both matter. A convenience `output_image` property MUST NOT be assumed to contain every block. If thinking emits interim images, the workflow MUST identify the documented final rendered image before saving an asset.

The repository MUST treat seed replay, negative-prompt weighting, CFG scale, and a universal image-count control as unsupported unless the selected provider surface explicitly declares and the workflow verifies them. The reviewed Google documentation does not establish these as stable cross-model controls.

## Safety and blocked outputs

Google documents adjustable filters for harassment, hate speech, sexually explicit content, and dangerous content, while some core harms, including child safety, are always blocked. Filtering is based on probability of unsafe content rather than harm severity. A low-probability rating MUST NOT be treated as approval for a high-severity use case.

The caller MUST retain prompt feedback, candidate safety ratings, and relevant errors when exposed. The workflow MUST distinguish a blocked prompt from a blocked or absent image and MUST handle image-specific failures such as `image_safety`, `image_prohibited_content`, `image_recitation`, and `image_other` as reviewable outcomes. It MUST NOT lower safety thresholds solely to increase output yield.

The repository MUST apply the security rules in [`../agent-session-security.md`](../agent-session-security.md) and the human, consent, cultural-authority, legal, accessibility, and escalation controls in the linked artistic standards. Google’s policy or a successful API response does not provide repository approval.

## Provenance, disclosure, and grounding

Google’s image-generation guide says generated images include a SynthID watermark. Google DeepMind describes SynthID as an imperceptible watermark designed to remain detectable through common transformations, while noting that extreme manipulation can defeat it. A watermark signal is evidence relevant to Google-AI generation; it is not proof of human authorship, ownership, factuality, or an unbroken edit history.

The workflow MUST disclose material generation or manipulation to the audience and record the model, inputs, prompt, exposed settings, human decisions, edits, and reproducibility limits. It MUST preserve the original response and hash derivatives where provenance matters. If a saved response or file contains C2PA, the workflow MUST preserve the manifest where delivery permits it; it MUST NOT promise C2PA coverage for every model or export path.

If Search or Image Search grounding is used, the workflow MUST retain returned citations and attribution metadata. For Image Search, it MUST satisfy Google’s documented requirement to display `search_suggestions`. Grounding does not remove the need to check factual claims.

## Rights, likeness, and cultural review

The owner MUST apply the rights, likeness, cultural-authority, consent, benefit, withdrawal, and correction controls in [`artistic-practice.md`](./artistic-practice.md), and the representation-specific gates in [`artistic-representations.md`](./artistic-representations.md). This annex does not restate those universal controls.

Image-specific review MUST separately record rights for every uploaded reference, consent or permission scope for recognizable people, trademark or property concerns, intended derivative and publication scope, and unresolved ownership or permission questions. A reference image license does not establish likeness consent. Cultural or living-heritage material MUST follow the existing authority and consultation path; a prompt or model capability does not create permission.

## Accessibility and delivery

The delivery owner MUST test the saved asset at its actual target size, device, background, language, and receiving surface, applying [`artistic-representations.md`](./artistic-representations.md). An informative image MUST ship with an equivalent description or other applicable alternative. Text in an image MUST be checked for exactness, language, contrast, reading order, and legibility; small text, long paragraphs, spelling, and full-page layouts are documented failure risks.

The package MUST identify format, dimensions, color assumptions, compression or resizing, alt or long description, disclosure, provenance metadata, and the correction or withdrawal contact. A delivery transformation that strips metadata or changes material content MUST be recorded.

## Reproducibility and evaluation

The owner MUST keep a generation record containing the exact model ID and surface, date, prompt, reference files and order, aspect ratio, image size, tools, thinking configuration, interaction lineage, output hash, safety outcome, and human edits. Unknown or unsupported controls MUST be recorded as unknown or unsupported; they MUST NOT be filled with assumed defaults.

Evaluation MUST use task-specific checks for required content and count, placement, identity, unchanged-region preservation, text exactness, aspect-ratio compliance, factual accuracy, visual quality, reviewer preference, latency, timeout and retry rate, output count, blocked-request and `no_image` rate, and token or cost data where exposed. Model-card comparisons are vendor-run evidence and MUST NOT be presented as local benchmark results. Grounded and ungrounded or differently configured runs MUST be labeled separately.

When the model, wrapper, grounding, output size, or prompt template changes, the owner SHOULD rerun a durable regression set containing representative successful and failed prompts. Repeated trials SHOULD be used because the reviewed vendor documentation does not establish deterministic output.

No live generation benchmark was run for this repository. This standard therefore does not validate latency, visual quality, safety recall, language parity, or reproducibility in the target deployment.

## Release evidence

Release is blocked until the evidence record shows, as applicable:

- exact model, surface, request settings, references, output hash, and interaction lineage;
- prompt-contract acceptance checks and recorded deviations;
- safety status, ratings or errors, and any escalation decision;
- rights, likeness, cultural-authority, and consent decisions;
- factual and text review, including grounding citations or attribution when used;
- accessibility and delivery-condition test with equivalent description;
- disclosure, SynthID/C2PA observations, metadata preservation, and derivative history;
- second-person review, accepted limitations, and correction, rollback, or withdrawal contact.

## Non-claims

This annex does not claim that a model will follow a prompt, preserve an edit invariant, represent every reference, render text correctly, produce a particular number of images, be deterministic, be factually correct, be accessible, or be legally safe. It does not claim that a model card is an independent benchmark, that SynthID proves authorship or ownership, that C2PA is universal, that a successful safety response is human approval, or that API, AI Studio, and Gemini app behavior is interchangeable. It does not replace human artistic, legal, accessibility, safety, community, or professional review.
