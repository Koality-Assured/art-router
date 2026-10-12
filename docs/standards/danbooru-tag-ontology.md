---
doc_kind: requirement
canonical_id: danbooru-tag-ontology
purpose: [requirement, reinforcement]
rank: high
topics: [generative-ai, prompt-engineering, danbooru, tag-groups, ontology, diffusion-models]
rag_keywords: [danbooru, tag-groups, tag-categories, general, artist, copyright, character, meta, wiki-pages, implications, aliases, anime-diffusion, novelai, animagine, pony, illustrious, wd14-tagger]
---

# Danbooru Tag Ontology and Classification Standard

## Scope and Authority

This standard defines the ontological structure, category schemas, functional tag groups, and relationship semantics of the Danbooru tagging system for generative AI pipelines within the `art-router` domain harness.

Danbooru tags constitute the primary latent semantic vocabulary and conditioning feature space for stylised illustration, anime, and hybrid visual diffusion models (including NovelAI, Animagine XL, Pony Diffusion, Illustrious XL, Waifu Diffusion, and WD14 vision taggers). This standard establishes the authoritative repository taxonomy for ingesting, parsing, validating, and structuring tag-based prompt contracts.

---

## 1. Native Database Categories

Every tag in the Danbooru database schema belongs to exactly one of five discrete category IDs:

| Category ID | Category Name | Prefix | Visual Role | Training Function | Example Tags |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`0`** | **General** | `gen:` | Visual descriptors (objects, clothing, anatomy, posture, actions, settings) | Primary subject and attribute conditioning (>90% of corpus) | `1girl`, `blue_eyes`, `twintails`, `school_uniform`, `smile` |
| **`1`** | **Artist** | `art:` | Illustrators, animators, circle creators | Stylistic conditioning, rendering brushwork, line weight | `kantoku`, `mika_pikazo`, `shiratamamaru` |
| **`3`** | **Copyright** | `copy:` | Intellectual property, franchise, game, or anime series | World-state, design language, costume consistency | `genshin_impact`, `vocaloid`, `hololive`, `fate_(series)` |
| **`4`** | **Character** | `char:` | Specific fictional entities or individual depictions | Canonical character appearance, hair/eye geometry | `hatsune_miku`, `raiden_shogun`, `frieren` |
| **`5`** | **Meta** | `meta:` | Technical metadata, resolution tiers, workflow states | Quality anchoring, image framing, text indicators | `highres`, `absurdres`, `bad_id`, `translated` |

*(Note: Category ID `2` is a retired booru legacy ID and is reserved/unused in modern Danbooru schemas).*

---

## 2. Functional Tag Groups (`tag_group:*`)

While database category IDs segment tags by administrative type, community curation organizes tags into over 110 structured **Tag Groups** (`tag_group:*`) cataloged on `wiki_pages/tag_groups`.

### 2.1 Core Ontological Branches

```
Danbooru Tag Ontology
├── Visual Characteristics
│   ├── Image Composition & Perspective (tag_group:image_composition, tag_group:focus_tags)
│   ├── Character Counters (tag_group:character_count)
│   ├── Lighting & Atmosphere (tag_group:lighting, tag_group:colors)
│   ├── Anatomy & Physical Features (tag_group:body_parts, tag_group:face_tags, tag_group:hair)
│   ├── Posture & Gestures (tag_group:posture, tag_group:gestures)
│   ├── Attire & Accessories (tag_group:attire, tag_group:headwear, tag_group:accessories)
│   ├── Objects & Gear (tag_group:holding_tags, list_of_weapons, tag_group:technology)
│   ├── Environment & Setting (tag_group:backgrounds, tag_group:locations)
│   └── Aesthetics & Artistic Modification (tag_group:visual_aesthetic, tag_group:censorship)
├── Copyrights & Character Taxonomies
│   ├── Franchise Catalogs (60+ dedicated franchise wiki indexes)
│   └── Genre Categories (tag_group:role-playing_games, tag_group:visual_novel_games)
└── Metatags & Production Tooling
    ├── Mathematical Resolution Thresholds (highres, absurdres, superabsurdres)
    └── Software Attribution (tag_group:drawing_software)
```

### 2.2 Mathematical Resolution Metatags

Danbooru automatically computes and applies resolution metatags based on pixel area:
- `highres`: Pixel area $\ge 1,600 \times 1,200\text{ px}$ ($\ge 1.92\text{ Megapixels}$).
- `absurdres`: Longest edge $\ge 3,200\text{ px}$ or total area $\ge 10.24\text{ Megapixels}$.
- `superabsurdres`: Dimensions exceeding $6,000 \times 6,000\text{ px}$.

Diffusion models trained on Danbooru associate these tokens with sharp high-frequency details, clean linework, and high compositional complexity.

---

## 3. Relational Semantics: DAGs & Aliases

The repository compiler MUST respect Danbooru's relational directed acyclic graphs:

1. **Tag Implications (`/tag_implications.json`):**
   - Implication rule: `antecedent` $\implies$ `consequent`.
   - Examples: `blue_hair` $\implies$ `hair`, `holding_sword` $\implies$ `holding_weapon`, `cat_ears` $\implies$ `animal_ears`.
   - *Optimization Rule:* To respect the 75-token CLIP boundary, redundant parent tags SHOULD be pruned when the specific child tag is already asserted.

2. **Tag Aliases (`/tag_aliases.json`):**
   - Canonical equivalence mapping: `alias` $\to$ `canonical_tag`.
   - Examples: `blond_hair` $\to$ `blonde_hair`, `twintail` $\to$ `twintails`, `catgirl` $\to$ `cat_ears`.
   - *Normalization Rule:* All input prompts MUST be resolved to their canonical tag variant before slot compilation.

---

## 4. REST API Integration Protocol

When live querying or synchronizing tag definitions from Danbooru:
- **Base Endpoint:** `https://danbooru.donmai.us`
- **Tag Search:** `GET /tags.json?search[name_matches]=<query>&search[category]=<cat>&limit=100`
- **Wiki Page Search:** `GET /wiki_pages.json?search[title_normalize]=tag_group:*&limit=100`
- **Post Tags:** `GET /posts.json?tags=<query>&limit=20`
- **Rate Limit Compliance:** Anonymous requests MUST NOT exceed 1 query per second. Caching in `references/prompt-engineering/catalogs/danbooru-tags/` MUST be prioritized over runtime API queries.
