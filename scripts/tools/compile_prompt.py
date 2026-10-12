#!/usr/bin/env python3
"""Danbooru Tag Compiler and Canonical Prompt Optimizer.

Parses, normalizes, deduplicates, and reorders tag-based image prompts into
the canonical 8-slot sequence adhering to docs/standards/prompt-token-ordering.md.
Translates prompts across diffusion model dialects (Illustrious, Pony, Animagine, Wan).

tags: [prompt, danbooru, tags, compiler, ordering, tools]
routing_hints: [prompt, compile, danbooru, tags, dialect]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Default path to catalogs relative to repository root
DEFAULT_CATALOG_DIR = Path(__file__).resolve().parent.parent.parent / "references" / "prompt-engineering" / "catalogs" / "danbooru-tags"

COMMON_ALIASES = {
    "blond_hair": "blonde_hair",
    "twintail": "twintails",
    "ponytails": "ponytail",
    "catgirl": "cat_ears, 1girl",
    "foxgirl": "fox_ears, 1girl",
    "bunnygirl": "bunny_ears, 1girl",
    "schoolgirl": "1girl, school_uniform",
    "megane": "glasses",
    "maid_uniform": "maid",
    "striped_panties": "striped_panties, panties",
    "very_long_hair": "very_long_hair, long_hair",
    "cowboy_pose": "cowboy_shot",
}


def load_dialects(catalog_dir: Path | None = None) -> dict[str, Any]:
    cat_dir = catalog_dir or DEFAULT_CATALOG_DIR
    dialect_file = cat_dir / "model-dialects.json"
    if dialect_file.exists():
        try:
            with open(dialect_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("dialects", {})
        except Exception:
            pass
    return {}


def load_tag_groups(catalog_dir: Path | None = None) -> list[dict[str, Any]]:
    cat_dir = catalog_dir or DEFAULT_CATALOG_DIR
    groups_file = cat_dir / "tag-groups.json"
    if groups_file.exists():
        try:
            with open(groups_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("groups", [])
        except Exception:
            pass
    return []


def normalize_tag(tag: str) -> str:
    """Normalize raw user tag string into canonical booru format."""
    cleaned = tag.strip().lower()
    # Normalize internal spaces to underscores unless it's a specific weighting bracket
    cleaned = re.sub(r"\s+", "_", cleaned)
    # Strip trailing commas or colons
    cleaned = cleaned.strip(",:;").strip()
    return cleaned


class PromptCompiler:
    def __init__(self, catalog_dir: Path | None = None) -> None:
        self.catalog_dir = catalog_dir or DEFAULT_CATALOG_DIR
        self.dialects = load_dialects(self.catalog_dir)
        self.groups = load_tag_groups(self.catalog_dir)
        self._build_lookup_maps()

    def _build_lookup_maps(self) -> None:
        self.tag_to_slot: dict[str, int] = {}
        for g in self.groups:
            slot = g.get("canonical_slot", 6)
            for sample in g.get("sample_tags", []):
                self.tag_to_slot[sample] = slot

    def classify_tag(self, tag: str) -> int:
        """Classify a tag into one of the 8 canonical slots."""
        norm = normalize_tag(tag)
        if norm in self.tag_to_slot:
            return self.tag_to_slot[norm]

        # Slot 1: Quality / Steering tokens
        if norm.startswith("score_") or norm in (
            "masterpiece", "best_quality", "very_aesthetic", "high_score",
            "great_score", "absurdres", "superabsurdres", "highres", "cinematic"
        ):
            return 1

        # Slot 2: Character counts / Presence
        if norm in ("solo", "1girl", "2girls", "3girls", "4girls", "multiple_girls",
                    "1boy", "2boys", "multiple_boys", "1other", "no_humans"):
            return 2
        if re.match(r"^\d+(girls?|boys?)$", norm):
            return 2

        # Slot 3: Character names and series (often contains parentheses or specific naming)
        if "_(" in norm or norm.endswith("_(series)") or norm in ("vocaloid", "genshin_impact", "hololive", "touhou"):
            return 3

        # Slot 4: Anatomy, Hair, Eyes, Face
        if any(norm.endswith(sfx) for sfx in ("_hair", "_eyes", "_skin", "_ears", "_tail", "_wings")):
            return 4
        if norm in ("smile", "open_mouth", "closed_eyes", "blush", "parted_lips", "fangs", "expressionless", "navel", "collarbone", "abs"):
            return 4

        # Slot 5: Attire & Accessories
        if any(norm.endswith(sfx) for sfx in ("_uniform", "_dress", "_shirt", "_skirt", "_socks", "_boots", "_shoes", "_ribbon", "_hat", "_glasses", "_gloves", "_sleeves")):
            return 5
        if norm in ("bikini", "swimsuit", "maid", "kimono", "hoodie", "jacket", "choker", "necktie", "bowtie", "hairclip", "headband", "halo"):
            return 5

        # Slot 6: Pose, Action, Framing, Perspective
        if any(norm.endswith(sfx) for sfx in ("_shot", "_view", "_angle", "_focus")):
            return 6
        if norm.startswith("holding_") or norm in ("standing", "sitting", "lying", "kneeling", "leaning", "walking", "running", "peace_sign", "from_above", "from_below", "from_side", "profile"):
            return 6

        # Slot 7: Environment & Background
        if any(norm.endswith(sfx) for sfx in ("_background", "_room", "_sky", "_street")):
            return 7
        if norm in ("indoors", "outdoors", "classroom", "bedroom", "city", "forest", "beach", "ocean", "window", "desk", "chair"):
            return 7

        # Slot 8: Lighting, Camera Optics, Atmosphere
        if any(norm.endswith(sfx) for sfx in ("_lighting", "_light", "_shadow", "_flare")):
            return 8
        if norm in ("sunlight", "moonlight", "depth_of_field", "blurry_background", "bokeh", "sparkles", "glowing", "dappled_sunlight"):
            return 8

        # Fallback default to Slot 6 (Action/Context descriptor)
        return 6

    def compile(
        self,
        raw_prompt: str | list[str],
        model_dialect: str = "illustrious_xl",
        extra_negative: str | None = None,
    ) -> dict[str, Any]:
        """Compile and reorder raw tags into canonical slot structure adhering to target model dialect."""
        dialect_spec = self.dialects.get(model_dialect, {})
        strip_tokens = set(dialect_spec.get("strip_tokens", []))
        quality_tokens = list(dialect_spec.get("quality_tokens", []))
        quality_position = dialect_spec.get("quality_anchor_position", "head")
        source_token = dialect_spec.get("source_token_default")
        rating_token = dialect_spec.get("rating_token_default")

        # Parse tags
        if isinstance(raw_prompt, str):
            raw_items = [raw_prompt]
        else:
            raw_items = [str(t) for t in raw_prompt]
        token_candidates: list[str] = []
        for item in raw_items:
            token_candidates.extend([t.strip() for t in re.split(r"[,，]", item) if t.strip()])

        # Resolve aliases and normalize
        normalized_tags: list[str] = []
        for t in token_candidates:
            n = normalize_tag(t)
            if not n:
                continue
            if n in COMMON_ALIASES:
                aliased = [normalize_tag(a) for a in re.split(r"[,，]", COMMON_ALIASES[n]) if a.strip()]
                normalized_tags.extend(aliased)
            else:
                normalized_tags.append(n)

        # Filter out stripped tokens
        filtered_tags: list[str] = []
        for t in normalized_tags:
            if t in strip_tokens:
                continue
            if not dialect_spec.get("artist_support", True) and (t.startswith("by_") or t.startswith("artist:")):
                continue
            filtered_tags.append(t)

        # Categorize into slots
        slots: dict[int, list[str]] = {i: [] for i in range(1, 9)}
        seen: set[str] = set()

        for t in filtered_tags:
            if t in seen:
                continue
            slot_id = self.classify_tag(t)
            slots[slot_id].append(t)
            seen.add(t)

        # Inject dialect-specific anchors into Slot 1
        if quality_position == "head" and quality_tokens:
            head_additions = []
            for q in quality_tokens:
                qn = normalize_tag(q)
                if qn not in seen:
                    head_additions.append(qn)
                    seen.add(qn)
            if source_token:
                stn = normalize_tag(source_token)
                if stn not in seen:
                    head_additions.append(stn)
                    seen.add(stn)
            if rating_token:
                rtn = normalize_tag(rating_token)
                if rtn not in seen:
                    head_additions.append(rtn)
                    seen.add(rtn)
            slots[1] = head_additions + slots[1]

        # Assemble final tag sequence per dialect slot ordering
        ordered_tags: list[str] = []
        slot_order = dialect_spec.get("slot_order", [1, 2, 3, 4, 5, 6, 7, 8])

        for s in slot_order:
            if s == 1 and quality_position == "tail":
                # Animagine style tail placement
                continue
            ordered_tags.extend(slots.get(s, []))

        if quality_position == "tail" and quality_tokens:
            for q in quality_tokens:
                qn = normalize_tag(q)
                if qn not in ordered_tags:
                    ordered_tags.append(qn)

        final_prompt = ", ".join(ordered_tags)

        # Compile negative prompt
        dialect_negatives = list(dialect_spec.get("negative_tokens", []))
        if extra_negative:
            extra_list = [normalize_tag(e) for e in re.split(r"[,，]", extra_negative) if e.strip()]
            normalized_dialect_set = {normalize_tag(d) for d in dialect_negatives}
            for e in extra_list:
                if e not in normalized_dialect_set:
                    dialect_negatives.append(e)
                    normalized_dialect_set.add(e)
        final_negative = ", ".join(dialect_negatives)

        # Estimated CLIP token budget (rough heuristic: 1 tag ≈ 1.25 tokens)
        estimated_tokens = int(len(ordered_tags) * 1.25)
        warnings = []
        if estimated_tokens > 75:
            warnings.append(
                f"Estimated CLIP tokens ({estimated_tokens}) exceeds single 75-token chunk boundary. "
                "Context splitting across chunks may reduce prompt cross-attention coherence."
            )

        return {
            "prompt": final_prompt,
            "negative_prompt": final_negative,
            "model_dialect": model_dialect,
            "clip_skip": dialect_spec.get("clip_skip", 1),
            "tag_count": len(ordered_tags),
            "estimated_clip_tokens": estimated_tokens,
            "slots": {str(k): v for k, v in slots.items() if v},
            "warnings": warnings,
        }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        prog="compile_prompt",
        description="Compile and reorder Danbooru tag prompts into the 8-slot canonical sequence.",
    )
    parser.add_argument("--prompt", "-p", required=True, help="Input prompt tags (comma-separated)")
    parser.add_argument(
        "--model", "-m",
        default="illustrious_xl",
        choices=["illustrious_xl", "pony_v6_xl", "animagine_xl_v3", "wan_video", "novelai_v3"],
        help="Target diffusion model dialect (default: illustrious_xl)",
    )
    parser.add_argument("--negative", "-n", default=None, help="Additional negative prompt tags")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--catalogs-dir", default=None, help="Path to danbooru-tags catalogs directory")

    args = parser.parse_args(argv)
    cat_dir = Path(args.catalogs_dir) if args.catalogs_dir else None
    compiler = PromptCompiler(catalog_dir=cat_dir)
    res = compiler.compile(args.prompt, model_dialect=args.model, extra_negative=args.negative)

    if args.json:
        print(json.dumps(res, indent=2))
        return 0

    print("=== Compiled Danbooru Tag Prompt ===")
    print(f"Model Dialect:  {res['model_dialect']} (CLIP Skip: {res['clip_skip']})")
    print(f"Tag Count:      {res['tag_count']} tags (~{res['estimated_clip_tokens']} CLIP tokens)")
    print(f"\nPositive Prompt:\n  {res['prompt']}")
    print(f"\nNegative Prompt:\n  {res['negative_prompt']}")
    if res["warnings"]:
        print("\nWarnings:")
        for w in res["warnings"]:
            print(f"  [!] {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
