---
doc_kind: research_result
canonical_id: art-router-results-2026-08-27
purpose: [research, validation, handoff]
status: fixture-validation-with-holds
date: 2026-08-27
topics: [art, representation, accessibility, provenance, delivery, fixity]
---

# Art-router representation fixture handoff

This package exercises the seven cases named in `research/art-router/representation-gaps.md`. The machine-readable manifest is [`manifest.json`](./manifest.json); the per-file SHA-256 record is [`SHA256SUMS.txt`](./SHA256SUMS.txt); the validator output is [`validation-report.json`](./validation-report.json).

## Case matrix

| Case | Package asset | Standards exercised | Observable failure or limitation | Coordinator review | Next change |
| --- | --- | --- | --- | --- | --- |
| Illustration | [`assets/illustration-community-garden.png`](./assets/illustration-community-garden.png) | WCAG 2.2 non-text alternative; NIST Generative AI Profile provenance fields; C2PA provenance gap | Bitmap is 1254×1254 and visually legible, but rights status and exact generation parameters are unresolved. | Visual spot check: hold release for provenance/rights review. | Retain provider/model/seed record and complete rights review; test the delivered responsive derivative. |
| Mark / favicon | [`fixtures/mark/mark.svg`](./fixtures/mark/mark.svg), [`fixtures/mark/favicon-16.svg`](./fixtures/mark/favicon-16.svg), [`fixtures/mark/favicon-32.svg`](./fixtures/mark/favicon-32.svg), [`fixtures/mark/favicon-48.svg`](./fixtures/mark/favicon-48.svg), [`fixtures/mark/favicon-monochrome.svg`](./fixtures/mark/favicon-monochrome.svg) | WCAG 2.2 contrast and non-color meaning; small-size delivery checks | SVG exports cover 16/32/48 px and monochrome; binary PNG/ICO derivatives are not included. | Source/visual review: approve fixture inclusion. | Generate binary favicon derivatives and verify them in receiving browsers and OS launchers. |
| Still-life image | [`assets/photo-still-life.png`](./assets/photo-still-life.png) | IPTC-style creator/rights separation; WCAG 2.2 equivalent description; NIST provenance | Supplied bitmap is 1535×1024, below the validator’s 2000×1500 photography threshold; no camera capture record exists; rights status is unresolved. | Visual spot check: hold release for provenance and delivery-size decision. | Produce or accept a larger delivery master, record synthetic disclosure, and complete rights review. |
| Body art | [`assets/tattoo-botanical-sprig.png`](./assets/tattoo-botanical-sprig.png) | Consent scope and body-art safety controls; non-body review path; cultural-context check | Generated reference has no wearer consent or rights record. Declared sanitation, licensing, and aging fields do not establish studio safety. | Visual spot check: hold release pending wearer/rights record. | Add wearer-approved placement record, licensed-practitioner review, sanitation/ink records, and aftercare handoff. |
| Artistic web / canvas | [`fixtures/site/index.html`](./fixtures/site/index.html) | WCAG 2.2 keyboard access, focus visibility, reduced motion, contrast, non-color meaning, and fallback | Source contains the controls and fallback; no real browser/assistive-technology compatibility pass is claimed. | Source review: approve fixture inclusion. | Run keyboard, screen-reader, zoom, narrow viewport, and reduced-motion checks in target browsers. |
| Captioned animation | [`fixtures/animation/animation.html`](./fixtures/animation/animation.html), [`fixtures/animation/captions.vtt`](./fixtures/animation/captions.vtt), [`fixtures/animation/delivery-metadata.json`](./fixtures/animation/delivery-metadata.json) | WCAG 2.2 captions, transcript, pause/stop; W3C media accessibility guidance; flash-rate and colorimetry fields | Code-native animated SVG is not an MP4/WebM encode; timed-caption synchronization and user-agent coverage are untested. | Source review: approve fixture inclusion. | Render and test a real delivery encode with selectable captions, pause behavior, and reduced-motion fallback. |
| CGI-style render | [`assets/cgi-stones.png`](./assets/cgi-stones.png) | Library of Congress format distinction; NIST provenance; scene/camera/render handoff fields | Only a 1254×1254 bitmap exists. The manifest exercises target USD/scene fields but does not claim a USD source package; rights status is unresolved. | Visual spot check: hold release for provenance and source-scene handoff. | Package the source scene, dependencies, camera, units, render settings, and rights record; re-open it in the receiving environment. |

## Provenance and fixity

The four bitmap inputs were supplied as real built-in image-generation outputs already present in the worktree. Prompt summaries, the declared unknown rights status, and the missing exact-provider/model/seed limitation are recorded per case in [`manifest.json`](./manifest.json). In brief: the illustration prompt describes a square dusk community garden with raised beds and a blue-and-ochre painterly palette; the still-life prompt describes a ceramic bowl, linen, leafy branch, and warm window light; the body-art prompt describes a black botanical sprig with three leaves and no lettering; the CGI prompt describes three translucent blue/amber stones on a round plinth with controlled studio light.

The package is fixed by SHA-256 entries in [`SHA256SUMS.txt`](./SHA256SUMS.txt). Recompute each listed path from this directory and compare the uppercase digest. The four supplied bitmap paths are exact and remain under `assets/`; no scratch or user-home path is required to open the package.

## Validation scope and non-claims

Run from the repository root:

```text
python scripts/validation/validate_art_router.py --manifest results/research/art-router/2026-08-27/manifest.json --json --fail-on-hold
```

The validator checks declared controls and supplied measurements only. It does not open asset paths, inspect pixels, recreate generation, or prove that any delivery exists. The expected result for this package is a hold because generated bitmap rights are unresolved and the supplied still-life dimensions are below the photography criterion; those failures are intentional and documented above.

Declared controls are not proof of artistic quality, rights, safety, accessibility, or user-agent compatibility. The package does not make those claims, does not establish legal authorship or ownership, and does not turn a fixture field into a production approval.
