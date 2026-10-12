"""Unit tests for Local Model Prompt Evaluator and Tag Management (prompt_evaluator.py).

tags: [tests, prompt, evaluator, local-llm]
routing_hints: [tests, prompt_evaluator, local-llm]
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from tools.prompt_evaluator import LocalPromptEvaluator


MOCK_LLM_RESPONSE = {
    "intent_summary": "A cyberpunk anime heroine standing in rainy neon streets",
    "slots": {
        "2": ["1girl", "solo"],
        "3": [],
        "4": ["blue_hair", "twintails", "cyan_eyes", "smile"],
        "5": ["cyberpunk_jacket", "pleated_skirt", "thighhighs"],
        "6": ["standing", "from_side", "peace_sign"],
        "7": ["cyberpunk_city", "rain", "wet_street", "neon_lights"],
        "8": ["volumetric_lighting", "lens_flare", "depth_of_field"],
    },
    "suggested_negatives": ["umbrella", "car"],
    "refinement_notes": "Added cyberpunk atmosphere and rain reflection tags.",
}


class TestPromptEvaluator(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluator = LocalPromptEvaluator()

    def test_evaluate_and_compile_with_mock_llm(self) -> None:
        with patch.object(self.evaluator, "query_local_llm", return_value=MOCK_LLM_RESPONSE):
            res = self.evaluator.evaluate_and_compile(
                raw_prompt="anime girl cyberpunk in rain",
                model_dialect="illustrious_xl",
            )

            self.assertTrue(res["llm_evaluated"])
            self.assertIsNone(res["llm_warning"])
            self.assertEqual(res["intent_summary"], "A cyberpunk anime heroine standing in rainy neon streets")

            compiled = res["compiled"]
            prompt = compiled["prompt"]

            # Quality tokens should be at the head for Illustrious
            self.assertTrue(prompt.startswith("masterpiece, best_quality"))
            # Subject anchor
            self.assertIn("1girl", prompt)
            # Hair/face
            self.assertIn("blue_hair", prompt)
            self.assertIn("twintails", prompt)
            # Negative tags merged
            self.assertIn("umbrella", compiled["negative_prompt"])

    def test_evaluate_and_compile_pony_dialect(self) -> None:
        with patch.object(self.evaluator, "query_local_llm", return_value=MOCK_LLM_RESPONSE):
            res = self.evaluator.evaluate_and_compile(
                raw_prompt="anime girl cyberpunk in rain",
                model_dialect="pony_v6_xl",
            )

            compiled = res["compiled"]
            self.assertEqual(compiled["clip_skip"], 2)
            # Must have score tokens and no masterpiece
            self.assertIn("score_9", compiled["prompt"])
            self.assertNotIn("masterpiece", compiled["prompt"])

    def test_fallback_when_llm_fails(self) -> None:
        with patch.object(self.evaluator, "query_local_llm", side_effect=ConnectionRefusedError("Connection refused")):
            res = self.evaluator.evaluate_and_compile(
                raw_prompt="1girl, blue_hair, standing, classroom",
                model_dialect="illustrious_xl",
            )

            self.assertFalse(res["llm_evaluated"])
            self.assertIsNotNone(res["llm_warning"])
            self.assertIn("Local LLM unreachable", res["llm_warning"])

            compiled = res["compiled"]
            self.assertIn("1girl", compiled["prompt"])
            self.assertIn("blue_hair", compiled["prompt"])

    def test_heuristic_fallback_inanimate_scene_does_not_inject_1girl(self) -> None:
        res = self.evaluator.evaluate_and_compile(
            raw_prompt="futuristic glowing cube rotating on dark surface",
            model_dialect="wan_video",
            force_heuristic=True,
        )
        compiled = res["compiled"]
        self.assertNotIn("1girl", compiled["prompt"])
        self.assertNotIn("solo", compiled["prompt"])


if __name__ == "__main__":
    unittest.main()
