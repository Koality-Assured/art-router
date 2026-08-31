---
doc_kind: research
canonical_id: nano-banana-prompting-generation
purpose: [research, validation]
rank: high
status: complete
date: 2026-08-31
topics: [generative-ai, image-generation, prompting, gemini, nano-banana, provenance, safety, evaluation]
rag_keywords: [nano-banana, nano-banana-2, nano-banana-pro, gemini-3.1-flash-image, gemini-3.1-flash-lite-image, gemini-3-pro-image, gemini-2.5-flash-image, image-generation, image-editing, multi-turn, reference-images, text-rendering, grounding, google-search, image-search, SynthID, C2PA, safety-filters, model-card, human-evaluation, Elo, factuality, reproducibility]
---

# Nano Banana / Gemini image-generation prompting research

## Bottom line

As of 2026-08-31, “Nano Banana” is Google’s name for Gemini’s native image-generation and image-editing family, not one model. Google’s current API guide names four models: Nano Banana 2 Lite (`gemini-3.1-flash-lite-image`), Nano Banana 2 (`gemini-3.1-flash-image`), Nano Banana Pro (`gemini-3-pro-image`), and the legacy Nano Banana (`gemini-2.5-flash-image`). Google positions Nano Banana 2 as the general-purpose default, Lite for the lowest latency and cost, and Pro for complex professional assets, grounded generation, and higher-resolution output. The 2.5 model is still documented as stable, but Google recommends migration to Nano Banana 2 Lite.

The safest working assumption for a production workflow is: route by task, write prompts as an image brief rather than a keyword list, iterate with small explicit changes, and verify every output. Google’s own model cards still report failures in small text, long paragraphs, fine detail, character consistency, spatial localization, complex blending, and factuality. Generated images should be treated as candidate assets until visual, factual, rights, safety, and provenance checks pass.

This is a research note, not a proposed repository standard. “Vendor-documented” below means stated in Google documentation or a Google DeepMind model card. “Working recommendation” means an operational hypothesis derived from those facts that still needs fixture-based validation in the target workflow.

## Scope and method

I checked the in-repo research corpus first. The worktree’s `qmd` search and direct `qmd get` lookups returned no indexed documents, so I used targeted reads of the required repository instructions and the existing research-note shape. The external pass prioritized Google AI for Developers, Google DeepMind model cards, and Google DeepMind’s SynthID documentation. No image-generation API call was run in this worktree because no authorized generation credential or test fixture was provided; latency, quality, and safety claims are therefore not locally reproduced.

The primary current sources were:

- [Gemini API image generation guide](https://ai.google.dev/gemini-api/docs/image-generation) — model naming, prompting examples, editing, references, grounding, image sizes, limitations, and output configuration; last updated 2026-08-26.
- [Gemini API models](https://ai.google.dev/gemini-api/docs/models) — current model listing and endpoints; crawled 2026-08-31.
- [Gemini 3.1 Flash Image model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-image) — stable endpoint, capabilities, context/output details, and supported operations; last updated 2026-08-18.
- [Gemini 3.1 Flash-Lite Image model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite-image) — stable endpoint, 1K-only envelope, latency/cost positioning, and lack of Search grounding; last updated 2026-08-18.
- [Gemini 3 Pro Image model page](https://ai.google.dev/gemini-api/docs/models/gemini-3-pro-image) — stable endpoint and professional/grounded-image positioning; last updated 2026-08-18.
- [Gemini 2.5 Flash Image model page](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-image) — legacy Nano Banana model and stable/preview naming; last updated 2026-08-18.
- [Gemini 3.1 Flash Image model card](https://deepmind.google/models/model-cards/gemini-3-1-flash-image/) — evaluation design, benchmark categories, known limitations, and safety evaluation; published February 2026.
- [Gemini 3 Pro Image model card](https://deepmind.google/models/model-cards/gemini-3-pro-image/) — Pro evaluation categories, limitations, safety, and model-card caveats; published November 2025.
- [Gemini API safety guidance](https://ai.google.dev/gemini-api/docs/safety-guidance) and [safety settings](https://ai.google.dev/gemini-api/docs/safety-settings) — application responsibility, filters, thresholds, and feedback.
- [Gemini API errors](https://ai.google.dev/gemini-api/docs/api-errors) — image safety, prohibited-content, recitation, SPII, language, and no-image failure codes; last updated 2026-08-26.
- [SynthID at Google DeepMind](https://deepmind.google/models/synthid/) — watermark behavior and detection workflow.

## Current model map

The model names and endpoints below are Google’s current documented names. Do not treat “Nano Banana” as an endpoint alias; record the exact model ID in every generation record.

- **Nano Banana 2 — Gemini 3.1 Flash Image (`gemini-3.1-flash-image`)**. Google’s generalist, high-efficiency model. The API guide documents text and image input, conversational editing, thinking, Search grounding, Image Search grounding, 0.5K/1K/2K/4K output, and up to 14 reference images in the family-level section. The model page says it is stable and supports image generation, image editing, Search grounding, and thinking.
- **Nano Banana 2 Lite — Gemini 3.1 Flash-Lite Image (`gemini-3.1-flash-lite-image`)**. The efficiency choice for high-volume interactive work. Google documents a 1K-only output envelope and no Google Search grounding. The image-generation guide also says it is not optimized for multiple reference inputs or multi-turn sequential editing; the model page describes fast local edits and a sub-2-second target as a product design goal, not a guarantee for a deployment.
- **Nano Banana Pro — Gemini 3 Pro Image (`gemini-3-pro-image`)**. The professional choice for complex visual tasks, text-heavy layouts, factual visualizations, and Search-grounded work. Google documents thinking, 1K/2K/4K output, and a smaller reference-image envelope than Flash Image for objects but more character/style-reference options. Use the stable model page as the endpoint authority; some Gemini 3 guide examples still show preview-style IDs.
- **Nano Banana — Gemini 2.5 Flash Image (`gemini-2.5-flash-image`)**. The legacy 1K image model. Google documents conversational generation/editing and no thinking or Search grounding for this model. Existing integrations may still depend on it, but new work should test migration to a current model rather than assume behavioral equivalence.

Google’s current models page also marks Imagen 4 as deprecated, and the image-generation guide says Imagen models are scheduled for shutdown on 2026-08-17. Since the research date is after that date, a new workflow should not select Imagen without checking live availability and migration status.

## Vendor-documented prompting practices

Google’s guide is unusually concrete about prompt structure. The following practices are documented recommendations, not guarantees of compliance:

- **Describe the subject, setting, and intended use in detail.** Google’s examples specify the shot type, subject attributes and action, environment, lighting, camera angle, lens, visual style, medium, color, and background. For a product shot, the guide adds surface, lighting purpose, camera angle, and the feature that should be sharp.
- **Give context and intent.** Google says that explaining the purpose of an image changes the model’s understanding; “a logo for a high-end minimalist skincare brand” is more informative than “create a logo.” Treat intent as a design constraint, not decorative prose.
- **Use photographic or cinematic language when composition matters.** Terms such as wide-angle, macro, low angle, depth of field, lighting direction, and shot type are part of Google’s examples. They are useful controls to test, not a universal guarantee of camera-accurate geometry.
- **Use step-by-step instructions for complex scenes.** The guide’s example builds a background, then a foreground object, then a focal object. This is a useful way to assign salience and reduce omission, but it is not a formal scene-graph interface.
- **Prefer semantic negative prompts.** Instead of only saying “no cars,” describe the intended state, such as an empty street with no traffic. This is a vendor recommendation for more reliable positive scene specification; it should be tested against direct exclusions for the actual model and task.
- **Iterate conversationally with small changes.** Google calls multi-turn conversation the recommended way to iterate and shows prompts that change one property while preserving the rest. For API workflows, `previous_interaction_id` carries the prior interaction into the next edit.
- **Treat text as a separate quality risk.** Google documents strong text-rendering capability for current Gemini 3 image models but also lists small text, long paragraphs, spelling, and page length as known weaknesses. The image-generation guide specifically recommends generating the desired text first and then asking for an image with that text. A final human or programmatic transcription check remains necessary.
- **Use references deliberately.** The family-level guide documents up to 14 images in a workflow, with model-specific allocations: Lite up to 14 objects; Flash Image up to 10 objects and up to 4 characters; Pro up to 6 objects, up to 5 characters, and up to 3 style references. These are input/fidelity limits, not a promise that all references will be represented correctly.
- **Use grounding when the image contains time-sensitive or factual content.** Google Search grounding is documented for current facts such as weather, stock charts, and recent events. Image Search grounding is documented only for Gemini 3.1 Flash Image. When Image Search is used, Google says the application must display `search_suggestions`, and the response includes citation and attribution metadata. Web Search results alone do not pass image results into the generation model.

### A working prompt structure

This structure is a working recommendation synthesized from the vendor examples. It is useful for controlled prompting and review, but it has not been benchmarked in this repository:

1. **Intent and deliverable:** what the image is for and what must be legible or recognizable.
2. **Subject inventory:** subjects, object identity, count, pose/action, wardrobe/material, and any reference-image mapping.
3. **Scene and composition:** setting, foreground/background, focal point, placement, negative space, horizon, and reading order.
4. **Style and medium:** photo, illustration, 3D render, poster, diagram, texture, line quality, palette, and surface treatment.
5. **Light and camera:** time of day, direction and softness, contrast, shot type, angle, lens, depth of field, and motion.
6. **Text and layout:** exact strings, language, hierarchy, placement, font character, and what must remain unchanged on an edit.
7. **Output controls:** aspect ratio and `image_size` in the API response format; use uppercase `K` values such as `1K`, `2K`, or `4K`.
8. **Acceptance check:** state what to inspect after generation: identity, count, placement, text, factual claims, safety, rights, and provenance.

For an edit, put the requested delta first or make it unmistakable, identify the source image(s) by role, and state the invariants: “change X; preserve Y, Z, and the original framing.” This is an operational recommendation based on Google’s edit examples, not evidence that unchanged pixels will remain unchanged.

## Generation and API implications

- **Set output geometry explicitly.** The current Interactions API guide says the default follows the input image size or otherwise produces a 1:1 square. Use `response_format` with `type: image`, `aspect_ratio`, and `image_size` when the delivery target matters. The current Flash Image guide documents 14 aspect ratios, including 1:4, 1:8, 4:1, 8:1, 21:9, and common portrait/landscape ratios; Pro documents a smaller set.
- **Choose resolution after composition is acceptable.** Current Gemini 3 image models generate 1K by default. Flash Image also supports 0.5K, 2K, and 4K; Pro supports 1K, 2K, and 4K; Lite supports 1K only. Higher resolution does not repair incorrect content, spelling, or composition, and Google’s token tables show that image-output token cost varies by resolution and aspect ratio.
- **Keep interleaved responses and thought steps separate from the final asset.** The API guide says convenience properties such as `output_image` do not capture every block in complex interleaved responses; clients should iterate through response steps when the workflow needs all text and image blocks. Gemini 3 image models can emit interim thought images; the last image in the thinking sequence is documented as the final rendered image.
- **Use batch only when latency allows.** Google documents Batch API support for image generation with higher rate limits and turnaround of up to 24 hours. Batch is appropriate for a queue of independent variants, not interactive correction loops.
- **Do not assume diffusion-style controls.** In the reviewed current Google primary documentation, seed-based determinism, negative-prompt weighting, CFG scale, and a universal “number of images” control are not documented as stable cross-model controls. The guide explicitly warns that the model will not always follow an exact requested number of image outputs. Treat reproducibility as a recorded workflow, not as a presumed seed replay.
- **Record the exact surface and model.** API, AI Studio, Gemini app, and other Google products can expose different wrappers and defaults. Record provider surface, model ID, date, prompt, reference assets, response format, tools, interaction IDs, and the saved output. Preview IDs in examples should not be silently substituted for stable IDs.

## Limitations and safety

Google’s current model cards and image guide identify limitations that should become release checks:

- small faces, fine details, accurate spelling, small text, long paragraphs, and full-page layouts can fail;
- character consistency is not perfect, even with references;
- masked/doodle edits can partially follow instructions and may leave persistent ink;
- edits can occasionally copy/paste input content unexpectedly, confuse left/right or other spatial localization, or blend multiple inputs into unnatural scenes;
- real-world knowledge, 3D reasoning, and factuality remain limited; the 3.1 image model card lists a January 2025 knowledge cutoff;
- image generation does not support audio inputs, and video inputs are documented only for Gemini 3.1 Flash Image;
- the best-performance language list is finite, so localization quality should be tested rather than inferred from the model’s general language support;
- generated output may be blocked or absent for safety, prohibited content, copyright/recitation, SPII, language, blocklist, or other policy reasons.

Google’s API safety documentation says adjustable filters cover harassment, hate speech, sexually explicit content, and dangerous content, while some core harms such as child safety are always blocked. Filtering is based on probability of unsafe content, not the severity of a possible harm; therefore a low-probability classification is not evidence that a high-severity use case is safe. The API returns prompt feedback and candidate safety ratings, and the image-specific error codes include `image_safety`, `image_prohibited_content`, `image_recitation`, and `image_other`.

For image editing, Google explicitly requires that the caller have the necessary rights to uploaded images and prohibits infringing, deceptive, harassing, or harmful generated content under its policies. Rights to a reference image are separate from consent to depict a recognizable person, permission to modify their likeness, trademark permissions, and permission to publish the derivative. The workflow should record those decisions rather than infer them from a successful API response.

## Provenance and disclosure

Google’s current image-generation guide says all generated images include a SynthID watermark. Google DeepMind describes SynthID as an imperceptible pixel-level watermark designed to remain detectable through common changes such as cropping, filters, color changes, and lossy compression, but its materials also state that it is not foolproof against extreme manipulation. A positive watermark signal is evidence relevant to Google-AI generation; it is not proof of human authorship, legal ownership, factuality, or an unbroken edit history.

The Gemini 3.1 Flash-Lite Image model page additionally lists “SynthID watermarking (Always On) + C2PA.” The generic image-generation guide does not describe C2PA for every model. Therefore, preserve any C2PA manifest that the actual API response or saved file contains, but verify metadata per model and delivery path instead of promising C2PA coverage universally. Keep the original response and a hash of each derivative where provenance matters; metadata may disappear during editing or export.

If Google Search or Image Search grounding is used, retain the returned citations/attribution metadata and satisfy the display requirements. Do not present a grounded graphic as independently verified merely because the model called Search: Google’s own guidance says that factuality still needs checking.

## Evaluation implications

Google’s model cards provide a useful evaluation vocabulary. Gemini 3.1 Flash Image reports human SxS Elo evaluations for general text-to-image, text rendering, visual design, general editing, stylization, character editing, object/environment editing, factuality, infographics, doodle editing, multi-image, and multi-turn work. It also uses expert ratings for subject-focused tasks and an AutoRater for factuality and style diversity. The Pro card similarly separates existing capabilities, new capabilities, and regression sets.

Those vendor results are directional, not a substitute for a local benchmark. They are vendor-run comparisons with selected prompts, configurations, and comparison models. In particular, the 3.1 Flash Image card reports separate columns for a Search-and-thinking configuration and the base model. A fair local comparison must not mix grounded and ungrounded generations or thinking settings without labeling them.

### Recommended local benchmark design

This is a working evaluation plan, not a completed experiment:

- **Freeze the variables.** For each trial, record exact model ID, API surface, date, prompt, reference files and order, aspect ratio, image size, tool configuration, thinking configuration, interaction lineage, and output hash.
- **Use capability slices, not one aesthetic score.** Build small fixtures for text-to-image, text rendering, visual design, general edit, object/environment edit, stylization, character consistency, multi-image composition, multi-turn preservation, factual infographic, and grounded current-information graphics.
- **Score task success separately from preference.** For every fixture, score required-object presence/count, placement, identity fidelity, unchanged-region preservation, text exactness, aspect-ratio compliance, factual accuracy, visual quality, and reviewer preference. A visually attractive image can still fail the task.
- **Test one prompt change at a time.** Compare concise versus detailed briefs, direct versus semantic negatives, one-shot versus multi-turn edits, and ungrounded versus grounded generation while holding assets and output settings constant. Use repeated trials because the vendor documentation does not establish deterministic output.
- **Measure operational behavior.** Record latency, timeout rate, retry rate, output count, blocked-request rate, `no_image` rate, token usage where exposed, and cost by resolution. Lite’s sub-2-second statement is a product target; it must be measured in the actual deployment.
- **Include safety and rights fixtures.** Test benign boundary cases relevant to the product, log prompt and image blocking separately, preserve safety ratings/error codes, and test how the workflow handles consent, recognizable people, private information, trademarks, and user-supplied references. Do not lower safety thresholds solely to increase yield.
- **Check provenance after delivery transformations.** Inspect SynthID where verification is available, retain C2PA when present, and test whether resizing, recompression, screenshots, or editing preserves or removes the available signals. Record “not detected” as uncertainty, not as proof that an image is human-made.
- **Run regression sets on model changes.** Keep representative successful and failed prompts from the intended product. Re-run them when changing model IDs, wrappers, grounding, output resolution, or prompt templates; the model cards’ use of regression sets is a strong reason to keep this set durable.

## Caveats and unresolved questions

- Google’s documentation changed rapidly during the research window. The image-generation guide was last updated 2026-08-26, while model pages were last updated 2026-08-18. Re-check model IDs, availability, pricing, quotas, and deprecation dates before implementation.
- Current Google pages are not perfectly uniform: stable model pages use `gemini-3-pro-image`, while some Gemini 3 guide examples use `gemini-3-pro-image-preview`. Treat the exact model page and live API capability response as authoritative for an implementation.
- Marketing labels such as “state-of-the-art,” “studio-quality,” and “most versatile” are vendor positioning, not independent evidence. The model-card numbers are more concrete but still depend on Google’s prompt sets, raters, comparison models, and configuration.
- No local generation or benchmark run was performed here. The note therefore supplies a grounded research basis and an evaluation design; it does not validate latency, visual quality, safety recall, language parity, or reproducibility for this repository’s eventual product.
- The referenced repository validation standard `docs/standards/research-and-empirical-validation.md` was absent from this worktree. This note follows the available repository rules and records the gap rather than recreating that standard.

