#!/usr/bin/env python3
"""Local Model Prompt Evaluator and Tag Management Pipeline.

Leverages a local LLM (Ollama, LM Studio, llama-server, or local OpenAI-compatible endpoint)
to evaluate user intent, translate natural language into canonical Danbooru tags across the 8 slots,
expand contextual details, and pass the result through the deterministic PromptCompiler.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from tools.compile_prompt import PromptCompiler

DEFAULT_LOCAL_URL = os.environ.get("HARNESS_LOCAL_BASE_URL", "http://127.0.0.1:11434/v1")
DEFAULT_LOCAL_MODEL = os.environ.get("HARNESS_LOCAL_MODEL", "qwen2.5-coder:14b")

SYSTEM_EVALUATION_PROMPT = """You are an expert anime/illustration prompt director and Danbooru tag taxonomist.
Your task is to analyze the user's creative vision, identify all core visual elements, and translate them into precise, canonical Danbooru tags.

Rules:
1. Deconstruct the scene into the 8-Slot Universal Prompt Hierarchy.
2. Convert descriptive phrases into standard booru tags (e.g., "blue twintails" -> "blue_hair, twintails", "school uniform with a tie" -> "school_uniform, necktie").
3. Expand implicit context tags that make the visual scene coherent (e.g. if rainy cyberpunk night: add wet_clothes, puddles, neon_lights, night, reflection).
4. Suggest relevant negative tags to prevent visual artifacts.
5. Return ONLY a valid JSON object with no markdown formatting, backticks, or extra commentary.

Required JSON Structure:
{
  "intent_summary": "1-sentence summary of the creative scene",
  "slots": {
    "2": ["subject_count_tags"],
    "3": ["character_and_franchise_tags"],
    "4": ["hair_eyes_face_anatomy_tags"],
    "5": ["clothing_garments_accessories_tags"],
    "6": ["pose_action_framing_perspective_tags"],
    "7": ["setting_environment_background_tags"],
    "8": ["lighting_camera_optics_atmosphere_tags"]
  },
  "suggested_negatives": ["tag1", "tag2"],
  "refinement_notes": "Explanation of expanded tags or adjustments"
}"""


class LocalPromptEvaluator:
    def __init__(
        self,
        base_url: str = DEFAULT_LOCAL_URL,
        model: str = DEFAULT_LOCAL_MODEL,
        timeout: int = 30,
        compiler: PromptCompiler | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        if not self.base_url.endswith("/v1"):
            self.api_url = f"{self.base_url}/v1/chat/completions"
        else:
            self.api_url = f"{self.base_url}/chat/completions"
        self.model = model
        self.timeout = timeout
        self.compiler = compiler or PromptCompiler()

    def query_local_llm(self, prompt: str) -> dict[str, Any]:
        """Send prompt evaluation request to local OpenAI-compatible endpoint."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_EVALUATION_PROMPT},
                {"role": "user", "content": f"Translate and refine this prompt into Danbooru tags:\n\n{prompt}"},
            ],
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.api_url,
            data=data,
            headers={"Content-Type": "application/json", "Authorization": "Bearer local"},
        )

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            # Clean possible markdown wrapping if returned
            clean_json = re.sub(r"^```(json)?\s*", "", content.strip(), flags=re.MULTILINE)
            clean_json = re.sub(r"\s*```$", "", clean_json.strip(), flags=re.MULTILINE)
            return json.loads(clean_json)

    def heuristic_fallback_refine(self, prompt: str) -> dict[str, Any]:
        """Heuristic rule-based extractor when local LLM server is offline."""
        raw_tokens = [t.strip().lower().replace(" ", "_") for t in re.split(r"[,;.]", prompt) if t.strip()]
        classified_slots: dict[str, list[str]] = {str(i): [] for i in range(2, 9)}

        for tok in raw_tokens:
            slot_id = self.compiler.classify_tag(tok)
            if 2 <= slot_id <= 8:
                classified_slots[str(slot_id)].append(tok)

        # Ensure minimal subject presence
        if not classified_slots["2"]:
            classified_slots["2"].append("1girl")

        return {
            "intent_summary": "Heuristic extraction from natural prompt",
            "slots": classified_slots,
            "suggested_negatives": ["lowres", "bad_anatomy", "worst_quality", "blurry"],
            "refinement_notes": "Local LLM offline. Extracted tags using heuristic taxonomy lookup.",
        }

    def evaluate_and_compile(
        self,
        raw_prompt: str,
        model_dialect: str = "illustrious_xl",
        extra_negative: str | None = None,
        force_heuristic: bool = False,
    ) -> dict[str, Any]:
        """Run the two-phase evaluation pipeline: Local LLM translation -> Deterministic AST compilation."""
        llm_error = None
        eval_result = None

        if not force_heuristic:
            try:
                eval_result = self.query_local_llm(raw_prompt)
            except Exception as e:
                llm_error = str(e)

        if eval_result is None:
            eval_result = self.heuristic_fallback_refine(raw_prompt)

        # Flatten slots into candidate list
        flattened_tags: list[str] = []
        slots_data = eval_result.get("slots", {})
        for slot_num in range(2, 9):
            slot_tags = slots_data.get(str(slot_num), [])
            if isinstance(slot_tags, list):
                flattened_tags.extend(slot_tags)

        # Merge negatives
        suggested_neg = eval_result.get("suggested_negatives", [])
        combined_negative = list(suggested_neg)
        if extra_negative:
            for extra in extra_negative.split(","):
                if extra.strip() and extra.strip() not in combined_negative:
                    combined_negative.append(extra.strip())
        neg_str = ", ".join(combined_negative) if combined_negative else None

        # Pass through the deterministic AST compiler
        compiled = self.compiler.compile(
            raw_prompt=flattened_tags,
            model_dialect=model_dialect,
            extra_negative=neg_str,
        )

        return {
            "original_prompt": raw_prompt,
            "intent_summary": eval_result.get("intent_summary"),
            "refinement_notes": eval_result.get("refinement_notes"),
            "llm_evaluated": llm_error is None and not force_heuristic,
            "llm_warning": f"Local LLM unreachable ({llm_error}); fallback applied" if llm_error else None,
            "compiled": compiled,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="prompt_evaluator",
        description="Evaluate, refine, and compile prompts using local LLM semantic analysis and Danbooru taxonomy.",
    )
    parser.add_argument("--prompt", "-p", required=True, help="Natural language prompt or rough tag list")
    parser.add_argument(
        "--model", "-m",
        default="illustrious_xl",
        choices=["illustrious_xl", "pony_v6_xl", "animagine_xl_v3", "wan_video", "novelai_v3"],
        help="Target diffusion model dialect (default: illustrious_xl)",
    )
    parser.add_argument("--negative", "-n", default=None, help="Additional negative prompt tags")
    parser.add_argument("--local-url", default=DEFAULT_LOCAL_URL, help=f"Local LLM base URL (default: {DEFAULT_LOCAL_URL})")
    parser.add_argument("--llm-model", default=DEFAULT_LOCAL_MODEL, help=f"Local LLM model name (default: {DEFAULT_LOCAL_MODEL})")
    parser.add_argument("--heuristic", action="store_true", help="Force rule-based heuristic extraction without calling local LLM")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args(argv)
    evaluator = LocalPromptEvaluator(base_url=args.local_url, model=args.llm_model)
    res = evaluator.evaluate_and_compile(
        raw_prompt=args.prompt,
        model_dialect=args.model,
        extra_negative=args.negative,
        force_heuristic=args.heuristic,
    )

    if args.json:
        print(json.dumps(res, indent=2))
        return 0

    compiled = res["compiled"]
    print("=== Local LLM Prompt Evaluation & Tag Compilation ===")
    print(f"Original Prompt:  {res['original_prompt']}")
    print(f"Intent Summary:   {res['intent_summary']}")
    print(f"LLM Evaluated:    {res['llm_evaluated']}")
    if res["llm_warning"]:
        print(f"Notice:           {res['llm_warning']}")
    print(f"Target Dialect:   {compiled['model_dialect']} (CLIP Skip: {compiled['clip_skip']})")
    print(f"Tag Count:        {compiled['tag_count']} tags (~{compiled['estimated_clip_tokens']} CLIP tokens)")
    print(f"\nPositive Prompt:\n  {compiled['prompt']}")
    print(f"\nNegative Prompt:\n  {compiled['negative_prompt']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
