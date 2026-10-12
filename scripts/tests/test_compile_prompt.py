"""Unit tests for Danbooru tag prompt compiler (compile_prompt.py)."""

from pathlib import Path
import pytest
from tools.compile_prompt import PromptCompiler, normalize_tag


@pytest.fixture
def compiler() -> PromptCompiler:
    return PromptCompiler()


def test_normalize_tag():
    assert normalize_tag("  Blonde_Hair  ") == "blonde_hair"
    assert normalize_tag("Blue Eyes,") == "blue_eyes"
    assert normalize_tag("school uniform") == "school_uniform"


def test_alias_resolution(compiler):
    res = compiler.compile("blond_hair, 1girl, solo", model_dialect="illustrious_xl")
    # blond_hair should be resolved to blonde_hair
    assert "blonde_hair" in res["prompt"]
    assert "blond_hair" not in res["prompt"]


def test_slot_reordering_illustrious(compiler):
    # Pass tags in scrambled order
    raw = "classroom, standing, 1girl, school_uniform, blue_eyes, sunlight, solo"
    res = compiler.compile(raw, model_dialect="illustrious_xl")
    tags = [t.strip() for t in res["prompt"].split(",")]

    # Slot 1: Quality
    assert tags[0] == "masterpiece"
    # Slot 2: Subject before attire and setting
    idx_girl = tags.index("1girl")
    idx_eyes = tags.index("blue_eyes")
    idx_attire = tags.index("school_uniform")
    idx_pose = tags.index("standing")
    idx_setting = tags.index("classroom")
    idx_light = tags.index("sunlight")

    assert idx_girl < idx_eyes < idx_attire < idx_pose < idx_setting < idx_light


def test_pony_dialect_transformation(compiler):
    raw = "1girl, solo, masterpiece, best_quality, blue_hair, standing"
    res = compiler.compile(raw, model_dialect="pony_v6_xl")
    assert res["clip_skip"] == 2
    # masterpiece and best_quality must be stripped
    assert "masterpiece" not in res["prompt"]
    assert "best_quality" not in res["prompt"]
    # score tokens must be prepended
    assert "score_9" in res["prompt"]
    assert "source_anime" in res["prompt"]
    assert "rating_safe" in res["prompt"]
    # Negative prompt contains score filters
    assert "score_6" in res["negative_prompt"]


def test_animagine_dialect_tail_quality(compiler):
    raw = "1girl, solo, blue_hair, standing, classroom"
    res = compiler.compile(raw, model_dialect="animagine_xl_v3")
    tags = [t.strip() for t in res["prompt"].split(",")]
    # Quality tokens should be at the tail
    assert tags[-1] == "absurdres"
    assert tags[-4] == "masterpiece"


def test_deduplication(compiler):
    raw = "1girl, solo, 1girl, blue_hair, blue_hair, solo"
    res = compiler.compile(raw, model_dialect="illustrious_xl")
    prompt = res["prompt"]
    assert prompt.count("1girl") == 1
    assert prompt.count("solo") == 1
    assert prompt.count("blue_hair") == 1


def test_token_warning_threshold(compiler):
    # Create 70 unique tags to exceed 75 estimated tokens
    many_tags = [f"tag_{i}" for i in range(70)]
    res = compiler.compile(many_tags, model_dialect="illustrious_xl")
    assert len(res["warnings"]) > 0
    assert "exceeds single 75-token chunk boundary" in res["warnings"][0]
