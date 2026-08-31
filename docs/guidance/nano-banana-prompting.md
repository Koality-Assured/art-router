---
doc_kind: guidance
canonical_id: nano-banana-prompting
purpose: [reinforcement]
rank: high
topics: [generative-ai, image-generation, image-editing, gemini, nano-banana, prompting, model-routing, evaluation]
rag_keywords: [nano-banana, prompt-template, iteration, model-routing, reference-images, aspect-ratio, image-size, previous-interaction-id, grounding, failure-diagnosis, release-checklist]
---

# Nano Banana prompting playbook

## Use this playbook

Use this playbook for Google Gemini image generation or editing when the exact provider surface and model are known. It implements [`../standards/nano-banana-image-generation.md`](../standards/nano-banana-image-generation.md); it does not replace [`../standards/artistic-request-contract.md`](../standards/artistic-request-contract.md), [`../standards/artistic-practice.md`](../standards/artistic-practice.md), or [`../standards/artistic-representations.md`](../standards/artistic-representations.md).

Google’s [image-generation guide](https://ai.google.dev/gemini-api/docs/image-generation) is the primary reference for prompt structure, editing, references, grounding, and image settings. Verify current model IDs and capabilities on Google’s [API models page](https://ai.google.dev/gemini-api/docs/models) before shipping a workflow. API, AI Studio, and Gemini app behavior may differ; do not infer UI/API parity.

## Compact prompt template

Fill the request contract first. Then compile only the fields that matter to the selected image task.

```text
Create [deliverable] for [audience/use].
Subject: [count, identity, action, materials; map each reference by role].
Scene/composition: [setting, focal point, placement, foreground/background, negative space, reading order].
Style/light/camera: [medium, palette, surface, lighting, shot, angle, lens, depth of field].
Text/layout: [exact strings, language, hierarchy, placement, legibility].
Output: [aspect ratio and image size; exact model is recorded outside the prose].
Acceptance: [what must be present, exact, unchanged, or reviewed].
```

For an edit, start with the delta and name the source image: `Change [one property] in [source role]. Preserve [framing, identity, count, pose, text, palette, aspect ratio, and other invariants].` Google recommends small conversational changes for iterative editing. Semantic description of the intended state is a vendor recommendation to test, not a guarantee that exclusions will work.

## Route by task

- Choose `gemini-3.1-flash-image` (Nano Banana 2) as the general current route when the task needs image input, conversational editing, thinking, Search grounding, Image Search grounding, or a 0.5K/1K/2K/4K output envelope.
- Choose `gemini-3.1-flash-lite-image` (Nano Banana 2 Lite) for efficiency-sensitive work that fits its 1K-only output and does not require Google Search grounding. Avoid routing multi-reference or sequential multi-turn work to Lite without a tested capability decision; Google’s guide says it is not optimized for those cases.
- Choose `gemini-3-pro-image` (Nano Banana Pro) for complex professional assets, text-heavy layouts, factual visualizations, Search grounding, thinking, or 1K/2K/4K output. Use the stable model page ID; some guide examples use preview-style names.
- Keep `gemini-2.5-flash-image` only for an existing dependency or a migration comparison. New work SHOULD test a current route instead.

Record the exact model ID, provider surface, date, and live capability result. Do not use “Nano Banana” as the endpoint value, and do not silently substitute a model when the selected route cannot satisfy a required setting.

## Reference and edit setup

Create a reference ledger before the request:

```text
Reference A: [asset ID/path; role: object | character | style; order; rights; likeness/permission status]
Reference B: [asset ID/path; role; order; rights; likeness/permission status]
Requested delta: [one change]
Preserve: [all unrequested identity, count, pose, framing, text, palette, and geometry]
```

Google documents up to 14 images at family level, with smaller model-specific allocations. Treat those limits as input limits, not fidelity guarantees. If an image depicts a recognizable person, record likeness consent separately from the right to upload the file. If the provider cannot represent a reference role or preserve a required invariant, record a capability gap and stop for a choice.

## API-shaped request

The following is provider-aware pseudocode, not a promise that every SDK exposes this exact object shape. Confirm the selected surface’s current schema in Google’s [image-generation guide](https://ai.google.dev/gemini-api/docs/image-generation). A UI flow may expose different controls.

```python
request = {
    "model": "gemini-3.1-flash-image",  # record the exact stable ID
    "input": [
        {"text": prompt_text},
        # Attach reference image data using the selected API's documented part shape.
    ],
    "response_format": {
        "type": "image",
        "aspect_ratio": "16:9",
        "image_size": "2K",
    },
    # Add Search or Image Search only when the selected model and surface support it.
    # Add previous_interaction_id for a supported conversational edit.
}
response = provider.generate(request)

# Inspect response blocks, safety feedback, citations, and image parts.
# Save the final rendered image, raw response, request record, and derivative hash.
```

Set aspect ratio and image size when delivery geometry matters. Current Google documentation describes 1K as the Gemini 3 default; Lite is 1K-only. Do not assume a diffusion-style seed, CFG scale, negative-prompt weight, or universal image-count parameter is available across these models.

## Iteration loop

1. Normalize the request and classify unknowns, conflicts, permissions, and required invariants before generating.
2. Route to a model whose documented envelope matches the task. Record the exact ID and surface.
3. Generate at a reviewable resolution and inspect the output against content, count, placement, identity, text, composition, and safety checks.
4. Change one material property at a time. For conversational edits, use `previous_interaction_id` only where the selected API supports it, and repeat the invariants in the edit prompt.
5. If the issue is text, simplify the copy or layout and verify the transcription manually or programmatically. Google documents small text, long paragraphs, spelling, and full-page layout as failure risks.
6. If the issue is spatial or identity drift, reduce the delta, restate source roles and invariants, inspect for copy/paste or left/right confusion, and consider a different model route.
7. Save the accepted output and evidence record. Do not treat a visually attractive result as accepted until rights, likeness, cultural, accessibility, provenance, and delivery checks pass.

Batch API is suitable for independent variants when up to 24 hours of turnaround is acceptable. It is not a substitute for this interactive correction loop.

## Failure diagnosis

- **No image or blocked response:** Separate prompt feedback from candidate safety ratings. Record the image-specific error (`image_safety`, `image_prohibited_content`, `image_recitation`, or `image_other`) when returned. Review the request; do not lower safety thresholds to force yield.
- **Wrong count, merged subjects, or omitted object:** Rewrite the subject inventory with explicit count and role mapping, then test a smaller scene. This is a diagnosis and next experiment, not a claim that more words guarantee compliance.
- **Reference drift or unnatural blend:** Check image order, role labels, model-specific reference limits, and permissions. Reduce the reference set or route to a model suited to the required reference mix.
- **Edit changes untouched areas:** Put the requested delta first, list invariants, use a small conversational edit, and compare against the prior version. Record any unavoidable collateral change as a deviation.
- **Text is wrong or unreadable:** Treat text as its own acceptance test. Reduce copy, state exact strings and placement, and verify at delivery size; higher resolution does not repair incorrect text.
- **Factual or time-sensitive graphic is stale:** Use documented Search grounding where supported, preserve returned citations or attribution, and independently check every factual claim. Grounding is not independent verification.
- **Latency or cost misses the target:** Measure the deployment. Google’s Lite sub-two-second statement is a product design target, not a guarantee. Record resolution, aspect ratio, tokens where exposed, retries, and blocked or no-image outcomes.
- **Provenance disappears after export:** Keep the original response and hashes, inspect SynthID where verification is available, preserve C2PA when present, and document metadata loss after resizing, recompression, screenshotting, editing, or export.

## Release checklist

- [ ] Exact stable model ID, provider surface, date, and live capability check are recorded.
- [ ] The normalized request preserves required text, references, constraints, invariants, permissions, and open questions.
- [ ] Prompt, reference order and roles, response format, aspect ratio, image size, tools, thinking configuration, interaction lineage, output hash, and human edits are saved.
- [ ] Required content, count, placement, identity, text, composition, and unchanged regions passed review at delivery size.
- [ ] Safety feedback, ratings, errors, blocked/no-image outcomes, and escalation are recorded.
- [ ] Rights, likeness consent, cultural-authority, trademark/property, and publication decisions are complete.
- [ ] Factual claims and grounding citations/attribution were checked where applicable.
- [ ] Alt or long description and the applicable delivery/accessibility checks are shipped with the asset.
- [ ] Disclosure, SynthID/C2PA observations, metadata preservation, and derivative history are recorded.
- [ ] A second reviewer accepted the result, limitations, and correction or withdrawal path.

No live generation benchmark was run for this repository. Prompt structures, routing choices, latency expectations, and failure mitigations in this playbook are therefore operational guidance grounded in vendor documentation and the completed research note, not locally validated performance claims.
