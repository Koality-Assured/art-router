"""Tests for ComfyUI Wan 2.1 / 2.2 video generation client, CLI, and MCP server.

tags: [test, comfyui, wan22, video, harness, mcp]
routing_hints: [test, video, comfy]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
for _p in (str(_SCRIPTS_DIR / "_lib"), str(_SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.test_comfy_video import ComfyVideoClient, DEFAULT_PROMPT
from tools.comfy_video_mcp_server import TOOLS_REGISTRY, dispatch_tool
from cli.harness import build_parser, main


def test_build_wan22_prompt_structure():
    """Verify that build_wan22_prompt constructs a fully valid 16-node graph."""
    client = ComfyVideoClient(server="127.0.0.1:8188")
    prompt_graph = client.build_wan22_prompt(
        prompt="A robotic astronaut floating in zero gravity",
        length=17,
        width=640,
        height=640,
        steps=4,
        fps=16.0,
        seed=42,
    )

    # Core node IDs
    expected_nodes = {"71", "73", "75", "76", "83", "85", "82", "86", "74", "89", "72", "81", "78", "87", "114", "115"}
    assert set(prompt_graph.keys()) == expected_nodes

    # Check positive text prompt
    assert prompt_graph["89"]["class_type"] == "CLIPTextEncode"
    assert prompt_graph["89"]["inputs"]["text"] == "A robotic astronaut floating in zero gravity"
    assert prompt_graph["89"]["inputs"]["clip"] == ["71", 0]

    # Check dimensions and frames
    assert prompt_graph["74"]["class_type"] == "EmptyHunyuanLatentVideo"
    assert prompt_graph["74"]["inputs"]["length"] == 17
    assert prompt_graph["74"]["inputs"]["width"] == 640
    assert prompt_graph["74"]["inputs"]["height"] == 640

    # Check dual-UNet LoRA loaders
    assert prompt_graph["83"]["class_type"] == "LoraLoaderModelOnly"
    assert "high_noise" in prompt_graph["83"]["inputs"]["lora_name"]
    assert prompt_graph["85"]["class_type"] == "LoraLoaderModelOnly"
    assert "low_noise" in prompt_graph["85"]["inputs"]["lora_name"]

    # Check output video node
    assert prompt_graph["115"]["class_type"] == "SaveVideo"
    assert prompt_graph["115"]["inputs"]["video"] == ["114", 0]


def test_mcp_tools_registry():
    """Verify MCP tools definition has the required 3 tools with valid schemas."""
    tool_names = [t["name"] for t in TOOLS_REGISTRY]
    assert "video_generate" in tool_names
    assert "video_status" in tool_names
    assert "video_list_models" in tool_names

    gen_tool = next(t for t in TOOLS_REGISTRY if t["name"] == "video_generate")
    assert "prompt" in gen_tool["inputSchema"]["properties"]
    assert "length" in gen_tool["inputSchema"]["properties"]
    assert "wait" in gen_tool["inputSchema"]["properties"]


def test_mcp_dispatch_unknown():
    """Verify dispatch_tool returns error on unknown tool."""
    res = dispatch_tool("non_existent_tool", {})
    assert res["ok"] is False
    assert "Unknown tool name" in res["error"]


def test_harness_cli_video_parser():
    """Test harness CLI parser handles video subcommands."""
    parser = build_parser()

    # Test status args
    args_status = parser.parse_args(["video", "status"])
    assert args_status.cmd == "video"
    assert args_status.video_cmd == "status"

    # Test models args
    args_models = parser.parse_args(["video", "models"])
    assert args_models.cmd == "video"
    assert args_models.video_cmd == "models"

    # Test generate args
    args_gen = parser.parse_args(["video", "generate", "--prompt", "cyberpunk car", "--length", "33", "--no-wait"])
    assert args_gen.cmd == "video"
    assert args_gen.video_cmd == "generate"
    assert args_gen.prompt == "cyberpunk car"
    assert args_gen.length == 33
    assert args_gen.no_wait is True


def test_harness_cli_video_models_execution(capsys):
    """Test harness video models prints installed Wan models."""
    ret = main(["video", "models"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "DIFFUSION_MODELS" in captured.out
    assert "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors" in captured.out
    assert "LORAS" in captured.out
