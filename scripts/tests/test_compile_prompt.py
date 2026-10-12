"""Unit tests for Danbooru tag prompt compiler (compile_prompt.py).

tags: [tests, prompt, danbooru, compiler]
routing_hints: [tests, compile_prompt, danbooru]
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from tools.compile_prompt import PromptCompiler, normalize_tag


class TestCompilePrompt(unittest.TestCase):
    def setUp(self) -> None:
        self.compiler = PromptCompiler()

    def test_normalize_tag(self) -> None:
        self.assertEqual(normalize_tag("  Blonde_Hair  "), "blonde_hair")
        self.assertEqual(normalize_tag("Blue Eyes,"), "blue_eyes")
        self.assertEqual(normalize_tag("school uniform"), "school_uniform")

    def test_alias_resolution(self) -> None:
        res = self.compiler.compile("blond_hair, 1girl, solo", model_dialect="illustrious_xl")
        self.assertIn("blonde_hair", res["prompt"])
        self.assertNotIn("blond_hair", res["prompt"])

    def test_slot_reordering_illustrious(self) -> None:
        raw = "classroom, standing, 1girl, school_uniform, blue_eyes, sunlight, solo"
        res = self.compiler.compile(raw, model_dialect="illustrious_xl")
        tags = [t.strip() for t in res["prompt"].split(",")]

        # Slot 1: Quality
        self.assertEqual(tags[0], "masterpiece")
        # Slot 2: Subject before attire and setting
        idx_girl = tags.index("1girl")
        idx_eyes = tags.index("blue_eyes")
        idx_attire = tags.index("school_uniform")
        idx_pose = tags.index("standing")
        idx_setting = tags.index("classroom")
        idx_light = tags.index("sunlight")

        self.assertTrue(idx_girl < idx_eyes < idx_attire < idx_pose < idx_setting < idx_light)

    def test_pony_dialect_transformation(self) -> None:
        raw = "1girl, solo, masterpiece, best_quality, blue_hair, standing"
        res = self.compiler.compile(raw, model_dialect="pony_v6_xl")
        self.assertEqual(res["clip_skip"], 2)
        # masterpiece and best_quality must be stripped
        self.assertNotIn("masterpiece", res["prompt"])
        self.assertNotIn("best_quality", res["prompt"])
        # score tokens must be prepended
        self.assertIn("score_9", res["prompt"])
        self.assertIn("source_anime", res["prompt"])
        self.assertIn("rating_safe", res["prompt"])
        # Negative prompt contains score filters
        self.assertIn("score_6", res["negative_prompt"])

    def test_animagine_dialect_tail_quality(self) -> None:
        raw = "1girl, solo, blue_hair, standing, classroom"
        res = self.compiler.compile(raw, model_dialect="animagine_xl_v3")
        tags = [t.strip() for t in res["prompt"].split(",")]
        # Quality tokens should be at the tail
        self.assertEqual(tags[-1], "absurdres")
        self.assertEqual(tags[-4], "masterpiece")

    def test_deduplication(self) -> None:
        raw = "1girl, solo, 1girl, blue_hair, blue_hair, solo"
        res = self.compiler.compile(raw, model_dialect="illustrious_xl")
        prompt = res["prompt"]
        self.assertEqual(prompt.count("1girl"), 1)
        self.assertEqual(prompt.count("solo"), 1)
        self.assertEqual(prompt.count("blue_hair"), 1)

    def test_token_warning_threshold(self) -> None:
        many_tags = [f"tag_{i}" for i in range(70)]
        res = self.compiler.compile(many_tags, model_dialect="illustrious_xl")
        self.assertGreater(len(res["warnings"]), 0)
        self.assertIn("exceeds single 75-token chunk boundary", res["warnings"][0])


if __name__ == "__main__":
    unittest.main()
