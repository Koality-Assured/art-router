---
doc_kind: requirement
canonical_id: artistic-representations
purpose: [requirement, reinforcement]
rank: high
topics: [art, media-production, accessibility, color-management, cultural-respect, safety]
rag_keywords: [painting, illustration, graphic-design, logos, icons, typography, photography, collage, raster, vector, sprites, websites, tattoos, print, packaging, animation, video, projection, CGI, 3D, VFX, audio, haptic, installation, signage, data-visualization, participatory, XR, AR, VR, literary, poetry, performance, theatre, dance, music, sculpture, ceramics, textiles, comics, sequential-art, games, software-art, cartography, geospatial, generative-art, synthetic-media, consent, community-authority, accessibility-evidence, safety-escalation, fixity, preservation, handoff, release-gates]
---

# Artistic representations standard

## How to use this matrix

Choose the row that describes the delivery risk, then add adjacent rows when a work crosses media. Each row requires a context decision, an artistic decision, a technical/accessibility/safety check, and handoff metadata. The gates are production controls, not universal laws of art. The legal and safety notes below are jurisdiction-specific and may require local counsel, a licensed practitioner, an accessibility specialist, an engineer, or an authority having jurisdiction.

## Medium matrix

### Painting and illustration

- **Context:** Original object, reproduction, editorial, education, public display, or screen delivery; record viewing distance and light.
- **Key decisions:** Surface, mark, edge, value, palette, figure/ground, scale, sequence, and whether realism, distortion, or material evidence carries meaning.
- **Gates:** Test the physical and reproduced work in intended light and size; provide a text description when the work conveys information online ([W3C Images Tutorial](https://www.w3.org/WAI/tutorials/images/)); use safe ventilation and material handling for solvents, dusts, and sprays ([OSHA painting hazards](https://www.osha.gov/sites/default/files/2019-04/Chemicals_in_Painting_Materials.pdf)).
- **Handoff:** Master capture, working files, medium and dimensions, pigments/materials, lighting/viewing notes, color profile, alt/long description, rights, provenance, conservation and display limits.

### Graphic design and minimalism

- **Context:** Identity, editorial, campaign, wayfinding, interface, or exhibit; define what the reduction must preserve.
- **Key decisions:** Hierarchy, grid, whitespace, contrast, repetition, omission, reading order, and the point where reduction hides required meaning.
- **Gates:** Verify legibility, reflow, contrast, non-text contrast, and non-color cues against the applicable WCAG 2.2 level ([WCAG 2.2](https://www.w3.org/TR/WCAG22/)); test with real content and target devices.
- **Handoff:** Design tokens or style rules, source layout, type licenses, color values and profiles, breakpoints, language variants, contrast results, alt text, and approved exports.

### Logos, icons, and favicons

- **Context:** Mark, product icon, app icon, favicon, or functional symbol; distinguish brand recognition from a control that needs an accessible name.
- **Key decisions:** Silhouette, mnemonic, negative space, small-size behavior, responsive variants, text inclusion, and separation of word mark from symbol.
- **Gates:** Test at every target size, theme, and background. For U.S. trademark filing, choose standard-character or special-form drawing deliberately; USPTO says standard characters cover wording without limiting font, style, size, or color, while special form covers stylization, design, or color ([USPTO drawing guidance](https://www.uspto.gov/trademarks/basics/mark-drawings-trademarks)). For Apple platforms, follow current icon layers and avoid nonessential text ([Apple HIG: App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)).
- **Handoff:** Symbol/word-mark files, clear space, minimum sizes, monochrome and high-contrast variants, platform manifests, accessible name, trademark search/filing status, license and provenance.

### Typography and color

- **Context:** Reading, labeling, expressive type, brand system, print, screen, HDR, or color-critical archive.
- **Key decisions:** Language/script coverage, hierarchy, measure, rhythm, optical sizing, contrast, color meaning, gamut, and failure mode when color is unavailable.
- **Gates:** Test text alternatives, contrast, zoom/reflow, focus/selection, and color-independent meaning under WCAG 2.2. Carry ICC profiles so device color can be transformed across systems ([ICC color management](https://www.color.org/getting-started/)); use FADGI capture guidance for cultural-heritage digitization ([FADGI at the Library of Congress](https://www.loc.gov/library-of-congress-resources/share-and-distribute/preservation-stewardship/)).
- **Handoff:** Font files and licenses, script coverage, OpenType features, text direction, tokens, contrast pairs, ICC profile, white point/gamma, print ink limits, HDR/SDR intent, and fallback behavior.

### Photography

- **Context:** Documentary, portrait, product, editorial, archive, evidence, or manipulated image; record consent and the relationship to the subject.
- **Key decisions:** Point of view, framing, light, timing, depth, staging, retouching, caption, and whether authenticity is part of the meaning.
- **Gates:** Obtain model/property permissions where required; preserve the original and disclose material edits. For archive or cultural-heritage capture, follow FADGI guidance and color-manage with ICC profiles. Provide an equivalent description for informative web images ([W3C Images Tutorial](https://www.w3.org/WAI/tutorials/images/)).
- **Handoff:** Camera/source file, capture date/place where safe, photographer and subjects, consent restrictions, edit history, IPTC/XMP/C2PA provenance, lens/light notes, crop, color space/profile, caption, alt/long description, and usage rights.

### Collage

- **Context:** Quotation, remix, assemblage, sampling, archival reconstruction, or critique; identify whose images, text, and symbols are present.
- **Key decisions:** Juxtaposition, scale shifts, seams, erasure, citation, transformation, and the power relation created by recontextualization.
- **Gates:** Clear rights and cultural permissions for each source; preserve source inventory and do not imply endorsement. Attach edit history or C2PA provenance when available ([C2PA specification](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html)); use alt/long descriptions that explain meaningful relationships, not just objects.
- **Handoff:** Source ledger, licenses/permissions, attribution, transformation notes, layers, fonts, linked assets, provenance, final raster/vector/PDF, and takedown contact.

### Raster, vector, and sprites

- **Context:** Screen asset, game sprite, print illustration, scalable diagram, texture, or archive master.
- **Key decisions:** Pixel grid, silhouette, anti-aliasing, layers, interpolation, tiling, density, scaling, and whether the source remains editable.
- **Gates:** Export losslessly where required; test nearest/linear filtering, alpha edges, reduced motion, high-contrast and non-color alternatives. For web SVG, expose meaningful text/structure and keyboard behavior where interactive ([W3C SVG](https://www.w3.org/TR/SVG2/)); for information-bearing images, provide an equivalent text description ([WCAG 2.2](https://www.w3.org/TR/WCAG22/)).
- **Handoff:** Source format, dimensions, pixel aspect, density, color space/profile, alpha convention, frame range, pivot/anchor, atlas rules, SVG viewBox/IDs, compression, naming, and alt/accessible name.

### Websites and creative UI

- **Context:** Portfolio, gallery, tool, interactive artwork, game-like experience, or commerce; define task completion and non-visual paths.
- **Key decisions:** Spatial/temporal navigation, interaction grammar, feedback, pacing, sound, motion, and what the interface means as part of the work.
- **Gates:** Meet the applicable WCAG 2.2 level; use semantic HTML and ARIA only where needed, with accessible names and keyboard behavior ([ARIA APG](https://www.w3.org/WAI/ARIA/apg/)). Provide text alternatives for images, captions/transcripts/audio description for media, visible focus, pause/stop controls, reduced-motion behavior, and no seizure-risk flashing. For SVG and animation, test the actual user agent, not only the design file ([W3C SVG](https://www.w3.org/TR/SVG2/), [Web Animations](https://www.w3.org/TR/web-animations-1/), [CSS Easing](https://www.w3.org/TR/css-easing-2/)).
- **Handoff:** URL/build, browser/device matrix, semantic outline, interaction map, accessible names/descriptions, keyboard and reduced-motion tests, media alternatives, performance budget, analytics/privacy notes, source repo, and rollback owner.

### Tattoos and body art

- **Context:** Permanent or temporary body art, placement, visibility, aging, consent, and cultural significance; the wearer controls the body and final consent.
- **Key decisions:** Scale, line weight, skin movement, color, placement, legibility over time, and whether a symbol has restricted or community-held meaning.
- **Gates:** **U.S.-specific safety note:** FDA reports infection and allergic-reaction risks from contaminated ink and unsterile practice, and says tattooing is overseen by state and local authorities ([FDA tattoo safety](https://www.fda.gov/consumers/consumer-updates/think-you-ink-tattoo-safety)). Verify local licensing, sanitation, age/consent, aftercare, ink lot records, and medical escalation with the practitioner; do not promise safety from a design file.
- **Handoff:** Consent record, wearer-approved stencil, placement/scale, ink brand/color/lot, artist and studio license as applicable, cultural consultation, aftercare, contraindications/referral, and a non-body preview.

### Print, merchandise, and packaging

- **Context:** Poster, book, garment, label, package, retail display, or shipped object; define substrate, viewing distance, lifecycle, and claims.
- **Key decisions:** Material, finish, fold/die line, ink/overprint, tactile experience, hierarchy, copy, waste, and unboxing sequence.
- **Gates:** Proof on the actual substrate; confirm bleed, trapping, barcodes, legibility, color profile, and accessibility of any supplied PDF. **U.S.-specific labeling note:** many textile and wool products require fiber content, country of origin, responsible business identity, and care instructions ([FTC apparel labeling](https://www.ftc.gov/news-events/topics/tools-consumers/apparel-labeling)). For federal ICT documents, use Section 508 PDF guidance and test tagged structure, reading order, alternatives, and contrast; PDF/UA-1 remains useful for authoring and assessment, but does not replace the applicable Section 508/WCAG requirements ([Section 508 PDFs](https://www.section508.gov/create/pdfs/), [U.S. Access Board ICT standards](https://www.access-board.gov/ict/)).
- **Handoff:** Press-ready PDF and packaged source, dieline, substrate/finish, inks and profiles, proof approval, copy/legal claims owner, barcode data, label fields, accessibility tags/alt text, quantities, and vendor specifications.

### Animation, video, and projection

- **Context:** Film, motion graphic, live visual, projection, installation loop, or web animation; record audience distance, duration, ambient light, and sound conditions.
- **Key decisions:** Timing, rhythm, loop, camera, transition, motion intensity, silence, synchronization, and what is learned from change over time.
- **Gates:** Provide captions, transcript, audio description or descriptive alternative as the audience and jurisdiction require ([W3C media guidance](https://www.w3.org/WAI/media/av/)). Avoid seizure-risk flashes and provide pause/stop where applicable. Specify SDR/HDR and delivery colorimetry; ITU-R BT.709 and BT.2100 distinguish common SDR and HDR production/exchange conditions ([BT.709](https://www.itu.int/rec/R-REC-BT.709), [BT.2100](https://www.itu.int/rec/R-REC-BT.2100)). For projection, test brightness, heat, rigging, cable paths, and egress with venue professionals.
- **Handoff:** Master/mezzanine/proxy, frame rate, resolution, aspect, timecode, audio layout, captions/VTT, transcript, audio description, color space/transfer, projector/display profile, loop behavior, playback software, venue map, and safety sign-off.

### CGI, 3D, and VFX

- **Context:** Render, game asset, simulation, virtual camera, product visualization, or composited shot; define scale, coordinate system, camera, and interchange target.
- **Key decisions:** Modeling abstraction, material response, lighting, camera, motion, simulation, compositing, and the boundary between observed and invented reality.
- **Gates:** Declare units, axes, frame rate, time sampling, naming, and color pipeline. OpenUSD keeps TimeCodes unitless but provides mapping to real time; its geometry metrics encode stage up-axis and meters-per-unit, so record both project time and spatial interpretation ([OpenUSD time and animated values](https://openusd.org/dev/user_guides/time_and_animated_values.html), [OpenUSD geometry metrics](https://openusd.org/dev/api/usd_geom_2metrics_8h.html)). Use glTF for runtime interchange when appropriate ([Khronos glTF](https://registry.khronos.org/glTF/)); use OpenEXR for high-dynamic-range image exchange and OCIO for declared transforms ([OpenEXR](https://openexr.com/en/latest/TechnicalIntroduction.html), [OpenColorIO documentation](https://opencolorio.readthedocs.io/en/latest/)).
- **Handoff:** USD/glTF scene, caches, textures, materials, camera/lens, units/axes, frame range/rate, timecode, render settings, OCIO config, EXR channels, cryptomatte/depth/motion vectors, dependencies, licenses, and known deviations.

### Audio and haptic work

- **Context:** Music, sound art, voice, interactive audio, vibration, accessible cue, or multisensory installation; identify hearing, touch, and sensory-sensitivity needs.
- **Key decisions:** Timbre, dynamics, silence, spatialization, rhythm, latency, frequency, vibration amplitude, and whether the cue is informational or expressive.
- **Gates:** Provide captions/transcripts or equivalent meaning where audio carries content; control autoplay and background audio; provide visual, textual, or haptic alternatives when needed ([W3C audio/video accessibility](https://www.w3.org/WAI/media/av/)). Test safe sound levels, vibration, latency, device differences, and opt-out paths with venue and accessibility specialists.
- **Handoff:** WAV/stems, sample rate/bit depth, loudness target, channel map, spatial format, cue sheet, transcript/captions, haptic waveform and limits, device mapping, calibration, consent/opt-out, and playback test report.

### Installation, public art, and signage

- **Context:** Site, audience flow, permanence, weather, historic fabric, public safety, and authority over the place; separate temporary intervention from built work.
- **Key decisions:** Scale, sightlines, material/weathering, route, dwell time, sound/light spill, interpretation, and maintenance or removal.
- **Gates:** **U.S.-specific built-environment note:** apply ADA requirements for visual/tactile signs, accessible routes, and communication; consult the authority having jurisdiction and local code ([2010 ADA Standards](https://www.ada.gov/law-and-regs/design-standards/2010-stds/)). OSHA controls apply to hazardous work, rigging, electrical, chemicals, and construction ([OSHA painting hazards](https://www.osha.gov/sites/default/files/2019-04/Chemicals_in_Painting_Materials.pdf)). For historic sites, NPS guidance calls for access modifications that preserve character-defining features and accessible interpretive alternatives ([NPS historic accessibility](https://www.nps.gov/orgs/1739/upload/preservation-brief-32-accessibility.pdf)); GSA facilities standards are relevant to federal facilities ([GSA P-100](https://www.gsa.gov/system/files/2017_Facilities_Standards_%28P100%29%C2%A0.pdf)).
- **Handoff:** Site survey, scaled drawings, accessible route/sign schedule, tactile/Braille and language plan, structural/electrical/egress review, materials and load limits, lighting/sound levels, permits, maintenance, emergency contact, installation/removal method, and public notice.

### Data visualization

- **Context:** Explanation, exploration, public information, evidence, or art; state the data source, population, uncertainty, and decision the viewer may make.
- **Key decisions:** Encoding, ordering, scale, annotation, uncertainty, interaction, color, omission, and whether the work prioritizes comparison, pattern, or emotion.
- **Gates:** Do not make color the only encoding; provide a text or tabular equivalent and a long description for complex charts ([WCAG non-text content](https://www.w3.org/WAI/WCAG22/Understanding/non-text-content), [W3C Images Tutorial](https://www.w3.org/WAI/tutorials/images/)). Preserve source data, transformations, units, date, and caveats; test keyboard, zoom, focus, and screen-reader access.
- **Handoff:** Source dataset and license, query/version, transformations, units, uncertainty, legend, accessible table/description, color profile, SVG/PNG/HTML exports, interaction states, and update owner.

### Participatory and social work

- **Context:** People are contributors, subjects, co-authors, or audience; define decision power, compensation, privacy, risk, and whether participation is voluntary.
- **Key decisions:** Invitation, consent, authorship, facilitation, translation, data capture, refusal, edit power, attribution, and what happens after the event.
- **Gates:** Obtain informed, ongoing consent appropriate to risk; minimize personal data; provide withdrawal and non-participation paths. UNESCO frames living heritage as community-recognized and emphasizes community participation; the 2005 Convention recognizes cultural interaction, civil society, and the role of cultural communities ([UNESCO 2003](https://www.unesco.org/en/legal-affairs/convention-safeguarding-intangible-cultural-heritage), [UNESCO 2005](https://www.unesco.org/en/legal-affairs/convention-protection-and-promotion-diversity-cultural-expressions)). For Indigenous cultural expressions, apply UNDRIP Article 31 and community authority; do not extract, tokenize, or commercialize without an appropriate agreement.
- **Handoff:** Consent/withdrawal log, participant roles and credit choices, compensation, safeguarding plan, language access, data map/retention, community-approved description, permissions, revenue/benefit agreement, and responsible contact.

### XR, AR, and VR

- **Context:** Headset, mobile AR, room-scale, passthrough, or spatial web; define physical boundaries, presence, privacy, duration, and exit.
- **Key decisions:** Spatial anchoring, scale, embodiment, field of view, locomotion, occlusion, interaction, haptics, sound, and what happens when tracking fails.
- **Gates:** Provide seated/standing and non-immersive alternatives where feasible; support clear entry, pause, exit, recentering, captions/transcripts, audio description or spatial descriptions, readable text, and safe boundaries. Follow applicable WCAG practices for non-text and time-based media ([WCAG 2.2](https://www.w3.org/TR/WCAG22/)) and record platform limitations against the W3C WebXR device model ([WebXR Device API](https://www.w3.org/TR/webxr/)). Test motion comfort, photosensitivity, fall/collision risk, privacy permissions, tracking loss, and bystander consent.
- **Handoff:** Platform/device matrix, runtime/build, scene scale and units, anchors/reference space, frame rate, input map, locomotion modes, accessibility alternatives, safety briefing, privacy/data flows, spatial audio/haptics, calibration, and known tracking failures.

## Additional representation families

These rows cover distinct production and preservation risks. Add them to the existing row when a work crosses media.

### Literary, textual, and poetic work

- **Context:** Poetry, prose, script, artist book, text-based installation, or visual treatment of language; identify the canonical words and intended reading conditions.
- **Key decisions:** Lineation, sequence, language and script, translation, typography, spacing, voice, and what meaning depends on layout rather than words.
- **Gates:** Preserve an author-approved plain-text or structured-text master; test reading order, text extraction, direction, and visual-text alternatives. Use WCAG where the delivery is web or ICT, without treating it as a complete measure of literary or visual quality ([WCAG 2.2](https://www.w3.org/TR/WCAG22/)).
- **Handoff:** Text master, rendered presentation, language/direction metadata, translation status, font and license record, version history, and a description of layout-dependent meaning.

### Performance, theatre, and dance

- **Context:** Live or recorded performance; define casting, rehearsal, audience proximity, venue, recording, and reuse conditions.
- **Key decisions:** Embodiment, role and credit, timing, staging, audience interaction, improvisation, warnings, and the emergency or stop procedure.
- **Gates:** Record performer consent and recording/reuse scope; plan venue access, live captions or interpretation where needed, audience communication, and a stop or incident path. For recordings, provide the applicable captions, transcript, audio description, sign language, and accessible-player checks ([W3C media guidance](https://www.w3.org/WAI/media/av/)).
- **Handoff:** Cast and credit record, rehearsal/access plan, cue or score lineage, venue plan, consent and recording restrictions, audience notices, accessibility delivery test, and emergency contact.

### Music, composition, and live sound

- **Context:** Composition, performance, improvisation, recording, sound art, or amplified public event; identify performers, listeners, and exposure conditions.
- **Key decisions:** Score or session lineage, lyrics, timbre, dynamics, silence, spatialization, improvisation, monitoring, and whether a cue is expressive or informational.
- **Gates:** Provide lyrics, spoken-content alternatives, or an equivalent where needed; test playback, monitoring, opt-out, quiet-space, and hearing-protection paths. For amplified public events, apply the relevant local rule and record calibrated monitoring when adopting the WHO venue standard, including its 100 dB LAeq,15 min reference ([WHO global standard for safe listening venues and events](https://www.who.int/publications/i/item/9789240043114)).
- **Handoff:** Score/session lineage, stems or notation, performer and recording permissions, sample rate/bit depth, loudness and dynamic targets, channel map, cue sheet, alternatives, monitoring record, and opt-out contact.

### Sculpture, ceramics, textiles, and material fabrication

- **Context:** Object, wearable, prop, vessel, textile, or fabricated work; define making, handling, display, skin contact, aging, and disposal conditions.
- **Key decisions:** Material behavior, surface, structure, tactility, weight, heat, fragility, maintenance, and whether making evidence remains part of the work.
- **Gates:** Record materials and hazards; set fabrication, handling, load, electrical, ventilation, cleaning, and conservation limits. Obtain the applicable practitioner, engineer, venue, or local-authority review; do not treat a design file as a safety approval.
- **Handoff:** Material and hazard inventory, fabrication and handling limits, structural/electrical review where applicable, tactile-access decision, conservation and maintenance plan, installation instructions, and disposal or removal method.

### Comics, sequential art, storyboards, and illustrated narrative

- **Context:** Panels, pages, captions, speech, sound effects, gutters, scroll sequences, or interactive narrative; identify the canonical sequence.
- **Key decisions:** Panel order, pacing, framing, lettering, localization, omission, alternate reading order, and what is lost when motion or interaction becomes static.
- **Gates:** Test text extraction and meaningful sequence; provide a descriptive transcript or equivalent for information carried by layout, imagery, or sound. For web delivery, test keyboard, focus, reflow, and non-text alternatives against the applicable WCAG level ([WCAG 2.2](https://www.w3.org/TR/WCAG22/)).
- **Handoff:** Source pages and text layers, canonical and alternate sequence, lettering and font licenses, localization constraints, transcript/description, interactive-to-static fallback, and approved exports.

### Games and software-based artworks

- **Context:** Installed game, executable artwork, interactive fiction, simulation, or software-dependent installation; define platform, runtime, network, data, and end-of-life conditions.
- **Key decisions:** Input map, onboarding, game state, save behavior, pacing, failure, privacy, patching, accessibility, and what remains when dependencies disappear.
- **Gates:** Test controller and input alternatives, onboarding and exit, save-state behavior, offline or degraded mode, privacy/data flows, content warnings, and a preservation build or bounded screen-recorded fallback. Treat software and video games as a distinct preservation concern ([Library of Congress Recommended Formats Statement](https://www.loc.gov/preservation/resources/rfs/)).
- **Handoff:** Build and runtime versions, platform/dependency manifest, input and accessibility map, save data, network requirements, source or escrow decision, privacy notes, content warnings, preservation build, and fallback capture.

### Cartographic and geospatial art

- **Context:** Map, spatial data artwork, GIS-based installation, or location-aware experience; define geographic scale, source date, audience, and update owner.
- **Key decisions:** Projection, datum, coordinate reference system, place names, spatial resolution, uncertainty, color, omission, and whether exact locations create risk.
- **Gates:** Preserve source data and transformations; state uncertainty and update date; provide accessible text or tabular equivalents. Review location precision and privacy or safety risk before release, and test the receiving map or render environment ([Library of Congress Recommended Formats Statement](https://www.loc.gov/preservation/resources/rfs/)).
- **Handoff:** Dataset and license, projection/datum/CRS, source date, transformations, spatial precision, uncertainty statement, place-name authority, accessible equivalent, render/export settings, and update or withdrawal owner.

## Workflow overlay: generative and AI-assisted work

Apply this overlay to any medium that uses generation, synthesis, digital replicas, or material manipulation. Record the tool or model and version, input references, prompts or procedures, exposed seeds and settings, human selections and edits, rejected or unsafe branches when retained, public disclosure language, and known reproduction limits. Use provenance mechanisms such as C2PA when the format and toolchain support them; record absence or stripping as a limitation ([NIST AI RMF: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf), [C2PA specifications](https://spec.c2pa.org/specifications/)).

## Cross-cutting release controls

Apply these controls across the matrix and use the evidence/exception record in [`artistic-practice.md`](./artistic-practice.md).

- **People and likeness:** Record participant or likeness permission scope for capture, edit, publication, training, derivatives, archival retention, and withdrawal. Name who can hold, correct, restrict, or request removal; high-risk cases require human review ([NIST AI RMF: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)).
- **Community authority:** For community-held or restricted material, identify decision authority where appropriate, permitted and restricted uses, attribution, benefit, confidentiality, and withdrawal. Carry a community-approved description and restriction contact with the handoff; do not publish protected source details in a public manifest. Hold release when required authority or permission is absent ([UNESCO Ethical Principles for Safeguarding Intangible Cultural Heritage](https://ich.unesco.org/en/ethics-and-ich-00866), [UNDRIP, Article 31](https://www.un.org/development/desa/indigenouspeoples/wp-content/uploads/sites/19/2018/11/UNDRIP_E_web.pdf)).
- **Accessibility evidence:** Identify the information or experience that must be preserved, choose equivalent modes for the audience, ship those assets with the work, and test them in the receiving player or venue. For non-web, live, physical, and immersive work, record the selected equivalent, delivery-condition result, and accepted limitation; do not claim WCAG conformance for a non-web work merely because an alternative exists ([WCAG 2.2](https://www.w3.org/TR/WCAG22/), [W3C media guidance](https://www.w3.org/WAI/media/av/)).
- **Safety escalation:** Screen content, privacy, material, body, sound, venue, and participant risks before release. Record the trigger, named reviewer, mitigation, hold decision, incident contact, and correction or withdrawal path; apply local professional or venue review where the risk requires it.
- **Package integrity and preservation:** Distinguish archival masters from delivery derivatives; include the manifest, source files, accessibility assets, dependencies/runtime notes, preservation intent, and a digest or equivalent fixity record. Re-verify after transfer and record any missing dependency or deviation in the receiving environment. A digest supports integrity checking, not authorship or ownership.

## Universal release gates

Every representation MUST pass the following gates, with exceptions recorded by the accountable owner:

1. Intent, audience, context, meaning, composition, ambiguity, and critique criteria are documented using [`artistic-practice.md`](./artistic-practice.md).
2. Source assets, permissions, licenses, collaborators, cultural consultation, human authorship, tool use, and provenance are recorded; generated or materially manipulated work includes the workflow record and audience-facing disclosure, and C2PA is used when supported.
3. The work is reviewed at delivery scale, duration, distance, device, substrate, venue, or body location, including failure and degraded modes.
4. Accessibility equivalents match the medium: text alternatives, accessible names, captions, transcripts, audio description, tactile/visual alternatives, keyboard/input paths, reduced motion, and non-color cues as applicable. Evidence includes a delivery-condition test for the player, device, venue, or physical work; WCAG 2.2 is a web/ICT conformance standard, not a complete art-quality rubric.
5. Color, time, units, dimensions, frame rate, loudness, spatial coordinates, and export settings are explicit; the handoff opens and renders in the receiving environment, and package fixity is rechecked after transfer.
6. Legal, cultural, health, safety, privacy, and venue requirements are identified by jurisdiction. High-risk cases have a named reviewer and escalation path; U.S. legal/safety references in this document do not establish compliance elsewhere and do not replace local professional review.
7. A second reviewer records pass, hold, or accepted limitation, with owner, version, date, and rollback/withdrawal contact.
