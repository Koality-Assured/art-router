"""Unit tests for Local Model Prompt Evaluator and Tag Management (prompt_evaluator.py)."""

from unittest.mock import patch
import pytest
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


@pytest.fixture
def evaluator() -> LocalPromptEvaluator:
    return LocalPromptEvaluator()


def test_evaluate_and_compile_with_mock_llm(evaluator):
    with patch.object(evaluator, "query_local_llm", return_value=MOCK_LLM_RESPONSE):
        res = evaluator.evaluate_and_compile(
            raw_prompt="anime girl cyberpunk in rain",
            model_dialect="illustrious_xl",
        )

        assert res["llm_evaluated"] is True
        assert res["llm_warning"] is None
        assert res["intent_summary"] == "A cyberpunk anime heroine standing in rainy neon streets"

        compiled = res["compiled"]
        prompt = compiled["prompt"]

        # Quality tokens should be at the head for Illustrious
        assert prompt.startswith("masterpiece, best_quality")
        # Subject anchor
        assert "1girl" in prompt
        # Hair/face
        assert "blue_hair" in prompt
        assert "twintails" in prompt
        # Negative tags merged
        assert "umbrella" in compiled["negative_prompt"]


def test_evaluate_and_compile_pony_dialect(evaluator):
    with patch.object(evaluator, "query_local_llm", return_value=MOCK_LLM_RESPONSE):
        res = evaluator.evaluate_and_compile(
            raw_prompt="anime girl cyberpunk in rain",
            model_dialect="pony_v6_xl",
        )

        compiled = res["compiled"]
        assert compiled["clip_skip"] == 2
        # Must have score tokens and no masterpiece
        assert "score_9" in compiled["prompt"]
        assert "masterpiece" not in compiled["prompt"]


def test_fallback_when_llm_fails(evaluator):
    with patch.object(evaluator, "query_local_llm", side_effect=ConnectionRefusedError("Connection refused")):
        res = evaluator.evaluate_and_compile(
            raw_prompt="1girl, blue_hair, standing, classroom",
            model_dialect="illustrious_xl",
        )

        assert res["llm_evaluated"] is False
        assert res["llm_warning"] is not None
        assert "Local LLM unreachable" in res["llm_warning"]

        compiled = res["compiled"]
        assert "1girl" in compiled["prompt"]
        assert "blue_hair" in compiled["prompt"]
