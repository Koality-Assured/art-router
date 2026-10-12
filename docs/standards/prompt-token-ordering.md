---
doc_kind: requirement
canonical_id: prompt-token-ordering
purpose: [requirement, reinforcement]
rank: high
topics: [generative-ai, prompt-engineering, token-ordering, clip-tokenizer, diffusion-conditioning, animagine, pony, illustrious]
rag_keywords: [prompt-ordering, canonical-slots, clip-attention, token-decay, 75-token-limit, animagine-xl, pony-diffusion, illustrious-xl, wan-video, negative-prompting]
---

# Canonical Prompt Token Ordering and Slot Architecture Standard

## Scope and Authority

This standard defines the universal 8-slot structural ordering, token decay dynamics, and cross-model dialect translation specifications for tag-conditioned visual diffusion models in `art-router`.

Diffusion text encoders (CLIP ViT-L/14, OpenCLIP ViT-bigG/14, UMT5) apply causal positional embeddings across fixed sequence lengths. Tokens positioned near the start of the sequence receive higher attention weights than trailing tokens. Unstructured tag lists lead to attribute bleeding, subject loss, and degraded composition. This standard establishes a deterministic, mathematically grounded sequence architecture.

---

## 1. The Universal 8-Slot Hierarchy

Every compiled tag prompt MUST be organized into the following 8-slot hierarchy:

```
[Slot 1: Quality / Steering Prefix]
  └── [Slot 2: Subject & Count Anchor]
        └── [Slot 3: Character Identity & Source IP]
              └── [Slot 4: Core Anatomy, Hair & Face]
                    └── [Slot 5: Attire, Garments & Accessories]
                          └── [Slot 6: Pose, Action, Framing & Perspective]
                                └── [Slot 7: Environment, Setting & Background]
                                      └── [Slot 8: Lighting, Camera Optics & Atmosphere (or Tail Quality)]
```

### Detailed Slot Definitions

| Slot ID | Slot Purpose | Danbooru Tag Groups | Representative Tokens |
| :--- | :--- | :--- | :--- |
| **Slot 1** | **Quality / Steering Prefix** | Model-specific steering presets | *Illustrious:* `masterpiece, best_quality, absurdres`<br>*Pony:* `score_9, score_8_up, score_7_up, rating_safe, source_anime` |
| **Slot 2** | **Subject & Count Anchor** | `tag_group:character_count` | `solo, 1girl`, `1boy, 1girl`, `2girls`, `no_humans` |
| **Slot 3** | **Character & Franchise** | Character (`4`), Copyright (`3`) | `hatsune_miku, vocaloid`, `frieren, sousou_no_frieren` |
| **Slot 4** | **Anatomy, Hair & Face** | `tag_group:body_parts`, `tag_group:face_tags`, `tag_group:hair`, `tag_group:eyes_tags` | `long_hair, twintails, blue_hair, blue_eyes, smile, blush, looking_at_viewer` |
| **Slot 5** | **Attire & Accessories** | `tag_group:attire`, `tag_group:headwear`, `tag_group:legwear`, `tag_group:accessories` | `school_uniform, pleated_skirt, thighhighs, necktie, hair_ribbon, headphones` |
| **Slot 6** | **Pose, Action & Framing** | `tag_group:image_composition`, `tag_group:posture`, `tag_group:gestures`, `tag_group:focus_tags` | `cowboy_shot, standing, peace_sign, from_side, dynamic_angle, holding_book` |
| **Slot 7** | **Environment & Setting** | `tag_group:backgrounds`, `tag_group:locations`, `tag_group:objects` | `indoors, classroom, window, sunlight, desk, detailed_background` |
| **Slot 8** | **Lighting, Optics & Atmosphere** | `tag_group:lighting`, `tag_group:visual_aesthetic`, Model Tail Quality | `cinematic_lighting, volumetric_lighting, lens_flare, depth_of_field`<br>*Animagine:* `masterpiece, high score, great score` |

---

## 2. Model Dialect Translation Matrix

Different model families enforce conflicting conventions regarding where quality tokens belong, whether artist tags are permitted, and what negative prompts are required:

| Feature / Control | Animagine XL Profile | Pony Diffusion V6 Profile | Illustrious XL Profile | Wan 2.1 / 2.2 / SDXL Profile |
| :--- | :--- | :--- | :--- | :--- |
| **Quality Placement** | **Tail (Slot 8)** | **Head (Slot 1)** | **Head (Slot 1)** | Head or Distributed |
| **Quality Tokens** | `masterpiece, high score, great score, absurdres` | `score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up` | `masterpiece, best_quality, very_aesthetic, absurdres` | Natural language or standard booru tags |
| **Source / Rating Tokens** | Not required | `source_anime, rating_safe` | Not required | Not required |
| **Artist Tag Support** | Supported (`by artist_name`) | **REJECTED / STRIPPED** (Pony strips artist tags) | Supported (`artist_name` or `by artist`) | Supported |
| **Standard Tags Strip** | None | Strips `masterpiece, best quality, absurdres` | Strips `score_9, score_8_up` | Strips score tokens |
| **Recommended CLIP Skip** | 1 | **2** (Strict requirement) | 1 | 1 |
| **Default Negative Bundle** | `lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name` | `score_6, score_5, score_4, rating_explicit, bad anatomy` | `lowres, worst_quality, low_quality, bad_anatomy, bad_hands, text, error` | Generic quality & deformation terms |

---

## 3. CLIP Chunking and Token Budget Limits

1. **The 75-Token Boundary:** Standard CLIP text encoders accept 77 tokens total (Token 0 is `<|startoftext|>`, Token 76 is `<|endoftext|>`), leaving a payload budget of **75 word tokens**.
2. **Chunk Splitting Degradation:** When a prompt exceeds 75 tokens, ComfyUI / A1111 splits it into separate chunks. Cross-attention context between Chunk 1 (e.g. subject) and Chunk 2 (e.g. setting) is attenuated unless specifically bridged.
3. **Budget Warning Thresholds:**
   - $\le 60\text{ tokens}$: **Optimal** (full attention bandwidth available).
   - $61\text{--}75\text{ tokens}$: **Bounded** (acceptable, approaching single-chunk limit).
   - $> 75\text{ tokens}$: **Warning** (triggers automatic multi-chunk splitting; compiler MUST warn operator).
